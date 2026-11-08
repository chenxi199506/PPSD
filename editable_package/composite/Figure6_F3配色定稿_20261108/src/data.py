"""
data.py — 只做一件事：把 plot_data/ 里的 CSV 读成 Python 对象。

所有图都从这里取数。要换数据，替换 plot_data/ 下的 CSV 即可，绘图代码不用动。
"""

from __future__ import annotations

import csv
import os
from collections import OrderedDict, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "plot_data")


def _rows(name: str):
    # utf-8-sig：扁平表由外部脚本导出，带 BOM，用 utf-8 会把 BOM 读进第一个列名
    with open(os.path.join(DATA, name), newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


# ---------------------------------------------------------------- 顺序定义
G5 = ["Untreated", "NT siRNA", "siRNA-1", "siRNA-2", "Rescue"]      # Figure 1 的 5 个条件
G4 = ["NT siRNA", "siRNA-1", "siRNA-2", "Rescue"]                   # Figure 1B 的 4 个条件
M5 = ["NT-CM", "KD-CM", "Rescue", "Vehicle", "Mock"]                # Figure 5 的 5 组
M5_KEY = {"NT-CM": "nt", "KD-CM": "kd", "Rescue": "rescue",
          "Vehicle": "vehicle", "Mock": "mock"}

GENE_BLOCKS = [
    ("NR-FB core",  ["CXCL12", "VCAN", "IGF1", "SMOC1", "FGF7"]),
    ("Neural",      ["PLXNA4", "PTPRD", "SLIT2", "SLIT3", "NRP1"]),
    ("Target/ECM",  ["PCDH9", "COL1A1", "COL3A1"]),
]

CMP_ORDER = ["Untreated vs NT", "KD1 vs NT", "KD2 vs NT",
             "Rescue vs KD1", "Rescue vs NT"]
CMP_LABEL = ["Ut vs NT", "si-1 vs NT", "si-2 vs NT",
             "Rescue vs si-1", "Rescue vs NT"]
NEURAL_ORDER = ["PLXNA4", "PTPRD", "SLIT2", "SLIT3", "NRP1"]


# ---------------------------------------------------------------- Figure 1
def fig1b():
    """敲低效率。返回 {group: [(donor, value), ...]}。"""
    out = defaultdict(list)
    for r in _rows("fig1B_knockdown.csv"):
        out[r["GroupLabel"]].append((r["Donor"], float(r["relative_to_NT"])))
    return OrderedDict((g, out[g]) for g in G4 if g in out)


def fig1c():
    out = defaultdict(list)
    for r in _rows("fig1C_nrfb_core.csv"):
        out[r["GroupLabel"]].append((r["Donor"], float(r["NRFB_core_score"])))
    return OrderedDict((g, out[g]) for g in G5 if g in out)


def fig1d(kind: str = "z"):
    """热图矩阵。kind='z' 画图用；'log2expr' 是底层表达，换归一化时用。"""
    fname = {"z": "fig1D_heatmap_z.csv",
             "log2expr": "fig1D_heatmap_log2expr.csv"}[kind]
    rows = _rows(fname)
    genes = [r["Gene"] for r in rows]
    cols = [k for k in rows[0] if k != "Gene"]
    mat = [[float(r[c]) for c in cols] for r in rows]
    return genes, cols, mat


def fig1e():
    """神经基因点图。返回 {(gene, comparison): (log2FC, q, neg_log10_q)}。"""
    out = {}
    for r in _rows("fig1E_neural_genes.csv"):
        out[(r["Gene"], r["Comparison"])] = (
            float(r["log2FC"]), float(r["BH_q"]), float(r["neg_log10_q"]))
    return out


def fig1f():
    out = defaultdict(list)
    for r in _rows("fig1F_cxcl12.csv"):
        out[r["GroupLabel"]].append((r["Donor"], float(r["pg_per_1e5_cells"])))
    return OrderedDict((g, out[g]) for g in G5 if g in out)


# ---------------------------------------------------------------- Figure 5
def fig5_wells():
    """84 孔明细，按组归并。返回 {group_label: {metric: [values]}}。"""
    key = {"G1": "NT-CM", "G2": "KD-CM", "G3": "Rescue",
           "G4": "Vehicle", "G5": "Mock"}
    out = {g: defaultdict(list) for g in M5}
    for r in _rows("fig5_well_level_84.csv"):
        g = key[r["Group"]]
        out[g]["firing"].append(float(r["MeanFiringRate_Hz"]))
        out[g]["isi"].append(float(r["MeanISI_ms"]))
        out[g]["nburst"].append(float(r["NetworkBurstFrequency_perMin"]))
        out[g]["donor"].append(r["Donor"])
    return out


def fig5_traj():
    """逐供体轨迹：[(donor, NT_Hz, KD%, Rescue%), ...]。"""
    return [(r["Donor"], float(r["NT_Hz"]), float(r["KD_pct_of_NT"]),
             float(r["Rescue_pct_of_NT"]))
            for r in _rows("fig5_donor_trajectory.csv")]


# ---------------------------------------------------------------- Figure S1
def figS1():
    """逐供体扁平表（唯一真源：figS1_tidy.csv，10 行 × 14 列）。

    返回 list of dict，键名做了短名映射，图里直接用。
    """
    keys = {
        "patient": "id", "protein_fmol_per_ug": "protein",
        "peptide1_fmol_per_ug": "p1", "peptide2_fmol_per_ug": "p2",
        "peptide3_fmol_per_ug": "p3", "mrna_rel_2ddct": "mrna",
        "nrfb_score": "nrfb", "womac_pain": "pain",
        "kl_grade": "kl", "age": "age", "sex": "sex", "passage": "passage",
    }
    out = []
    for r in _rows("figS1_tidy.csv"):
        d = {}
        for k, v in keys.items():
            raw = r[k]
            d[v] = raw if v in ("id", "kl", "sex", "passage") else float(raw)
        out.append(d)
    return out


def figS1_peptides():
    """面板 A 的肽段元数据。

    注意：L/H 比值与技术 CV 来自采集端（data.json），无法从扁平表反推，
    因此单独存一份 CSV；其余各列同理。改肽段表就改这个文件。
    """
    return _rows("figS1_peptides.csv")
