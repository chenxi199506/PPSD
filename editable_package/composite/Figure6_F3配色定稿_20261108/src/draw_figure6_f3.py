# -*- coding: utf-8 -*-
"""
draw_figure6_f3.py — Figure 6 重绘 v2：改用 Figure 3 B 的配色语法

与 v1（draw_figure6.py）的差别，只在配色体系，数据 / 统计 / 版面完全一致：

  v1 = 六个语义色平铺，同等视觉权重（Figure 4/7 的「分类色」语法）
  v2 = Figure 3 B 的「单一强调色 + 一群低饱和配角」语法
       被检验的条件（siRNA 敲低）是砖红主角，其余一律退为配角

2026-11-08 配色对账修正（v3，只动两个常量，数据/版式/统计一字未改）
--------------------------------------------------------------
原 v2 直接照搬 Figure 3 的深蓝 #2F5D8A 与青绿 #2E9C8E。但 A.3 版式与配色
表对同一批五个条件声明的是另一套色：

    G1 NT-CM  #4C78A8      ← v2 用 #2F5D8A   ✗ 同名不同色
    G2 KD-CM  #B4482F      ← 一致            ✓
    G3 Rescue #6B8E6F      ← v2 用 #2E9C8E   ✗ 同名不同色
    G4 Vehicle #8C8C8C     ← 一致            ✓
    G5 Mock   #8E6C8A      ← 一致            ✓

也就是说 Figure 6 与 Figure S1 / Figure 5 对「同一个 NT-CM」「同一个 Rescue」
给了两种色号，读者会以为是不同处理。本版把这两个常数锚回 A.3 声明值：
NT-CM / NT siRNA → CONTROL #4C78A8（主题·对照侧）；Rescue → SAGE #6B8E6F。
改完 Figure 6 与 Figure S1 / Figure 5 的五个共有组**完全同色**。

取自 Figure 3（build_F3_P08_portable.py 第 141–144 行与 STATE_COLOR）：
    BRICK     #B4482F   C_ACCENT / NR-FB core  —— 主角
    CONTROL   #4C78A8   主题·对照侧（v2 的 NAVY #2F5D8A 已退役）
    SAGE      #6B8E6F   语义扩展色·回补（v2 的 TEAL #2E9C8E 已退役）
    GREY_BOX  #8C8C8C   Figure 3 命名常量
    C_OTHER[1] #7FA8C9  Figure 3 B 的浅钢蓝（Untreated）
    C_OTHER[4] #8E6C8A  Figure 3 B 的藕紫

渲染约定也照 Figure 3 B：
    · 柱 / 箱无描边（edgecolor="none"），颜色只由填充承担
    · 误差线 / 须线用满强度同色细线（α 0.8, lw 0.7）
    · 供体连线用 FAINT #C9CFD4
    · 连续色标用 Figure 3 自己的 CMAP_V23（蓝–浅蓝–米白–浅砖–砖红），
      C、D 两个面板统一，不再用 RdBu_r

输出：out_f3/Figure6_F3配色.png (600 dpi) / .pdf
"""

from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Rectangle

# 可编辑包便携版：全部路径相对本脚本解析，整夹拷走也能重出 PNG / PDF。
# data.py 会到 ../plot_data/ 读 CSV；输出直接落在本资源目录根部，
# 供 切换Figure3版本.py 当作「Figure 6 定稿源图」嵌入合稿。
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import data as D          # noqa: E402
import style as S         # noqa: E402

OUT = ROOT

# ------------------------------------------------- Figure 3 的命名常量
BRICK = "#B4482F"      # C_ACCENT
CONTROL = "#4C78A8"    # 主题·对照侧（= A.3 的 G1 NT-CM；v2 的 NAVY #2F5D8A 已退役）
SAGE = "#6B8E6F"       # 语义扩展·回补（= A.3 的 G3 Rescue；v2 的 TEAL #2E9C8E 已退役）
GREY_BOX = "#8C8C8C"
STEEL = "#7FA8C9"      # C_OTHER[1]
PLUM = "#8E6C8A"       # C_OTHER[4]
FAINT = "#C9CFD4"      # Figure 3 的 FAINT

