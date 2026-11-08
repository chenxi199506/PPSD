#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建 `清单_可编辑包.csv`：全夹逐文件字节数 + MD5。

格式与 11-07 初版完全一致：
  · UTF-8 BOM + CRLF（`utf-8-sig` + `csv.writer(lineterminator="\\r\\n")`）
  · 按 `pathlib.Path` 的 parts 元组排序（即目录分组优先，不是整串字典序）
  · 排除隐藏文件/目录、`.DS_Store`、`__pycache__`、以及清单自身

用法：`python3 重建清单.py`（路径相对脚本所在目录，整夹拷走也能跑）。
"""
from __future__ import annotations

import csv
import hashlib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent
OUT = BASE / "清单_可编辑包.csv"
SKIP_PARTS = {"__pycache__"}


def included(p: Path) -> bool:
    parts = p.relative_to(BASE).parts
    if any(part.startswith(".") or part in SKIP_PARTS for part in parts):
        return False
    return p.relative_to(BASE).as_posix() != OUT.name


files = sorted((p for p in BASE.rglob("*") if p.is_file() and included(p)),
               key=lambda p: p.relative_to(BASE))
rows = []
for p in files:
    b = p.read_bytes()
    rows.append((p.relative_to(BASE).as_posix(), len(b), hashlib.md5(b).hexdigest()))

with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh, lineterminator="\r\n")
    w.writerow(["path", "size_bytes", "md5"])
    w.writerows(rows)

print(f"已写入 {OUT.name}：{len(rows)} 个文件，{OUT.stat().st_size:,} bytes")
print(f"  md5 = {hashlib.md5(OUT.read_bytes()).hexdigest()}")
