# -*- coding: utf-8 -*-
"""check_layout.py — 几何核验：绘图框是否落在同一网格、文字是否越界/互撞

用法：python check_layout.py <图脚本.py> [<图脚本.py> ...]
脚本会被执行到 savefig 之前（不产图），然后：
  1. 打印每个 axes 的绘图框（mm），并按 x 边界分组，检查"同列上下对齐"；
  2. 收集全部可见文字的 bbox，找 (a) 超出画布 (b) 两两重叠；
  3. 报告 <5 pt 文字。
"""
from __future__ import annotations

import os
import sys
import itertools
import matplotlib
matplotlib.use("Agg")
import matplotlib.text as mtext
from matplotlib.transforms import Bbox


def load(path):
    src = open(path, encoding="utf-8").read()
    for tag in ('FIG.savefig(stem + ".pdf"', 'FIG.savefig(stem + ".png"',
                'FIG.savefig(stem + ".svg"', 'FIG.savefig(str(stem) + ".pdf"',
                'FIG.savefig(str(stem) + ".png"'):
        src = src.replace(tag, "#" + tag)
    g = {"__name__": "__check__", "__file__": os.path.abspath(path)}
    exec(compile(src, path, "exec"), g)
    return g


def mm_bbox(fig, bb, W, H):
    inv = fig.transFigure.inverted()
    x0, y0 = inv.transform((bb.x0, bb.y0))
    x1, y1 = inv.transform((bb.x1, bb.y1))
    return x0 * W, y0 * H, x1 * W, y1 * H


def report(path):
    g = load(path)
    FIG, W, H = g["FIG"], g["W"], g["H"]
    FIG.canvas.draw()
    r = FIG.canvas.get_renderer()
    print(f"\n{'='*74}\n{os.path.basename(path)}   {W:.1f} x {H:.1f} mm\n{'='*74}")

    # ---- 1) 绘图框
    boxes = []
    for ax in FIG.axes:
        bb = ax.get_position()
        boxes.append((bb.x0 * W, bb.y0 * H, bb.x1 * W, bb.y1 * H))
    print(f"\n绘图框（mm）  共 {len(boxes)} 个")
    for x0, y0, x1, y1 in sorted(boxes, key=lambda b: (-b[3], b[0])):
        print(f"   x {x0:6.1f} – {x1:6.1f}  (w {x1-x0:5.1f})   "
              f"y {y0:6.1f} – {y1:6.1f}  (h {y1-y0:5.1f})")

    # ---- 2) 同列上下对齐：按 x0 聚类
    print("\n列对齐（x0 相同的面板应上下齐）")
    tol = 0.6
    groups = {}
    for x0, y0, x1, y1 in boxes:
        key = next((k for k in groups if abs(k - x0) < tol), x0)
        groups.setdefault(key, []).append((x0, y0, x1, y1))
    for key in sorted(groups):
        rows = sorted(groups[key], key=lambda b: -b[3])
        x1s = [b[2] for b in rows]
        span = max(x1s) - min(x1s)
        flag = "✓" if span < tol else "✗ 右缘不齐"
        print(f"   x0≈{key:6.1f}  {len(rows)} 个面板  右缘 {min(x1s):6.1f}–{max(x1s):6.1f}  {flag}")

    # ---- 3) 文字越界 / 互撞
    texts = []
    for t in FIG.findobj(mtext.Text):
        s = t.get_text().strip()
        if not s or not t.get_visible():
            continue
        if t.axes is not None and not t.axes.axison:   # axis('off') 的表格面板
            continue
        bb = t.get_window_extent(r)
        if bb.width <= 0 or bb.height <= 0:
            continue
        texts.append((s.replace("\n", "|"), mm_bbox(FIG, bb, W, H), t.get_fontsize()))

    out = [(s, b) for s, b, _ in texts
           if b[0] < -0.4 or b[1] < -0.4 or b[2] > W + 0.4 or b[3] > H + 0.4]
    print(f"\n超出画布的文字：{len(out)} 处")
    for s, b in out[:12]:
        print(f"   [{b[0]:6.1f},{b[1]:6.1f}]–[{b[2]:6.1f},{b[3]:6.1f}]  {s[:44]!r}")

    hits = []
    for (s1, b1, _), (s2, b2, _) in itertools.combinations(texts, 2):
        ix = min(b1[2], b2[2]) - max(b1[0], b2[0])
        iy = min(b1[3], b2[3]) - max(b1[1], b2[1])
        if ix > 0.25 and iy > 0.25:          # 0.25 mm 容差，滤掉贴边
            hits.append((ix * iy, s1, s2, ix, iy))
    hits.sort(reverse=True)
    print(f"文字互撞：{len(hits)} 对（重叠 > 0.25 x 0.25 mm）")
    for a, s1, s2, ix, iy in hits[:12]:
        print(f"   {ix:4.1f} x {iy:4.1f} mm   {s1[:34]!r}  ×  {s2[:34]!r}")

    small = [(fs, s) for s, _, fs in texts if fs < 5.0]
    print(f"<5 pt 文字：{len(small)} 处")


for p in sys.argv[1:]:
    report(p)
