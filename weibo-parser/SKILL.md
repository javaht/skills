---
name: weibo-parser
description: 微博用户画像分析工具。爬取指定用户的全部微博，导出 Markdown 归档，生成发布时间统计图表，并从 10 个维度（情感模式、职业轨迹、价值观、性格心理、语言风格、原生家庭、性别认同、心理健康、审美趣味、人生叙事）深度分析用户人格。
metadata:
  author: zhou
  version: "1.0.0"
  triggers:
    - 分析微博用户
    - 微博画像
    - 爬取微博
    - 微博人格分析
    - weibo analysis
---

# Weibo Parser Skill

一键完成：**微博爬取 → Markdown 导出 → 统计图表 → 10 维度人格分析**

## 前置条件

- Chrome 已登录 weibo.com
- Python 3 + matplotlib 已安装
- Node.js 22+（CDP Proxy 使用原生 WebSocket）

## 工作流程

### Phase 1: 爬取阶段

1. 确认 CDP Proxy 可用（自包含，无需 web-access skill）：
   ```bash
   node "{SKILL_DIR}/scripts/check-deps.mjs"
   ```

2. 运行爬取脚本（支持 UID 或主页链接）：
   ```bash
   python3 "{SKILL_DIR}/scripts/scrape_weibo.py" {用户UID或链接} --output ~/Downloads/weibo_{UID}.json
   ```
   脚本自动从链接中提取 UID，例如 `https://weibo.com/u/1234567890` → UID `1234567890`。
   输出 JSON 文件路径和用户昵称。

### Phase 2: 导出 & 图表阶段

3. 导出 Markdown：
   ```bash
   python3 "{SKILL_DIR}/scripts/export_markdown.py" ~/Downloads/weibo_{UID}.json -n "{昵称}" -o ~/Downloads/{昵称}微博归档.md
   ```

4. 生成统计图表：
   ```bash
   python3 "{SKILL_DIR}/scripts/generate_charts.py" ~/Downloads/weibo_{UID}.json -n "{昵称}" -o ~/Downloads/{昵称}微博统计图.png
   ```

5. 向用户展示图表（用 Read 工具查看 PNG），并输出统计摘要。

### Phase 3: 分析阶段

6. 生成 analysis prompts（可选，了解 10 个维度）：
   ```bash
   python3 "{SKILL_DIR}/scripts/analyze_prompts.py" ~/Downloads/{昵称}微博归档.md
   ```

