#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Export FULL Cursor transcripts (user + assistant replies + tool calls) to per-project Markdown."""
import json, os, re, sys, io, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECTS = r"C:\Users\29989\.cursor\projects"
OUT = r"C:\Users\29989\WorkBuddy AI\2026-09-16-00-48-34\对话全文"
MAX_BLOCK = 20000          # per tool-input cap
PART_LIMIT = 1_400_000     # bytes per output part

NAMES = {
 "d-Cursor-EDM": "EDM营销平台",
 "d-Cursor-pet-collar": "智能宠物项圈",
 "d-Codex-first-aid": "FirstAid急救副驾",
 "d-Cursor": "Cursor主工作区",
 "d-Cursor-worldGen": "WorldGen世界生成",
 "d-Cursor-Agent": "客服Agent",
 "d-ClaudeCode-agent-company": "AgentCompany多智能体协作",
 "d-Cursor-face-editor": "FaceEditor面部编辑器",
 "d-Cursor-Hotel-Manger": "酒店行程规划",
 "d-Cursor-baby-camera": "BabyCamera桌面宠物",
 "d-Cursor-musician-gym": "MusicianGym团课音乐律动",
 "d-Cursor-XLeRobort": "XLeRobot机器人语音",
 "d-Cursor-new-release": "NewRelease站内展示",
 "d-Cursor-model-test": "模型评测体系",
 "d-Cursor-musician": "Musician音乐控制台",
 "d-Cursor-RedHeckson-repo-accompany-mac-companion-agent-FuFuAgent": "FuFuAgent桌面陪伴",
 "d-Cursor-apple-box": "AppleBox手机体感手柄",
 "d-Cursor-Model-Test-Console": "ModelTestConsole视频模型控制台",
 "d-Cursor-Evolution": "Evolution自我进化Agent",
 "d-Cursor-release-tool": "Release发布工具链",
 "d-Cursor-Tapnoz-skill": "Tapnoz任务跟进Skill",
 "d-Cursor-Extend-song": "ExtendSong音频续写",
 "d-Cursor-CC": "CC-ClaudeCode",
 "d-Cursor-agent-EVA": "AgentEVA",
 "d-Cursor-skill-Master": "SkillMaster",
 "d-Cursor-learn-claudecode": "LearnClaudeCode",
 "c-Users-29989-Projects-pet-collar": "智能宠物项圈-备份",
 "d-openclaw": "openclaw",
 "d-Cursor-RedHeckson-repo-companion-agent-backend": "CompanionAgent后端",
 "d-Cursor-FuFu-Agent": "FuFuAgent",
 "d-Cursor-Rebuild-the-world": "RebuildTheWorld",
 "d-RenderCV": "RenderCV",
 "d-Cursor-Model-Lab": "ModelLab",
 "d-Codex-agent": "CodexAgent",
 "empty-window": "无项目窗口",
}

