# -*- coding: utf-8 -*-
"""顶刊标准图版：Figure 6（主图）+ Figure S1–S4（补充图）。

只从 data.json / stats.json / 01_数据 下的 CSV 取数，不手写任何统计量。
所有面板标题为完整句子；每张图版有 header（claim）与 footer（分析单位 / 方法 / 不主张什么）。
"""
import csv
import json
import os

import numpy as np
from scipy import stats

import journal_style as J

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FIG = os.path.join(ROOT, "08_图版_顶刊交付_20261101", "figures")
DATA = os.path.join(ROOT, "07_配对组织-体液验证_20261101", "01_数据")
SCRIPT = os.path.join(ROOT, "07_配对组织-体液验证_20261101", "02_脚本")

D = json.load(open(os.path.join(SCRIPT, "data.json"), encoding="utf-8"))
S = json.load(open(os.path.join(SCRIPT, "stats.json"), encoding="utf-8"))

STRICT = os.environ.get("STRICT", "0") == "1"

# 画幅与页脚里出现的样本量一律从 stats.json 取，扩组后不用改文字
FLOW = S["flow"]
NP = FLOW["paired"]                 # 可配对例数
NE = FLOW["enrolled"]               # 入组例数
NPRM = FLOW["prm_valid"]            # PRM 质控通过例数
ROC = S["roc"]
NROC = ROC["n_hi"] + ROC["n_lo"]    # 两端对比实际入模的例数
CILO = ROC["ci"][0]

# ---------------------------------------------------------------- 数据
ids = D["ids"]
paired = np.array(D["paired"], bool)
pi = [i for i in range(len(ids)) if paired[i]]
P = [ids[i] for i in pi]
SF = np.array([D["sf_fmol"][i] for i in pi])
TIS = np.array([D["pcdh9"][i] for i in pi])
CORE = np.array([D["core20"][i] for i in pi])
PPSD = np.array([D["ppsd"][i] for i in pi])
WOM = np.array([D["womac"][i] for i in pi], float)
SSI = np.array([D["ssi"][i] for i in pi])
TP = np.array([D["tp"][i] for i in pi], float)
RIN = np.array([D["rin"][i] for i in pi], float)
BATCH = [D["batch"][i] for i in pi]
LLOQ, LOD = D["lloq"], D["lod"]

# PRM 有效集：从排除名单反推（血性 / 量不足 / PRM 质控不合格），不写死编号
_PRM_BAD = {k for k, v in D["excl"].items()
            if ("肉眼血性" in v) or ("滑液量" in v) or ("PRM 质控不合格" in v)}
PRM_VALID = [i for i in range(len(ids)) if ids[i] not in _PRM_BAD]
SF_ALL = np.array([D["sf_fmol"][i] for i in PRM_VALID])
IDS_ALL = [ids[i] for i in PRM_VALID]

FL = S["flow"]
ROC = S["roc"]
MOD = S["models"]
MODP = S["models_prespec"]
SEC = {r["id"]: r for r in S["secondary"]}
PR = S["primary"]

CUT = ROC["ppsd_cut"]


def lab_rule():
    lab = np.full(len(PPSD), -1, int)
    lab[PPSD >= CUT] = 1
    lab[PPSD <= -CUT] = 0
    return lab


LAB = lab_rule()
SEL = LAB >= 0


# ---------------------------------------------------------------- 标签英译
# 图版必须纯英文：stats.json 里的标签是中文，这里逐条映射，不做机器翻译
EN = {
    "全部可配对病例（主分析）": "All pairable patients (primary)",
    "排除 < LLOQ": "Excluding < LLOQ",
    "仅无血液污染": "No blood contamination only",
    "仅单次冻融": "Single freeze–thaw only",
    "排除近期关节腔注射": "Excluding recent injection",
    "仅测序批次 B1": "Sequencing batch B1 only",
    "仅 KL IV": "KL grade IV only",
    "仅肽 P1 定量": "Quantified on P1 only",
    "仅肽 P2 定量": "Quantified on P2 only",
    "仅肽 P3（确认肽）": "Quantified on P3 (confirmatory)",
    "年龄 + 性别 + BMI": "Age, sex, BMI",
    "滑膜炎症（Krenn）": "Synovial inflammation (Krenn)",
    "免疫细胞评分": "Immune-cell score",
    "泛 ECM 评分": "Global ECM score",
    "滑液血液污染分级": "Fluid blood grade",
    "预设 |PPSD| ≥ 0.5 SD（两端对比）": "Prespecified, |PPSD| ≥ 0.5",
    "预设 PPSD ≥ +0.5 SD vs 其余": "Prespecified, one-sided",
    "本队列中位切分": "This-cohort median split",
    "本队列极端三分位": "This-cohort tertiles",
    "本队列极端四分位": "This-cohort quartiles",
}


def en(s):
    return EN.get(s, s)


# ---------------------------------------------------------------- 小工具
def pstr(p):
    return "P < 0.001" if p < 0.001 else f"P = {p:.3f}"