# Figure 3 自己的连续色标（源图 Figure 6 D 的蓝–白–砖红标尺）
CMAP_V23 = LinearSegmentedColormap.from_list(
    "nrfb", ["#4C78A8", "#C9D9E6", "#F3F0EE", "#DCAE9C", "#B4482F"])

# 同一色标、只把中点压深一点：CMAP_V23 是为 ±1…1.8 的量程调的，
# 用在 D 面板 ±0.3 的 log2 FC 上时，接近 0 的点会白到看不见。
CMAP_V23_D = LinearSegmentedColormap.from_list(
    "nrfb_d", ["#4C78A8", "#C9D9E6", "#E4DFDA", "#DCAE9C", "#B4482F"])

# ------------------------------------------------- 语义映射（主角 / 配角）
COL5 = {
    "Untreated": STEEL,     # 上游基线：最浅，退到最后
    "NT siRNA":  CONTROL,   # 对照：主题钢蓝，稳定参照
    "siRNA-1":   BRICK,     # 被检验条件 —— 唯一主角
    "siRNA-2":   BRICK,
    "Rescue":    SAGE,
}
COL_M = {
    "NT-CM":  CONTROL,
    "KD-CM":  BRICK,
    "Rescue": SAGE,
    "Vehicle": GREY_BOX,
    "Mock":   PLUM,
}
ACCENT = {BRICK}           # 主角集合：只有它们拿满强度

BAR_A = 0.45           # 柱填充：Figure 3 B 的箱体档（0.55）略收，因为这里还有点
BAR_A_ACC = 0.62       # 主角柱再深一档，让砖红压得住
DOT_A = 0.88           # 个体点：Figure 3 B 的强调档
DOT_A_ACC = 0.92
W_LW = 0.7             # 误差线 / 须线：Figure 3 B 的细线约定
W_A = 0.85

NB_CAP = 1.75


# ---------------------------------------------------------------- 工具
def _sem(v):
    v = np.asarray(v, float)
    return v.std(ddof=1) / np.sqrt(len(v))


def _alpha(c):
    return BAR_A_ACC if c in ACCENT else BAR_A


def _dotalpha(c):
    return DOT_A_ACC if c in ACCENT else DOT_A


def xlabels(ax, groups, rot=45, fs=None):
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels(groups, rotation=rot, ha="right",
                       rotation_mode="anchor", fontsize=fs or S.FS["tick"])
    ax.set_xlim(-0.62, len(groups) - 0.38)


def bar_dots(ax, groups, table, colmap, width=0.58, lines=True,
             seed=0, jitter=0.11, s=9):
    """柱 = 均值，误差线 = SEM，实心点 = 个体；按供体跨条件连线。"""
    rng = np.random.default_rng(seed)
    xs = np.arange(len(groups))
    donors = [d for d, _ in table[groups[0]]]

    for i, g in enumerate(groups):
        vals = [v for _, v in table[g]]
        m, se = np.mean(vals), _sem(vals)
        c = colmap[g]
        # Figure 3 B：箱体无描边，颜色只由填充承担
        ax.bar(i, m, width, facecolor=c, alpha=_alpha(c),
               edgecolor="none", linewidth=0, zorder=1)
        # Figure 3 B：须线用满强度同色细线
        ax.errorbar(i, m, yerr=se, fmt="none", ecolor=c, alpha=W_A,
                    elinewidth=W_LW, capsize=0, zorder=3)

    if lines:
        for dn in donors:
            ys = [dict(table[g]).get(dn, np.nan) for g in groups]
            ax.plot(xs, ys, color=FAINT, lw=0.5, zorder=2)

    for i, g in enumerate(groups):
        vals = [v for _, v in table[g]]
        off = rng.uniform(-jitter, jitter, len(vals))
        ax.scatter(np.full(len(vals), i) + off, vals, s=s, facecolor=colmap[g],
                   edgecolor="none", alpha=_dotalpha(colmap[g]), zorder=4)


