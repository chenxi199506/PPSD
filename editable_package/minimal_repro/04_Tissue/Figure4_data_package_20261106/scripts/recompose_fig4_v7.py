#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 4, v7 (2026-11-03): v6 + y titles on H/I + per-panel markers.

Three changes over v5, all requested by the user in one message:

1. Row 3 (G-I) confidence bands are now brick red instead of light grey, so
   they read as the same object as Figure 3 M-O / Figure S1 D-F, which draw
   `fill_between(color=BRICK, alpha=0.20)` from the identical ten-donor table.
2. One tick size (6.4 pt) for all nine panels. v5 used 5.9 / 6.0 / 6.4 depending
   on label length, which is visible as "字号不统一" when A/D/G sit in a column.
3. All three rows are 36 mm tall and every column shares one label gutter, so
   A/D/G, B/E/H and C/F/I are identical rectangles and the three y spines in a
   column land on one vertical line. 3 x 36 = 37 + 32 + 39, so the page height
   is unchanged from v5 (180 x 168.7 mm).

Everything below the layout block is v5, i.e. the 2026-11-01 three-row plate
with the 2026-11-03 protein third row. Original v5 header follows.

Figure 4, third recomposition (2026-11-01, user request: shorter plate).

Three rows, nine panels, letters A-I in reading order, no plate header
(no figure title, no subtitle), panel sentence titles dropped -- only the
letter and, where a number is not already printed inside the panel, one
grey statistic line. This matches the typography pass already applied to
Figure 3 (`fig3_retitle.py` + `recompose_fig3.py`).

Row 1: A <- old Figure 4 panel D   which compartment shifts in OA
       B <- old Figure 4 panel C   NR-FB transcript contribution
       C <- old Figure 4 panel B   within-cohort CORE20 forest
Row 2: D <- old Figure 4 panel E   PCDH9 vs continuous pain
       E <- old Figure 4 panel F   PCDH9 across three diagnostic groups
       F <- old Figure 4 panel G   per-cohort PCDH9 delta
Row 3: G <- Figure 6 panel A       FinnGen R12 rs1413573 endpoints
       H <- Figure 6 panel B       pain-pleiotropy regional association
       I <- Figure 6 panel H       tissue-specific IVW (GTEx proxies)

Old Figure 4 panel A (CORE20 score by disease group) is not carried over:
the request named panels D C B for row 1.

Every plotted value is read from the same source tables the originals used;
no number is recomputed other than the S6 IVW estimates, which are re-derived
from the archived harmonised instruments exactly as `add_s6_column.py` does.
Axis limits, colours and estiimates are otherwise unchanged.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "journal"))
import journal_style as J  # noqa: E402

# v5：第三行换成 Figure S1 的 D–F（10 例配对样本的 PCDH9 蛋白），
# 数据与统计必须与 Figure 3 的 M–O、Figure S1 的 D–F 完全同源。
# 本机用项目外的原始目录；服务器回落到随项目分发的 _external/ 副本。
_MAC_EDIT = Path("ppsd_workspace/figure_audit/editable")
EDIT = str(_MAC_EDIT if (_MAC_EDIT / "data.py").is_file()
           else HERE.parent / "_external/figure_audit/editable")
if not (Path(EDIT) / "data.py").is_file():
    raise SystemExit(f"[F] 找不到 figure_audit/editable（data.py）：{EDIT}")
sys.path.insert(0, EDIT)
import data as D  # noqa: E402
import stats as ST  # noqa: E402
from scipy import stats as SS  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import Polygon  # noqa: E402
from matplotlib.textpath import TextPath, TextToPath  # noqa: E402

plt.rcParams.update({
    "mathtext.fontset": "custom",
    "mathtext.rm": "Arial",
    "mathtext.it": "Arial:italic",
    "mathtext.bf": "Arial:bold",
    "mathtext.cal": "Arial",
    "mathtext.sf": "Arial",
    "mathtext.tt": "Arial",
})

# ------------------------------------------------------------------ paths ----
PROJ = HERE.parents[1]
# 服务器上没有图册项目的父级目录，外部兄弟目录回落到项目的 _external/
if not (PROJ / "GSE99662_W28_W29_重绘_20261019").is_dir():
    PROJ = HERE.parent / "_external"
SRC = PROJ / "GSE99662_W28_W29_重绘_20261019" / "source"
F7 = HERE.parent / "sources" / "bulk_own_cohort_20261028" / "Figure7" / "data"
OUT = HERE.parent
F6 = PROJ / "PCDH9_integrated_reproduction_20261024"
F6_T = F6 / "tables"
F6_G = F6 / "gwas_reproduced" / "tables"
F6_MR = F6 / "source" / "53_图版_顶刊交付_20261024" / "mr_independent_summary.json"

STEM = "Figure4_NRFB_OA_PCDH9_three_rows_v7"

# ------------------------------------------------------------------ load -----
eff = pd.read_csv(SRC / "within_cohort_effects.csv")
eff = eff[eff["module"] == "CORE20"].sort_values("hedges_g").reset_index(drop=True)
meta = pd.read_csv(SRC / "random_effects_meta.csv")
meta = meta[(meta["scope"] == "all_mixed_cohorts") & (meta["module"] == "CORE20")].iloc[0]

frac = pd.read_csv(SRC / "deconv_v2/T30_deconv_donor_fractions.csv")
frac = frac[frac["method"] == "svr"]
dmeta = pd.read_csv(SRC / "deconv_v2/T32_deconv_meta.csv")
dmeta = dmeta[(dmeta["method"] == "svr") &
              (dmeta["metric"] == "NR-FB fraction difference")].iloc[0]
