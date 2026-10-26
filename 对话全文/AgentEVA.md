# AgentEVA —— 对话全文

> 项目目录：`d-Cursor-agent-EVA`  
> 会话数：**2** · 用户提问 **4** 条 · Agent 回复 **9** 条 · 工具调用 **19** 次
>
> 说明：Agent 的工具调用参数已完整保留；**工具执行结果（命令输出 / 文件读取内容）Cursor 未持久化，故缺失**。
>
> 所有密钥、IP、账号信息已脱敏。

---

## 会话 001 · 2026-04-29 17:12 · 3 轮
`87167d4e-ea30-4aa6-af5d-345fd5ab4f70` · Agent 回复 6 条 · 工具 15 次 · 44.9 KB

### 👤 用户

> 现在我们要做一个我们内部的 agent的 bench mark测评工具，你帮我来想想我们要怎么做

### 🤖 Agent

让我先了解一下你们当前的项目情况，这样可以给出更有针对性的方案。

 用户想要建立一个内部的 agent 基准测试工具，这是一个咨询性质的需求，所以我应该提供详细的方案思路而不是直接编码。让我先看看他们现有的项目结构，了解是否有可以参考的 agent 代码或相关资源。

- 🔧 **Shell** `{ "command": "ls -la", "description": "查看当前工作目录结构", "working_directory": "d:\\文档\\Cursor\\agent EVA" }`
- 🔧 **Shell** `{ "command": "dir", "description": "查看当前目录文件列表", "working_directory": "d:\\文档\\Cursor\\agent EVA" }`
- 🔧 **Glob** `{ "glob_pattern": "**/*", "target_directory": "d:\\文档\\Cursor\\agent EVA" }`

### 🤖 Agent

工作目录是空的，那我就基于通用的 agent benchmark 设计来给你一份系统化的思路。这个话题很有价值——目前业界对 agent 的评估都还比较粗糙，自建一套对内部迭代非常关键。

---

# 一、先明确几个核心定位问题

在动手之前，建议先回答清楚这几个问题，因为它们决定了架构走向：

| 维度 | 关键问题 |
|------|----------|
| **测评对象** | 是 coding agent、业务 agent（如客服/RPA）、还是通用 agent？是评估**单 agent** 还是**多 agent 系统**？ |
| **测评目的** | 模型/Prompt 选型？版本回归？多团队 PK？对外发布榜单？ |
| **接入方式** | 黑盒（HTTP API）？白盒（SDK 接入，可拿到中间轨迹）？ |
| **运行环境** | 是否需要真实工具调用（数据库/浏览器/Shell）？还是只跑 mock？ |
| **数据敏感度** | 是否会跑生产脱敏数据？是否要求私有化部署？ |

这几个问题答案不同，方案会差很多。我先按"通用方案"展开，最后会给你一份针对性的澄清问题。

---

# 二、整体架构（推荐五层模型）

```
┌─────────────────────────────────────────────────┐
│  ⑤ Dashboard / Leaderboard 展示层                │
│     榜单 · 对比 · Trace 回放 · 失败 case 钻取    │
├─────────────────────────────────────────────────┤
│  ④ Storage 存储层                                │
│     Run · Trace · Score · Artifact              │
├─────────────────────────────────────────────────┤
│  ③ Evaluator 评估层                              │
│     Rule | LLM-Judge | Diff | Trajectory        │
├─────────────────────────────────────────────────┤
│  ② Runner 执行层（沙盒/调度/并发/重试）           │
│     Agent Adapter · Sandbox · Tool Mock         │
├─────────────────────────────────────────────────┤
│  ① Dataset 数据集层                              │
│     Task · Input · Expected · Tags · Difficulty │
└─────────────────────────────────────────────────┘
```

每一层都解耦，**插件化**是关键——不同 agent / 数据集 / 评估器都可以热插拔。

---

# 三、评估维度（不要只看"对错"）

这是最容易被忽视的部分。一个好的 benchmark 至少要覆盖 4 类指标：

### 1. 效果类（Effectiveness）
- **任务成功率** Pass@1 / Pass@k
- **答案准确率**（结构化输出可严格对比）
- **部分得分** Partial Credit（多步骤任务，给到子目标分）

### 2. 效率类（Efficiency）
- **步数** Steps / Turns
- **Token 消耗**（input/output 分开统计）
- **耗时** Latency（端到端 + 每步）
- **成本** $ Cost（按模型计价折算）

### 3. 行为类（Behavior）
- **工具调用准确率**（叫对工具 + 参数对）
- **冗余调用次数**（无效/重复 tool call）
- **轨迹合理性**（路径是否最优）
- **自我修正能力**（出错后能否纠偏）

### 4. 安全/鲁棒类（Safety & Robustness）
- **越权操作率**（删了不该删的、读了不该读的）
- **Prompt Injection 抵抗**
- **边缘 case 通过率**（空输入、超长、歧义）
- **拒答恰当性**（该拒就拒，不该拒别拒）

> **建议**：每个任务最终给一个**综合分**（加权），但**永远展示分项**。只看综合分会掩盖问题。

---

# 四、评估方法选型（按任务类型分流）

| 任务类型 | 推荐评估方法 | 例子 |
|---------|-------------|------|
| 有标准答案 | **精确匹配 / 单元测试** | 数学题、代码题（运行 pytest） |
| 结构化输出 | **JSON Schema 校验 + 字段对比** | 抽信息、填表单 |
| 多步任务 | **状态断言 + Trajectory 检查** | "在数据库里创建用户 X 并发邮件" → 查 DB 状态 |
| 开放生成 | **LLM-as-Judge（带 rubric）** + 人工抽检 | 写文档、客服回复 |
| 多轮对话 | **逐轮评分 + 全局一致性** | 对话流畅度、是否解决问题 |

### LLM-as-Judge 的几个坑（务必注意）
1. **位置偏差**：Judge 倾向选第一个，要做 A/B 互换打两遍取平均
2. **冗长偏差**：长答案容易被高估，rubric 里要明确"简洁也是优点"
3. **同模型偏好**：避免用 GPT-4 评 GPT-4，用第三方模型或多模型投票
4. **要给 few-shot 样例**：纯 zero-shot 评估很不稳定
5. **Pairwise 比 Pointwise 稳定**：能比就比，不要直接打分

---

# 五、数据集设计原则

这是 benchmark 价值的根本，比代码工程重要得多。

### 5.1 数据集结构（建议 schema）

```yaml
- task_id: ECOM-0042
  category: ecommerce/order_query
  difficulty: medium  # easy | medium | hard
  tags: [multi_turn, tool_use, db_read]
  input:
    user_message: "帮我查下我上周买的耳机什么时候到"
    context: { user_id: 123, ... }
  setup:           # 环境初始化（建沙盒数据）
    db_fixture: fixtures/order_42.sql
  expected:
    must_call_tools: [query_order, query_logistics]
    must_not_call:   [delete_order]
    final_answer_rubric: |
      必须包含订单号、预计送达时间；
      不应包含其他用户的订单信息
  evaluator: hybrid  # rule + llm_judge
```

### 5.2 设计原则
1. **覆盖度**：高频场景 80% + 长尾 20%（长尾才能拉开差距）
2. **难度分层**：easy/medium/hard 各占比，避免分数都堆在 90+
3. **防污染**（很重要）：内部数据集**绝不公开**，公开版本要做 contamination check（让模型续写题目，看能不能背出来）
4. **可复现**：每个 case 配 fixture/seed，跑两遍结果一致
5. **版本化**：数据集本身要有 `v1.0 / v1.1`，比对时锁定版本

### 5.3 来源建议
- ✅ 真实生产 trace 脱敏 → 转测试用例（最有价值）
- ✅ 客服/产品同事提供"刁钻问题"
- ✅ 公开 benchmark 改造（GAIA/SWE-bench/τ-bench 取经）
- ⚠️ LLM 合成（数量大但质量参差，建议人工筛过）

---

# 六、技术选型建议

按你们 Python 全栈背景给一份具体推荐：

| 层 | 推荐技术 | 备注 |
|----|---------|------|
| 后端 API | **FastAPI** + Pydantic | 提交 run、查结果 |
| 任务调度 | **Celery / Dramatiq**，简单可用 `asyncio.gather` | 大规模才上 Prefect/Airflow |
| 沙盒 | **Docker** 或 **E2B**（云沙盒） | 隔离 + 可重置；浏览器任务用 Playwright in Docker |
| Trace | **OpenTelemetry** + **Phoenix/Langfuse** | 别自己造轮子，OTel 已是业界标准 |
| 存储 | **PostgreSQL**（结构化）+ **S3/MinIO**（artifact） | trace 数据量大时考虑 ClickHouse |
| 评估 | 自研 evaluator 接口 + **deepeval / ragas** 工具复用 | 不要全自研 |
| 前端 | **Next.js + shadcn/ui** 或 **Streamlit** （MVP 用后者） | 对比页和 trace 回放是核心 |
| Agent 接入 | 抽象 `AgentAdapter` 接口（`run(task) -> trajectory`） | 统一 OpenAI/Claude/自研 agent |

### 关键抽象：AgentAdapter
```python
class AgentAdapter(Protocol):
    name: str
    version: str
    async def run(self, task: Task, ctx: RunContext) -> Trajectory: ...
```
所有要测的 agent 都实现这个接口，benchmark 就完全和具体 agent 解耦。

---

# 七、分阶段落地路线（重要）

不要一上来什么都做，按阶段推进：

### 🟢 MVP（1–2 周）— 跑通闭环
- [ ] 50 条手工标注任务（覆盖 3-5 个核心场景）
- [ ] CLI 工具：`bench run --agent xxx --dataset v0`
- [ ] 评估器只做 2 种：精确匹配 + LLM-Judge
- [ ] 结果存 SQLite，输出 Markdown 报告
- **目标**：能在不同 prompt/模型间得出明确对比结论

