#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the organized Cursor conversation history report + HTML browser."""
import json, os, collections, html, sys, io, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = r"C:\Users\29989\WorkBuddy AI\2026-09-16-00-48-34"
d = json.load(open(os.path.join(BASE, "cursor_sessions_full.json"), encoding="utf-8"))
S = d["sessions"]

# ---------- project metadata (friendly names + theme) ----------
META = {
    "D:\\Cursor\\EDM": ("EDM 自动化营销系统", "营销/内容自动化的多 Agent 流水线"),
    "D:\\Cursor\\pet\\collar": ("智能宠物项圈", "宠物防丢硬件 + 配套 App"),
    "D:\\Codex\\first\\aid": ("First Aid 急救助手", "急救指导类应用"),
    "D:\\Cursor": ("Cursor 主工作区", "杂项工程与实验"),
    "D:\\Cursor\\worldGen": ("WorldGen 世界生成", "程序化世界/游戏生成"),
    "D:\\Cursor\\Agent": ("Agent 通用实验", "Agent 架构与能力探索"),
    "D:\\ClaudeCode\\agent\\company": ("Agent Company", "多 Agent 协作公司模拟"),
    "D:\\Cursor\\face\\editor": ("Face Editor 面部编辑器", "人脸/图像编辑"),
    "D:\\Cursor\\Hotel\\Manger": ("酒店管理系统", "酒店管理后台"),
    "D:\\Cursor\\baby\\camera": ("Baby Camera 数字宠物", "婴儿/宠物摄像头 + 云台追踪"),
    "D:\\Cursor\\musician\\gym": ("Musician Gym", "音乐相关练习应用"),
    "D:\\Cursor\\XLeRobort": ("XLeRobot 机器人", "机器人控制/语音交互"),
    "D:\\Cursor\\new\\release": ("New Release", "版本发布工具"),
    "D:\\Cursor\\model\\test": ("Model Test", "模型 Agentic 能力评测"),
    "D:\\Cursor\\Model\\Test\\Console": ("Model Test Console", "模型测试控制台"),
    "D:\\Cursor\\musician": ("Musician", "音乐工具"),
    "D:\\Cursor\\apple\\box": ("Apple Box", "硬件/设备相关"),
    "D:\\Cursor\\Evolution": ("Evolution", "演进式 Agent 实验"),
    "D:\\Cursor\\release\\tool": ("Release Tool", "发布流程工具"),
    "D:\\Cursor\\Tapnoz\\skill": ("Tapnoz Skill", "Skill 开发"),
    "D:\\Cursor\\Extend\\song": ("Extend Song", "音频续写/生成"),
    "D:\\Cursor\\skill\\Master": ("Skill Master", "Skill 体系管理"),
    "D:\\Cursor\\agent\\EVA": ("Agent EVA", "Agent 实验"),
    "D:\\Cursor\\CC": ("CC", "Claude Code 相关"),
    "D:\\Cursor\\learn\\claudecode": ("Learn Claude Code", "Claude Code 学习"),
    "D:\\Cursor\\RedHeckson\\repo\\accompany\\mac\\companion\\agent\\FuFuAgent": ("FuFu Agent (陪伴)", "桌面陪伴 Agent"),
    "D:\\Cursor\\RedHeckson\\repo\\companion\\agent\\backend": ("Companion Agent Backend", "陪伴 Agent 后端"),
    "D:\\Cursor\\FuFu\\Agent": ("FuFu Agent", "陪伴 Agent"),
    "D:\\Cursor\\Rebuild\\the\\world": ("Rebuild the World", "世界重建实验"),
    "D:\\Cursor\\Model\\Lab": ("Model Lab", "模型实验台"),
    "D:\\openclaw": ("openclaw", "CLI 工具"),
    "D:\\RenderCV": ("RenderCV", "简历渲染"),
    "D:\\Codex\\agent": ("Codex Agent", "Codex 相关"),
    "C:\\Users\\29989\\Projects\\pet\\collar": ("智能宠物项圈 (C 盘)", "宠物项圈备份工作区"),
    "empty-window": ("无项目窗口", "空窗口临时会话"),
}

byproj = collections.defaultdict(list)
for s in S:
    byproj[s["real_path"] or s["project_dir"]].append(s)

