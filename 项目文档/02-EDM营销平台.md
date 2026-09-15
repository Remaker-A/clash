# EDM 多 Agent 邮件营销平台（TapNow EDM Service）

> 工作区：`D:\文档\Cursor\EDM` ｜ 会话数：**313**（全项目最多）｜ 提问轮次：**902** ｜ 时间跨度：2026-04-13 ~ 2026-06-23
> 本文基于 Cursor 全部 313 轮会话记录 + 项目现存的 README.md / AGENTS.md 整理

---

## 一、项目做了什么

**一句话**：把「活动简报 → 受众选择 → 策略制定 → 邮件生成 → 多语种翻译 → 定向发送 → 追踪反馈」整条链路，拆成若干**自治 AI Agent**，做成工程化编排、可观测、可回放、可治理的企业级 EDM 服务。

这是一个从零到一、**持续迭代了两个多月**的项目，也是整个 Cursor 使用史中投入最大的一个（313 个会话 / 902 轮提问 / 累计 902 轮）。

### 演进主线

| 时间 | 阶段 | 关键转变 |
|---|---|---|
| **04-13** | 需求对齐 + 架构设计 | 从「自动化会议整理.md」开始探讨细节，确定模板库 + 参数化配置路线 |
| **04-13 ~ 04-14** | 前后端脚手架 | Vite+React+TS 前端、FastAPI+SQLAlchemy 后端全面落地 |
| **04-15** | **AI 自主决策重构** | 砍掉人为编辑，把分层、语气、写作策略交给 AI 自主决策 |
| **04-15** | **Prompt → Skill 升级** | 用 `/skill-creator` 把单条 prompt 升级为完整 Skill |
| **04-16** | **Multi-Agent 重构** ⭐ | 砍掉死板的 S/A/B/C 分级，改成多 Agent 协作 + 行为标签驱动 |
| **04-16** | 砍掉模板选择 | 让 Agent 自主写 content，不再受模板限制 |
| **04-17** | 发信体系 + Agent 0 | SES 配置、Agent 0 接管受众选择、Brief Preflight、HTML 视觉打磨 |
| **04-20** | **Harness Engineering** ⭐ | 按 Anthropic/OpenAI/Fowler 的方法论做工程化加固 |
| **05-27 ~ 05-28** | 架构梳理 | 梳理模块、Agent 编排、删去 Preflight |
| **06-02 ~ 06-03** | 部署上线 | 部署到 GCP VM，docker-compose 跑起来 |
| **06-18 ~ 06-23** | 回调接入 | 腾讯云 SES 回调接入，打通送达/打开/点击追踪 |

---

## 二、用了什么技术

### 2.1 后端 `edm-backend`

| 层 | 选型 | 版本 |
|---|---|---|
| 运行时 | Python | 3.11 |
| Web 框架 | FastAPI + Uvicorn + Gunicorn | 0.115+ |
| ORM | SQLAlchemy（**async**） | 2.0+ |
| 数据库迁移 | Alembic | latest |
| 数据库 | PostgreSQL（生产）/ SQLite（本地） | 16+ |
| 模型层 | Pydantic v2 + pydantic-settings | 2.x |
| 认证 | PyJWT + bcrypt + email-validator | — |
| 定时任务 | APScheduler | 3.10+ |
| 邮件 | **腾讯云 SES**（SDK + SMTP 双通道） | 3.x |
| DNS | dnspython（**发信身份体检**） | 2.6+ |
| 模板 | Jinja2 | 3.1+ |
| CSV | pandas | 2.x |
| 对象存储 | google-cloud-storage | 2.16+ |
| AI SDK | httpx（统一 HTTP 客户端） | 0.27+ |
| 测试 | pytest + pytest-asyncio | 8.x |

### 2.2 前端 `edm-frontend`

| 层 | 选型 | 版本 |
|---|---|---|
| 运行时 | Node.js | 20+ |
| 构建 | Vite | 6.x |
| 语言 | TypeScript | 5.6 |
| UI 框架 | React | 18.3 |
| 组件库 | **Ant Design** | 5.22+ |
| 状态管理 | Redux Toolkit + react-redux | 2.x |
| 路由 | react-router-dom | 6.28+ |
| 图表 | ECharts + echarts-for-react | 5.6+ |
| 编辑器 | Monaco Editor | 4.x |
| 静态托管 | Nginx | 1.25+ |

