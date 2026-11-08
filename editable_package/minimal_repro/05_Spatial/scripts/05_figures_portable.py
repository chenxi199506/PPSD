# -*- coding: utf-8 -*-
"""Figure plates for the neural-marker feasibility audit."""
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D
from scipy import ndimage

import journal_style as J
from matplotlib.colors import LinearSegmentedColormap
NEU_CMAP = LinearSegmentedColormap.from_list(
    "neu", ["#F4F4F2", "#E1EAF1", "#C3D7E6", "#9BB9D1", "#6A94B4", "#3C6889", "#22455E"])

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "data" / "spatial_tables"
FIG = ROOT / "data"
FIG.mkdir(exist_ok=True)

SECTIONS = ["Knee2", "Knee3"]
COL = {"Knee2": J.HEALTHY, "Knee3": J.OA}
PITCH = 50.0

# Plate 1 ships from identical code in three places: as Figure S6 on the
# standalone assessment page, as the "Figure 5 - continued" manuscript copy,
# and as the LOWER BLOCK (L-O) of the redrawn journal-format Figure 5.
# Everything that differs is an environment override; with no variables set the
# output is byte-for-byte the original Figure S6.  Example:
#   PLATE1_NUMBER="Figure S10" PLATE1_STEM=FigureS10_neural_marker python 05_figures.py
# Lower block of the 180 x 240 mm journal page (no second header/footer):
#   PLATE1_ONLY=1 PLATE1_HEADER=0 PLATE1_FOOTER=0 PLATE1_TAGS=LMNO \
#   PLATE1_HEIGHT=92 PLATE1_TOP=0.80 PLATE1_CELL_H=0.575 \
#   PLATE1_STEM=Figure5_lower_LO PLATE1_STRICT=1 python 05_figures.py
P1_NUMBER = os.environ.get("PLATE1_NUMBER", "Figure S6")
P1_STEM = os.environ.get("PLATE1_STEM", "FigureS6_neural_feasibility")
P1_TAGS = os.environ.get("PLATE1_TAGS", "ABCD")
P1_HEADER = os.environ.get("PLATE1_HEADER", "1") != "0"
P1_FOOTER = os.environ.get("PLATE1_FOOTER", "1") != "0"
P1_ONLY = os.environ.get("PLATE1_ONLY", "0") == "1"
P1_STRICT = os.environ.get("PLATE1_STRICT", "0") == "1"
P1_H = float(os.environ.get("PLATE1_HEIGHT", "102.0"))
P1_TOP = float(os.environ.get("PLATE1_TOP", "0.720"))
P1_CELL_H = float(os.environ.get("PLATE1_CELL_H", "0.500"))
P1_TITLE = os.environ.get(
    "PLATE1_TITLE",
    "The full-transcriptome release can be joined to the domain, but cannot resolve nerve fibres")
P1_SUBTITLE = os.environ.get(
    "PLATE1_SUBTITLE",
    "Stereo-Seq bin50, same two OA sections as Figure 5; 24,774 and 33,049 bins, all barcodes matched")
assert len(P1_TAGS) == 4, "PLATE1_TAGS must be exactly four letters"

NEU = ["TUBB3", "NEFL", "NEFM", "NEFH", "SNAP25", "SYT1", "UCHL1", "PRPH",
       "RTN1", "SNCG", "GAP43", "STMN2", "NCS1", "SYN1", "SYP"]
SHEATH = ["PLP1", "MPZ", "MBP", "MAG", "EGR2", "SOX10"]

S = pd.read_csv(TAB / "S_scale_sweep.csv")
T = pd.read_csv(TAB / "T_continuous_alignment.csv")
V = pd.read_csv(TAB / "V_two_sided.csv")
CI = pd.read_csv(TAB / "V_domain_ci.csv")   # per-panel shift-null spread (05c)
W = pd.read_csv(TAB / "W_depth_stratified.csv")
WM = pd.read_csv(TAB / "W_depth_matched_summary.csv")
A = pd.read_csv(TAB / "A_section_summary.csv")

G = pd.read_csv(TAB / "D_gene_level.csv")


def _r(sample, panel, sigma=50.0):
    d = S[(S["sample"] == sample) & (S["panel"] == panel) & (S["sigma_um"] == sigma)]
    return float(d.ratio.iloc[0]) if not d.empty else float("nan")