states = pd.read_csv(SRC / "deconv_v2/T38_state_diff_cohort_adjusted.csv").sort_values(
    "diff", ascending=False).reset_index(drop=True)

pain = pd.read_csv(F7 / "Fig7B_painscore_samplelevel.tsv", sep="\t")
poolz = pd.read_csv(F7 / "Fig7DE_pooled_z_samplelevel.tsv", sep="\t")
deltas = pd.read_csv(F7 / "Fig7E_cohort_deltas.tsv", sep="\t")
stats = pd.read_csv(F7 / "Fig7_summary_stats.tsv", sep="\t")

endpoints = pd.read_csv(F6_G / "10_selected_forest_source.csv")
region = pd.read_csv(F6_G / "05_Mocci_region_plot_source.tsv", sep="\t")


def sv(panel, quantity):
    return stats.loc[(stats["panel"] == panel) &
                     (stats["quantity"] == quantity), "value"].iloc[0]


def fmt_p(p):
    if p < 1e-3:
        exp = int(np.floor(np.log10(p)))
        return rf"P = {p / 10 ** exp:.1f} × $10^{{{exp}}}$"
    return f"P = {p:.3f}"


# ---- tissue MR: same arithmetic as add_s6_column.recalculate(), no file writes
SHORT = {"Adipose_Subcutaneous": "Adipose subcut.", "Artery_Aorta": "Artery aorta",
         "Artery_Tibial": "Artery tibial",
         "Cells_Cultured_fibroblasts": "Fibroblasts",
         "Colon_Sigmoid": "Colon sigmoid", "Heart_Left_Ventricle": "Heart LV",
         "Lung": "Lung", "Muscle_Skeletal": "Muscle skeletal",
         "Nerve_Tibial": "Nerve tibial",
         "Skin_Not_Sun_Exposed_Suprapubic": "Skin not sun-exp.",
         "Skin_Sun_Exposed_Lower_leg": "Skin lower leg", "Stomach": "Stomach",
         "Testis": "Testis", "Thyroid": "Thyroid", "Prostate": "Prostate"}


def mr_table() -> pd.DataFrame:
    data = json.loads(F6_MR.read_text())
    rows = []
    for key, v in data.items():
        if not key.startswith("oa_") or key.endswith("_pooled"):
            continue
        tissue = key[3:]
        ins = pd.DataFrame(v["instruments"])
        x, y = ins.beta_gx.to_numpy(), ins.beta_gy.to_numpy()
        sx, sy = ins.se_gx.to_numpy(), ins.se_gy.to_numpy()
        theta = y / x
        var = sy ** 2 / x ** 2 + y ** 2 * sx ** 2 / x ** 4
        w = 1 / var
        b = np.sum(w * theta) / w.sum()
        se = 1 / np.sqrt(w.sum())
        p = 2 * float(__import__("scipy.stats", fromlist=["stats"]).norm.sf(abs(b / se)))
        # the archived per-tissue IVW must be reproduced, not approximated
        assert abs(b - v["ivw_fe"]["beta"]) < 1e-10, tissue
        rows.append(dict(tissue=tissue, short=SHORT.get(tissue, tissue),
                         k=len(x), b=b, se=se, p=p))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ style ----
# v6（2026-11-03，用户要求「字体大小和前面的六张图统一」）：九个面板共用同一个
# 刻度字号，不再按标签长短分档。v5 里 A/C/F 被压到 5.9/6.0 是为了把标签栏压进
# 四分之一画幅，代价是同一幅图里出现 5.9 / 6.0 / 6.4 三种刻度字号——一列并排看
# 就是「大小不一致」。现在统一到 rcParams 默认的 6.4 pt，靠列内共享标签栏
# （见下面 GUTCOL）来吸收长标签多出来的宽度。
TICK_FS = 6.4
TICK = {L: TICK_FS for L in "ABCDEFGHI"}

# Third pass (2026-11-01, second request): nothing is written above a panel any
# more. The three-line letter-plus-statistics stack that used to sit there made
# the plate 224 mm tall and left the letters at uneven heights whenever a note
# wrapped to a different number of lines. Every statement that used to live in
# those grey lines now lives in the figure legend instead (see
# `apply_fig4_three_rows.py`, panel table C and F, where the pooled g, I2 and
# the weighted delta were added for that reason). Only the bold letter remains.
NOTE = {L: "" for L in "ABCDEFGHI"}

STATE_SHORT = {"Transitional activated": "Transitional",
               "COMP+ transitional": "COMP+ trans.",
               "DKK3+ intermediate": "DKK3+ interm.",
               "Proliferating": "Prolif."}

FOOTER = (
    "Analysis unit: the donor in A and B, the sample in D and E, and the ten "
    "paired explants in G-I; C and F are cohort-level meta-analyses over 8 and 7 "
    "estimates, and cohort labels give n as control/OA. Method: CORE20 and PCDH9 "
    "are z-scored within cohort; deconvolution is reference-guided \u03bd-SVR on bulk "
    "mRNA, so fractions are transcript contributions, not cell counts; the bracket "
    "in B is the cohort-level meta. Row 3 is the same ten-donor table as Figure 3 "
    "M-O (Figure S1 D-F), redrawn here: apparent PCDH9 protein against the paired "
    "transcript, against the fixed 12-gene NR-FB score and against WOMAC pain; the "
    "band is the 95% confidence band of the least-squares fit (t distribution, "
    "df = 8), and H is not an independent repeat of G because both read one "
    "transcriptome. This figure does not support a rise in NR-FB cell number, and "
    "does not show that PCDH9 causes pain: the clinical contrasts are "
    "cross-sectional, E compares diagnostic labels rather than pain states within "
    "OA, and the pain association in I is cross-sectional and rests on ten explants."
)


