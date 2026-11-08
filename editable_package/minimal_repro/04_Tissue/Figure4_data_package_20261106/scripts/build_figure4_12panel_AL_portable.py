#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 4 · 四行三列 12 面板 A–L（2026-11-06 第八次追加 / 精简版）。

用户要求：
  1. 「去掉 M」→ 删除原第一行第四列的 M（NR-FB 转录贡献的 Control/OA/RA 三组箱线）；
  2. 「把 D 的位置替换成 N」→ 原 D（255 供体、两组 PCDH9 ~ CORE20 散点）撤下，
     把原 N（616 供体、Control/OA/RA 三色 PCDH9 ~ CORE20 散点）放到 D 的格位；
  3. 面板字母连续重编为 A–L：D 槽位仍标 D，其余字母不变，全图无 M/N。

版面（四行三列，180 mm 铺满，无留白列）：

      A B C
      D E F      <- D = 原 N 的 RA 三色散点
      G H I
      J K L

列几何沿用四列版按 y 轴标签实测宽度分配间距的思路，但由 4 列改为 3 列：
LEFT 21.374 mm（A 的 15 个状态名 14.37 mm）、G12 7.5 mm（数值刻度）、
G23 23.0 mm（C/F 队列标签 18.63 mm、I 16.94 mm）、RIGHT_M 3.0 mm，
剩下 (180 - 21.374 - 3 - 7.5 - 23)/3 = 41.709 mm 三等分。

统计量全部来自本包 compute_y_ra.py 的产出（y_ra_stats.json /
y_ra_donor_scores.csv），绘图脚本不重算统计，并在开头断言 CSV 与 JSON 同步。
所有 12 个面板均为原生重绘：不读取任何图版位图、不 imshow、不裁贴。
PDF 中 /Subtype /Image 应为 0。
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon
from matplotlib.textpath import TextPath
from scipy import stats as SS

sys.stdout.reconfigure(encoding="utf-8")

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG / "data"
V7 = PKG / "scripts" / "recompose_fig4_v7_portable.py"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(PKG / "scripts"))
OUT = PKG / "figures"
OUT.mkdir(parents=True, exist_ok=True)

RES = ROOT / "identity_results"
F7 = ROOT / "sources" / "bulk_own_cohort_20261028" / "Figure7" / "data"
DER = ROOT / "derived"
XS = json.loads((DER / "x_ppsd_stats.json").read_text(encoding="utf-8"))
YR = json.loads((DER / "y_ra_stats.json").read_text(encoding="utf-8"))
YRA = pd.read_csv(DER / "y_ra_donor_scores.csv")

# 改数据后忘了同步统计量时，这里会直接报错，避免「点云是新的、P 值是旧的」
for _g in ("all", "Control", "OA", "RA"):
    _d = YRA if _g == "all" else YRA[YRA.group == _g]
    _r = float(np.corrcoef(_d["PCDH9"], _d["CORE20"])[0, 1])
    assert len(_d) == YR["groups"][_g]["n"], f"D 面板 {_g} 的 n 与 JSON 不一致"
    assert abs(_r - YR["groups"][_g]["r"]) < 1e-6, f"D 面板 {_g} 的 r 与 JSON 不一致"

# ---------------------------------------------------------------- v7 复用 ----
_v7txt = V7.read_text(encoding="utf-8")
_cut = _v7txt.index("fig = J.plate(")
V: dict = {"__file__": str(V7), "__name__": "_v7_layout_readonly"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(_v7txt[:_cut], str(V7), "exec"), V)

_NEED = ("J", "D", "ST", "SS", "np", "pd", "plt", "Polygon", "FontProperties",
         "TextPath", "eff", "meta", "frac", "dmeta", "states", "STATE_SHORT",
         "pain", "poolz", "deltas", "stats", "box", "forest", "fmt_p", "sv",
         "TICK", "AXPOS", "COLX", "COLOF", "ROW_H_MM", "TAG_LIFT", "XLABEL_H")
