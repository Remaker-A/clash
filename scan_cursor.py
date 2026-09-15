#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan local Cursor conversation history: agent transcripts + state.vscdb chat data."""
import json, os, sys, sqlite3, datetime, re, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

CURSOR = r"C:\Users\29989\.cursor"
APPDATA = r"C:\Users\29989\AppData\Roaming\Cursor"
PROJECTS = os.path.join(CURSOR, "projects")

out = {"projects": [], "totals": {}}

def ts_ms(v):
    try:
        return datetime.datetime.fromtimestamp(int(v)/1000).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return "?"

# ---------- 1. agent-transcripts ----------
proj_dirs = sorted([d for d in os.listdir(PROJECTS) if os.path.isdir(os.path.join(PROJECTS, d))])
total_sessions = 0
total_files = 0
total_bytes = 0
total_user_msgs = 0

for pd in proj_dirs:
    tdir = os.path.join(PROJECTS, pd, "agent-transcripts")
    if not os.path.isdir(tdir):
        continue
    sessions = []
    for sid in sorted(os.listdir(tdir)):
        sdir = os.path.join(tdir, sid)
        if not os.path.isdir(sdir):
            continue
        main = os.path.join(sdir, sid + ".jsonl")
        if not os.path.isfile(main):
            continue
        size = os.path.getsize(main)
        mtime = os.path.getmtime(main)
        ctime = os.path.getctime(main)
        # parse
        first_user = ""
        last_user = ""
        n_user = 0
        n_asst = 0
        n_lines = 0
        tools = {}
        files_touched = set()
        try:
            with open(main, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    n_lines += 1
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue
                    role = o.get("role")
                    content = (o.get("message") or {}).get("content")
                    if isinstance(content, str):
                        content = [{"type": "text", "text": content}]
                    if not isinstance(content, list):
                        continue
                    for c in content:
                        if not isinstance(c, dict):
                            continue
                        t = c.get("type")
                        if t == "text":
                            txt = c.get("text") or ""
                            if role == "user":
                                m = re.search(r"<user_query>\s*(.*?)\s*</user_query>", txt, re.S)
                                q = (m.group(1) if m else txt).strip()
                                q = re.sub(r"@[\w:\\/\.\-]+", "", q).strip()
                                if q.startswith("<") and len(q) > 200:
                                    continue
                                n_user += 1
                                if not first_user:
                                    first_user = q[:400]
                                last_user = q[:400]
                            elif role == "assistant":
                                n_asst += 1
                        elif t == "tool_use":
                            nm = c.get("name") or "?"
                            tools[nm] = tools.get(nm, 0) + 1
                            inp = c.get("input") or {}
                            for k in ("path", "file_path", "target_file", "notebook_path"):
                                if isinstance(inp.get(k), str):
                                    files_touched.add(inp[k])
        except Exception as e:
            continue
        subs = os.path.join(sdir, "subagents")
        n_sub = len([x for x in os.listdir(subs)]) if os.path.isdir(subs) else 0
        sessions.append({
            "id": sid,
            "title": (first_user or "(无用户消息)")[:200],
            "last": last_user[:200],
            "start": ts_ms(ctime*1000) if ctime else "?",
            "end": ts_ms(mtime*1000),
            "size": size,
            "lines": n_lines,
            "user_msgs": n_user,
            "asst_msgs": n_asst,
            "subagents": n_sub,
            "tools": dict(sorted(tools.items(), key=lambda x: -x[1])[:8]),
            "files": sorted(files_touched)[:40],
        })
        total_sessions += 1
        total_bytes += size
        total_user_msgs += n_user
        total_files += 1 + n_sub
    if sessions:
        out["projects"].append({
            "dir": pd,
            "real_path": pd.replace("-", "/") if pd.startswith("d-") or pd.startswith("c-") else pd,
            "sessions": sessions,
        })

out["totals"] = {
    "projects_with_transcripts": len(out["projects"]),
    "total_sessions": total_sessions,
    "transcript_files": total_files,
    "total_bytes": total_bytes,
    "total_user_msgs": total_user_msgs,
}

print(json.dumps(out["totals"], ensure_ascii=False, indent=2))

with open(r"C:\Users\29989\WorkBuddy AI\2026-09-16-00-48-34\cursor_index.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# ---------- 2. state.vscdb chat data ----------
print("\n===== state.vscdb =====")
for db in [os.path.join(APPDATA, "User", "globalStorage", "state.vscdb"),
           os.path.join(APPDATA, "User", "globalStorage", "conversation-search.db")]:
    if not os.path.exists(db):
        print("missing:", db); continue
    print("\n--", db, os.path.getsize(db), "bytes")
    for tmp in (db,):
        try:
            src = sqlite3.connect("file:%s?mode=ro" % db.replace("\\", "/"), uri=True)
            cur = src.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cur.fetchall()]
            print("tables:", tables)
            for t in tables:
                try:
                    cur.execute("SELECT COUNT(*) FROM [%s]" % t)
                    print("  ", t, cur.fetchone()[0])
                except Exception as e:
                    print("  ", t, "err", e)
            src.close()
        except Exception as e:
            print("open err", e)