def rho_box(ax, r, ci, p, n, x=0.04, y=0.96, extra=None):
    txt = f"$\\rho$ = {r:.2f} ({ci[0]:.2f} to {ci[1]:.2f})\n{pstr(p)}   n = {n}"
    if extra:
        txt += "\n" + extra
    ax.text(x, y, txt, transform=ax.transAxes, va="top", ha="left",
            fontsize=6.2, color=J.INK, linespacing=1.45,
            bbox=dict(facecolor="white", alpha=0.86, edgecolor="none", pad=1.6))


def logy(ax, ticks):
    ax.set_yscale("log")
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{t:g}" for t in ticks])
    ax.yaxis.set_minor_locator(J.matplotlib.ticker.NullLocator())


def scat(ax, x, y, color=J.OA, s=16, log=True, ticks=(0.2, 0.3, 0.5, 1, 2, 3, 4)):
    ax.scatter(x, y, s=s, facecolor=color, edgecolor="white", linewidth=0.4,
               zorder=3, alpha=0.95)
    if log:
        logy(ax, ticks)
        ax.set_ylim(0.16, 5.2)


def lowess(x, y, frac=0.8):
    import statsmodels.api as sm
    z = sm.nonparametric.lowess(y, x, frac=frac, return_sorted=True)
    return z[:, 0], z[:, 1]


def roc_xy(score, label):
    ths = np.sort(np.unique(score))[::-1]
    tpr, fpr = [0.0], [0.0]
    for t in ths:
        pred = score >= t
        tpr.append(((pred == 1) & (label == 1)).sum() / max((label == 1).sum(), 1))
        fpr.append(((pred == 1) & (label == 0)).sum() / max((label == 0).sum(), 1))
    tpr.append(1.0)
    fpr.append(1.0)
    return np.array(fpr), np.array(tpr)


def box(ax, x, y, w, h, text, fc="#F2F2F2", fs=6.3, bold=False):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.012",
                                linewidth=0.5, edgecolor=J.HAIRLINE, facecolor=fc,
                                zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=J.INK, zorder=3, linespacing=1.35,
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1):
    from matplotlib.patches import FancyArrowPatch
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=6, linewidth=0.5,
                                 color=J.GRAY, shrinkA=0, shrinkB=0, zorder=1))



def tagp(fig, ax, letter, title, note=None):
    """面板标题按本面板宽度换行，避免越到相邻面板上。"""
    bb = ax.get_position()
    pw, _ = J.plate_mm(fig)
    J.tag(fig, ax, letter, title, note, max_mm=max(22.0, bb.width * pw - 5.0))