# --------------------------------------------------------------- primitives --
def box(ax, groups, labels, colors, width=0.52, ptsize=4.2):
    bp = ax.boxplot(groups, widths=width, patch_artist=True, showfliers=False,
                    medianprops=dict(color=J.INK, lw=0.9),
                    whiskerprops=dict(color=J.RULE, lw=0.6),
                    capprops=dict(color=J.RULE, lw=0.6),
                    boxprops=dict(lw=0.6))
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor("white")
        patch.set_edgecolor(c)
    rng = np.random.default_rng(11)
    for i, (g, c) in enumerate(zip(groups, colors), start=1):
        bp["medians"][i - 1].set_color(c)
        ax.scatter(i + rng.uniform(-0.16, 0.16, len(g)), g, color=c,
                   s=ptsize, alpha=0.55, linewidths=0, zorder=3)
    ax.set_xticks(range(1, len(labels) + 1))
    ax.set_xticklabels(labels)
    ax.set_xlim(0.45, len(labels) + 0.55)


def forest(ax, labels, est, lo, hi, color, diamond=None, label_size=6.0,
           point_size=10, xlabel="", xlim=None, xticks=None):
    n = len(est)
    y = np.arange(n, 0, -1)
    ax.axvline(0, color=J.HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=0)
    ax.hlines(y, lo, hi, color=color, lw=0.9, alpha=0.5, zorder=2)
    ax.scatter(est, y, s=point_size, color=color, zorder=4, linewidths=0)
    ticks, ticklab = list(y), list(labels)
    bottom = -0.30
    if diamond is not None:
        d_est, d_lo, d_hi = diamond
        ax.add_patch(Polygon([[d_lo, bottom], [d_est, bottom + 0.30],
                              [d_hi, bottom], [d_est, bottom - 0.30]],
                             closed=True, facecolor=J.INK, edgecolor="none", zorder=5))
        ticks.append(bottom)
        ticklab.append("Overall")
        ax.set_ylim(bottom - 0.95, n + 0.55)
    else:
        ax.set_ylim(0.35, n + 0.65)
    ax.set_yticks(ticks)
    ax.set_yticklabels(ticklab)
    ax.set_xlim(xlim if xlim is not None else (min(lo) - 0.3, max(hi) + 0.3))
    if xticks is not None:
        ax.set_xticks(xticks)
    ax.set_xlabel(xlabel, labelpad=1.6)
    J.style_axis(ax, labelpad=1.6)
    ax.tick_params(axis="y", length=0, labelsize=label_size, pad=2.0)


# ------------------------------------------------------------------ layout ---
W = J.W2
GAPX = 9.0        # horizontal gap between panel blocks, mm
LMARGIN = 1.6     # keeps the first column's letters off the trim line
RMARGIN = 3.0
TOP_PAD = 1.2     # v4：压扁后首行字母更贴裁切线
XLABEL_H = 6.6
GAP_ROW = 2.4     # v4：行间再收 0.6 mm
TAG_LIFT = 4.4    # v4：字母离面板顶再近 0.6 mm
GAP_LETTER = 3.6  # gap_mm handed to journal_style.tag; tag adds 0.9 mm of leading
                  # so that 4.1 + 0.9 = TAG_LIFT and the letter clears the panel by 1.8 mm

# Row heights: 42 / 36 / 44 mm instead of 48 / 42 / 50, which is what brings the
# plate from 224 mm down to a near-square 180 x 185 mm.
#
# v6（2026-11-03）：三行统一 36 mm。v5 是 37 / 32 / 39，同一个画幅里九张面板
# 物理尺寸不等，第三行明显比第二行"大一号"，并排读起来像两组图。三行改等高的
# 好处是 3 x 36 = 108 = 37 + 32 + 39，**画幅总高一分不变**（168.7 mm），页脚位置
# 也不用重算；同时 A/D/G、B/E/H、C/F/I 各自成为完全相同的矩形，九宫格才真正成立。
ROW_H_MM = 36.0

ROWS = [
    dict(h=ROW_H_MM, weight={"A": .36, "B": .25, "C": .39}),
    dict(h=ROW_H_MM, weight={"D": .40, "E": .28, "F": .32}),
    dict(h=ROW_H_MM, weight={"G": .36, "H": .32, "I": .32}),
]