_missing = [k for k in _NEED if k not in V]
assert not _missing, f"v7 布局块缺少这些名字: {_missing}"
for _k in _NEED:
    globals()[_k] = V[_k]

J = V["J"]
assert (PKG / "scripts" / "journal_style.py").exists()

# ------------------------------------------------- 蛋白三联图：字母重映射 ----
# 原 G/H/I 重编为 J/K/L；统计量按新 key 现算（与 v7 同口径、同函数）
_d = D.figS1()
_prot = np.array([r["protein"] for r in _d], float)
_XKEY = {"J": "mrna", "K": "nrfb", "L": "pain"}
_X = {k: np.array([r[v] for r in _d], float) for k, v in _XKEY.items()}
RHO = {k: float(ST.spearman(_prot, v)) for k, v in _X.items()}
PVAL = {k: float(ST.exact_spearman_p(_prot, v)) for k, v in _X.items()}
TQ = float(SS.t.ppf(0.975, len(_prot) - 2))

# ---------------------------------------------------------------- 本版数据 ----
BD = pd.read_csv(RES / "bulk_donor_scores.csv")
BST = json.load(open(RES / "stats_bulk.json", encoding="utf-8"))
assert len(BD) == BST["n_donors"] == 255
BOX = pd.read_csv(F7 / "Fig7A_box_samplelevel.tsv", sep="\t")

# ---------------------------------------------------------------- 版式 --------
PW = 180.0
AXES_H = 36.0
ROW_BAND_H = TAG_LIFT + AXES_H + XLABEL_H
GAP = 6.0
Y0 = 12.0
ROW_TOP = [Y0 + r * (ROW_BAND_H + GAP) for r in range(4)]
BOTTOM = ROW_TOP[3] + ROW_BAND_H

COL_X = [AXPOS["A"][0], AXPOS["B"][0], AXPOS["C"][0]]
COL_W = [AXPOS["A"][1], AXPOS["B"][1], AXPOS["C"][1]]
LETTER_X = [COLX[0], COLX[1], COLX[2]]

# ------------------------------------------------------- 三列几何（实测） ----
# 沿用四列版「按各列 y 轴标签实测宽度分配间距」的思路，改为 3 列铺满 180 mm。
#   实测：A 状态名 14.37、C/F 队列标签 18.63、I 面板 16.94、数值刻度 ≤ 3.0 mm。
NCOL = 3
LEFT = AXPOS["A"][0]                 # 21.374：沿用 v7，A 的 15 个状态名靠它留白
RIGHT_M = 3.0
G12 = 7.5                            # 第 2 列标签：数值刻度
G23 = 23.0                           # 第 3 列标签：C/F 18.63、I 16.94
COL_W3 = (PW - LEFT - RIGHT_M - (G12 + G23)) / NCOL
_GAPS = [0.0, G12, G12 + G23]
COL_X3 = [LEFT + i * COL_W3 + _GAPS[i] for i in range(NCOL)]
COL_X, COL_W = COL_X3, [COL_W3] * NCOL
LETTER_X = list(COL_X3)
assert COL_X3[-1] + COL_W3 <= PW - RIGHT_M + 1e-9

HEADER_SUB = (
    "Twelve panels, four rows; D shows PCDH9 against CORE20 across control, OA and RA. "
    "Every panel drawn from source result tables, no raster content. 180 mm."
)

def _fp(p: float) -> str:
    """图注里的 P 值：不走 fmt_p，避免 mathtext 混进纯文本页脚。"""
    return "P < 0.001" if p < 1e-3 else f"P = {p:.3f}"


_YG = YR["groups"]