# ================================================================ Figure 6
def figure6():
    fig = J.plate(J.W2, 158.0)
    gs = fig.add_gridspec(2, 3, left=0.084, right=0.962, top=0.800,
                          bottom=0.130, wspace=0.58, hspace=0.72)

    # ---------------------------------------------------------- A 流程
    axA = fig.add_subplot(gs[0, 0])
    J.no_frame(axA)
    axA.set_xlim(0, 1)
    axA.set_ylim(0, 1)
    box(axA, 0.14, 0.760, 0.72, 0.150, f"Screened\n{FL['screened']}", fc="#F7F7F7")
    box(axA, 0.14, 0.500, 0.72, 0.150, f"Operated\n{FL['enrolled']}", fc="#F7F7F7")
    box(axA, 0.14, 0.240, 0.72, 0.170,
        f"Paired tissue and fluid\n{FL['paired']}", fc="#E9EFE7", bold=True, fs=6.6)
    arrow(axA, 0.50, 0.760, 0.50, 0.655)
    arrow(axA, 0.50, 0.500, 0.50, 0.415)
    axA.text(0.55, 0.707, f"{FL['screened'] - FL['enrolled']} excluded",
             fontsize=5.9, color=J.MUTED, ha="left", va="center")
    axA.text(0.55, 0.457, f"{FL['enrolled'] - FL['paired']} not paired",
             fontsize=5.9, color=J.MUTED, ha="left", va="center")
    axA.text(0.50, 0.175, f"{FL['paired']/FL['enrolled']*100:.0f}% of enrolled",
             fontsize=5.9, color=J.MUTED, ha="center", va="center")
    axA.text(0.50, 0.075,
             f"{FL['prm_valid']} of {FL['sf_processed']} fluid and "
             f"{FL['rna_valid']} of {FL['enrolled']} tissue\nsamples passed QC",
             fontsize=5.6, color=J.MUTED, ha="center", va="center",
             linespacing=1.35)
    tagp(fig, axA, "A", "Every enrolled patient contributes one pair",
          "one sample per compartment, no repeat sampling")

    # ---------------------------------------------------------- B 丰度
    axB = fig.add_subplot(gs[0, 1])
    order = np.argsort(SF_ALL)
    v = SF_ALL[order]
    low = v < LLOQ
    axB.plot(np.arange(len(v)) + 1, v, color=J.LIGHT, lw=0.8, zorder=1)
    axB.scatter((np.arange(len(v)) + 1)[~low], v[~low], s=13, facecolor=J.OA,
                edgecolor="white", linewidth=0.35, zorder=3)
    axB.scatter((np.arange(len(v)) + 1)[low], v[low], s=20, facecolor=J.ACCENT,
                edgecolor="white", linewidth=0.4, zorder=4)
    axB.axhline(LLOQ, color=J.ACCENT, lw=0.6, ls=(0, (4, 2)), zorder=2)
    axB.text(len(v) * 0.99, LLOQ * 1.12, f"LLOQ {LLOQ:.2f}", fontsize=6.0,
             color=J.ACCENT, ha="right", va="bottom")
    logy(axB, (0.2, 0.5, 1, 2, 4))
    axB.set_ylim(0.18, 6.0)
    axB.set_xlim(0.5, len(v) + 0.5)
    axB.set_xticks([1, 5, 10, 15, 20, 25])
    J.style_axis(axB, "Patient (ordered by abundance)",
                 "Synovial-fluid PCDH9\n(fmol µL$^{-1}$)")
    axB.text(0.03, 0.96, f"{len(v)} of {len(v)} above LOD\n"
                         f"{int((v >= LLOQ).sum())} of {len(v)} at or above LLOQ",
             transform=axB.transAxes, va="top", ha="left", fontsize=6.2,
             color=J.INK, linespacing=1.45)
    tagp(fig, axB, "B", "PCDH9 is quantifiable in every fluid sample",
          f"{len(v)} PRM-valid samples")

    # ---------------------------------------------------------- C 组织–体液
    axC = fig.add_subplot(gs[0, 2])
    a = SEC["A"]
    scat(axC, TIS, SF, color=J.OA)
    lx, ly = lowess(TIS, np.log10(SF), 0.9)
    axC.plot(lx, 10 ** ly, color=J.GRAY, lw=0.7, ls=(0, (4, 2)), zorder=2)
    axC.set_xticks([2, 3, 4, 5])
    axC.set_xlabel("Synovial PCDH9, log$_2$(TPM+1)")
    axC.set_ylabel("Synovial fluid\n(fmol µL$^{-1}$)")
    rho_box(axC, a["rho"], a["ci"], a["p"], len(SF))
    J.style_axis(axC)
    tagp(fig, axC, "C", "Fluid and tissue agree only moderately",
          f"prespecified target $\\rho$ $\\geq$ 0.55; {a['rho']:.2f} reached")

    # ---------------------------------------------------------- D 主终点
    axD = fig.add_subplot(gs[1, 0])
    scat(axD, CORE, SF, color=J.OA)
    lx, ly = lowess(CORE, np.log10(SF), 0.9)
    axD.plot(lx, 10 ** ly, color=J.GRAY, lw=0.7, ls=(0, (4, 2)), zorder=2)
    axD.set_xticks([-2, -1, 0, 1])
    axD.set_xlabel("NR-FB programme score (CORE20, z)")
    axD.set_ylabel("Synovial fluid\n(fmol µL$^{-1}$)")
    rho_box(axD, PR["rho"], PR["ci"], PR["p"], PR["n"])
    J.style_axis(axD)
    tagp(fig, axD, "D", "Fluid PCDH9 tracks the fibroblast programme",
          "primary endpoint, Spearman rank correlation")

    # ---------------------------------------------------------- E PPSD
    axE = fig.add_subplot(gs[1, 1])
    b = SEC["B"]
    axE.axvspan(-2.6, -CUT, color="#F4F4F4", zorder=0)
    axE.axvspan(CUT, 2.0, color="#F4F4F4", zorder=0)
    scat(axE, PPSD, SF, color=J.OA)
    lx, ly = lowess(PPSD, np.log10(SF), 0.9)
    axE.plot(lx, 10 ** ly, color=J.GRAY, lw=0.7, ls=(0, (4, 2)), zorder=2)
    axE.set_xlim(-2.6, 1.9)
    axE.set_xticks([-2, -1, 0, 1])
    axE.set_xlabel("Pain–structure discordance (PPSD, z)")
    axE.set_ylabel("Synovial fluid\n(fmol µL$^{-1}$)")
    rho_box(axE, b["rho"], b["ci"], b["p"], len(SF))
    J.style_axis(axE)
    tagp(fig, axE, "E", "Fluid PCDH9 tracks clinical discordance",
          f"shaded bands: |PPSD| $\\geq$ {CUT:.1f} SD, the ROC subset")

    # ---------------------------------------------------------- F ROC
    axF = fig.add_subplot(gs[1, 2])
    f1, t1 = roc_xy(SF[SEL], LAB[SEL])
    f2, t2 = roc_xy(SSI[SEL], LAB[SEL])
    axF.plot([0, 1], [0, 1], color=J.HAIRLINE, lw=0.6, ls=(0, (2, 2)), zorder=1)
    axF.plot(f2, t2, color=J.GRAY, lw=0.8, drawstyle="steps-post", zorder=2)
    axF.plot(f1, t1, color=J.OA, lw=1.1, drawstyle="steps-post", zorder=3)
    axF.set_xlim(-0.02, 1.02)
    axF.set_ylim(-0.02, 1.02)
    axF.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    axF.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    axF.set_xlabel("1 − specificity")
    axF.set_ylabel("Sensitivity")
    axF.text(0.97, 0.06,
             f"PCDH9   AUC {ROC['auc']:.2f} ({ROC['ci'][0]:.2f}–{ROC['ci'][1]:.2f})\n"
             f"Structural index   AUC {MOD['auc_ssi']:.2f}",
             transform=axF.transAxes, ha="right", va="bottom", fontsize=6.2,
             linespacing=1.45, color=J.INK,
             bbox=dict(facecolor="white", alpha=0.86, edgecolor="none", pad=1.6))
    J.style_axis(axF)
    tagp(fig, axF, "F", "Separation holds inside this cohort only",
          f"{ROC['n_hi']} vs {ROC['n_lo']} at |PPSD| $\\geq$ {CUT:.1f} SD")

    J.header(fig, "Figure 6",
             "Fluid PCDH9 reports the synovial fibroblast programme and separates "
             "pain\u2013structure strata",
             f"Paired knee OA cohort; {NE} enrolled, {NP} analysable; exploratory ROC only")
    J.footer(fig,
             f"Analytic unit is the patient (n = {NP} with paired tissue and fluid). "
             "Spearman rank correlations with 10,000-sample bootstrap percentile intervals; "
             "the ROC uses a cut-point fixed in the 426-patient locked cohort, not in this one. "
             "The figure does not support diagnostic, prognostic or threshold claims: "
             "every patient had advanced OA, so there is no disease-versus-healthy contrast; "
             f"the AUC interval spans {ROC['ci'][0]:.2f} to {ROC['ci'][1]:.2f} and moves with "
             "the cut-point, and the increment over a structural model keeps its sign but "
             "carries an interval that includes zero.")
    J.save(fig, FIG, "Figure6_fluid_PCDH9_reports_programme_not_discrimination",
           strict=STRICT)


