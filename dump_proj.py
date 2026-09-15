#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dump full conversation flow for a project dir key."""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = r"C:\Users\29989\WorkBuddy AI\2026-09-16-00-48-34"
d = json.load(open(BASE + r"\cursor_sessions_full.json", encoding="utf-8"))
key = sys.argv[1]
maxq = int(sys.argv[2]) if len(sys.argv) > 2 else 6
qlen = int(sys.argv[3]) if len(sys.argv) > 3 else 300
v = [s for s in d["sessions"] if s["project_dir"] == key]
v.sort(key=lambda x: x["start_ts"])
print("PROJECT:", key, "| SESSIONS:", len(v))
print("=" * 90)
for s in v:
    print("--- %s | %d turns | %dKB" % (s["end"][:16], s["n_turns"], s["bytes"] // 1024))
    for q in s["all_user_queries"][:maxq]:
        print("   Q:", q[:qlen].replace("\n", " "))
    print()