### 2.3 AI 多 Provider 抽象

同一份代码可同时接入：**OpenAI / DeepSeek / 腾讯混元 / Google Gemini / SiliconFlow**

- 按 `AI_CONTENT_PROVIDER` / `AI_TRANSLATE_PROVIDER` **热切换**
- 单一 Provider 限流或下线**不会拖死整条管线**

> 实战中确实换过多次：Gemini 3.1 flash / `google/gemini-3.1-flash-lite-preview`，以及网关代理的 Claude。

### 2.4 云原生部署

首日即按 **Cloud Run** 拓扑设计：

- **HTTP Service**（按请求伸缩）＋ **Worker Service**（`min=max=1, concurrency=1` 单实例）**分离部署**
- 上传图片默认走 **GCS**，邮件 HTML 里的图床地址即公网 CDN
- Secret Manager + Cloud SQL + Cloud Scheduler 全托管
- 同一套镜像也能用 `docker-compose.yml` 在裸机或 K3s 自托管

**实际部署**：GCP VM `tap-testing-edm.tamaredge.host`（`***REDACTED-IP***`），docker-compose 起容器。

---

## 三、具体是怎么设计的

### 3.1 系统架构 ⭐

```
用户浏览器
  │
  ├─ HTTPS → edm-frontend (Nginx + Vite 静态)
  │            └─ /api/*  反向代理 ────┐
  │                                  ▼
  │                         edm-backend (FastAPI + Gunicorn)
  │                              │
  │                              ├─ PostgreSQL (Cloud SQL)
  │                              ├─ GCS / 对象存储 (上传 & 邮件图片)
  │                              ├─ AI Providers (OpenAI / DeepSeek / …)
  │                              └─ 腾讯云 SES (SMTP / API 发信)
  │
  └─ HTTPS → 邮件里的追踪链接
               ├─ /t/o/*   打开像素   → edm-backend
               ├─ /t/c/*   点击跳转   → edm-backend
               └─ /t/u/*   一键退订   → edm-backend

腾讯云 SES ─Webhook→ /webhooks/tencent-ses → edm-backend  (投递状态回传)
Cloud Scheduler ─Pub/Sub→ edm-worker                      (定时批量发送)
```

**运行时组件的伸缩策略**（关键设计）：

| 组件 | 角色 | 伸缩 |
|---|---|---|
| `edm-backend` (HTTP) | REST API + **SSE** `/ai/auto-generate` 生成流 | 按请求伸缩 |
| `edm-worker` | APScheduler + SendService dispatcher 循环 | **严格 `min=max=1, concurrency=1`** |
| `edm-frontend` | Nginx 托管静态 + 反代 `/api` | 按请求伸缩 |
| `PostgreSQL` | 业务数据、Trace、Suppression、Sender Health | Cloud SQL HA |

> ⚠️ **重要工程细节**：进程内 scheduler 只在 `edm-worker` 里开启（`SCHEDULER_ENABLED=true`），HTTP service 严格 `SCHEDULER_ENABLED=false`，**杜绝多副本重复 cron**。

### 3.2 多 Agent 管线 ⭐⭐

这是整个项目最核心的设计。

```
                 ┌───────────────────────────────────────────────────────┐
素材 + 简报 ───▶ │  Preflight                                             │
                 │    └─ 只读素材，不写文案，输出缺口与追问               │
                 ├───────────────────────────────────────────────────────┤
收件人数据 ───▶ │  Audience Selector (Agent 0)                           │
                 │    └─ 决定发给谁 + 怎么分组 → AudienceSelection         │
                 ├───────────────────────────────────────────────────────┤
                 │  Strategy Planner (Agent 1)                            │
                 │    └─ 每组差异化策略 + acceptance_criteria             │
                 │        (意图/语气/CTA/避讳/个性化建议)                  │
                 ├───────────────────────────────────────────────────────┤
                 │  Content Writer (Agent 2)                              │
                 │    └─ 基础语种完整 HTML → ContentFields + AIDecisions  │
                 │    ↑                                                    │
                 │    ├── Content Validator  (机械门)                     │
                 │    └── Content Evaluator  (LLM Judge / 六维评分)       │
                 ├───────────────────────────────────────────────────────┤
                 │  Translator (Agent 3)                                  │
                 │    └─ 目标语种 → ContentFields                         │
                 │    ↑                                                    │
                 │    ├── Translation Validator (机械门)                  │
                 │    └── Translation Checker   (高风险语种 LLM Judge)    │
                 └───────────────────────────────────────────────────────┘
                                      │
                                      ▼
                        SSE 事件流（逐组逐语种推送）
           profiling_complete → group_defined → strategy
           → ai_decision → content_ready → translation_ready → done
```