def bar_wells(ax, groups, table, metric, width=0.58, seed=1, cap=None, s=8):
    """MEA：柱 = 孔均值，误差线 = SEM，实心点 = 单孔；cap 以上画空心三角。"""
    rng = np.random.default_rng(seed)
    for i, g in enumerate(groups):
        vals = np.array(table[g][metric], float)
        m, se = vals.mean(), _sem(vals)
        c = COL_M[g]
        ax.bar(i, m, width, facecolor=c, alpha=_alpha(c),
               edgecolor="none", linewidth=0, zorder=1)
        ax.errorbar(i, m, yerr=se, fmt="none", ecolor=c, alpha=W_A,
                    elinewidth=W_LW, capsize=0, zorder=3)

        off = rng.uniform(-0.17, 0.17, len(vals))
        if cap is None:
            ax.scatter(np.full(len(vals), i) + off, vals, s=s, facecolor=c,
                       edgecolor="none", alpha=_dotalpha(c), zorder=4)
        else:
            lo = vals <= cap
            ax.scatter((np.full(lo.sum(), i) + off[lo]), vals[lo], s=s,
                       facecolor=c, edgecolor="none", alpha=_dotalpha(c),
                       zorder=4)
            hi = ~lo
            k = int(hi.sum())
            if k == 0:
                continue
            spread = np.linspace(-0.13, 0.13, k) if k > 1 else np.zeros(1)
            ax.scatter(i + spread, np.full(k, cap + 0.025), s=15,
                       facecolor="none", edgecolor=c, linewidth=0.8,
                       marker="^", zorder=5, clip_on=True)

    xlabels(ax, groups)


# ---------------------------------------------------------------- A
def panel_a(ax):
    tab = D.fig1b()
    groups = list(tab)
    bar_dots(ax, groups, tab, COL5, seed=0, jitter=0.10, s=10, lines=False)

    ax.axhline(1.0, color=FAINT, lw=0.7, ls=(0, (4, 3)), zorder=0)

    ax.set_ylim(0, 1.45)
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4])
    xlabels(ax, groups)
    S.style_axis(ax, "PCDH9 mRNA (relative to NT)")
    S.panel_head(ax, "A", "PCDH9 knockdown efficiency", pad=14)


# ---------------------------------------------------------------- B
def panel_b(ax):
    tab = D.fig1c()
    groups = list(tab)

    ax.axvspan(1.55, 3.45, color=BRICK, alpha=0.045, lw=0, zorder=0)
    ax.axvspan(3.55, 4.45, color=SAGE, alpha=0.070, lw=0, zorder=0)

    for i, g in enumerate(groups):
        vals = np.array([v for _, v in tab[g]], float)
        c = COL5[g]
        ax.errorbar(i, vals.mean(), yerr=_sem(vals), fmt="none", ecolor=c,
                    alpha=W_A, elinewidth=W_LW, capsize=0, zorder=3)
        rng = np.random.default_rng(7)
        off = rng.uniform(-0.05, 0.05, len(vals))
        ax.scatter(np.full(len(vals), i) + off, vals, s=9, facecolor=c,
                   edgecolor="none", alpha=_dotalpha(c), zorder=4)
        # 均值横杠：直接对应 Figure 3 B 箱体内的白 / 同色中位线
        ax.plot([i - 0.16, i + 0.16], [vals.mean()] * 2, color=c,
                lw=1.3 if c in ACCENT else 1.0,
                solid_capstyle="butt", zorder=5)

    ax.axhline(0.0, color=FAINT, lw=0.7, ls=(0, (4, 3)), zorder=0)
    ax.set_ylim(-1.62, 1.15)
    ax.set_yticks([-1.5, -1.0, -0.5, 0.0, 0.5, 1.0])
    S.bracket(ax, 1, 2, 0.62, "**", h=0.10)
    S.bracket(ax, 2, 4, 0.90, "*", h=0.10)
    xlabels(ax, groups)
    S.style_axis(ax, "NR-FB signature score (z)")
    S.panel_head(ax, "B", "NR-FB core programme", pad=14)


