#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""改动本包内任何文件后，刷新 MANIFEST.csv 并重建上层 zip。

用法：在本包根目录运行  python rebuild_manifest.py
口径与原 build_package.py 一致（不含 MANIFEST.csv 自身与 .zip）。
"""
from __future__ import annotations
import csv, hashlib, io, sys, zipfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(__file__).resolve().parent
TEXT = {"README.md", "PANEL_DATA_DEPENDENCIES.csv", "check_package.py",
        "build_package.py", "make_portable.py"}
files = sorted(p for p in P.rglob("*") if p.is_file()
               and p.suffix != ".zip" and p.name != "MANIFEST.csv")

# 内容没变就不重写，保住 mtime -> zip 逐字节可复现（幂等）
buf = io.StringIO(newline="")
w = csv.writer(buf)
w.writerow(["path", "size_bytes", "md5", "kind"])
for p in files:
    rel = p.relative_to(P).as_posix()
    kind = ("文档/清单" if p.name in TEXT or (p.suffix in (".md", ".csv") and rel.count("/") == 0)
            else "脚本" if p.suffix in (".py", ".R")
            else "成品/参考" if p.suffix in (".png", ".pdf", ".svg", ".jpg")
            else "数据")
    w.writerow([rel, p.stat().st_size, hashlib.md5(p.read_bytes()).hexdigest(), kind])
mf = P / "MANIFEST.csv"
data = ("\ufeff" + buf.getvalue()).encode("utf-8")
if not mf.exists() or mf.read_bytes() != data:
    mf.write_bytes(data)

zpath = P.parent / (P.name + ".zip")
# 固定 zip 条目时间戳：文件 mtime 每次重打包都可能变，用固定值保证 zip 逐字节可复现
FIXED = (2026, 11, 7, 0, 0, 0)
mem = io.BytesIO()
with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(P.rglob("*")):
        if p.is_file() and p.suffix != ".zip":
            arc = P.name + "/" + p.relative_to(P).as_posix()
            zi = zipfile.ZipInfo(arc, date_time=FIXED)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = (p.stat().st_mode & 0xFFFF) << 16
            z.writestr(zi, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED,
                       compresslevel=6)
zdata = mem.getvalue()
if not zpath.exists() or zpath.read_bytes() != zdata:
    zpath.write_bytes(zdata)
print("MANIFEST.csv: %d files / %.2f MB" %
      (len(files), sum(p.stat().st_size for p in files) / 1e6))
print("ZIP: %s (%.2f MB)" % (zpath, zpath.stat().st_size / 1e6))