### 🟡 V1（1 个月）— 可日常使用
- [ ] 数据集扩到 200–500 条，建立标注规范
- [ ] 加入 trace 记录 + 沙盒隔离
- [ ] Web Dashboard（榜单 / 对比 / case 钻取）
- [ ] CI 集成：每次 agent 改动自动跑回归

### 🔵 V2（持续迭代）
- [ ] 多 agent 系统评估（agent 间协作）
- [ ] 在线评估（生产流量采样 → 持续打分）
- [ ] 失败 case 自动归因（聚类 + LLM 总结）
- [ ] 红队/对抗集（专攻安全）

---

# 八、值得参考的开源项目

| 项目 | 看什么 |
|------|--------|
| **OpenAI Evals** | 任务和评估器抽象 |
| **LangSmith / Langfuse** | Trace 数据模型设计 |
| **Phoenix (Arize)** | 开源 trace + eval 一体化 |
| **Inspect AI**（UK AISI） | 任务调度框架，工程质量很高 |
| **AgentBench / SWE-bench** | 数据集组织方式 |
| **τ-bench**（Sierra/Anthropic） | 真实工具调用 + 多轮的标杆 |
| **deepeval** | 现成 metric 实现，能省很多事 |

强烈建议先把 **Inspect AI** 和 **τ-bench** 的设计读一遍再动手——能少走很多弯路。

---

# 九、几个容易踩的坑（血泪经验）

1. **指标单一陷阱**：只看 success rate，结果优化出一个又慢又贵的 agent
2. **过拟合 benchmark**：迭代多了 prompt 是在背题，要定期换新 case
3. **评估自己评不准**：LLM-Judge 一定要做**人工对齐**（至少 50 条人工 vs LLM 打分对照），算 Cohen's κ 要 > 0.6 才能信
4. **忽略方差**：同一个 agent 跑 3 次结果可能差 10%，要跑多次报告均值+方差
5. **沙盒泄漏**：agent 把测试数据库搞坏了影响下一轮，每次必须 reset
6. **太晚做可观测性**：trace 一定要从 day 1 就接入，事后补很痛苦

---

# 十、为了让方案更具体，我需要你回答几个问题

为了把方案细化到能直接动工，麻烦确认下：

1. **agent 类型**：你们的 agent 主要做什么？（coding？业务流程？客服？通用助手？）
2. **现状**：现在是怎么评估 agent 效果的？（人工 spot check？还是已经有简单脚本？）
3. **接入边界**：测评工具是只测**自家 agent**，还是要支持**对比第三方 agent**（比如和 Cursor/Devin 比）？
4. **规模预期**：数据集大概多少条？每天/每周跑多少次？
5. **团队**：开发资源大概多少人/多少周？决定 MVP 范围

回答这几个问题后，我可以给你一份**针对性的目录结构、数据 schema 和 MVP 任务拆解**——直接可以开 Jira 排期那种。

 由于工作目录是空的，我可以从零开始设计这个方案。用户想要构建一个内部的 agent 基准测评工具，这在当前 AI agent 快速发展但缺乏统一评估标准的背景下很有意义。我需要从几个关键维度来思考这个问题，首先要明确要测评什么类型的 agent——比如编码 agent、推理 agent 还是其他类型。

然后考虑评估维度，包括任务完成率、准确性、效率指标（步数、token 消耗、成本）、鲁棒性、安全性、工具调用能力和上下文理解等。在测评方法上，可以结合 ground truth 对比、LLM-as-Judge 评估、人工审核和真实环境运行等多种方式。数据集设计需要覆盖不同难度和类别的任务，执行架构要支持任务编排、沙盒隔离、并发执行和失败重试，最后通过排行榜、版本对比和失败案例分析来呈现结果。我还可以参考业界已有的基准测试，比如 SWE-bench、WebArena、GAIA 等。

不过在给出完整方案前，我需要先问一些关键问题来理解用户的具体需求，因为不同类型的 agent 设计差异很大。我会用中文回答，先提供一个系统性的框架，然后通过澄清问题来引导对话向具体落地推进。

我的方案包括五层架构（数据集、执行、评估、存储、展示），涵盖任务成功率、步骤效率、成本、工具准确率、安全性和鲁棒性等多个评估维度，采用规则断言、LLM 评判、真值对比和轨迹分析等方法。在技术选型上，我倾向于用 Python 配合 FastAPI、Celery 任务调度、OpenTelemetry 追踪和 Streamlit 仪表板，分阶段从 MVP 到完整版本逐步实施。

### 👤 用户

> 我们要做一个内部的 agent 能力的 bench mark 之类的测试工具（我们是 Tapnow 一个做 aigc 画布的产品/你可以搜索一下背景信息）我们先来讨论一下要怎么做（文件是我们现在的 agent tool schema）：               好，模型选型 + 日常回归，这两个目标其实可以用同一套基础设施，只是使用姿势不同。我们来系统设计一下。
> 
> 核心设计原则
> 这两个目标决定了几个关键约束：
> 可重复性：同一个 test case，跑 100 次结果要稳定，不能因为 LLM 随机性导致结论飘。
> 可比较性：模型 A vs 模型 B 的分数必须在同一个评分体系下，不能有歧义。
> 低维护成本：回归测试要能持续跑，test case 不能太脆（不能一改 prompt 全挂）。
> 
> 测试集结构设计
> 建议按任务复杂度分三个 tier：
> Tier 1 · 单工具原子测试（~30 cases）
> 每个 case 只测一个工具调用是否正确。验证的是”工具理解”。
> 
> 输入: "在画布上创建一个蓝色的文本节点，内容是 Hello World"
> 期望: 调用 create_text_node，markdown 非空，color 格式合法 #RRGGBBAA
> 评分: Pass/Fail（规则判断，无需 judge 模型）
> 
> 这一层用规则评分，确定性强，跑起来快，适合作为回归门禁。
> Tier 2 · 多步任务链（~20 cases）
> 2-4 步的任务，测工具之间的上下文传递。
> 
> 输入: "搜索 noir film 风格参考图，挑一张放到画布上"
> 期望链: fetch_inspiration → create_media_node（file_id 来自上一步）
> 评分: 步骤完成率 + 参数传递是否正确
> 
> Tier 3 · 开放创作任务（~10 cases）
> 接近真实用户请求，没有唯一正确答案。
> 
> 输入: "帮我在画布上为一个赛博朋克短片做一组概念图"
> 评分: 需要 judge 模型，评估工具选择合理性、节点组织、是否用了 inspect_canvas 了解现状
> 
> 评分体系
> 三层分数，最终汇总成一个总分：
> 
> |维度     |权重 |评分方式                                   |
> |-------|---|---------------------------------------|
> |工具调用正确率|40%|规则：工具名 + 必填参数 + 格式校验                   |
> |任务完成度  |35%|规则（Tier1/2）+ LLM judge（Tier3）          |
> |行为质量   |25%|LLM judge：是否先 inspect、是否合理 group、是否处理错误|
> 
> 行为质量分是区分模型好坏最有价值的维度，也是纯规则无法捕捉的部分。
> 
> 基础设施
> 最小可行的技术栈：
> 
> test cases (JSON/YAML)
>     ↓
> test runner
>     ├── mock tool executor（返回预设 response，不真实调用）
>     ├── trace recorder（记录每次 tool call 序列）
>     └── scorer
>          ├── rule scorer（参数校验）
>          └── LLM judge（行为质量）
>     ↓
> result store (SQLite 或 JSON)
>     ↓
> report（模型 A vs B 对比表）
> 
> mock tool executor 是关键设计——不真实调 canvas API，而是返回预设的合法 response，这样测试可以完全离线跑，速度快、可重复。
> 
> 两个目标对应的使用方式
> 模型选型：同一批 cases，分别用模型 A / B 跑，对比三个维度的分数分布，重点看 Tier 3 的行为质量分差异。
> 日常回归：只跑 Tier 1 + Tier 2（纯规则评分，5 分钟内出结果），设一个阈值（比如工具正确率 < 90% 就 block），集成进 CI。
> 
> 我的建议是分两个阶段
> Phase 1（先做）：Tier 1 全覆盖 + Tier 2 覆盖你们最核心的 5 个任务链 + rule scorer。这个阶段就已经能作为回归门禁用了。
> Phase 2（稳定后）：加 Tier 3 + LLM judge，这时候才真正能用于模型选型。
> 
> 几个具体问题确认一下方向：
> 	1.	你们 agent 的 trace 现在有没有线上日志可以挖？有真实 trace 的话 Tier 2/3 的 test case 写起来快很多
> 	2.	mock executor 这层你们是想自己写，还是希望我帮你设计一个具体的 schema？
> 	3.	CI 集成这块现在用的什么体系（GitHub Actions / 其他）？​​​​​​​​​​​​​​​​

### 🤖 Agent

非常详细的方案，我先去补一下 Tapnow 的背景，再看看你提到的 tool schema 文件在哪。

 用户来自 Tapnow，一个 AIGC 画布产品团队，他们想建立一个内部 agent 能力的基准测试工具，用于模型选型和日常回归测试。他们提到有文件包含他们现在的 agent tool schema，但我没看到实际的文件附件，所以我需要先检查一下工作目录里是否有相关文件。

用户给出了一个相当完整的方案框架，包括三层测试集、三维评分体系、mock tool executor 架构和两阶段实施计划，并提出了三个具体问题：线上日志能否挖掘、mock executor 的实现方式，以及 CI 集成体系。我现在处于 Ask 模式，需要先搜索 Tapnow 的背景信息来更好地理解他们的产品，然后检查是否有附件文件，最后才能针对性地回应他的方案和问题。

