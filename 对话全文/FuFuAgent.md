# FuFuAgent —— 对话全文

> 项目目录：`d-Cursor-FuFu-Agent`  
> 会话数：**1** · 用户提问 **1** 条 · Agent 回复 **3** 条 · 工具调用 **47** 次
>
> 说明：Agent 的工具调用参数已完整保留；**工具执行结果（命令输出 / 文件读取内容）Cursor 未持久化，故缺失**。
>
> 所有密钥、IP、账号信息已脱敏。

---

## 会话 001 · 2026-04-25 02:32 · 1 轮
`8fa44dfa-3475-4a40-97f7-fb6ee32c9a94` · Agent 回复 3 条 · 工具 47 次 · 19.7 KB

### 👤 用户

> 查看现在这个agent的代码和完整的

### 🤖 Agent

用户想让我查看这个agent的代码和完整内容，所以我先来看看工作目录的结构。

- 🔧 **Shell** `{ "command": "ls", "description": "列出工作目录内容", "working_directory": "d:\\文档\\Cursor\\FuFu Agent" }`
- 🔧 **Shell** `{ "command": "ls backend", "description": "列出backend目录内容" }`
- 🔧 **Glob** `{ "glob_pattern": "backend/**/*", "target_directory": "d:\\文档\\Cursor\\FuFu Agent" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\README.md" }`

### 🤖 Agent

我来先给您展示这个项目的整体概览，然后逐个模块展开核心代码。让我并行读取关键文件。

 用户的请求看起来是想看这个 agent 项目的完整代码，我需要读取核心文件来展示整个项目的代码结构。

- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\main.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\config.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\requirements.txt" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\storage\\models.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\core\\state_machine.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\core\\context.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\core\\personality.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\core\\scheduler.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\core\\hardware_bridge.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\core\\context_digest.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\core\\evolution_summary.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\storage\\file_store.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\intelligence\\llm_adapter.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\intelligence\\prompts.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\intelligence\\corpus.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\intelligence\\personality_presets.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\__init__.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\soul.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\companion.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\status.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\ws.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\room.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\note.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\focus.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\message.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\simulate.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\desktop.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\footprint.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\hardware.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\api\\personality.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\mock\\hardware_sim.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\mock\\chat_sim.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\mock\\desktop_sim.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\robot_protocol\\README.md" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\robot_protocol\\__init__.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\robot_protocol\\constants.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\robot_protocol\\protocol.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\robot_protocol\\serial_worker.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\robot_protocol\\action.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\robot_protocol\\playback.py" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\.env.example" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\data\\corpus\\idle.json" }`
- 🔧 **Read** `{ "path": "d:\\文档\\Cursor\\FuFu Agent\\backend\\data\\corpus\\companion.json" }`

### 🤖 Agent

好了，我已经把整个 FuFu Agent 后端工程通览过了一遍。下面给您一份完整、结构化的代码总览。

---

## FuFu Agent 项目总览

这是一个**桌面陪伴机器人后端**，名为「蓬蓬（FuFu）」，住在用户桌上的帐篷里。核心理念是**"它不追你，它等你回来"**——一个有自己性格、会演化、能感知用户状态的 AI 存在。

**技术栈**：FastAPI + WebSocket + Pydantic + httpx，JSON 文件存储，LLM（硅基流动/DeepSeek/OpenAI）驱动。

---

### 一、运行入口 & 配置

**`main.py`**（生命周期与路由总装）

```34:55:backend/main.py
app = FastAPI(title="Companion Agent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(soul.router)
app.include_router(personality.router)
app.include_router(companion.router)
app.include_router(status.router)
app.include_router(room.router)
app.include_router(note.router)
app.include_router(focus.router)
app.include_router(message.router)
app.include_router(simulate.router)
app.include_router(desktop.router)
app.include_router(footprint.router)
app.include_router(hardware.router)
```