# ---------------------------------------------------------------- C
def panel_c(ax, cax):
    genes, cols, mat = D.fig1d("z")
    m = np.array(mat)

    im = ax.pcolormesh(np.arange(m.shape[1] + 1), np.arange(m.shape[0] + 1), m,
                       cmap=CMAP_V23, vmin=-2, vmax=2, shading="flat",
                       linewidth=0, antialiased=False, edgecolors="none")

    for r in (5, 10):
        ax.axhline(r, color="white", lw=1.8, zorder=3)
    for c in (5, 10, 15, 20):
        ax.axvline(c, color="white", lw=1.8, zorder=3)

    ax.set_xlim(0, m.shape[1])
    ax.set_ylim(m.shape[0], 0)
    ax.set_yticks(np.arange(len(genes)) + 0.5)
    ax.set_yticklabels(genes, fontsize=S.FS["tick"] - 0.5, fontstyle="italic")
    ax.set_xticks([2.5, 7.5, 12.5, 17.5, 22.5])
    ax.set_xticklabels(D.G5, rotation=45, ha="right", rotation_mode="anchor",
                       fontsize=S.FS["tick"] - 0.5)
    ax.tick_params(length=0)
    S.strip_spines(ax, keep=())

    # 顶部条件色条：必须与热图的列块严格一一对应。
    # 2026-11-08 修正：旧代码写死 ((0,5,BRICK),(5,5,CONTROL),(10,3,FAINT))——
    # 只有 3 段、只覆盖 0–13 列，而热图是 5 组 × 5 位供体 = 25 列。
    # 结果色条只占热图一半宽，前两段还都是蓝红颠倒的，读者对不上组别。
    for i, g in enumerate(D.G5):
        ax.add_patch(Rectangle((i * 5, -0.52), 5, 0.22,
                               facecolor=COL5[g], edgecolor="white",
                               linewidth=0.45, clip_on=False, zorder=4))

    cb = ax.figure.colorbar(im, cax=cax, ticks=[-2, -1, 0, 1, 2])
    cb.ax.tick_params(labelsize=S.FS["small"], width=0.6, length=2)
    cb.outline.set_linewidth(0.6)
    cb.set_label("z-score", fontsize=S.FS["small"], labelpad=1)

    S.panel_head(ax, "C", "All 13 target genes (within-donor z)", pad=14)


# ---------------------------------------------------------------- D
def panel_d(ax, cax):
    d = D.fig1e()
    genes = D.NEURAL_ORDER
    n_r, n_c = len(genes), len(D.CMP_ORDER)

    norm = Normalize(vmin=-0.36, vmax=0.36)
    for j, c in enumerate(D.CMP_ORDER):
        for i, g in enumerate(genes):
            lfc, q, nlq = d[(g, c)]
            ax.scatter(j, n_r - 1 - i, s=8 + nlq * 32, c=[lfc], cmap=CMAP_V23_D,
                       norm=norm, edgecolor="none", zorder=3)

    ax.axvline(2.5, color=FAINT, lw=0.6, ls=(0, (2, 3)), zorder=0)

    ax.set_xlim(-0.6, n_c - 0.4)
    ax.set_ylim(-0.6, n_r - 0.4)
    ax.set_xticks(range(n_c))
    ax.set_xticklabels(D.CMP_LABEL, rotation=45, ha="right",
                       rotation_mode="anchor", fontsize=S.FS["tick"] - 1.0)
    ax.set_yticks(range(n_r))
    ax.set_yticklabels(genes[::-1], fontsize=S.FS["tick"] - 0.4, fontstyle="italic")
    ax.tick_params(length=0)
    S.strip_spines(ax, keep=())

    cb = ax.figure.colorbar(ScalarMappable(norm=norm, cmap=CMAP_V23_D), cax=cax,
                            ticks=[-0.3, 0, 0.3])
    cb.ax.tick_params(labelsize=S.FS["small"], width=0.6, length=2)
    cb.outline.set_linewidth(0.6)
    cb.ax.set_title("log2 FC", fontsize=S.FS["small"], color=S.C["ink"], pad=3)
    cb.ax.set_yticklabels(["-0.3", "0", "0.3"])

    S.panel_head(ax, "D", "Neural-associated genes", pad=14)