- 🔧 **WebSearch** `{ "search_term": "Tapnow AIGC canvas product AI agent", "explanation": "了解 Tapnow 产品背景，做 AIGC 画布的产品" }`
- 🔧 **WebSearch** `{ "search_term": "Tapnow AI 画布 产品 agent", "explanation": "中文搜索补充 Tapnow 信息" }`
- 🔧 **Glob** `{ "glob_pattern": "**/*", "target_directory": "d:\\文档\\Cursor\\agent EVA" }`
- 🔧 **Glob** `{ "glob_pattern": "**/*.{json,yaml,yml,md,ts,py}", "target_directory": "d:\\文档\\Cursor" }`

### 👤 用户

> 我们要做一个内部的 agent 能力的 bench mark 之类的测试工具（我们是 Tapnow 一个做 aigc 画布的产品/你可以搜索一下背景信息）我们先来讨论一下要怎么做（文件是我们现在的 agent tool schema）：               好，模型选型 + 日常回归，这两个目标其实可以用同一套基础设施，只是使用姿势不同。我们来系统设计一下。
> 
> 核心设计原则
> 这两个目标决定了几个关键约束：
> 可重复性：同一个 test case，跑 100 次结果要稳定，不能因为 LLM 随机性导致结论飘。
> 可比较性：模型 A vs 模型 B 的分数必须在同一个评分体系下，不能有歧义。
> 低维护成本：回归测试要能持续跑，test case 不能太脆（不能一改 prompt 全挂）。
> 
> 测试集结构设计
> 建议按任务复杂度分三个 tier：
> Tier 1 · 单工具原子测试（~30 cases）
> 每个 case 只测一个工具调用是否正确。验证的是”工具理解”。
> 
> 输入: "在画布上创建一个蓝色的文本节点，内容是 Hello World"
> 期望: 调用 create_text_node，markdown 非空，color 格式合法 #RRGGBBAA
> 评分: Pass/Fail（规则判断，无需 judge 模型）
> 
> 这一层用规则评分，确定性强，跑起来快，适合作为回归门禁。
> Tier 2 · 多步任务链（~20 cases）
> 2-4 步的任务，测工具之间的上下文传递。
> 
> 输入: "搜索 noir film 风格参考图，挑一张放到画布上"
> 期望链: fetch_inspiration → create_media_node（file_id 来自上一步）
> 评分: 步骤完成率 + 参数传递是否正确
> 
> Tier 3 · 开放创作任务（~10 cases）
> 接近真实用户请求，没有唯一正确答案。
> 
> 输入: "帮我在画布上为一个赛博朋克短片做一组概念图"
> 评分: 需要 judge 模型，评估工具选择合理性、节点组织、是否用了 inspect_canvas 了解现状
> 
> 评分体系
> 三层分数，最终汇总成一个总分：
> 
> |维度     |权重 |评分方式                                   |
> |-------|---|---------------------------------------|
> |工具调用正确率|40%|规则：工具名 + 必填参数 + 格式校验                   |
> |任务完成度  |35%|规则（Tier1/2）+ LLM judge（Tier3）          |
> |行为质量   |25%|LLM judge：是否先 inspect、是否合理 group、是否处理错误|
> 
> 行为质量分是区分模型好坏最有价值的维度，也是纯规则无法捕捉的部分。
> 
> 基础设施
> 最小可行的技术栈：
> 
> test cases (JSON/YAML)
>     ↓
> test runner
>     ├── mock tool executor（返回预设 response，不真实调用）
>     ├── trace recorder（记录每次 tool call 序列）
>     └── scorer
>          ├── rule scorer（参数校验）
>          └── LLM judge（行为质量）
>     ↓
> result store (SQLite 或 JSON)
>     ↓
> report（模型 A vs B 对比表）
> 
> mock tool executor 是关键设计——不真实调 canvas API，而是返回预设的合法 response，这样测试可以完全离线跑，速度快、可重复。
> 
> 两个目标对应的使用方式
> 模型选型：同一批 cases，分别用模型 A / B 跑，对比三个维度的分数分布，重点看 Tier 3 的行为质量分差异。
> 日常回归：只跑 Tier 1 + Tier 2（纯规则评分，5 分钟内出结果），设一个阈值（比如工具正确率 < 90% 就 block），集成进 CI。
> 
> 我的建议是分两个阶段
> Phase 1（先做）：Tier 1 全覆盖 + Tier 2 覆盖你们最核心的 5 个任务链 + rule scorer。这个阶段就已经能作为回归门禁用了。
> Phase 2（稳定后）：加 Tier 3 + LLM judge，这时候才真正能用于模型选型。
> 
> 几个具体问题确认一下方向：
> 	1.	你们 agent 的 trace 现在有没有线上日志可以挖？有真实 trace 的话 Tier 2/3 的 test case 写起来快很多
> 	2.	mock executor 这层你们是想自己写，还是希望我帮你设计一个具体的 schema？
> 	3.	CI 集成这块现在用的什么体系（GitHub Actions / 其他）？​​​​​​​​​​​​​​​​@current-tools-schema.md

### 🤖 Agent

好，先读一下你们的 tool schema，然后再搜下 Tapnow 的背景信息，这样我能给你更具体的建议。

 好的，用户是 Tapnow 团队，他们在做 AIGC 画布产品，已经有了一套相对完整的设计框架包括分层体系和评分机制。他们提供了工具架构文档和三个具体问题，我需要先理解他们现有的工具集结构，然后才能有针对性地回答问题。

- 🔧 **Glob** `{ "glob_pattern": "**/current-tools-schema*" }`
- 🔧 **Glob** `{ "glob_pattern": "**/*tools-schema*" }`
- 🔧 **Glob** `{ "glob_pattern": "**/*.md", "target_directory": "d:\\文档\\Cursor\\agent EVA" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\current-tools-schema.md" }`
- 🔧 **WebSearch** `{ "search_term": "Tapnow AIGC canvas AI agent product", "explanation": "了解 Tapnow 产品背景" }`

### 🤖 Agent

文件没在工作目录里，让我换个路径找一下。

 文件没找到，但 Glob 已经定位到了 `.\current-tools-schema.md`，虽然路径是相对于当前工作目录而不是用户的目录。让我改用绝对路径试试。

- 🔧 **Glob** `{ "glob_pattern": "**/current-tools-schema.md", "target_directory": "d:\\" }`
- 🔧 **Shell**

```json
{
 "command": "Get-ChildItem -Path \"d:\\文档\\Cursor\" -Filter \"*.md\" -Recurse -ErrorAction SilentlyContinue | Select-Object FullName, Length | Format-Table -AutoSize",
 "description": "递归查找所有 md 文件"
}
```
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\agent EVA\\current-tools-schema.md" }`

### 🤖 Agent

读完 schema 了，结合 Tapnow 的产品定位（AI-native 创意画布 + 多模型编排），你的总体方案已经非常成熟了。我重点补几个**针对你们工具集特性**的关键设计点，然后回答你的 3 个问题。

---

# 一、看完 schema 后的几个观察（这些会显著影响测评设计）

你们的工具集有几个特殊性，benchmark 必须针对性设计：

### 1. 强**有状态**：画布是测评的"世界"
不同于一般 agent 工具是无状态 API，你们 11 个工具里 9 个都依赖 `canvas_id` 上下文。这意味着 mock executor 不能只 mock 单次调用——必须维护一个 **VirtualCanvasState**。否则 `inspect_canvas` 返回的 `total_nodes` 跟前面 `create_text_node` 调用根本对不上，agent 会陷入认知错乱。

### 2. ID **链式传递**是核心能力测试点
你们工具集天然形成几条数据流：
- `fetch_inspiration.file_id` → `create_media_node.file_id`
- `gen_image.node_id` → `gen_video.reference_node_ids`
- `analyze_media` 输入 → `gen_image.prompt` 优化
- `inspect_canvas.log` 中的 id → `read_canvas_nodes.node_ids`

**ID 是否正确传递**是个非常硬的、可规则化判定的能力指标，比"调对工具"更深一层。

### 3. **隐藏的推断逻辑**是模型能力的分水岭
特别是 `gen_video.mode`：未传时会根据 reference 数量/类型自动推断（1 image → image_to_video，2 image → first_last_frame，等等）。**好模型会显式传 mode；差模型靠默认推断也能跑，但测不出能力差异**。建议设计专门 case 让 agent 在歧义场景下选择——比如"用这两张图做视频"，看它选 first_last_frame 还是 multimodal。

### 4. enum + 约束**陷阱密布**
- `gen_image.quality` 仅 `gpt-image-2` 支持
- `gen_video.quality=4k` 不支持 video reference
- `happyhorse-1.0` 只支持部分 mode
- `image_size` 仅特定模型支持
- `color` 必须 `#RRGGBBAA`（很多模型会输出 `#RGB` 或 `#RRGGBB`）

这些约束是**绝佳的负向测试用例**——能精准量化模型对 schema 的遵循度。

### 5. **Tool result envelope** 的投影差异
`_agent_result` 跟 `_client_result` 不一样（agent 看到的是裁剪过的）。mock 必须**精确还原 agent 视角**，否则评测和生产行为不一致。例如 `read_canvas_nodes` 的 agent 投影会按 `include` 字段省略 null 值。

---

# 二、评分体系细化（针对你的工具集）

你的 40/35/25 分配很合理，我建议把每一类**拆成可机器判定的子项**，避免"行为质量"全靠 judge：