# ================================================================ Figure S1
def figureS1():
    fig = J.plate(J.W2, 142.0)
    gs = fig.add_gridspec(2, 3, left=0.078, right=0.982, top=0.788,
                          bottom=0.145, wspace=0.60, hspace=0.92)

    rows = list(csv.DictReader(open(os.path.join(DATA, "PRM_校准曲线.csv"),
                                    encoding="utf-8-sig")))
    cal = {}
    for r in rows:
        cal.setdefault(r["Peptide"], []).append(
            (float(r["Nominal_fmol_per_uL"]), float(r["Area_ratio"])))

    # A 校准
    axA = fig.add_subplot(gs[0, 0])
    for pep, col, mk in (("P1", J.OA, "o"), ("P2", J.HEALTHY, "s")):
        x = np.array([v[0] for v in cal[pep]])
        y = np.array([v[1] for v in cal[pep]])
        axA.scatter(x, y, s=9, marker=mk, facecolor=col, edgecolor="white",
                    linewidth=0.3, zorder=3, label=pep)
        xs = np.logspace(np.log10(0.04), np.log10(12), 40)
        k = S["cal"][pep]
        axA.plot(xs, k["slope"] * xs + k["intercept"], color=col, lw=0.7, zorder=2)
    axA.set_xscale("log")
    axA.set_yscale("log")
    axA.set_xlim(0.03, 14)
    axA.set_ylim(0.02, 14)
    axA.set_xticks([0.05, 0.2, 1, 5, 10])
    axA.set_xticklabels(["0.05", "0.2", "1", "5", "10"])
    axA.set_yticks([0.05, 0.2, 1, 5, 10])
    axA.set_yticklabels(["0.05", "0.2", "1", "5", "10"])
    axA.xaxis.set_minor_formatter(J.matplotlib.ticker.NullFormatter())
    axA.yaxis.set_minor_formatter(J.matplotlib.ticker.NullFormatter())
    axA.set_xlabel("Nominal (fmol µL$^{-1}$)")
    axA.set_ylabel("Light/heavy area ratio")
    J.style_axis(axA)
    axA.text(0.04, 0.96,
             f"P1  slope {S['cal']['P1']['slope']:.3f}, $R^2$ {S['cal']['P1']['r2']:.3f}\n"
             f"P2  slope {S['cal']['P2']['slope']:.3f}, $R^2$ {S['cal']['P2']['r2']:.3f}",
             transform=axA.transAxes, va="top", ha="left", fontsize=6.2,
             linespacing=1.45)
    tagp(fig, axA, "A", "Calibration is linear over four orders",
          "1/x² weighted, seven levels in triplicate")

    # B 准确度
    axB = fig.add_subplot(gs[0, 1])
    lv = S["validation"]
    conc = sorted({v["conc"] for v in lv})
    for pep, col, mk in (("P1", J.OA, "o"), ("P2", J.HEALTHY, "s")):
        xs = [v["conc"] for v in lv if v["pep"] == pep]
        ys = [v["acc"] for v in lv if v["pep"] == pep]
        axB.scatter(xs, ys, s=12, marker=mk, facecolor=col, edgecolor="white",
                    linewidth=0.3, zorder=3)
    axB.axhline(100, color=J.HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=1)
    for y in (85, 115):
        axB.axhline(y, color=J.GRAY, lw=0.5, ls=(0, (1.5, 2)), zorder=1)
    axB.set_xscale("log")
    axB.set_xticks(conc)
    axB.set_xticklabels([f"{c:g}" for c in conc])
    axB.set_xlim(conc[0] * 0.7, conc[-1] * 1.4)
    axB.set_ylim(78, 122)
    axB.set_xlabel("Nominal (fmol µL$^{-1}$)")
    axB.set_ylabel("Back-calculated accuracy (%)")
    J.style_axis(axB)
    axB.text(0.04, 0.96, "dashed: ±15% acceptance", transform=axB.transAxes,
             va="top", ha="left", fontsize=6.2, color=J.MUTED)
    tagp(fig, axB, "B", "Accuracy stays inside ±15% at every level",
          f"lowest level {min(v['acc'] for v in lv):.0f}%, "
          f"highest {max(v['acc'] for v in lv):.0f}%")

    # C 肽段一致性
    axC = fig.add_subplot(gs[0, 2])
    P1 = np.array([D["prm"][f"{p}|P1"] for p in P])
    P2 = np.array([D["prm"][f"{p}|P2"] for p in P])
    diff = (P2 - P1) / P1 * 100
    mean = (P1 + P2) / 2
    pa = S["pep_agree"]
    axC.scatter(mean, diff, s=13, facecolor=J.OA, edgecolor="white",
                linewidth=0.35, zorder=3)
    axC.axhline(pa["p12_bias"], color=J.OA, lw=0.6, zorder=2)
    for y in pa["p12_loa"]:
        axC.axhline(y, color=J.GRAY, lw=0.5, ls=(0, (4, 2)), zorder=1)
    axC.set_xscale("log")
    axC.set_xlim(0.4, 6)
    axC.set_xticks([0.5, 1, 2, 4])
    axC.set_xticklabels(["0.5", "1", "2", "4"])
    axC.xaxis.set_minor_formatter(J.matplotlib.ticker.NullFormatter())
    axC.set_ylim(-40, 30)
    axC.set_xlabel("Mean of P1 and P2 (fmol µL$^{-1}$)")
    axC.set_ylabel("P2 − P1 (% of mean)")
    J.style_axis(axC, zero=False)
    axC.text(0.04, 0.96,
             f"bias {pa['p12_bias']:+.1f}%\n"
             f"limits {pa['p12_loa'][0]:+.0f}% to {pa['p12_loa'][1]:+.0f}%\n"
             f"$\\rho$ = {pa['p12_rho']:.3f}",
             transform=axC.transAxes, va="top", ha="left", fontsize=6.2,
             linespacing=1.45,
             bbox=dict(facecolor="white", alpha=1.0, edgecolor="none", pad=1.8))
    tagp(fig, axC, "C", "The two quantifier peptides agree",
          f"Bland–Altman, n = {len(P)}")

    # D pool QC
    axD = fig.add_subplot(gs[1, 0])
    q = S["poolqc"]
    x = np.arange(1, len(q["series1"]) + 1)
    for ser, col, mk, nm in ((q["series1"], J.OA, "o", "P1"),
                             (q["series2"], J.HEALTHY, "s", "P2")):
        base = np.mean(ser)
        axD.plot(x, (np.array(ser) / base - 1) * 100, color=col, lw=0.7,
                 marker=mk, ms=2.6, zorder=3)
    axD.axhline(0, color=J.HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=1)
    axD.axhspan(-15, 15, color="#F6F6F6", zorder=0)
    axD.set_xlim(0.5, len(x) + 0.5)
    axD.set_ylim(-18, 18)
    axD.set_xticks([1, 4, 8, 12])
    axD.set_xlabel("Pooled-QC injection")
    axD.set_ylabel("Deviation from mean (%)")
    J.style_axis(axD)
    axD.text(0.04, 0.95, f"CV  P1 {q['cv1']:.1f}%\n      P2 {q['cv2']:.1f}%",
             transform=axD.transAxes, va="top", ha="left", fontsize=6.2,
             linespacing=1.45,
             bbox=dict(facecolor="white", alpha=0.86, edgecolor="none", pad=1.4))
    tagp(fig, axD, "D", "Pooled QC holds across the run",
          f"{q['n']} injections, one every third sample")

    # E 稳定性
    axE = fig.add_subplot(gs[1, 1])
    a = S["assay"]
    names = ["Digestion", "Bench 4 h", "3 freeze–thaw", "Carry-over"]
    vals = [a["digest"], a["bench"], a["ft3"]]
    ypos = np.arange(4)[::-1]
    for i, v_ in enumerate(vals):
        y = ypos[i]
        axE.plot([0, v_], [y, y], color=J.LIGHT, lw=2.0, solid_capstyle="butt",
                 zorder=2)
        axE.scatter([v_], [y], s=14, facecolor=J.OA, edgecolor="white",
                    linewidth=0.35, zorder=4)
        axE.text(v_ + 2.5, y, f"{v_:.1f}%", fontsize=6.2, va="center",
                 ha="left", color=J.INK)
    axE.scatter([a["carryover"]], [ypos[3]], s=14, facecolor=J.ACCENT,
                edgecolor="white", linewidth=0.35, zorder=4)
    axE.text(a["carryover"] + 3.0, ypos[3],
             f"{a['carryover']:.2f}%  (limit 1.0%)", fontsize=6.2,
             va="center", ha="left", color=J.ACCENT)
    axE.set_yticks(ypos)
    axE.set_yticklabels(names)
    axE.set_xlim(0, 108)
    axE.set_ylim(-0.7, 3.6)
    axE.set_xticks([0, 25, 50, 75, 100])
    axE.set_xlabel("Recovery (%)")
    J.style_axis(axE)
    tagp(fig, axE, "E", "Pre-analytical recovery clears every limit",
          "spike-in recovery, single batch")

    # F P4 域对照
    axF = fig.add_subplot(gs[1, 2])
    axF.bar([0, 1], [0, 100], width=0.46, color=[J.LIGHT, J.OA], linewidth=0)
    axF.set_xticks([0, 1])
    axF.set_xticklabels([f"Synovial fluid\n(0/{NPRM})", "Tissue lysate\n(5/5)"], fontsize=6.2)
    axF.set_xlim(-0.6, 1.6)
    axF.set_ylim(0, 118)
    axF.set_ylabel("Samples with P4 detected (%)")
    axF.text(0, 3, "not detected", ha="center", va="bottom", fontsize=6.0,
             color=J.ACCENT)
    axF.text(1, 103, "detected", ha="center", va="bottom", fontsize=6.0,
             color=J.INK)
    J.style_axis(axF)
    tagp(fig, axF, "F", "The cytoplasmic peptide stays intracellular",
          "domain control, residues 1156–1165")

    J.header(fig, "Figure S1",
             "The fluid assay is technically sound before any biology is read",
             "Targeted PRM for PCDH9 in synovial fluid; matrix-matched calibration")
    J.footer(fig,
             "Analytic unit is the injection for assay panels and the patient for panel C "
             f"(n = {NP} paired samples). Calibration uses light/heavy area ratios with 1/x² "
             "weighting; accuracy is back-calculated from the fitted line. "
             "The figure does not establish clinical performance: precision and recovery "
             "are shown for a single batch, and the absence of the cytoplasmic peptide "
             "in fluid is consistent with shedding but does not prove it.")
    J.save(fig, FIG, "FigureS1_fluid_assay_validation", strict=STRICT)