FOOTER = (
    "Analysis unit: the donor in A, B, D and G; the sample in E and H; 10 paired "
    "synovial explants in J-L; C and F are cohort-level meta-analyses over 8 and 7 estimates. "
    "I is a z-unit forest of PCDH9 high-minus-low contrasts: P1 pain (11/11) and P2 OA (41/41) "
    "from the in-house array, plus four non-overlapping PPSD strata (IPFP 7/8, syn 12/14, "
    "SF 12/13, cart 14/14). PPSD is the donor-level mean z of 300 pain-axis genes (GSE248453), "
    "split at the tissue median; the two grey open rows (all 46/50, threshold 19/77) overlap "
    "the strata and are shown for reference, not pooled. P1/P2 log2-CPM deltas were divided by "
    "cohort SD to enter the z scale. The diamond is a DerSimonian-Laird pool of the six "
    "non-overlapping contrasts (0.65, 0.14-1.17; I2 = 55%). H is the B-style boxplot of P1 "
    "high versus low pain. "
    f"D is the RA-extended PCDH9 against CORE20 scatter in three colours: "
    f"r = {_YG['all']['r']:+.2f} overall (n = {_YG['all']['n']}), "
    f"{_YG['RA']['r']:+.2f} within RA (n = {_YG['RA']['n']}), "
    f"{YR['n_cohorts_positive_core20']}/{YR['n_cohorts_with_r']} cohorts positive. "
    "D z-scores within cohort over the three groups together, so its axis is not the archived "
    "two-group 255-donor basis; within-group correlations are unaffected by this linear "
    "rescaling. "
    "Method: CORE20 and PCDH9 are z-scored within cohort; deconvolution is reference-guided "
    "nu-SVR on bulk mRNA, so fractions are transcript contributions, not cell counts; C and F "
    "show Hedges' g or weighted delta with 95% CI. All twelve panels are drawn natively from "
    "archived source tables; the PDF contains no image objects. J-L show apparent PCDH9 protein "
    "(fmol/ug) against the paired transcript, the fixed 12-gene NR-FB score and WOMAC pain with "
    "the 95% band of the least-squares fit (t, df = 8); K is not an independent repeat of J, "
    "and after conditioning on the NR-FB score the partial correlation with pain is r = 0.32 "
    "(P = 0.37). G is re-plotted from merged Figure 1 with the same 255 bulk donors "
    "(r = 0.61), no new analysis. Does not support: a rise in NR-FB cell number, "
    "a causal role for PCDH9 in pain, an independent PCDH9 effect after conditioning on the "
    "NR-FB score, or that bulk neural-module reads localise nerve fibres; E compares diagnostic "
    "labels rather than pain states within OA; the P2 high/low split in I is the OA/control "
    "contrast, not a pain score; the PPSD strata are cross-sectional and tissue-confounded; "
    "the RA group in D is cross-sectional and drawn from more cohorts than the control/OA "
    "groups, so the RA contrast is cohort-confounded; and the pain association in L is "
    "cross-sectional on ten explants only."
)


def footer_height_mm() -> float:
    probe = J.plate(PW, 150.0)
    n = J.wrap_mm(probe, FOOTER, PW - 10.0, 6.0).count("\n") + 1
    plt.close(probe)
    return n * 6.0 * 1.55 * 0.3528


FOOT_H = footer_height_mm()
PH = BOTTOM + FOOT_H + 7.0


# ---------------------------------------------------------------- 通用工具 ----
def ax_h_mm(ax) -> float:
    return ax.get_position().height * PH


def bracket(ax, x1, x2, y_base_frac, label, leg_mm=1.1, gap_mm=0.9, fs=6.2) -> None:
    h = ax_h_mm(ax)
    leg, gap = leg_mm / h, gap_mm / h
    tr = ax.get_xaxis_transform()
    ax.plot([x1, x1, x2, x2],
            [y_base_frac, y_base_frac + leg, y_base_frac + leg, y_base_frac],
            color=J.RULE, lw=0.6, transform=tr, clip_on=False, solid_capstyle="butt")
    ax.text((x1 + x2) / 2, y_base_frac + leg + gap, label,
            ha="center", va="bottom", fontsize=fs, color=J.INK, transform=tr)