# label gutters are measured against the real rendered strings, not guessed
LABELS = {
    "A": [STATE_SHORT.get(s, s) for s in states.state],
    "B": ["Control", "OA"],
    "C": [f"{r.cohort_id} ({r.n_Normal}/{r.n_OA})" for r in eff.itertuples()] + ["Overall"],
    "D": ["0", "2", "4", "6"],
    "E": ["Control", "OA+pain", "RA"],
    "F": [f"{r.cohort} ({r.n_control}/{r.n_OA_pain})" for r in deltas.itertuples()] + ["Overall"],
    # v6：G/H/I 原来填的是 x 轴标签（"0.0..2.0" / "−1.5..1.0" / "8..20"），
    # 但 gutter() 要的是**纵轴**（蛋白 fmol/µg，0.0/0.4/0.8/1.2/1.6）。填错后
    # H 的标签栏被 "−1.5" 高估约 1.9 mm、I 的 "12" 又低估约 0.7 mm，只是碰巧没
    # 裁到字。现在填真值。
    "G": ["0.0", "0.4", "0.8", "1.2", "1.6"],
    "H": ["0.0", "0.4", "0.8", "1.2", "1.6"],
    "I": ["0.0", "0.4", "0.8", "1.2", "1.6"],
}
# v7（2026-11-03，用户：「H 和 I 的纵坐标怎么没有标题了？」）：v5/v6 只给 G 挂了
# 纵轴标题，H、I 靠 `show_ylabel=False` 省掉，理由是三个面板共用同一个纵轴量。
# 但九面板并排时，第二、三列各自缺一条轴标题就只剩刻度数字，读者要先回头找 G
# 才知道单位。现在三张都画，并同时进 YLABEL —— gutter() 用它决定列宽里要不要
# 预留标题的位置，漏了就会被裁。
YLABEL = {"B": "NR-FB transcript contribution (%)", "D": "PCDH9 (log2 CPM)",
          "E": "PCDH9 (within-cohort z)", "G": "Apparent PCDH9 (fmol/µg)",
          "H": "Apparent PCDH9 (fmol/µg)", "I": "Apparent PCDH9 (fmol/µg)"}


_mr = mr_table()


def gutter(letter: str) -> float:
    """Left margin an axes needs: longest tick label, then the rotated y title.

    Both are measured with Arial glyph outlines at the exact size that will be
    drawn, because a guessed gutter is what clipped panel D's y title on the
    first pass.
    """
    widest = max(J.measure_mm(None, t, TICK[letter]) for t in LABELS[letter])
    pad = 2.0 + 2.4 + 1.0          # tick pad + tick mark + hairline clearance
    if letter in YLABEL:
        pad += J.measure_mm(None, "Mg", 7.0) + 1.6   # rotated title + labelpad
    return widest + pad


GUT = {L: gutter(L) for L in "ABCDEFGHI"}

# ---------------------------------------------------------------- column grid
# Until now each row distributed its own free width, so the three rows started
# their panels at different x (18.7 / 11.2 / 25.0 mm for the first column) and
# the letters, pinned to each panel's y spine, looked scattered even though
# their vertical positions were identical to the micron.
#
# The three rows are now snapped onto one grid of three columns: a column is as
# wide as its widest (gutter + axes) pair across the rows, and the letters are
# drawn at the column's left edge rather than at the spine. A/D/G, B/E/H and
# C/F/I therefore each form a straight vertical line down the plate.
#
# v6（2026-11-03，用户要求「彼此的 y 轴位置可以对齐」）：标签栏（gutter）也从
# "每张图自己算" 改成 "每列共享最宽的那个"。v5 的 y 轴 x 是 COLX + GUT[L]，而
# GUT 逐面板不同（A 的状态名长、D 的只有一位数字、G 的是 0.0/0.4），于是同一列
# 里 A / D / G 的三条 y 轴各在 x = 30.4 / 20.9 / 22.6 mm，肉眼就是一列歪的轴。
# 现在一列只留一个标签栏宽度（取该列最宽者，否则会被裁字），三条 y 轴落在同一
# 条竖线上，且列内三张图宽度完全相同——代价是 D / G 左侧各让出几毫米空档，这
# 正是"对齐"必然要付的价钱。
NCOL = 3

col_letters = [[list(r["weight"])[_c] for r in ROWS] for _c in range(NCOL)]
GUTCOL = [max(GUT[L] for L in col) for col in col_letters]

# 标签栏是列级量之后，每行的可用绘图宽度都相同，权重只决定列与列的相对宽窄
FREE = W - LMARGIN - sum(GUTCOL) - GAPX * (NCOL - 1) - RMARGIN

# ---- 列宽必须能装下自己那一列的 x 轴刻度（v6 新增）----------------------
# 共享标签栏会把绘图区压窄：H 列的标签栏被 B/E 拉宽到 18.7 mm 后，绘图区只剩
# 27.3 mm，而 "−1.5 −1.0 −0.5 0.0 0.5 1.0" 六个 6.4 pt 标签实测要 38.6 mm，
# 于是首轮渲染出现 "−1.5−1.0−0.5" 挤成一串（实测缝 0.23 mm）。所以列宽不能只
# 按权重分，必须先在**实测**的最小宽度上封底，再分配余额——这是唯一能同时做到
# 「字号统一」和「y 轴对齐」而不撞标签的次序。
#
# 宽度需求按**相邻标签对**算，不按标签总宽：居中定位下，两个宽标签相撞只看
# 它们自己的宽度和刻度间距。用 advance 宽度（TextToPath）而不是字形墨迹外框，
# 否则会低估约 10%（墨迹不含左右轴承），第一版就是这么把 H 算窄的。
def _sk(v) -> str:
    return ("%g" % v).replace("-", "\u2212")


_TP = TextToPath()


def adv_mm(s: str, size: float = TICK_FS) -> float:
    """字符串的 advance 宽度（mm）——排版真正占的宽度，不是墨迹外框。"""
    w = _TP.get_text_width_height_descent(
        s, FontProperties(size=size), False)[0]
    return w * 0.3528          # pt -> mm