**各 Agent 职责表**：

| Agent | 角色 | Prompt 入口 | 业务入口 | Schema 输出 |
|---|---|---|---|---|
| **Preflight** | 素材理解预检，不写邮件，只列缺口与追问 | `prompts.py::build_material_preflight_system_prompt` | `AIService.preflight_material` | `MaterialPreflightResponse` |
| **Audience Selector (Agent 0)** | 读简报 → 决定发给谁 + 怎么分组 | `build_audience_selector_system_prompt` | `AIService.select_audience` | `AudienceSelection` |
| **Strategy Planner (Agent 1)** | 为每组生成差异化策略 + acceptance_criteria | `build_strategy_planner_system_prompt` | `AIService.plan_strategies` | `dict[str, GroupStrategy]` |
| **Content Writer (Agent 2)** | 根据策略生成完整邮件 HTML | `build_content_writer_system_prompt` | `AIService.generate_content` | `ContentFields` + `AIDecisions` |
| **Translator (Agent 3)** | 把基础语言译成其他语言 | `_build_translate_system_prompt` | `AIService.translate_content` | `ContentFields` |
| **Content Evaluator** | 独立 LLM Judge，六维打分 + criteria 校验 | `prompts/agents/evaluators/content_evaluator.md` | `evaluators.evaluate_content` | `ContentEvalReport` |
| **Translation Checker** | 高风险语种翻译评审（ja/ko/ar/th/zh-TW） | `evaluators.translation_checker` | `evaluators.evaluate_translation` | `TranslationEvalReport` |

> 所有 Agent 的 Pydantic Schema 集中在 `edm-backend/app/schemas/ai.py`；Prompt 集中在 `app/agent/prompts.py` 与 `prompts/` 下的 Markdown 文件。

### 3.3 受众画像：抛弃 S/A/B/C 分级 ⭐

**这是用户主动推翻的第一版设计。**

原本用 S/A/B/C 四级分类，用户觉得"**太死板、限制了 Agent 自由度**"，改为**多维行为标签驱动**：

| 维度 | 取值 | 用途 |
|---|---|---|
| `lifecycle_stage` | new_inactive / onboarding / active / power_user / declining / dormant / churned | 生命周期 |
| `activity_level` | 0–1 连续值 | 活跃度 |
| `subscription_plan` | Free / Basic / Pro / Ultimate / Max | 付费梯度 |
| `payment_willingness` | high / medium / low / none | 付费意愿 |
| `engagement_score` | 0–1 连续值 | 综合互动评分 |
| `feature_adoption_depth` | shallow / moderate / deep | 功能渗透 |
| `churn_risk` | low / medium / high / critical | 流失风险 |

**流程**：系统先自动分桶（`loyal_power_users` / `paid_active_users` / `active_free_users` / `casual_free_users` / `new_users` / `declining_users` / `dormant_users` / `churned_users`），再交给 Strategy Planner Agent **按需细分或合并**，每组独立制定差异化策略。

**设计理念**（用户原话的意思）：

> 我们想要的是 AI 根据用户的信息或状态**自动编写**邮件内容。比如用户突然不用了，我们识别用户状态，编写"为什么不用"——是他不会用，还是暂时有问题——然后给到一些独特的东西。**核心目的是促进用户使用产品**：引导新用户、召回流失用户、推动付费转化。

**落地时机**：Agent 0 接管了"选择用户"这一步。用户发现 Agent 0 的意图识别有问题（说"面向所有活跃用户"却只选了下降用户和新注册用户），专门做了 **Agent 0 分组策略优化**。

