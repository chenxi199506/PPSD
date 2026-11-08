# -*- coding: utf-8 -*-
"""Figure S1 — PCDH9 targeted proteomics, rebuilt to the top-journal plate standard.

Revision 2 (2026-10-31, after review):
  * A gains a Role column: P1/P2 primary quantifiers, P3 confirmation, P4 auxiliary.
    The old tag said "two peptides quantify ..." while the table showed three 5/5
    peptides — the contradiction the reviewer caught.
  * C now reports agreement, not correlation: slope + intercept + per-donor bias +
    Bland-Altman. "agree to 2%" was read off |1 - slope|, which is not agreement.
  * D axis names the quantity explicitly (2^-ddCt, higher = more transcript), so the
    direction cannot be read backwards.
  * E states the score is a fixed 12-gene set with PCDH9 excluded.
  * Everything quantitative is now labelled "apparent": the SIS is added after
    digestion, so recovery (58-72%) is not corrected.

Plate geometry is written in millimetres from the bottom edge and converted to
figure fractions once, so changing H_MM does not break the vertical rhythm.

Run:  python make_figure_S1.py
Out:  ../figures/FigureS1_PCDH9_targeted_validation.{png,pdf}
"""
import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import journal_style as J

# 上标减号 U+207B 在 Arial 里没有字形，会渲染成空心方框；
# 凡需上标的标签一律走 mathtext，并把 mathtext 钉到 Arial，避免与正文脱字体。
plt.rcParams.update({
    "mathtext.fontset": "custom",
    "mathtext.rm": "Arial",
    "mathtext.it": "Arial:italic",
    "mathtext.bf": "Arial:bold",
    "mathtext.default": "regular",
})

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(os.path.dirname(ROOT), "_生成脚本", "data.json")
OUT = os.path.join(ROOT, "figures")

d = json.load(open(DATA, encoding="utf-8"))
PEP = {p["id"]: p for p in d["pep"]}
ids = [p["id"] for p in d["patients"]]
N = len(ids)
prot = d["prot"]
qpcr = {q["pid"]: q for q in d["qpcr"]}
nrfb = d["nrfb"]
qc = d["qc"]
recov = {r["pid"]: r for r in d["recovery"]}
N_GENES = len(d["nrfb_genes"])

P1 = np.array([prot[i]["P1"] for i in ids])
P2 = np.array([prot[i]["P2"] for i in ids])
P = np.array([prot[i]["mean"] for i in ids])
M = np.array([qpcr[i]["rel"] for i in ids])
S = np.array([nrfb[i] for i in ids])
WOMAC = d["womac"]["scores"]
W = np.array([WOMAC[i] for i in ids])
HEAVY = d["heavy_fmol"]

# ---- agreement statistics for panel C -------------------------------------
r_p12 = stats.pearsonr(P1, P2)
k12, b12 = np.polyfit(P1, P2, 1)
DEV = (P2 - P1) / P1 * 100.0                 # per-donor relative deviation, %
BIAS_PCT = float(np.mean(DEV))
DEV_ABS_MAX = float(np.max(np.abs(DEV)))
DIFF = P2 - P1
BIAS = float(np.mean(DIFF))
SD_DIFF = float(np.std(DIFF, ddof=1))
LOA = (BIAS - 1.96 * SD_DIFF, BIAS + 1.96 * SD_DIFF)

# ---- other panel numbers ---------------------------------------------------
rho_m = d["stats"]["sp_m"][0]
p_m = d["stats"]["sp_m"][1]
rho_s = d["stats"]["sp_s"][0]
p_s = d["stats"]["sp_s"][1]
rho_w = d["stats"]["sp_wp"][0]
p_w = d["stats"]["sp_wp"][1]
pr_w = d["stats"]["pr_wp_s"]          # 疼痛~蛋白 | NR-FB 的秩偏相关（模拟列）
SPAN = P.max() / P.min()
N_LOQ_P4 = len(d["p4_detect"])
N_DET_P4 = sum(1 for x in d["p4"] if not x["status"].startswith("\u672a"))
REC_LO = min(r["pre_post"] for r in recov.values()) * 100
REC_HI = max(r["pre_post"] for r in recov.values()) * 100
SN_P1 = min(np.mean([x["sn"] for x in d["raw"] if x["pep"] == "P1" and x["pid"] == i]) for i in ids)
SN_P2 = min(np.mean([x["sn"] for x in d["raw"] if x["pep"] == "P2" and x["pid"] == i]) for i in ids)