def _v(sample, panel):
    d = V[(V["sample"] == sample) & (V["panel"] == panel)]
    return float(d.ratio.iloc[0]) if not d.empty else float("nan")


def _w(sample, panel="NEU_all"):
    d = WM[(WM["sample"] == sample) & (WM["panel"] == panel)]
    return float(d.pooled_ratio.iloc[0]) if not d.empty else float("nan")


K3_NEU_MAX = float(S[(S["sample"] == "Knee3") &
                      (S["panel"].isin(["NEU_all", "NEU_strict"]))].ratio.max())


def pstr(p):
    if p < 0.001:
        return "P < 0.001"
    return f"P = {p:.3f}"


# ===================================================================== plate 1
# Layout: all four panels in a single row -- A | B | C | D.  A is a 21-gene bar
# chart and therefore sets the plate height; B and C are near-square maps that
# hang from the common top edge; D is the domain contrast turned upright so it
# can live in a ~29 mm column.  Cells are deliberately unequal: A needs a wide
# plotting area to carry five log ticks, D needs a label column for three
# panels, and B/C are square so extra width would only add whitespace.
PLATE_H = P1_H
fig = J.plate(J.W2, PLATE_H)
if P1_HEADER:
    J.header(fig, P1_NUMBER, P1_TITLE, P1_SUBTITLE)

TOP, CELL_H = P1_TOP, P1_CELL_H     # shared top edge and slot height
A_X, A_LAB, A_W = 0.030, 0.070, 0.230   # cell origin, tick-label band, cell width
B_X, BC_W = 0.282, 0.176
C_X = 0.480
D_X, D_LAB, D_W = 0.678, 0.068, 0.292   # D is the widest cell: a horizontal
                                        # forest plot needs x, not y

# ---------------- A. transcript budget
axA = fig.add_axes([A_X + A_LAB, TOP - CELL_H, A_W - A_LAB, CELL_H])
bud = (G[G["sample"] == "Knee2"]
       .assign(total=lambda x: x.inside_counts + x.outside_counts)
       .sort_values("total", ascending=True))
bud = bud[bud.total > 0]
y = np.arange(len(bud))
cols = [J.PLUM if g in SHEATH else "#5A87A8" for g in bud.gene]
axA.barh(y, bud.total, height=0.70, color=cols, edgecolor="none")
axA.set_yticks(y)
axA.set_yticklabels(bud.gene, fontsize=5.6, fontstyle="italic")
axA.set_xscale("log")
axA.set_xlim(1, 3e4)
# explicit ticks: the default log locator also emits 10^-1 / 10^5, which on a
# panel this narrow land outside the axes and trip the layout check
axA.set_xticks([1, 10, 100, 1000])
axA.set_xticklabels(["1", "10", "100", "1,000"])
axA.minorticks_off()
axA.set_xlabel("Transcripts per section", labelpad=2.0)
J.style_axis(axA)
axA.legend(handles=[Patch(facecolor="#5A87A8", edgecolor="none", label="neuronal"),
                    Patch(facecolor=J.PLUM, edgecolor="none", label="myelin sheath")],
           loc="lower right", fontsize=5.6, frameon=False, handlelength=1.0,
           labelspacing=0.30, borderpad=0.12, handletextpad=0.45)
axA.axvline(100, color=J.HAIRLINE, lw=0.6, ls=(0, (3, 2)), zorder=0)

J.tag(fig, axA, P1_TAGS[0], "Neuronal transcripts are rare",
      "0.013% of reads; dashed line = 100 reads", max_mm=28)

# ---------------- B, C. maps, one column each, hanging from the shared top
# Both maps are drawn on ONE colour scale (the larger of the two 99th
# percentiles) so the two sections can be read against each other, and the
# shared bar sits under the pair.  Per-slice scaling would make the two maps
# incomparable at a glance, which is the only thing this pair is for.
maps = []
for s in SECTIONS:
    z = np.load(TAB / f"grid_{s}.npz")
    tot, dom, neu = z["tot"], z["dom"], z["neu"]
    st = ndimage.gaussian_filter(tot, 3.0, mode="constant")
    rate = np.divide(ndimage.gaussian_filter(neu, 3.0, mode="constant"), st,
                     out=np.zeros_like(st), where=st > 0) * 1e6
    footprint = ndimage.binary_fill_holes(
        ndimage.binary_closing(tot > 0, np.ones((3, 3)), iterations=2))
    show = np.where(footprint, rate, np.nan)
    maps.append(dict(s=s, show=show, dom=dom, neu=neu, tot=tot,
                     aspect=tot.shape[0] / tot.shape[1],
                     vmax=float(np.nanpercentile(show, 99))))
