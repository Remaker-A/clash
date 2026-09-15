#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a full organized index of local Cursor conversation history."""
import json, os, re, sys, io, datetime, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECTS = r"C:\Users\29989\.cursor\projects"

def ms(v):
    try:
        return datetime.datetime.fromtimestamp(int(v) / 1000)
    except Exception:
        return None

def fmt(d):
    return d.strftime("%Y-%m-%d %H:%M") if d else "?"

def clean_q(txt):
    m = re.search(r"<user_query>\s*(.*?)\s*</user_query>", txt, re.S)
    q = (m.group(1) if m else txt).strip()
    q = re.sub(r"@[\w:\\/\.\-]+", "", q)
    q = re.sub(r"<(?:user_info|system[_-]reminder|additional_data|current_time)[^>]*>.*?</[^>]+>", " ", q, flags=re.S)
    q = re.sub(r"\s+", " ", q).strip()
    return q

def path_from_dir(pd):
    if pd.startswith("empty-window") or pd.isdigit():
        return None
    parts = pd.split("-")
    drive = parts[0]
    if drive in ("c", "d", "e") and len(parts) > 1:
        p = drive.upper() + ":\\" + "\\".join(parts[1:])
        return p
    return pd

sessions = []
for pd in sorted(os.listdir(PROJECTS)):
    tdir = os.path.join(PROJECTS, pd, "agent-transcripts")
    if not os.path.isdir(tdir):
        continue
    for sid in sorted(os.listdir(tdir)):
        sdir = os.path.join(tdir, sid)
        main = os.path.join(sdir, sid + ".jsonl")
        if not os.path.isfile(main):
            continue
        users = []
        tools = collections.Counter()
        files = set()
        first_ts = last_ts = None
        n_asst = 0
        model = None
        try:
            with open(main, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    ts = o.get("timestamp") or o.get("ts")
                    if ts:
                        d = ms(ts) if isinstance(ts, (int, float)) or str(ts).isdigit() else None
                        if d:
                            first_ts = first_ts or d
                            last_ts = d
                    role = o.get("role")
                    msg = o.get("message") or {}
                    if msg.get("model"):
                        model = msg["model"]
                    content = msg.get("content")
                    if isinstance(content, str):
                        content = [{"type": "text", "text": content}]
                    if not isinstance(content, list):
                        continue
                    for c in content:
                        if not isinstance(c, dict):
                            continue
                        t = c.get("type")
                        if t == "text" and role == "user":
                            q = clean_q(c.get("text") or "")
                            if q:
                                users.append(q[:600])
                        elif t == "text" and role == "assistant":
                            n_asst += 1
                        elif t == "tool_use":
                            tools[c.get("name") or "?"] += 1
                            inp = c.get("input") or {}
                            for k in ("path", "file_path", "target_file"):
                                if isinstance(inp.get(k), str):
                                    files.add(inp[k])
        except Exception:
            continue
        st = os.stat(main)
        start = first_ts or ms(st.st_ctime * 1000)
        end = last_ts or ms(st.st_mtime * 1000)
        subs = os.path.join(sdir, "subagents")
        n_sub = len(os.listdir(subs)) if os.path.isdir(subs) else 0

        title = users[0].split(" ") if False else users[0] if users else "(无用户消息)"
        title = title[:120]
        sessions.append({
            "project_dir": pd,
            "real_path": path_from_dir(pd),
            "session_id": sid,
            "title": title,
            "all_user_queries": users,
            "n_turns": len(users),
            "n_asst": n_asst,
            "n_subagents": n_sub,
            "start": fmt(start),
            "end": fmt(end),
            "start_ts": start.timestamp() if start else 0,
            "bytes": st.st_size,
            "model": model,
            "top_tools": tools.most_common(8),
            "n_files": len(files),
            "files": sorted(files)[:60],
        })

sessions.sort(key=lambda s: s["start_ts"])
print("TOTAL SESSIONS:", len(sessions))
print("DATE RANGE:", sessions[0]["start"], "->", sessions[-1]["end"])
print("TOTAL USER TURNS:", sum(s["n_turns"] for s in sessions))
print()

# Group by real project path (fallback to dir)
byproj = collections.defaultdict(list)
for s in sessions:
    key = s["real_path"] or s["project_dir"]
    byproj[key].append(s)

print("PROJECTS (excluding temp):")
tot = 0
for k, v in sorted(byproj.items(), key=lambda x: -len(x[1])):
    if "AppData-Local-Temp" in k:
        continue
    tot += len(v)
    print("  %-70s sessions=%-4d turns=%-5d %s -> %s" % (k[:70], len(v), sum(x["n_turns"] for x in v), v[0]["start"][:10], v[-1]["end"][:10]))
print("  (temp/non-project sessions: %d)" % (len(sessions) - tot))

with open(r"C:\Users\29989\WorkBuddy AI\2026-09-16-00-48-34\cursor_sessions_full.json", "w", encoding="utf-8") as f:
    json.dump({"sessions": sessions, "by_project": {k: len(v) for k, v in byproj.items()}}, f, ensure_ascii=False, indent=1)
print("\nwrote cursor_sessions_full.json")
