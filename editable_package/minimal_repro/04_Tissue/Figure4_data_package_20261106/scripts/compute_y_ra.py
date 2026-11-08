#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Y 面板统计：PCDH9 ~ CORE20 散点，加 RA 组（D 图的三色扩展版）。

数据纪律与 `09_NRFB身份定义_20261104/00_脚本/02b_bulk.py` 完全一致——
直接 import 该脚本的 fetch_cohort / normalise / 基因集，不另写一套：
  - 每个队列单独归一化（raw counts → log2 CPM，FPKM/TPM → log2(x+1)，芯片原值）；
  - 每基因在队列内 z-score，跨平台绝对值差异不会变成「相关」；
  - 技术重复按 within_study_donor_key 取均值；
  - 队列内有效供体 < 8 的不参与。

与 02b 的唯一差别：02b 只收 OA/Control，这里把 RA 一起收进来做 z 基准，
因为 Y 面板问的就是「RA 里这条关系还在不在」。

校验：不含 RA 的队列，重算值必须与归档 bulk_donor_scores.csv 逐供体一致。
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from scipy import stats as SS

sys.stdout.reconfigure(encoding="utf-8")

SRC = Path(r"experiment_root//09_NRFB身份定义_20261104/00_脚本/02b_bulk.py")
ARCH = Path(r"experiment_root//09_NRFB身份定义_20261104/02_结果/bulk_donor_scores.csv")
HERE = Path(__file__).resolve().parent
OUTD = HERE.parent

_spec = importlib.util.spec_from_file_location("bulk02b", SRC)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)          # 只定义函数/常量，main() 有 __main__ 守卫

print(f"CORE20 = {len(m.CORE20)} genes; MIN_N = {m.MIN_N}")

con = duckdb.connect(m.DB, read_only=True)
blocks = con.execute("""
    select s.cohort_id, s.matrix_table, c.expression_unit,
           sum(case when s.disease_group in ('OA','Control','RA') then 1 else 0 end) n
    from sample_annotation s left join cohorts c on s.cohort_id = c.cohort_id
    where s.disease_group in ('OA','Control','RA')
    group by 1,2,3 having n >= ? order by n desc
""", [m.MIN_N]).df()
print(f"\n候选队列块: {len(blocks)}")

rows = []
for _, row in blocks.iterrows():
    coh, mt = row["cohort_id"], row["matrix_table"]
    expr, _ = m.fetch_cohort(con, coh, mt)
    if expr is None or expr.shape[0] < 20:
        print(f"  skip {coh}/{mt}: no genes")
        continue
    reg = con.execute(
        "select column_name, within_study_donor_key from column_registry "
        "where matrix_table = ? and column_role = 'expression'", [mt]).df()
    ann = con.execute(
        "select expression_column, disease_group from sample_annotation "
        "where matrix_table = ? and disease_group in ('OA','Control','RA')", [mt]).df()
    cols = [c for c in expr.columns if c in set(ann["expression_column"])]
    if len(cols) < m.MIN_N:
        print(f"  skip {coh}/{mt}: {len(cols)} cols matched")
        continue
    expr = expr[cols]
    key = reg.set_index("column_name")["within_study_donor_key"]
    grp = pd.Series({c: (key.get(c) if isinstance(key.get(c), str) else c) for c in cols})
    expr = expr.T.groupby(grp.values).mean().T
    grp_donor = pd.Series(expr.columns).map(
        ann.set_index("expression_column")["disease_group"].groupby(grp.values).first())
    if expr.shape[1] < m.MIN_N:
        print(f"  skip {coh}/{mt}: {expr.shape[1]} donors")
        continue

    X = m.normalise(expr, row["expression_unit"]).replace([np.inf, -np.inf], np.nan)
    X = X.dropna(axis=1, how="all")
    z = X.sub(X.mean(axis=1), axis=0).div(X.std(axis=1).replace(0, np.nan), axis=0)
    z = z.dropna(axis=0, how="all")

    d = pd.DataFrame({
        "cohort": coh, "matrix_table": mt, "sample": expr.columns.astype(str),
        "group": grp_donor.values,
        "unit": row["expression_unit"],
        "PCDH9": z.loc["PCDH9"].values if "PCDH9" in z.index else np.nan,
    })
    for tag, genes in m.MODS.items():
        present = [g for g in genes if g in z.index]
        d[tag] = z.loc[present].mean(axis=0).values if present else np.nan
        d[f"{tag}_n"] = len(present)
    rows.append(d)
    nra = int((d.group == "RA").sum())
    print(f"  {coh:<24} {mt:<24} donors {expr.shape[1]:>3} (RA {nra:>3})")