VMAX = max(m["vmax"] for m in maps)

axBC = []
for k, m in enumerate(maps):
    # equal_rect keeps the top edge and shrinks the height to the tissue's true
    # aspect, so the map is neither letterboxed nor stretched
    rect = J.equal_rect(fig, [(B_X, C_X)[k], TOP - CELL_H, BC_W, CELL_H], m["aspect"])
    ax = fig.add_axes(rect)
    im = ax.imshow(m["show"], cmap=NEU_CMAP, vmin=0, vmax=VMAX, origin="upper",
                   interpolation="nearest")
    dsmooth = ndimage.gaussian_filter(m["dom"], 1.6, mode="constant")
    ax.contour(dsmooth, levels=[0.45], colors=[J.ACCENT], linewidths=0.6)
    ax.set_xticks([])
    ax.set_yticks([])
    J.no_frame(ax)
    axBC.append(ax)
    J.tag(fig, ax, P1_TAGS[1 + k], m["s"],
          f"{np.sum(m['neu'])/np.sum(m['tot'])*1e6:.0f} per 10$^6$ reads; red = NR-FB domain",
          max_mm=34)

# one colour bar under the pair, spanning B's left edge to C's right edge.
# Centred in the slack under the square maps: hugging the maps leaves a 10 mm
# void at the panel foot, which reads as something missing rather than margin.
bbB, bbC = axBC[0].get_position(), axBC[1].get_position()
cb_y = (min(bbB.y0, bbC.y0) + (TOP - CELL_H)) / 2 - 0.020
cax = fig.add_axes([bbB.x0, cb_y, bbC.x1 - bbB.x0, 0.010])
cb = fig.colorbar(im, cax=cax, orientation="horizontal")
cb.outline.set_visible(False)
cb.ax.tick_params(length=2.0, width=0.5, labelsize=6.0, pad=1.5, colors=J.RULE)
for t in cb.ax.get_xticklabels():
    t.set_color(J.INK)
fig.text(bbB.x0, cb_y + 0.016, "Neural transcripts per 10$^6$ reads",
         fontsize=6.0, color=J.INK, va="bottom", ha="left")

# ---------------- D. domain contrast, horizontal
# Same numbers as before: ratio with the 95% interval implied by that panel's
# own toroidal-shift null (tables/V_domain_ci.csv), interval built on the log
# scale.  Rotated back to horizontal now that D owns the widest cell (52 mm):
# a forest plot reads along x, so width is what it needs, and the six rows have
# 4.7 mm of pitch each -- enough that the value labels sit clear of every bar.
# A 40 mm plot still cannot carry a second legend, so significance stays on the
# asterisks next to the values and every marker is filled.
axD = fig.add_axes([D_X + D_LAB, TOP - CELL_H, D_W - D_LAB, CELL_H])
panels = [("NEU_all", "Neural 15"), ("NEU_strict", "Neural 12"), ("sheath", "Sheath 6")]
ypos, ylab = [], []
yy = 5.0
for key, plabel in panels:
    for s in SECTIONS:
        r = CI[(CI["sample"] == s) & (CI["panel"] == key)].iloc[0]
        sig = r.p_two_sided < 0.05
        c = COL[s]
        axD.plot([r.ci_lo, r.ci_hi], [yy, yy], color=c, lw=1.1,
                 solid_capstyle="butt", zorder=2)
        for xx in (r.ci_lo, r.ci_hi):
            axD.plot([xx, xx], [yy - 0.26, yy + 0.26], color=c, lw=1.1,
                     solid_capstyle="butt", zorder=2)
        axD.plot([r.ratio], [yy], marker="o", ms=4.2, color=c, mew=0.9, zorder=4)
        star = "**" if r.p_two_sided < 0.001 else ("*" if sig else "")
        # right-aligned value column: hanging the number off each interval end
        # pushes the sparse panels' labels (CI to 2.05) far from their markers,
        # which reads as a detached number rather than that row's estimate
        axD.text(2.38, yy, f"{r.ratio:.2f}{star}", va="center", ha="right",
                 fontsize=5.6, color=c, fontweight="bold" if sig else "normal", zorder=5)
        yy -= 1.0
    ypos.append(yy + 1.5)          # centre of the pair
    ylab.append(plabel)
    yy -= 0.35                     # gap between groups