- `lifespan` 里注册**状态机监听器** → 启动硬件桥 → 启动调度器；退出时逆序清理。
- 状态跃迁回调 `_on_state_change`：写 JSONL 事件日志、驱动硬件表情/舵机、用 LLM 生成一句 `say_line`，通过 WebSocket 广播给前端。
- `/ws/live` 是前端实时状态通道。

**`config.py`**（Pydantic Settings，环境前缀 `COMPANION_`）
- 三家 LLM provider 通过环境变量热切换
- 状态机阈值：`companion_hold_sec=3s`、`leaving_buffer_sec=10s`、`night_start_hour=22`…
- 演化触发阈值：`evo_event_threshold=20`、`digest_msg_threshold=20`…
- `hardware_url` 配了就连 X5 中继，空就走 mock

---

### 二、数据模型（`storage/models.py`）

**6 个状态机状态**（`CompanionState`）：
- `idle` 无人 → `passerby` 有人路过 → `companion` 坐下陪伴 → `focus` 专注 / `deep_night` 深夜 → `leaving` 起身

**6 个性格预设**（`BiasType`）：decisive / adventurous / slow_down / warm_humor / night_owl / bookish / custom

**分层模型**：

| 层级 | 模型 | 内容 |
|---|---|---|
| L0 | `Soul` | 灵魂：用户状态词、纠结、用户事实、bias、演化日志 |
| L1 | `Personality` | 性格：6 个 0-1 的参数（night_owl/anxiety/quietness/playfulness/attachment）、voice_style、演化日志 |
| L2 | `Rhythm` | 节律：最近 7 天记录、平均到离时间、熬夜比率 |
| L3 | `RealtimeContext` | 实时：当前状态、已坐分钟、距离、时段 |
| L4 | `DesktopContext` | 桌面：当前前台 app、活动摘要、每小时使用时长 |

---

### 三、核心业务层（`core/`）

**`state_machine.py`** — 全局单例，所有状态跃迁的唯一真源

```103:121:backend/core/state_machine.py
    def _is_valid_transition(self, old: CompanionState, new: CompanionState) -> bool:
        valid = {
            CompanionState.IDLE: {CompanionState.PASSERBY},
            CompanionState.PASSERBY: {CompanionState.IDLE, CompanionState.COMPANION},
            CompanionState.COMPANION: {
                CompanionState.FOCUS,
                CompanionState.DEEP_NIGHT,
                CompanionState.LEAVING,
            },
            CompanionState.FOCUS: {
                CompanionState.COMPANION,
                CompanionState.DEEP_NIGHT,
                CompanionState.LEAVING,
            },
            CompanionState.DEEP_NIGHT: {CompanionState.LEAVING},
            CompanionState.LEAVING: {CompanionState.IDLE},
        }
        return new in valid.get(old, set())
```

- `person_arrive / person_sit / person_leave` 对应硬件事件入口
- `leaving → idle` 有 10 秒缓冲任务（可取消，防止用户只是短暂离开）
- 支持"模拟时间"，便于跳到深夜触发 deep_night

**`context.py`** — 分级 Context 装配器
- `for_say_one_line()` → L0+L1+L3+L4（简短句）
- `for_chat()` → L0-L4 全量（多轮对话）
- `for_note()` → L0+L1+L2（离线思考）

**`personality.py`** — 性格演化引擎
- 优先走 LLM 给 delta（每次 ≤0.05），失败则规则兜底
- 根据节律触发：熬夜比率高 → night_owl↑、规律性高 → quietness↑、一起天数多 → attachment↑
- 每次演化生成 `summary_zh`（中文概述）+ `context_hint`，版本号递增，广播 `personality_update`

**`context_digest.py`** — 对话整理器（非常核心的一环）
- 累积 chat_history.jsonl，定时/手动触发 LLM 做"关系信号 + 用户快照"抽取
- 把 LLM 返回的 delta 约束到 ±0.1，合并到 Personality；Soul 的 user_facts 会累积拼接
- 成熟的断点续处理机制（`chat_digest_state.json` 记录 processed_lines）