def ink_left_mm(letter: str, size: float = 9.2) -> float:
    tp = TextPath((0, 0), letter, size=size,
                  prop=FontProperties(family="Arial", weight="bold"))
    return tp.get_extents().x0 * 0.3528


def axes_at(row: int, col: int):
    top = ROW_TOP[row] + TAG_LIFT
    return [COL_X[col] / PW, 1.0 - (top + AXES_H) / PH,
            COL_W[col] / PW, AXES_H / PH]


def letter_at(fig, row: int, col: int, letter: str) -> None:
    x = (LETTER_X[col] - ink_left_mm(letter)) / PW
    fig.text(x, 1.0 - ROW_TOP[row] / PH, letter, fontsize=9.2,
             fontweight="bold", color=J.INK, va="top", ha="left")


# ---------------------------------------------------------------- 统计 --------
def high_low(cohort: str):
    g = BOX[BOX["cohort"] == cohort]
    hi = g.loc[g["group"] == "High", "PCDH9_log2cpm"].to_numpy(float)
    lo = g.loc[g["group"] == "Low", "PCDH9_log2cpm"].to_numpy(float)
    d = hi.mean() - lo.mean()
    vh, vl = hi.var(ddof=1) / len(hi), lo.var(ddof=1) / len(lo)
    se = float(np.sqrt(vh + vl))
    df = (vh + vl) ** 2 / (vh ** 2 / (len(hi) - 1) + vl ** 2 / (len(lo) - 1))
    t = SS.t.ppf(0.975, df)
    return dict(cohort=cohort, n=(len(hi), len(lo)), d=d, se=se,
                lo=d - t * se, hi=d + t * se,
                p=float(2 * SS.t.sf(abs(d / se), df)), samples=(hi, lo))


P1, P2 = high_low("P1 (pain)"), high_low("P2 (OA)")
assert abs(P1["d"] - 0.88) < 0.01
assert abs(float(sv("A", "pain Welch P")) - 0.003) < 1e-9

# I 面板显示顺序：先两个队列，再 PPSD 四层（按效应降序），最后两行参考
_I_ORDER = ["P1 pain", "P2 OA", "PPSD IPFP", "PPSD syn", "PPSD SF",
            "PPSD cart", "PPSD all", "PPSD thr all"]
_I = {r["key"]: r for r in XS["rows"]}
assert set(_I_ORDER) == set(_I), (set(_I_ORDER) ^ set(_I))
I_ROWS = [_I[k] for k in _I_ORDER]
I_OV = XS["overall"]
I_COR = {c["stratum"]: c for c in XS["correlations"]}


# ------------------------------------------------- A/B/C/E/F/J/K/L（v7 原生）--
def draw_A(ax) -> None:
    nonfib = {"Macrophage", "T_NK", "B_Plasma", "Endothelial", "Pericyte_SMC", "Mast"}
    yD = np.arange(len(states), 0, -1)
    ax.axvline(0, color=J.HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=0)
    for yy, r in zip(yD, states.itertuples()):
        if r.state == "NR-FB core":
            c, filled = J.ACCENT, True
        elif r.state in nonfib:
            c, filled = J.GRAY, False
        else:
            c, filled = J.GRAY, True
        ax.hlines(yy, r.lo * 100, r.hi * 100, color=c, lw=0.9, alpha=0.5, zorder=2)
        ax.scatter(r.diff * 100, yy, s=11, zorder=4, linewidths=0.7,
                   facecolor=c if filled else "white", edgecolor=c)
    ax.set_yticks(yD)
    ax.set_yticklabels([STATE_SHORT.get(s, s) for s in states.state])
    ax.set_ylim(0.35, len(states) + 0.65)
    ax.set_xlim(-7.4, 6.4)
    ax.set_xticks([-5, 0, 5])
    ax.set_xlabel("Difference in transcript contribution (pp)", labelpad=1.6)
    J.style_axis(ax, labelpad=1.6)
    ax.tick_params(axis="y", length=0, labelsize=TICK["A"], pad=2.0)
    for lbl in ax.get_yticklabels():
        if lbl.get_text() == "NR-FB core":
            lbl.set_color(J.ACCENT)
            lbl.set_fontweight("bold")


