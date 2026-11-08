#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数据包自检：文件齐不齐、每个面板的头条数字是多少。

改完 CSV 跑一下，能立刻看到 n / 均值 / r 有没有按预期变化。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
PKG = Path(__file__).resolve().parent
D = PKG / "data"

NEED = [
    "data/_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T38_state_diff_cohort_adjusted.csv",
    "data/_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T30_deconv_donor_fractions.csv",
    "data/_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T32_deconv_meta.csv",
    "data/_external/GSE99662_W28_W29_重绘_20261019/source/within_cohort_effects.csv",
    "data/_external/GSE99662_W28_W29_重绘_20261019/source/random_effects_meta.csv",
    "data/sources/bulk_own_cohort_20261028/Figure7/data/Fig7A_box_samplelevel.tsv",
    "data/sources/bulk_own_cohort_20261028/Figure7/data/Fig7B_painscore_samplelevel.tsv",
    "data/sources/bulk_own_cohort_20261028/Figure7/data/Fig7DE_pooled_z_samplelevel.tsv",
    "data/sources/bulk_own_cohort_20261028/Figure7/data/Fig7E_cohort_deltas.tsv",
    "data/sources/bulk_own_cohort_20261028/Figure7/data/Fig7_summary_stats.tsv",
    "data/identity_results/bulk_donor_scores.csv",
    "data/identity_results/stats_bulk.json",
    "data/_external/figure_audit/plot_data/figS1_tidy.csv",
    "data/_external/figure_audit/editable/data.py",
    "data/_external/figure_audit/editable/stats.py",
    "data/_external/PCDH9_integrated_reproduction_20261024/gwas_reproduced/tables/10_selected_forest_source.csv",
    "data/_external/PCDH9_integrated_reproduction_20261024/gwas_reproduced/tables/05_Mocci_region_plot_source.tsv",
    "data/derived/x_ppsd_stats.json",
    "data/derived/x_ra_donor_fractions.csv",
    "data/derived/x_ra_stats.json",
    "data/derived/y_ra_donor_scores.csv",
    "data/derived/y_ra_stats.json",
    "scripts/build_figure4_4col.py",
    "scripts/recompose_fig4_v7.py",
    "scripts/journal_style.py",
    "scripts/compute_x_ra.py",
    "scripts/compute_y_ra.py",
    "scripts/verify_4col.py",
]

print(f"包内文件 {len(NEED)} 个")
missing = [f for f in NEED if not (PKG / f).exists()]
if missing:
    for f in missing:
        print(f"  缺: {f}")
    raise SystemExit(1)
tot = sum((PKG / f).stat().st_size for f in NEED)
print(f"合计 {tot/1e6:.2f} MB，全部存在\n")

G = "data/_external/GSE99662_W28_W29_重绘_20261019/source"
F7 = "data/sources/bulk_own_cohort_20261028/Figure7/data"

t38 = pd.read_csv(PKG / G / "deconv_v2/T38_state_diff_cohort_adjusted.csv")
print(f"A  {len(t38):>4} 个状态，NR-FB core diff = {t38.set_index('state').loc['NR-FB core','diff']*100:+.2f} pp")

t30 = pd.read_csv(PKG / G / "deconv_v2/T30_deconv_donor_fractions.csv")
t30s = t30[t30.method == "svr"]
nb = t30s.groupby("condition").size().to_dict()
print(f"B  svr 供体 Control {nb.get('Normal',0)} / OA {nb.get('OA',0)}；"
      f"NR-FB core 均值 {t30s[t30s.condition=='Normal']['NR-FB core'].mean()*100:.2f}% / "
      f"{t30s[t30s.condition=='OA']['NR-FB core'].mean()*100:.2f}%")

eff = pd.read_csv(PKG / G / "within_cohort_effects.csv")
effc = eff[eff.module == "CORE20"]
meta = pd.read_csv(PKG / G / "random_effects_meta.csv")
metac = meta[(meta.scope == "all_mixed_cohorts") & (meta.module == "CORE20")].iloc[0]
print(f"C  {len(effc)} 个队列（原表 {len(eff)} 行），合并 g = {metac.g:.3f} "
      f"[{metac.ci_low:.3f}, {metac.ci_high:.3f}]")