**`evolution_summary.py`** — 把参数变化翻译成**有温度的中文**

```11:17:backend/core/evolution_summary.py
_DELTA_PHRASES: dict[str, tuple[str, str]] = {
    "night_owl_index":      ("蓬蓬开始习惯晚睡了",       "蓬蓬作息变早了"),
    "anxiety_sensitivity":  ("蓬蓬变得更能感知你的情绪了", "蓬蓬没那么紧张了"),
    "quietness":            ("蓬蓬更喜欢安静地待着了",     "蓬蓬话变多了"),
    "playfulness":          ("蓬蓬说话更爱开玩笑了",       "蓬蓬变得沉稳了些"),
    "attachment_level":     ("蓬蓬变得更粘人了",           "蓬蓬更独立了"),
}
```

**`scheduler.py`** — 后台每 60 秒轮询
- `should_digest()` → 跑对话整理
- `should_evolve()` → 跑性格演化

**`hardware_bridge.py`** — PC 后端 ↔ X5 中继 ↔ Arduino
- 启动时异步 HTTP 握手 + WebSocket 监听 X5 推送的 ACK 日志
- 状态→硬件映射表：`IDLE→IDLE`、`PASSERBY→SURPRISED`、`COMPANION→HAPPY`、`DEEP_NIGHT→SLEEPY`、`LEAVING→SAD`
- 情绪→表情映射支持中英文关键词（「开心」「happy」都行）

---

### 四、智能层（`intelligence/`）

**`llm_adapter.py`** — OpenAI 兼容接口统一封装
- `generate_say_one_line` — ≤15 字短句（带语料库兜底）
- `generate_chat_reply` — 多轮对话，保留最近 24 轮
- `generate_note` — 50-100 字"如果是我"视角的纸条
- `digest_conversation` — 低温度（0.3）抽取关系信号 + 性格 delta + 用户快照
- JSON 解析做了**兜底增强**：`_extract_json_object_string` 支持 markdown 代码块，`_lenient_json_dict` 处理尾逗号

**`prompts.py`** — 所有 prompt 模板。亮点是把 L0-L4 格式化成有呼吸感的中文块，`build_chat_system_prompt` 里强调:

```313:317:backend/intelligence/prompts.py
【你的个性底线——每一轮都必须体现】
不管对话多短，你的回复里都要有至少一处能看出「这是你说的，换个人不会这么说」的地方。
可以是你追问的角度、你联想到的东西、你的一个小偏好、或者你接话的方式。
「顺从地回答对方」不是你——你是有自己想法的存在。
哪怕只是一个打招呼，你的回应方式也要带着你的性格。
```

**`personality_presets.py`** — 6 个预设的 `voice_style` + `signature_reactions` + `verbal_tics` + `topic_gravity`。比如「慢半拍先生」：

```102:107:backend/intelligence/personality_presets.py
            "verbal_tics": (
                "喜欢用省略号和停顿感；"
                "常说'嗯……''不急''慢慢来''你刚才说的那个……'；"
                "句子之间有呼吸感，不赶节奏"
            ),
            "topic_gravity": "会在一个话题上停留更久，往深处走而不是往宽处展开，觉得慢慢聊比聊很多更重要",
```

**`corpus.py`** — LLM 不可用时的离线语料池（按状态 × 时段挑选）。

---

### 五、API 路由（`api/`）