# ---------------------------------------------------------------- E
def panel_e(ax):
    tab = D.fig1f()
    groups = list(tab)
    bar_dots(ax, groups, tab, COL5, seed=4, jitter=0.10, s=10, lines=False)

    ax.set_ylim(0, 275)
    ax.set_yticks([0, 50, 100, 150, 200, 250])
    S.bracket(ax, 1, 2, 228, "**", h=14)
    S.bracket(ax, 2, 4, 250, "**", h=14)
    xlabels(ax, groups)
    S.style_axis(ax, r"CXCL12 (pg per $10^5$ cells)")
    S.panel_head(ax, "E", "CXCL12 secretion (ELISA)", pad=14)


# ---------------------------------------------------------------- F / G / H
def panel_f(ax):
    t = D.fig5_wells()
    bar_wells(ax, D.M5, t, "firing", seed=1)

    ax.set_ylim(0, 5.3)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    S.bracket(ax, 0, 1, 3.80, "***", h=0.18)
    S.bracket(ax, 1, 2, 4.18, "***", h=0.18)
    S.bracket(ax, 0, 3, 4.58, "n.s.", h=0.18, fs=S.FS["annot"])
    S.bracket(ax, 1, 3, 5.00, "**", h=0.18)

    S.style_axis(ax, "Mean firing rate (Hz)")
    S.panel_head(ax, "F", "Firing falls below vehicle", pad=14)


def panel_g(ax):
    t = D.fig5_wells()
    bar_wells(ax, D.M5, t, "isi", seed=2)

    ax.set_ylim(0, 1160)
    ax.set_yticks([0, 200, 400, 600, 800, 1000])
    S.bracket(ax, 0, 1, 890, "***", h=30)
    S.bracket(ax, 1, 2, 966, "***", h=30)
    S.bracket(ax, 0, 3, 1044, "***", h=30)

    S.style_axis(ax, "Mean inter-spike interval (ms)")
    S.panel_head(ax, "G", "Intervals lengthen past vehicle", pad=14)


def panel_h(ax):
    t = D.fig5_wells()
    bar_wells(ax, D.M5, t, "nburst", seed=3, cap=NB_CAP)

    ax.set_ylim(0, NB_CAP + 0.07)
    ax.set_yticks([0.0, 0.5, 1.0, 1.5])
    ax.set_yticklabels(["0.0", "0.5", "1.0", "1.5"])
    S.bracket(ax, 0, 1, 1.28, "**", h=0.06)
    S.bracket(ax, 0, 2, 1.47, "*", h=0.06)
    S.bracket(ax, 1, 2, 1.09, "n.s.", h=0.06, fs=S.FS["annot"])

    S.style_axis(ax, "Network bursts (per min)")
    S.panel_head(ax, "H", "Network bursts reach vehicle", pad=14)


# ---------------------------------------------------------------- 组装
def build():
    S.apply()
    plt.rcParams["savefig.bbox"] = None
    fig = S.figure(180, 158)

    ax_a = fig.add_axes([0.075, 0.712, 0.200, 0.180])
    ax_b = fig.add_axes([0.395, 0.712, 0.200, 0.180])
    ax_c = fig.add_axes([0.700, 0.395, 0.225, 0.497])
    cax_c = fig.add_axes([0.936, 0.545, 0.0075, 0.160])

    ax_d = fig.add_axes([0.075, 0.401, 0.155, 0.160])
    cax_d = fig.add_axes([0.264, 0.440, 0.008, 0.070])
    ax_e = fig.add_axes([0.395, 0.401, 0.200, 0.160])

    ax_f = fig.add_axes([0.075, 0.070, 0.200, 0.180])
    ax_g = fig.add_axes([0.395, 0.070, 0.200, 0.180])
    ax_h = fig.add_axes([0.700, 0.070, 0.200, 0.180])

    panel_a(ax_a)
    panel_b(ax_b)
    panel_c(ax_c, cax_c)
    panel_d(ax_d, cax_d)
    panel_e(ax_e)
    panel_f(ax_f)
    panel_g(ax_g)
    panel_h(ax_h)

    S.stamp(fig)
    return fig


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    f = build()
    png = os.path.join(OUT, "Figure6_F3配色.png")
    pdf = os.path.join(OUT, "Figure6_F3配色.pdf")
    f.savefig(png, dpi=600, facecolor="white")
    f.savefig(pdf, facecolor="white")
    print("saved:", png, os.path.getsize(png), "bytes")
    print("saved:", pdf)