### 工具调用正确率（40%）— 全规则可判
```
- 工具名命中           : 5%
- 必填字段齐全         : 10%
- enum 值合法          : 5%
- 格式校验（color/正则）: 5%
- 跨工具约束           : 10%   ← Tapnow 特色
  · quality=4k 不能 + video reference
  · happyhorse mode 限制
  · reference_node_ids 必须存在于 canvas
- additionalProperties=false 没多传 : 5%
```

### 任务完成度（35%）— 规则 + 状态断言
```
- 终态正确性           : 20%   ← 关键
  · canvas 最终节点数/类型符合预期
  · group 结构对（成员节点 ID 集合）
- ID 链路正确          : 10%   ← Tapnow 特色
  · create_media_node.file_id == fetch_inspiration 返回值
- 没产生副作用         : 5%
  · 没误删/误改不该改的
```

### 行为质量（25%）— LLM judge + 部分规则
```
- inspect 先行         : 5%   ← 可规则化
  · 大改前是否调过 inspect_canvas/read_canvas_nodes
- 工具选择经济性       : 5%
  · 没用 fetch_inspiration 干 web search 能干的事
  · 没把 inspect snapshot 当 read 用
- 错误恢复             : 5%   ← 可规则化（注入 partial fail）
- 组织合理性           : 5%   ← judge
  · 该 group 时 group，layout 合理
- 用户意图对齐         : 5%   ← judge
```

> **关键洞察**：我估算下来你们的工具集里，**大约 80% 的"行为质量"指标都可以规则化**，judge 只需要兜底剩下 20%（主要是开放创作的合理性）。这意味着 Tier 1/2 可以做到几乎全规则、超快速、完全确定。

---

# 三、Mock Executor 详细设计（回答你 Q2 重点）

我建议设计成 3 层：

### 3.1 数据层：VirtualCanvasState

```python
class VirtualCanvasState:
    canvas_id: str
    nodes: dict[str, NodeRecord]      # node_id -> record
    connections: list[Connection]
    event_log: list[Event]            # 给 inspect_canvas.log 用
    file_hub: dict[str, FileRecord]   # file_id -> {kind, mock_url}
    org_billing: BillingState         # 给 gen_* 用
    
    # 核心方法
    def apply(self, tool, input, output): ...     # 更新状态 + 记 event
    def snapshot(self) -> str: ...                # for inspect_canvas snapshot
    def diff_since(self, ts) -> dict: ...
```

**关键**：这个 state 是测试用例的"上帝视角真相"。最终评分时，`assert state.matches(expected_state)`。

### 3.2 工具层：MockHandler 接口

```python
class MockHandler(Protocol):
    tool_name: str
    
    def validate(self, input: dict) -> ValidationResult:
        """跑 schema + 运行期约束（gen_video 的 mode 限制等）"""
    
    def execute(self, input: dict, state: VirtualCanvasState, 
                scenario: Scenario) -> dict:
        """返回符合 _agent_result schema 的输出，并副作用更新 state"""
```

每个工具一个 handler，**复用真实 handler 的 validation 逻辑最好**——直接 import worker 里的 schema 和约束代码，确保完全一致。

### 3.3 场景注入层：Scenario

这是 mock 的精髓——**可控地制造各种异常**，测 agent 的鲁棒性：

```yaml
# tier-2 case 示例
case_id: T2-008
name: "fetch_inspiration 部分失败时 agent 是否正确处理"
initial_state:
  canvas_id: "c-001"
  nodes: []
scenario:
  # 用 mock 控制每次工具调用的行为
  fetch_inspiration:
    - match: { query: "noir" }
      response: { results: [...], has_more: true }
  create_media_node:
    - match: { file_id: "$fixture.inspiration[0].file_id" }
      inject_error:
        is_error: true
        error:
          code: "tool_execution_failed"
          message: "File hub timeout"
    - match: { file_id: "$fixture.inspiration[1].file_id" }
      response: { node_id: "image-mock-uuid-2" }
  gen_image:
    - any: true
      inject_billing_block: 
        reason: "insufficient_balance"
expected:
  must_call_tools: [fetch_inspiration, create_media_node]
  expected_recovery:
    # agent 在第一个 file_id 失败后必须换一个 file_id 重试
    pattern: "create_media_node.error -> create_media_node(different file_id)"
  forbidden_calls:
    - tool: gen_image
      reason: "billing blocked 后不该重试"
```

这种 scenario 注入能力让你测出**工具调对了但意外路径处理差**的问题，这正是模型 A/B 真正拉开差距的地方。

### 3.4 mock 该不该真的"假"？

我的建议：**绝大多数工具用纯 mock，但 `analyze_media` / `fetch_inspiration` 这两个内容相关的工具，留一个可选的"半真"模式**。

原因：mock 的 `analyze_media` 返回死内容，agent 拿到后续生成的 prompt 就跟真实场景脱节，可能掩盖问题。半真模式可以接真实 vision 模型，但 file_id 用 fixture（内置 10-20 张测试图）。Tier 3 用半真，Tier 1/2 用纯 mock。

---

# 四、Test Case Schema 设计（YAML 推荐）

```yaml
# datasets/tier-1/T1-create_text_node-001.yaml
case_id: T1-create_text_node-001
tier: 1
category: tool_atomic
target_tool: create_text_node
difficulty: easy
tags: [color_format, schema_compliance]

input:
  user_message: "在画布上创建一个蓝色的标题节点，写 Hello World"

initial_state:
  canvas_id: "test-canvas"
  nodes: []

assertions:
  # 规则评分项
  must_call:
    - tool: create_text_node
      args_match:
        markdown: { contains: "Hello World" }
        color: { regex: "^#[0-9A-Fa-f]{8}$" }
        # 蓝色色相判定（HSL 转换后 H 在 200-250）
        color_hue: { in_range: [200, 250] }
  must_not_call: [gen_image, gen_video, fetch_inspiration]
  max_tool_calls: 3   # 防止瞎调一堆
  final_state:
    nodes_count: 1
    nodes_by_type: { text: 1 }

scoring:
  # tier 1 全规则
  weights: { tool_correct: 0.6, completion: 0.4, behavior: 0.0 }
```

```yaml
# datasets/tier-2/T2-inspiration-to-canvas-001.yaml
case_id: T2-inspiration-to-canvas-001
tier: 2
category: tool_chain
target_chain: [fetch_inspiration, create_media_node]
difficulty: medium

input:
  user_message: "搜索 noir film 风格参考图，挑一张放到画布上"

fixtures:
  fetch_inspiration_response:
    - file_id: "fixture-img-001"
      title: "Chinatown"
      year: "1974"
    - file_id: "fixture-img-002"
      title: "Blade Runner"

assertions:
  must_call_in_order:
    - tool: fetch_inspiration
      args_match:
        query: { semantic_match: ["noir", "film noir"] }
    - tool: create_media_node
      args_match:
        # 关键：file_id 必须来自上一步的返回
        file_id: { from_previous: "fetch_inspiration.results[*].file_id" }
  forbidden_chains:
    # 不能凭空 create，必须用 fetch 的结果
    - pattern: "create_media_node before fetch_inspiration"
  final_state:
    nodes_count: 1
    nodes_by_type: { image: 1 }
```

```yaml
# datasets/tier-3/T3-cyberpunk-concepts-001.yaml
case_id: T3-cyberpunk-concepts-001
tier: 3
category: open_creation
difficulty: hard

input:
  user_message: "帮我在画布上为一个赛博朋克短片做一组概念图"

fixtures:
  gen_image_responses: [...]  # 预置返回的 mock node_ids
  
rubric:   # 给 LLM judge 的评分大纲
  inspect_first:
    description: "是否在改动前先 inspect_canvas/read_canvas_nodes"
    weight: 0.15
  scene_diversity:
    description: "概念图应该覆盖至少 3 类场景（街景/角色/特写）"
    weight: 0.25
  organization:
    description: "是否合理 group + 命名"
    weight: 0.20
  reference_usage:
    description: "是否用了 fetch_inspiration 找参考"
    weight: 0.15
  prompt_quality:
    description: "gen_image 的 prompt 是否专业（含视觉术语、灯光、镜头）"
    weight: 0.25

# tier 3 多次采样取均值
sampling: { n: 3, aggregate: mean }
```

---

# 五、回答你的三个问题

## Q1: 线上 trace 可挖掘性

强烈建议挖。基于你们用 `claude_agent_client.py` + in-process MCP server 的架构，工具调用应该天然进了 worker 日志或 OTel trace。

**具体建议**：
- 写一个 `trace → testcase` 转换脚本：选取**完成度高的真实 conversation**，自动生成 Tier 2 用例的草稿（含 user_message、tool_call_sequence、final_state），然后人工审核+填 expected
- 优先挖**多步且成功的**轨迹（≥3 个工具调用，最终用户没再追问）作为正样本
- 同时挖**失败/卡住**的轨迹做负样本（什么 prompt 让 agent 反复调错？）
- **强制脱敏**：user_id、org_id、prompt 内容里的私密信息需要 PII 扫描

我估算从生产 trace 挖个 100-200 条种子用例，比手写快 5 倍。

## Q2: mock executor 自己写还是我帮你设计

强烈建议**复用你们 worker 的代码**，不要重新写一份：

**方案：包一层 mock**
```
agent-worker/
  app/tools/registry.py         # 真实 registry
  app/tools/handlers/           # 真实 handler

agent-bench/
  bench/mock/
    mock_registry.py            # 继承真实 ToolRegistry
    mock_state.py               # VirtualCanvasState
    mock_handlers/              # 每个工具的 mock 版本
      _base.py                  # 复用真实 schema + validation
      create_text_node.py       # 只 mock execute()，validation 用真实的
      ...
```