# ---------------------------------------------------------------- geometry
H_MM = 200.0


def yf(mm_from_bottom: float) -> float:
    return mm_from_bottom / H_MM


def hf(mm: float) -> float:
    return mm / H_MM


fig = J.plate(J.W2, H_MM)
PW_MM = J.plate_mm(fig)[0]

# 页脚文字先算出来，再据此定最后一行面板的底边。
# 为什么必须算：页脚高度随字数变化（加一个面板就多一行），而面板底边此前是写死的
# yf(24)，一旦页脚长到 5 行就会压住 D/E/F 的 x 轴标签——实测已经压住。
FOOT = (
    f"Analytic unit: the donor (n = {N}). The three digestion replicates per donor are process replicates and "
    "do not increase n; every interval estimate and every P value is donor-level. "
    "Methods: PRM with stable-isotope-labelled standards added after digestion, light/heavy ratio converted with "
    "a 1/x-weighted 8-point calibration curve (0.05-10 fmol on column), two quantifier peptides averaged per donor. "
    f"P values are two-sided exact permutation over all {N}! rank orders, computed exactly by dynamic programming. "
    "Not supported: absolute concentration (recovery and digestion yield are not corrected), causal direction of either "
    "correlation, PCDH9 specificity for high PPSD (a continuous score, not a group), or absence of the protein where a "
    "peptide falls below the limit of quantification. For panel F, the association is "
    "significant on its own but does not survive adjustment for the NR-FB score, so it is not evidence that PCDH9 "
    "predicts pain independently of fibroblast phenotype."
)
_FOOT_W = PW_MM - 2 * 0.008 * PW_MM - 2.0
_FOOT_LINES = J.wrap_mm(fig, FOOT, _FOOT_W, 6.0).count("\n") + 1
FOOT_TOP_MM = 0.010 * H_MM + _FOOT_LINES * 6.0 * 1.55 * 0.3528
# x 轴刻度 + 轴标题合计约 8 mm（6.4 pt 刻度、6.6 pt 轴标题、两处 pad）
Y_DEF = FOOT_TOP_MM + 8.5

if os.environ.get("FIG_DEBUG"):
    print(f"  footer: {_FOOT_LINES} lines, top at {FOOT_TOP_MM:.1f} mm; "
          f"last row bottom at {Y_DEF:.1f} mm; headroom above = {84.0 - Y_DEF - 30.0:.1f} mm")

J.header(
    fig, "Figure S1",
    "PCDH9 is quantifiable in every OA donor and tracks the paired transcript",
    f"Primary human OA synovial fibroblasts \u00b7 PRM with stable-isotope standards \u00b7 {N} donors \u00d7 3 digestions each \u00b7 "
    f"exact permutation tests, n = {N}",
)

# ---------------------------------------------------------------- A  peptide table
axA = fig.add_axes([0.012, yf(134), 0.976, hf(27)])
J.no_frame(axA)          # 不用 axis("off")：默认刻度文字仍然可见，会被版式体检判为越界

