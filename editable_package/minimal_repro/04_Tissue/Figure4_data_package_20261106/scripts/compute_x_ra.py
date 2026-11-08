#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""X 面板统计：给 B 图（NR-FB transcript contribution, Control vs OA）补一个 RA 组。

为什么必须现算：
  归档的 T30_deconv_donor_fractions.csv 只有 Normal / OA 两组（原脚本显式
  `disease_class.isin(["OA","Normal"])`，RA 被排除）。滑膜库里 RA 是
  `disease_class = Inflammatory` 下的 499 个样本 / 351 名供体，从未跑过反卷积。

本脚本做什么：
  用**与 10_deconv_bulk_v2.py 完全相同的**参考谱、marker panel、qnorm 目标、
  nu-SVR 估计器，只把样本集扩到 RA，重跑一遍。为了让新 RA 值与旧 OA/对照值
  严格同尺度，脚本会把 OA/对照也重算一遍，并与 T30 逐供体比对，要求一致到 1e-9。

输出：
  x_ra_donor_fractions.csv   供体级分数（Control / OA / RA）
  x_ra_stats.json            组间检验 + 队列内 RA−OA 随机效应合并
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from scipy import stats as SS

sys.stdout.reconfigure(encoding="utf-8")

CODE = r"home_root/WorkBuddy/2026-10-19-21-13-42/nrfb_bulk_state/code"
sys.path.insert(0, CODE)
from config import BULK_MAT, BULK_META, CACHE, TAB  # noqa: E402
from deconv_lib import select_markers  # noqa: E402

ROOT = Path(r"E:/NRFB_atlas_plate_20261104")
HERE = Path(__file__).resolve().parent
OUTD = HERE.parent
T30 = ROOT / "_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T30_deconv_donor_fractions.csv"

NRFB = "NR-FB core"
FIBRO = ["AP-1 stress", "COMP+ transitional", "DKK3+ intermediate", "NR-FB core",
         "PRG4+ lining", "Proliferating", "Remodeling", "Sublining",
         "Transitional activated"]

# ------------------------------------------------------------ 参考谱 / panel --
prof = pd.read_parquet(os.path.join(CACHE, "ref_v2_profiles_cpm.parquet"))
states = list(prof.index)
markers = select_markers(prof, n_top=80, exclusive=False)
panel = [g for g in dict.fromkeys(markers.gene.tolist())]
print(f"reference states: {len(states)}  marker panel: {len(panel)} genes")

mat = pq.read_table(BULK_MAT).to_pandas().set_index("gene_key").astype("float32")
meta = pd.read_csv(BULK_META, sep="\t").set_index("sample_uid")
panel_ok = [g for g in panel if g in mat.index]
print(f"panel present in bulk: {len(panel_ok)} / {len(panel)}")

ref_mean = prof.mean(axis=0)
ref_mean = ref_mean / ref_mean.sum() * 1e6
target = np.sort(np.log2(ref_mean[panel_ok].values + 1))


def qnorm(vec):
    ok = ~np.isnan(vec)
    v = vec[ok]
    if ok.sum() < 10:
        return np.zeros_like(vec)
    r = np.argsort(np.argsort(v))
    out = np.zeros_like(vec)
    out[ok] = np.interp(r / (len(v) - 1), np.linspace(0, 1, len(target)), target)
    return out


def build_signature(genes):
    A = prof.loc[:, genes].to_numpy(dtype=float)
    A = np.nan_to_num(A, nan=0.0, posinf=0.0, neginf=0.0)
    A = np.clip(A, 0, None)
    A = A / np.maximum(A.sum(axis=1, keepdims=True), 1e-9)
    return A.T


def fit_svr(y, S, nus=(0.25, 0.5, 0.75)):
    from sklearn.svm import NuSVR
    yz = (y - y.mean()) / (y.std() + 1e-12)
    Sz = (S - S.mean(0)) / (S.std(0) + 1e-12)
    best, best_rmse = None, np.inf
    for nu in nus:
        m = NuSVR(kernel="linear", C=1.0, nu=nu, cache_size=400)
        m.fit(Sz, yz)
        rmse = float(np.sqrt(np.mean((yz - m.predict(Sz)) ** 2)))
        if rmse < best_rmse:
            best_rmse, best = rmse, m.coef_.ravel().copy()
    w = np.clip(best, 0, None)
    s = w.sum()
    return w / s if s > 0 else np.full(S.shape[1], 1.0 / S.shape[1])


