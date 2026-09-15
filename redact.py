#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Redact secrets from all generated data files before publishing."""
import re, os, sys, io, json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
BASE = r"C:\Users\29989\WorkBuddy AI\2026-09-16-00-48-34"

# Order matters: more specific first
PATTERNS = [
    ("github_token",  re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("anthropic_key", re.compile(r"cr_[A-Za-z0-9]{40,}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_\-]{33,}")),
    ("openai_key",    re.compile(r"sk-[A-Za-z0-9_\-]{20,}")),
    ("tencent_secret", re.compile(r"AKID[A-Za-z0-9]{25,}")),
    ("aliyun_key",    re.compile(r"LTAI[A-Za-z0-9]{12,}")),
    # credentials pasted in chat (IP/account/password lines)
    ("ip_leak",       re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b")),
    ("privkey",       re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]
# ssh keys
SSHKEY = re.compile(r"ssh-(?:ed25519|rsa)\s+[A-Za-z0-9+/=]{40,}")
# password assignments like 密码：buddy.chen
PWD = re.compile(r"(密码|password|passwd|pwd)\s*[:：=]\s*[A-Za-z0-9!@#$%^&*_.\-]{5,}", re.I)

TARGETS = [
    "cursor_index.json",
    "cursor_sessions_full.json",
    "per_project.json",
    "Cursor对话历史整理.html",
    "Cursor对话历史整理.md",
]

report = {}
for name in TARGETS:
    fp = os.path.join(BASE, name)
    if not os.path.exists(fp):
        print("SKIP (missing):", name); continue
    t = open(fp, encoding="utf-8", errors="replace").read()
    orig = t
    counts = {}
    for label, pat in PATTERNS:
        n = len(pat.findall(t))
        if n:
            t = pat.sub("***REDACTED-%s***" % label.upper(), t)
            counts[label] = counts.get(label, 0) + n
    n = len(SSHKEY.findall(t))
    if n:
        t = SSHKEY.sub("***REDACTED-SSH-KEY***", t); counts["ssh_key"] = n
    n = len(PWD.findall(t))
    if n:
        t = PWD.sub(lambda m: m.group(1) + ": ***REDACTED***", t); counts["password_field"] = n
    if t != orig:
        open(fp, "w", encoding="utf-8").write(t)
    report[name] = counts
    print("%-32s %s" % (name, counts if counts else "(clean)"))

print("\n=== VERIFY ===")
for name in TARGETS:
    fp = os.path.join(BASE, name)
    if not os.path.exists(fp): continue
    t = open(fp, encoding="utf-8", errors="replace").read()
    left = []
    for label, pat in PATTERNS:
        c = len(pat.findall(t))
        if c: left.append("%s=%d" % (label, c))
    c = len(SSHKEY.findall(t))
    if c: left.append("ssh=%d" % c)
    print("%-32s %s" % (name, ("STILL DIRTY: " + ", ".join(left)) if left else "OK clean"))