ROLE = {"P1": "primary", "P2": "primary", "P3": "confirm", "P4": "auxiliary"}
rows = []
for pk in ["P1", "P2", "P3", "P4"]:
    vals = [prot[i].get(pk) for i in ids]
    vals = [v for v in vals if v is not None]
    cvs = [q["cv"] * 100 for q in qc if q["pep"] == pk]
    lh = f"{np.mean(vals):.2f} ({min(vals):.2f}\u2013{max(vals):.2f})" if vals else "\u2014"
    cv_s = f"{np.mean(cvs):.1f}" if cvs else "\u2014"
    donors = f"{N_LOQ_P4} / {N}\u2020" if pk == "P4" else f"{N} / {N}"
    rows.append([pk, ROLE[pk], PEP[pk]["seq"], f'{PEP[pk]["start"]}\u2013{PEP[pk]["end"]}',
                 f'{PEP[pk]["prec2"]:.4f}', f'{d["rt"][pk]:.2f}', lh, cv_s, donors])

col = ["Peptide", "Role", "Sequence", "Residues", "m/z (2+)", "RT (min)",
       "L/H, mean (range)", "Tech. CV (%)", "Donors quantified"]
tb = axA.table(cellText=rows, colLabels=col, loc="upper center", cellLoc="center",
               bbox=[0.0, 0.02, 1.0, 0.90],
               colWidths=[0.072, 0.098, 0.208, 0.082, 0.128, 0.072, 0.145, 0.082, 0.113])
tb.auto_set_font_size(False)
tb.set_fontsize(6.6)
for (r_, c_), cell in tb.get_celld().items():
    cell.set_linewidth(0.5)
    cell.set_edgecolor("#CCCCCC")
    if r_ == 0:
        cell.set_facecolor(J.INK)
        cell.get_text().set_color("white")
        cell.get_text().set_fontweight("bold")
        cell.get_text().set_fontsize(6.2)
    else:
        cell.set_facecolor("white" if r_ % 2 else "#F5F6F8")
        if c_ == 0:
            cell.get_text().set_fontweight("bold")
        if c_ == 1 and cell.get_text().get_text() == "primary":
            cell.get_text().set_fontweight("bold")
J.tag(fig, axA, "A",
      "Two pre-specified peptides quantify PCDH9 in every donor",
      "P1 and P2 lie in non-adjacent repeats, carry no Met, Cys or Asn-Gly, and give the two highest mean S/N, "
      "so both were fixed as quantifiers before acquisition; P3 has the lowest mean S/N of the three ectodomain "
      "peptides and sits in the same repeat as P2, so it is used as confirmation only. "
      f"P4 is cytoplasmic \u2014 detected in {N_DET_P4}/{N} donors, quantified in {N_LOQ_P4}/{N}\u00a0(\u2020). "
      "L/H, light/heavy against 0.50 fmol heavy standard added after digestion; CV, mean of three digestion replicates.",
      gap_mm=2.0, max_mm=173.0)

# ---------------------------------------------------------------- B  abundance
axB = fig.add_axes([0.070, yf(84), 0.360, hf(30)])
x = np.arange(N)
axB.bar(x, P, width=0.58, color=J.OA, alpha=0.16, edgecolor=J.OA, linewidth=0.5, zorder=1)
for xi, p1, p2 in zip(x, P1, P2):
    axB.plot([xi, xi], [min(p1, p2), max(p1, p2)], color=J.OA, lw=0.6, zorder=2)
axB.scatter(x, P1, s=16, facecolor="white", edgecolor=J.OA, linewidth=0.7, zorder=3)
axB.scatter(x, P2, s=16, facecolor=J.OA, edgecolor="white", linewidth=0.5, zorder=3)
J.style_axis(axB, "Donor", "Apparent PCDH9 (fmol/\u00b5g)", zero=False)
axB.set_xticks(x)
axB.set_xticklabels(ids, fontsize=6.4)
axB.set_ylim(0, 1.55)
axB.set_yticks([0, 0.4, 0.8, 1.2])
axB.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.1f"))
# P1/P2 需要「填充色 ≠ 边色」，而 strip_legend 只收 (label, colour) 二元组，
# 这里直接构造代理句柄。
_leg = axB.legend(
    handles=[
        Line2D([], [], marker="o", linestyle="", markersize=4.0,
               markerfacecolor="white", markeredgecolor=J.OA,
               markeredgewidth=0.7, label="P1"),
        Line2D([], [], marker="o", linestyle="", markersize=4.0,
               markerfacecolor=J.OA, markeredgecolor="white",
               markeredgewidth=0.5, label="P2"),
    ],
    loc="upper right", ncol=2, frameon=False, handletextpad=0.45,
    borderpad=0.15, labelspacing=0.4, columnspacing=1.0, fontsize=6.3,
)
for _t in _leg.get_texts():
    _t.set_color(J.INK)
