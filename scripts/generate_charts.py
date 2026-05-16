#!/usr/bin/env python3
"""
微博发布时间统计图表生成脚本

依赖: matplotlib, numpy（pip3 install matplotlib numpy）

用法:
    python3 generate_charts.py /tmp/weibo.json
    python3 generate_charts.py /tmp/weibo.json --output ~/Downloads/weibo_charts.png
"""

import json
import sys
import argparse
import os
from datetime import datetime
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np


def configure_chinese_font():
    """配置中文字体"""
    for family in ["PingFang HK", "Heiti TC", "STHeiti", "SimHei", "Noto Sans CJK SC", "sans-serif"]:
        try:
            plt.rcParams["font.family"] = [family]
            plt.rcParams["axes.unicode_minus"] = False
            return
        except Exception:
            continue


def generate_charts(json_path, output_path=None, nickname="用户"):
    """
    生成四张微博统计子图。

    Args:
        json_path: 微博 JSON 文件路径
        output_path: PNG 输出路径（默认与 JSON 同目录）
        nickname: 用户昵称

    Returns:
        str: PNG 文件路径
    """
    if output_path is None:
        base = os.path.splitext(json_path)[0]
        output_path = f"{base}_charts.png"

    configure_chinese_font()

    with open(json_path, encoding="utf-8") as f:
        posts = json.load(f)

    # 解析日期
    dates = []
    for p in posts:
        try:
            d = datetime.strptime(p["t"], "%a %b %d %H:%M:%S +0800 %Y")
            dates.append(d)
        except (ValueError, KeyError):
            pass

    if not dates:
        print("错误: 无法解析日期")
        sys.exit(1)

    dates.sort()
    print(f"共 {len(dates)} 条有效日期，范围 {dates[0]} ~ {dates[-1]}")

    # ---- 创建图表 ----
    fig, axes = plt.subplots(2, 2, figsize=(18, 10))
    fig.suptitle(
        f"@{nickname} 微博发布统计 ({dates[0].year}-{dates[-1].year} · {len(dates)}条)",
        fontsize=18,
        fontweight="bold",
        y=0.98,
    )

    # ---- 子图 1: 每月发博数 ----
    ax1 = axes[0, 0]
    monthly = Counter()
    for d in dates:
        monthly[d.strftime("%Y-%m")] += 1
    months_sorted = sorted(monthly.keys())
    monthly_counts = [monthly[m] for m in months_sorted]
    month_dates = [datetime.strptime(m, "%Y-%m") for m in months_sorted]

    ax1.fill_between(month_dates, monthly_counts, alpha=0.25, color="#e74c3c")
    ax1.plot(month_dates, monthly_counts, color="#c0392b", linewidth=1.0)
    ax1.set_title("每月发博数", fontsize=14)
    ax1.set_ylabel("微博数", fontsize=11)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.grid(True, alpha=0.25, linestyle="--")

    if monthly_counts:
        peak_idx = monthly_counts.index(max(monthly_counts))
        ax1.annotate(
            f'{max(monthly_counts)}条 ({month_dates[peak_idx].strftime("%Y.%m")})',
            xy=(month_dates[peak_idx], max(monthly_counts)),
            xytext=(month_dates[peak_idx], max(monthly_counts) + 8),
            ha="center",
            fontsize=9,
            color="#c0392b",
            fontweight="bold",
        )

    # ---- 子图 2: 每年发博数 ----
    ax2 = axes[0, 1]
    yearly = Counter()
    for d in dates:
        yearly[d.year] += 1
    years = sorted(yearly.keys())
    yearly_counts = [yearly[y] for y in years]

    colors = []
    for y in years:
        if y < 2020:
            colors.append("#3498db")
        elif y < 2022:
            colors.append("#2980b9")
        elif y < 2024:
            colors.append("#e67e22")
        elif y < 2025:
            colors.append("#d35400")
        else:
            colors.append("#e74c3c")

    bars = ax2.bar(years, yearly_counts, color=colors, edgecolor="white", linewidth=0.8, width=0.7)
    ax2.set_title("每年发博数", fontsize=14)
    ax2.set_ylabel("微博数", fontsize=11)
    ax2.set_xticks(years)
    ax2.grid(True, alpha=0.25, axis="y", linestyle="--")

    for bar, count in zip(bars, yearly_counts):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 3,
            str(count),
            ha="center",
            fontsize=11,
            fontweight="bold",
            color="#2c3e50",
        )

    # ---- 子图 3: 累计发博数 ----
    ax3 = axes[1, 0]
    cumulative = list(range(1, len(dates) + 1))
    ax3.fill_between(dates, cumulative, alpha=0.2, color="#2ecc71")
    ax3.plot(dates, cumulative, color="#27ae60", linewidth=1.5)
    ax3.set_title("累计发博数", fontsize=14)
    ax3.set_ylabel("累计微博数", fontsize=11)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax3.xaxis.set_major_locator(mdates.YearLocator())
    ax3.grid(True, alpha=0.25, linestyle="--")

    # ---- 子图 4: 时段 × 星期热力图 ----
    ax4 = axes[1, 1]
    hour_wd = Counter()
    for d in dates:
        hour_wd[(d.hour, d.weekday())] += 1

    heatmap = np.zeros((24, 7))
    for (h, wd), count in hour_wd.items():
        heatmap[h, wd] = count

    im = ax4.imshow(heatmap, aspect="auto", cmap="YlOrRd", interpolation="bilinear", origin="upper")
    ax4.set_title("发博时段 × 星期分布", fontsize=14)
    ax4.set_xlabel("星期", fontsize=11)
    ax4.set_ylabel("小时", fontsize=11)
    ax4.set_xticks(range(7))
    ax4.set_xticklabels(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
    ax4.set_yticks(range(0, 24, 3))
    ax4.set_yticklabels([f"{h}:00" for h in range(0, 24, 3)])

    nonzero = heatmap[heatmap > 0]
    if len(nonzero) > 0:
        threshold = np.percentile(nonzero, 85)
        for h in range(24):
            for wd in range(7):
                val = heatmap[h, wd]
                if val >= threshold and val > 0:
                    color = "white" if val > threshold * 1.3 else "#2c3e50"
                    ax4.text(wd, h, int(val), ha="center", va="center", fontsize=7.5, fontweight="bold", color=color)

    cbar = plt.colorbar(im, ax=ax4, shrink=0.82, pad=0.02)
    cbar.set_label("微博数", fontsize=10)

    plt.tight_layout(pad=2)
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close()

    # 统计摘要
    weeks = ["一", "二", "三", "四", "五", "六", "日"]
    top_times = sorted(hour_wd.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"\n--- 统计摘要 ---")
    print(f"总微博数: {len(dates)}")
    print(f"日均发博: {len(dates) / max(1, (dates[-1] - dates[0]).days):.2f} 条")
    print(f"最高产年: {max(yearly, key=yearly.get)}年 ({yearly[max(yearly, key=yearly.get)]}条)")
    print(f"最高产月: {max(monthly, key=monthly.get)} ({monthly[max(monthly, key=monthly.get)]}条)")
    print("高频时段:")
    for (h, wd), c in top_times:
        print(f"  周{weeks[wd]} {h}:00-{h}:59 — {c}条")
    print(f"\n图表: {output_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="微博发布时间统计图表生成脚本")
    parser.add_argument("json_path", help="微博 JSON 文件路径")
    parser.add_argument("--output", "-o", default=None, help="PNG 输出路径")
    parser.add_argument("--nickname", "-n", default="用户", help="用户昵称")
    args = parser.parse_args()

    if not os.path.exists(args.json_path):
        print(f"错误: 文件不存在 {args.json_path}")
        sys.exit(1)

    output = generate_charts(args.json_path, args.output, args.nickname)
    print(json.dumps({"status": "ok", "file": output}))


if __name__ == "__main__":
    main()