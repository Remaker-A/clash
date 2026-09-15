#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract Cursor Chat (composer) conversations from state.vscdb cursorDiskKV."""
import sqlite3, json, sys, io, datetime, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB = r"C:\Users\29989\AppData\Roaming\Cursor\User\globalStorage\state.vscdb"
con = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\","/"), uri=True)
cur = con.cursor()

print("===== ItemTable keys =====")
cur.execute("SELECT key, length(value) FROM ItemTable ORDER BY key")
for k, l in cur.fetchall():
    print("  ", k, l)

print("\n===== cursorDiskKV =====")
cur.execute("SELECT key, length(value) FROM cursorDiskKV ORDER BY key")
rows = cur.fetchall()
buckets = {}
for k, l in rows:
    p = k.split(":")[0]
    buckets.setdefault(p, []).append((k, l))
for p, v in buckets.items():
    print("  prefix=%s count=%d totalbytes=%d" % (p, len(v), sum(x[1] for x in v)))
    for k, l in v[:5]:
        print("      ", k[:120], l)

print("\n===== composerHeaders =====")
cur.execute("SELECT * FROM composerHeaders")
cols = [d[0] for d in cur.description]
print(cols)
for r in cur.fetchall():
    print(dict(zip(cols, r)))

con.close()