# ---------- grouped by theme ----------
THEMES = [
    ("Agent / 多智能体", ["D:\\Cursor\\Agent", "D:\\ClaudeCode\\agent\\company", "D:\\Cursor\\agent\\EVA",
                          "D:\\Cursor\\Evolution", "D:\\Codex\\agent", "D:\\openclaw",
                          "D:\\Cursor\\RedHeckson\\repo\\accompany\\mac\\companion\\agent\\FuFuAgent",
                          "D:\\Cursor\\RedHeckson\\repo\\companion\\agent\\backend", "D:\\Cursor\\FuFu\\Agent"]),
    ("模型评测 / 测试", ["D:\\Cursor\\model\\test", "D:\\Cursor\\Model\\Test\\Console", "D:\\Cursor\\Model\\Lab"]),
    ("硬件 / 机器人与多模态", ["D:\\Cursor\\baby\\camera", "D:\\Cursor\\XLeRobort", "D:\\Cursor\\apple\\box",
                              "D:\\Cursor\\pet\\collar", "C:\\Users\\29989\\Projects\\pet\\collar"]),
    ("内容 / 营销 / 音乐", ["D:\\Cursor\\EDM", "D:\\Cursor\\musician", "D:\\Cursor\\musician\\gym",
                            "D:\\Cursor\\Extend\\song"]),
    ("应用产品线", ["D:\\Codex\\first\\aid", "D:\\Cursor\\face\\editor", "D:\\Cursor\\Hotel\\Manger",
                    "D:\\Cursor\\worldGen", "D:\\Cursor\\Rebuild\\the\\world", "D:\\RenderCV"]),
    ("工程 / 发布 / Skill", ["D:\\Cursor\\release\\tool", "D:\\Cursor\\new\\release", "D:\\Cursor\\Tapnoz\\skill",
                            "D:\\Cursor\\skill\\Master", "D:\\Cursor\\CC", "D:\\Cursor\\learn\\claudecode",
                            "D:\\Cursor", "empty-window"]),
]

def nice(p):
    return META.get(p, (os.path.basename(p.replace("\\", "/")) or p, ""))[0]

def theme_of(p):
    for name, members in THEMES:
        if p in members:
            return name
    return "其他"

# ---------- Markdown report ----------
L = []
A = L.append
A("# Cursor 本地对话历史整理报告")
A("")
A("> 扫描时间：2026-09-16 · 数据来源：`~/.cursor/projects/*/agent-transcripts`")
A("")
A("## 一、总览")
A("")
A("| 指标 | 数值 |")
A("|---|---|")
A("| 会话总数 | **%d** 个 |" % len(S))
A("| 用户提问轮次 | **%d** 次 |" % sum(s["n_turns"] for s in S))
A("| 涉及项目 | **%d** 个工作区 |" % len([k for k in byproj if k != "empty-window"]))
A("| 时间跨度 | **%s ~ %s**（约 6 个月） |" % (S[0]["start"][:10], S[-1]["end"][:10]))
A("| 原始数据量 | **%.0f MB** / 1520 个 transcript 文件 |" % (sum(s["bytes"] for s in S) / 1024 / 1024))
A("| 子 Agent 调用 | **%d** 个 |" % sum(s["n_subagents"] for s in S))
A("")
A("### 月度分布")
A("")
mon = collections.Counter(s["start"][:7] for s in S)
A("| 月份 | 会话数 | 占比 |")
A("|---|---|---|")
for k in sorted(mon):
    A("| %s | %d | %.0f%% |" % (k, mon[k], mon[k] * 100.0 / len(S)))
A("")
A("**结论**：2026 年 4 月是使用高峰（407 个会话，占 51%%），主要来自 EDM 项目的密集开发；6 月后使用频率明显下降，9 月仅 1 个会话。".replace("%%", "%"))
A("")
A("### 工具使用画像")
A("")
A("| 工具 | 调用次数 |")
A("|---|---|")
tp = collections.Counter()
for s in S:
    for t, c in s["top_tools"]:
        tp[t] += c
for k, v in tp.most_common(12):
    A("| %s | %d |" % (k, v))
A("")
A("以 **读代码（Read 10.8k）+ 改代码（StrReplace 5.1k）+ 跑命令（Shell 7.0k）** 为主，属于典型的重度代码开发型使用，而不是纯问答。")
A("")
A("## 二、按主题分类")
A("")

for tname, members in THEMES:
    sub = [(k, v) for k, v in byproj.items() if k in members]
    if not sub:
        continue
    ns = sum(len(v) for _, v in sub)
    nt = sum(x["n_turns"] for _, v in sub for x in v)
    A("### %s" % tname)
    A("")
    A("*共 %d 个会话 / %d 轮提问*" % (ns, nt))
    A("")
    A("| 项目 | 会话 | 提问 | 时间范围 | 说明 |")
    A("|---|---|---|---|---|")
    for k, v in sorted(sub, key=lambda x: -len(x[1])):
        nm, desc = META.get(k, (k, ""))
        A("| %s | %d | %d | %s ~ %s | %s |" % (
            nm, len(v), sum(x["n_turns"] for x in v),
            v[0]["start"][:10], v[-1]["end"][:10], desc))
    A("")

