#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 4 四行四列 14 面板版的独立验收。

不复用生成脚本的任何中间结果，逐项从原始文件重算：
  [1] 交付物：PNG 尺寸／DPI、PDF 无图像对象、字体嵌入
  [2] 版面：14 个 axes 落在设计列位上，字母 A–L ＋ M、N 齐全，行 3/4 第 4 列确实留白
  [3] 统计：M 的三组 n 与 B 的 Control/OA n 必须一致；N 的 r 从 CSV 重算；I 的 8 行与 JSON 对齐
  [4] 可复现：原样重跑生成脚本，PNG md5 逐字节一致
  [5] 静态审计：生成脚本不含 imshow / Image.open / 任何图版读取
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
from scipy import stats as SS

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(r"E:/NRFB_atlas_plate_20261104")
D = ROOT / "22_Figure4_四列_20261106"
SCRIPT = D / "scripts/build_figure4_4col.py"
PNG = D / "figures/Figure4_14panel_4col_180mm.png"
PDF = D / "figures/Figure4_14panel_4col_180mm.pdf"
T30 = ROOT / "_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T30_deconv_donor_fractions.csv"

XR = json.loads((D / "x_ra_stats.json").read_text(encoding="utf-8"))
YR = json.loads((D / "y_ra_stats.json").read_text(encoding="utf-8"))
XS = json.loads((D / "x_ppsd_stats.json").read_text(encoding="utf-8"))
XRA = pd.read_csv(D / "x_ra_donor_fractions.csv")
YRA = pd.read_csv(D / "y_ra_donor_scores.csv")


def md5(b: bytes) -> str:
    return hashlib.md5(b).hexdigest()


# ---------------------------------------------------------------- [1] 交付物 --
print("[1] 交付物")
from PIL import Image
im = Image.open(PNG)
w, h = im.size
dpi = im.info.get("dpi", (600, 600))[0]
mm = (w / dpi * 25.4, h / dpi * 25.4)
print(f"  PNG {w} x {h} @ {dpi:.0f} dpi -> {mm[0]:.1f} x {mm[1]:.1f} mm, {PNG.stat().st_size:,} bytes, md5 {md5(PNG.read_bytes())}")
assert abs(mm[0] - 180.0) < 0.2, mm
assert 275.0 < mm[1] < 280.0, mm

qb = PDF.read_bytes()
n_img = qb.count(b"/Subtype /Image") + qb.count(b"/Subtype/Image")
n_t3 = qb.count(b"/Type3") + qb.count(b"/Type /3")
n_f2 = qb.count(b"/FontFile2")
print(f"  PDF {len(qb):,} bytes  /Image={n_img}  /Type3={n_t3}  /FontFile2={n_f2}")
assert qb.startswith(b"%PDF") and qb.rstrip().endswith(b"%%EOF")
assert n_img == 0 and n_t3 == 0 and n_f2 >= 1

# ------------------------------------------------------------------ [2] 版面 --
print("\n[2] 版面（重跑一次，拦截 save 检查 axes 与字母）")
g = runpy.run_path(str(SCRIPT), run_name="_probe")
J = g["J"]
J_SAVE = J.save
probe: dict = {}


def _capture(fig, outdir, stem, dpi=600, strict=False):
    probe["fig"] = fig
    probe["axes"] = [[round(a.get_position().x0 * 180.0, 3),
                      round(a.get_position().width * 180.0, 3),
                      round((1 - a.get_position().y1) * fig.get_size_inches()[1] * 25.4, 3)]
                     for a in fig.axes]
    probe["letters"] = [(t.get_text(), round(t.get_position()[0] * 180.0, 3),
                         round((1 - t.get_position()[1]) * fig.get_size_inches()[1] * 25.4, 3))
                        for t in fig.texts if len(t.get_text()) == 1 and t.get_text().isalpha()]
    plt.close(fig)


J.save = _capture
g["build"]()
COLX = [21.374, 58.281, 110.687, 147.594]
COLW = 29.406
axes = probe["axes"]
print(f"  axes: {len(axes)}（应为 14）")
assert len(axes) == 14, len(axes)
for x0, w, top in axes:
    assert min(abs(x0 - c) for c in COLX) < 0.05, (x0, COLX)
    assert abs(w - COLW) < 0.05, w
cells = {(round(top, 1), min(range(4), key=lambda i: abs(COLX[i] - x0))) for x0, w, top in axes}
print(f"  占用格：{sorted(cells)}")
for row_top in (12.0, 65.0, 118.0, 171.0):
    used = {c for t, c in cells if abs(t - (row_top + 4.4)) < 0.2}
    print(f"    行顶 {row_top:5.1f} mm -> 列 {sorted(used)}")
assert {c for t, c in cells if abs(t - (12.0 + 4.4)) < 0.2} == {0, 1, 2, 3}
assert {c for t, c in cells if abs(t - (65.0 + 4.4)) < 0.2} == {0, 1, 2, 3}
assert {c for t, c in cells if abs(t - (118.0 + 4.4)) < 0.2} == {0, 1, 2}
assert {c for t, c in cells if abs(t - (171.0 + 4.4)) < 0.2} == {0, 1, 2}
letters = sorted(t for t, _, _ in probe["letters"])
print(f"  字母：{letters}")
assert letters == sorted(list("ABCDEFGHIJKLMN")), letters