### 3.4 Harness Engineering 三层保护 ⭐

项目专门参考了三份方法论（Anthropic / OpenAI / Martin Fowler 的 Harness Engineering），为**每个 Agent 配三层保护**：

| 层 | 名称 | 位置 | 作用 |
|---|---|---|---|
| **1** | **机械门**（Behaviour harness） | `app/agent/validators/` | **零成本硬规则**，LLM 返回后立即判定，硬违规触发重写 |
| **2** | **LLM Judge**（Generator-Evaluator pair） | `app/agent/evaluators/` | 另一个 LLM 当评审者（软门），打分 + 逐条校验 acceptance_criteria |
| **3** | **Trace / Prompt-as-Data** | — | 全量 trace，按 `run_id` 回放 |

**机械门守护对象**：

| 文件 | 守护对象 | 规则编码位置 |
|---|---|---|
| `content_validator.py` | Content Writer 输出 | `validate_content()` |
| `translation_validator.py` | Translator 输出 | `validate_translation()` |
| `audience_validator.py` | Audience Selector 输出 | `validate_audience()`（仅 warn） |

**灰度与预算控制**：`EVAL_ENABLED` / `EVAL_CONTENT_MAX_RETRY` 等 settings。

### 3.5 可观测性：三级 Trace ⭐

每一次 `auto_generate` 都留下完整的 **AgentRun / AgentStep / AgentEvent** 三级 trace，前端 `/traces` 页面可以**像看 Jaeger 一样回放**：

```
Run #01K … auto_generate
 ├─ step 1 preflight      prompt v3   eval_score=4.5/5   42s
 ├─ step 2 select_audience prompt v2  violations=[]      8s
 ├─ step 3 plan_strategies prompt v7  eval_score=4.8/5   18s
 ├─ step 4 generate_content(zh-CN)   eval_score=4.7/5   35s
 └─ step 5 translate(en,ja,ko,ar,th) checker=pass        1m12s
```

> 这是「可回放、可治理」的关键 —— 出问题能精确定位到**哪个 Agent、哪个 prompt 版本、哪一步**。

### 3.6 面向送达率的发信体系 ⭐

这部分工程密度很高，直接决定邮件能不能进用户收件箱：

- **发信身份体检**：启动期 + 执行前**双重检查** SPF / DKIM / DMARC / PTR / TLS，任一硬项不通过**直接拒跑**（避免赔上域名口碑）
- **营销 / 事务发信域物理隔离**：硬红线，`SES_FROM_EMAIL_MARKETING` 与 `SES_FROM_EMAIL_TRANSACTIONAL` 必须不同子域
- **Ramp-up 冷启动爬坡**：`send_ramp.py` 根据发送天数自动放量，避免新域被反垃圾引擎一次性打入冷宫
- **三级限流**：全局 / 分组 / 接收域（基于令牌桶），对 Gmail / Outlook 等大供应商配独立阈值
- **反馈闭环 `send_feedback_loop`**：实时监听 bounce / complaint / unsubscribe webhook，自动降速 / 停跑 / 抑制
- **Suppression List**：永久抑制名单统一落库，**跨活动生效**

**实战配置**：腾讯云 SES，SMTP 走 `smtp.qcloudmail.com:465`（SSL/TLS），发信地址 `news`。

### 3.7 追踪与回调

| 路径 | 用途 |
|---|---|
| `/t/o/*` | 打开像素追踪 |
| `/t/c/*` | 点击跳转追踪 |
| `/t/u/*` | 一键退订 |
| `/webhooks/tencent-ses` | 投递状态回传 |

**公网入口方案**：本地接口 + **Cloudflare Tunnel** 暴露 webhook 给腾讯云 SES 回调。
踩坑：`trycloudflare` quick tunnel 公网不可用，反复重试后才稳定。

### 3.8 内容生成的关键约束

**多语言支持**：至少 日语 / 韩语 / 中文简体 / 中文繁体 / 英语 / 法语 / 德语 / 意大利语 / 西班牙语

**隐私红线**：**HTML 中不要引入用户个性化数据** —— 用户明确要求，展示过多用户数据容易造成反感或隐私担忧。个性化体现在**策略和措辞**，不是把用户数据印在邮件里。

