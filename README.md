# Cursor 项目文档整理

对本机 Cursor 全部对话历史的系统性整理成果。

## 数据规模

| 指标 | 数值 |
|---|---|
| 会话总数 | **1012** |
| 用户提问 | **4326** 条 |
| Agent 回复 | **46457** 条（17.7 MB 正文） |
| 工具调用 | **57507** 次（34.1 MB 参数） |
| 涉及工作区 | **35** |
| 时间跨度 | 2026-03-16 ~ 2026-10 |
| 原始数据量 | 1019 个主会话 + 898 个子 Agent |

## 目录结构

```
.
├── 项目文档/                        # ⭐ 18 份项目归纳文档
│   ├── README.md                   #   索引与主题分类
│   ├── 01-客服Agent.md
│   ├── 02-EDM营销平台.md
│   ├── 03-BabyCamera桌面宠物.md
│   ├── 04-FirstAid急救副驾.md
│   ├── 05-智能宠物项圈.md
│   ├── 06-WorldGen世界生成.md
│   ├── 07-AgentCompany多智能体协作.md
│   ├── 08-MusicianGym团课音乐律动.md
│   ├── 09-FaceEditor面部编辑器.md
│   ├── 10-酒店行程规划.md
│   ├── 11-模型评测体系.md
│   ├── 12-XLeRobot机器人语音.md
│   ├── 13-AppleBox手机体感手柄.md
│   ├── 14-FuFuAgent桌面陪伴.md
│   ├── 15-Evolution自我进化Agent.md
│   ├── 16-音乐与音频工具.md
│   ├── 17-Release发布工具链.md
│   └── 18-其他项目与技术探索.md
├── 对话全文/                        # ⭐ 完整对话记录（含 Agent 回复）
│   ├── README.md                   #   索引：会话数 / 提问 / 回复 / 工具调用
│   ├── 客服Agent-part1..5.md
│   ├── EDM营销平台-part1..18.md
│   └── ...                         #   按项目拆分，共 72 份
├── Cursor对话历史整理.md             # 总体报告（总览/月度/主题/重点项目）
├── Cursor对话历史整理.html           # 可展开浏览的会话索引
├── cursor_sessions_full.json       # 结构化索引（提问 / 统计 / 涉及文件）
├── per_project.json                # 按项目聚合的数据
├── cursor_index.json               # 初版扫描索引
└── *.py                            # 分析脚本
```

**两类文档的分工**：

| 目录 | 内容 | 适合 |
|---|---|---|
| `项目文档/` | 归纳总结（做了什么 / 技术栈 / 设计思路） | 快速了解项目 |
| `对话全文/` | 原始对话（用户提问 + Agent 回复 + 工具调用） | 追溯具体决策过程 |

> **关于「工具执行结果」**：Cursor 的 transcript 只保存 `user` / `assistant` 两类消息，**不保存 `tool_result`**。因此可以看到 Agent 调用了 `Read`、参数是什么，但看不到读取到的文件内容；可以看到 `Shell` 命令，但看不到命令输出。这是数据源本身的限制，非导出遗漏。


每份项目文档统一包含三部分：**做了什么 · 用了什么技术 · 具体是怎么设计的**。

## 使用脚本

```bash
# 扫描 Cursor agent-transcripts，建立会话索引
python scan_cursor.py

# 构建完整会话数据（含提问原文）
python build_index.py

# 生成 Markdown 报告 + HTML 浏览页
python gen_report.py

# 按项目 dump 对话流（仅用户提问）
python dump_proj.py <project_dir_key> [max_questions] [max_len]

# ⭐ 导出完整对话全文（用户 + Agent 回复 + 工具调用）到 对话全文/
python export_full.py

# 发布前对数据文件脱敏
python redact.py
```

## 数据来源

| 位置 | 内容 |
|---|---|
| `~/.cursor/projects/<项目>/agent-transcripts/<sessionId>/<sessionId>.jsonl` | **主数据源** —— Agent 会话全文 |
| `~/.cursor/projects/<项目>/agent-transcripts/*/subagents/` | 子 Agent 记录 |
| `~/AppData/Roaming/Cursor/User/globalStorage/state.vscdb` | Chat(composer) 模式（`cursorDiskKV` 表） |

> ⚠️ **注意**：`state.vscdb` 里的 Chat 历史已被 Cursor 大幅清理，完整历史只存在于 `agent-transcripts` 中。建议定期备份该目录。

**目录命名规则**：盘符与路径分隔符都替换为 `-`，例如 `d-Cursor-EDM` 对应 `D:\Cursor\EDM`。

## 安全说明

发布前已对以下内容做**脱敏处理**（替换为 `***REDACTED-XXX***`）：

- API Key（OpenAI `sk-` / Google `AIza`、`AQ.` / Anthropic `cr_` / 火山引擎 `ark-`）
- GitHub Token（`ghp_`、`github_pat_`）
- SSH 公钥
- 服务器 IP 地址
- 账号与密码字段

如需处理未经脱敏的原始数据，请使用 `redact.py` 并自行复核。