7. **并行启动 10 个 subagent**，每个从一个维度深度分析 Markdown 文件。必须使用 Agent 工具，subagent_type=general-purpose。

   每个 subagent 的 prompt 模板如下（用实际文件路径替换 `{MD_PATH}`）：

   **Agent 1 — 情感与人际关系模式**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **情感与人际关系模式**.
   Focus on: 依恋模式类型及证据、亲密关系中的渴望→靠近→退缩→反思循环、对'被爱'和'去爱'的认知变化轨迹、友情观演变、核心情感伤口、婚姻观转变。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 2 — 职业发展与技术成长轨迹**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **职业发展与技术成长轨迹**.
   Focus on: 职业路径全貌（大学→第一份工作→跳槽→Gap→当前）、技术栈演化、职业焦虑形态变化、对技术行业的真实态度、副业与技能焦虑、城市迁移与职业关联。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 3 — 价值观与世界观演变**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **价值观与世界观演变**.
   Focus on: 5-8条核心信条及演变、对努力的态度变化、金钱观和成功观、人性假设（信任vs警惕）、性别观、内在矛盾（自我奋斗vs星座/命运）。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 4 — 性格特质心理画像**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **性格特质心理画像**.
   Focus on: 大五人格(OCEAN)各维度1-10分及证据、MBTI倾向推断、依恋类型深度诊断、至少5种防御机制、认知风格、'孔雀型人格'和'低精力人群'的心理学对应、可能心理困扰倾向。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 5 — 语言风格与表达方式演变**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **语言风格与表达方式演变**.
   Focus on: 三个时期的语言风格对比、修辞策略图谱（自嘲/隐喻/格言体/网络梗/诗化语言/技术隐喻）、中英混用的心理动机、情绪与语言形式的对应、沉默的语法、表演性vs真实性边界、代码思维渗透。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 6 — 家庭与原生家庭影响**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **家庭与原生家庭影响**.
   Focus on: 家庭结构推断、父亲形象分析、母亲形象分析、姐姐/兄弟姐妹影响、原生家庭对人格的塑造路径、重复vs反抗家庭模式、离家与归家的张力。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 7 — 自我认同与性别意识**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **自我认同与性别意识**.
   Focus on: 男子气概定义及多种男性气质拉扯、对女性态度演变、多重身份标签权重、外貌与身体意象、小镇青年身份矛盾、年龄焦虑演变。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 8 — 情绪波动规律与心理健康**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **情绪波动规律与心理健康**.
   Focus on: 季节性/周期性情绪波动规律、压力源变迁时间线、应对机制评估(健康vs不健康)、自毁倾向信号、微博写作是否是叙事疗愈、躯体化症状、转折点/觉醒时刻、心理健康风险信号。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 9 — 审美趣味与文化消费图谱**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **审美趣味与文化消费图谱**.
   Focus on: 音乐品味全貌及审美光谱、影视剧偏好及叙事偏好、阅读与内容消费、旅行与空间审美、美食作为情感出口、硬汉审美vs文艺审美的融合、审美演变。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

   **Agent 10 — 关键转折点与人生叙事弧线**
   ```
   Read the file {MD_PATH}. Analyze from the angle of **关键转折点与人生叙事弧线**.
   Focus on: 5-7个改变人生的关键事件及前后变化、人生章节划分(命名和主题)、觉醒时刻、叙事类型判定、英雄之旅框架当前阶段、未来2-3年预测。
   Quote specific posts with dates as evidence. 300-500 words in Chinese.
   ```

### Phase 4: 综合阶段

8. 等待全部 10 个 agent 返回结果。

9. 将 10 个维度的分析结果整合为一份结构化的最终报告，包含：
   - 基本信息（年龄/城市/职业/时间跨度）
   - 人格基底（大五人格/MBTI/依恋类型总结）
   - 各维度核心发现（每个维度 1-2 段精华提炼）
   - 核心矛盾（定义性张力列表）
   - 一句话总结

10. 将最终报告输出到 `~/Downloads/{昵称}微博分析报告.md`。

## 用户交互

- 用户提供微博主页链接（如 `https://weibo.com/u/1234567890`）或 UID（如 `1234567890`）
- 脚本自动从链接中提取 UID，用户无需了解 UID 概念
- 整个流程自动运行，关键节点向用户同步进度

## 输出文件清单

| 文件 | 说明 |
|------|------|
| `~/Downloads/weibo_{UID}.json` | 原始 JSON 数据 |
| `~/Downloads/{昵称}微博归档.md` | Markdown 归档（可读） |
| `~/Downloads/{昵称}微博统计图.png` | 四合一统计图表 |
| `~/Downloads/{昵称}微博分析报告.md` | 10 维度综合人格分析报告 |

## 脚本依赖

| 脚本 | 用途 | 依赖 |
|------|------|------|
| `scripts/scrape_weibo.py` | CDP + 内部 API 爬取 | Python 3 标准库 + CDP Proxy（内置） |
| `scripts/export_markdown.py` | JSON → Markdown | Python 3 标准库 |
| `scripts/generate_charts.py` | 统计图表 | Python 3 + matplotlib + numpy |
| `scripts/analyze_prompts.py` | 分析维度 prompt 生成 | Python 3 标准库 |
| `scripts/check-deps.mjs` | CDP Proxy 环境检测 + 启动 | Node.js 22+ |
| `scripts/cdp-proxy.mjs` | CDP Proxy 服务 | Node.js 22+（原生 WebSocket） |

## 技术参考

- 站点经验: `references/site-pattern.md` — 微博平台特征、API 格式、已知陷阱
- CDP Proxy 自包含，无需依赖 web-access skill