def draw_B(ax) -> None:
    gC = [frac.loc[frac.condition == "Normal", "NR-FB core"].to_numpy() * 100,
          frac.loc[frac.condition == "OA", "NR-FB core"].to_numpy() * 100]
    box(ax, gC, ["Control", "OA"], [J.HEALTHY, J.OA])
    ax.set_ylabel("NR-FB transcript contribution (%)")
    ax.set_ylim(-1.5, 1.0)
    J.style_axis(ax)
    lo, _ = ax.get_ylim()
    top = max(max(gC[0]), max(gC[1]))
    h = ax_h_mm(ax)
    ax.set_ylim(lo, lo + (max(top, 0.6) - lo) * h / (h - 6.0))
    lo2, hi2 = ax.get_ylim()
    yb = (top - lo2) / (hi2 - lo2) + 1.1 / h
    bracket(ax, 1, 2, yb, fmt_p(float(dmeta.p)))


def draw_C(ax) -> None:
    labC = [f"{r.cohort_id} ({r.n_Normal}/{r.n_OA})" for r in eff.itertuples()]
    forest(ax, labC, eff.hedges_g.to_numpy(), eff.ci_low.to_numpy(), eff.ci_high.to_numpy(),
           J.OA, diamond=(meta.g, meta.ci_low, meta.ci_high), point_size=11,
           label_size=TICK["C"], xlabel="Hedges' g (OA − control)",
           xlim=(-1.7, 5.5), xticks=[-1, 0, 1, 2, 3, 4, 5])


def draw_E(ax) -> None:
    grp = poolz.group.replace({"Arthralgia": "OA+pain", "OA": "OA+pain"})
    keep = grp.isin(["Control", "OA+pain", "RA"])
    poolz2, grp2 = poolz[keep], grp[keep]
    gF = [poolz2.loc[grp2 == k, "z"].to_numpy() for k in ["Control", "OA+pain", "RA"]]
    box(ax, gF, ["Control", "OA+pain", "RA"], [J.HEALTHY, J.OA, J.GRAY])
    ax.axhline(0, color=J.HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=0)
    ax.set_ylabel("PCDH9 (within-cohort z)")
    ax.set_ylim(-4.4, 5.8)
    ax.set_yticks([-4, -2, 0, 2, 4])
    J.style_axis(ax)
    pvals = [float(sv("D", "OA+pain vs control, Welch P")),
             float(sv("D", "OA+pain vs RA, Welch P")),
             float(sv("D", "RA vs control, Welch P"))]
    for (x1, x2), y_base, p in zip([(1, 2), (2, 3)], [0.715, 0.812], pvals[:2]):
        bracket(ax, x1, x2, y_base, fmt_p(p))


def draw_F(ax) -> None:
    labG = [f"{r.cohort} ({r.n_control}/{r.n_OA_pain})" for r in deltas.itertuples()]
    nums = [float(v) for v in sv("E", "weighted delta [95% CI]")
            .replace("[", " ").replace("]", " ").replace(",", " ").replace("+", " ").split()]
    forest(ax, labG, deltas.delta_z.to_numpy(),
           (deltas.delta_z - deltas.ci95).to_numpy(),
           (deltas.delta_z + deltas.ci95).to_numpy(),
           J.OA, diamond=(nums[0], nums[1], nums[2]), label_size=TICK["F"],
           point_size=9, xlabel="Δ PCDH9 (OA − control)",
           xlim=(-1.75, 2.45), xticks=[-1, 0, 1, 2])


