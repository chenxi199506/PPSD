#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 4 · 四行三列 12 面板 A–L 版（去 M、D 位换原 N）的独立验收。

用法：把本脚本放在作图数据包的 scripts/ 目录，在该数据包根目录执行
    python scripts/verify_12panel_AL.py [--no-repro]

检查项：
  [1] 交付物：PNG 尺寸/DPI、PDF 无图像对象、字体嵌入
  [2] 版面：12 个 axes 落在三列设计列位，字母恰为 A–L，无 M/N，无留白列
  [3] 内容：D 是 Control/OA/RA 三色 616 供体散点；G 仍是 255 供体两色散点
  [4] 统计：D 的 r/n 由 CSV 重算并与 JSON 一致；I 的 8 行与 JSON 对齐
  [5] 可复现：原样重跑生成脚本，PNG md5 逐字节一致（--no-repro 可跳过）
  [6] 静态审计：生成脚本无 imshow / PIL / 裁图 / 随机源
"""
from __future__ import annotations

import hashlib
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")

PKG = Path(__file__).resolve().parents[1]
SCRIPT = PKG / "scripts" / "build_figure4_12panel_AL_portable.py"
STEM = "Figure4_12panel_AL_180mm"
PNG = PKG / "figures" / f"{STEM}.png"
PDF = PKG / "figures" / f"{STEM}.pdf"
DER = PKG / "data" / "derived"
YRA = pd.read_csv(DER / "y_ra_donor_scores.csv")
YR = json.loads((DER / "y_ra_stats.json").read_text(encoding="utf-8"))
XS = json.loads((DER / "x_ppsd_stats.json").read_text(encoding="utf-8"))
SKIP_REPRO = "--no-repro" in sys.argv


def md5(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


# ---------------------------------------------------------------- [1] 交付物 --
print("[1] 交付物")
im = Image.open(PNG)
w, h = im.size
dpi = im.info.get("dpi", (600, 600))[0]
mm = (w / dpi * 25.4, h / dpi * 25.4)
print(f"  PNG {w} x {h} @ {dpi:.0f} dpi -> {mm[0]:.1f} x {mm[1]:.1f} mm, "
      f"{PNG.stat().st_size:,} bytes, md5 {md5(PNG.read_bytes())}")
assert abs(mm[0] - 180.0) < 0.2, mm
assert 268.0 < mm[1] < 274.0, mm
assert (w, h) == (4251, 6400), (w, h)

qb = PDF.read_bytes()
n_img = qb.count(b"/Subtype /Image") + qb.count(b"/Subtype/Image")
n_t3 = qb.count(b"/Type3") + qb.count(b"/Type /3")
n_f2 = qb.count(b"/FontFile2")
print(f"  PDF {len(qb):,} bytes  /Image={n_img}  /Type3={n_t3}  /FontFile2={n_f2}")
assert qb.startswith(b"%PDF") and qb.rstrip().endswith(b"%%EOF")
assert n_img == 0 and n_t3 == 0 and n_f2 >= 1

# ------------------------------------------------------------------ [2] 版面 --
print("\n[2] 版面（拦截 save，检查 axes 与字母）")
g = runpy.run_path(str(SCRIPT), run_name="_probe")
J = g["J"]
probe: dict = {}


def _capture(fig, outdir, stem, dpi=600, strict=False):
    probe["fig"] = fig
    probe["axes"] = [[round(a.get_position().x0 * 180.0, 3),
                      round(a.get_position().width * 180.0, 3),
                      round((1 - a.get_position().y1) * fig.get_size_inches()[1] * 25.4, 3)]
                     for a in fig.axes]
    probe["letters"] = [(t.get_text(), round(t.get_position()[0] * 180.0, 3))
                        for t in fig.texts if len(t.get_text()) == 1 and t.get_text().isalpha()]
    probe["legends"] = [tuple(t.get_text() for t in a.get_legend().get_texts())
                        for a in fig.axes if a.get_legend() is not None]
    probe["collections"] = [[c.get_label() for c in a.collections] for a in fig.axes]
    probe["footer"] = "\n".join(t.get_text() for t in fig.texts if len(t.get_text()) > 100)
    plt.close(fig)


J.save = _capture
g["build"]()
COLX = [21.374, 70.583, 135.291]
COLW = 41.709
axes = probe["axes"]
print(f"  axes: {len(axes)}（应为 12）")
assert len(axes) == 12, len(axes)
for x0, wid, top in axes:
    assert min(abs(x0 - c) for c in COLX) < 0.05, (x0, COLX)
    assert abs(wid - COLW) < 0.05, wid
cells = {(round(top, 1), min(range(3), key=lambda i: abs(COLX[i] - x0)))
         for x0, wid, top in axes}
for row_top in (12.0, 65.0, 118.0, 171.0):
    used = {c for t, c in cells if abs(t - (row_top + 4.4)) < 0.2}
    print(f"    行顶 {row_top:5.1f} mm -> 列 {sorted(used)}")
    assert used == {0, 1, 2}, (row_top, used)
letters = sorted(t for t, _ in probe["letters"])
print(f"  字母：{letters}")
assert letters == sorted(list("ABCDEFGHIJKL")), letters
assert "M" not in letters and "N" not in letters
footer = probe["footer"]
assert "Fourteen" not in footer and "M and N" not in footer
assert "All twelve panels" in footer

# --------------------------------------------------------------- [3] 内容 --
print("\n[3] D 槽位内容")
d_leg = [leg for leg in probe["legends"] if any("RA" in x for x in leg)]
print(f"  含 RA 的图例：{d_leg}")
assert d_leg and set(d_leg[0]) == {"Control (73)", "OA (191)", "RA (352)"}, d_leg
g_leg = [leg for leg in probe["legends"] if set(leg) == {"Control (73)", "OA (182)"}]
assert len(g_leg) == 1, probe["legends"]
print(f"  G 仍为归档 255 供体两色：{g_leg[0]}")
assert len(d_leg[0]) == 3 and len(g_leg[0]) == 2

# --------------------------------------------------------------- [4] 统计 --
print("\n[4] 统计一致性")
for grp in ("all", "Control", "OA", "RA"):
    df = YRA if grp == "all" else YRA[YRA.group == grp]
    r = float(np.corrcoef(df.PCDH9, df.CORE20)[0, 1])
    assert abs(r - YR["groups"][grp]["r"]) < 1e-9, (grp, r)
    assert len(df) == YR["groups"][grp]["n"], (grp, len(df))
print(f"  D r：all {YR['groups']['all']['r']:+.3f}（n={YR['groups']['all']['n']}）、"
      f"RA {YR['groups']['RA']['r']:+.3f}（n={YR['groups']['RA']['n']}）、"
      f"Control {YR['groups']['Control']['r']:+.3f}、OA {YR['groups']['OA']['r']:+.3f}")
assert YR["groups"]["all"]["n"] == 616
assert len(XS["rows"]) == 8 and sum(1 for r in XS["rows"] if r["pooled"]) == 6
print(f"  I：8 行，6 行参与 Overall，随机效应 {XS['overall']['d']:.3f} "
      f"[{XS['overall']['lo']:.3f},{XS['overall']['hi']:.3f}]")

# --------------------------------------------------------------- [5] 复现 --
if SKIP_REPRO:
    print("\n[5] 可复现：已按 --no-repro 跳过（跨平台字体不同，字节校验须在同一台机跑）")
else:
    print("\n[5] 可复现：原样重跑生成脚本")
    before = md5(PNG.read_bytes())
    r = subprocess.run([sys.executable, str(SCRIPT)], cwd=str(PKG),
                       capture_output=True, text=True, encoding="utf-8", timeout=900)
    assert r.returncode == 0, (r.stdout[-1500:], r.stderr[-1500:])
    after = md5(PNG.read_bytes())
    print(f"  PNG {before} -> {after}")
    assert before == after, "重跑后字节不一致"

# --------------------------------------------------------------- [6] 审计 --
print("\n[6] 静态审计")
src = SCRIPT.read_text(encoding="utf-8")
for pat, why in [(r"\.imshow\s*\(", "imshow 调用"),
                 (r"Image\.open\s*\(", "Image.open 调用"),
                 (r"\.crop\s*\(", "裁图调用"),
                 (r"(?:from|import)\s+PIL", "PIL 导入")]:
    assert not re.search(pat, src, re.M), f"生成脚本出现可疑调用: {why}"
assert "np.random" not in src
assert '("M", 0, 3, draw_M)' not in src and '("N", 1, 3, draw_N)' not in src
assert src.count('("D", 1, 0, draw_D)') == 1
print("  无 imshow / 无 PIL / 无裁图；LAYOUT 无 M/N，D 槽位为 RA 三色散点")

print("\nALL CHECKS PASSED")