# ------------------------------------------------------------------ 队列集合 --
aud = pd.read_csv(os.path.join(TAB, "T02_primary_case_control_cohorts.csv"))
coh_oa = [c for c in aud.cohort_id.tolist() if c in set(meta.cohort_id)]
coh_ra = sorted(set(meta.loc[meta.disease == "RA", "cohort_id"]))
print(f"\nOA/Normal cohorts (T30 口径): {len(coh_oa)} -> {coh_oa}")
print(f"RA cohorts: {len(coh_ra)} -> {coh_ra}")

rows = []
S = build_signature(panel_ok)
for cid in sorted(set(coh_oa) | set(coh_ra)):
    m = meta[meta.cohort_id == cid]
    keep = pd.Series(False, index=m.index)
    if cid in coh_oa:
        keep |= m.disease_class.isin(["OA", "Normal"])
    keep |= (m.disease == "RA")
    sub = m[keep].copy()
    if sub.empty:
        continue
    cols = [c for c in sub.index if c in mat.columns]
    if not cols:
        continue
    sub = sub.loc[cols]
    X = mat.loc[panel_ok, cols].astype(float)
    Xl = 2 ** np.clip(X.values, 0, 20) - 1
    Xl = np.where(np.isnan(Xl), np.nan, Xl)
    Xq = np.column_stack([qnorm(Xl[:, i]) for i in range(Xl.shape[1])])
    Xl = 2 ** np.clip(Xq, 0, 20) - 1

    est = []
    for j in range(Xl.shape[1]):
        y = Xl[:, j]
        y = y / max(y.sum(), 1e-9)
        est.append(fit_svr(y, S))
    est = pd.DataFrame(est, index=cols, columns=states)
    est["cohort_id"] = cid
    est["condition"] = sub.disease_class.values
    est["disease"] = sub.disease.values
    est["donor_key"] = sub.donor_key.astype(str).values
    est["method"] = "svr"
    rows.append(est)
    n_ra = int((sub.disease == "RA").sum())
    print(f"  {cid:<24} samples {len(cols):>3}  (RA {n_ra:>3})", flush=True)

frac = pd.concat(rows)
frac["fibro_total"] = frac[FIBRO].sum(axis=1)
frac["nrf_of_fibro"] = frac[NRFB] / frac.fibro_total.replace(0, np.nan)

num_cols = states + ["fibro_total", "nrf_of_fibro"]
donor = (frac.groupby(["cohort_id", "method", "donor_key", "condition", "disease"],
                      as_index=False)[num_cols].median())
donor["group"] = np.where(donor.disease == "RA", "RA", donor.condition)
print("\ndonor-level rows:", len(donor))
print(donor.group.value_counts().to_string())

# ------------------------------------------------------------------ 复现校验 --
t30 = pd.read_csv(T30)
t30 = t30[t30.method == "svr"][["cohort_id", "donor_key", "condition", NRFB]]
t30["donor_key"] = t30.donor_key.astype(str)
chk = donor[donor.group.isin(["OA", "Normal"])].merge(
    t30, on=["cohort_id", "donor_key", "condition"], suffixes=("_new", "_t30"))
assert len(chk) == len(t30), f"供体数不一致: 重算 {len(chk)} vs T30 {len(t30)}"
diff = float(np.nanmax(np.abs(chk[f"{NRFB}_new"] - chk[f"{NRFB}_t30"])))
print(f"\n[复现校验] {len(chk)} 个 OA/对照供体 vs 归档 T30：max |Δ| = {diff:.3e}")
assert diff < 1e-9, f"未能复现 T30（max Δ = {diff:.3e}），RA 与旧值不同尺度，停止"
print("  OK：同一参考谱 / 同一 panel / 同一估计器，RA 与旧值严格同尺度")

