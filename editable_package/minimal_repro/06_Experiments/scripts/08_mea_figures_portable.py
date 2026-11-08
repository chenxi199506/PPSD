# -*- coding: utf-8 -*-
"""
实验 A —— Figure（A–E）绘制
A 实验设计示意 | B 平均放电频率 | C 爆发频率 | D 网络活动 | E 患者级可重复性
输出：04_图表/Figure5_MEA_A-E.pdf / .png
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
PROC, RES, FIG = (ROOT / "data" / "MEA_02_处理后数据",
                  ROOT / "data" / "MEA_03_统计结果", ROOT / "output")
FIG.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "Arial", "font.size": 7.2,
    "axes.linewidth": 0.7, "xtick.major.width": 0.7, "ytick.major.width": 0.7,
    "xtick.major.size": 2.6, "ytick.major.size": 2.6,
    "xtick.direction": "out", "ytick.direction": "out",
    "axes.spines.top": False, "axes.spines.right": False,
    "pdf.fonttype": 42, "ps.fonttype": 42, "savefig.dpi": 600,
})

C = {"G1": "#2E5C8A", "G2": "#B03A2E", "G3": "#2E8B8B", "G4": "#9AA5B1", "G5": "#8FB8DE"}
LAB = {"G1": "NT-CM", "G2": "PCDH9-KD-CM", "G3": "Rescue-CM", "G4": "Vehicle", "G5": "Mock-CM"}
SHORT = {"G1": "NT", "G2": "KD", "G3": "RES", "G4": "Veh", "G5": "Mock"}
ORDER = ["G1", "G2", "G3", "G4", "G5"]
XPOS = {"G1": 0.0, "G2": 1.0, "G3": 2.0, "G4": 3.0, "G5": 4.15}

wells = pd.read_csv(PROC / "MEA_孔级_清洗后.csv", encoding="utf-8-sig")
wells = wells[wells.Included]
donor = pd.read_csv(PROC / "MEA_供体级均值.csv", encoding="utf-8-sig")
lmm = pd.read_csv(RES / "主要终点_LMM对比.csv", encoding="utf-8-sig")
veh = pd.read_csv(RES / "基质对照_G1vsG4.csv", encoding="utf-8-sig")


def p_any(metric, a, b):
    if "G4" in (a, b):
        s = veh[veh.Metric == metric]
        return float(s.p_Welch.iloc[0]) if len(s) else np.nan
    s = lmm[(lmm.Metric == metric) & (lmm.Comparison == f"{a} vs {b}")]
    return float(s.p_raw.iloc[0]) if len(s) else np.nan


def stars(p):
    if p != p:
        return ""
    return "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"


def panel_metric(ax, metric, ylab, comps, jitter=0.055, ylim=None, short=False,
                 lab_size=6.6, rot=28):
    means = wells.groupby("Group", observed=True)[metric].mean()
    sems = wells.groupby("Group", observed=True)[metric].sem()
    rng = np.random.default_rng(11)
    for g in ORDER:
        x = XPOS[g]
        ax.bar(x, means[g], width=0.62, color=C[g], alpha=0.28,
               edgecolor=C[g], linewidth=0.8, zorder=1)
        ax.errorbar(x, means[g], yerr=sems[g], fmt="none", ecolor=C[g],
                    elinewidth=0.9, capsize=2.2, capthick=0.9, zorder=4)
        v = wells[wells.Group == g][metric].dropna().values
        ax.scatter(x + rng.normal(0, jitter, len(v)), v, s=5.0, color=C[g],
                   alpha=0.60, linewidths=0, zorder=2)

    ax.set_xticks([XPOS[g] for g in ORDER])
    labels = [SHORT[g] if short else LAB[g] for g in ORDER]
    ax.set_xticklabels(labels, rotation=rot, ha="right" if rot < 90 else "center",
                       fontsize=lab_size)
    ax.set_ylabel(ylab, fontsize=7.2)
    ax.set_xlim(-0.72, 4.88)
    if ylim:
        ax.set_ylim(*ylim)

    # 显著性括号：起点取"被比较两组中实测最大值"与"柱顶+误差"的较大者，
    # 保证括号始终位于所有散点之上（而非穿过散点），再逐层上移
    y0, y1 = ax.get_ylim()
    span = y1 - y0
    top_used = -np.inf
    for a, b in comps:
        p = p_any(metric, a, b)
        vmax = max(wells.loc[wells.Group == a, metric].max(),
                   wells.loc[wells.Group == b, metric].max())
        base = max(means[a] + sems[a], means[b] + sems[b], float(vmax))
        y = max(base + span * 0.055, top_used + span * 0.105)
        x1, x2 = XPOS[a], XPOS[b]
        ax.plot([x1, x1, x2, x2], [y - span * 0.020, y, y, y - span * 0.020],
                color="#3A3A3A", linewidth=0.6, clip_on=False, zorder=5)
        ax.text((x1 + x2) / 2, y + span * 0.010, stars(p), ha="center", va="bottom",
                fontsize=6.6, color="#3A3A3A", zorder=6)
        top_used = y
    ax.set_ylim(y0, max(y1, top_used + span * 0.085))


# ================================================================== 画布
fig = plt.figure(figsize=(7.3, 7.15))
gs = GridSpec(3, 6, figure=fig, height_ratios=[0.74, 1.02, 1.02],
              hspace=0.58, wspace=1.55, left=0.075, right=0.975, top=0.975, bottom=0.070)

# ---------------------------------------------------------------- A 设计示意
axA = fig.add_subplot(gs[0, :])
axA.axis("off")
axA.set_xlim(0, 10)
axA.set_ylim(0, 2.42)


def box(x, y, w, h, title, sub=""):
    axA.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.07",
                                 linewidth=0.7, edgecolor="#4A4A4A", facecolor="#F7F8FA",
                                 zorder=2))
    axA.text(x + w / 2, y + h * (0.70 if sub else 0.5), title, ha="center", va="center",
             fontsize=6.3, color="#1A1A1A", fontweight="bold", zorder=3, linespacing=1.25)
    if sub:
        axA.text(x + w / 2, y + h * 0.29, sub, ha="center", va="center",
                 fontsize=5.3, color="#3C3C3C", zorder=3, linespacing=1.40)


def arrow(x1, y1, x2, y2):
    axA.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                  mutation_scale=6.5, linewidth=0.7, color="#6B6B6B",
                                  shrinkA=0, shrinkB=0, zorder=1))


BY, BH = 0.80, 0.90
boxes = [
    (0.05, 1.45, "OA synovium", "5 donors\n(independent)"),
    (1.67, 1.55, "Primary synovial\nfibroblasts", "P2–P3, 6-well"),
    (3.39, 1.95, "Four fibroblast states",
     "1) NT siRNA\n2) PCDH9 siRNA\n3) PCDH9 siRNA + Rescue\n4) Mock (reagent only)"),
    (5.51, 1.65, "Conditioned medium", "24 h, 1:1 dilution\nper donor"),
    (7.33, 1.50, "Sensory neurons", "human iPSC-derived\n2 lots / 2 plates"),
    (9.00, 0.95, "MEA", "48-well\n16 elec./well"),
]
for x, w, t, s in boxes:
    h = 1.24 if "states" in t else BH
    box(x, BY - (h - BH) / 2, w, h, t, s)
for x, w, t, s in boxes[:-1]:
    arrow(x + w + 0.005, BY + 0.02, x + w + 0.155, BY + 0.02)

axA.text(0.05, 2.26, "A  Experimental design", fontsize=8, fontweight="bold")
axA.text(0.05, 1.99,
         "5 donors × 4 CM × 4 wells + 4 vehicle wells/plate = 88 wells "
         "(2 × 48-well MEA plates, randomized)", fontsize=5.9, color="#333333")
axA.text(0.05, 0.14,
         "Recording: 10 min spontaneous activity (baseline) → 25 mM KCl 5 min (evoked).  "
         "Readouts: MFR, bursts, network bursts, active electrodes, ISI.  Donor = random effect.",
         fontsize=5.7, color="#555555")

# ---------------------------------------------------------------- B MFR
axB = fig.add_subplot(gs[1, 0:2])
panel_metric(axB, "MeanFiringRate_Hz", "Mean firing rate (Hz)",
             [("G2", "G1"), ("G3", "G2"), ("G1", "G4")])
axB.set_title("B  Mean firing rate", fontsize=8, fontweight="bold", loc="left", pad=6)
axB.text(0.995, 1.012, "primary endpoint", transform=axB.transAxes,
         fontsize=5.5, color="#777777", va="bottom", ha="right")

# ---------------------------------------------------------------- C burst
axC = fig.add_subplot(gs[1, 2:4])
panel_metric(axC, "BurstFrequency_perMin", "Burst frequency (/min)",
             [("G2", "G1"), ("G3", "G2")])
axC.set_title("C  Burst frequency", fontsize=8, fontweight="bold", loc="left", pad=6)

# ---------------------------------------------------------------- D network
gs_d = gs[1, 4:6].subgridspec(1, 2, wspace=1.05)
axD1 = fig.add_subplot(gs_d[0, 0])
panel_metric(axD1, "NetworkBurstFrequency_perMin", "Network burst (/min)",
             [("G2", "G1")], jitter=0.05, short=True, lab_size=5.6, rot=90)
axD1.set_title("D  Network activity", fontsize=8, fontweight="bold", loc="left", pad=6)
axD2 = fig.add_subplot(gs_d[0, 1])
panel_metric(axD2, "ActiveElectrode_pct", "Active electrodes (%)",
             [("G1", "G4")], jitter=0.05, ylim=(0, 108), short=True, lab_size=5.6, rot=90)

# ---------------------------------------------------------------- E 患者级
gs_e = gs[2, :].subgridspec(1, 3, width_ratios=[1.30, 1.05, 0.80], wspace=0.52)
axE1 = fig.add_subplot(gs_e[0, 0])
axE2 = fig.add_subplot(gs_e[0, 1])
axE3 = fig.add_subplot(gs_e[0, 2])

d = donor[donor.Group.isin(["G1", "G2", "G3"])].pivot_table(
    index="Donor", columns="Group", values="MeanFiringRate_Hz", observed=True)
dn = d.div(d["G1"], axis=0) * 100
donor_cols = ["#2E5C8A", "#B03A2E", "#2E8B8B", "#C9922E", "#6B4C9A"]
for i, (dnr, row) in enumerate(dn.iterrows()):
    axE1.plot([0, 1, 2], row[["G1", "G2", "G3"]].values, "-o", color=donor_cols[i],
              markersize=3.0, linewidth=0.9, alpha=0.9, zorder=3)

# 供体标签：按 y 排序后做最小间距避让，避免数值接近时文字重叠；
# 偏移超过阈值时画一段引线，保证"标签—数据点"对应关系不产生歧义
_lab = sorted([[float(row["G3"]), dnr, donor_cols[i]]
               for i, (dnr, row) in enumerate(dn.iterrows())], key=lambda t: t[0])
_GAP = 3.4
for k in range(1, len(_lab)):
    if _lab[k][0] - _lab[k - 1][0] < _GAP:
        _lab[k][0] = _lab[k - 1][0] + _GAP
for _y, _dnr, _c in _lab:
    _y0 = float(dn.loc[_dnr, "G3"])
    if abs(_y - _y0) > 0.4:
        axE1.plot([2.02, 2.10], [_y0, _y], color=_c, linewidth=0.5, alpha=0.75,
                  zorder=2, solid_capstyle="round")
    axE1.text(2.14, _y, _dnr, fontsize=5.3, va="center", color=_c)
axE1.set_ylim(axE1.get_ylim()[0], max(axE1.get_ylim()[1], 104))
axE1.plot([-0.25, 2.02], [100, 100], color="#999999", linewidth=0.6,
          linestyle=(0, (3, 2)), zorder=1)
axE1.set_xticks([0, 1, 2])
axE1.set_xticklabels(["NT-CM", "KD-CM", "Rescue"], rotation=22, ha="right", fontsize=6.3)
axE1.set_ylabel("% of same donor's NT-CM", fontsize=7)
axE1.set_xlim(-0.25, 2.58)
axE1.set_title("E  Patient-level reproducibility", fontsize=8, fontweight="bold",
               loc="left", pad=6)

eff = pd.read_csv(RES / "供体级效应量与恢复率.csv", encoding="utf-8-sig")
x = np.arange(len(eff))
axE2.bar(x - 0.19, eff.KD_effect_pct, width=0.36, color=C["G2"], alpha=0.88,
         edgecolor="white", linewidth=0.4, label="KD effect")
axE2.bar(x + 0.19, eff.Rescue_recovery_pct, width=0.36, color=C["G3"], alpha=0.88,
         edgecolor="white", linewidth=0.4, label="Rescue recovery")
axE2.axhline(0, color="#555555", linewidth=0.6)
# 纵轴按数据留 12% 余量：个别供体的恢复率可能 >100%，不能按固定上限裁掉
_y_hi = max(float(eff.Rescue_recovery_pct.max()), 100.0)
_y_lo = min(float(eff.KD_effect_pct.min()), 0.0)
axE2.set_ylim(_y_lo * 1.10, _y_hi * 1.14)
axE2.set_xticks(x)
axE2.set_xticklabels(eff.Donor, fontsize=6.3)
axE2.set_ylabel("%", fontsize=7)
axE2.legend(frameon=False, fontsize=5.5, loc="lower left",
            bbox_to_anchor=(0.0, 1.004, 1.0, 0.06), ncol=2,
            handlelength=1.0, handletextpad=0.4, columnspacing=1.0,
            borderaxespad=0.0)
axE2.set_title("per-donor effect", fontsize=6.6, loc="left", pad=18, color="#444444")

for i, dnr in enumerate(eff.Donor):
    axE3.plot([0, 1], [eff.MFR_G1_Hz[i], eff.MFR_G2_Hz[i]], "-o", color=donor_cols[i],
              markersize=2.8, linewidth=0.9)
axE3.set_xticks([0, 1])
axE3.set_xticklabels(["NT-CM", "KD-CM"], rotation=22, ha="right", fontsize=6.3)
axE3.set_ylabel("MFR (Hz)", fontsize=7)
axE3.set_xlim(-0.3, 1.3)
axE3.set_title("paired wells", fontsize=6.6, loc="left", pad=4, color="#444444")

fig.savefig(FIG / "Figure5_MEA_A-E.pdf")
fig.savefig(FIG / "Figure5_MEA_A-E.png", dpi=600)
print("[OK] Figure5_MEA_A-E 已输出")