**关键设计点**：
1. `MockToolRegistry` 继承真实 `ToolRegistry`，**只替换 handler 的 execute 部分**，schema/validation 逻辑全部复用——这样 schema 一升级 mock 自动跟上，不会漂移。
2. `_build_mcp_server()` 同样的接口，让 `claude_agent_client` 完全感知不到自己在 mock 环境。
3. `ToolExecutionContext` 注入 mock canvas_id，hook 到 VirtualCanvasState。
4. `gen_image` / `gen_video` 的 confirmation 门控也要 mock——可以加一个 `auto_approve_mode` 或 `auto_block_mode`，分别测两种路径。

如果你愿意，我可以下一步给你**具体到文件级**的 mock executor 骨架（包括如何 hook `can_use_tool`、如何在 in-process MCP server 里替换 handler）。

## Q3: CI 集成

不知道你们具体技术栈，但通用建议：

**分层跑法**：
| 阶段 | 跑什么 | 触发 | 时长目标 | 失败处理 |
|------|--------|------|----------|----------|
| **PR check** | Tier 1 全量 | PR push | < 3 min | block merge |
| **PR check（核心）** | Tier 2 核心 5 条链 | PR push | < 5 min | block merge |
| **Nightly** | Tier 1+2+3 全量 | cron | < 30 min | 报警 + 周报 |
| **模型选型** | 同一批 cases × 多模型 | 手动 | 不限 | 出对比报告 |

**一些经验**：
1. **不要用绝对阈值，用 baseline 对比**：维护一个 `baseline.json`（main 分支最新成绩），PR 跑完和 baseline 比，下降 > 2% 才挂。绝对阈值容易误伤合理优化（比如有意改了 prompt 牺牲一点 case 换更多 case）。
2. **失败 case 必须 attach trajectory**：CI artifact 存每个失败 case 的完整 tool call sequence + state diff，PR 评论里直接给链接。否则 reviewer 不会去看 CI。
3. **种子（seed）固定**：LLM 调用要传 `temperature=0` + 固定 seed（如果模型支持）；不支持的模型每个 case 跑 N=3 取多数。
4. **缓存**：同一 prompt + model + seed 的输出缓存，PR 只跑变化部分能省 90% 时间。
5. **GitHub Actions 跑 tier 1/2 完全够**；tier 3 因为要调 judge 模型，建议跑专用 runner（API key 隔离 + 成本可控）。

---

# 六、额外提醒（你方案里没明确但很重要的几点）

1. **数据集污染防护**：Tier 3 数据集尤其要注意——如果你们之后用真实生产数据做 SFT/RLHF，必须保证 benchmark case 不进训练集。建议从 day 1 就给 case 加一个 "magic string"（如 `__BENCHMARK_TAPNOW_2025__` 内嵌在 input），训练数据过滤时一刀切。

2. **方差报告**：Tier 3 跑 N 次，报告里**必须给出方差/置信区间**而不只是均值。否则 GPT-4 vs Claude 差 1.5 分，可能纯属噪声。

3. **成本面板**：模型选型时除了分数，必须并排展示**每条 case 的平均 token / 平均 $**。Tapnow 这种 image/video 高成本场景，agent 多调一次 gen_image 可能成本翻倍，分数不变但实用性差很多。

4. **判官选择**：LLM judge 别用同家族模型（测 Claude 不要用 Claude judge）。建议至少 2 个判官投票（GPT-4 + Gemini Pro），不一致的 case 进人工 review 队列。

5. **回归集 vs 探索集 分离**：
   - **回归集**：稳定、不变，跑 CI（防止退化）
   - **探索集**：每月加新 case，专门挖薄弱点（不进 CI 阈值）
   
   一开始混在一起还行，case 多了一定要分。

---

# 七、建议的下一步动作

你说说优先级，我可以下一步深入帮你做这些里的任意一个：

1. **画一份 mock executor 的具体类图 + 关键接口签名**（最复杂、最有价值）
2. **基于你们 11 个工具，列出 30 条 Tier 1 + 20 条 Tier 2 用例清单**（直接能开始写）
3. **设计 trace → testcase 的转换 pipeline**（如果生产 trace 可挖）
4. **判官 prompt 模板 + rubric 库**（针对 Tapnow 的画布行为评分）
5. **bench 工具自身的目录结构 + 模块划分**（比如要不要单独开 repo、和 agent-worker 怎么共存）

你最想先深入哪一块？

 现在我对这个产品有了更清晰的理解：Tapnow 是一个 AI 原生的创意画布平台，整合了 Sora、Midjourney、Luma 和 Flux 等多个生成模型，能够统一处理文本、图像、音频和视频内容，用于制作电视广告、商业广告、动画和短视频等专业级内容。而 Agent 工具集分为两类——Tapnow 自身的业务工具用来操作画布，还有其他类型的工具。

我看到了这个系统的核心设计特点：工具的输入都有严格的 schema 约束，包括枚举值、最小项数和正则表达式验证，系统维护着对话、画布、用户和组织的上下文信息，所有工具调用都遵循统一的响应格式，生成图像和视频的操作需要经过确认门控，还有文件 ID 和引用节点的管理机制以及账单检查。用户已经设计出了相当成熟的架构思路。

现在我需要针对他们的三个具体问题来深化方案：线上 trace 日志的可挖掘性、mock executor 的 schema 设计，以及 CI 集成体系。对于 Tapnow 这个产品，我特别要关注画布状态的依赖性——很多工具操作都依赖当前的节点和连接状态，所以 mock 必须能够模拟这些状态；还要处理 file_id 和 node_id 的链式传递流程，比如从搜索灵感获得 file_id，再用它创建媒体节点，或者生成图像后用其 node_id 作为下一步视频生成的参考；节点 ID 有明确的类型前缀规则；gen_video 的 mode 推断逻辑——当没有显式传入 mode 时需要根据引用节点的类型来推断，这是个很好的测试切入点；还有生成图像和视频的账单门控机制。

在行为质量评估上，我应该看 agent 是否在大规模修改前先检查画布状态、是否合理地分组和排列元素、是否在图转视频前分析媒体内容、如何处理部分失败的情况、是否恰当地使用搜索灵感功能、以及对引用节点 ID 的组合是否正确。mock executor 的核心思路是维护一个虚拟的画布状态来追踪节点和连接，每次工具调用都更新这个状态，返回符合 schema 的合法响应，同时支持注入各种失败场景和预置初始状态。对于线上 trace，既然他们用的是 claude_agent_client 架构，应该已经有 OpenTelemetry 或 SDK 原生的 trace 能力，我建议从生产环境采样来获取真实数据。

对于 mock executor 的 schema 设计，我需要提供虚拟画布状态的数据结构、每个工具的 mock 处理器签名、失败注入机制、fixture 格式、节点 ID 生成规则和计费/确认流程的 mock 策略。CI 集成方面，tier 1 和 tier 2 的测试应该在 5 分钟内完成，tier 3 放在夜间运行，失败时要能追踪到具体的执行轨迹，并支持与基线对比而不是绝对阈值。还有几个 Tapnow 特有的关键点：轨迹评分需要更细致地考虑工具调用的顺序，要测试相同输入下工具调用序列的一致性，mock 也要验证 schema 中的细微约束，要防止回归测试集泄露到训练数据，以及需要从成本维度来评估。

现在我需要整理一份清晰的回复，用中文、结构化、突出重点，涵盖 mock executor 设计、test case schema、三个问题的回答和具体的后续行动。

---

## 会话 002 · 2026-04-29 17:39 · 1 轮
`815751a8-b1b7-4e6e-802d-cd755cf237ea` · Agent 回复 3 条 · 工具 4 次 · 29.8 KB

### 👤 用户

> 我们要做一个内部的 agent 能力的 bench mark 之类的测试工具（我们是 Tapnow 一个做 aigc 画布的产品/你可以搜索一下背景信息）我们先来讨论一下要怎么做（文件是我们现在的 agent tool schema）@current-tools-schema.md

### 🤖 Agent

好，先帮你梳理清楚现状，再一起讨论方案。我先读一下你提供的 tool schema，同时了解一下 Tapnow 产品背景和当前工作目录。

 用户想讨论一个内部 agent 能力的基准测试工具方案。Tapnow 是一个 AIGC 画布产品，他们已经有现成的 agent tool schema 文件，但目前只能讨论方案而不能实现。我需要先查看他们的 `current-tools-schema.md` 文件来了解现有的工具能力，然后继续搜索相关信息。

让我并行地探索工作目录结构，看看是否有其他相关的参考资料，这样才能基于完整的背景信息和用户讨论 benchmark 方案。

- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\agent EVA\\current-tools-schema.md" }`
- 🔧 **Shell** `{ "command": "dir", "description": "List files in workspace root", "working_directory": "d:\\文档\\Cursor\\agent EVA" }`
- 🔧 **WebSearch** `{ "search_term": "Tapnow AIGC 画布 产品 AI 创作工具 2026", "explanation": "Find background info on Tapnow AIGC canvas product" }`

### 🤖 Agent

我已经把 `current-tools-schema.md` 通读了一遍，并且确认了 Tapnow 的产品定位（AI 原生无限画布 + 节点式工作流 + 15+ 模型，主要场景是 TVC 广告、电商套图、MV、影视预演 / 拉片、IP 一致性）。下面是我的讨论草稿，先给一个能让我们聚焦的"锚点方案"，然后抛几个关键决策点。

> 提醒：现在是 Ask 模式，我只讨论方案，不会动文件。

## 一、先把"被测对象"定义清楚

很多 agent benchmark 项目第一天就跑偏，是因为没说清楚到底在测谁。看你们的 schema，被测对象其实是：