axD.axvline(1.0, color=J.HAIRLINE, lw=0.7, ls=(0, (4, 2)), zorder=0)
axD.set_yticks(ypos)
axD.set_yticklabels(ylab, fontsize=5.9)
axD.set_ylim(yy + 0.45, 6.25)
axD.set_xlim(0.10, 2.47)
axD.set_xticks([0.5, 1.0, 1.5, 2.0])
axD.set_xlabel("Inside / outside the domain (95% CI)", labelpad=2.0)
J.style_axis(axD)
# colour key only, in the band kept free above the top row: the right-hand side
# is now the value column, so the legend cannot live there
hSec = [Line2D([], [], marker="o", ls="", ms=3.8, color=COL[s], mfc=COL[s],
               mew=0.9, label=s) for s in SECTIONS]
lg = axD.legend(handles=hSec, loc="upper right", ncol=2, frameon=False,
                fontsize=6.0, handletextpad=0.5, borderpad=0.10, columnspacing=1.6)
for t in lg.get_texts():
    t.set_color(J.INK)
J.tag(fig, axD, P1_TAGS[3], "Knee2 shifts up, Knee3 does not",
      "95% CI from each panel's own shift null; * P<0.05, ** P<0.001", max_mm=44)


if P1_FOOTER:
    J.footer(
        fig,
        "Analysis unit: tissue section (n = 2, both OA); bins are observations, not replicates. "
        "Contrast = rate of panel transcripts per 10$^6$ reads inside the Figure 5 domain divided by the rate outside, "
        "against a toroidal-shift null that keeps the domain geometry and the neural field intact. "
        "Intervals in D are that null's own spread on the ratio (log scale), so sparse panels widen rather than borrow a width. "
        "Does not support: a neural niche for the NR-FB domain, or PCDH9-positive cells contacting nerve fibres.",
        y=0.008)
J.save(fig, FIG, P1_STEM, strict=P1_STRICT)

if P1_ONLY:
    # The journal-format lower block is assembled into a larger page, so plate 2
    # (Figure S7) must not be re-rendered or touched by this run.
    print("done (plate 1 only)")
    raise SystemExit(0)

# ===================================================================== plate 2
fig2 = J.plate(J.W2, 120.0)
J.header(fig2, "Figure S7",
         "What the contrast does and does not survive",
         "Depth matching, smoothing scale, and a circularity check on the NR-FB definition")

# ---------------- E. depth stratified
axE = fig2.add_axes([0.072, 0.250, 0.195, 0.545])
for j, s in enumerate(SECTIONS):
    d = W[(W["sample"] == s) & (W["panel"] == "NEU_all")]
    axE.plot(d.depth_quintile + (j - 0.5) * 0.13, d.ratio, marker="o", ms=3.4,
             lw=0.9, color=COL[s], mfc="white" if j == 0 else COL[s], mew=0.8,
             label=s)
axE.axhline(1.0, color=J.HAIRLINE, lw=0.7, ls=(0, (4, 2)), zorder=0)
axE.set_xticks([1, 2, 3, 4, 5])
axE.set_xlim(0.6, 5.4)
axE.set_ylim(0.65, 1.80)
axE.set_xlabel("Depth quintile", labelpad=2.0)
axE.set_ylabel("Inside / outside", labelpad=2.5)
J.style_axis(axE)
J.strip_legend(axE, [(s, COL[s]) for s in SECTIONS], loc="upper left")
J.tag(fig2, axE, "E", "Depth matching halves the Knee2 shift",
      f"{_v('Knee2','NEU_all'):.2f}\u00d7 crude \u2192 {_w('Knee2'):.2f}\u00d7 after weighting",
      max_mm=44)

# ---------------- F. scale sweep
axF = fig2.add_axes([0.355, 0.250, 0.215, 0.545])
for s in SECTIONS:
    for key, ls, mk in [("NEU_all", "-", "o"), ("sheath", "--", "s")]:
        d = S[(S["sample"] == s) & (S["panel"] == key)].sort_values("sigma_um")
        axF.plot(d.sigma_um, d.ratio, ls=ls, marker=mk, ms=2.6, lw=0.9,
                 color=COL[s], mfc="white", mew=0.7)