MK = {"J": dict(marker="o", size=11.0),
      "K": dict(marker="^", size=14.0),
      "L": dict(marker="s", size=11.5)}
# v7 的 TICK 以 A–I 为 key；重编后 J/K/L 分别沿用 G/H/I 的刻度字号
TICK_P = {"J": TICK["G"], "K": TICK["H"], "L": TICK["I"]}
PROT_SPEC = {
    "J": ((0.0, 2.25), [0, 0.5, 1.0, 1.5, 2.0], r"PCDH9 mRNA ($2^{-\Delta\Delta Ct}$)"),
    "K": ((-1.75, 1.75), [-1.5, -0.5, 0.5, 1.5], "NR-FB signature score"),
    "L": ((5.0, 21.0), [8, 12, 16, 20], "WOMAC pain (0\u201320)"),
}


def draw_protein(ax, letter: str) -> None:
    xlim, xticks, xlabel = PROT_SPEC[letter]
    x, y = _X[letter], _prot
    k, b = np.polyfit(x, y, 1)
    xpad = 0.03 * (xlim[1] - xlim[0])
    xs = np.linspace(xlim[0] + xpad, xlim[1] - xpad, 120)
    res = y - (b + k * x)
    se = np.sqrt((res ** 2).sum() / (len(x) - 2))
    sxx = ((x - x.mean()) ** 2).sum()
    band = TQ * se * np.sqrt(1.0 / len(x) + (xs - x.mean()) ** 2 / sxx)
    ax.fill_between(xs, b + k * xs - band, b + k * xs + band,
                    color=J.OA, alpha=0.20, lw=0, zorder=2)
    ax.plot(xs, b + k * xs, color=J.INK, lw=0.9, zorder=4)
    ax.scatter(x, y, s=MK[letter]["size"], marker=MK[letter]["marker"],
               facecolor=J.OA, edgecolor="none", linewidth=0.0, alpha=0.85, zorder=3)
    ax.set_xlim(*xlim)
    ax.set_xticks(xticks)
    ax.set_ylim(0.0, 1.6)
    ax.set_yticks([0, 0.4, 0.8, 1.2, 1.6])
    ax.set_xlabel(xlabel, labelpad=1.6)
    ax.set_ylabel("Apparent PCDH9 (fmol/\u00b5g)")
    J.style_axis(ax, labelpad=1.6)
    ax.tick_params(axis="y", labelsize=TICK_P[letter], pad=2.0)
    ax.annotate("\u03c1 = %.2f  \u00b7  P = %.4f" % (RHO[letter], PVAL[letter]),
                xy=(0.04, 0.97), xycoords="axes fraction", ha="left", va="top",
                fontsize=6.2, color=J.GRAY)


# ------------------------------------------------------------ D / G / H / I --
def scatter_bulk(ax, xcol: str, xlabel: str, stat: dict) -> None:
    for g, col in [("Control", J.HEALTHY), ("OA", J.OA)]:
        sub = BD[BD["group"] == g]
        ax.scatter(sub[xcol], sub["PCDH9"], s=4.5, color=col, alpha=0.72,
                   lw=0, zorder=3, label=f"{g} ({len(sub)})")
    k = np.polyfit(BD[xcol], BD["PCDH9"], 1)
    xs = np.linspace(BD[xcol].min(), BD[xcol].max(), 10)
    ax.plot(xs, np.polyval(k, xs), color=J.INK, lw=0.8, zorder=4)
    J.style_axis(ax, xlabel=xlabel, ylabel="PCDH9 (z)", labelpad=1.6)
    ax.legend(loc="lower right", handletextpad=0.25, borderpad=0.05,
              labelspacing=0.2, handlelength=0.8, fontsize=6.0)
    ax.annotate(f"r = {stat['r']:.2f} ({stat['ci'][0]:.2f}\u2013{stat['ci'][1]:.2f})",
                xy=(0.03, 0.90), xycoords="axes fraction", ha="left", va="top",
                fontsize=6.2, color=J.MUTED,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.82, pad=0.3))