# ------------------------------------------------------------------ 统计 ------
def welch(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a.mean() - b.mean()
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = float(np.sqrt(va + vb))
    df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
    t = SS.t.ppf(0.975, df)
    return dict(d=float(d), se=se, lo=float(d - t * se), hi=float(d + t * se),
                p=float(2 * SS.t.sf(abs(d / se), df)), df=float(df),
                n=(len(a), len(b)))


def hedges(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    nx, ny = len(a), len(b)
    sp = np.sqrt(((nx - 1) * a.var(ddof=1) + (ny - 1) * b.var(ddof=1)) / (nx + ny - 2))
    J = 1 - 3 / (4 * (nx + ny) - 9)
    return float(J * (a.mean() - b.mean()) / sp)


G = {g: donor.loc[donor.group == g, NRFB].to_numpy() * 100 for g in ["Normal", "OA", "RA"]}
print("\n=== NR-FB transcript contribution (%) by group ===")
for g, v in G.items():
    print(f"  {g:<7} n={len(v):>3}  mean={v.mean():.3f}  sd={v.std(ddof=1):.3f} "
          f"median={np.median(v):.3f}  IQR={np.percentile(v, 75) - np.percentile(v, 25):.3f}")

comparisons = {}
for lab, (a, b) in {"Control vs OA": ("Normal", "OA"),
                    "OA vs RA": ("OA", "RA"),
                    "Control vs RA": ("Normal", "RA")}.items():
    r = welch(G[a], G[b])
    r["g"] = hedges(G[a], G[b])
    comparisons[lab] = r
    print(f"  {lab:<14} Δ={r['d']:+.3f}% [{r['lo']:+.3f},{r['hi']:+.3f}] "
          f"P={r['p']:.3g}  g={r['g']:+.2f}")

# 队列内 RA − OA（8 个队列同时有两者），DL 随机效应
within = []
for cid, g in donor.groupby("cohort_id"):
    oa = g.loc[g.group == "OA", NRFB].to_numpy() * 100
    ra = g.loc[g.group == "RA", NRFB].to_numpy() * 100
    if len(oa) < 2 or len(ra) < 2:
        continue
    r = welch(ra, oa)
    within.append(dict(cohort_id=cid, n_OA=len(oa), n_RA=len(ra),
                       d=r["d"], se=r["se"], lo=r["lo"], hi=r["hi"], p=r["p"],
                       g=hedges(ra, oa)))
W = pd.DataFrame(within)
print(f"\n=== 队列内 RA − OA（{len(W)} 个队列，NR-FB %）===")
print(W.round(3).to_string(index=False))

w = 1 / W.se.to_numpy() ** 2
fe = float((w * W.d.to_numpy()).sum() / w.sum())
Q = float((w * (W.d.to_numpy() - fe) ** 2).sum())
dfree = len(W) - 1
C = float(w.sum() - (w ** 2).sum() / w.sum())
tau2 = max(0.0, (Q - dfree) / C) if C > 0 else 0.0
wr = 1 / (W.se.to_numpy() ** 2 + tau2)
re_est = float((wr * W.d.to_numpy()).sum() / wr.sum())
re_se = float(np.sqrt(1 / wr.sum()))
re_p = float(2 * SS.norm.sf(abs(re_est / re_se)))
I2 = max(0.0, (Q - dfree) / Q) * 100 if Q > 0 else 0.0
print(f"  DL random-effects: {re_est:+.3f} [{re_est - 1.96 * re_se:+.3f}, "
      f"{re_est + 1.96 * re_se:+.3f}]  P={re_p:.3g}  "
      f"Q={Q:.2f} df={dfree} I2={I2:.0f}%")

payload = dict(
    group_stats={g: dict(n=int(len(v)), mean=float(v.mean()), sd=float(v.std(ddof=1)),
                         median=float(np.median(v)),
                         q1=float(np.percentile(v, 25)), q3=float(np.percentile(v, 75)))
                 for g, v in G.items()},
    comparisons=comparisons,
    within_cohort=W.to_dict(orient="records"),
    within_pooled=dict(k=int(len(W)), d=re_est, se=re_se,
                       lo=re_est - 1.96 * re_se, hi=re_est + 1.96 * re_se,
                       p=re_p, Q=Q, df=int(dfree), I2=I2, tau2=tau2,
                       fe=fe, method="DerSimonian-Laird random effects"),
    provenance=dict(
        reference="ref_v2_profiles_cpm.parquet (12-donor non-fibro + fibro atlas states)",
        markers="select_markers(n_top=80, exclusive=False) -> %d genes" % len(panel_ok),
        estimator="nu-SVR (CIBERSORT-style), nu sweep 0.25/0.5/0.75, negative clamp, rescale",
        bulk="core_matrix_log2.parquet + samples_metadata.tsv",
        t30_reproduction_max_abs_diff=diff,
        n_t30_donors_checked=int(len(chk)),
        ra_cohorts=coh_ra,
        note="RA = disease_class Inflammatory & disease == RA; all tissue_group synovium",
    ),
)
(OUTD / "x_ra_stats.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
donor.to_csv(OUTD / "x_ra_donor_fractions.csv", index=False, encoding="utf-8-sig")
print("\nwrote x_ra_stats.json / x_ra_donor_fractions.csv")