axF.axhline(1.0, color=J.HAIRLINE, lw=0.7, ls=(0, (4, 2)), zorder=0)
axF.set_xscale("log")
axF.set_xticks([50, 100, 200, 300])
axF.set_xticklabels(["50", "100", "200", "300"])
axF.minorticks_off()
axF.xaxis.get_offset_text().set_visible(False)
axF.set_xlim(45, 340)
axF.set_ylim(0.55, 1.48)
axF.set_xlabel("Smoothing kernel (\u00b5m)", labelpad=2.0)
axF.set_ylabel("Inside / outside", labelpad=2.5)
J.style_axis(axF)
h = [Line2D([], [], color=J.INK, lw=0.9, ls="-", label="neural, 15"),
     Line2D([], [], color=J.INK, lw=0.9, ls="--", label="sheath, 6"),
     Line2D([], [], color=J.HEALTHY, lw=1.1, label="Knee2"),
     Line2D([], [], color=J.OA, lw=1.1, label="Knee3")]
leg = axF.legend(handles=h, loc="upper right", ncol=1, fontsize=5.6,
                 frameon=False, handlelength=1.5, labelspacing=0.28,
                 borderpad=0.10, handletextpad=0.5)
for t_ in leg.get_texts():
    t_.set_color(J.INK)
J.tag(fig2, axF, "F", "Widening the kernel does not rescue it",
      f"No scale puts Knee3 above {K3_NEU_MAX:.2f}", max_mm=44)

# ---------------- G. circularity
axG = fig2.add_axes([0.690, 0.250, 0.290, 0.545])
rows_g = [("NRFB_core", "NR-FB\ncore 20", True),
          ("NRFB_output", "NR-FB\noutput 32", True),
          ("NEU_strict", "Neural\n12", False),
          ("sheath", "Sheath\n6", False)]
xg = np.arange(len(rows_g))
for j, s in enumerate(SECTIONS):
    vals = []
    for key, _, circ in rows_g:
        d = S[(S["sample"] == s) & (S["panel"] == key) & (S["sigma_um"] == 50.0)]
        vals.append(float(d.ratio.iloc[0]) if not d.empty else np.nan)
    off = -0.19 if j == 0 else 0.19
    axG.bar(xg + off, np.array(vals) - 1.0, bottom=1.0, width=0.34,
            color=[COL[s] if not c else "white" for _, _, c in rows_g],
            edgecolor=COL[s], linewidth=0.75,
            hatch=[None if not c else "////" for _, _, c in rows_g])
    for i, v in enumerate(vals):
        if np.isnan(v):
            continue
        if v >= 1.0:
            axG.text(i + off, v + 0.05, f"{v:.2f}", ha="center", va="bottom",
                     fontsize=5.5, color=COL[s])
        else:
            axG.text(i + off, v - 0.05, f"{v:.2f}", ha="center", va="top",
                     fontsize=5.5, color=COL[s])
axG.axhline(1.0, color=J.RULE, lw=0.6)
axG.set_xticks(xg)
axG.set_xticklabels([r[1] for r in rows_g], fontsize=5.8, linespacing=1.25)
axG.set_xlim(-0.6, len(rows_g) - 0.4)
axG.set_ylim(0.5, 2.65)
axG.set_ylabel("Inside / outside", labelpad=2.5)
J.style_axis(axG)
axG.text(-0.55, 2.62, "hatched = genes are part of the NR-FB definition",
         fontsize=5.5, color=J.MUTED, ha="left", va="top")
J.tag(fig2, axG, "G", "The strong ratios are the circular ones",
      f"Core {_r('Knee2','NRFB_core'):.2f} / {_r('Knee3','NRFB_core'):.2f}\u00d7; "
      f"output {_r('Knee2','NRFB_output'):.2f} / {_r('Knee3','NRFB_output'):.2f}\u00d7",
      max_mm=60)

J.footer(
    fig2,
    "Analysis unit: tissue section (n = 2). Depth quintiles are within section. "
    "Hatched rows use genes that are part of the NR-FB definition itself (core programme 20 genes, of which DCLK1, SCG2, NTNG1 and TUBB2B are neural; "
    "output programme 32 genes, all neurotrophic or axon-guidance), so their enrichment restates the definition rather than testing it. "
    "Does not support: treating the core or output enrichment as evidence that the domain sits near nerves.",
    y=0.010)
J.save(fig2, FIG, "FigureS7_neural_limits", strict=False)

print("done")