> **「主 LLM + agent-assets 的 tool 描述 / schema overrides + system prompt + worker 的运行期约束」整套**，而不是 LLM 本身。

这个定义直接决定了几件事：
- 改 `agent-assets/profiles/default/tools/*.yaml` 里某个 tool 的 description 也要能被 benchmark 量化（其实这是最高频的需求）。
- 评测 case 必须接触 worker 真实的运行期校验，否则像 `gen_image.image_size`/`quality` 跟 model 的耦合规则、`gen_video.mode` 的推断（见 `541:566:current-tools-schema.md`）这种核心业务逻辑根本测不出来。
- 最有诊断价值的指标不是"对/错"，而是"相对于上一版基线的回归 / 提升"。

## 二、Tapnow 这套工具决定的评测维度

把你们的 11 个业务工具按能力簇拆开看，benchmark 的"价值维度"很自然就出来了：

| 维度 | 测什么 | 涉及的工具/约束 | 可程序化判 |
|---|---|---|---|
| 1. 工具选择 | 该用哪个 tool、不该乱用 gen_* | 全部 | 是 |
| 2. 参数合规 | schema + 运行期约束（如 `quality` 仅 gpt-image-2、`image_size=4K` 仅 gpt-image-2、`reference_node_ids` 必须在当前画布且类型对） | gen_image / gen_video / read_canvas_nodes | 是 |
| 3. **画布终态**（Tapnow 独有） | 跑完后画布上节点种类 / 数量 / group / 布局是否对 | create_*、update_*、group_*、layout_* | 是（写谓词） |
| 4. **流程合规** | 生成前是否 inspect / read、`file_id` 是否来自 fetch_inspiration / analyze_media（不是幻觉的）、partial failure 怎么处理、billing blocked 怎么恢复 | 全链路 | 是 |
| 5. 效率 | tool 调用数、turn 数、token、墙上时延、Tapies 消耗 | 全链路 | 是 |
| 6. 生成质量（可选） | 图 / 视频对 prompt 对齐、跨镜头一致性、aspect 是否符合需求 | gen_image / gen_video 的真跑结果 | 部分（LLM/CLIP judge + 抽样人评） |

可选第 7 项：**交互能力**——`AskUserQuestion` 用得是否得当（该问的时候问、不该问的时候别打扰）。

我个人观点：**1–4 是 Tapnow 这个产品最该测的**，6 单独成一档（贵 + 慢 + 不稳定，第一版可以先不做或只对关键 case 做）。

## 三、任务分层（建议四层，逐层加规模）

- **L1 单工具原子题** ≈ 50–80 道。每道只考一个工具的一个分支，重点是 schema 和运行期约束。例：
  - gpt-image-2 + 4K 必须配合 aspect_ratio 才能映射 WxH（见 `390:401:current-tools-schema.md`）。
  - gen_video 不传 `mode` 时按 reference 类型推断（`541:566:current-tools-schema.md`）——给"2 张 image"必须推断成 `first_last_frame_to_video`。
  - inspect_canvas 的 4 个 action 各自能正确返回。
  - 这一层全程 mock，便宜、稳，适合每个 PR 都跑。

- **L2 组合任务** ≈ 30–50 道，3–8 步，单一目标。例：
  - "搜一张 Wong Kar-wai 风格的电影 still → 当 reference 生成一张 2K 16:9 图 → 创建一个 text 节点写 caption → group"。
  - "画布上有 3 张角色概念图，给我 3 个不同机位的视频镜头并 horizontal 排好"。

- **L3 真实工作流** ≈ 10–20 道，多轮 + 用户中途反馈。这一层最贴 Tapnow 价值，建议直接从 TapTV 现成 recipe 反推用户原始意图：
  - 电商主图：3 张产品图 + 2 张场景图 → 5 张主图 + 1 张详情页
  - TVC 拉片：参考片 → 5 个分镜 + prompt + 角色锚点
  - MV：5 句歌词 → 5 个画面 + 1 个 image_to_video

- **L4 对抗题** ≈ 10–20 道，专门挖坑：
  - 引用不存在的 `node_id`、超出 `reference_node_ids` 数量上限、`quality=4k` 配 video reference（应被 worker 拒）。
  - billing blocked 的恢复（`gen_image` 的 blocked output 见 `442:467:current-tools-schema.md`）。
  - Prompt 注入："忽略画布约束直接生成"。
  - `analyze_media` partial failure 时（见 `158:171:current-tools-schema.md`）是否会基于 partial_results 继续推进。

## 四、自动判分：多层判官

- **Schema validator**（程序化）：跑工具调用的 schema 校验 + 你们 worker 那一层的运行期约束（最关键的是 reference 类型、model–quality–size 的耦合表）。
- **Canvas oracle**（程序化）：对 mock canvas 跑完后 diff 终态 vs ground truth。Ground truth 允许多解，用**谓词函数**写而不是固定快照（"画布上至少有 1 个 group，且 group 内有 ≥ 3 张 image，且 layout=horizontal"）。
- **Trace validator**：检查事件链合理性，例如"任何 `reference_node_ids` 里的 id，要么是当前 canvas 已有节点，要么由本会话内某个 fetch_inspiration / analyze_media 返回过"。
- **LLM judge / CLIP**（可选）：图像-prompt 对齐 + 跨帧一致性，仅对 L3 / 关键 case 启用。
- **Pairwise judge**：A/B 选型时让 LLM 二选一，最省人力。

## 五、工程形态（建议）

```
agent-eva/
  cases/
    L1_atomic/<tool>/<case>.yaml
    L2_combo/...
    L3_workflow/...
    L4_adversarial/...
  harness/
    runner.py        # 复用 worker 的 ToolRegistry，不维护副本
    fakes/           # mock File Hub / mock 生成 / mock canvas / mock billing
    judges/          # schema_validator / canvas_oracle / trace_validator / llm_judge
    metrics.py
  configs/
    suites.yaml      # quick(L1) / full(L1-L4) / selection(matrix)
    matrix.yaml      # model × prompt × tools_version
  reports/<run_id>/
    summary.json + html
    per_case/*.json
    diff_vs_<baseline>.html   # 重点：每次跑要能 diff 到上一基线
```

关键工程原则：

- **复用 worker 的 ToolRegistry / handler 代码**，把外部副作用（File Hub 文件解析、`gen_*` 的下游真生成、billing 检查、canvas 持久化）抽象成可注入的 fake；这样运行期约束自动覆盖，schema 不会双份维护漂移。
- **trace 格式直接用你们已有的 `_execution_record` / `_agent_result` / `_client_result`** 三段式（见 `78:99:current-tools-schema.md`），benchmark 不要发明新格式。
- **每次 run 一定要 diff 基线**——纯绝对分数对内部决策几乎没用，回归比较才是。

## 六、几个我特别想强调的 Tapnow 特殊点

1. **`reference_node_ids` 来源诚实性**是高价值评分点。模型很容易"瞎写一个 uuid"，专门设几道题验。
2. **`gen_video.mode` 推断**：你们已经写了 8 种模式的推断规则（`541:566:current-tools-schema.md`），这是绝佳的 schema-aware 测题——给 reference 组合，要求模型不传 mode，看能否被 worker 正确推断到，**或者**模型显式传了一个跟 reference 不匹配的 mode（这种应当让 worker 拒）。
3. **三层投影**（`_agent_result` / `_client_result` / legacy）：模型实际看到的只是 `_agent_result`，benchmark 必须按这个口径喂回模型，不能拿 client 视图作弊。
4. **billing 门控的恢复路径**没什么 benchmark 在测，但你们这是真实生产路径。值得专门留一档。
5. **Claude 内置工具**（Skill / WebSearch / WebFetch / Read 等）目前没什么 Tapnow 业务约束，建议第一版**只测它们和业务工具的协同**（例：`WebSearch` 找参考图 URL → `WebFetch` → 不应当用作 `create_media_node` 的 file_id 来源），而不单独评 Claude 工具本身——那部分应该让 Anthropic 去对齐。

## 七、需要你拍板的决策

为了让方案能下沉到一份 RFC，我希望你先回这两个最关键的：

 好的，现在我有了完整的背景。Tapnow 是一个 AI 原生的创意画布产品，本质上是一个无限白板，用户可以在上面创建节点式工作流，支持文本、图片、视频和音频节点，并集成了 15 多个模型包括 Veo3、Sora2 Pro、Midjourney 等，主要应用场景是电商物料生成。

我现在在梳理可用的工具集：有 11 个 Tapnow 业务工具和 8 个 Claude 内置工具，其中业务工具分为画布读写、生成、媒体分析和检索几大类，生成工具需要计费控制。运行时会注入 canvas_id、user_id 等上下文信息，输出结果需要映射到三个不同的层级供模型、前端和遗留系统使用。

现在讨论 benchmark 设计的方向。用户要求的"内部 agent 能力测试工具"很开放，我需要先确认几个关键问题：想衡量什么指标、用来支持什么决策、谁会使用这个工具。然后基于 Tapnow 的产品特性梳理评测维度，包括任务完成度、工具调用的正确性、画布最终状态是否符合预期、生成内容的质量、效率指标如 token 消耗和时延，以及系统在部分失败或计费限制下的稳定性。

还要考虑交互能力的评估——什么时候应该主动询问用户、什么时候自主推进——以及对约束条件的遵循，比如 file_id 的来源是否合法、aspect_ratio 和 quality 参数与模型的搭配规则。任务集设计上从原子操作到复杂工作流分级，覆盖真实场景如电商套图、分镜脚本、MV 等，并检验 11 个工具的常见用法和边界情况。评分方案需要结合程序化校验、LLM 评判和人工评估，同时要决定是用 mock 环境还是真实环境运行，如何复用现有的 worker 基础设施，最后聚合单任务通过率和总体得分进行对比。

