#!/usr/bin/env python3
"""Publish allowlist for device-ai-ivfit."""
import pathlib
import re
import subprocess
import sys

ALLOW = re.compile(
    r"^(README\.md|LICENSE|SPEC\.md|Makefile|requirements\.txt|\.gitignore|"
    r"src/.*|data/synthetic\.csv|reports/\.gitkeep|"
    r"scripts/leak_check\.py|\.github/workflows/.*\.yml)$"
)
FORBIDDEN_SUFFIX = {".plt", ".tdr", ".lib", ".lef", ".gds", ".db"}
PATH_LEAK = re.compile(
    r"(D:\\\\|/mnt/d|/home/EDA|/opt/cadence|/opt/synopsys|winbox)",
    re.I,
)
# fragments so the joined tokens never appear as literals in git
TOPIC_LEAK = re.compile(
    "|".join(["Fe" "CAP", "CU" "MEC", "Hera" "cles", "A" "42"])
)

raw = subprocess.check_output(["git", "ls-files"], text=True)
bad = False
for p in raw.splitlines():
    if not p:
        continue
    if not ALLOW.match(p):
        print("leak-check extra:", p)
        bad = True
    suf = pathlib.Path(p).suffix.lower()
    if suf in FORBIDDEN_SUFFIX:
        print("leak-check forbidden suffix:", p)
        bad = True
    try:
        text = pathlib.Path(p).read_text(errors="replace")
    except OSError:
        continue
    if p.startswith("src/") and TOPIC_LEAK.search(text):
        print("leak-check topic keyword in", p)
        bad = True
    if p.endswith("leak_check.py"):
        continue
    if PATH_LEAK.search(text):
        print("leak-check machine path in", p)
        bad = True
sys.exit(1 if bad else 0)