B = pd.concat(rows, ignore_index=True).dropna(subset=["PCDH9", "CORE20"])
B = B[B.group.isin(["Control", "OA", "RA"])]
print(f"\n总供体 {len(B)}（{B.cohort.nunique()} 队列）")
print(B.group.value_counts().to_string())

# ---------------------------------------------------------------- 复现校验 ----
arch = pd.read_csv(ARCH)
no_ra = sorted(set(B.cohort) - set(B.loc[B.group == "RA", "cohort"]))
sub = B[B.cohort.isin(no_ra)][["cohort", "sample", "group", "PCDH9", "CORE20"]]
j = sub.merge(arch[["cohort", "sample", "group", "PCDH9", "CORE20"]],
              on=["cohort", "sample", "group"], suffixes=("_new", "_arch"))
d_core = float(np.nanmax(np.abs(j["CORE20_new"] - j["CORE20_arch"])))
d_pcdh = float(np.nanmax(np.abs(j["PCDH9_new"] - j["PCDH9_arch"])))
print(f"\n[复现校验] 无 RA 队列 {len(no_ra)} 个，{len(j)} 供体 vs 归档："
      f"max|ΔCORE20| = {d_core:.3e}  max|ΔPCDH9| = {d_pcdh:.3e}")
assert len(j) > 100 and d_core < 1e-9 and d_pcdh < 1e-9, "无 RA 队列未能复现归档值，停止"
print("  OK：无 RA 队列与归档逐供体一致，RA 与旧值同尺度")

# ---------------------------------------------------------------- 相关 --------
def r_of(df):
    return float(np.corrcoef(df.PCDH9, df.CORE20)[0, 1])


def rho_of(df):
    return float(SS.spearmanr(df.PCDH9, df.CORE20).statistic)


def boot_ci(df, fn=r_of, nboot=2000, seed=20261106):
    rng = np.random.default_rng(seed)
    cohorts = df.cohort.unique()
    idx = {c: df.index[df.cohort == c].to_numpy() for c in cohorts}
    vals = []
    for _ in range(nboot):
        pick = rng.choice(cohorts, len(cohorts), True)
        ii = np.concatenate([rng.choice(idx[c], len(idx[c]), True) for c in pick])
        s = df.loc[ii]
        vals.append(fn(s))
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


groups = {"all": B, "Control": B[B.group == "Control"],
          "OA": B[B.group == "OA"], "RA": B[B.group == "RA"]}
stats_out = {}
print("\n=== PCDH9 ~ CORE20 ===")
for g, df in groups.items():
    if len(df) < 5:
        continue
    r, ci = r_of(df), boot_ci(df)
    rho = rho_of(df)
    p = float(SS.pearsonr(df.PCDH9, df.CORE20).pvalue)
    stats_out[g] = dict(n=int(len(df)), n_cohorts=int(df.cohort.nunique()),
                        r=r, ci=ci, rho=rho, p=p,
                        slope=float(np.polyfit(df.CORE20, df.PCDH9, 1)[0]))
    print(f"  {g:<8} n={len(df):>3} cohorts={df.cohort.nunique():>2}  "
          f"r={r:+.3f} ({ci[0]:+.3f}–{ci[1]:+.3f})  rho={rho:+.3f}  P={p:.3g}")

# 队列内（去队列中心）的合并相关：控制队列构成
within = []
for coh, g in B.groupby("cohort"):
    if len(g) >= 5:
        within.append(dict(cohort=coh, n=len(g), r=r_of(g),
                           n_RA=int((g.group == "RA").sum())))
W = pd.DataFrame(within)
npos = int((W.r > 0).sum())
print(f"\n队列内相关：{len(W)} 个队列，正向 {npos}/{len(W)}，中位 r = {W.r.median():+.3f}")
print(W.round(3).to_string(index=False))

payload = dict(groups=stats_out, within_cohort=W.to_dict(orient="records"),
               n_cohorts_positive_core20=npos, n_cohorts_with_r=len(W),
               provenance=dict(
                   pipeline="02b_bulk.py::fetch_cohort + normalise（直接 import，未改写）",
                   z_basis="每队列内每基因 z-score，基准含 Control/OA/RA",
                   core20_genes=m.CORE20, min_donors=m.MIN_N,
                   archived_reproduction_max_abs_diff=dict(
                       CORE20=d_core, PCDH9=d_pcdh, n_donors=int(len(j)),
                       cohorts_without_RA=no_ra),
                   note="RA 只进入 z 基准与散点，不改变 02b 的归档表"))
(OUTD / "y_ra_stats.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                                     encoding="utf-8")
B.to_csv(OUTD / "y_ra_donor_scores.csv", index=False, encoding="utf-8-sig")
con.close()
print("\nwrote y_ra_stats.json / y_ra_donor_scores.csv")
