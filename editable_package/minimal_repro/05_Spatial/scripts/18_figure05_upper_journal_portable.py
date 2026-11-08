# -*- coding: utf-8 -*-
"""Upper half (panels A-K) of the journal-format Figure 5.

Redrawn from the ORIGINAL spot tables in sources/figure5/source, not scaled
from the 427 mm legacy PNG.  Scaling that PNG to 180 mm leaves its 8-10 pt
labels at ~4 pt, below the 5.6 pt print floor.  Here every label is typeset
again at the journal hierarchy (9.2 / 7.3 / 7.0 / 6.4 / 6.3 / 6.2 pt).

Panel letters are continuous with the lower half: A-C = NR-FB region,
D-F = PCDH9 expression, G-I = same-spot merge, J/K = the two summary bars.
The lower half continues at L-O (see 05_figures.py with PLATE1_TAGS=LMNO).

Colour scheme E (teal + magenta) is kept, as specified for this figure; the
deviation from the package's 8-colour board is recorded in the reproduction
note.  All numbers are moved OUT of the image into the legend table.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.cm import ScalarMappable
from matplotlib.colors import ListedColormap, Normalize
from matplotlib.lines import Line2D

import journal_style as J

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "data" / "figure5_source"
OUT = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 180.0, 113.0                 # mm; upper block of the 180 x 240 page
TEAL, PLUM = "#277F8E", "#8E2B83"  # specified palette E
VMAX = json.loads((S / "colour_limits.json").read_text())["PCDH9_limits"][1]
CMAP = ListedColormap(plt.get_cmap("magma_r")(np.linspace(0.06, 0.94, 256)))
MERGE_BG = "#080B10"
MERGE_COL = ["#242A32", "#00DCE5", "#F34ACB", "#FFFFFF"]
SAMPLES = [("Knee2", "highPPSD"), ("Knee3", "low-PPSD"), ("A4", "control")]
BAR = pd.read_csv(S / "seven_section_summary.csv")

fig = J.plate(W, H)


def R(x, y, w, h):
    """mm -> figure coordinates."""
    return [x / W, y / H, w / W, h / H]


COLS = [13.0, 45.0, 77.0]          # three spatial columns
ROWS = [71.0, 36.0, 1.0]           # three rows, bottom edges
CW, CH = 30.0, 30.5                # cell size, mm
RX, RW = 111.0, 67.0               # legend / bar column

# ---- column headers -------------------------------------------------------
for x, (_, label) in zip(COLS, SAMPLES):
    fig.text((x + CW / 2) / W, 109.5 / H, label, ha="center", va="center",
             fontsize=7.3, fontweight="bold", color=J.INK)
fig.text((RX + RW / 2) / W, 109.5 / H, "Legend / OA vs Control",
         ha="center", va="center", fontsize=7.3, fontweight="bold", color=J.INK)

# ---- row labels ------------------------------------------------------------
for y, lab in zip(ROWS, ["NR-FB region", "PCDH9 expression", "Same-spot merge"]):
    fig.text(6.0 / W, (y + CH / 2) / H, lab, rotation=90, ha="center",
             va="center", fontsize=7.3, color=J.INK)

# ---- nine spatial panels ---------------------------------------------------
LETTERS = "ABCDEFGHI"
for r, ry in enumerate(ROWS):
    for c, (orig, _) in enumerate(SAMPLES):
        x = COLS[c]
        fig.text((x + 0.4) / W, (ry + CH + 0.7) / H, LETTERS[r * 3 + c],
                 ha="left", va="bottom", fontsize=9.2, fontweight="bold",
                 color=J.INK)

        d = pd.read_csv(S / f"{orig}_CD_units.csv.gz")
        xx, yy = d.x.to_numpy(), -d.y.to_numpy()
        bg = "#E5E5E5" if orig.startswith("Knee") else "#EEEEEE"
        ax = fig.add_axes(R(x, ry, CW, CH))
        ax.set_aspect("equal", adjustable="datalim")
        ax.margins(0.02)

        if r == 0:
            ax.scatter(xx, yy, c=np.where(d.domain == 1, TEAL, bg),
                       s=0.8, linewidths=0)
        elif r == 1:
            ax.scatter(xx, yy, c=bg, s=0.55, linewidths=0)
            ix = np.argsort(d.PCDH9_log1pCPM.to_numpy(), kind="stable")
            ix = ix[d.PCDH9_counts.to_numpy()[ix] > 0]
            ax.scatter(xx[ix], yy[ix],
                       c=d.PCDH9_log1pCPM.to_numpy()[ix], cmap=CMAP,
                       vmin=0, vmax=VMAX, s=1.0, linewidths=0)
        else:
            ax.set_facecolor(MERGE_BG)
            region = d.domain.to_numpy() == 1
            pos = d.PCDH9_counts.to_numpy() > 0
            cat = region.astype(int) + 2 * pos.astype(int)
            for k, col in enumerate(MERGE_COL):
                m = cat == k
                ax.scatter(xx[m], yy[m], c=col, s=0.8, linewidths=0)
        J.no_frame(ax)

# ---- legend ----------------------------------------------------------------
# 2 x 2 legend: four keys in one vertical column leaves no room for the colour
# bar's tick labels, the J/K captions and two rows of x-axis labels.
LEG = [("Neither", "#242A32", 113.0, 100.5),
       ("NR-FB region only", "#00DCE5", 145.0, 100.5),
       ("PCDH9+ only", "#F34ACB", 113.0, 96.5),
       ("Both (same spot)", "#FFFFFF", 145.0, 96.5)]
for lab, col, x, y in LEG:
    yy = y / H
    # a single point: two endpoints would draw two markers per key
    fig.add_artist(Line2D([x / W], [yy],
                          transform=fig.transFigure, ls="", marker="o",
                          ms=4.0, mfc=col, mec="#637080", mew=0.6))
    fig.text((x + 5.0) / W, yy, lab, va="center", fontsize=6.4, color=J.INK)

# ---- shared colour scale ---------------------------------------------------
cax = fig.add_axes(R(113, 86.5, 63, 2.0))
cb = fig.colorbar(ScalarMappable(norm=Normalize(0, VMAX), cmap=CMAP),
                  cax=cax, orientation="horizontal")
cb.outline.set_visible(False)
cb.set_ticks([0, 3, 6, 9])
cb.ax.tick_params(labelsize=6.2, length=2.0, width=0.5, pad=1.0, colors=J.RULE)
for t in cb.ax.get_xticklabels():
    t.set_color(J.INK)
fig.text(113 / W, 91.0 / H, "PCDH9 log1p(CPM), common scale for D-F",
         fontsize=6.2, color=J.MUTED, va="bottom")

# ---- J / K summary bars ----------------------------------------------------

def bars(y0, h, letter_y, letter, key, color, title):
    fig.text((RX + 0.4) / W, letter_y / H, letter, ha="left", va="bottom",
             fontsize=9.2, fontweight="bold", color=J.INK)
    fig.text((RX + 6.0) / W, letter_y / H, title, ha="left", va="bottom",
             fontsize=7.3, color=J.INK)
    ax = fig.add_axes(R(RX + 2.0, y0, RW - 4.0, h))
    means, sds, vals = [], [], []
    for g in ("Healthy", "OA"):
        v = BAR.loc[BAR.group == g, key].to_numpy(dtype=float)
        means.append(v.mean())
        sds.append(v.std(ddof=1))
        vals.append(v)
    ax.bar([0, 1], means, color=color, alpha=0.85, width=0.56, zorder=2)
    ax.errorbar([0, 1], means, yerr=sds, fmt="none", ecolor=J.INK,
                elinewidth=0.7, capsize=2.4, capthick=0.7, zorder=3)
    for i, v in enumerate(vals):
        ax.scatter(i + np.linspace(-0.13, 0.13, len(v)), v, s=5.5,
                   c="white", edgecolors=J.INK, linewidths=0.6, zorder=4)
        ax.text(i, means[i] + sds[i] + 1.1, f"{means[i]:.2f}%",
                ha="center", va="bottom", fontsize=6.3, color=J.INK)
    ax.set_ylim(0, max(m + s for m, s in zip(means, sds)) * 1.28)
    ax.set_xlim(-0.6, 1.6)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Control\n(n = 5)", "OA\n(n = 2)"], fontsize=6.4)
    ax.set_ylabel("Positive spots (%)", fontsize=7.0)
    ax.tick_params(axis="x", length=0)
    J.style_axis(ax)
    return ax


bars(47.0, 27.0, 78.0, "J", "PCDH9_positive_percent", PLUM,
     "PCDH9+ among all spots")
bars(8.0, 25.0, 35.5, "K", "PCDH9_positive_within_region_percent", TEAL,
     "PCDH9+ within the NR-FB region")

problems = J.check_layout(fig)
print(f"layout check: {len(problems)} problem(s)")
for p in problems[:20]:
    print("  -", p)

J.save(fig, OUT, "Figure5_upper_AK", strict=True)