# (xlim, tick 数值, tick 文字)：必须与下面各面板实际的 set_xlim / set_xticks 一致
XSPEC = {
    "A": ((-7.4, 6.4), (-5, 0, 5), None),
    "B": ((0.45, 2.55), (1, 2), ["Control", "OA"]),
    "C": ((-1.7, 5.5), (-1, 0, 1, 2, 3, 4, 5), None),
    "D": ((-2.0, 84.0), (0, 20, 40, 60, 80), None),
    "E": ((0.45, 3.55), (1, 2, 3), ["Control", "OA+pain", "RA"]),
    "F": ((-1.75, 2.45), (-1, 0, 1, 2), None),
    "G": ((0.0, 2.25), (0, 0.5, 1.0, 1.5, 2.0), ["%.1f" % v for v in (0, .5, 1, 1.5, 2)]),
    "H": ((-1.75, 1.75), (-1.5, -0.5, 0.5, 1.5), ["%.1f" % v for v in (-1.5, -.5, .5, 1.5)]),
    "I": ((5.0, 21.0), (8, 12, 16, 20), None),
}

XGAP = 1.6      # 相邻两个 x 刻度标签之间至少留的气（mm）
XPAD = 2.0      # 两端各留的气（mm）


def xneed(letter: str) -> float:
    (lo, hi), ticks, labs = XSPEC[letter]
    labs = labs or [_sk(v) for v in ticks]
    ws = [adv_mm(s) for s in labs]
    span = hi - lo
    need = 0.0
    for i in range(len(ticks) - 1):
        d = ticks[i + 1] - ticks[i]
        need = max(need, (0.5 * (ws[i] + ws[i + 1]) + XGAP) * span / d)
    # 不再约束"首末标签必须落在坐标区内"：标签居中定位时探出左/右边框是常态，
    # 探出去的那半毫米落在标签栏或列间空档里，不会撞任何东西。硬按"首刻度到
    # 边框的距离 ≥ 半个字宽"来算，D 的首刻度离左边框只有 2/86 个数据单位，
    # 会算出 113 mm 这种荒唐值（第一版就是这么把画幅撑到 250 mm 的）。
    return need


XMIN = {L: xneed(L) for L in "ABCDEFGHI"}
COLMIN = [max(XMIN[L] for L in col) for col in col_letters]

# 目标宽度按"该列最大行权重"分配，再做水位填充：低于实测下限的列先钉在下限上，
# 被它挤掉的差额按目标宽度比例从其余列扣回，迭代到稳定。
_W_OF = {L: w for r in ROWS for L, w in r["weight"].items()}
_share = [max(_W_OF[L] for L in col_letters[c]) for c in range(NCOL)]
_tgt = [FREE * v / sum(_share) for v in _share]
COLW = list(_tgt)
for _ in range(6):
    fixed = [c for c in range(NCOL) if COLMIN[c] > COLW[c] - 1e-9]
    if not fixed:
        break
    rest = FREE - sum(COLMIN[c] for c in fixed)
    free_c = [c for c in range(NCOL) if c not in fixed]
    if not free_c:
        COLW = list(COLMIN)
        break
    tot_t = sum(_tgt[c] for c in free_c)
    new = list(COLW)
    for c in fixed:
        new[c] = COLMIN[c]
    for c in free_c:
        new[c] = rest * _tgt[c] / tot_t
    if all(abs(new[c] - COLW[c]) < 1e-9 for c in range(NCOL)):
        COLW = new
        break
    COLW = new

CELL = [GUTCOL[c] + COLW[c] for c in range(NCOL)]
COLX = [LMARGIN + sum(CELL[:_c]) + GAPX * _c for _c in range(NCOL)]

AXPOS, COLOF = {}, {}
for _i, _row in enumerate(ROWS):
    for _c, L in enumerate(_row["weight"]):
        AXPOS[L] = (COLX[_c] + GUTCOL[_c], CELL[_c] - GUTCOL[_c])
        COLOF[L] = _c

ROW_H = {list(r["weight"])[0]: r["h"] for r in ROWS}

foot_lines = J.wrap_mm(None, FOOTER, W - 4.0, 6.0).count("\n") + 1
FOOTER_H = foot_lines * 6.0 * 1.55 * 0.3528

# Each row now reserves exactly the height of a bare letter above its axes, so
# every letter in a row lands on the same line no matter how narrow its panel is.
def note_block_h(letter: str) -> float:
    return 0.0


ROW_LBL, ROW_NOTE, ROW_OF = {}, {}, {}
for _r in ROWS:
    _key = list(_r["weight"])[0]
    for _L in _r["weight"]:
        ROW_OF[_L] = _key
    ROW_NOTE[_key] = 0.0
    ROW_LBL[_key] = TAG_LIFT

# Row gap is spent *between* rows only, so the top row's letters start at TOP_PAD
# rather than at TOP_PAD + gap.
H = (TOP_PAD
     + sum(ROW_LBL[list(r["weight"])[0]] + r["h"] + XLABEL_H for r in ROWS)
     + GAP_ROW * (len(ROWS) - 1)
     + FOOTER_H + 2.0)

row_y = {}
y = FOOTER_H + 2.0
for _i, r in enumerate(reversed(ROWS)):
    if _i:
        y += GAP_ROW
    y += XLABEL_H + r["h"]
    key = list(r["weight"])[0]
    row_y[key] = y - r["h"]
    y += ROW_LBL[key]