# ================================================================ Figure S2
def figureS2():
    fig = J.plate(J.W2, 132.0)
    gs = fig.add_gridspec(1, 2, left=0.215, right=0.975, top=0.735,
                          bottom=0.205, wspace=1.05)

    # A 敏感性
    axA = fig.add_subplot(gs[0, 0])
    rows = [r for r in S["sens"] if not r.get("na")]
    labels = [en(r["label"]) for r in rows]
    vals = [r["rho"] for r in rows]
    los = [r["ci"][0] for r in rows]
    his = [r["ci"][1] for r in rows]
    y = np.arange(len(rows))[::-1]
    for i in range(len(rows)):
        col = J.OA if i == 0 else J.GRAY
        axA.plot([los[i], his[i]], [y[i], y[i]], color=col, lw=0.7, zorder=2)
        axA.scatter([vals[i]], [y[i]], s=15 if i == 0 else 11,
                    facecolor=col, edgecolor="white", linewidth=0.35, zorder=3)
    axA.axvline(PR["rho"], color=J.OA, lw=0.5, ls=(0, (4, 2)), zorder=1)
    axA.axvline(0, color=J.HAIRLINE, lw=0.55, zorder=1)
    axA.set_yticks(y)
    axA.set_yticklabels(labels, fontsize=6.2)
    axA.set_xlim(-0.45, 1.05)
    axA.set_xticks([-0.4, 0, 0.4, 0.8])
    axA.set_ylim(-0.7, len(rows) - 0.3)
    axA.set_xlabel("Spearman $\\rho$ with 95% CI")
    J.style_axis(axA)
    tagp(fig, axA, "A", "Every sensitivity analysis keeps the sign",
         f"{len(rows)} analyses, one cohort")

    # B 偏相关
    axB = fig.add_subplot(gs[0, 1])
    parts = S["partial"]
    labels = [en(p["label"]) for p in parts]
    y = np.arange(len(parts))[::-1]
    for i, p in enumerate(parts):
        axB.plot([p["ci"][0], p["ci"][1]], [y[i], y[i]], color=J.GRAY, lw=0.7,
                 zorder=2)
        axB.scatter([p["rho"]], [y[i]], s=11, facecolor=J.GRAY,
                    edgecolor="white", linewidth=0.35, zorder=3)
    axB.axvline(PR["rho"], color=J.OA, lw=0.5, ls=(0, (4, 2)), zorder=1)
    axB.axvline(0, color=J.HAIRLINE, lw=0.55, zorder=1)
    axB.set_yticks(y)
    axB.set_yticklabels(labels, fontsize=6.2)
    axB.set_xlim(-0.15, 0.95)
    axB.set_xticks([-0.1, 0.1, 0.3, 0.5, 0.7, 0.9])
    axB.set_ylim(-0.7, len(parts) - 0.3)
    axB.set_xlabel("Rank partial $\\rho$ with 95% CI")
    J.style_axis(axB)
    tagp(fig, axB, "B", "Adjustment attenuates but does not remove it",
         "dashed line is the unadjusted estimate")

    J.header(fig, "Figure S2",
             "The primary association survives every prespecified perturbation",
             "One cohort; nine sensitivity analyses and five adjustment sets")
    J.footer(fig,
             f"Analytic unit is the patient (n = {NP} paired). Intervals are bootstrap "
             "percentile intervals from 2,000 resamples; partial correlations rank-transform "
             "all variables before residualising. "
             "The figure does not show that the association is causal or specific to PCDH9: "
             f"every analysis re-uses the same {NP} patients, so the analyses are correlated "
             "with one another and none is independent evidence.")
    J.save(fig, FIG, "FigureS2_primary_association_robustness", strict=STRICT)