A("## 三、重点项目详情")
A("")
top = sorted(byproj.items(), key=lambda x: -len(x[1]))[:8]
for k, v in top:
    nm, desc = META.get(k, (k, ""))
    A("### %s — `%s`" % (nm, k))
    A("")
    A("- **%d** 个会话 · **%d** 轮提问 · %s ~ %s" % (
        len(v), sum(x["n_turns"] for x in v), v[0]["start"][:10], v[-1]["end"][:10]))
    A("- 累积数据量 %.1f MB" % (sum(x["bytes"] for x in v) / 1024 / 1024))
    A("")
    A("关键讨论主题（按时间排序，摘录首个提问）：")
    A("")
    seen = set()
    cnt = 0
    for s in v:
        t = s["title"][:100]
        if t in seen or not t:
            continue
        seen.add(t)
        A("- `%s` %s" % (s["end"][:10], t))
        cnt += 1
        if cnt >= 8:
            break
    A("")

A("## 四、值得回看的会话 Top 10")
A("")
A("| 日期 | 项目 | 轮次 | 大小 | 首个提问 |")
A("|---|---|---|---|---|")
for s in sorted(S, key=lambda x: -x["bytes"])[:10]:
    A("| %s | %s | %d | %.0fKB | %s |" % (
        s["end"][:10], nice(s["real_path"] or s["project_dir"]),
        s["n_turns"], s["bytes"] / 1024, s["title"][:70].replace("|", "/")))
A("")
A("## 五、数据说明")
A("")
A("| 存储位置 | 内容 | 状态 |")
A("|---|---|---|")
A("| `~/.cursor/projects/*/agent-transcripts/` | 全部 Agent 会话（801 个） | ✅ 已解析 |")
A("| `~/.cursor/projects/*/agent-transcripts/*/subagents/` | 子 Agent 记录 | ✅ 已统计 |")
A("| `~/AppData/Roaming/Cursor/User/globalStorage/state.vscdb` | Chat 模式会话（bubbleId） | ⚠️ 仅 78 条气泡，多为近期草稿 |")
A("| `~/AppData/Roaming/Cursor/User/workspaceStorage/*/state.vscdb` | 各工作区编辑器状态 | 非对话数据 |")
A("")
A("**注意**：`state.vscdb` 中的 Chat 历史已被 Cursor 清理（仅剩空草稿与 1 个活跃会话），完整历史保存在 agent-transcripts 中。")

md = "\n".join(L)
with open(os.path.join(BASE, "Cursor对话历史整理.md"), "w", encoding="utf-8") as f:
    f.write(md)
print("wrote MD, %d chars" % len(md))

# ---------- HTML ----------
def esc(x):
    return html.escape(str(x))