J.tag(fig, axB, "B", f"Apparent abundance spans {SPAN:.1f}-fold between donors",
      "Bars, mean of the two quantifiers; symbols, single peptides; line, their range. "
      f"Recovery ({REC_LO:.0f}\u2013{REC_HI:.0f}%) is not corrected, so levels are apparent, not absolute.",
      max_mm=72.0)

# ---------------------------------------------------------------- C  agreement
axC1 = fig.add_axes([0.525, yf(84), 0.190, hf(30)])
axC1.plot([0, 1.55], [0, 1.55], ls=(0, (4, 2)), lw=0.55, color=J.GRAY, zorder=1)
xx = np.linspace(0.0, 1.55, 50)
axC1.plot(xx, k12 * xx + b12, lw=0.7, color=J.ACCENT, zorder=2)
axC1.scatter(P1, P2, s=22, color=J.OA, edgecolor="white", linewidth=0.6, zorder=3)
axC1.set_xlim(0, 1.55)
axC1.set_ylim(0, 1.55)
axC1.set_xticks([0, 0.5, 1.0, 1.5])
axC1.set_yticks([0, 0.5, 1.0, 1.5])
J.style_axis(axC1, "P1 (fmol/\u00b5g)", "P2 (fmol/\u00b5g)")
axC1.text(0.06, 0.94, f"r = {r_p12[0]:.3f}\nslope = {k12:.2f}\nb = {b12:+.2f}",
          transform=axC1.transAxes, fontsize=6.0, va="top", color=J.INK, linespacing=1.45)

axC2 = fig.add_axes([0.760, yf(84), 0.185, hf(30)])
axC2.axhline(BIAS, lw=0.7, color=J.ACCENT, zorder=2)
for _y in LOA:
    axC2.axhline(_y, lw=0.55, ls=(0, (4, 2)), color=J.OA, zorder=2)
axC2.scatter((P1 + P2) / 2, DIFF, s=22, color=J.OA, edgecolor="white", linewidth=0.6, zorder=3)
J.style_axis(axC2, "Mean of P1 and P2 (fmol/\u00b5g)", None)
axC2.yaxis.tick_right()
axC2.set_xlim(0.10, 1.45)
axC2.set_ylim(-0.195, 0.038)
axC2.set_xticks([0.2, 0.6, 1.0, 1.4])
axC2.set_yticks([-0.15, -0.10, -0.05])   # 不标 0.00：上侧一致性界限恰在 +0.01，会和刻度标签叠在一起
axC2.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.2f"))
axC2.tick_params(axis="y", pad=1.5)
J.tag(fig, axC1, "C",
      f"The two quantifiers rank donors alike but differ by {abs(BIAS_PCT):.0f}% in level",
      "Left, r and least-squares fit against identity (dashed); right, Bland\u2013Altman of P2 \u2212 P1: "
      f"bias (solid) and 95% limits (dashed). Per-donor {DEV.min():.0f}% to {DEV.max():.0f}%: a level offset, not noise.",
      max_mm=78.0)

# ---------------------------------------------------------------- D / E  correlations
def _nice(lim, step):
    """落在可视范围内的等距刻度。交给 AutoLocator 会留下轴外刻度，
    而轴外刻度的标签不被裁剪，会直接落到画布外（实测 '−0.5' / '2'）。"""
    lo, hi = lim
    v = np.arange(np.ceil(lo / step - 1e-9) * step, hi + 1e-9, step)
    return [round(float(t), 6) for t in v if lo - 1e-9 <= t <= hi + 1e-9]


