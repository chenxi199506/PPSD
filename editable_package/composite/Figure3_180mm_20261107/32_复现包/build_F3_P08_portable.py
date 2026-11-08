# -*- coding: utf-8 -*-
"""
F3_P08 · 四行十八面板 · v9 —— 状态排序图改为 NR-FB core 置顶
================================================================
相对 v8 **只改 6 个状态排序图的 y 轴顺序**：B / C / J / K / O / R 由
「PRG4+ lining 在顶、NR-FB core 在底」改为 **NR-FB core 置顶、其余状态
逆序**。D / L / T 是分组箱线（分组在横轴），不排状态，保持原样；
四个 UMAP 的图例顺序、v7 的 KDE 密度边缘勾勒、配色、面板字母、网格、
数据源与统计口径一律不动。

v8 的改动（本版全部继承）：统一状态显示名 / 统一无灰配色 / 统一图例顺序。
改动缘由与证据边界：

  原 08_addon_M2_L2.py 把 M2/L2 特有的 6 个状态固定涂成六档灰
  （GREY_NEW），而 A/I 用彩色主色板；N/Q 里 Lining-1/2/3、Myofibroblast、
  MHCII 占多数细胞，于是大半张 UMAP 是灰，六档灰彼此又难分辨。v8 建立
  一张跨四个图谱的统一状态字典：同一状态名 -> 同一显示名 + 同一颜色 +
  同一顺序位置，5 个共有状态在四个 UMAP 里同名同色，M2/L2 特有状态改用
  主色板同系彩色。名称统一只作用于显示层：不合并细胞，也不把
  Lining-1/2/3 改名为 PRG4+ lining（两套图谱是独立聚类，没有等价证据）。
  完整映射见 F3_P08_状态统一表_v9.csv。

v7 相对 v6 的改动（本版全部继承）：

  原版 F3_P01 的虚线既不是椭圆，也不是凸包：它是 NR-FB core 细胞的
  **高斯核密度（KDE）等值线**，画在 core 细胞密度的 5% 分位水平上
  （约覆盖 95% 的 core 细胞）。口径见原项目
  E:/NRFB_atlas_plate_20261104/sources/figure3/scripts/unified_annotation.py：
      kde  = gaussian_kde(core.T)
      pad  = maximum(0.2 * ptp(core), 0.3)
      grid = 160 x 160
      level= quantile(kde(core.T), 0.05)
      ax.contour(..., levels=[level], colors="black",
                 linestyles=[(0,(4,3))], linewidths=.9)
  以及 rebuild.py 的注释：“KDE boundary uses the 5th percentile density,
  enclosing approximately 95% of core cells”。它沿点云密度边缘走，可以有
  内凹、尖角和不对称，所以才是对细胞团边缘的勾勒。
  v5 的 2 sigma 椭圆和 v6 的「凸包 + 周期样条」都是光滑卵形，视觉上仍然像
  椭圆，不是原版那种贴着红色点团边缘走的不规则线。v7 改回密度等值线：
    1) 对 NR-FB core 的 UMAP 坐标建高斯 KDE（Scott 带宽 x 0.75，略收紧以
       让边缘起伏更清楚；x 1.0 更平滑，x 0.55 会出现锯齿）；
    2) 在 200 x 200 网格上取 core 细胞密度 5% 分位的等值线，取最大闭合环；
    3) 按原版虚线画法 (0,(4,3))、0.9 pt 绘制，颜色沿用 J.INK。
  实测四套图谱覆盖率 94.9%–95.0%、圈内纯度 72.9%–91.9%，均优于 v6 凸包；
  轮廓是描述性标注：不是置信区间、不是聚类边界、不是统计区域，也不能把
  「圈内纯度」读成分类精度。

v5 相对 v4 的两处改动（本版全部继承）：

  0. 修复 E / M / T 三格与同排其它格的「高度」不齐：
     三格原先 note=""（无灰色副注行），而 J.tag 的标题块是「自 axes 上沿
     向上生长」，少一行 note 会让字母 / 标题整体低约 2.9 mm（实测 D 顶
     17.95 mm vs E 顶 20.45 mm；L 127.93 vs M 130.47）。现为三格各补一行
     与同行等长的数据说明，18 格标题块高度、字母与标题基线全部对齐；
     同时把 T 的 disease / Ctrl 图例从轴下方（-0.17，向下多伸出约 6 mm）
     移到轴内顶部空白区，使第四行各格底部留白一致。
     轴框本身在 v4 中已经完全对齐（同行底边落在同一 mm 上），本版不改
     任何轴的 x / y / w / h。

v4 相对 v3 的两处改动（本版全部继承）：

  1. 移除第四行的 P（源 F3_P05-C，半月板 g1_pos）与 S（源 F3_P05-D，
     韧带 g1_pos）。其余面板沿用 v3 字母，故字母序列在 P / S 处跳号；
     第四行由 7 格改为 5 格等宽（与第一 / 三行同一 COL5 网格）。
  2. 四个 UMAP 面板（A / I / N / Q）的状态图例从点位下方移到绘图区
     **右侧的独立竖排图例栏**（每格右侧预留 22 mm），点位区不再为
     下方图例留出 38% 的 y 空白，UMAP 点位占比回到来源图水平。
     虚线椭圆仍圈在数据坐标上（它不是「下方注释」，不移动）。

v3 的还原口径（本版全部继承）：

  * 点图 F（源 F3_P01-J）恢复源图的 蓝–白–砖红连续标尺 + Normalize(-1, 1.8)，
    不再用 v2 的对称 TwoSlopeNorm（v2 把负值染成饱和蓝，源图没有蓝点）；
    状态名回到源表行序的全名、点径回到 3.1 + 8.3·frac^0.55、加 Marker gene 轴题。
  * 供体面板 D / L / T（源 F3_P01-B/E/H）由「散点 + 中位线」改回源图的
    箱线（淡色填充 + 描边）+ 蜂群散点（白边）+ 中位线 + 须线 + 白色均值菱形，
    并按源图配色：high/OA/disease 砖红，low/Ctrl 青绿或蓝灰；T 补 disease / Ctrl 图例。
  * 拟合面板 E / M（源 F3_P01-C/F）改回红/青绿双色点 + 灰色虚线回归，
    去掉红色实线与粉色置信带，ρ / P 两行注记移到图内左上，纵轴从 0 起。
  * PCDH9 面板 G（源 F3_P01-K）改回按 mean 降序的竖直灰带 + 中位短横线 +
    均值点 + 0 虚线 + 固定 y 刻度 + Kruskal–Wallis 注记；H（源 F3_P01-L）
    改回四分位箱体 + 蜂群点 + 白边 + 0 虚线。
  * CORE20 / g1_pos 的状态名由 v2 自造缩写（PRG4/Subl/TrAct…）改回
    来源图使用的 SHORT 全名；横轴题、副注改用来源图原文
    （"CORE20 (mean z)" / "Neural (mean gene z)" / "2nd = …; Cliff's d = …" /
     "rank r of n; tissue"）。
  * UMAP 补来源图的状态图例（两列彩色圆点）与 M2/L2 的 UMAP 1 / UMAP 2 轴题，
    点色沿用 v2 映射不变（配色不改动）。

**仍然没有任何一张图来自既有位图或 PDF 的裁切、贴图或缩放。**
18 个面板全部由原始表用 matplotlib 逐点 / 逐柱 / 逐箱重新绘制。

数据来源（与 v2 相同，读原表，不手抄数字）：
  G1/G2/M2/L2 *_obs.parquet + *.npz(emb_X_umap)、stats_sc.json、
  neural_module_audit.json、recomputed_donor_counts.csv、
  _external/fig6_data/Fig6A/C/D.tsv。

运行（解压后在本目录内）：python build_F3_P08_portable.py
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.path import Path as MplPath
from PIL import Image
from scipy import stats as SS
from scipy.stats import gaussian_kde

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUT = HERE / "outputs"

sys.path.insert(0, str(HERE))
import journal_style as J  # noqa: E402
import figstyle_constants as F  # noqa: E402

NRFB = F.NRFB
STATE_ORDER = F.STATE_ORDER
SHORT = F.SHORT
C_ACCENT = F.C_ACCENT
C_OTHER = F.C_OTHER
box_h = F.box_h

# 来源图的固定色（v23 / 08_addon / 12_neural_variant）
BRICK = "#B4482F"
NAVY = "#2F5D8A"
TEAL = "#2E9C8E"
GREY_BOX = "#8C8C8C"
SPINE = "#98A1A9"
FAINT = "#C9CFD4"
# 源图 Figure 6 D 的连续标尺（蓝–白–砖红），归一化区间 -1 … 1.8
CMAP_V23 = LinearSegmentedColormap.from_list(
    "nrfb", ["#4C78A8", "#C9D9E6", "#F3F0EE", "#DCAE9C", "#B4482F"])

ORDER_ALT = ["Lining-1", "Lining-2", "Lining-3", "Sublining", "Myofibroblast",
             "Remodeling", "AP-1 stress", "MHCII", "Proliferating",
             "NR-FB gradient", "NR-FB core"]

# ------------------------------------------------------- v8 统一状态字典
# 问题：来源脚本 08_addon_M2_L2.py 把 M2/L2 特有的 6 个状态固定涂成六档灰
# （GREY_NEW），A/I 却是彩色主色板；N/Q 里 Lining-1/2/3 + Myofibroblast +
# MHCII 占多数细胞，于是大半张 UMAP 是灰，六档灰彼此也几乎分不开。
# 另外 draw_umap 原用 STATE_ORDER + ORDER_ALT 拼接，共有状态被排到最前、
# 新状态排到最后，四个 UMAP 的图例顺序互不相同。
#
# v8：一张跨四个图谱的统一状态字典 —— 同一状态名对应同一显示名、同一颜色、
# 同一顺序位置。5 个共有状态（Sublining / Remodeling / AP-1 stress /
# Proliferating / NR-FB core）在四个图谱里同名同色；G1/G2 特有状态沿用
# 来源图配色；M2/L2 特有状态改为主色板同系的彩色，不再是灰。
# 名称统一只在显示层：不合并细胞，也不把 Lining-1/2/3 改名为
# PRG4+ lining —— 两套图谱是独立聚类，没有等价证据。映射表见
# F3_P08_状态统一表_v9.csv 与 meta 的 state_harmonisation 段。

UNIFIED_ORDER = [
    "PRG4+ lining", "Lining-1", "Lining-2", "Lining-3",
    "Sublining",
    "DKK3+ intermediate", "COMP+ transitional", "Transitional activated",
    "Myofibroblast",
    "Remodeling", "AP-1 stress",
    "Inflammatory", "MHCII", "Proliferating",
    "NR-FB gradient", "NR-FB core",
]

# v9：六个「每个状态一条」的排序面板（B / C / J / K / O / R）改为
# NR-FB core 置顶、其余状态按 UNIFIED_ORDER 逆序排列。只倒转 y 轴顺序，
# 不改数值、不改配色、不改状态名；D / L / T 是分组箱线（分组在横轴），
# 不涉及状态排序，保持原样。四个 UMAP 的图例仍按 UNIFIED_ORDER（功能家族）。
BOX_ORDER = list(reversed(UNIFIED_ORDER))

DISPLAY_NAME = dict(SHORT)
DISPLAY_NAME.update({
    # 编号式标签改成与主体系一致的书写风格；缩写风格对齐
    # "DKK3+ interm." / "COMP+ transit." / "Trans. activated"
    "Lining-1": "Lining 1",
    "Lining-2": "Lining 2",
    "Lining-3": "Lining 3",
    "MHCII": "MHCII+",
    "NR-FB gradient": "NR-FB grad.",
})

STATE_COLOR = {
    # G1 / G2 —— A、I 的来源图配色。原色板最后两档本就是灰，v8 换成
    # 同系低饱和彩色，让四个 UMAP 共用一套无灰色板（同名仍然同色）。
    "PRG4+ lining": C_OTHER[0],
    "Sublining": C_OTHER[1],
    "DKK3+ intermediate": C_OTHER[2],
    "COMP+ transitional": C_OTHER[3],
    "Transitional activated": C_OTHER[4],
    "Remodeling": C_OTHER[5],
    "AP-1 stress": C_OTHER[6],
    "Inflammatory": "#7C9C98",
    "Proliferating": "#AC8B5C",
    "NR-FB core": C_ACCENT,
    # M2 / L2 特有 —— 原六档灰改为同色系彩色，彼此可区分
    "Lining-1": "#3D6B9E",
    "Lining-2": "#5B9AA6",
    "Lining-3": "#9B86BE",
    "Myofibroblast": "#7FA96B",
    "MHCII": "#C97BA0",
    "NR-FB gradient": "#D98873",
}

STATE_FAMILY = {
    "PRG4+ lining": "Lining", "Lining-1": "Lining",
    "Lining-2": "Lining", "Lining-3": "Lining",
    "Sublining": "Sublining",
    "DKK3+ intermediate": "Transitional",
    "COMP+ transitional": "Transitional",
    "Transitional activated": "Transitional",
    "Myofibroblast": "Transitional",
    "Remodeling": "Remodeling", "AP-1 stress": "Stress",
    "Inflammatory": "Immune", "MHCII": "Immune",
    "Proliferating": "Proliferating",
    "NR-FB gradient": "NR-FB", "NR-FB core": "NR-FB",
}

G1G2_ONLY = ["PRG4+ lining", "DKK3+ intermediate", "COMP+ transitional",
             "Transitional activated", "Inflammatory"]
M2L2_ONLY = ["Lining-1", "Lining-2", "Lining-3", "Myofibroblast",
             "MHCII", "NR-FB gradient"]


def display_name(s):
    return DISPLAY_NAME.get(s, s)


K_ABBR = {"DKK3+ intermediate": "DKK3+ int.",
          "Transitional activated": "Trans. act.",
          "COMP+ transitional": "COMP+ trans."}

TISSUE_NOTE = {"G1": "synovium core8", "G2": "synovium extended",
               "M2": "meniscus (panel G)", "L2": "ligament (panel I)"}

# --------------------------------------------------------------- 画布（mm）
PW, PH = 320.0, 250.0
MG = 6.0
GAP = 3.0
CW = PW - 2 * MG
ROW_H = 36.0
# 行 1→2 与行 3→4 各需 14 mm；行 2 的 PCDH9 斜排状态名（约 60°）向下伸出
# 约 11 mm，若行 2→3 只留 20 mm，G 的 "COMP+ trans." / "Trans. act." 与
# L/M 的标题会贴到 < 1 mm（check_layout 查不出这类行间碰撞）。故在原先
# 下移 6 mm 的基础上再下移 4 mm，把该带加宽到 24 mm。
# 页脚是 fig.text(y=0.010) 固定在画布底部，不随行移动：行 4 底 222 mm
# 距页脚顶约 237 mm 仍有 15 mm 空白，不会相撞。
ROW_TOP = [26.0, 76.0, 136.0, 186.0]
COL5 = (CW - 4 * GAP) / 5.0
COL7 = (CW - 6 * GAP) / 7.0
W2 = CW - 2 * GAP
RIGHT_PAD = 2.0

# 每种画法左侧留给状态名 / 纵轴题的空间（mm）——v3 用全名，须比 v2 宽
LPAD = {
    "umap": (5.0, 3.0), "core20": (21.0, 17.0), "g1pos": (21.0, 16.0),
    "dot": (22.0, 22.0), "pcdh9": (14.0, 14.0), "corepc": (9.0, 9.0),
    "pctgrp": (13.0, 13.0), "pctoa": (13.0, 13.0), "fit": (15.0, 15.0),
    "tissue": (13.0, 13.0),
}

OUT_PNG = OUT / "F3_P08_four_rows_A-T_v9.png"
OUT_PDF = OUT / "F3_P08_four_rows_A-T_v9.pdf"
OUT_MAP = OUT / "F3_P08_面板映射_v9.csv"
OUT_META = OUT / "F3_P08_meta_v9.json"
OUT_STATES = OUT / "F3_P08_状态统一表_v9.csv"

# UMAP 面板右侧给状态图例留出的竖排图例栏宽度（mm）
LEG_W = 22.0
LEG_GAP = 1.0

# ------------------------------------------------------------ v7 边缘勾勒
# 原版 F3_P01 的虚线是 NR-FB core 细胞的 KDE 密度等值线（5% 分位水平），
# 不是椭圆也不是凸包。它沿点云密度边缘走，允许内凹 / 尖角 / 不对称。
KDE_QUANTILE = 0.05        # core 细胞密度的 5% 分位 ≈ 覆盖 95% core 细胞
KDE_BW_FACTOR = 0.75       # 相对 Scott 带宽收紧：1.0 太光滑，0.55 起锯齿
KDE_GRID = 200             # 等值线网格 200 x 200
OUTLINE_STATS = {}
ELLIPSE_V5_STATS = {}


def _mahalanobis(p, pts):
    mu = p.mean(axis=0)
    cov = np.cov(p.T)
    inv = np.linalg.inv(cov + 1e-9 * np.eye(2))
    return np.sqrt(np.einsum("ij,jk,ik->i", pts - mu, inv, pts - mu))


def kde_edge_contour(p, u, m):
    """NR-FB core 细胞的 KDE 密度边缘：5% 分位等值线的最大闭合环。"""
    kde = gaussian_kde(p.T)
    scott = float(kde.factor)
    kde.set_bandwidth(bw_method=scott * KDE_BW_FACTOR)
    pad = np.maximum(np.ptp(p, axis=0) * 0.2, 0.3)
    xx, yy = np.mgrid[
        p[:, 0].min() - pad[0]:p[:, 0].max() + pad[0]:KDE_GRID * 1j,
        p[:, 1].min() - pad[1]:p[:, 1].max() + pad[1]:KDE_GRID * 1j,
    ]
    dens = kde(np.vstack([xx.ravel(), yy.ravel()])).reshape(xx.shape)
    lvl = float(np.quantile(kde(p.T), KDE_QUANTILE))
    # 离屏取等值线顶点，避免把 contour 的其它副作用带进图版坐标
    probe = plt.figure()
    pax = probe.add_subplot(111)
    cs = pax.contour(xx, yy, dens, levels=[lvl])
    segs = [np.asarray(s) for s in cs.allsegs[0] if len(s) > 20]
    plt.close(probe)
    loops = [np.vstack([s, s[0]]) if not np.allclose(s[0], s[-1]) else s
             for s in segs]
    if not loops:
        raise RuntimeError("KDE 密度等值线未生成闭合环；请检查带宽或分位水平")
    xy = max(loops, key=len)
    path = MplPath(xy)
    inside_core = path.contains_points(p)
    inside_all = path.contains_points(u)
    info = dict(
        n_core=int(len(p)), quantile=KDE_QUANTILE,
        bw_factor=KDE_BW_FACTOR, bw_scott=round(scott, 6),
        grid=KDE_GRID, level=round(lvl, 8),
        n_loops=len(loops), n_contour_points=int(len(xy)),
        core_covered=round(float(inside_core.mean()), 4),
        purity=round(float(m[inside_all].mean()), 4)
        if inside_all.any() else None,
    )
    return xy, info


def ellipse_v5_stats(p, u, m):
    """仅用于 meta 里对照 v5 的 2 sigma 椭圆，不参与绘图。"""
    inside_all = _mahalanobis(p, u) <= 2.0
    return dict(core_covered=round(float((_mahalanobis(p, p) <= 2.0).mean()), 4),
                purity=round(float(m[inside_all].mean()), 4)
                if inside_all.any() else None)


_CACHE = {}


def obs(key):
    if key not in _CACHE:
        _CACHE[key] = pd.read_csv(DATA / f"{key}_obs.csv.gz")
    return _CACHE[key]


def umap(key):
    k = "u_" + key
    if k not in _CACHE:
        _CACHE[k] = np.load(DATA / f"{key}_umap.npz")["emb_X_umap"]
    return _CACHE[k]


def donor():
    if "donor" not in _CACHE:
        _CACHE["donor"] = pd.read_csv(DATA / "recomputed_donor_counts.csv")
    return _CACHE["donor"]


def audit():
    if "audit" not in _CACHE:
        _CACHE["audit"] = json.load(
            open(DATA / "neural_module_audit.json", encoding="utf-8"))
    return _CACHE["audit"]


def fig6(name):
    k = "f6_" + name
    if k not in _CACHE:
        _CACHE[k] = pd.read_csv(DATA / f"{name}.tsv", sep="\t")
    return _CACHE[k]


# v8：配色只从统一字典取，不再有「新状态专用灰阶」这条旁路。
COLORS = dict(STATE_COLOR)


def color_of(s):
    if s in COLORS:
        return COLORS[s]
    return C_OTHER[sum(ord(c) for c in s) % len(C_OTHER)]


def cliff_delta(a, b):
    a = np.asarray(a, float); a = a[np.isfinite(a)]
    b = np.asarray(b, float); b = b[np.isfinite(b)]
    if not len(a) or not len(b):
        return np.nan
    u = SS.mannwhitneyu(a, b, alternative="two-sided").statistic
    return 2 * u / (len(a) * len(b)) - 1


def second_highest(o):
    means = o.groupby("state")["m_CORE20"].mean().sort_values(ascending=False)
    top, second = means.index[0], means.index[1]
    assert top == NRFB, f"CORE20 最高状态不是 NR-FB core: {top}"
    return second, float(cliff_delta(
        o.loc[o["state"] == top, "m_CORE20"],
        o.loc[o["state"] == second, "m_CORE20"]))


def add_ax(fig, x, y_top, w, h=ROW_H):
    return fig.add_axes([x / PW, (PH - y_top - h) / PH, w / PW, h / PH])


def tag(ax, letter, title, w, note=None):
    # 来源图的副注在标题正下方一行；放进 J.tag 的 note 槽，不再浮在图内右上角压标题
    J.tag(ax.figure, ax, letter, title, note=note,
          gap_mm=1.5, tx_mm=3.4, size_letter=9.0, size_title=6.6,
          size_note=6.0, max_mm=max(20.0, w - 4.2))


def finish_axis(ax, size=5.6):
    ax.tick_params(axis="both", labelsize=size, length=2.0, width=0.45, pad=1.4)
    for lbl in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
        lbl.set_fontsize(size)
    if ax.get_xlabel():
        ax.xaxis.label.set_fontsize(size)
    if ax.get_ylabel():
        ax.yaxis.label.set_fontsize(size)


def soft_spines(ax, keep=True):
    if keep:
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(SPINE)
            ax.spines[s].set_linewidth(0.5)
    else:
        for s in ax.spines.values():
            s.set_visible(False)


def clip_xticks(ax):
    lo, hi = ax.get_xlim()
    ticks = [t for t in ax.get_xticks() if lo - 1e-9 <= t <= hi + 1e-9]
    if len(ticks) != len(ax.get_xticks()):
        ax.set_xticks(ticks)


def beeswarm(v, dy=0.142, dx=0.155, maxk=2):
    """与来源图 L 相同的一维蜂群：值相近的点左右错开。"""
    order = np.argsort(v)
    xs = np.zeros(len(v))
    placed = []
    for i in order:
        cand = [0.0]
        for k in range(1, maxk + 1):
            cand += [k * dx, -k * dx]
        for c in cand:
            if all(abs(v[i] - v[j]) >= dy or abs(c - xs[j]) >= dx * 0.9
                   for j in placed):
                xs[i] = c
                break
        placed.append(i)
    return xs


# =============================================================== 面板画法
def draw_umap(ax, key, narrow=False, legend_ax=None):
    o, u = obs(key), umap(key)
    st = o["state"].values
    # v8：四个 UMAP 共用同一套功能家族顺序，与同行箱线图 / 点图的行序一致
    order = [s for s in UNIFIED_ORDER if s in set(st)]
    for s in order:
        if s == NRFB:
            continue
        m = st == s
        ax.scatter(u[m, 0], u[m, 1], s=0.22, c=[color_of(s)],
                   alpha=0.30, lw=0, rasterized=True)
    m = st == NRFB
    ax.scatter(u[m, 0], u[m, 1], s=0.30, c=[C_ACCENT],
               alpha=0.55, lw=0, rasterized=True)
    p = u[m]
    xy, info = kde_edge_contour(p, u, m)
    OUTLINE_STATS[key] = info
    ELLIPSE_V5_STATS[key] = ellipse_v5_stats(p, u, m)
    # 原版虚线画法：长划 (4,3)、0.9 pt；颜色沿用 J.INK（配色不变）
    ax.plot(xy[:, 0], xy[:, 1], color=J.INK, lw=0.9,
            ls=(0, (4, 3)), zorder=5)
    # v4：状态图例移到绘图区右侧的独立竖排图例栏；绘图区不再为下方
    # 图例预留 38% 的 y 空白，datalim 让点位按真实比例填满整个绘图框。
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xticks([]); ax.set_yticks([])
    soft_spines(ax, keep=False)
    if key in ("M2", "L2"):
        ax.set_xlabel("UMAP 1", fontsize=5.6, labelpad=1)
        ax.set_ylabel("UMAP 2", fontsize=5.6, labelpad=1)
    # 来源图的图例：彩色圆点 + SHORT 状态名；v4 由两列改为右侧单列。
    # STATE_ORDER 与 ORDER_ALT 有交集（Sublining / Remodeling / AP-1 stress /
    # Proliferating / NR-FB core），绘图循环保留逐状态叠加，图例条目只去重显示。
    legend_order = list(dict.fromkeys(order))
    handles = [Line2D([], [], marker="o", ls="", ms=2.6, mfc=color_of(s),
                      mec="none", label=display_name(s)) for s in legend_order]
    if legend_ax is not None:
        legend_ax.legend(handles=handles, ncol=1, loc="center left",
                         bbox_to_anchor=(-0.01, 0.5), frameon=False,
                         fontsize=5.6, handletextpad=0.22,
                         handlelength=1.1, labelspacing=0.10,
                         borderpad=0.0)
    else:  # 兜底：没有独立图例轴时仍画在绘图轴内下方
        ax.legend(handles=handles, ncol=2, loc="lower center",
                  bbox_to_anchor=(0.5, 0.012), frameon=True, facecolor="white",
                  edgecolor="none", framealpha=0.92, fontsize=5.6,
                  handletextpad=0.25, columnspacing=0.9, labelspacing=0.10,
                  borderpad=0.05)
    return len(o)


def draw_core20(ax, key, narrow=False):
    o = obs(key)
    states = [s for s in BOX_ORDER if s in set(o["state"])]
    data = {s: o.loc[o["state"] == s, "m_CORE20"].values for s in states}
    box_h(ax, data, states, {s: color_of(s) for s in states}, show_labels=False)
    ax.set_yticklabels([display_name(s) for s in states], fontsize=5.6)
    z = key in ("G1", "G2")
    ax.set_xlabel("CORE20 (mean z)" if z else "CORE20 (log-norm mean)",
                  fontsize=5.6, labelpad=2)
    soft_spines(ax, keep=True)
    ax.tick_params(axis="y", length=0)
    if z:
        ax.axvline(0, color=FAINT, lw=0.5, ls=(0, (3, 2)), zorder=0)
    finish_axis(ax, 5.6)
    return second_highest(o)


def draw_g1pos(ax, key, narrow=False):
    d = audit()["datasets"][key]["variants"]["g1_pos"]
    g = pd.Series(d["per_state"])
    states = [s for s in BOX_ORDER if s in g.index]
    vals = g.reindex(states).values
    yy = np.arange(len(states))[::-1]
    ax.barh(yy, vals, height=0.62,
            color=[C_ACCENT if s == NRFB else J.GRAY for s in states],
            alpha=0.9, lw=0)
    ax.axvline(0, color=J.RULE, lw=0.5)
    ax.set_ylim(-0.7, len(states) - 0.3)
    ax.set_yticks(yy)
    ax.set_yticklabels([display_name(s) for s in states], fontsize=5.6)
    ax.tick_params(axis="y", length=0)
    ax.set_xlabel("Neural (mean gene z)", fontsize=5.6, labelpad=2)
    soft_spines(ax, keep=True)
    finish_axis(ax, 5.6)
    return d


def draw_marker_dot(ax):
    """源图 Figure 6 D 的原画法：连续色标 + 分档点径 + 每两列分隔线。"""
    d = fig6("Fig6D_marker_expr_matrix").set_index("state")
    states = list(d.index)          # 源表行序，不重排
    genes = list(d.columns)
    Z = d.values.astype(float)
    nr, nc = Z.shape
    vmin, vmax = -1.0, 1.8
    norm = Normalize(vmin, vmax)
    frac = np.clip((Z - vmin) / (vmax - vmin), 0, 1)
    # 源图 J 的绘图区高 205 pt / 10 行（行距 20.5 pt）；本板只有 30 mm ≈ 85 pt，
    # 行距 8.5 pt，故按 0.46 缩放点径，否则上下相邻点会连成一串、蓝点也过饱和。
    d_pt = (3.1 + 8.3 * frac ** 0.55) * 0.46
    size = d_pt ** 2
    for j in range(2, nc, 2):
        ax.axvline(j - 0.5, color="#C9CFD4", lw=0.7, zorder=1)
    for i in range(nr):
        for j in range(nc):
            ax.scatter(j, i, s=size[i, j], c=[CMAP_V23(norm(Z[i, j]))],
                       linewidth=0, edgecolors="none", zorder=3)
    ax.set_xlim(-0.6, nc - 0.4)
    ax.set_ylim(nr - 0.4, -0.6)
    ax.set_xticks(range(nc))
    ax.set_xticklabels(genes, rotation=55, ha="right", va="top",
                       rotation_mode="anchor", fontsize=5.6, color="#4A5158")
    ax.set_yticks(range(nr))
    ax.set_yticklabels(states, fontsize=5.6, color="#4A5158")
    ax.set_xlabel("Marker gene", fontsize=5.6, labelpad=0)
    soft_spines(ax, keep=False)
    ax.tick_params(length=0, pad=1.6)
    finish_axis(ax, 5.6)


def draw_pcdh9_by_state(ax):
    """源图 Figure 6 A：竖直灰带 mean±0.5SD + 中位短横线 + 均值点。"""
    d = fig6("Fig6A_pcdh9_by_state").sort_values("mean", ascending=False)
    names = list(d["state"])
    mean = d["mean"].values.astype(float)
    med = d["median"].values.astype(float)
    sd = d["sd"].values.astype(float)
    x = np.arange(len(d), dtype=float)
    core = names.index(NRFB)
    for i in range(len(d)):
        col = BRICK if i == core else "#C6CDD3"
        ax.add_patch(Rectangle((x[i] - 0.235, mean[i] - 0.5 * sd[i]),
                               0.47, sd[i], facecolor=col, edgecolor="none",
                               alpha=0.20 if i == core else 0.36, zorder=1))
        ax.plot([x[i] - 0.235, x[i] + 0.235], [med[i], med[i]],
                color=BRICK if i == core else "#6E767D",
                lw=2.6 if i == core else 1.3, zorder=2, solid_capstyle="butt")
    ax.scatter(x, mean, s=26,
               c=[BRICK if i == core else "#7E868D" for i in range(len(d))],
               linewidth=0, zorder=3)
    ax.axhline(0, color="#6E767D", lw=0.7, ls=(0, (3, 3)), zorder=0)
    ax.set_xlim(-0.62, len(d) - 0.38)
    ax.set_ylim(-0.78, 2.52)
    ax.set_xticks(x)
    # 69° 斜排在本板 100 mm 宽里会向左越出面板、压到 F 的基因名；
    # 改 48° 并加宽左侧标签槽，状态名仍保持来源图的斜排读法。
    ax.set_xticklabels([K_ABBR.get(s, s) for s in names], rotation=48,
                       ha="right", va="top", rotation_mode="anchor",
                       fontsize=5.6, color="#4A5158")
    ax.tick_params(axis="x", pad=1.0)
    ax.set_yticks([-0.5, 0, 0.5, 1.0, 1.5, 2.0, 2.5])
    ax.set_yticklabels(["-0.5", "0", "0.5", "1.0", "1.5", "2.0", "2.5"])
    ax.set_ylabel("PCDH9 (z units)", fontsize=5.6, labelpad=2)
    soft_spines(ax, keep=True)
    finish_axis(ax, 5.6)
    ax.text(0.99, 1.01, "Kruskal–Wallis  P < 1e-300", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=5.6, color=J.MUTED)


def draw_core_pcdh9(ax):
    """源图 Figure 6 C 的 L：四分位箱体 + 中位线 + min/max + 蜂群点。"""
    d = fig6("Fig6C_core_within_donor")
    for xi, (lab, key, col) in enumerate(
            [("Ctrl", "healthy", NAVY), ("OA", "OA", BRICK)]):
        v = d.loc[d.condition == key, "mean"].values.astype(float)
        q1, q2, q3 = np.percentile(v, [25, 50, 75])
        ax.add_patch(Rectangle((xi - 0.25, q1), 0.50, q3 - q1,
                               facecolor=col, alpha=0.16, edgecolor=col,
                               linewidth=0.9, zorder=1))
        ax.plot([xi - 0.25, xi + 0.25], [q2, q2], color=col, lw=2.0, zorder=2)
        ax.plot([xi, xi], [v.min(), v.max()], color=col, lw=0.7,
                alpha=0.5, zorder=1)
        ax.scatter(xi + beeswarm(v), v, s=26, facecolor=col,
                   edgecolor="white", linewidth=0.7, alpha=0.9, zorder=3)
    ax.axhline(0, color="#B9C0C6", lw=0.7, ls=(0, (3.2, 2.4)), zorder=0)
    ax.set_xlim(-0.62, 1.62)
    ax.set_ylim(-0.75, 2.62)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["Ctrl", "OA"])
    ax.set_yticks([-0.5, 0, 0.5, 1.0, 1.5, 2.0, 2.5])
    ax.set_yticklabels(["-0.5", "0", "0.5", "1.0", "1.5", "2.0", "2.5"])
    ax.set_ylabel("PCDH9 in core (z)", fontsize=5.6, labelpad=2)
    soft_spines(ax, keep=True)
    finish_axis(ax, 5.6)


def draw_donor_box(ax, groups, colors, ylim, ylabel, legend=False,
                   narrow=False):
    """来源图 B/E 的原画法：箱线 + 白边散点 + 均值菱形；不再只画散点。"""
    for i, (name, v) in enumerate(groups):
        v = np.asarray(v, float)
        v = v[np.isfinite(v)]
        if not len(v):
            continue
        col = colors[name]
        q1, q2, q3 = np.percentile(v, [25, 50, 75])
        ax.add_patch(Rectangle((i - 0.22, q1), 0.44, q3 - q1,
                               facecolor=col, alpha=0.13, edgecolor=col,
                               linewidth=1.0, zorder=1))
        ax.plot([i - 0.22, i + 0.22], [q2, q2], color=col, lw=1.6, zorder=3)
        lo, hi = float(v.min()), float(v.max())
        ax.plot([i, i], [lo, hi], color=col, lw=0.7, alpha=0.8, zorder=1)
        ax.plot([i - 0.12, i + 0.12], [lo, lo], color=col, lw=0.7, zorder=1)
        ax.plot([i - 0.12, i + 0.12], [hi, hi], color=col, lw=0.7, zorder=1)
        jit = (np.random.default_rng(11 + i).random(len(v)) - 0.5) * 0.16
        ax.scatter(i + jit, v, s=26, facecolor=col, edgecolor="white",
                   linewidth=0.7, alpha=0.92, zorder=4)
        ax.scatter([i], [float(np.mean(v))], s=26, marker="D",
                   facecolor="white", edgecolor=col, linewidth=1.0, zorder=5)
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([n for n, _ in groups])
    ax.set_xlim(-0.55, len(groups) - 0.45)
    ax.set_ylim(0, ylim)
    ax.axhline(0, color=FAINT, lw=0.6, zorder=0)
    ax.set_ylabel(ylabel, fontsize=5.6, labelpad=2)
    soft_spines(ax, keep=True)
    finish_axis(ax, 5.6)
    if legend:
        hs = [Line2D([], [], marker="s", ls="", ms=3.6, mfc=colors[n],
                     mec=colors[n], label=n) for n, _ in colors.items()]
        ax.legend(handles=hs, ncol=2, loc="upper center",
                  bbox_to_anchor=(0.5, -0.16), frameon=False, fontsize=5.6,
                  handletextpad=0.3, columnspacing=0.8, labelspacing=0.2,
                  borderpad=0.0)


def draw_tissue_box(ax, narrow=True):
    """来源图 H：meniscus / ligament 两组，每组 disease 与 Ctrl 两个箱。"""
    rows = []
    for key, tissue in (("M2", "meniscus"), ("L2", "ligament")):
        o = obs(key)
        for s, g in o.groupby("sample", observed=True):
            cond = g["condition_geo_corrected"].iloc[0]
            dis = "Ctrl" if cond == "healthy" else "disease"
            rows.append(dict(tissue=tissue, group=dis,
                             pct=100.0 * (g["state"] == NRFB).mean()))
    d = pd.DataFrame(rows)
    palette = {"disease": BRICK, "Ctrl": "#6E818C"}
    for i, tissue in enumerate(["meniscus", "ligament"]):
        for j, gname in enumerate(["disease", "Ctrl"]):
            v = d.loc[(d.tissue == tissue) & (d.group == gname), "pct"].values
            if not len(v):
                continue
            x = 2 * i + j * 0.95
            col = palette[gname]
            q1, q2, q3 = np.percentile(v, [25, 50, 75])
            ax.add_patch(Rectangle((x - 0.32, q1), 0.64, q3 - q1,
                                   facecolor=col, alpha=0.15,
                                   edgecolor=col, linewidth=1.0, zorder=1))
            ax.plot([x - 0.32, x + 0.32], [q2, q2], color=col, lw=1.6, zorder=3)
            lo, hi = float(v.min()), float(v.max())
            ax.plot([x, x], [lo, hi], color=col, lw=0.7, alpha=0.8, zorder=1)
            ax.plot([x - 0.14, x + 0.14], [lo, lo], color=col, lw=0.7)
            ax.plot([x - 0.14, x + 0.14], [hi, hi], color=col, lw=0.7)
            ax.scatter(x + beeswarm(v, dy=1.0, dx=0.16), v, s=24,
                       facecolor=col, edgecolor="white", linewidth=0.7,
                       alpha=0.92, zorder=4)
            ax.scatter([x], [float(np.mean(v))], s=24, marker="D",
                       facecolor="white", edgecolor=col, linewidth=1.0, zorder=5)
    ax.set_xticks([0.475, 2.475])
    ax.set_xticklabels(["meniscus", "ligament"])
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(0, 40)
    ax.axhline(0, color=FAINT, lw=0.6, zorder=0)
    ax.set_ylabel("NR-FB core share\n(% of fibroblasts)", fontsize=5.6,
                  labelpad=2)
    soft_spines(ax, keep=True)
    finish_axis(ax, 5.6)
    hs = [Line2D([], [], marker="s", ls="", ms=3.6, mfc=palette[n],
                 mec=palette[n], label=n) for n in ("disease", "Ctrl")]
    # v5：图例收进轴内顶部空白区（ylim 0-40，数据最高约 28，顶部约 30% 为空），
    # 不再挂在轴下方多伸出约 6 mm；第四行各格底部留白因此一致。
    ax.legend(handles=hs, ncol=2, loc="upper center",
              bbox_to_anchor=(0.5, 0.995), frameon=False, fontsize=5.6,
              handletextpad=0.3, columnspacing=0.8, labelspacing=0.2,
              borderpad=0.0)
    return d


def draw_fit(ax, df, ylim, ylabel):
    """来源图 C/F：红/青绿双色点 + 灰色虚线回归，无置信带，ρ/P 两行在左上。"""
    q = df[df.PPSD_score.notna()]
    x = q.PPSD_score.values.astype(float)
    y = q.pct.values.astype(float)
    rho, p = SS.spearmanr(x, y)
    hi = q.PPSD_group.eq("high-PPSD").values
    cols = np.where(hi, BRICK, TEAL)
    ax.scatter(x, y, s=36, c=cols, edgecolors="white", linewidths=0.6,
               zorder=3)
    b, a = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, a + b * xs, color="#B9C0C6", lw=1.6, ls=(0, (5, 4)), zorder=2)
    ax.axhline(0, color=FAINT, lw=0.6, zorder=0)
    ax.set_ylim(0, ylim)
    span = x.max() - x.min()
    ax.set_xlim(x.min() - 0.06 * span, x.max() + 0.06 * span)
    ax.set_xlabel("PPSD score", fontsize=5.6, labelpad=2)
    ax.set_ylabel(ylabel, fontsize=5.6, labelpad=2)
    soft_spines(ax, keep=True)
    finish_axis(ax, 5.6)
    ax.text(0.035, 0.96, f"ρ = {rho:.3f}\nP = {p:.4g} (n = {len(x)})",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=5.6, color=J.MUTED, zorder=9)
    return float(rho), float(p), len(x)


# =============================================================== 18 格清单
PANEL_MAP = [
    ("A", 0, "F3_P01", "A", "NR-FB forms a region",       "umap",   "G1"),
    ("B", 0, "F3_P02", "P", "CORE20 marks one state",     "core20", "G1"),
    ("C", 0, "F3_P05", "A", "G1-selected genes peak",     "g1pos",  "G1"),
    ("D", 0, "F3_P01", "B", "Core share by pain stratum", "pctgrp", "G1"),
    ("E", 0, "F3_P01", "C", "Core share vs PPSD",         "fit",    "G1"),

    ("F", 1, "F3_P01", "J", "Markers separate states",    "dot",    None),
    ("G", 1, "F3_P01", "K", "PCDH9 peaks in NR-FB",       "pcdh9",  None),
    ("H", 1, "F3_P01", "L", "Core PCDH9: OA vs Ctrl",     "corepc", None),

    ("I", 2, "F3_P01", "D", "The state persists in G2",   "umap",   "G2"),
    ("J", 2, "F3_P02", "Q", "CORE20 again in G2",         "core20", "G2"),
    ("K", 2, "F3_P05", "B", "The subset peaks in G2",     "g1pos",  "G2"),
    ("L", 2, "F3_P01", "E", "Core share higher in OA",    "pctoa",  None),
    ("M", 2, "F3_P01", "F", "PPSD link at n = 28",        "fit",    "G2"),

    ("N", 3, "F3_P01", "G", "Meniscus UMAP",              "umap",   "M2"),
    ("O", 3, "F3_P02", "X", "CORE20 in meniscus",         "core20", "M2"),
    # v4 移除：("P", 3, "F3_P05", "C", "g1_pos in meniscus", "g1pos", "M2")
    ("Q", 3, "F3_P01", "I", "Ligament UMAP",              "umap",   "L2"),
    ("R", 3, "F3_P02", "Y", "CORE20 in ligament",         "core20", "L2"),
    # v4 移除：("S", 3, "F3_P05", "D", "g1_pos in ligament", "g1pos", "L2")
    ("T", 3, "F3_P01", "H", "Core share by tissue",       "tissue", None),
]


def positions():
    out = {}
    for i, L in enumerate("ABCDE"):
        out[L] = (MG + i * (COL5 + GAP), ROW_TOP[0], COL5)
    out["F"] = (MG, ROW_TOP[1], W2 / 2.0)
    out["G"] = (MG + W2 / 2.0 + GAP, ROW_TOP[1], W2 / 3.0)
    out["H"] = (MG + W2 / 2.0 + W2 / 3.0 + 2 * GAP, ROW_TOP[1], W2 / 6.0)
    for i, L in enumerate("IJKLM"):
        out[L] = (MG + i * (COL5 + GAP), ROW_TOP[2], COL5)
    # v4：第四行删去 P / S 后为 5 格等宽，与第一 / 三行共用 COL5 网格
    for i, L in enumerate("NOQRT"):
        out[L] = (MG + i * (COL5 + GAP), ROW_TOP[3], COL5)
    return out


HEADER = (
    "Figure 3 · F3_P08",
    "The NR-FB state across four single-cell atlases, and what defines it",
    "Eighteen panels in four rows, all re-drawn from source tables (no image cropping); "
    "letters follow v3 with P and S removed; UMAP state legends are placed to the right of each embedding; "
    "320 mm working plate",
)

FOOTER = (
    "Single-cell RNA-seq only; no bulk data. Analytic unit: the cell for A-C, F, G, I-K, N, O, Q and R "
    "(G1 35,862 / 8 donors; G2 96,236 / 35; M2 meniscus 34,760 / 14; L2 ligament 21,243 / 6); the donor for "
    "D, E, H, L, M and T. Method: all 18 panels are drawn from the source tables (obs.parquet, npz UMAP "
    "coordinates, stats_sc.json, neural_module_audit.json, recomputed donor counts, Figure 6 source TSVs); no panel "
    "was cropped, pasted or rescaled. Panel types and palette follow the source plates: "
    "box-and-whisker with white-edged donor points and a white mean diamond in D, L, H, T; dashed grey linear "
    "fit without a confidence band in E and M; the source blue-white-brick scale (Normalize -1 to 1.8) in F; grey "
    "mean +/- 0.5 SD bands in G. G1/G2 CORE20 scores are gene-wise z, M2/L2 log-normalised, so absolute values "
    "are not comparable across those rows. Cliff's d uses the true second-highest state. In B, C, J, K, O and R, "
    "states run NR-FB core first, then in reverse. The "
    "g1_pos 20-gene subset was selected in G1 by positive CORE20 correlation only (no threshold, test or "
    "multiple-testing correction; 19/20 genes present in L2): C and K are circular with G1, and the meniscus and "
    "ligament g1_pos bars from v3 are omitted. Does not support: that CORE20 is the only valid definition of "
    "NR-FB, that PCDH9 causes the programme, that NR-FB contacts nerve fibres, or that g1_pos provides independent "
    "validation. All clinical associations are correlations; no spatial or perturbation data are shown. Letters "
    "follow v3 numbering with P and S removed. In the four UMAPs the legend sits right of the embedding; "
    "the dashed line is a Gaussian kernel-density contour of NR-FB core cells at the 5th percentile of their "
    "density (about 95% of core cells inside), tracing the observed density edge with its indentations; it is "
    "descriptive, not a fitted ellipse, convex hull, confidence region, cluster boundary or statistical region, "
    "and purity inside it is not classification accuracy. One dictionary sets state names and colours "
    "across the four UMAPs: the five shared states have identical names and colours, the six meniscus- and "
    "ligament-specific states use the same colour family instead of grey, and all legends follow one "
    "functional-family order. Harmonisation is display-layer only: clusters were not merged and independently "
    "annotated states are not declared equivalent."
)


def main():
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    fig = J.plate(PW, PH)
    J.header(fig, *HEADER)

    pos = positions()
    D = donor()
    g1 = D[D.group == "G1_core8"]
    g2 = D[D.group == "G2_OA_healthy"]
    stat_rows, panel_rows = [], []

    for letter, row, src, src_panel, title, kind, arg in PANEL_MAP:
        x, ytop, w = pos[letter]
        narrow = (row == 3)
        lpad = LPAD[kind][1 if narrow else 0]
        tag_ax = add_ax(fig, x, ytop, w)
        tag_ax.set_xticks([]); tag_ax.set_yticks([]); tag_ax.set_axis_off()
        # 点图的 20 个斜排基因名还要向下占约 10 mm，单独把它压矮，避免压到下一行标题
        plot_h = 30.0 if letter == "F" else ROW_H
        is_umap = kind == "umap"
        leg_ax = None
        if is_umap:
            # 绘图区右侧让出 LEG_W 作为竖排图例栏（含 1 mm 间隔）
            leg_ax = add_ax(fig, x + w - RIGHT_PAD - LEG_W + LEG_GAP,
                            ytop, LEG_W - LEG_GAP, h=plot_h)
            leg_ax.set_xticks([]); leg_ax.set_yticks([])
            leg_ax.set_axis_off()
        ax = add_ax(fig, x + lpad, ytop,
                    w - lpad - RIGHT_PAD - (LEG_W if is_umap else 0.0),
                    h=plot_h)
        note, extra = "", {}

        if kind == "umap":
            n_cell = draw_umap(ax, arg, narrow=narrow, legend_ax=leg_ax)
            note = f"{arg}; {n_cell // 1000}k cells" if narrow else f"{arg} UMAP; {n_cell:,} cells"
            extra = dict(dataset=arg, n_cells=int(n_cell))
        elif kind == "core20":
            second, d = draw_core20(ax, arg, narrow=narrow)
            note = (f"2nd = {display_name(second)}; Cliff's d = {d:.2f}"
                    if not narrow else f"Cliff's d = {d:.2f}")
            extra = dict(dataset=arg, second=second, cliff_d=round(d, 4))
        elif kind == "g1pos":
            gd = draw_g1pos(ax, arg, narrow=narrow)
            nstate = len(gd["per_state"])
            note = (f"rank {gd['rank']} of {nstate}; {TISSUE_NOTE[arg]}"
                    if not narrow else f"rank {gd['rank']}/{nstate}")
            extra = dict(dataset=arg, n_genes=gd["n_genes"],
                         rank=gd["rank"], n_states=nstate)
        elif kind == "pctgrp":
            groups = [("high", g1.loc[g1.PPSD_group == "high-PPSD", "pct"].values),
                      ("low", g1.loc[g1.PPSD_group == "low-PPSD", "pct"].values),
                      ("Ctrl", g1.loc[g1.PPSD_group == "healthy-ref", "pct"].values)]
            draw_donor_box(ax, groups,
                           {"high": BRICK, "low": TEAL, "Ctrl": NAVY},
                           30, "NR-FB core (% fibroblasts)")
            note = "G1; 8 donors"
        elif kind == "pctoa":
            groups = [("OA", g2.loc[g2.clinical_group == "OA", "pct"].values),
                      ("Ctrl", g2.loc[g2.clinical_group == "non-arthritic control", "pct"].values)]
            draw_donor_box(ax, groups, {"OA": BRICK, "Ctrl": TEAL},
                           50, "NR-FB core (% fibroblasts)")
            note = "G2; 25 OA / 3 control"
        elif kind == "fit":
            ylim = 30 if arg == "G1" else 40
            rho, p, n = draw_fit(ax, g1 if arg == "G1" else g2, ylim,
                                 "NR-FB core (% fibroblasts)")
            # v5：补一行灰色副注，让 E / M 的标题块与同排其它格同高
            note = f"{arg}; {n} donors with PPSD score"
            stat_rows.append(dict(panel=letter, source=src + "-" + src_panel,
                                  group=arg, rho=rho, P=p, n=n))
            extra = dict(rho=rho, P=p, n=n)
        elif kind == "dot":
            draw_marker_dot(ax)
            note = ""
        elif kind == "pcdh9":
            draw_pcdh9_by_state(ax)
            note = ""
        elif kind == "corepc":
            draw_core_pcdh9(ax)
            note = "2 control / 5 OA donors"
        elif kind == "tissue":
            td = draw_tissue_box(ax, narrow=True)
            # v5：补一行灰色副注，让 T 的标题块与同排其它格同高
            n_men = int((td.tissue == "meniscus").sum())
            n_lig = int((td.tissue == "ligament").sum())
            note = f"{n_men} meniscus / {n_lig} ligament samples"
            extra = dict(n_donors=int(len(td)))

        clip_xticks(ax)
        tag(tag_ax, letter, title, w, note=note or None)
        panel_rows.append(dict(letter=letter, row=row + 1,
                               source_plate=src, source_panel=src_panel,
                               title=title, draw_kind=kind, data_key=arg,
                               note=note,
                               x_mm=round(x, 2), y_mm=round(ytop, 2),
                               w_mm=round(w, 2), h_mm=ROW_H,
                               **extra))

    J.footer(fig, FOOTER, size=5.8, linespacing=1.35)

    problems = J.check_layout(fig)
    print(f"check_layout: {len(problems)} problems")
    for p in problems[:30]:
        print("   -", p)
    if problems:
        fig.set_dpi(300)
        fig.canvas.draw()
        r = fig.canvas.get_renderer()
        fw, fh = fig.bbox.width, fig.bbox.height
        for ax in fig.axes:
            for t in list(ax.get_xticklabels()) + list(ax.get_yticklabels()) + \
                     [ax.xaxis.label, ax.yaxis.label]:
                s = t.get_text()
                if not s or not s.strip():
                    continue
                bb = t.get_window_extent(renderer=r)
                if bb.x0 / fw < 0.001 or bb.x1 / fw > 0.999:
                    print(f"   BOUND {s[:22]!r} ax={[round(v, 4) for v in ax.get_position().bounds]} "
                          f"x=[{bb.x0/fw:.3f},{bb.x1/fw:.3f}]")
        fig.set_dpi(100)
        raise SystemExit("版式体检未通过，未导出（修正后重跑）")

    fig.savefig(OUT_PNG, dpi=600, facecolor="white")
    fig.savefig(OUT_PDF, facecolor="white")
    plt.close(fig)

    with Image.open(OUT_PNG) as im:
        px = im.size
    md5 = hashlib.md5(OUT_PNG.read_bytes()).hexdigest()
    print(f"saved {OUT_PNG.name}  {px[0]} x {px[1]} px  md5={md5}")
    print(f"saved {OUT_PDF.name}")

    with open(OUT_MAP, "w", encoding="utf-8-sig", newline="") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(["new_letter", "row", "source_plate", "source_panel",
                       "title", "draw_kind", "data_key"])
        for r in PANEL_MAP:
            # CSV 的 row 用 1 基，与 meta 的 panel_rows、页面「第 1–4 行」一致
            wcsv.writerow((r[0], r[1] + 1, *r[2:]))
    print("saved", OUT_MAP.name)

    # v8：把统一状态字典落成一张可编辑的映射表，方便后期改名 / 改色后重绘
    counts = {}
    for key in ("G1", "G2", "M2", "L2"):
        counts[key] = obs(key)["state"].value_counts().to_dict()
    with open(OUT_STATES, "w", encoding="utf-8-sig", newline="") as f:
        wcsv = csv.writer(f)
        wcsv.writerow(["state_raw", "display_name", "color", "family",
                       "present_in", "n_G1", "n_G2", "n_M2", "n_L2",
                       "scope", "note"])
        for st in UNIFIED_ORDER:
            present = [k for k in ("G1", "G2", "M2", "L2") if counts[k].get(st, 0)]
            if st in G1G2_ONLY:
                scope, note = "synovium only", "source synovial label kept"
            elif st in M2L2_ONLY:
                scope, note = ("meniscus / ligament only",
                               "display name normalised; cluster NOT merged "
                               "and NOT declared equivalent to any synovial state")
            else:
                scope, note = "shared", "identical name and colour in all four UMAPs"
            wcsv.writerow([st, display_name(st), color_of(st),
                           STATE_FAMILY.get(st, ""), "+".join(present),
                           *(counts[k].get(st, 0) for k in ("G1", "G2", "M2", "L2")),
                           scope, note])
    print("saved", OUT_STATES.name)

    meta = dict(
        id="F3_P08", version="v9", stem="F3_P08_four_rows_A-T_v9",
        png="outputs/F3_P08_four_rows_A-T_v9.png",
        pdf="outputs/F3_P08_four_rows_A-T_v9.pdf",
        width_mm=PW, height_mm=PH, dpi=600,
        width_px=px[0], height_px=px[1], png_md5=md5,
        n_panels=len(PANEL_MAP), rows=4,
        row_structure=[5, 3, 5, 5],
        letters="".join(r[0] for r in PANEL_MAP),
        removed_from_v3=["P", "S"],
        umap_legend="single column in a 22 mm right-side gutter for A, I, N and Q",
        umap_outline=dict(
            method="Gaussian KDE density contour of NR-FB core UMAP coordinates at "
                   "the 5th percentile of core-cell density (Scott bandwidth x 0.75, "
                   "200 x 200 grid, largest closed loop); restores the source plate's "
                   "edge-tracing outline, replacing the v6 convex-hull / spline "
                   "contour and the v5 2-sigma covariance ellipse",
            source_method="E:/NRFB_atlas_plate_20261104/sources/figure3/scripts/"
                          "unified_annotation.py :: boundary(); rebuild.py note: "
                          "'KDE boundary uses the 5th percentile density, enclosing "
                          "approximately 95% of core cells'",
            quantile=KDE_QUANTILE, bw_factor=KDE_BW_FACTOR, grid=KDE_GRID,
            line_style="J.INK, lw 0.9, dash (0,(4,3)) — source-plate dash pattern",
            panels=OUTLINE_STATS, v5_ellipse_comparison=ELLIPSE_V5_STATS,
            caveat="descriptive density-edge annotation covering about 95% of core "
                   "cells; not a confidence region, not a cluster boundary, not a "
                   "statistical region; purity is not classification accuracy"),
        alignment_fix=dict(
            issue="E, M and T had no grey note line, so J.tag's bottom-anchored title "
                  "block was about 2.9 mm lower than the other panels in the same row; "
                  "T also had its disease/Ctrl legend hanging 6 mm below the axes",
            fix="one grey note line added to E, M and T; T legend moved into the empty "
                "top of its axes; no axis x/y/w/h changed",
            measured_v4_title_top_mm=dict(D=17.95, E=20.45, L=127.93, M=130.47),
            axis_frames="unchanged and already aligned in v4 (same-row bottom spines "
                        "at y=62, 172, 222 mm)",
        ),
        redrawn_from_data=True, cropped_panels=0,
        fidelity="v3 restoration of panel types, palette, axis labels, state names and "
                 "annotations kept; v4 removes P/S and moves the UMAP state legends right; "
                 "v5 aligns the E/M/T title blocks and the bottom margin of T; "
                 "v6 replaces the four UMAP 2-sigma ellipses with convex-hull "
                 "outer contours; v7 replaces those with the source-plate KDE "
                 "density-edge contour (an irregular tracing of the core cell "
                 "edge), all other panels unchanged; v8 harmonises state display "
                 "names, removes the six grey shades assigned to M2/L2-specific "
                 "states, gives every state one shared colour and one shared "
                 "legend order across the four UMAPs, without merging clusters; "
                 "v9 reverses the y-axis order of the six per-state ranking "
                 "panels (B, C, J, K, O and R) so that NR-FB core sits "
                 "first, leaving D, L and T (grouped boxes) and the four "
                 "UMAP legends unchanged",
        state_harmonisation=dict(
            csv="F3_P08_状态统一表_v9.csv",
            method="one shared dictionary: state_raw -> (display_name, colour, "
                   "order); replaces the source 08_addon_M2_L2.py grey ramp "
                   "GREY_NEW and the STATE_ORDER + ORDER_ALT concatenation",
            legend_order=UNIFIED_ORDER,
            display_names=DISPLAY_NAME,
            colors=STATE_COLOR,
            families=STATE_FAMILY,
            shared_states=["Sublining", "Remodeling", "AP-1 stress",
                           "Proliferating", "NR-FB core"],
            synovium_only=G1G2_ONLY,
            meniscus_ligament_only=M2L2_ONLY,
            grey_states_removed=["Lining-1", "Lining-2", "Lining-3", "MHCII",
                                 "Myofibroblast", "NR-FB gradient",
                                 "Inflammatory", "Proliferating"],
            caveat="display-layer harmonisation only: clusters were not merged "
                   "or re-clustered; M2/L2 lining clusters were not relabelled "
                   "as biological equivalents of the synovial PRG4+ lining "
                   "state; the two atlas families were annotated independently. "
                   "A shared colour never implies state equivalence."),
        box_panel_order=dict(
            panels=["B", "C", "J", "K", "O", "R"],
            top_state="NR-FB core",
            order=BOX_ORDER,
            unchanged_panels=["D", "L", "T"],
            note="y-axis order only: NR-FB core first, the rest reversed against the v8 unified order; numbers, colours and display names unchanged; the four UMAP legends keep the functional-family order",
        ),
        header=dict(zip(("number", "title", "subtitle"), HEADER)),
        footer=FOOTER,
        panel_map=panel_rows, correlations=stat_rows,
    )
    OUT_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print("saved", OUT_META.name)

    if stat_rows:
        print("\n=== 相关面板（由源表实时重算） ===")
        for r in stat_rows:
            print(f"  {r['panel']} {r['source']:<12} rho={r['rho']:.4f} "
                  f"P={r['P']:.5g} n={r['n']}")


if __name__ == "__main__":
    main()
