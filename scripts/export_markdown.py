#!/usr/bin/env python3
"""
微博归档 Markdown 导出脚本 — 将 scrape_weibo.py 生成的 JSON 转为可读 Markdown。

用法:
    python3 export_markdown.py /tmp/weibo.json
    python3 export_markdown.py /tmp/weibo.json --output ~/Downloads/weibo_archive.md --nickname 阅州
"""

import json
import sys
import argparse
import os


def export_markdown(json_path, output_path=None, nickname="用户"):
    """
    将微博 JSON 导出为 Markdown。

    Args:
        json_path: JSON 文件路径
        output_path: Markdown 输出路径（默认与 JSON 同目录同名 .md）
        nickname: 用户昵称

    Returns:
        str: 输出文件路径
    """
    if output_path is None:
        base = os.path.splitext(json_path)[0]
        output_path = f"{base}.md"

    with open(json_path, encoding="utf-8") as f:
        posts = json.load(f)

    if not posts:
        print("警告: JSON 中没有数据")
        lines = [f"# {nickname}的微博归档\n", "> 暂无数据\n"]
    else:
        date_first = posts[-1]["t"].split(" +0800")[0] if "+0800" in posts[-1]["t"] else posts[-1]["t"]
        date_last = posts[0]["t"].split(" +0800")[0] if "+0800" in posts[0]["t"] else posts[0]["t"]

        lines = [
            f"# {nickname}的微博归档\n",
            f"> 共 {len(posts)} 条微博，时间跨度 {date_first} ~ {date_last}\n",
            "---\n\n",
        ]

        total = len(posts)
        for i, p in enumerate(posts):
            date_str = p["t"].split(" +0800")[0] if "+0800" in p["t"] else p["t"]
            # 倒序编号: 最早的第 1 条，最新的第 N 条
            idx = total - i
            lines.append(f"### #{idx} — {date_str}\n\n")
            lines.append(f"{p['txt']}\n\n")

            meta_parts = []
            if p.get("src"):
                meta_parts.append(f"设备 {p['src']}")
            if p.get("rc"):
                meta_parts.append(f"阅读 {p['rc']}")
            if p.get("ac"):
                meta_parts.append(f"点赞 {p['ac']}")
            if p.get("cc"):
                meta_parts.append(f"评论 {p['cc']}")
            if p.get("rpc"):
                meta_parts.append(f"转发 {p['rpc']}")
            if meta_parts:
                lines.append(f"*{' · '.join(meta_parts)}*\n\n")
            else:
                lines.append("\n")

    content = "".join(lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"导出完成: {output_path} ({len(posts):,} 条微博)")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="微博归档 Markdown 导出脚本")
    parser.add_argument("json_path", help="微博 JSON 文件路径")
    parser.add_argument("--output", "-o", default=None, help="Markdown 输出路径")
    parser.add_argument("--nickname", "-n", default="用户", help="用户昵称")
    args = parser.parse_args()

    if not os.path.exists(args.json_path):
        print(f"错误: 文件不存在 {args.json_path}")
        sys.exit(1)

    output = export_markdown(args.json_path, args.output, args.nickname)
    print(json.dumps({"status": "ok", "file": output}))


if __name__ == "__main__":
    main()