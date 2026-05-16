#!/usr/bin/env python3
"""
微博分析维度 Prompt 生成 — 为 10 个分析角度的 subagent 准备上下文。

用法:
    python3 analyze_prompts.py /path/to/weibo.md
    python3 analyze_prompts.py /path/to/weibo.md --chunks-dir /tmp/chunks
"""

import os
import sys
import argparse
import json

# 10 个分析角度定义
ANALYSIS_ANGLES = [
    {
        "id": 1,
        "name": "情感与人际关系模式",
        "focus": [
            "依恋模式类型及证据（回避型/焦虑型/安全型）",
            "亲密关系中的行为循环：渴望→靠近→退缩→反思",
            "对'被爱'和'去爱'的认知变化轨迹",
            "友情观的演变：如何定义朋友",
            "核心情感伤口（原生家庭、早期经历等）",
            "婚姻观从大学到现在的转变",
        ],
    },
    {
        "id": 2,
        "name": "职业发展与技术成长轨迹",
        "focus": [
            "职业路径全貌：大学→第一份工作→跳槽→Gap期→当前状态",
            "技术栈演化：Java → 前端 → AI/Agent",
            "职业焦虑的来源和形态变化",
            "对技术行业的真实态度（热爱 vs 倦怠）",
            "副业和技能焦虑（闲鱼接单、RPA、AI学习）",
            "城市迁移（济南→厦门→青岛→北京）与职业选择关联",
        ],
    },
    {
        "id": 3,
        "name": "价值观与世界观演变",
        "focus": [
            "核心信条清单（5-8条）及其演变",
            "对'努力'的态度演变",
            "金钱观和成功观",
            "对人性的底层假设（信任 vs 警惕）",
            "性别观和两性观",
            "内在矛盾（自我奋斗 vs 星座/命运等）",
        ],
    },
    {
        "id": 4,
        "name": "性格特质心理画像",
        "focus": [
            "大五人格（OCEAN）各维度 1-10 分评估及证据",
            "MBTI 倾向推断及认知功能堆栈分析",
            "依恋类型深度诊断",
            "防御机制清单（至少 5 种）",
            "认知风格（系统化 vs 共情思维）",
            "'孔雀型人格'和'低精力人群'的心理学对应概念",
            "可能的心理困扰倾向（抑郁/焦虑/ADHD特征）",
        ],
    },
    {
        "id": 5,
        "name": "语言风格与表达方式演变",
        "focus": [
            "三个时期的语言风格分期对比（大学/初入职场/近期）",
            "修辞策略图谱（自嘲、隐喻、格言体、网络梗、诗化语言、技术隐喻）",
            "中英混用的功能和心理动机",
            "情绪与语言形式的对应关系",
            "沉默的语法：如何表达说不出来的东西",
            "表演性和真实性的边界",
            "代码思维在文字表达中的渗透",
        ],
    },
    {
        "id": 6,
        "name": "家庭与原生家庭影响",
        "focus": [
            "家庭结构推断",
            "父亲形象分析（恐惧/同情/愤怒/理解/和解）",
            "母亲形象分析及角色定位",
            "姐姐/兄弟姐妹的影响",
            "原生家庭对人格的塑造路径",
            "重复 vs 反抗家庭模式的具体证据",
            "离家与归家的张力演变",
        ],
    },
    {
        "id": 7,
        "name": "自我认同与性别意识",
        "focus": [
            "男子气概定义及多种男性气质的共存/拉扯",
            "对女性的态度演变（是否有觉醒过程）",
            "多重身份标签（河南人/程序员/北漂/I人/天蝎男）的权重和互动",
            "外貌与身体意象（减肥/健身动机）",
            "'小镇青年'身份认同的矛盾",
            "年龄焦虑的演变（23岁到29岁）",
        ],
    },
    {
        "id": 8,
        "name": "情绪波动规律与心理健康",
        "focus": [
            "情绪波动的季节性/周期性规律",
            "压力源变迁时间线",
            "应对机制评估（健康 vs 不健康策略）",
            "自我伤害/自毁倾向的信号",
            "微博写作是否是叙事疗愈行为",
            "躯体化症状清单",
            "可识别的转折点/觉醒时刻",
            "心理健康风险信号评估",
        ],
    },
    {
        "id": 9,
        "name": "审美趣味与文化消费图谱",
        "focus": [
            "音乐品味全貌及审美光谱",
            "影视剧偏好及叙事偏好分析",
            "阅读与内容消费（书/播客/知识获取）",
            "旅行与空间审美（'用宏大的世界稀释痛苦'）",
            "美食作为情感出口的功能",
            "硬汉审美 vs 文艺审美的并存/融合",
            "从大学到现在的审美演变",
        ],
    },
    {
        "id": 10,
        "name": "关键转折点与人生叙事弧线",
        "focus": [
            "5-7 个改变人生的关键事件",
            "每个转折点前后内容/语气/主题的变化",
            "人生章节划分（命名和主题）",
            "觉醒时刻识别",
            "叙事类型判定（成长小说/悲剧循环/觉醒之路/西西弗斯式）",
            "英雄之旅框架中的当前阶段定位",
            "未来 2-3 年挑战和机遇预测",
        ],
    },
]