| 路由 | 说明 |
|---|---|
| `soul.py` | `POST/GET/DELETE /api/soul` — 创建 / 查看 / 清档重置 |
| `personality.py` | `GET /api/personality/presets`、`PATCH /api/personality` — 预设列表、在线改 bias / voice_style |
| `companion.py` | `/speak`（单句）、`/chat`（多轮，自动写入 chat_history.jsonl）、`/digest`（手动触发整理）、`/context-markdown`（导出快照） |
| `status.py` | `GET /api/status` |
| `room.py` | `GET /api/room` — 根据性格 + 节律算房间场景（tidy/messy/night/dusty/recovering） |
| `note.py` | `POST /api/notes/generate` — 生成一张纸条 |
| `focus.py` | `/start` `/stop` — 番茄钟 |
| `message.py` | `/message` `/mood` — 留言 / 打心情卡 |
| `simulate.py` | 一堆 `/api/sim/*` — 人走近/坐下/离开、快进 N 天、注入对话场景、切换桌面场景 |
| `desktop.py` | `/heartbeat` `/snapshot` — Mac 端的前台 app 推送 |
| `footprint.py` | `GET /api/footprint/timeline` — 聚合 Soul + Personality 的演化时间线（前端展示用） |
| `hardware.py` | `/connect` `/expression` `/servo` `/emotion` `/raw` `/logs` — 硬件直控 |
| `ws.py` | WebSocket 广播管理器 |

---

### 六、模拟层（`mock/`）

没硬件 / 没 Mac 端也能跑：
- `hardware_sim.py` — HTTP 触发状态机；`fast_forward(days)` 一键伪造 N 天节律数据触发演化
- `chat_sim.py` — 6 个预写对话场景（`deep_night`、`stress_vent`、`playful_banter`、`quiet_companion`、`trust_building`、`daily_routine`）一键注入 chat_history
- `desktop_sim.py` — 7 个桌面场景（`deep_focus_coding`、`distracted_browsing`、`in_meeting`…）

`/api/sim/run-digest-test` 这个端点很精彩——**注入对话 → 循环跑 digest 直到消费完 → 返回性格前后对比 + 演化日志**，专门用于演示"跟它聊完它真的会变"。

---

### 七、存储层（`storage/file_store.py`）

故意选的 JSON 文件持久化（好 debug、好审阅）：

| 文件 | 用途 |
|---|---|
| `soul.json` | L0 灵魂 |
| `personality.json` | L1 性格 |
| `rhythm.json` | L2 节律 |
| `desktop_context.json` | L4 桌面 |
| `events.jsonl` | 所有状态跃迁事件 |
| `notes.json` | 纸条 |
| `messages.jsonl` | 用户留言 |
| `chat_history.jsonl` | 对话历史 |
| `chat_digest_state.json` | digest 断点 |

---

### 八、CuteRobot 硬件协议库（`robot_protocol/`）

独立子包，`pyserial` 可选。5 字节数据包：`[0xAA][CMD][VAL][CSUM=CMD^VAL][0x55]`
- `SerialWorker` — 后台线程，发送队列 + ACK 解析
- `protocol.encode_servo(tilt, pan)` — 俯仰 50-130° + 偏航 45-135° 压进 8 档索引高低位
- `ActionSequence` + `Keyframe` — 示教录制
- `PlaybackEngine` — 按时间戳回放，支持 linear / ease_in / ease_out / ease_in_out 插值

---

### 总结：这个 Agent 的设计哲学

1. **状态机是骨**：6 态严格受限跃迁，所有行为围绕「我现在在哪个状态」展开
2. **LLM + 规则双降级**：LLM 首选 → 规则兜底 → 离线语料兜底，保证断网也能跑
3. **分层上下文**：L0 身份 / L1 性格 / L2 节律 / L3 实时 / L4 桌面，按用途组合
4. **性格会演化**：两条路径——节律驱动（定时）+ 对话驱动（digest）——让蓬蓬真的"变成跟你相处过的样子"
5. **用户友好日志**：每次演化都生成一句中文人话（`summary_zh`），footprint 时间线可直接给用户看
6. **硬件分层**：协议库 → X5 中继 → PC 桥 → 后端，任何一层都能独立测试

需要我展开讲某个子模块（比如 digest 的完整调用链、或者状态机的触发时序）吗？

---