print(f"plate {W:.0f} x {H:.1f} mm | footer {foot_lines} lines")
print("x-tick need  " + "  ".join(f"{L}={XMIN[L]:.1f}" for L in "ABCDEFGHI"))
print("col min/act  " + "  ".join(f"c{c}: {COLMIN[c]:.1f} -> {COLW[c]:.1f}"
                                 for c in range(NCOL)))
print("columns at  " + "  ".join(f"c{c}={COLX[c]:.1f}" for c in range(NCOL))
      + "  widths " + "  ".join(f"{CELL[c]:.1f}" for c in range(NCOL)))
for L in "ABCDEFGHI":
    print(f"  {L}: letter x={COLX[COLOF[L]]:6.1f}  axes x={AXPOS[L][0]:6.1f} "
          f"w={AXPOS[L][1]:5.1f} gutter={GUTCOL[COLOF[L]]:5.1f}")


def rect(letter, rowkey):
    x, w = AXPOS[letter]
    for r in ROWS:
        if rowkey in r["weight"]:
            return [x / W, row_y[rowkey] / H, w / W, r["h"] / H]
    raise KeyError(rowkey)


fig = J.plate(W, H)
aA = fig.add_axes(rect("A", "A"))
aB = fig.add_axes(rect("B", "A"))
aC = fig.add_axes(rect("C", "A"))
aD = fig.add_axes(rect("D", "D"))
aE = fig.add_axes(rect("E", "D"))
aF = fig.add_axes(rect("F", "D"))
aG = fig.add_axes(rect("G", "G"))
aH = fig.add_axes(rect("H", "G"))
aI = fig.add_axes(rect("I", "G"))


def ax_h_mm(ax):
    return ax.get_position().height * H


# ================================ row 1 =====================================
# A <- old panel D: which compartment shifts in OA
nonfib = {"Macrophage", "T_NK", "B_Plasma", "Endothelial", "Pericyte_SMC", "Mast"}
yD = np.arange(len(states), 0, -1)
aA.axvline(0, color=J.HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=0)
for yy, r in zip(yD, states.itertuples()):
    if r.state == "NR-FB core":
        c, filled = J.ACCENT, True
    elif r.state in nonfib:
        c, filled = J.GRAY, False
    else:
        c, filled = J.GRAY, True
    aA.hlines(yy, r.lo * 100, r.hi * 100, color=c, lw=0.9, alpha=0.5, zorder=2)
    aA.scatter(r.diff * 100, yy, s=11, zorder=4, linewidths=0.7,
               facecolor=c if filled else "white", edgecolor=c)
aA.set_yticks(yD)
aA.set_yticklabels([STATE_SHORT.get(s, s) for s in states.state])
aA.set_ylim(0.35, len(states) + 0.65)
aA.set_xlim(-7.4, 6.4)
aA.set_xticks([-5, 0, 5])
aA.set_xlabel("Difference in transcript contribution (pp)", labelpad=1.6)
J.style_axis(aA, labelpad=1.6)
aA.tick_params(axis="y", length=0, labelsize=TICK["A"], pad=2.0)
for lbl in aA.get_yticklabels():
    if lbl.get_text() == "NR-FB core":
        lbl.set_color(J.ACCENT)
        lbl.set_fontweight("bold")

# B <- old panel C: NR-FB transcript contribution
gC = [frac.loc[frac.condition == "Normal", "NR-FB core"].to_numpy() * 100,
      frac.loc[frac.condition == "OA", "NR-FB core"].to_numpy() * 100]
box(aB, gC, ["Control", "OA"], [J.HEALTHY, J.OA])
aB.set_ylabel("NR-FB transcript contribution (%)")
aB.set_ylim(-1.5, 1.0)
J.style_axis(aB)
lo, hi = aB.get_ylim()
top = max(max(gC[0]), max(gC[1]))
h = ax_h_mm(aB)
aB.set_ylim(lo, lo + (max(top, 0.6) - lo) * h / (h - 6.0))
lo2, hi2 = aB.get_ylim()
yb = (top - lo2) / (hi2 - lo2) + 1.1 / h
leg, gap = 1.1 / h, 0.9 / h
tr = aB.get_xaxis_transform()
aB.plot([1, 1, 2, 2], [yb, yb + leg, yb + leg, yb], color=J.RULE, lw=0.6,
        transform=tr, clip_on=False, solid_capstyle="butt")
aB.text(1.5, yb + leg + gap, fmt_p(float(dmeta.p)), ha="center", va="bottom",
        fontsize=6.2, color=J.INK, transform=tr)

# C <- old panel B: within-cohort CORE20 forest
labC = [f"{r.cohort_id} ({r.n_Normal}/{r.n_OA})" for r in eff.itertuples()]
forest(aC, labC, eff.hedges_g.to_numpy(), eff.ci_low.to_numpy(), eff.ci_high.to_numpy(),
       J.OA, diamond=(meta.g, meta.ci_low, meta.ci_high), point_size=11,
       label_size=TICK["C"], xlabel="Hedges' g (OA − control)",
       xlim=(-1.7, 5.5), xticks=[-1, 0, 1, 2, 3, 4, 5])

# ================================ row 2 =====================================
# D <- old panel E: PCDH9 vs pain score
p1 = pain[pain.cohort.str.startswith("P1")]
p2 = pain[pain.cohort.str.startswith("P2")]
aD.scatter(p1.pain_score, p1.PCDH9_log2cpm, s=7, color=J.OA, alpha=0.75,
           linewidths=0, zorder=3)