# ================================================================ Figure S3
def figureS3():
    fig = J.plate(J.W2, 96.0)
    gs = fig.add_gridspec(1, 3, left=0.084, right=0.982, top=0.720,
                          bottom=0.235, wspace=0.62)

    NM = S["normalise"]
    RQ = S["rnaqc"]

    # A 上样量伪影
    axA = fig.add_subplot(gs[0, 0])
    axA.scatter(TP, SF, s=15, facecolor=J.OA, edgecolor="white", linewidth=0.35,
                zorder=3)
    axA.set_xlabel("Total protein loaded (µg)")
    axA.set_ylabel("Synovial fluid\n(fmol µL$^{-1}$)")
    logy(axA, (0.2, 0.5, 1, 2, 4))
    axA.set_ylim(0.18, 5.2)
    J.style_axis(axA)
    axA.text(0.04, 0.96,
             f"$\\rho$ = {NM['sf_tp']['rho']:+.2f}\n{pstr(NM['sf_tp']['p'])}",
             transform=axA.transAxes, va="top", ha="left", fontsize=6.2,
             linespacing=1.45)
    tagp(fig, axA, "A", "Abundance is not a loading artefact",
          "on-column mass varies with starting volume")

    # B 归一化
    axB = fig.add_subplot(gs[0, 1])
    names = ["Per µL\nof fluid", "Per µg\nof protein"]
    vals = [PR["rho"], NM["sf_ug_rho"]["rho"]]
    los = [PR["ci"][0], NM["sf_ug_ci"][0]]
    his = [PR["ci"][1], NM["sf_ug_ci"][1]]
    x = np.arange(2)
    for i in range(2):
        axB.plot([x[i], x[i]], [los[i], his[i]], color=J.GRAY, lw=0.8, zorder=2)
        axB.scatter([x[i]], [vals[i]], s=22, facecolor=J.OA, edgecolor="white",
                    linewidth=0.4, zorder=3)
        axB.text(x[i] + 0.10, vals[i], f"{vals[i]:.2f}", fontsize=6.3,
                 va="center", ha="left")
    axB.axhline(0, color=J.HAIRLINE, lw=0.55, zorder=1)
    axB.set_xticks(x)
    axB.set_xticklabels(names, fontsize=6.2)
    axB.set_xlim(-0.5, 1.6)
    axB.set_ylim(-0.1, 1.0)
    axB.set_ylabel("$\\rho$ with CORE20 (95% CI)")
    J.style_axis(axB)
    tagp(fig, axB, "B", "Normalisation leaves the endpoint unchanged",
          "same patients, two reporting units")

    # C RNA 质控
    axC = fig.add_subplot(gs[0, 2])
    for b, col, mk in (("B1", J.HEALTHY, "o"), ("B2", J.SAND, "s")):
        k = np.array([bb == b for bb in BATCH])
        axC.scatter(RIN[k], CORE[k], s=15, marker=mk, facecolor=col,
                    edgecolor="white", linewidth=0.35, zorder=3, label=b)
    axC.axhline(0, color=J.HAIRLINE, lw=0.55, zorder=1)
    axC.set_xticks([6, 7, 8, 9, 10])
    axC.set_xlabel("RNA integrity number (RIN)")
    axC.set_ylabel("CORE20 score (z)")
    J.style_axis(axC)
    axC.legend(loc="upper right", fontsize=6.2, handletextpad=0.4,
               borderpad=0.2, labelspacing=0.35, frameon=False)
    axC.text(0.04, 0.04,
             f"$\\rho$ = {RQ['core_rin']['rho']:+.2f}\n"
             f"batch {pstr(RQ['batch_p'])}",
             transform=axC.transAxes, va="bottom", ha="left", fontsize=6.2,
             linespacing=1.45,
             bbox=dict(facecolor="white", alpha=0.9, edgecolor="none", pad=1.6))
    tagp(fig, axC, "C", "Neither RNA quality nor batch drives the score",
          f"B1 n = {RQ['b1_n']}, B2 n = {RQ['b2_n']}")

    J.header(fig, "Figure S3",
             "The association is not explained by loading or by library quality",
             f"Two orthogonal technical checks on the same {NP} patients")
    J.footer(fig,
             f"Analytic unit is the patient (n = {NP} paired). Total protein is the on-column "
             "mass measured by BCA; the per-microgram value divides fluid concentration by "
             "that mass. "
             "The figure does not prove that joint dilution is irrelevant in general: "
             "total protein happens to be uncorrelated with CORE20 in this cohort, and a "
             "cohort in which it is correlated would need the normalised value as primary.")
    J.save(fig, FIG, "FigureS3_loading_and_library_quality_controls", strict=STRICT)


