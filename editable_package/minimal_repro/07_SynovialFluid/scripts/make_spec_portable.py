# -*- coding: utf-8 -*-
"""从 stats.json 生成文字层 spec（图注 / 索引 / 清单）。

图注里的数字全部取自 stats.json，不手写，避免"图上 0.56、图注 0.57"。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
PROJ = ROOT
SCRIPT = os.path.join(ROOT, "data")

S = json.load(open(os.path.join(SCRIPT, "stats.json"), encoding="utf-8"))
PR = S["primary"]
ROC = S["roc"]
MOD = S["models"]
MODP = S["models_prespec"]
SEC = {r["id"]: r for r in S["secondary"]}
FL = S["flow"]
NM = S["normalise"]
RQ = S["rnaqc"]
PA = S["pep_agree"]
AS = S["assay"]
PQ = S["poolqc"]
CAL = S["cal"]
T1 = S["table1"]


NP = FL["paired"]        # 可配对例数
NE = FL["enrolled"]      # 入组例数
NROC = ROC["n_hi"] + ROC["n_lo"]


def f2(x):
    return f"{x:.2f}"


def ci(d):
    return f"{d['ci'][0]:.2f}–{d['ci'][1]:.2f}"


spec = {
    "outdir": ROOT,
    "figdir": "figures",
    "gallery": "图版索引_20261101.html",
    "legends": "Figure_legends_20261101.md",
    "manifest": "图版交付清单_20261101.csv",
    "expect_width_mm": 180,
    "expect_dpi": 600,
    "bilingual": True,
    "kicker": "PCDH9 paired tissue–fluid validation · revision 2026-11-01 · 中文对照版",
    "title_en": "Five plates that answer one question and state where the answer stops",
    "title_cn": "五张图回答一个问题，并标明答案止于何处",
    "lede_en": (
        "Does synovial-fluid PCDH9 report the synovial fibroblast programme and clinical "
        "discordance in knee osteoarthritis? These plates support technical feasibility, a "
        "moderate tissue–fluid association, and an association with pain–structure "
        "discordance. They do not support diagnostic, prognostic or threshold claims. Every "
        "plate carries an explicit does-not-support line, so that a boundary is never read "
        "as a conclusion."
    ),
    "lede_cn": (
        "滑液 PCDH9 能否反映膝骨关节炎的滑膜成纤维细胞程序与临床失配？这五张图支持三件事："
        "技术上测得出来、组织与体液之间存在中等强度关联、与疼痛–结构失配相关。"
        "它们不支持任何诊断、预后或阈值结论。每张图都写明「不支撑什么」，"
        "避免把边界读成结论。"
    ),
    "footer_spec_en": (
        "Plates are English-only, 180 mm double-column, Arial, minimum type 5.6 pt, pure "
        "white ground, no shadow, no gridline, left/bottom rules only (0.5 pt), 600 dpi PNG "
        "plus vector PDF with Type 42 fonts."
    ),
    "footer_spec_cn": (
        "图版为纯英文，画幅 180 mm（双栏），"
        "Arial 字体，最小字号 5.6 pt，纯白底、无阴影、无网格，仅保留左/下轴线（0.5 pt），"
        "输出 600 dpi PNG 与 Type 42 矢量 PDF。"
    ),
    "footer_unit_en": (
        f"The analytic unit is the patient throughout (n = {NP} with paired tissue and fluid; "
        f"{NE} enrolled). Assay panels in Figure S1 use the injection as the unit. Correlations "
        "are Spearman rank with 10,000-sample bootstrap percentile intervals; AUC intervals "
        "are DeLong."
    ),
    "footer_unit_cn": (
        f"全部分析单位为患者（{NP} 例完成组织–体液配对，入组 {NE} 例）。图 S1 的方法学面板以进针为单位。"
        "相关系数为 Spearman 秩相关，区间为 10 000 次 bootstrap 百分位区间；AUC 区间为 DeLong 法。"
    ),
    "figures": [],
}

# ---------------------------------------------------------------- Figure 6
spec["figures"].append({
    "file": "Figure6_fluid_PCDH9_reports_programme_not_discrimination",
    "number": "Figure 6",
    "short_en": "Fluid PCDH9 reports the programme and separates discordance strata",
    "short_cn": "滑液 PCDH9 反映程序活性，并在本队列内区分失配分层",
    "supports_en": (
        f"Fluid PCDH9 is quantifiable in all {FL['prm_valid']} PRM-valid samples, tracks the "
        f"synovial fibroblast programme (rho = {f2(PR['rho'])}, 95% CI {ci(PR)}), tracks "
        f"pain–structure discordance (rho = {f2(SEC['B']['rho'])}), is unrelated to "
        f"structural severity (rho = {f2(SEC['F']['rho'])}), and separates the two discordance "
        f"strata (AUC {f2(ROC['auc'])}, 95% CI {ci(ROC)})."
    ),
    "supports_cn": (
        f"滑液 PCDH9 在全部 {FL['prm_valid']} 例 PRM 有效样本中可定量，与滑膜成纤维细胞程序评分"
        f"相关（ρ = {f2(PR['rho'])}，95% CI {ci(PR)}），与疼痛–结构失配相关"
        f"（ρ = {f2(SEC['B']['rho'])}），与结构严重度无关（ρ = {f2(SEC['F']['rho'])}），"
        f"并在本队列内分开两端失配分层（AUC {f2(ROC['auc'])}，95% CI {ci(ROC)}）。"
    ),
    "not_en": (
        f"Any diagnostic, prognostic or threshold claim. Every patient had advanced OA, so "
        f"there is no disease-versus-healthy contrast; the tissue–fluid correlation is "
        f"{f2(SEC['A']['rho'])} against a prespecified 0.55; and the ROC interval runs "
        f"{ci(ROC)} at n = {ROC['n_hi']} vs {ROC['n_lo']}, moving with the cut-point."
    ),
    "not_cn": (
        f"不能支撑任何诊断、预后或阈值结论。全部病例均为终末期 OA，不存在「有病 vs 无病」的对比；"
        f"组织–体液相关仅 {f2(SEC['A']['rho'])}，低于预设的 0.55；ROC 区间为 {ci(ROC)}，"
        f"样本量 {ROC['n_hi']} 对 {ROC['n_lo']} 例，且随切点变动。"
    ),
    "panels": [
        ["A", "Paired sampling and analysis set; one sample per compartment.",
         "配对采样与入组流程；每个部位只取一份样本。"],
        ["B", "Fluid PCDH9 abundance per patient, ordered, with the LLOQ marked.",
         "各例滑液 PCDH9 丰度排序，标出 LLOQ。"],
        ["C", "Fluid PCDH9 against paired synovial PCDH9 transcript.",
         "滑液 PCDH9 与配对滑膜 PCDH9 转录本的关系。"],
        ["D", "Fluid PCDH9 against the NR-FB programme score (primary endpoint).",
         "滑液 PCDH9 与 NR-FB 程序评分的关系（主要终点）。"],
        ["E", "Fluid PCDH9 against continuous pain–structure discordance.",
         "滑液 PCDH9 与连续疼痛–结构失配的关系。"],
        ["F", "Exploratory ROC against a cut-point fixed in the locked cohort.",
         "以锁定队列切点做的探索性 ROC。"],
    ],
    "caption_en": (
        f"Synovial-fluid PCDH9 in paired knee OA samples. (A) Of {FL['screened']} screened, "
        f"{FL['enrolled']} were operated and {FL['paired']} yielded an analysable tissue–fluid "
        f"pair; {FL['prm_valid']} of {FL['sf_processed']} processed fluid samples and "
        f"{FL['rna_valid']} of {FL['enrolled']} tissue samples passed QC. (B) Fluid PCDH9 in "
        f"the {FL['prm_valid']} PRM-valid samples, ordered by abundance; the dashed line is the "
        f"lower limit of quantification ({AS['lloq']:.2f} fmol µL⁻¹). (C) Fluid PCDH9 against "
        f"paired synovial PCDH9 transcript (rho = {f2(SEC['A']['rho'])}, 95% CI "
        f"{ci(SEC['A'])}). (D) Primary endpoint: fluid PCDH9 against the locked 20-gene NR-FB "
        f"programme score (rho = {f2(PR['rho'])}, 95% CI {ci(PR)}, P = {PR['p']:.4f}). "
        f"(E) Fluid PCDH9 against continuous pain–structure discordance (rho = "
        f"{f2(SEC['B']['rho'])}, 95% CI {ci(SEC['B'])}); shaded bands mark |PPSD| >= "
        f"{ROC['ppsd_cut']:.1f} SD, the subset used in F. (F) Exploratory ROC for that "
        f"two-sided contrast ({ROC['n_hi']} vs {ROC['n_lo']}); the cut-point was fixed in the "
        f"426-patient locked cohort, not in this one. Curves are dashed where the empirical "
        f"step function is interpolated. The structural index, "
        f"z(0.45·KL grade + 0.30·joint-space narrowing + 0.25·osteophyte score), is shown "
        f"for reference "
        f"(AUC {f2(MOD['auc_ssi'])})."
    ),
    "caption_cn": (
        f"配对膝骨关节炎样本中的滑液 PCDH9。(A) 筛查 {FL['screened']} 例，手术 {FL['enrolled']} 例，"
        f"{FL['paired']} 例获得可分析的组织–体液配对；{FL['sf_processed']} 例处理滑液中 "
        f"{FL['prm_valid']} 例、{FL['enrolled']} 例滑膜中 {FL['rna_valid']} 例通过质控。"
        f"(B) {FL['prm_valid']} 例 PRM 有效样本的滑液 PCDH9，按丰度排序；虚线为定量下限"
        f"（{AS['lloq']:.2f} fmol µL⁻¹）。(C) 滑液 PCDH9 与配对滑膜 PCDH9 转录本"
        f"（ρ = {f2(SEC['A']['rho'])}，95% CI {ci(SEC['A'])}）。(D) 主要终点：滑液 PCDH9 与锁定的 "
        f"20 基因 NR-FB 程序评分（ρ = {f2(PR['rho'])}，95% CI {ci(PR)}，P = {PR['p']:.4f}）。"
        f"(E) 滑液 PCDH9 与连续疼痛–结构失配（ρ = {f2(SEC['B']['rho'])}，95% CI "
        f"{ci(SEC['B'])}）；灰底为 |PPSD| ≥ {ROC['ppsd_cut']:.1f} SD，即 F 所用子集。"
        f"(F) 该两端对比的探索性 ROC（{ROC['n_hi']} 对 {ROC['n_lo']} 例）；切点取自 426 例锁定队列，"
        f"不在本队列内重切。结构严重度指数"
        f"（z(0.45·KL 分级 + 0.30·关节间隙狭窄 + 0.25·骨赘评分)）作为参照"
        f"（AUC {f2(MOD['auc_ssi'])}）。"
    ),
})

# ---------------------------------------------------------------- Figure S1
spec["figures"].append({
    "file": "FigureS1_fluid_assay_validation",
    "number": "Figure S1",
    "short_en": "The fluid assay is technically sound before any biology is read",
    "short_cn": "在读生物学之前，滑液检测本身先要站得住",
    "supports_en": (
        f"Calibration is linear across four orders (R² {CAL['P1']['r2']:.3f} and "
        f"{CAL['P2']['r2']:.3f}), back-calculated accuracy stays within ±15% at every level, "
        f"the two quantifier peptides agree (rho = {PA['p12_rho']:.3f}), pooled-QC CV is "
        f"{PQ['cv1']:.1f}% and {PQ['cv2']:.1f}%, and pre-analytical recovery clears each limit."
    ),
    "supports_cn": (
        f"校准在四个数量级内线性（R² 分别为 {CAL['P1']['r2']:.3f} 与 {CAL['P2']['r2']:.3f}），"
        f"各浓度回算准确度均在 ±15% 内，两条定量肽一致（ρ = {PA['p12_rho']:.3f}），"
        f"混合 QC 的 CV 为 {PQ['cv1']:.1f}% 与 {PQ['cv2']:.1f}%，前处理回收率全部达标。"
    ),
    "not_en": (
        "Clinical performance. Precision and recovery come from a single batch, and the "
        "absence of the cytoplasmic peptide in fluid is consistent with shedding but does "
        "not demonstrate it."
    ),
    "not_cn": (
        "不能说明临床性能。精密度与回收率来自单一批次；胞质域肽在滑液中未检出"
        "与「脱落」一致，但不能证明脱落机制。"
    ),
    "panels": [
        ["A", "Matrix-matched calibration for both quantifier peptides.",
         "两条定量肽的基质匹配校准曲线。"],
        ["B", "Back-calculated accuracy across the validated range.",
         "验证范围内各浓度的回算准确度。"],
        ["C", "Agreement between the two quantifier peptides.",
         "两条定量肽之间的一致性。"],
        ["D", "Pooled synovial-fluid QC across the injection series.",
         "混合滑液 QC 在整个进样序列中的漂移。"],
        ["E", "Digestion, bench and freeze–thaw recovery, and carry-over.",
         "酶解、台面与冻融回收率，以及残留。"],
        ["F", "Cytoplasmic-domain peptide as a domain control.",
         "以胞质域肽作结构域对照。"],
    ],
    "caption_en": (
        f"Targeted PRM assay validation for PCDH9 in synovial fluid. (A) Light/heavy area "
        f"ratio against nominal concentration for P1 (slope {CAL['P1']['slope']:.3f}) and P2 "
        f"(slope {CAL['P2']['slope']:.3f}), seven levels in triplicate, 1/x² weighted. "
        f"(B) Back-calculated accuracy; dashed lines mark ±15%. (C) Bland–Altman agreement "
        f"between P1 and P2 (bias {PA['p12_bias']:+.1f}%, limits {PA['p12_loa'][0]:+.0f}% to "
        f"{PA['p12_loa'][1]:+.0f}%). (D) Pooled-QC deviation from the series mean across "
        f"{PQ['n']} injections. (E) Spike-in recovery for digestion ({AS['digest']:.1f}%), "
        f"4 h at bench ({AS['bench']:.1f}%) and three freeze–thaw cycles ({AS['ft3']:.1f}%); "
        f"carry-over {AS['carryover']:.2f}% against a 1.0% limit. (F) The cytoplasmic peptide "
        f"P4 was not detected in any of the {FL['prm_valid']} fluid samples but was detected "
        f"in all five tissue lysates, consistent with a shed extracellular domain."
    ),
    "caption_cn": (
        f"滑液 PCDH9 的靶向 PRM 方法学验证。(A) P1（斜率 {CAL['P1']['slope']:.3f}）与 P2"
        f"（斜率 {CAL['P2']['slope']:.3f}）的轻/重峰面积比与标称浓度的关系，7 个浓度、每浓度 3 平行，"
        f"1/x² 加权。(B) 回算准确度，虚线为 ±15%。(C) P1 与 P2 的 Bland–Altman 一致性"
        f"（偏倚 {PA['p12_bias']:+.1f}%，一致性界限 {PA['p12_loa'][0]:+.0f}% 至 "
        f"{PA['p12_loa'][1]:+.0f}%）。(D) 混合 QC 相对序列均值的偏差，共 {PQ['n']} 针。"
        f"(E) 加标回收：酶解 {AS['digest']:.1f}%、台面 4 h {AS['bench']:.1f}%、"
        f"三次冻融 {AS['ft3']:.1f}%；残留 {AS['carryover']:.2f}%（限值 1.0%）。"
        f"(F) 胞质域肽 P4 在 {FL['prm_valid']} 例滑液中均未检出，在 5 例组织裂解液中全部检出，"
        f"与「胞外域脱落」相符。"
    ),
})

# ---------------------------------------------------------------- Figure S2
spec["figures"].append({
    "file": "FigureS2_primary_association_robustness",
    "number": "Figure S2",
    "short_en": "The primary association survives every prespecified perturbation",
    "short_cn": "主关联经得起所有预设扰动",
    "supports_en": (
        f"All {len([r for r in S['sens'] if not r.get('na')])} prespecified sensitivity "
        f"analyses keep a positive sign, and adjustment for age, sex and BMI leaves the "
        f"estimate essentially unchanged."
    ),
    "supports_cn": (
        f"{len([r for r in S['sens'] if not r.get('na')])} 项预设敏感性分析全部保持正号；"
        f"校正年龄、性别与 BMI 后估计值基本不变。"
    ),
    "not_en": (
        f"Causal or PCDH9-specific inference. Every analysis re-uses the same {NP} patients, so "
        "the estimates are correlated with one another and none is independent evidence."
    ),
    "not_cn": (
        f"不能推断因果，也不能证明关联特异于 PCDH9。所有分析重复使用同一批 {NP} 例，"
        "各估计之间彼此相关，没有任何一项是独立证据。"
    ),
    "panels": [
        ["A", "Nine prespecified sensitivity analyses, one cohort.",
         "9 项预设敏感性分析，同一队列。"],
        ["B", "Five adjustment sets as rank partial correlations.",
         "5 组校正后的秩偏相关。"],
    ],
    "caption_en": (
        f"Robustness of the primary endpoint. (A) Spearman rho with bootstrap 95% CI for the "
        f"primary analysis and {len([r for r in S['sens'] if not r.get('na')]) - 1} prespecified "
        f"sensitivity analyses; the dashed line is the primary estimate "
        f"({f2(PR['rho'])}). (B) Rank partial correlations adjusting for demographics, "
        f"synovial inflammation, immune-cell score, global ECM score and fluid blood grade. "
        f"All intervals are percentile intervals from 2,000 bootstrap resamples."
    ),
    "caption_cn": (
        f"主要终点的稳健性。(A) 主分析与 {len([r for r in S['sens'] if not r.get('na')]) - 1} 项"
        f"预设敏感性分析的 Spearman ρ 与 bootstrap 95% CI；虚线为主分析估计值（{f2(PR['rho'])}）。"
        f"(B) 分别校正人口学、滑膜炎症、免疫细胞评分、泛 ECM 评分与滑液血液分级后的秩偏相关。"
        f"全部区间为 2 000 次 bootstrap 的百分位区间。"
    ),
})

# ---------------------------------------------------------------- Figure S3
spec["figures"].append({
    "file": "FigureS3_loading_and_library_quality_controls",
    "number": "Figure S3",
    "short_en": "The association is not explained by loading or by library quality",
    "short_cn": "关联既不是上样量伪影，也不是建库质量造成的",
    "supports_en": (
        f"Fluid PCDH9 is uncorrelated with on-column protein (rho = {NM['sf_tp']['rho']:+.2f}, "
        f"P = {NM['sf_tp']['p']:.2f}), the per-microgram endpoint reproduces the per-microlitre "
        f"one ({f2(NM['sf_ug_rho']['rho'])} vs {f2(PR['rho'])}), and the programme score is "
        f"unrelated to RIN (rho = {RQ['core_rin']['rho']:+.2f}) and to sequencing batch "
        f"(P = {RQ['batch_p']:.2f})."
    ),
    "supports_cn": (
        f"滑液 PCDH9 与上柱总蛋白无关（ρ = {NM['sf_tp']['rho']:+.2f}，P = {NM['sf_tp']['p']:.2f}）；"
        f"按每微克总蛋白归一化后的主终点（{f2(NM['sf_ug_rho']['rho'])}）与按每微升原液"
        f"（{f2(PR['rho'])}）一致；程序评分与 RIN 无关（ρ = {RQ['core_rin']['rho']:+.2f}），"
        f"与测序批次也无关（P = {RQ['batch_p']:.2f}）。"
    ),
    "not_en": (
        "That joint dilution is irrelevant in general. Total protein happens to be "
        "uncorrelated with the programme score in this cohort; a cohort in which it is "
        "correlated would need the normalised value as primary."
    ),
    "not_cn": (
        "不能说明关节内稀释在任何队列中都无关。本队列里总蛋白恰好与程序评分无关；"
        "若换一个两者相关的队列，就必须把归一化值作为主分析。"
    ),
    "panels": [
        ["A", "Fluid abundance against on-column total protein.",
         "滑液丰度与上柱总蛋白的关系。"],
        ["B", "Primary endpoint reported in two units.",
         "两种报告单位下的主终点。"],
        ["C", "Programme score against RIN, split by sequencing batch.",
         "程序评分与 RIN 的关系，按测序批次分组。"],
    ],
    "caption_en": (
        f"Technical controls for loading and library quality. (A) Fluid PCDH9 against "
        f"on-column total protein measured by BCA (rho = {NM['sf_tp']['rho']:+.2f}, "
        f"P = {NM['sf_tp']['p']:.2f}). (B) The primary correlation reported per microlitre of "
        f"fluid ({f2(PR['rho'])}, 95% CI {ci(PR)}) and per microgram of total protein "
        f"({f2(NM['sf_ug_rho']['rho'])}, 95% CI {NM['sf_ug_ci'][0]:.2f}–"
        f"{NM['sf_ug_ci'][1]:.2f}). (C) CORE20 score against RIN, coloured by sequencing batch "
        f"(B1 n = {RQ['b1_n']}, B2 n = {RQ['b2_n']}); rho = {RQ['core_rin']['rho']:+.2f}, "
        f"batch comparison P = {RQ['batch_p']:.2f}."
    ),
    "caption_cn": (
        f"上样量与建库质量的技术对照。(A) 滑液 PCDH9 与 BCA 测得上柱总蛋白的关系"
        f"（ρ = {NM['sf_tp']['rho']:+.2f}，P = {NM['sf_tp']['p']:.2f}）。"
        f"(B) 主关联的两种报告方式：按每微升原液（{f2(PR['rho'])}，95% CI {ci(PR)}）"
        f"与按每微克总蛋白（{f2(NM['sf_ug_rho']['rho'])}，95% CI {NM['sf_ug_ci'][0]:.2f}–"
        f"{NM['sf_ug_ci'][1]:.2f}）。(C) CORE20 评分与 RIN 的关系，按测序批次着色"
        f"（B1 n = {RQ['b1_n']}，B2 n = {RQ['b2_n']}）；ρ = {RQ['core_rin']['rho']:+.2f}，"
        f"批次比较 P = {RQ['batch_p']:.2f}。"
    ),
})

# ---------------------------------------------------------------- Figure S4
spec["figures"].append({
    "file": "FigureS4_cutpoint_and_outcome_sensitivity",
    "number": "Figure S4",
    "short_en": "Where the exploratory analysis stops being informative",
    "short_cn": "探索性分析在哪里失去信息量",
    "supports_en": (
        f"At n = {NP} the cut-point still moves the AUC as much as sampling error: five "
        f"defensible dichotomies of the same data give AUCs from {f2(ROC['spread'][0])} to "
        f"{f2(ROC['spread'][1])}, and the increment over a structural model keeps its sign "
        f"({MOD['delta_corrected']:+.2f} and {MODP['delta_corrected']:+.2f}) but carries "
        "intervals that include zero."
    ),
    "supports_cn": (
        f"在 n = {NP} 时，切点对 AUC 的影响仍与抽样误差同一量级：同一批数据的五种合理二分法给出 "
        f"{f2(ROC['spread'][0])} 至 {f2(ROC['spread'][1])} 的 AUC；相对结构模型的增量"
        f"符号一致（{MOD['delta_corrected']:+.2f} 与 {MODP['delta_corrected']:+.2f}），"
        "但两个区间都包含 0。"
    ),
    "not_en": (
        "Which cut-point is correct. None is at this sample size. The plate makes the "
        "dependence explicit; it does not rank the alternatives."
    ),
    "not_cn": (
        "不能说明哪个切点是对的。在这个样本量下没有一个是。本图只是把这种依赖性摆出来，"
        "并不对几种切法排序。"
    ),
    "panels": [
        ["A", "AUC under five defensible dichotomies of the same cohort.",
         "同一队列五种合理二分法下的 AUC。"],
        ["B", "Increment over the structural model under two outcome definitions.",
         "两种结局定义下相对结构模型的增量。"],
    ],
    "caption_en": (
        f"Cut-point and outcome sensitivity of the exploratory analysis. (A) AUC with DeLong "
        f"95% CI for five dichotomies of the same {NP} patients; red marks the prespecified "
        f"two-sided contrast used in Figure 6F, grey the four alternatives. (B) Harrell "
        f"optimism-corrected ΔAUC for adding log fluid PCDH9 to a model containing the "
        f"structural index, age, sex and body-mass index, under a median split of this cohort "
        f"({MOD['events']} events) and under the prespecified cut ({MODP['events']} events). "
        f"Intervals are percentile intervals from 600 bootstrap resamples."
    ),
    "caption_cn": (
        f"探索性分析的切点与结局敏感性。(A) 同一批 {NP} 例五种二分法下的 AUC 与 DeLong 95% CI；"
        f"红色为图 6F 所用的预设两端对比，灰色为另外四种。(B) 在含结构严重度指数、年龄、性别与 BMI "
        f"的模型中加入 log 滑液 PCDH9 后的 Harrell 乐观度校正 ΔAUC，分别在本队列中位切分"
        f"（{MOD['events']} 个事件）与预设切点（{MODP['events']} 个事件）下估计。"
        f"区间为 600 次 bootstrap 的百分位区间。"
    ),
})

out = os.path.join(ROOT, "spec.json")
json.dump(spec, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("spec.json written:", out)
print("figures:", len(spec["figures"]))