aD.scatter(p2.pain_score, p2.PCDH9_log2cpm, s=11, color=J.OA, alpha=0.32,
           linewidths=0, marker="^", zorder=3)
b1, a1 = np.polyfit(pain.pain_score, pain.PCDH9_log2cpm, 1)
xs = np.linspace(pain.pain_score.min(), pain.pain_score.max(), 120)
res = pain.PCDH9_log2cpm - (a1 + b1 * pain.pain_score)
se = np.sqrt((res ** 2).sum() / (len(pain) - 2))
sxx = ((pain.pain_score - pain.pain_score.mean()) ** 2).sum()
band = 1.983 * se * np.sqrt(1 / len(pain) + (xs - pain.pain_score.mean()) ** 2 / sxx)
aD.fill_between(xs, a1 + b1 * xs - band, a1 + b1 * xs + band,
                color=J.LIGHT, alpha=0.8, lw=0, zorder=2)
aD.plot(xs, a1 + b1 * xs, color=J.INK, lw=0.9, zorder=5)
aD.set_xlim(-2, 84)
aD.set_xticks([0, 20, 40, 60, 80])
aD.set_xlabel("Pain score", labelpad=1.6)
aD.set_ylabel("PCDH9 (log2 CPM)")
J.style_axis(aD, labelpad=1.6)

# E <- old panel F: PCDH9 across control / OA+pain / RA
grp = poolz.group.replace({"Arthralgia": "OA+pain", "OA": "OA+pain"})
keep = grp.isin(["Control", "OA+pain", "RA"])
poolz2, grp2 = poolz[keep], grp[keep]
gF = [poolz2.loc[grp2 == k, "z"].to_numpy() for k in ["Control", "OA+pain", "RA"]]
box(aE, gF, ["Control", "OA+pain", "RA"], [J.HEALTHY, J.OA, J.GRAY])
aE.axhline(0, color=J.HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=0)
aE.set_ylabel("PCDH9 (within-cohort z)")
aE.set_ylim(-4.4, 5.8)
aE.set_yticks([-4, -2, 0, 2, 4])
J.style_axis(aE)

pvals = [float(sv("D", "OA+pain vs control, Welch P")),
         float(sv("D", "OA+pain vs RA, Welch P")),
         float(sv("D", "RA vs control, Welch P"))]


def bracket(ax, x1, x2, y_base_frac, label, leg_mm=1.1, gap_mm=0.9, fs=6.2):
    h = ax_h_mm(ax)
    leg, gap = leg_mm / h, gap_mm / h
    tr = ax.get_xaxis_transform()
    ax.plot([x1, x1, x2, x2],
            [y_base_frac, y_base_frac + leg, y_base_frac + leg, y_base_frac],
            color=J.RULE, lw=0.6, transform=tr, clip_on=False, solid_capstyle="butt")
    ax.text((x1 + x2) / 2, y_base_frac + leg + gap, label,
            ha="center", va="bottom", fontsize=fs, color=J.INK, transform=tr)


for (x1, x2), y_base, p in zip([(1, 2), (2, 3)], [0.715, 0.812], pvals[:2]):
    bracket(aE, x1, x2, y_base, fmt_p(p))

# F <- old panel G: per-cohort PCDH9 delta
labG = [f"{r.cohort} ({r.n_control}/{r.n_OA_pain})" for r in deltas.itertuples()]
nums = [float(v) for v in sv("E", "weighted delta [95% CI]")
        .replace("[", " ").replace("]", " ").replace(",", " ").replace("+", " ").split()]
forest(aF, labG, deltas.delta_z.to_numpy(),
       (deltas.delta_z - deltas.ci95).to_numpy(),
       (deltas.delta_z + deltas.ci95).to_numpy(),
       J.OA, diamond=(nums[0], nums[1], nums[2]), label_size=TICK["F"],
       point_size=9, xlabel="Δ PCDH9 (OA − control)",
       xlim=(-1.75, 2.45), xticks=[-1, 0, 1, 2])

# ================================ row 3 =====================================
# v5: G/H/I <- Figure S1 panels D-F. Ten paired explants; apparent PCDH9
# protein against the paired transcript, the fixed 12-gene NR-FB score and
# WOMAC pain. rho and exact P are recomputed from the very table that feeds
# Figure 3 M-O and Figure S1 D-F, so the three plates cannot drift apart.
_d = D.figS1()
_prot = np.array([r["protein"] for r in _d], float)
_XKEY = {"G": "mrna", "H": "nrfb", "I": "pain"}
_X = {k: np.array([r[v] for r in _d], float) for k, v in _XKEY.items()}
RHO = {k: float(ST.spearman(_prot, v)) for k, v in _X.items()}
PVAL = {k: float(ST.exact_spearman_p(_prot, v)) for k, v in _X.items()}
TQ = float(SS.t.ppf(0.975, len(_prot) - 2))     # t(0.975, df = n-2), same band as v23