# ---------- redaction ----------
PAT = [
 ("GITHUB_PAT",  re.compile(r"github_pat_[A-Za-z0-9_]{40,}")),
 ("GITHUB_TOKEN",re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
 ("ANTHROPIC",   re.compile(r"cr_[A-Za-z0-9]{40,}")),
 ("GOOGLE_KEY",  re.compile(r"AIza[0-9A-Za-z_\-]{33,}")),
 ("GOOGLE_OAUTH",re.compile(r"AQ\.[A-Za-z0-9_\-\.]{20,}")),
 ("OPENAI_KEY",  re.compile(r"sk-[A-Za-z0-9_\-]{20,}")),
 ("VOLC_ARK",    re.compile(r"ark-[0-9a-fA-F\-]{20,}")),
 ("TENCENT_ID",  re.compile(r"AKID[A-Za-z0-9]{25,}")),
 ("ALIYUN_KEY",  re.compile(r"LTAI[A-Za-z0-9]{12,}")),
 ("BEARER",      re.compile(r"(Bearer\s+)[A-Za-z0-9_\-\.]{20,}", re.I)),
 ("SSH_KEY",     re.compile(r"ssh-(?:ed25519|rsa)\s+[A-Za-z0-9+/=]{40,}")),
 ("PRIVATE_KEY", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
 ("IP",          re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
 ("PWD",         re.compile(r"((?:密码|password|passwd|pwd)\s*[:：=]\s*)(?!\*\*\*)[A-Za-z0-9!@#$%^&*_.\-]{5,}", re.I)),
]

def redact(t):
    if not t:
        return t
    for label, p in PAT:
        if label == "BEARER":
            t = p.sub(lambda m: m.group(1) + "***REDACTED***", t)
        elif label == "PWD":
            t = p.sub(lambda m: m.group(1) + "***REDACTED***", t)
        else:
            t = p.sub("***REDACTED-%s***" % label, t)
    return t

def clean_user(txt):
    m = re.search(r"<user_query>\s*(.*?)\s*</user_query>", txt, re.S)
    if m:
        return m.group(1).strip(), True
    # system / automated message
    t = txt.strip()
    t = re.sub(r"^<[^>]+>\s*", "", t)
    return t, False

def fmt_size(n):
    if n < 1024: return "%d B" % n
    if n < 1024*1024: return "%.1f KB" % (n/1024)
    return "%.1f MB" % (n/1024/1024)

def esc_fence(s):
    """Avoid breaking out of a fenced block."""
    return s.replace("```", "``\u200b`")

def render_tool(name, inp):
    raw = json.dumps(inp, ensure_ascii=False, indent=1)
    truncated = len(raw) > MAX_BLOCK
    if truncated:
        raw = raw[:MAX_BLOCK] + "\n… （已截断，原长 %s）" % fmt_size(len(json.dumps(inp, ensure_ascii=False)))
    # short single-key inputs -> inline
    if not truncated and len(raw) <= 200:
        one = " ".join(raw.split())
        return "- 🔧 **%s** `%s`\n" % (name, esc_fence(one))
    return ("- 🔧 **%s**\n\n```json\n%s\n```\n" % (name, esc_fence(raw)))

# ---------- build ----------
os.makedirs(OUT, exist_ok=True)
proj_stats = []
total_sessions = 0
total_bytes = 0

for proj in sorted(os.listdir(PROJECTS)):
    td = os.path.join(PROJECTS, proj, "agent-transcripts")
    if not os.path.isdir(td):
        continue
    sessions = []
    for sid in sorted(os.listdir(td)):
        fp = os.path.join(td, sid, sid + ".jsonl")
        if not os.path.isfile(fp):
            continue
        blocks = []
        n_user = n_asst = n_tool = 0
        for line in open(fp, encoding="utf-8", errors="replace"):
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            role = o.get("role")
            c = (o.get("message") or {}).get("content")
            if isinstance(c, str):
                c = [{"type": "text", "text": c}]
            if not isinstance(c, list):
                continue
            for b in c:
                if not isinstance(b, dict):
                    continue
                t = b.get("type")
                if t == "text":
                    txt = b.get("text") or ""
                    if role == "user":
                        q, is_q = clean_user(txt)
                        if not q:
                            continue
                        blocks.append(("user", q, is_q))
                        n_user += 1
                    elif role == "assistant" and txt.strip():
                        blocks.append(("asst", txt, True))
                        n_asst += 1
                elif t == "tool_use":
                    blocks.append(("tool", (b.get("name") or "?", b.get("input") or {}), True))
                    n_tool += 1
        if not blocks:
            continue
        st = os.stat(fp)
        sessions.append({
            "sid": sid, "blocks": blocks, "n_user": n_user,
            "n_asst": n_asst, "n_tool": n_tool,
            "start": st.st_ctime, "end": st.st_mtime, "size": st.st_size,
        })
    if not sessions:
        continue
    sessions.sort(key=lambda s: s["start"])

    label = NAMES.get(proj, proj)
    safe = re.sub(r'[\\/:*?"<>|]', "-", label)

    # header
    head = ["# %s —— 对话全文\n\n" % label,
            "> 项目目录：`%s`  \n" % proj,
            "> 会话数：**%d** · 用户提问 **%d** 条 · Agent 回复 **%d** 条 · 工具调用 **%d** 次\n>\n" % (
                len(sessions),
                sum(s["n_user"] for s in sessions),
                sum(s["n_asst"] for s in sessions),
                sum(s["n_tool"] for s in sessions)),
            "> 说明：Agent 的工具调用参数已完整保留；**工具执行结果（命令输出 / 文件读取内容）Cursor 未持久化，故缺失**。\n>\n",
            "> 所有密钥、IP、账号信息已脱敏。\n\n---\n"]

    parts = []
    cur = list(head)
    cur_len = sum(len(x) for x in cur)
    idx = 0
    for i, s in enumerate(sessions, 1):
        idx += 1
        chunk = []
        import datetime
        dt = datetime.datetime.fromtimestamp(s["end"]).strftime("%Y-%m-%d %H:%M")
        chunk.append("\n## 会话 %03d · %s · %d 轮\n" % (i, dt, s["n_user"]))
        chunk.append("`%s` · Agent 回复 %d 条 · 工具 %d 次 · %s\n" % (
            s["sid"], s["n_asst"], s["n_tool"], fmt_size(s["size"])))
        last = None
        for kind, payload, flag in s["blocks"]:
            if kind == "user":
                if last != "user":
                    chunk.append("\n### 👤 用户\n")
                chunk.append("\n%s\n" % ("> " + payload.replace("\n", "\n> ") if flag else "> ⚙️ *系统指令*：" + payload.replace("\n", " ")[:800]))
                last = "user"
            elif kind == "asst":
                if last != "asst":
                    chunk.append("\n### 🤖 Agent\n")
                chunk.append("\n%s\n" % payload.strip())
                last = "asst"
            else:
                name, inp = payload
                if last != "tool":
                    chunk.append("\n")
                chunk.append(render_tool(name, inp))
                last = "tool"
        chunk.append("\n---\n")
        body = "".join(chunk)
        body = redact(body)
        if cur_len + len(body) > PART_LIMIT and len(cur) > 5:
            parts.append("".join(cur))
            cur = ["# %s —— 对话全文（续 %d）\n\n" % (label, len(parts) + 1)]
            cur_len = sum(len(x) for x in cur)
        cur.append(body)
        cur_len += len(body)
    if cur:
        parts.append("".join(cur))

    written = []
    for pi, ptext in enumerate(parts, 1):
        fn = "%s.md" % safe if len(parts) == 1 else "%s-part%d.md" % (safe, pi)
        fp = os.path.join(OUT, fn)
        open(fp, "w", encoding="utf-8").write(ptext)
        written.append((fn, len(ptext.encode("utf-8"))))

    for fn, sz in written:
        total_bytes += sz
    total_sessions += len(sessions)
    proj_stats.append((label, len(sessions), len(written), sum(x[1] for x in written)))

print("sessions exported:", total_sessions)
print("total output: %.1f MB" % (total_bytes/1024/1024))
print("\n%-34s %6s %5s %10s" % ("project", "sess", "files", "size"))
for label, ns, nf, sz in sorted(proj_stats, key=lambda x: -x[3]):
    print("%-34s %6d %5d %10s" % (label[:34], ns, nf, fmt_size(sz)))