def draw_G(ax) -> None:
    """原 U：PCDH9 ~ 神经模块。"""
    scatter_bulk(ax, "NEURAL", "Neural module (z)", BST["pcdh9_neural"])


def draw_H(fig, ax, col: int = 1) -> None:
    """原 D：P1 疼痛队列 High/Low 分组箱线。"""
    hi, lo = P1["samples"]
    box(ax, [lo, hi], ["Low", "High"], [J.HEALTHY, J.OA])
    ax.set_ylim(min(lo.min(), hi.min()) - 0.20, max(lo.max(), hi.max()) + 1.00)
    ax.set_yticks([3, 4, 5, 6])
    J.style_axis(ax, xlabel="Pain score", ylabel="PCDH9 (log2 CPM)", labelpad=1.6)
    bracket(ax, 1, 2, 0.80, "** P = 0.003")
    for cand in ["Pain score (P1, n = 11 / 11)", "Pain score (high / low)", "Pain score"]:
        if J.measure_mm(fig, cand, 7.0) <= COL_W[col] + 6.0:
            ax.set_xlabel(cand, labelpad=1.6)
            break


def draw_I(fig, ax) -> None:
    """原 X：ΔPCDH9 森林图，8 行，统一 z 口径，含三套 PPSD 数据。"""
    n = len(I_ROWS)
    y = np.arange(n, 0, -1)
    ax.axvline(0, color=J.HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=0)
    for yy, r in zip(y, I_ROWS):
        c = J.OA if r["pooled"] else J.MUTED
        ax.hlines(yy, r["lo"], r["hi"], color=c, lw=0.9, alpha=0.5, zorder=2)
        ax.scatter(r["d"], yy, s=9, zorder=4, linewidths=0.7,
                   facecolor=c if r["pooled"] else "white", edgecolor=c)
    bottom = -0.55
    ax.add_patch(Polygon([[I_OV["lo"], bottom], [I_OV["d"], bottom + 0.34],
                          [I_OV["hi"], bottom], [I_OV["d"], bottom - 0.34]],
                         closed=True, facecolor=J.INK, edgecolor="none", zorder=5))
    ax.set_ylim(bottom - 1.05, n + 0.55)
    ax.set_yticks(list(y) + [bottom])
    ax.set_yticklabels([r["label"] for r in I_ROWS] + ["Overall"], fontsize=6.0)
    ax.set_xlim(-1.15, 2.35)
    ax.set_xticks([-1, 0, 1, 2])
    ax.set_xlabel("Δ PCDH9 (z, high − low)", labelpad=1.6)
    J.style_axis(ax, labelpad=1.6)
    ax.tick_params(axis="y", length=0, labelsize=6.0, pad=2.0)
    for lbl, r in zip(ax.get_yticklabels()[:n], I_ROWS):
        if not r["pooled"]:
            lbl.set_color(J.MUTED)
    # 连续相关（第三套口径）压一行放在轴下，避免压住 8 行数据
    ax.text(0.5, -0.215, "r: all +%.2f · syn +%.2f"
            % (I_COR["all"]["r"], I_COR["syn"]["r"]),
            transform=ax.transAxes, ha="center", va="top", fontsize=5.6, color=J.MUTED)