bd = pd.read_csv(PKG / "data/identity_results/bulk_donor_scores.csv")
bst = json.loads((PKG / "data/identity_results/stats_bulk.json").read_text(encoding="utf-8"))
print(f"D  {len(bd)} 名供体，r(PCDH9~CORE20) = {bst['pcdh9_core20']['r']:.3f} "
      f"({bst['pcdh9_core20']['ci'][0]:.2f}–{bst['pcdh9_core20']['ci'][1]:.2f})")
print(f"G  同一批 {len(bd)} 名供体，r(PCDH9~NEURAL) = {bst['pcdh9_neural']['r']:.3f}")

poolz = pd.read_csv(PKG / F7 / "Fig7DE_pooled_z_samplelevel.tsv", sep="\t")
print(f"E  {len(poolz)} 个样本：" + "、".join(f"{k} {v}" for k, v in poolz.group.value_counts().items()))

deltas = pd.read_csv(PKG / F7 / "Fig7E_cohort_deltas.tsv", sep="\t")
print(f"F  {len(deltas)} 个队列，Δz 范围 {deltas.delta_z.min():+.2f} ~ {deltas.delta_z.max():+.2f}")

box = pd.read_csv(PKG / F7 / "Fig7A_box_samplelevel.tsv", sep="\t")
p1 = box[box.cohort == "P1 (pain)"]
hi = p1[p1.group == "High"].PCDH9_log2cpm
lo = p1[p1.group == "Low"].PCDH9_log2cpm
print(f"H  P1 疼痛 {len(hi)}/{len(lo)}，High − Low = {hi.mean()-lo.mean():+.2f} log2 CPM")

xs = json.loads((PKG / "data/derived/x_ppsd_stats.json").read_text(encoding="utf-8"))
print(f"I  {len(xs['rows'])} 行（{sum(1 for r in xs['rows'] if r['pooled'])} 行参与合并），"
      f"随机效应 {xs['overall']['d']:.3f} [{xs['overall']['lo']:.3f}, {xs['overall']['hi']:.3f}]，"
      f"I² = {xs['overall']['I2']:.0f}%")

fs1 = pd.read_csv(PKG / "data/_external/figure_audit/plot_data/figS1_tidy.csv")
print(f"J–L {len(fs1)} 例配对样本；蛋白 {fs1.protein_fmol_per_ug.min():.2f}–"
      f"{fs1.protein_fmol_per_ug.max():.2f} fmol/µg")

xra = pd.read_csv(PKG / "data/derived/x_ra_donor_fractions.csv")
xrj = json.loads((PKG / "data/derived/x_ra_stats.json").read_text(encoding="utf-8"))
gs = xrj["group_stats"]
print(f"M  Control {gs['Normal']['n']} / OA {gs['OA']['n']} / RA {gs['RA']['n']}；"
      f"均值 {gs['Normal']['mean']:.2f} / {gs['OA']['mean']:.2f} / {gs['RA']['mean']:.2f} %；"
      f"OA−RA {xrj['within_pooled']['d']:+.2f}% P = {xrj['within_pooled']['p']:.3f}")

yra = pd.read_csv(PKG / "data/derived/y_ra_donor_scores.csv")
yrj = json.loads((PKG / "data/derived/y_ra_stats.json").read_text(encoding="utf-8"))
print(f"N  {len(yra)} 名供体（" + "、".join(f"{k} {v['n']}" for k, v in yrj["groups"].items() if k != "all")
      + f"）；r all = {yrj['groups']['all']['r']:+.3f}、RA = {yrj['groups']['RA']['r']:+.3f}；"
      f"{yrj['n_cohorts_positive_core20']}/{yrj['n_cohorts_with_r']} 队列正向")

# 与统计量一致性（和生成脚本里的断言同一套规则）
for g, k in [("Normal", "Normal"), ("OA", "OA"), ("RA", "RA")]:
    v = xra.loc[xra.group == g, "NR-FB core"].to_numpy() * 100
    assert len(v) == gs[k]["n"] and abs(v.mean() - gs[k]["mean"]) < 1e-6, f"M 的 {g} 与 json 不同步"
for g in ("all", "Control", "OA", "RA"):
    d = yra if g == "all" else yra[yra.group == g]
    r = float(np.corrcoef(d.PCDH9, d.CORE20)[0, 1])
    assert len(d) == yrj["groups"][g]["n"] and abs(r - yrj["groups"][g]["r"]) < 1e-6, \
        f"N 的 {g} 与 json 不同步"
print("\nOK：文件齐全，CSV 与统计量 JSON 同步")