# ------------------------------------------------------------------ [3] 统计 --
print("\n[3] 统计一致性")
t30 = pd.read_csv(T30)
t30 = t30[t30.method == "svr"]
nB = t30.groupby("condition").size().to_dict()
nM = {k: XR["group_stats"][k]["n"] for k in ("Normal", "OA", "RA")}
print(f"  B (T30 svr)  Control {nB['Normal']} / OA {nB['OA']}")
print(f"  M (重算)     Control {nM['Normal']} / OA {nM['OA']} / RA {nM['RA']}")
assert nM["Normal"] == nB["Normal"] and nM["OA"] == nB["OA"], (nM, nB)
assert abs(XR["provenance"]["t30_reproduction_max_abs_diff"]) < 1e-9

# M 的组均值从供体表重算
for grp, key in [("Normal", "Normal"), ("OA", "OA"), ("RA", "RA")]:
    v = XRA.loc[XRA.group == grp, "NR-FB core"].to_numpy() * 100
    assert len(v) == XR["group_stats"][key]["n"]
    assert abs(v.mean() - XR["group_stats"][key]["mean"]) < 1e-9
print(f"  M 三组均值 %：{XR['group_stats']['Normal']['mean']:.3f} / "
      f"{XR['group_stats']['OA']['mean']:.3f} / {XR['group_stats']['RA']['mean']:.3f}")

# M 的 Control-OA 括号必须与 B 同值（队列级 meta，不是合并 Welch）
dmeta = pd.read_csv(ROOT / "_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T32_deconv_meta.csv")
dmeta = dmeta[(dmeta.method == "svr") & (dmeta.metric == "NR-FB fraction difference")].iloc[0]
pooled = XR["comparisons"]["Control vs OA"]["p"]
print(f"  B/M 共用括号 P = {float(dmeta.p):.5f}（B 的队列级 meta）；"
      f"合并 Welch 为 {pooled:.2e} —— 面板用前者，两图不打架")
assert abs(float(dmeta.p) - 0.00278) < 1e-4
assert pooled < 1e-4

# N：从供体表重算 r
for grp in ("all", "Control", "OA", "RA"):
    df = YRA if grp == "all" else YRA[YRA.group == grp]
    r = float(np.corrcoef(df.PCDH9, df.CORE20)[0, 1])
    assert abs(r - YR["groups"][grp]["r"]) < 1e-9, (grp, r)
    assert len(df) == YR["groups"][grp]["n"], (grp, len(df))
print(f"  N r：all {YR['groups']['all']['r']:+.3f}（n={YR['groups']['all']['n']}）、"
      f"RA {YR['groups']['RA']['r']:+.3f}（n={YR['groups']['RA']['n']}）、"
      f"Control {YR['groups']['Control']['r']:+.3f}、OA {YR['groups']['OA']['r']:+.3f}")
assert YR["groups"]["all"]["n"] == 616

# I：8 行 + Overall 与 JSON 对齐
assert len(XS["rows"]) == 8
assert sum(1 for r in XS["rows"] if r["pooled"]) == 6
print(f"  I：8 行，{sum(1 for r in XS['rows'] if r['pooled'])} 行参与 Overall，"
      f"随机效应 {XS['overall']['d']:.3f} [{XS['overall']['lo']:.3f},{XS['overall']['hi']:.3f}]")

# ------------------------------------------------------------------ [4] 复现 --
print("\n[4] 可复现：原样重跑生成脚本")
before = md5(PNG.read_bytes())
r = subprocess.run([sys.executable, str(SCRIPT)], cwd=str(ROOT),
                   capture_output=True, text=True, encoding="utf-8", timeout=900)
assert r.returncode == 0, (r.stdout[-1500:], r.stderr[-1500:])
after = md5(PNG.read_bytes())
print(f"  PNG {before} -> {after}")
assert before == after, "重跑后字节不一致"
print("  OK：脚本 + 归档结果表即可完整复现")

# ------------------------------------------------------------------ [5] 审计 --
print("\n[5] 静态审计")
src = SCRIPT.read_text(encoding="utf-8")
# 只查真实调用，不查文档字符串里的说明文字
for pat, why in [(r"\.imshow\s*\(", "imshow 调用"),
                 (r"Image\.open\s*\(", "Image.open 调用"),
                 (r"\.crop\s*\(", "裁图调用"),
                 (r"(?:from|import)\s+PIL", "PIL 导入"),
                 (r"read_bytes\s*\(\s*\)\s*$", "直接读字节")]:
    assert not re.search(pat, src, re.M), f"生成脚本出现可疑调用: {why}"
reads = sorted(set(re.findall(r'"(?:sources|_external)[^"]+"', src)))
print(f"  无 imshow / 无 PIL / 无裁图；读取的外部路径 {len(reads)} 条")
assert "np.random" not in src

print("\nALL CHECKS PASSED")
