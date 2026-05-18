#!/usr/bin/env python3
"""
微博爬取脚本 — 通过 CDP Proxy 调用微博内部 API，逐页抓取用户所有微博。

爬取策略（两阶段）：
  Phase 1: since_id 链式翻页 — 覆盖近期约 200-300 条，连续性好
  Phase 2: 直接页码扫描 — 不带 since_id，突破翻页深度限制，可回溯数年

依赖: Python 3 标准库（无需额外安装）
前置: Chrome 已登录 weibo.com，CDP Proxy 已启动

用法:
    python3 scrape_weibo.py 1234567890
    python3 scrape_weibo.py https://weibo.com/u/1234567890 --output /tmp/weibo.json
"""

import urllib.request
import urllib.error
import json
import time
import sys
import argparse
import os


def cdp_eval(target, js_code, proxy_port=3456, timeout=15):
    """在 CDP tab 中执行 JS 并返回结果"""
    data = js_code.encode("utf-8")
    url = f"http://localhost:{proxy_port}/eval?target={target}"
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "text/plain"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
            # CDP Proxy 返回 {value: ...} 或 {result: ...}
            if "value" in result:
                return result["value"]
            elif "result" in result:
                # 处理 {result: {type: "undefined"}} 等情况
                res = result["result"]
                if isinstance(res, dict) and res.get("type") == "undefined":
                    return None
                return res
            return None
    except urllib.error.URLError as e:
        raise RuntimeError(f"CDP Proxy 连接失败 (port {proxy_port}): {e}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"CDP 返回非 JSON 数据: {e}")


def cdp_new_tab(url, proxy_port=3456, timeout=10):
    """创建新的 CDP tab 并返回 targetId"""
    from urllib.parse import urlencode
    params = urlencode({'url': url})
    req = urllib.request.Request(
        f"http://localhost:{proxy_port}/new?{params}",
        data=b"",
        headers={"Content-Type": "text/plain"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read())
            return result.get("targetId") or result.get("target")
    except urllib.error.URLError as e:
        raise RuntimeError(f"无法创建 CDP tab: {e}")


def cdp_close_tab(target, proxy_port=3456):
    """关闭 CDP tab"""
    try:
        urllib.request.urlopen(f"http://localhost:{proxy_port}/close?target={target}", timeout=5)
    except Exception:
        pass  # 尽力关闭，失败不阻塞


def check_cdp_proxy(proxy_port=3456):
    """检查 CDP Proxy 是否可用"""
    try:
        with urllib.request.urlopen(f"http://localhost:{proxy_port}/targets", timeout=3) as resp:
            json.loads(resp.read())
        return True
    except Exception:
        return False


def scrape_weibo(uid, output_path=None, proxy_port=3456, max_pages=60, rate_limit=0.3):
    """
    抓取指定 UID 用户的所有微博（两阶段策略）。

    阶段 1: since_id 链式翻页 — 近期的连续性好
    阶段 2: 直接页码扫描 — 不带 since_id，突破翻页深度限制

    Args:
        uid: 微博用户 UID
        output_path: JSON 输出路径（默认 ~/Downloads/weibo_{uid}.json）
        proxy_port: CDP Proxy 端口
        max_pages: Phase 1 最大翻页数（Phase 2 会自动扩展）
        rate_limit: 页间延迟（秒）

    Returns:
        dict: {"total": int, "posts": list, "file": str, "nickname": str}
    """
    if output_path is None:
        output_path = os.path.expanduser(f"~/Downloads/weibo_{uid}.json")

    print(f"[1/4] 检查 CDP Proxy (port {proxy_port})...")
    if not check_cdp_proxy(proxy_port):
        print("  CDP Proxy 未运行，正在启动...")
        skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        check_deps = os.path.join(skill_dir, "scripts", "check-deps.mjs")
        if os.path.exists(check_deps):
            os.system(f"node {check_deps}")
            time.sleep(2)
            if not check_cdp_proxy(proxy_port):
                raise RuntimeError("CDP Proxy 启动失败，请手动运行: node scripts/check-deps.mjs")
        else:
            raise RuntimeError(f"CDP Proxy 不可用且找不到 {check_deps}")
    print("  CDP Proxy 就绪")

    print(f"[2/4] 打开微博主页 https://weibo.com/u/{uid} ...")
    target = cdp_new_tab(f"https://weibo.com/u/{uid}", proxy_port)
    time.sleep(3)  # 等待页面加载
    print(f"  targetId: {target}")

    # 获取昵称（页面标题格式: "阅州的个人主页 - 微博" → "阅州"）
    import re
    full_title = cdp_eval(target, "document.title", proxy_port, timeout=5)
    nickname = re.sub(r'[@\s]*的个人主页.*$', '', full_title).strip()
    if not nickname or nickname == full_title:
        nickname = f"用户{uid}"
    print(f"  昵称: {nickname}")

    print(f"[3/4] 开始抓取微博...")

    # JS 片段：解析微博列表（直接代码块，不是 IIFE）
    PARSE_POSTS_JS = """
      const posts = [];
      for (const post of (json.data.list || [])) {
        const tmp = document.createElement("div");
        tmp.innerHTML = post.text || "";
        posts.push({
          t: post.created_at,
          txt: (tmp.textContent || tmp.innerText || "").replace(/\\n/g, " ").replace(/\\t/g, " ").trim(),
          rc: post.reads_count || 0,
          ac: post.attitudes_count || 0,
          cc: post.comments_count || 0,
          rpc: post.reposts_count || 0,
          src: post.source || ""
        });
      }
      return {sid: json.data.since_id || "", count: posts.length, posts: posts};
    """

    # JS 模板：since_id 链式翻页
    def make_since_id_js(uid, page, since_id):
        sid_param = f'&since_id={since_id}' if since_id else ''
        return f"""
        (async () => {{
          const url = "/ajax/statuses/mymblog?uid={uid}&page={page}&feature=0{sid_param}";
          const resp = await fetch(url);
          const json = await resp.json();
          if (!json.data || !json.data.list || !json.data.list.length) return {{done: true, count: 0}};
          {PARSE_POSTS_JS}
        }})()
        """

    # JS 模板：直接页码访问（不带 since_id，用于深层翻页）
    def make_page_js(uid, page):
        return f"""
        (async () => {{
          const url = "/ajax/statuses/mymblog?uid={uid}&page={page}&feature=0";
          const resp = await fetch(url);
          const json = await resp.json();
          if (!json.data || !json.data.list || !json.data.list.length) return {{count: 0}};
          {PARSE_POSTS_JS}
        }})()
        """

    all_posts = []
    seen_keys = set()  # 去重用

    def add_posts(posts):
        added = 0
        for p in posts:
            key = (p.get("t", ""), p.get("txt", "")[:50])
            if key not in seen_keys:
                seen_keys.add(key)
                all_posts.append(p)
                added += 1
        return added

    # Phase 1: since_id 链式翻页（覆盖近期约 200-300 条，连续性好）
    print("  Phase 1: since_id 链式翻页...")
    since_id = 0
    for page in range(1, max_pages + 1):
        result = cdp_eval(target, make_since_id_js(uid, page, since_id), proxy_port, timeout=15)

        # 处理返回值
        if result is None or not isinstance(result, dict):
            print(f"    ⚠ 第 {page} 页返回无效: {type(result)}")
            break

        if result.get("done"):
            print(f"    ✓ 第 {page} 页无更多数据，Phase 1 完成")
            break

        posts = result.get("posts", [])
        added = add_posts(posts)
        since_id = result.get("sid", 0)
        print(f"    ✓ 第 {page} 页: {len(posts)} 条 (新增 {added}, 累计 {len(all_posts)})")
        time.sleep(rate_limit)

    phase1_total = len(all_posts)
    print(f"  Phase 1 完成，共 {phase1_total} 条")

    # Phase 2: 直接页码扫描（不带 since_id，突破翻页深度限制）
    # 从 Phase 1 结束的下一页开始，逐页扫描直到连续空页
    print(f"  Phase 2: 直接页码扫描 (page {page + 1} ~ {max_pages + 30})...")
    empty_streak = 0
    scan_max = max(max_pages + 30, page + 40)  # 至少扫 40 页
    for scan_page in range(page + 1, scan_max + 1):
        result = cdp_eval(target, make_page_js(uid, scan_page), proxy_port, timeout=15)

        # 处理返回值
        if result is None or not isinstance(result, dict):
            empty_streak += 1
            continue

        posts = result.get("posts", [])
        if posts:
            added = add_posts(posts)
            fd = posts[0].get("t", "?")
            ld = posts[-1].get("t", "?")
            print(f"    ✓ 第 {scan_page} 页: {len(posts)} 条 (新增 {added}, 累计 {len(all_posts)}) [{ld} ~ {fd}]")
            empty_streak = 0
        else:
            empty_streak += 1

        if empty_streak >= 5:  # 连续 5 页空，认为已到尽头
            print(f"    ✓ 连续 {empty_streak} 页空，Phase 2 完成")
            break

        time.sleep(rate_limit)

    phase2_total = len(all_posts) - phase1_total
    print(f"  Phase 2 完成，追加 {phase2_total} 条")

    # 按时间降序排列
    all_posts.sort(key=lambda p: p.get("t", ""), reverse=True)

    print(f"[4/4] 保存到 {output_path} ...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False)

    # 清理
    cdp_close_tab(target, proxy_port)

    print(f"\n完成！共 {len(all_posts)} 条微博，昵称: {nickname}")
    print(f"JSON: {output_path}")

    return {
        "total": len(all_posts),
        "posts": all_posts,
        "file": output_path,
        "nickname": nickname,
    }


def extract_uid(input_str):
    """从微博链接或纯数字中提取 UID。
    支持格式:
      - https://weibo.com/u/1234567890
      - https://m.weibo.cn/u/1234567890
      - https://weibo.com/u/1234567890/home
      - /u/1234567890
      - 1234567890 (纯数字)
    """
    import re
    # 尝试匹配 /u/{uid} 模式
    m = re.search(r'/u/(\d+)', input_str)
    if m:
        return m.group(1)
    # 尝试匹配纯数字
    m = re.search(r'^(\d+)$', input_str.strip())
    if m:
        return m.group(1)
    raise ValueError(f"无法从输入中提取 UID: {input_str}。支持格式: https://weibo.com/u/数字ID 或纯数字UID")


def main():
    parser = argparse.ArgumentParser(
        description="微博爬取脚本 — 通过 CDP + 微博内部 API 抓取用户所有微博",
        epilog="示例: python3 scrape_weibo.py 1234567890  |  python3 scrape_weibo.py https://weibo.com/u/1234567890"
    )
    parser.add_argument("input", help="微博用户 UID 或主页链接（例如 1234567890 或 https://weibo.com/u/1234567890）")
    parser.add_argument("--output", default=None, help="JSON 输出路径（默认 ~/Downloads/weibo_{uid}.json）")
    parser.add_argument("--proxy-port", type=int, default=3456, help="CDP Proxy 端口（默认 3456）")
    parser.add_argument("--max-pages", type=int, default=60, help="Phase 1 最大翻页数（Phase 2 会自动扩展 +30 页，默认 60）")
    parser.add_argument("--rate-limit", type=float, default=0.3, help="页间延迟秒数（默认 0.3）")
    args = parser.parse_args()

    uid = extract_uid(args.input)
    print(f"输入: {args.input} → UID: {uid}")

    try:
        result = scrape_weibo(
            uid=uid,
            output_path=args.output,
            proxy_port=args.proxy_port,
            max_pages=args.max_pages,
            rate_limit=args.rate_limit,
        )
        # 输出 JSON 结果供下游使用
        print(json.dumps({"status": "ok", "total": result["total"], "file": result["file"], "nickname": result["nickname"]}))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
