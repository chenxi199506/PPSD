#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交接自检：依赖表引用的文件是否齐全、MANIFEST 的 MD5 是否与实物一致。"""
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(__file__).resolve().parent
problems = []
with (P / "PANEL_DATA_DEPENDENCIES.csv").open(encoding="utf-8-sig", newline="") as fh:
    deps = list(csv.DictReader(fh))
refs = set()
for r in deps:
    for f in r["data_files_in_package"].split("|"):
        f = f.strip()
        if f and not f.startswith("("):
            refs.add(f)
missing = sorted(f for f in refs if not (P / f).is_file())
if missing:
    problems.append("依赖表引用了 %d 个不存在的文件" % len(missing))
    for f in missing[:20]: print("  [MISS]", f)
print("逐 panel 依赖: %d 行, %d 个唯一数据文件, 缺失 %d" % (len(deps), len(refs), len(missing)))
with (P / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as fh:
    man = list(csv.DictReader(fh))
bad = []
for r in man:
    f = P / r["path"]
    if not f.is_file():
        bad.append(r["path"]); continue
    h = hashlib.md5(f.read_bytes()).hexdigest()
    if h != r["md5"] or f.stat().st_size != int(r["size_bytes"]):
        bad.append(r["path"])
if bad:
    problems.append("MANIFEST 不符 %d 个文件" % len(bad))
    for f in bad[:20]: print("  [DIFF]", f)
for d in ("01_OAI", "02_TKA", "03_NRFB_sc", "04_Tissue", "05_Spatial",
          "06_Experiments", "07_SynovialFluid"):
    if not (P / d).is_dir(): problems.append("缺目录 " + d)
print("MANIFEST: %d 个文件, %.2f MB, 不符 %d" %
      (len(man), sum(int(r["size_bytes"]) for r in man)/1e6, len(bad)))
if problems:
    for p in problems: print("[FAIL]", p)
    raise SystemExit(1)
print("ALL CHECKS PASSED")