rows = []
for k, v in sorted(byproj.items(), key=lambda x: -len(x[1])):
    nm, desc = META.get(k, (os.path.basename(k.replace("\\", "/")) or k, ""))
    sess_html = []
    for s in sorted(v, key=lambda x: x["start_ts"], reverse=True):
        qs = "".join("<li>%s</li>" % esc(q[:200]) for q in s["all_user_queries"][:6])
        sess_html.append("""
        <details class="sess">
          <summary><span class="dt">{dt}</span><span class="ttl">{ttl}</span><span class="badge">{n} 轮</span><span class="sz">{sz}KB</span></summary>
          <ul class="qs">{qs}</ul>
        </details>""".format(
            dt=esc(s["end"]), ttl=esc(s["title"][:110] or "(空会话)"),
            n=s["n_turns"], sz=s["bytes"] // 1024, qs=qs))
    rows.append("""
    <section class="proj">
      <h3>{nm} <code>{path}</code></h3>
      <p class="desc">{desc} · <b>{ns}</b> 个会话 · <b>{nt}</b> 轮提问 · {d0} ~ {d1}</p>
      {sess}
    </section>""".format(
        nm=esc(nm), path=esc(k), desc=esc(desc), ns=len(v),
        nt=sum(x["n_turns"] for x in v), d0=v[0]["start"][:10], d1=v[-1]["end"][:10],
        sess="".join(sess_html)))

mon_rows = "".join(
    "<tr><td>%s</td><td>%d</td><td><div class='bar' style='width:%.1f%%'></div></td></tr>"
    % (k, mon[k], mon[k] * 100.0 / max(mon.values())) for k in sorted(mon))

tool_rows = "".join(
    "<div class='toolrow'><span class='tn'>%s</span><span class='tb' style='width:%.1f%%'></span><span class='tv'>%d</span></div>"
    % (esc(k), v * 100.0 / tp.most_common(1)[0][1], v) for k, v in tp.most_common(10))

HTML = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cursor 对话历史整理</title>
<style>
:root{--bg:#0f1115;--panel:#171a21;--panel2:#1e222b;--line:#2a2f3a;--tx:#e6e9ef;--tx2:#9aa3b2;--ac:#5b9dff;--ac2:#7c5cff;--ok:#3ddc97}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--tx);font:14px/1.65 -apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:32px 24px 80px}
h1{font-size:28px;margin:0 0 6px;letter-spacing:-.4px}
.sub{color:var(--tx2);margin-bottom:28px;font-size:13px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:32px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.kpi .v{font-size:24px;font-weight:700;background:linear-gradient(90deg,var(--ac),var(--ac2));-webkit-background-clip:text;background-clip:text;color:transparent}
.kpi .l{color:var(--tx2);font-size:12px;margin-top:2px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:34px}
@media(max-width:820px){.grid2{grid-template-columns:1fr}}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
.card h3{margin:0 0 14px;font-size:15px}
table{width:100%%;border-collapse:collapse;font-size:13px}
td{padding:6px 4px;border-bottom:1px solid var(--line)}
td:last-child{padding:6px 0}
.bar{height:8px;border-radius:4px;background:linear-gradient(90deg,var(--ac),var(--ac2));min-width:4px}
h2{font-size:18px;margin:0 0 16px}
.toolrow{display:flex;align-items:center;gap:10px;margin-bottom:8px;font-size:13px}
.tn{width:88px;color:var(--tx2);flex:none}
.tb{height:7px;border-radius:4px;background:linear-gradient(90deg,var(--ok),var(--ac));min-width:3px}
.tv{color:var(--tx2);font-size:12px;margin-left:auto}
.proj{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:16px}
.proj h3{margin:0 0 4px;font-size:16px}
.proj code{font-size:11px;color:var(--tx2);background:var(--panel2);padding:2px 7px;border-radius:5px;font-weight:400}
.desc{color:var(--tx2);font-size:12.5px;margin:0 0 12px}
.sess{border-top:1px solid var(--line);padding:0}
.sess summary{display:flex;gap:12px;align-items:center;padding:9px 2px;cursor:pointer;list-style:none;font-size:13px}
.sess summary::-webkit-details-marker{display:none}
.sess summary:hover{color:var(--ac)}
.dt{color:var(--tx2);font-size:11.5px;flex:none;font-variant-numeric:tabular-nums}
.ttl{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.badge{background:var(--panel2);border:1px solid var(--line);color:var(--tx2);font-size:11px;padding:1px 7px;border-radius:20px;flex:none}
.sz{color:var(--tx2);font-size:11px;flex:none;width:52px;text-align:right}
.qs{margin:2px 0 12px 8px;padding-left:16px;border-left:2px solid var(--line);color:var(--tx2);font-size:12.5px}
.qs li{margin:5px 0}
.foot{color:var(--tx2);font-size:12px;margin-top:36px;padding-top:18px;border-top:1px solid var(--line)}
</style></head><body><div class="wrap">
<h1>Cursor 本地对话历史整理</h1>
<div class="sub">扫描自 <code>~/.cursor/projects/*/agent-transcripts</code> · 2026-09-16</div>
<div class="kpis">
  <div class="kpi"><div class="v">%(ns)d</div><div class="l">会话总数</div></div>
  <div class="kpi"><div class="v">%(nt)d</div><div class="l">用户提问轮次</div></div>
  <div class="kpi"><div class="v">%(np)d</div><div class="l">涉及项目</div></div>
  <div class="kpi"><div class="v">%(mb).0fMB</div><div class="l">原始数据量</div></div>
  <div class="kpi"><div class="v">%(span)s</div><div class="l">时间跨度</div></div>
</div>
<div class="grid2">
  <div class="card"><h3>月度会话分布</h3><table>%(monrows)s</table></div>
  <div class="card"><h3>工具调用 Top 10</h3>%(toolrows)s</div>
</div>
<h2 style="font-size:18px;margin:0 0 16px">按项目分组（%(np2)d 个工作区）</h2>
%(rows)s
<div class="foot">点击任意会话行可展开查看该会话中的用户提问原文。子 Agent 记录已合并计入所属会话。</div>
</div></body></html>""" % {
    "ns": len(S), "nt": sum(s["n_turns"] for s in S),
    "np": len([k for k in byproj if k != "empty-window"]),
    "np2": len(byproj),
    "mb": sum(s["bytes"] for s in S) / 1024 / 1024,
    "span": "%s → %s" % (S[0]["start"][:7], S[-1]["end"][:7]),
    "monrows": mon_rows, "toolrows": tool_rows, "rows": "".join(rows),
}
with open(os.path.join(BASE, "Cursor对话历史整理.html"), "w", encoding="utf-8") as f:
    f.write(HTML)
print("wrote HTML, %d chars" % len(HTML))