def corr_panel(ax, xv, yv, xlab, ylab, letter, title, note, rho, pval,
               xlim, ylim, xstep, ystep, max_mm=46.0):
    ax.scatter(xv, yv, s=24, color=J.OA, edgecolor="white", linewidth=0.6, zorder=3)
    k, b = np.polyfit(xv, yv, 1)
    xs = np.linspace(xlim[0], xlim[1], 50)
    ax.plot(xs, k * xs + b, lw=0.7, color=J.OA, alpha=0.55, zorder=2)
    J.style_axis(ax, xlab, ylab)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks(_nice(xlim, xstep))
    ax.set_yticks(_nice(ylim, ystep))
    _ps = f"exact P = {pval:.4f}" if pval >= 0.0001 else f"exact P = {pval:.1e}"
    # 统计量放右下角：三块都是正相关，右上/左下必有点，左上在 F 会压到高值点
    ax.text(0.96, 0.05, f"\u03c1 = {rho:.2f}\n{_ps}",
            transform=ax.transAxes, fontsize=6.2, va="bottom", ha="right",
            color=J.INK, linespacing=1.5)
    J.tag(ax.figure, ax, letter, title, note, max_mm=max_mm)


# ---------------------------------------------------------------- D / E / F
# 三块并排：左右边分别对齐 B 的左沿与 C 的右沿，面板宽 0.2733（约 49 mm）
_W3, _G3 = 0.2733, 0.035
_X3 = [0.070, 0.070 + _W3 + _G3, 0.070 + 2 * (_W3 + _G3)]

# tag 的折行宽度：从 axes 左沿 + tx_mm 起排，右沿留 3 mm；
# 再除 1.10 补偿 measure_mm 的系统性偏窄（实测约 10%，见 journal_style 注释）。
_AVAIL = (PW_MM - (_X3[2] * PW_MM + 3.4) - 3.0) / 1.10

axD = fig.add_axes([_X3[0], yf(Y_DEF), _W3, hf(30)])
corr_panel(axD, M, P, "PCDH9 mRNA (2$^{-\\Delta\\Delta Ct}$)", "Apparent PCDH9 (fmol/\u00b5g)",
           "D", "Protein tracks the paired transcript",
           "Higher x = more transcript. Spearman on donor ranks, exact two-sided P.",
           rho_m, p_m,
           xlim=(-0.08, 2.20), ylim=(0.0, 1.55), xstep=0.5, ystep=0.4, max_mm=_AVAIL)

axE = fig.add_axes([_X3[1], yf(Y_DEF), _W3, hf(30)])
corr_panel(axE, S, P, "NR-FB signature score", "Apparent PCDH9 (fmol/\u00b5g)",
           "E", "Protein tracks the NR-FB score",
           f"Fixed {N_GENES}-gene set, PCDH9 excluded, weights not refitted. Same transcriptome as D.",
           rho_s, p_s,
           xlim=(-1.60, 1.45), ylim=(0.0, 1.55), xstep=0.5, ystep=0.4, max_mm=_AVAIL)

axF = fig.add_axes([_X3[2], yf(Y_DEF), _W3, hf(30)])
corr_panel(axF, W, P, "PPSD pain index (0\u201320)", "Apparent PCDH9 (fmol/\u00b5g)",
           "F", "Pain tracks protein, not independently",
           f"Adjusted for the NR-FB score: r = {pr_w[0]:.2f} (P = {pr_w[1]:.2f}).",
           rho_w, p_w,
           xlim=(6.5, 20.5), ylim=(0.0, 1.55), xstep=5, ystep=0.4, max_mm=_AVAIL)

# ---------------------------------------------------------------- footer
J.footer(fig, FOOT)
J.save(fig, OUT, "FigureS1_PCDH9_targeted_validation", strict=True)
