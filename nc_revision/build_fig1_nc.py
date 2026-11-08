# -*- coding: utf-8 -*-
"""build_fig1_nc.py — Figure 1（183 x 170 mm，NC 双栏满幅）

第三轮重排。上一版被判"只是把旧 PDF 拷过来"，根因是它自己另起了一套
版面与配色，与 Figure 2 没有共同的度量：

  · 旧版三列绘图框 25–65 / 75–114 / 126–178（宽 40 / 39 / 52，不等宽），
    底行两面板 26–87 / 122–180，接缝与上面三条列线完全错开 —— 上下的
    y 轴自然对不齐。
  · 旧版六模型条图用 TEAL / BROWN / PURPLE，Figure 2 用青蓝 / 金 / 紫，
    两张图都不在同一色系里。

本版改为直接 import nc_style（Figure 2 也用同一份），于是：
  · 绘图框严格落在 COL1 / COL2 / COL3 三条列上，行内三面板等宽 44 mm；
  · 两面板拼幅时接缝取 COL_MID（= 中列中心线 102 mm），左右外沿与第一行
    完全对齐；
  · 六模型颜色走 MODEL_COLORS（蓝族 = 结构，红族 = PPSD，越深 = 越完整）；
  · 森林表改成与 Fig. 2g 同一套三线表参数（顶部粗线 / 表头细线 / 底部粗线、
    点位节距、CI 帽高、OR 数值右对齐到版心右缘）。

面板（字母连续小写）
    a  基线协变量平衡哑铃图            b  随访疼痛负荷（加权小提琴）
    c  随访功能负荷轨迹                d  六模型调整 OR 三线表 + 森林
    e  随访疼痛留出预测                f  随访功能留出预测

原 d（SMD 热条）已移入补充图 Figure S6。
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source")
OUT = os.path.join(HERE, "out")

sys.path.insert(0, os.path.dirname(HERE))          # -> out/，nc_style.py 所在
import nc_style as S                                # noqa: E402

W, H = S.W, S.H
DPI = S.DPI
FS_LETTER = S.FS_LETTER
FS_TICK = S.FS_TICK
FS_AXIS = S.FS_AXIS
FS_CELL = S.FS_CELL
FS_NOTE = S.FS_NOTE
FS_HDR = S.FS_HDR

BLUE, RED = S.BLUE, S.RED
BLUE_LIGHT, BLUE_MID, BLUE_SOFT, BLUE_PALE = (
    S.BLUE_LIGHT, S.BLUE_MID, S.BLUE_SOFT, S.BLUE_PALE)
RED_DARK, RED_PALE = S.RED_DARK, S.RED_PALE
GREY, GREY_SOFT = S.GREY, S.GREY_SOFT
INK, MUTED = S.INK, S.MUTED

plt.rcParams.update(S.rc())


def ax_at(x, y, w, h, **kw):
    """mm -> figure fraction 的 add_axes。x,y 为左下角，原点在页面左下。"""
    return FIG.add_axes([x / W, y / H, w / W, h / H], **kw)


def letter(ax, s):
    S.panel_letter(FIG, ax, s)


# --------------------------------------------------------------- 数据
bal = pd.read_csv(os.path.join(SRC, "balance_values.csv"))
pain = pd.read_csv(os.path.join(SRC, "pain_values.csv"))
traj = pd.read_csv(os.path.join(SRC, "function_trajectory.csv"))
eff = pd.read_csv(os.path.join(SRC, "six_model_effects.csv"))
perf = pd.read_csv(os.path.join(SRC, "performance.csv"))
sig = pd.read_csv(os.path.join(SRC, "significance_tests.csv"), na_values=["NA"])

BAL_ORDER = ["KL 3 proportion", "Age", "BMI", "Female proportion",
             "Medial JSN grades", "Lateral JSN grades",
             "Medial osteophyte grades", "Lateral osteophyte grades",
             "Baseline medial JSW", "Baseline expected pain"]
# 显示名与 Fig. 2a 的协变量名逐字一致（"KL grade" / "Medial JSN" /
# "Lateral osteophyte" / "Female" ...），单位与措辞放进图注。
# 用全名 "Lateral osteophyte grades" 会占 25 mm，把标签顶到画布左缘 0 mm。
BAL_DISPLAY = ["KL grade 3", "Age", "BMI", "Female", "Medial JSN",
               "Lateral JSN", "Medial osteophyte", "Lateral osteophyte",
               "Medial JSW", "Expected pain"]


def balance_pivot():
    b = bal.copy()
    b["order"] = b["label"].map({k: i for i, k in enumerate(BAL_ORDER)})
    assert b["order"].notna().all(), "balance_values.csv 出现未登记标签"
    pre = b[b.stage == "Before weighting"].sort_values("order")
    post = b[b.stage == "Overlap weighted"].sort_values("order")
    assert list(pre.label) == list(post.label)
    return pre, post


# =============================================================== 版面
FIG = plt.figure(figsize=(W / 25.4, H / 25.4), dpi=DPI)

# 行带（mm，自下而上）——三条行的左右边界全部落在 COL1/2/3
#   e/f  10.0-56.0   H 46
#   d    64.0-114.0  H 50
#   a/b/c 124.0-164.0 H 40
Y_EF, H_EF = 10.0, 46.0
Y_D, H_D = 64.0, 50.0
Y_ABC, H_ABC = 124.0, 40.0

# ---------------------------------------------------------------- a
axA = ax_at(S.COL1[0], Y_ABC, S.COL_W, H_ABC)
pre, post = balance_pivot()
yy = np.arange(len(BAL_ORDER))[::-1]
for i in yy:
    axA.plot([pre.value.values[len(BAL_ORDER) - 1 - i],
              post.value.values[len(BAL_ORDER) - 1 - i]], [i, i],
             color=GREY_SOFT, lw=0.5, zorder=1)
axA.scatter(pre.value.values[::-1], yy, s=7.5, color=GREY, zorder=3,
            label="Before weighting", linewidths=0)
axA.scatter(post.value.values[::-1], yy, s=9.0, color=BLUE, zorder=4,
            label="Overlap weighted", linewidths=0)
axA.axvline(0.1, ls=(0, (3, 2)), color=GREY, lw=S.LW_DASH, zorder=0)
axA.set_yticks(yy)
axA.set_yticklabels(BAL_DISPLAY, fontsize=FS_TICK)
axA.set_xlim(-0.03, 1.05)
axA.set_xticks([0, 0.1, 0.5, 1.0])
axA.set_xticklabels(["0", "0.1", "0.5", "1.0"], fontsize=FS_TICK)
axA.set_xlabel("Absolute standardised difference", fontsize=FS_AXIS,
               fontweight="bold", labelpad=1.5)
axA.tick_params(axis="both", pad=1.2)
S.strip_axes(axA)
axA.legend(loc="upper right", fontsize=FS_NOTE, frameon=False, handletextpad=0.4,
           borderpad=0.1, labelspacing=0.25, borderaxespad=0.2, markerscale=1.0)
letter(axA, "a")

# ---------------------------------------------------------------- b
axB = ax_at(S.COL2[0], Y_ABC, S.COL_W, H_ABC)
lo_g, hi_g = "Lower early decile", "Upper early decile"
groups = [lo_g, hi_g]
cols = [BLUE, RED]
rng = np.random.default_rng(20261027)
grid = np.linspace(0.0, 21.0, 220)


def wkde(v, w, g=grid):
    """加权高斯核密度（权重口径与 geom_violin(weight=) 一致）。"""
    w = np.asarray(w, float)
    v = np.asarray(v, float)
    neff = w.sum() ** 2 / (w ** 2).sum()
    mu = (w * v).sum() / w.sum()
    sd = np.sqrt((w * (v - mu) ** 2).sum() / w.sum())
    bw = 1.06 * sd * neff ** (-1.0 / 5.0)
    d = np.exp(-0.5 * ((g[:, None] - v[None, :]) / bw) ** 2)
    return (d * w[None, :]).sum(1) / w.sum()


for k, gname in enumerate(groups):
    d = pain[pain.group == gname]
    dens = wkde(d.future_pain.values, d.weight.values)
    dens = dens / dens.max() * 0.38
    x0 = k + 1
    axB.add_patch(Polygon(np.column_stack([np.r_[x0 - dens, (x0 + dens)[::-1]],
                                          np.r_[grid, grid[::-1]]]),
                          closed=True, facecolor=cols[k], alpha=0.12,
                          edgecolor="none", zorder=1))
    jx = x0 + rng.uniform(-0.11, 0.11, len(d))
    axB.scatter(jx, d.future_pain.values, s=0.9, color=cols[k], alpha=0.55,
                linewidths=0, zorder=2)
    w = d.weight.values
    m = (w * d.future_pain.values).sum() / w.sum()
    ess = w.sum() ** 2 / (w ** 2).sum()
    se = np.sqrt((w ** 2 * (d.future_pain.values - m) ** 2).sum() / w.sum() ** 2)
    axB.errorbar([x0], [m], yerr=[1.96 * se], fmt="none", ecolor=INK,
                 elinewidth=0.7, capsize=1.8, capthick=0.7, zorder=5)
    axB.scatter([x0], [m], marker="D", s=10, facecolor="white",
                edgecolor=INK, linewidths=0.7, zorder=6)
    globals()["ESS_" + ("LO" if k == 0 else "HI")] = ess
    globals()["M_" + ("LO" if k == 0 else "HI")] = m

axB.plot([1, 2], [18.6, 18.6], color=INK, lw=0.4, zorder=5)
axB.text(1.5, 19.4, "Difference 7.45 (95% CI 6.08\u20138.68)", ha="center",
         va="bottom", fontsize=FS_NOTE, color=INK)
axB.set_xlim(0.45, 2.55)
axB.set_xticks([1, 2])
axB.set_xticklabels([f"Lower PPSD\nn=52; ESS {ESS_LO:.1f}",
                     f"Higher PPSD\nn=52; ESS {ESS_HI:.1f}"], fontsize=FS_TICK)
axB.set_ylim(0, 21)
axB.set_yticks([0, 5, 10, 15, 20])
axB.set_ylabel("WOMAC pain (0\u201320)", fontsize=FS_AXIS, fontweight="bold",
               labelpad=1.5)
axB.tick_params(axis="both", pad=1.2)
S.strip_axes(axB)
letter(axB, "b")

# ---------------------------------------------------------------- c
axC = ax_at(S.COL3[0], Y_ABC, S.COL_W, H_ABC)
axC.axvspan(30, 49.2, color=BLUE_PALE, zorder=0, lw=0)
tcol = {"Higher early PSAP": RED, "Remaining participants": BLUE}
for gname, c in tcol.items():
    d = traj[traj.group == gname].sort_values("month")
    axC.fill_between(d.month, d.lower, d.upper, color=c, alpha=0.10, lw=0, zorder=1)
    axC.plot(d.month, d.estimate, color=c, lw=0.65, zorder=3)
    axC.scatter(d.month, d.estimate, s=7, color=c, zorder=4, linewidths=0)
axC.text(37, 62, "Difference 14.78\n95% CI 11.32\u201318.12", ha="center",
         va="top", fontsize=FS_NOTE, color=INK, linespacing=1.25)
axC.set_xlim(-1.2, 49.2)
axC.set_xticks([0, 12, 24, 36, 48])
axC.set_ylim(0, 68)
axC.set_yticks([0, 20, 40, 60])
axC.set_xlabel("Follow-up (months)", fontsize=FS_AXIS, fontweight="bold",
               labelpad=1.5)
axC.set_ylabel("WOMAC function (0\u201368)", fontsize=FS_AXIS, fontweight="bold",
               labelpad=1.5)
axC.tick_params(axis="both", pad=1.2)
S.strip_axes(axC)
_hc = [Line2D([], [], color=RED, lw=0.9, label="Higher PPSD (n=49)"),
       Line2D([], [], color=BLUE, lw=0.9, label="Remaining (n=456)")]
axC.legend(handles=_hc, loc="upper left", fontsize=FS_NOTE, frameon=False,
           handlelength=1.0, handletextpad=0.35, borderpad=0.05,
           labelspacing=0.30, borderaxespad=0.15)
letter(axC, "c")

# ---------------------------------------------------------------- d（三线表+森林）
# 与 Fig. 2g 同一套纵向参数（全部按本面板毫米高换算，改行带即自动跟随）
axD = ax_at(0.0, Y_D, W, H_D)
axD.set_xlim(0, W)
axD.set_ylim(0, H_D)
axD.axis("off")

E_ROWS = [("Structure", "Structure"),
          ("BaselinePain", "Baseline pain"),
          ("StructureBaselinePain", "Baseline pain + structure"),
          ("StructureClinic", "Structure + clinical"),
          ("BaselinePainClinic", "Baseline pain + clinical"),
          ("Full", "Baseline pain + structure + clinical")]
INCL = {"BaselinePain": (1, 0, 0), "Structure": (0, 1, 0),
        "BaselinePainClinic": (1, 0, 1), "StructureClinic": (0, 1, 1),
        "StructureBaselinePain": (1, 1, 0), "Full": (1, 1, 1)}
eff = eff.set_index("model")

DOTX = [44.0, 54.0, 64.0]
FX0, FX1 = 76.0, 152.0
ORX = W - 0.5
LOGL, LOGH = 1.0, 25.0


def mx(v):
    return FX0 + (np.log(v) - np.log(LOGL)) / (np.log(LOGH) - np.log(LOGL)) * (FX1 - FX0)


Y_TOP = H_D - 1.0
Y_HDR = H_D - 3.6
Y_HDRRULE = H_D - 6.0
Y_RULE_BOT = 6.6
ROWS_Y = np.linspace(H_D - 9.2, 8.8, len(E_ROWS))

axD.plot([0, W], [Y_TOP, Y_TOP], color=INK, lw=S.LW_RULE, solid_capstyle="butt")
axD.plot([0, W], [Y_HDRRULE, Y_HDRRULE], color=INK, lw=S.LW_RULE_THIN,
         solid_capstyle="butt")
axD.text(0, Y_HDR, "ADJUSTMENT SET", fontsize=FS_HDR, fontweight="bold",
         color=INK, va="center")
for k, lab in enumerate(["PAIN", "X-RAY", "CLINICAL"]):
    axD.text(DOTX[k], Y_HDR, lab, fontsize=FS_HDR, fontweight="bold", color=INK,
             va="center", ha="center")
axD.text((FX0 + FX1) / 2, Y_HDR, "DISCORDANCE OR", fontsize=FS_HDR,
         fontweight="bold", color=INK, va="center", ha="center")
axD.text(ORX, Y_HDR, "OR [95% CI]", fontsize=FS_HDR, fontweight="bold",
         color=INK, va="center", ha="right")

axD.plot([mx(1), mx(1)], [Y_HDRRULE - 0.8, Y_RULE_BOT], color=GREY, lw=S.LW_DASH,
         ls=(0, (2.5, 2)), zorder=1)
for y, (key, lab) in zip(ROWS_Y, E_ROWS):
    r = eff.loc[key]
    axD.text(0, y, lab, fontsize=FS_CELL, color=INK, va="center")
    for k in range(3):
        on = INCL[key][k] == 1
        axD.scatter([DOTX[k]], [y], s=9.5,
                    facecolor=BLUE if on else "white",
                    edgecolor="none" if on else GREY_SOFT,
                    linewidths=0.5 if not on else 0, zorder=3)
    axD.plot([mx(r.lo), mx(r.hi)], [y, y], color=BLUE, lw=S.LW_CI, zorder=3,
             solid_capstyle="butt")
    for xv in (mx(r.lo), mx(r.hi)):
        axD.plot([xv, xv], [y - 0.85, y + 0.85], color=BLUE, lw=S.LW_CI, zorder=3)
    axD.scatter([mx(r.OR)], [y], s=11, color=RED, zorder=4, linewidths=0)
    axD.text(ORX, y, f"{r.OR:.2f} [{r.lo:.2f}, {r.hi:.2f}]", fontsize=FS_CELL,
             color=INK, va="center", ha="right")

axD.plot([0, W], [Y_RULE_BOT, Y_RULE_BOT], color=INK, lw=S.LW_RULE,
         solid_capstyle="butt")
axD.plot([mx(1), mx(25)], [Y_RULE_BOT - 1.0, Y_RULE_BOT - 1.0], color=INK,
         lw=S.LW_AXIS + 0.05, solid_capstyle="butt")
for v in (1, 2, 5, 10, 20):
    axD.plot([mx(v), mx(v)], [Y_RULE_BOT - 1.0, Y_RULE_BOT - 1.9], color=MUTED,
             lw=S.LW_TICK)
    axD.text(mx(v), Y_RULE_BOT - 3.0, str(v), fontsize=FS_CELL, color=MUTED,
             ha="center", va="center")
axD.text((FX0 + FX1) / 2, 1.2, "Adjusted odds ratio (log scale); dashed line: OR = 1",
         fontsize=FS_CELL, color=INK, ha="center", va="center", fontweight="bold")
letter(axD, "d")

# ---------------------------------------------------------------- e / f（预测条图）
MODS = ["Structure", "Reference", "ReferenceStructure", "PPSD",
        "ReferencePPSD", "Full"]
MCOL = S.MODEL_COLORS


def bars(ax, endpoint, domain, letter_, show_ylabels=True):
    q = perf[(perf.endpoint == endpoint) & (perf.model.isin(MODS))].copy()
    q["__o"] = q.model.map({m: i for i, m in enumerate(MODS)})
    q = q.sort_values("__o").reset_index(drop=True)
    assert len(q) == 6, (endpoint, len(q))
    # 短名与 Fig. 2h-j 完全一致（全称进图注）：
    # 两面板拼幅时 22 mm 宽的全名会横穿接缝，压住左面板的条形与数值。
    labels = ["Structure", "Reference", "Ref + structure", "PPSD",
              "Ref + PPSD", "Full"]
    q["lab"] = labels
    tests = sig[sig.endpoint == endpoint]
    st = {c: str(tests[tests.comparison == c].stars.iloc[0])
          for c in tests.comparison}

    lim_lo = min(-0.03, q.r2_lo.min() - 0.02)
    lim_hi = max(0.58, q.r2_hi.max() + 0.10)

    ypos = np.arange(6)[::-1]
    for i in range(6):
        r = q.iloc[i]
        ax.barh(ypos[i], r.r2, height=0.58, color=MCOL[r.model], alpha=1.0,
                linewidth=0, zorder=2)
        ax.plot([r.r2_lo, r.r2_hi], [ypos[i], ypos[i]], color=INK, lw=0.5,
                zorder=3, solid_capstyle="butt")
        ax.plot([r.r2_lo, r.r2_lo], [ypos[i] - 0.10, ypos[i] + 0.10],
                color=INK, lw=0.5, zorder=3)
        ax.plot([r.r2_hi, r.r2_hi], [ypos[i] - 0.10, ypos[i] + 0.10],
                color=INK, lw=0.5, zorder=3)
        star = ""
        if r.model == "ReferencePPSD":
            star = st.get("PPSD_added_to_reference", "")
        elif r.model == "Full":
            star = st.get("StructureClinical_added_to_reference_PPSD", "")
        off = (lim_hi - lim_lo) * 0.012
        ax.text(r.r2_hi + off, ypos[i], f"{r.r2:.3f}{star}", va="center",
                ha="left", fontsize=FS_CELL, color=INK)

    ax.axvline(0, color=GREY, lw=S.LW_AXIS, zorder=1)
    ax.set_xlim(lim_lo, lim_hi)
    ax.set_ylim(-0.62, 5.62)
    ax.set_xticks([0.0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_yticks(ypos)
    if show_ylabels:
        ax.set_yticklabels(labels, fontsize=FS_TICK, linespacing=1.0)
    else:
        ax.set_yticklabels([])
    ax.set_xlabel("Held-out R\u00b2 (95% CI); higher is better", fontsize=FS_AXIS,
                  fontweight="bold", labelpad=1.5)
    ax.tick_params(axis="x", pad=1.2)
    ax.tick_params(axis="y", length=0, pad=1.5)
    S.strip_axes(ax, keep=("bottom",))
    letter(ax, letter_)
    return q


# 两面板拼幅：接缝取中列中心线 COL_MID，两面板等宽、外沿对齐第一行的 a / c。
# 两面板行标签完全相同 -> 只由左面板印一次，右面板留净空，避免 22 mm 宽
# 的两行全名横穿接缝（这正是上一版 e/f 互相压字的原因）。
_E_R = S.COL_MID - 1.0
_F_L = S.COL_MID + 1.0
axE = ax_at(S.COL1[0], Y_EF, _E_R - S.COL1[0], H_EF)
bars(axE, "pain_mean", "pain", "e", show_ylabels=True)
axF = ax_at(_F_L, Y_EF, S.COL3[1] - _F_L, H_EF)
bars(axF, "function_mean", "function", "f", show_ylabels=False)

# ---------------------------------------------------------------- 保存
S.clip_ticks(FIG)
os.makedirs(OUT, exist_ok=True)
stem = os.path.join(OUT, "Figure1_NC_final_183x170")

small = [(t.get_fontsize(), t.get_text()[:40])
         for t in FIG.findobj(matplotlib.text.Text)
         if t.get_text().strip() and t.get_visible() and t.get_fontsize() < 5.0]
print(f"Figure 1: {W:.1f} x {H:.1f} mm  |  <5 pt 的文字: {len(small)} 处")
for s_, t_ in small[:10]:
    print(f"   {s_} pt  {t_!r}")

FIG.savefig(stem + ".pdf", dpi=DPI, facecolor="white")
FIG.savefig(stem + ".png", dpi=DPI, facecolor="white")
FIG.savefig(stem + ".svg", dpi=DPI, facecolor="white")
print("saved:", os.path.basename(stem) + ".pdf/.png/.svg")