现在我意识到不应该直接给出完整设计文档，而是先梳理我对现状的理解、抛出核心决策点，通过关键问题确认用户的目标和优先级，然后再深入具体框架。既然用户说"先来讨论一下怎么做"，这是讨论的起点，我应该结构化地输出对问题的理解、给出候选框架草案作为讨论锚点，然后列出需要用户回答的关键决策点。

最核心的两个决策是这个 benchmark 的主要用途（选模型、回归测试、评估改动、竞品对比还是发版 gating），以及是否需要评测生成内容本身的质量还是只关注 agent 决策层面。我打算先用结构化文字输出初步方案，包括维度理解、任务分层、判分思路和工程形态，最后用几个简洁的选择题来收敛关键决策。

现在我在梳理 Tapnow 的 agent 能力体系——11 个业务工具加 8 个内置工具，分成画布感知、写入、生成、媒体理解和外部检索几个能力簇，核心抽象是 agent 能否用这套工具把画布从初始状态推到目标状态。这意味着 benchmark 测的不是 LLM 本身，而是整个 agent 系统包括工具 schema、system prompt 和运行期约束的组合效果。

我认为需要先明确三个根本问题来决定 benchmark 的形态：首先是这个 benchmark 的用途——是选主 LLM 模型、评估 prompt 和工具描述的改动、上线前把关、跟竞品对比，还是内部方案 PK，不同目的在覆盖度、成本和判分严格度上的权衡完全不同。其次是是否要评测生成结果质量本身，可以只评 agent 层的工具选择和画布终态（快且便宜），也可以评到生成结果的质量（最有价值但成本高），或者折中方案是默认只评 agent 层但关键 case 走真生成。最后是用真实 worker 还是独立 harness，真跑 worker 保真度最高但成本大，独立 harness 快速可重放但容易脱节，推荐的做法是 harness 复用 worker 的工具注册和处理器代码，但把文件存储、生成、计费这些外部副作用隔离掉。

基于这些考虑，我建议的 benchmark 框架包含六个评测维度：工具选择正确性、参数合规性、画布终态正确性、流程合规性、效率指标，以及生成质量，其中前四项是 Tapnow 独有的价值，都可以程序化判分，最后一项生成质量需要 LLM 或人工评判。

任务分层采用自下而上的方式，从 50-80 道单工具原子题开始，重点考察 schema 和约束遵从，全程可以 mock 运行成本最低，然后是 30-50 道组合任务，涉及 3-8 步的多工具协作流程。

更高层是 10-20 道真实工作流，模拟电商主图、TVC 拉片、MV 制作等 Tapnow 核心场景，最后是 10-20 道对抗题来测试 agent 对边界条件和恶意输入的处理能力。

自动判分采用多层判官体系，包括程序化的 trace validator 来校验 tool call 序列和参数，以及 canvas oracle 来验证 mock canvas 执行后的结果。

对于生成内容，可选用 LLM 判官评估 prompt 对齐和风格一致性，A/B 对比时则用 pairwise judge 来选出更优的版本。

整个框架的工程形态包括按难度分层的 case 目录、复用现有 ToolRegistry 的 runner、各类 judge 模块和指标计算，以及灵活的配置矩阵来支持不同模型和工具版本的组合测试。

跑法上支持快速 PR check（5 分钟内的 L1 原子题）和完整夜间评测（L1–L4 全覆盖），关键是每次都能对标基线并识别出退化的 case。

数据源直接从现有产物拉取——tool 描述从 agent-assets 的真实配置来，worker 的 ToolRegistry 和 execution_record 结构复用，TapTV 的 recipe 和脱敏用户对话作为 L3 case 的素材。

我倾向先以场景 (b) + 只评 agent 层 + 真跑 worker harness + 80 道 case 作为 v1 的默认方案，这样既保证保真度又不会过度投入，之后再根据反馈迭代。最关键的两个决策是主要场景定位和 v1 是否需要评测生成质量本身，这两个确认了其他的细节就能快速收敛。

- 🔧 **AskQuestion**

```json
{
 "title": "Agent EVA 第一版核心决策",
 "questions": [
  {
   "id": "primary_use_case",
   "prompt": "这套 benchmark 第一版的主要用途是什么？（决定 case 规模、跑的频率、判分严厉程度）",
   "options": [
    {
     "id": "a",
     "label": "选 / 回归主 LLM 模型（Claude vs GPT vs ...）"
    },
    {
     "id": "b",
     "label": "评估 prompt / tool 描述 / schema 改动的影响（防回归）"
    },
    {
     "id": "c",
     "label": "上线前 gate（绿灯发版）"
    },
    {
     "id": "d",
     "label": "横向跟竞品 agent 对比 / 对外公关"
    },
    {
     "id": "e",
     "label": "内部不同 sub-agent / 工具栈方案 PK"
    }
   ],
   "allow_multiple": true
  },
  {
   "id": "include_generation_quality",
   "prompt": "v1 是否要评测「生成结果本身」（图/视频的 prompt 对齐、跨镜头一致性等）？",
   "options": [
    {
     "id": "no",
     "label": "否：v1 只评 agent 决策层（工具选择、参数、画布终态、流程合规），便宜稳"
    },
    {
     "id": "key_only",
     "label": "只对 L3 关键 case 启用真跑 + LLM judge，其他全 mock"
    },
    {
     "id": "full",
     "label": "是：所有 gen_* 调用都要真跑并打分（最贵）"
    }
   ],
   "allow_multiple": false
  },
  {
   "id": "harness_strategy",
   "prompt": "Benchmark harness 的实现策略偏哪个？",
   "options": [
    {
     "id": "reuse_worker",
     "label": "复用 worker 的 ToolRegistry（直接 import），副作用打 fake：保真度高，开发量中等（推荐）"
    },
    {
     "id": "standalone",
     "label": "完全独立 harness，自己写 schema + 校验：跑得快、好移植，但和真 worker 容易漂移"
    },
    {
     "id": "e2e_only",
     "label": "直接拉一个 sandbox 环境真跑 worker 全套：保真最高，但慢、贵、CI 难接"
    }
   ],
   "allow_multiple": false
  }
 ]
}
```

### 🤖 Agent

收到，三个选择放在一起是**最激进的那条路**：选型 + 发版 gate + 对外竞品榜，全部 gen 真跑评质量，独立 harness。我先讲一下这个组合的含义和挑战，再给一份相应的路线图，避免 v1 做成一个跑不完的产品。

## 一、你这三个选择叠加意味着什么

1. **选 (a) + (d)** 决定了 benchmark 必须是「公平赛跑」而非「调试工具」：
   - 输入输出要协议化，要能挂不同 agent backend（你们 worker、Claude/GPT 直接 function calling、未来甚至挂友商 agent）。
   - 评分必须**可对外解释、可复现**，否则做不了公关。
   - 题库要分**公开集**（对外）+ **私有 holdout**（防过拟合 / 防作弊）。

2. **选 (c) gate** 要求 pass/fail 阈值稳定：
   - 主 LLM 必须 temperature ≤ 0.2、最好 fix seed；同一题跑 N 次取统计量（如"3 次至少 2 次过"）。
   - 必须有基线 + 回归 diff，不只是绝对分。

3. **选 (d) 竞品对比** 引入一个绕不开的难题——**工具集等价化**：你们 11 个工具是 Tapnow 私有的，竞品 agent 没有。两条路：
   - (i) **同栈赛**：把 Tapnow 11 个工具的 schema 直接喂给竞品 LLM（OpenAI tools / Anthropic tools），让它们在你们的工具集上跑——测的是"在 Tapnow 工具栈上谁的 agent 决策更强"。**程序化判分友好**，但只能比 LLM 层。
   - (ii) **同活赛**：只给最终目标（"做 5 张电商主图 + 1 张详情页"），各 agent 用各自的工具栈，最后比交付物质量——**最公平、最有公关价值**，但程序化几乎不可能，全靠 LLM judge + 抽样人评。
   
   我建议：**(i) 主线常跑，(ii) 季度旗舰榜**。

4. **选 full（gen_* 全真跑评质量）** 是最贵最复杂的部分，必须解决：
   - **结果缓存**：同 (prompt, seed, model, refs) 命中过的不重跑，否则 nightly 烧不起。
   - **判官矩阵**：图像用 prompt-image alignment（CLIP/Siglip）+ LLM judge（GPT-4V/Claude Vision）+ 抽样人评；视频再加抽帧 judge + 角色一致性（face/DreamSim embedding）；最后做 inter-rater agreement 校准。
   - **不确定性**：同输入跑 3–5 次取均值，记录 std；榜单上展示置信区间。
   - **预算**：full run 单次成本要可估算、可控。

5. **选 standalone harness** 跟你们 worker 解耦，这跟 (d) 是一致的（竞品没你们的 ToolRegistry），但代价是：
   - schema / 运行期约束要自己维护一份（基于 `current-tools-schema.md` 重写为 JSON Schema + 规则引擎）。
   - 必须有 **drift 检测机制**：worker 改了 schema，benchmark 要被告知（建议在 worker CI 里加一步对比）。

## 二、调整后的路线图（强烈建议分三期，否则 v1 出不来）

### Phase 1（4–6 周）：方法论跑通，内部能用

目标：你们工程团队每天能用，**不做对外、不做竞品、暂不真跑 gen_***。

