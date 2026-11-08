# -*- coding: utf-8 -*-
"""
18b_overview_figure_short.py — Figure 06 顶刊净版（3 行 × 3 列，纵轴对齐）

相对上一版（3×3 九宫格 + 标题区）的改动：
  · 删除 OVERVIEW kicker、两行主标题、两行说明副标题
  · 删除 PART I / PART II 分区标签及其下方灰色横线
  · 删除底部灰色横线与 "Simulated data" 彩色脚注（声明移到文字层/图注）
  · 八个面板按「纵轴左缘」与「x 轴基线」双重对齐：
      水平 — 由墨迹投影测出每块内 y 轴的 x，反解裁切框左边界，
             使所有块内 y 轴落在同一 x（块左缘、标题左缘也随之对齐）；
      垂直 — 由投影测出每块内 x 轴基线的 y，粘贴时整体下移补齐，
             使所有块基线落在同一 y（不做非等比缩放、不裁内容）。
  · 纯白底，图版内只保留面板与原始数据图元；无外框、无装饰线。

对齐约束：面板一律等比缩放；不改任何数据、坐标轴刻度、数值与统计图元。
图版内保留源图面板字母（B/C/D/E/F/B/C/D），重复字母与统计单位
属于文字层待办，不在本脚本里改动源图内容。

源图（600 dpi 原版）：
  Figure_PCDH9_perturbation.png             4254 × 3270   Fig. 1 A–F
  04_MEA实验A/04_图表/Figure5_MEA_A-E.png  4380 × 4290   Fig. 5 A–E

输出：06_总览图/PCDH9_总览图_重排.png / .pdf / _web.jpg / _1800.jpg
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data"
OUT.mkdir(exist_ok=True)

F1 = Image.open(ROOT / "data" / "Figure_PCDH9_perturbation.png").convert("RGB")
F5 = Image.open(ROOT / "data" / "Figure5_MEA_A-E.png").convert("RGB")

# ---- 面板裁切（x0, y0, x1, y1）：由行/列 ink-profile 实测 ---------------
BASE_BOXES = {
    # Fig. 1 行 1：A 91–1439 / B 1560–2763 / C 2792–4151
    "1B": (F1, (1555, 105, 2770, 1500)),
    "1C": (F1, (2790, 105, 4160, 1500)),
    # Fig. 1 行 2：D 91–1439（含 colorbar）/ E 1560–2900 / F 2905–4151
    "1D": (F1, (85, 1655, 1495, 3180)),
    "1E": (F1, (1548, 1655, 2905, 3180)),
    "1F": (F1, (2905, 1655, 4160, 3180)),
    # Fig. 5：B/C/D 同一行，D 含 Network burst 与 Active electrodes 两个子图
    "5B": (F5, (140, 1285, 1420, 2695)),
    "5C": (F5, (1570, 1285, 2860, 2695)),
    "5D": (F5, (3065, 1285, 4290, 2695)),
}

# ---- 版式参数 ------------------------------------------------------------
ROW_H = 553          # 面板统一高度（等比缩放，图内字号不额外缩小）
AXIS_T = 106         # 目标：块内 y 轴左缘统一落在此 x
MARGIN_X = 70
MARGIN_Y = 22
GAP_X = 44
GAP_Y = 30

ROWS = [
    ("1B", "1C", "1D"),
    ("1E", "1F"),           # 第 9 格留空
    ("5B", "5C", "5D"),
]

# 源图字母为 1B/1C/1D/1E/1F 与 5B/5C/5D，B/C/D 在一张图里重复出现，
# 顶刊图版不允许。这里只替换字母字形，不动标题文字与任何数据图元。
RELABEL = True
LETTERS = {
    "1B": "A", "1C": "B", "1D": "C",
    "1E": "D", "1F": "E",
    "5B": "F", "5C": "G", "5D": "H",
}
F_BOLD = "C:/Windows/Fonts/arialbd.ttf"
f_letter = ImageFont.truetype(F_BOLD, 30)


def scaled(im, h):
    """等比缩放到指定高度。"""
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)


def detect_axes(im):
    """墨迹投影：返回 (纵轴 x, x 轴基线 y)，坐标均相对本块左上角。

    纵轴 = 左 45% 区域内最长的连续竖直暗线；
    基线 = 下 55% 区域内最长的连续水平暗线。
    已逐块目视核对：红线落在 y 轴、蓝线落在 x 轴，不落在柱体/散点上。
    """
    a = np.array(im.convert("L"))
    ink = a < 120
    h, w = a.shape

    vx = np.zeros(w, int)
    for x in range(int(w * 0.45)):
        col = ink[:int(h * 0.9), x]
        best = cur = 0
        for v in col:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        vx[x] = best

    hy = np.zeros(h, int)
    for y in range(int(h * 0.45), h):
        row = ink[y, :]
        best = cur = 0
        for v in row:
            cur = cur + 1 if v else 0
            best = max(best, cur)
        hy[y] = best

    return int(np.argmax(vx)), int(np.argmax(hy))


# ---- 第一遍：测出每块内纵轴的 x -----------------------------------------
pass1 = {k: scaled(im.crop(b), ROW_H) for k, (im, b) in BASE_BOXES.items()}
axis1 = {k: detect_axes(t)[0] for k, t in pass1.items()}

# ---- 第二遍：反解裁切框左边界，让所有块的纵轴落在 AXIS_T ----------------
# 块内 axis = (axis_abs - x0) * ROW_H / box_h ；要让 axis → AXIS_T，
# 需 x0 += (axis - AXIS_T) * box_h / ROW_H。右边界不动，故块宽随之变化。
BOXES2 = {}
for k, (im, b) in BASE_BOXES.items():
    box_h = b[3] - b[1]
    shift = (axis1[k] - AXIS_T) * box_h / ROW_H
    x0 = max(0, int(round(b[0] + shift)))
    BOXES2[k] = (im, (x0, b[1], b[2], b[3]))

TILES = {k: scaled(im.crop(b), ROW_H) for k, (im, b) in BOXES2.items()}
axis2 = {k: detect_axes(t)[0] for k, t in TILES.items()}
base2 = {k: detect_axes(t)[1] for k, t in TILES.items()}


def relabel(tile, letter):
    """把块内左上角源图字母替换为统一的 A–H；标题文字与数据图元不动。"""
    a = np.array(tile.convert("L"))[:75, 100:132]
    rows = (a < 120).sum(axis=1)
    segs, start = [], None
    for y, v in enumerate(rows):
        if v > 0:
            if start is None:
                start = y
        elif start is not None:
            segs.append((start, y))
            start = None
    if start is not None:
        segs.append((start, 75))
    y0, y1 = segs[0]                      # 第一段就是粗体面板字母
    d = ImageDraw.Draw(tile)
    d.rectangle([100, y0 - 3, 130, y1 + 3], fill="white")
    d.text((104, y0 - 5), letter, font=f_letter, fill=(26, 26, 26))
    return tile


if RELABEL:
    TILES = {k: relabel(t, LETTERS[k]) for k, t in TILES.items()}

BASE_T = max(base2.values())          # 只允许下移，保证顶部标题不被裁
dy = {k: BASE_T - base2[k] for k in TILES}

# ---- 拼版 ---------------------------------------------------------------
COL_W = max(t.width for t in TILES.values())
ROW_SPAN = ROW_H + max(dy.values())
W = COL_W * 3 + GAP_X * 2 + MARGIN_X * 2
H = MARGIN_Y * 2 + ROW_SPAN * 3 + GAP_Y * 2

img = Image.new("RGB", (W, H), "white")
for r, keys in enumerate(ROWS):
    y_top = MARGIN_Y + r * (ROW_SPAN + GAP_Y)
    for c, k in enumerate(keys):
        x = MARGIN_X + c * (COL_W + GAP_X)
        img.paste(TILES[k], (x, y_top + dy[k]))

img.save(OUT / "PCDH9_总览图_重排.png", dpi=(300, 300))
img.save(OUT / "PCDH9_总览图_重排.pdf", resolution=300.0)
web = img.resize((1600, round(img.height * 1600 / img.width)), Image.LANCZOS)
web.save(OUT / "PCDH9_总览图_重排_web.jpg", quality=86, optimize=True, progressive=False)
web = img.resize((1500, round(img.height * 1500 / img.width)), Image.LANCZOS)
web.save(OUT / "PCDH9_总览图_重排_1800.jpg", quality=88, optimize=True, progressive=False)

# 参照口径：HTML 内嵌的原版是 2314 × 2127；磁盘上的 PCDH9_总览图.png
# 是更早一版 2403 × 2662。文档与对照按钮统一用前者。
EMBEDDED_OLD_H = 2127
old = Image.open(OUT / "PCDH9_总览图.png")
print("col_w=%d  row_h=%d  row_span=%d" % (COL_W, ROW_H, ROW_SPAN))
print("axis  before:", axis1)
print("axis  after :", axis2)
print("base  after :", base2, " target", BASE_T)
print("dy          :", dy)
print("size  = %d x %d px  (%.0f x %.0f mm @300dpi)" % (
    img.width, img.height, img.width / 300 * 25.4, img.height / 300 * 25.4))
print("disk old   = %d x %d px" % (old.width, old.height))
print("embedded old = 2314 x %d px  -> height ratio %.3f" % (
    EMBEDDED_OLD_H, img.height / EMBEDDED_OLD_H))
print("saved:", OUT / "PCDH9_总览图_重排.png")