# ------------------------------------------------- D（RA 三色散点）---------
def draw_D(ax) -> None:
    """新 D（原「Y 图」/ N）：PCDH9 ~ CORE20，Control/OA/RA 三色，616 供体。

    原 D（255 供体、两组、r = 0.42）与本面板内容重复，按用户要求撤下。
    z 在队列内按三组合并计算（一组基准，三组同等对待）；组内相关不受
    基准选择影响（线性变换不改变组内 Pearson r）。
    """
    for g, col in [("Control", J.HEALTHY), ("OA", J.OA), ("RA", J.GRAY)]:
        sub = YRA[YRA.group == g]
        ax.scatter(sub["CORE20"], sub["PCDH9"], s=3.2, color=col, alpha=0.62,
                   lw=0, zorder=3, label=f"{g} ({len(sub)})")
    k = np.polyfit(YRA["CORE20"], YRA["PCDH9"], 1)
    xs = np.linspace(YRA["CORE20"].min(), YRA["CORE20"].max(), 10)
    ax.plot(xs, np.polyval(k, xs), color=J.INK, lw=0.8, zorder=4)
    ax.set_xlim(-3.2, 1.75)
    ax.set_xticks([-3, -2, -1, 0, 1])
    ax.set_ylim(-4.4, 3.5)
    ax.set_yticks([-4, -2, 0, 2])
    J.style_axis(ax, xlabel="CORE20 (z)", ylabel="PCDH9 (z)", labelpad=1.6)
    ax.legend(loc="lower right", handletextpad=0.2, borderpad=0.05,
              labelspacing=0.15, handlelength=0.7, fontsize=5.6)
    ax.annotate("r = %+.2f · RA %+.2f" % (_YG["all"]["r"], _YG["RA"]["r"]),
                xy=(0.03, 0.94), xycoords="axes fraction", ha="left", va="top",
                fontsize=5.8, color=J.MUTED,
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.82, pad=0.3))


# ---------------------------------------------------------------- build ------
LAYOUT = [
    ("A", 0, 0, draw_A), ("B", 0, 1, draw_B), ("C", 0, 2, draw_C),
    ("D", 1, 0, draw_D), ("E", 1, 1, draw_E), ("F", 1, 2, draw_F),
    ("G", 2, 0, draw_G), ("H", 2, 1, draw_H), ("I", 2, 2, draw_I),
    ("J", 3, 0, draw_protein), ("K", 3, 1, draw_protein), ("L", 3, 2, draw_protein),
]


def build() -> None:
    print("3-col grid (mm): x = " + ", ".join(f"{v:.3f}" for v in COL_X) +
          f" | w = {COL_W3:.3f} | gutters {G12}/{G23}")
    print(f"rows (mm): band {ROW_BAND_H:.2f}, tops " +
          ", ".join(f"{v:.2f}" for v in ROW_TOP) +
          f"; bottom {BOTTOM:.2f}; footer {FOOT_H:.1f}; plate {PW:.0f} x {PH:.1f} mm")
    print(f"I: {len(I_ROWS)} rows + Overall; random-effects {I_OV['d']:.3f} "
          f"[{I_OV['lo']:.3f},{I_OV['hi']:.3f}] I2={I_OV['I2']:.0f}%")
    print("row4 rho", {k: round(v, 4) for k, v in RHO.items()},
          "p", {k: round(v, 4) for k, v in PVAL.items()})
    print(f"D (RA 3-colour): r all {_YG['all']['r']:+.3f} (n={_YG['all']['n']}), "
          f"RA {_YG['RA']['r']:+.3f} (n={_YG['RA']['n']}); M panel removed")

    fig = J.plate(PW, PH)
    J.header(fig, "Figure 4", "The NR-FB programme and PCDH9 in OA and pain", HEADER_SUB)

    for letter, row, col, fn in LAYOUT:
        ax = fig.add_axes(axes_at(row, col))
        letter_at(fig, row, col, letter)
        if letter in ("J", "K", "L"):
            fn(ax, letter)
        elif letter == "H":
            fn(fig, ax, col)
        elif letter == "I":
            fn(fig, ax)
        else:
            fn(ax)

    J.footer(fig, FOOTER, x=5.0 / PW, y=0.006, width_mm=PW - 10.0)
    J.save(fig, OUT, "Figure4_12panel_AL_180mm", dpi=600, strict=True)


if __name__ == "__main__":
    build()
    print("DONE")