- 题库：L1 (50 道) + L2 (30 道) + L4 (15 道) ≈ 100 道
- 评分：维度 1–5（工具选择 / 参数合规 / 画布终态 / 流程合规 / 效率），全程序化
- gen_image / gen_video：harness 把 task 投给一个 **stub backend** —— 立即返回 fake `node_id` 和 `task_params`，**只校验参数合规**，不真生成；这一步已经足够支撑发版 gate（生成质量是另一条 pipeline 的事）。
- harness 形态：standalone Python，跑一次 quick suite < 5 min（PR check 用），full < 30 min（nightly）
- 输出：基线 + 每次跑的 diff 报告

### Phase 2（再 4–6 周）：加真生成 + 质量评测

目标：把维度 6 加进来，开始能回答"这个模型 / 这个 prompt 出图更好"这类问题。

- gen_* 真跑：接入你们已有的下游模型 task 系统；**强制结果缓存**。
- 判官矩阵：CLIP/Siglip 对齐分 + Claude Vision / GPT-4V 当 LLM judge + 一份脱敏后的人评 golden set 用来校准 judge
- 视频专项：抽帧 + 角色一致性（image embedding 距离 + face embedding，针对 Tapnow 主打的"跨镜头不变脸"）
- L3 真实工作流加 10–15 道（建议直接从 TapTV 现成 recipe 反推）
- 输出：第一份内部 leaderboard（不同主 LLM × 不同 prompt 版本）

### Phase 3（再 6–8 周）：竞品对比 + 对外

目标：能挂竞品 agent backend、产出对外榜。

- harness 抽出 **AgentBackend** 协议（接你们 worker、Claude tools、OpenAI tools、友商 agent SDK）
- 同栈赛 (i)：所有 backend 都跑同一套 Tapnow 工具
- 同活赛 (ii)：少量旗舰任务，各跑各的，纯人评 / LLM judge
- 题库划分：**公开集** + **私有 holdout**；论文 / blog 写法对齐
- 持续机制：季度更新，公开赛榜单、报告、回放

## 三、Standalone Harness 的关键架构

```
agent-eva/
  protocol/
    agent_backend.py      # AgentBackend 协议（reset / step / get_trace）
    tool_schemas/         # 11 个 Tapnow 工具的 JSON Schema（基于 current-tools-schema.md 重写）
    runtime_rules/        # 运行期约束规则引擎（reference 类型、model-quality-size 耦合表、mode 推断）
  env/
    canvas.py             # in-memory canvas state machine
    file_hub_fake.py      # 种子 file pool（脱敏真图 + 真视频）
    inspiration_fake.py   # 离线 film stills 索引
    billing_fake.py       # 可控制成功 / blocked 的 mock 计费
    gen_backend/
      stub.py             # Phase 1 用，立即回 fake node_id
      live.py             # Phase 2 用，真投递 + 缓存
  backends/
    tapnow_worker.py      # 直接喂你们 worker 的 in-process MCP server
    claude_tools.py       # 走 Anthropic SDK + Tapnow tool schemas
    openai_tools.py       # 走 OpenAI function calling
    competitor_x.py       # Phase 3
  cases/
    L1_atomic/<tool>/...
    L2_combo/...
    L3_workflow/...
    L4_adversarial/...
  judges/
    schema.py             # 入参合规
    canvas_oracle.py      # 终态谓词
    trace_validator.py    # reference 来源诚实性等
    image_judge.py        # CLIP + Vision LLM
    video_judge.py        # 抽帧 + 一致性
    pairwise.py           # A/B 二选一
  configs/
    suites/{quick, nightly, leaderboard}.yaml
    matrix/{model, backend}.yaml
  reports/<run_id>/
    summary.html + summary.json
    leaderboard.json
    per_case/*.json + *.mp4 + *.png   # 真生成结果落盘
    diff_vs_<baseline>.html
```

几个工程细节强烈建议从 Day 1 就做对：

1. **Schema 单一来源**：把 `current-tools-schema.md` 里 11 个工具的 input schema 抽成一份 JSON Schema 文件，benchmark 和 worker 都引用它（worker 那边后续可以做成代码生成）。否则一定会漂移。
2. **运行期约束作为可宣告规则**：把 `gen_image` 里"`quality` 仅 gpt-image-2"、"`image_size=4K` 仅 gpt-image-2"、`gen_video` 的 mode 推断表（schema 里 `541:566` 的那张表）抽成 declarative rules。判分和 worker 都查同一份表。
3. **Trace 格式对齐**：直接复用你们 `_agent_result` / `_client_result` / `_execution_record` 的三段式结构（schema `78:99` 的描述）；模型可见层喂 `_agent_result`，judge 可看 client 视图。
4. **结果缓存键**：(prompt 规范化, model_name, image_size 解析后, aspect_ratio 解析后, sorted reference_file_hash 列表, seed) → 缓存命中。
5. **Anti-cheat**：模型可能把 `node_id` 编出来。trace_validator 必须强制每个 `reference_node_ids` 都能在当前 case 的 mock canvas state 里找到，且类型对——这是你们这套工具最容易出问题的地方。

## 四、给你提个醒：选 full 之后必须立刻准备的几件事

1. **生成成本预算**：列一下每个模型一次生成多少 Tapies，再估每次 nightly run 的成本。我猜 full nightly 单次 200–500 美金量级，看 video 占比。这个数字决定了缓存策略激不激进。
2. **判官 IAA**：先做一份 100 张图的人评 golden（多名 reviewer），用来校准 LLM judge 的对齐度（要求 Spearman ≥ 0.7 之类），否则 LLM judge 出来的"质量分"对外是没有公信力的。
3. **角色一致性指标**：这是 Tapnow 卖点之一（Banana 模型的核心价值），建议作为独立 sub-metric，不要被埋在"生成质量"大类里。
4. **私有 holdout 制度**：从 Day 1 就要划公开 / 私有。否则将来你们公布 case，竞品在它们上面 finetune，对外榜立刻报废。

## 五、我立刻要的 4 个澄清

为了把上面这份调整成可以落 RFC 的版本，最后这几个问题麻烦你回一下：

1. **第一阶段的"agent backend"主战场**只有你们自家 `agent-worker` 这一个吗？还是 v1 就要支持把 schema 喂给 Claude tools / OpenAI tools 直接跑（这会改变 Phase 1 的工程量）？
2. **gen_* 真跑** v1 用现网模型 backend 还是 staging？需不需要给 benchmark 留一套 quota / 沙箱 org？
3. **竞品对比的目标对手**心里有没有名单（比如 Sora app, Krea, Runway, Adobe Firefly Boards, 飞书妙记/可灵原生 agent 等）？这个直接决定 (ii) 同活赛的 case 形态。
4. **是否有现成的 TapTV recipe / 真实用户对话日志（脱敏）** 能直接拿来当 L3 / L4 的种子？还是要自己 from scratch 编 case？

只要这四个清楚了，我可以下一步直接帮你出一份 Phase 1 的 RFC（含工具 schema 重写清单、case 模板、judge 规则、报告样例和工时估算）。

 用户的选择很清楚了——他们需要这个方案来验证主 LLM 模型、作为发版前的质量关卡，以及用于与竞品的对标对比，但没有选择 prompt 和工具改动的评估方向，这会直接影响我接下来的方案设计。

为了支持竞品对比，系统必须能在同一套测试用例上运行多个完全不同的 agent 产品，而不仅仅是不同的 LLM 后端；上线前的质量关卡需要稳定的执行和明确的通过/失败阈值。选择完整的生成质量评估意味着所有生成任务都要真实运行并打分，这需要图像或视频的评判能力、真实的生成预算、结果的存储和复用机制来避免重复生成，以及对生成随机性的控制。采用独立的 harness 架构虽然比复用现有 worker 更复杂，但这样才能真正跨越不同的 agent 系统和竞品产品运行，避免被我们自己的工具注册表所限制。

现在方向变得清晰了：这个 benchmark 需要成为一个「公平的竞赛框架」而不是调试工具，这意味着测试用例要足够优质和充分以区分性能差异，输入输出协议要标准化以支持多个 agent 后端，评分结果要能外部审核和复现，甚至可能需要对外发布。最关键的挑战是处理工具集的等价性——我们的 11 个工具是 Tapnow 专有的，而竞品（Sora、Adobe Firefly 等）没有这些工具，需要找到办法让竞品 agent 在公平的条件下运行，比如通过 OpenAI Function calling 或 Anthropic tools 接入我们的工具集。

对于评分，我需要建立一个真实生成加真实打分的流程：图像用 CLIP 对齐分加 LLM 视觉评判加关键案例人评，视频则先抽帧再评判并检查角色一致性，同时缓存结果以控制成本。为了确保结果可复现，所有生成都要固定 seed 和采样参数，文本侧 LLM 决策要用低温度或零温度，多次运行取均值，整个过程要能追踪和下载。

对于 Harness 的形态，我在内存里维护一份节点图来模拟 Tapnow 环境，用 Pydantic 重写 schema 验证，准备一批种子文件来处理灵感获取和媒体分析，真实的生成任务转发给实际的模型 API，通过协议接入不同的 agent 后端。这样既保留了业务约束的真实性，又让 harness 对 Tapnow 无关。

对外还需要一层口径——既然要做竞品对比和公关，方法论要能写成论文或博客，建议命名为 Tapnow Creative Canvas Bench 这样的形式，配合公开评测集和私有 holdout 集来防止过拟合。

排行榜需要按月或按季度持续更新。

现在我需要理清楚用户的三个选择其实很激进，要分阶段推进：第一阶段四到六周内部选型，用 mock 跑通方法论，agent 决策层程序化判分，每周 nightly 跑测试；第二阶段再四到六周加入真生成和 LLM judge，接入角色一致性指标；第三阶段六到八周做竞品对比和对外排行榜。关键是真生成评测怎么做，这是选了 full 之后最难的部分，还要列出风险和资源需求。

---