def generate_prompts(md_path, chunks_dir=None):
    """
    为 10 个分析角度生成 subagent prompt 模板。

    Args:
        md_path: Markdown 微博归档文件路径
        chunks_dir: 拆分文件输出目录（可选，不拆分时只需 md_path）

    Returns:
        list: 10 个分析角度的 prompt 字典 [{id, name, prompt}, ...]
    """
    prompts = []
    for angle in ANALYSIS_ANGLES:
        focus_text = "\n".join(f"  {i+1}. {f}" for i, f in enumerate(angle["focus"]))
        prompt = f"""Read the file {md_path} — it contains Weibo posts from a user spanning 9 years (2017-2026).

Your analysis angle: **{angle['name']}**

Deeply analyze:
{focus_text}

Requirements:
- Quote specific Weibo posts as evidence (include dates)
- 300-500 words in Chinese
- Return structured analysis with clear sub-sections"""

        prompts.append({
            "id": angle["id"],
            "name": angle["name"],
            "prompt": prompt,
        })

    # 如果指定了 chunks_dir，将 Markdown 拆分为 10 份
    if chunks_dir:
        os.makedirs(chunks_dir, exist_ok=True)

        with open(md_path, encoding="utf-8") as f:
            content = f.read()

        # 按 ### 分割微博
        posts = content.split("### #")
        header = posts[0]
        post_blocks = ["### #" + p for p in posts[1:]]

        chunk_size = max(1, len(post_blocks) // 10)
        for i in range(10):
            start = i * chunk_size
            end = start + chunk_size if i < 9 else len(post_blocks)
            chunk = header + "\n" + "".join(post_blocks[start:end])
            chunk_path = os.path.join(chunks_dir, f"chunk_{i+1}.md")
            with open(chunk_path, "w", encoding="utf-8") as f:
                f.write(chunk)
            prompts[i]["chunk_file"] = chunk_path
            print(f"Chunk {i+1}: posts {start+1}-{end} → {chunk_path}")

    return prompts


def main():
    parser = argparse.ArgumentParser(description="微博分析维度 Prompt 生成")
    parser.add_argument("md_path", help="Markdown 微博归档文件路径")
    parser.add_argument("--chunks-dir", "-c", default=None, help="拆分文件输出目录")
    parser.add_argument("--output", "-o", default=None, help="Prompt JSON 输出路径")
    args = parser.parse_args()

    if not os.path.exists(args.md_path):
        print(f"错误: 文件不存在 {args.md_path}")
        sys.exit(1)

    prompts = generate_prompts(args.md_path, args.chunks_dir)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"Prompts 已保存到: {args.output}")

    print(f"\n生成了 {len(prompts)} 个分析角度 prompt:")
    for p in prompts:
        print(f"  {p['id']}. {p['name']}")


if __name__ == "__main__":
    main()