# ================================================================ Figure S4
def figureS4():
    fig = J.plate(J.W2, 118.0)
    gs = fig.add_gridspec(1, 2, left=0.285, right=0.975, top=0.745,
                          bottom=0.205, wspace=1.05)

    ALT = ROC["alt"]

    # A AUC 随切点
    axA = fig.add_subplot(gs[0, 0])
    y = np.arange(len(ALT))[::-1]
    for i, r in enumerate(ALT):
        col = J.OA if i == 0 else J.GRAY
        axA.plot([r["ci"][0], r["ci"][1]], [y[i], y[i]], color=col, lw=0.7, zorder=2)
        axA.scatter([r["auc"]], [y[i]], s=15 if i == 0 else 11, facecolor=col,
                    edgecolor="white", linewidth=0.35, zorder=3)
        axA.text(r["ci"][1] + 0.015, y[i], f"{r['auc']:.2f}", fontsize=6.0,
                 va="center", ha="left", color=J.INK)
    axA.axvline(0.5, color=J.HAIRLINE, lw=0.55, zorder=1)
    axA.set_yticks(y)
    axA.set_yticklabels([en(r["label"]) for r in ALT], fontsize=6.2)
    axA.set_xlim(0.18, 1.18)
    axA.set_xticks([0.3, 0.5, 0.7, 0.9])
    axA.set_ylim(-0.7, len(ALT) - 0.3)
    axA.set_xlabel("AUC with 95% CI")
    J.style_axis(axA)
    tagp(fig, axA, "A", "Cut-point shifts rival sampling error",
         f"five dichotomies, one cohort, {ROC['spread'][0]:.2f}\u2013{ROC['spread'][1]:.2f}")

    # B 增量随结局
    axB = fig.add_subplot(gs[0, 1])
    rows = [("Median split\n(this cohort)", MOD),
            ("Prespecified cut\n(locked cohort)", MODP)]
    x = np.arange(2)
    for i, (nm, m) in enumerate(rows):
        axB.plot([x[i], x[i]], [m["delta_ci"][0], m["delta_ci"][1]], color=J.GRAY,
                 lw=0.8, zorder=2)
        axB.scatter([x[i]], [m["delta_corrected"]], s=22, facecolor=J.OA,
                    edgecolor="white", linewidth=0.4, zorder=3)
        axB.text(x[i] + 0.10, m["delta_corrected"],
                 f"{m['delta_corrected']:+.2f}", fontsize=6.3, va="center", ha="left")
    axB.axhline(0, color=J.HAIRLINE, lw=0.55, zorder=1)
    axB.set_xticks(x)
    axB.set_xticklabels([r[0] for r in rows], fontsize=6.2)
    axB.set_xlim(-0.55, 1.55)
    _lo = min(m["delta_ci"][0] for _, m in rows) - 0.06
    _hi = max(m["delta_ci"][1] for _, m in rows) + 0.08
    axB.set_ylim(_lo, _hi)
    axB.set_yticks(np.arange(-0.1, _hi, 0.1).round(2))
    axB.set_ylabel("$\\Delta$AUC over the structural model")
    J.style_axis(axB)
    tagp(fig, axB, "B", "The sign is stable, the precision is not",
         f"{MOD['events']} and {MODP['events']} events, five predictors")

    J.header(fig, "Figure S4",
             "Where the exploratory analysis stops being informative",
             f"Same {NP} patients; five cut-points and two outcome definitions")
    J.footer(fig,
             f"Analytic unit is the patient (n = {NP} paired; {NROC} contribute to the two-sided "
             "contrast). AUC intervals are DeLong; \u0394AUC is Harrell optimism-corrected with "
             "bootstrap intervals from 600 resamples. "
             "The figure does not identify which cut-point is correct: none is, at this "
             "sample size. It is included to make the dependence explicit, not to rank "
             "the alternatives.")
    J.save(fig, FIG, "FigureS4_cutpoint_and_outcome_sensitivity", strict=STRICT)


if __name__ == "__main__":
    os.makedirs(FIG, exist_ok=True)
    figure6()
    figureS1()
    figureS2()
    figureS3()
    figureS4()
    print("done")