def protein_panel(ax, letter, xlim, xticks, xlabel, show_ylabel,
                  marker="o", size=9.0, face=None, edge="none", lw=0.0, alpha=0.85):
    x, y = _X[letter], _prot
    k, b = np.polyfit(x, y, 1)
    xpad = 0.03 * (xlim[1] - xlim[0])
    xs = np.linspace(xlim[0] + xpad, xlim[1] - xpad, 120)
    res = y - (b + k * x)
    se = np.sqrt((res ** 2).sum() / (len(x) - 2))
    sxx = ((x - x.mean()) ** 2).sum()
    band = TQ * se * np.sqrt(1.0 / len(x) + (xs - x.mean()) ** 2 / sxx)
    # v6（用户要求「阴影应该是红色」）：置信带由浅灰 J.LIGHT(#E2E2E2) 换成
    # OA 砖红 J.OA(#B4482F) @ 0.20 —— 与 Figure 3 第 4 行 M/N/O 的
    # `fill_between(..., color=BRICK, alpha=0.20)` 逐位同一套配色，三张同源图
    # 摆在一起时阴影不会一种是灰、一种是红。
    ax.fill_between(xs, b + k * xs - band, b + k * xs + band,
                    color=J.OA, alpha=0.20, lw=0, zorder=2)
    ax.plot(xs, b + k * xs, color=J.INK, lw=0.9, zorder=4)
    ax.scatter(x, y, s=size, marker=marker,
               facecolor=(J.OA if face is None else face),
               edgecolor=edge, linewidth=lw, alpha=alpha, zorder=3)
    ax.set_xlim(*xlim)
    ax.set_xticks(xticks)
    ax.set_ylim(0.0, 1.6)
    ax.set_yticks([0, 0.4, 0.8, 1.2, 1.6])
    ax.set_xlabel(xlabel, labelpad=1.6)
    if show_ylabel:
        ax.set_ylabel("Apparent PCDH9 (fmol/\u00b5g)")
    J.style_axis(ax, labelpad=1.6)
    ax.tick_params(axis="y", labelsize=TICK[letter], pad=2.0)
    ax.annotate("\u03c1 = %.2f  \u00b7  P = %.4f" % (RHO[letter], PVAL[letter]),
                xy=(0.04, 0.97), xycoords="axes fraction", ha="left", va="top",
                fontsize=6.2, color=J.GRAY)


# v7：三张各自换一种 marker。形状按面积定，三角/方块看起来比同一 s 的圆小，
# 所以尺寸一起给，免得三个面板的墨量差一截。
MK = {
    "G": dict(marker="o", size=11.0),
    "H": dict(marker="^", size=14.0),
    "I": dict(marker="s", size=11.5),
}

protein_panel(aG, "G", (0.0, 2.25), [0, 0.5, 1.0, 1.5, 2.0],
              r"PCDH9 mRNA ($2^{-\Delta\Delta Ct}$)", True, **MK["G"])
protein_panel(aH, "H", (-1.75, 1.75), [-1.5, -0.5, 0.5, 1.5],
              "NR-FB signature score", True, **MK["H"])
protein_panel(aI, "I", (5.0, 21.0), [8, 12, 16, 20],
              "WOMAC pain (0\u201320)", True, **MK["I"])
print("row3 rho", {k: round(v, 4) for k, v in RHO.items()},
      "p", {k: round(v, 4) for k, v in PVAL.items()})

# ------------------------------------------------------------ letters -------
def ink_left_mm(letter: str, size: float = 9.2) -> float:
    """Left sidebearing of a bold capital, in mm, from its own outline.

    Drawing at the column edge lines up the *advance boxes*, but the ink of an
    "A" starts 0.2 mm to the right of the ink of a "D" because of the diagonal,
    which is exactly the kind of sub-millimetre scatter that still reads as a
    wobble down a column of letters. Subtracting the sidebearing puts the ink
    itself on the grid.
    """
    tp = TextPath((0, 0), letter, size=size,
                  prop=FontProperties(family="Arial", weight="bold"))
    return tp.get_extents().x0 * 0.3528


for letter, ax in zip("ABCDEFGHI", [aA, aB, aC, aD, aE, aF, aG, aH, aI]):
    # the letter is placed against the column grid, not against the axes spine:
    # x is the column's left edge, y is TAG_LIFT above that row's axes top. Both
    # numbers are constants, so A/D/G share one x, A/B/C share one y, and there
    # is no arithmetic that could drift when a label or a colour changes.
    _key = ROW_OF[letter]
    fig.text((COLX[COLOF[letter]] - ink_left_mm(letter)) / W,
             (row_y[_key] + ROW_H[_key] + TAG_LIFT) / H,
             letter, fontsize=9.2, fontweight="bold", color=J.INK,
             va="top", ha="left")

J.footer(fig, FOOTER)

problems = J.check_layout(fig)
print(f"layout problems: {len(problems)}")
for p in problems[:15]:
    print("   -", p)

J.save(fig, OUT / "figures", STEM, strict=False)

for ext in ("png", "pdf"):
    src = OUT / "figures" / f"{STEM}.{ext}"
    dst = OUT / "assets" / f"figure4_v7.{ext}"
    dst.write_bytes(src.read_bytes())
def _tool(name):
    """Homebrew → /usr/local → 项目内 _tools/poppler → PATH。"""
    cands = [Path("/opt/homebrew/bin") / name, Path("/usr/local/bin") / name,
             Path("/usr/bin") / name]
    cands += sorted((OUT / "_tools/poppler").glob(f"*/Library/bin/{name}.exe"))
    for c in cands:
        if c.is_file():
            return str(c)
    found = shutil.which(name)
    if found:
        return found
    raise SystemExit(f"[F] 找不到 {name}：PDF 已生成，SVG 无法导出")


subprocess.run([_tool("pdftocairo"), "-svg", str(OUT / "assets/figure4_v7.pdf"),
                str(OUT / "assets/figure4_v7.svg")], check=True)
print("wrote assets/figure4_v7.{png,pdf,svg}")