**素材理解预检（Brief Preflight）**：解决"用户输入太简洁，Agent 没理解新功能是什么，就开始瞎编"的问题。

设计要点：
- 素材不够时**主动要求用户补充**，而不是编造
- **追问要克制**：用户强烈反对"填表式"提问 ——「不要这样给我一个表格一样的东西，我来填，很烦」→ 改成**一次问一条，像 GPT 对话那样自然澄清**，3~4 个问题就够

**图文结合**：HTML 支持用户上传顶部/底部装饰图片，**可在预览布局上拖动、编辑、裁剪**。视觉上做了多轮打磨（图片等宽、液态玻璃效果、统一白色文字、字号调整）。

### 3.9 SSE 流式生成

`/ai/auto-generate` 用 **Server-Sent Events** 推送生成进度，事件序列：

```
profiling_complete → group_defined → strategy
→ ai_decision → content_ready → translation_ready → done
```

前端能实时看到**逐组、逐语种**的生成过程 —— 而不是干等一个 loading。

---

## 四、踩过的坑（真实记录）

| 问题 | 表现 | 解决 |
|---|---|---|
| **语言错乱** | 上传选英文，正文却用简体中文写 | 多轮排查修复 |
| **素材图片丢失** | Campaign 已存 `material_image_urls`，最终 HTML 没引用任何图 | 修复 HTML 渲染链路 |
| **邮件进垃圾箱** | 审核确认链接被投到垃圾邮箱 | 排查发信身份 + 内容特征 |
| **AI 生成失败** | 文案含敏感词直接 `Passthrough` 失败 | 改成识别后**帮用户优化**，不过度改动 |
| **分层内容漏生成** | A 层 4 个语言全没生成 | 修复生成调度 |
| **Illegal header value** | 测试环境发信报 `Illegal header value b'Bearer '` | 修 VM 配置缺失 |
| **公网入口不通** | trycloudflare quick tunnel 不可用 | 重试 + 换方案 |
| **Agent 0 意图偏差** | 说"所有活跃用户"却只选了部分 | Agent 0 分组策略优化 |

---

## 五、关键文件索引

| 路径 | 内容 |
|---|---|
| `README.md` | 架构总览（⭐ 最权威） |
| `AGENTS.md` | Agent 改动地图（⭐ 改任何 Agent 前必读） |
| `edm-backend/app/agent/prompts.py` | 所有 Agent 的 System Prompt 构造函数 |
| `edm-backend/app/agent/validators/` | 机械门校验器 |
| `edm-backend/app/agent/evaluators/` | LLM Judge 评审器 |
| `edm-backend/app/schemas/ai.py` | 所有 Agent 的 Pydantic IO Schema |
| `edm-backend/app/services/ai_service.py` | AI 服务主入口（改动最频繁：80 次） |
| `edm-backend/app/services/send_service.py` | 发送服务 |
| `edm-backend/app/agent/skills/` | Skill 体系（自主决策 + 内容编写） |
| `edm-frontend/src/features/campaigns/` | 活动创建主流程（StepAudience / StepContent / aiApi / campaignSlice） |
| `edm-marketing-agent.skill` / `edm-marketing-agent/` | 营销 Agent Skill 包 |
| `DEPLOY.md` / `docker-compose.yml` / `deploy/` | 部署 |
| `PROJECT_HANDOFF.md` / `HANDOFF_CHECKLIST.md` | 交接文档 |

---

## 六、复盘：这个项目最值得借鉴的三件事

1. **敢于推翻自己的设计** —— S/A/B/C 分级 → 多维标签；模板选择 → Agent 自主创作；Prompts 注入 → 真 Agent。每一次都是**主动砍掉已经能跑的东西**换取更高的上限。
2. **Harness Engineering 是 AI 系统的分水岭** —— 机械门（零成本硬规则）+ LLM Judge（软门）+ Trace（可回放）三层，让"能跑"变成"**可治理**"。
3. **送达率是工程问题不是玄学** —— SPF/DKIM/DMARC 体检、域隔离、冷启动爬坡、三级限流、反馈闭环，五件事缺一不可。
