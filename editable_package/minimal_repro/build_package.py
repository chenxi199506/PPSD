#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重建「图版 01–07 最小复现总包」。

只读原项目、复制到本包、生成逐 panel 依赖表 / MANIFEST / 校验脚本 / zip。
运行：python build_package.py
"""
from __future__ import annotations

import csv
import hashlib
import os
import subprocess
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

E = Path("E:/NRFB_atlas_plate_20261104")
C = Path("experiment_root/")
OUT = E / "24_图版01-07_最小复现总包_20261106"
OUT.mkdir(parents=True, exist_ok=True)

PAIRS: list[tuple[str, Path]] = []
MISSING: list[str] = []


def A(dst: str, src: Path) -> None:
    PAIRS.append((dst, src))


def ADIR(dst_prefix: str, src_dir: Path, exts: tuple[str, ...], recursive: bool = False) -> None:
    it = src_dir.rglob("*") if recursive else src_dir.glob("*")
    for f in sorted(it):
        if f.is_file() and f.suffix.lower() in exts:
            rel = f.relative_to(src_dir).as_posix()
            A(f"{dst_prefix}/{rel}", f)


def ATREE(dst_prefix: str, src_dir: Path) -> None:
    for f in sorted(src_dir.rglob("*")):
        if f.is_file():
            A(f"{dst_prefix}/{f.relative_to(src_dir).as_posix()}", f)


# ---------------------------------------------------------------- 01 OAI ----
F1 = E / "sources" / "figure1"
ADIR("01_OAI/data", F1 / "source", (".csv",))
for n in ("draw_prediction_pair.R", "figure_manifest.csv", "render_manifest.json"):
    A(f"01_OAI/scripts/{n}", F1 / n)
A("01_OAI/reference/figure1.svg", E / "assets" / "figure1.svg")

# ---------------------------------------------------------------- 02 TKA ----
F2 = E / "sources" / "figure2"
A("02_TKA/data/OA初次TKA_453例_合并骨赘候选_20261016.xlsx",
  F2 / "data" / "OA初次TKA_453例_合并骨赘候选_20261016.xlsx")
A("02_TKA/scripts/redraw_master.py", F2 / "code" / "redraw_master.py")
# redraw_master.py 第 662 行从 BASE/../figures/figure_manifest.csv 读取，必须放这个位置
A("02_TKA/figures/figure_manifest.csv", F2 / "figures" / "figure_manifest.csv")
A("02_TKA/reference/figure2.svg", E / "assets" / "figure2.svg")

# ------------------------------------------------- 03 / 04 现成复现包 ----
ATREE("03_NRFB_sc/F3_P08_重绘包_v5",
      C / "13_Figure3_合并稿_20261106" / "F3_P08_重绘包_v5")
ATREE("04_Tissue/Figure4_data_package_20261106",
      E / "22_Figure4_四列_20261106" / "package" / "Figure4_data_package_20261106")
# v7 布局块在 exec 到 fig = J.plate( 之前会引用 MR json，原包漏带，这里补上
A("04_Tissue/Figure4_data_package_20261106/data/_external/"
  "PCDH9_integrated_reproduction_20261024/source/53_图版_顶刊交付_20261024/"
  "mr_independent_summary.json",
  E / "_external" / "PCDH9_integrated_reproduction_20261024" / "source" /
  "53_图版_顶刊交付_20261024" / "mr_independent_summary.json")

# ------------------------------------------------------------- 05 Spatial ----
F5 = E / "sources" / "figure5"
F12 = E / "12_空间组神经标记_20261104"
for n in ("A4_CD_units.csv.gz", "Knee2_CD_units.csv.gz", "Knee3_CD_units.csv.gz",
          "seven_section_summary.csv", "colour_limits.json"):
    A(f"05_Spatial/data/figure5_source/{n}", F5 / "source" / n)
for n in ("bar_mean_SD.csv", "merge_overlap_summary.csv", "panel_manifest.csv"):
    A(f"05_Spatial/data/figure5_tables/{n}", F5 / "tables" / n)
for n in ("S_scale_sweep.csv", "T_continuous_alignment.csv", "V_two_sided.csv",
          "V_domain_ci.csv", "W_depth_stratified.csv", "W_depth_matched_summary.csv",
          "A_section_summary.csv", "D_gene_level.csv", "P1_pre_specified_panels.csv",
          "P2_PCDH9_vs_panels.csv", "detect_Knee2.csv", "detect_Knee3.csv",
          "grid_Knee2.npz", "grid_Knee3.npz"):
    A(f"05_Spatial/data/spatial_tables/{n}", F12 / "tables" / n)
for n in ("18_figure05_upper_journal.py", "05_figures.py",
          "19_assemble_figure5_journal.py", "journal_style.py"):
    A(f"05_Spatial/scripts/{n}", F12 / "scripts" / n)
A("05_Spatial/scripts/build_figure5_E.py", F5 / "build.py")
for n in ("Figure5_upper_AK.png", "Figure5_upper_AK.pdf",
          "Figure5_lower_LO.png", "Figure5_lower_LO.pdf"):
    A(f"05_Spatial/data/{n}", F12 / "figures" / n)

# --------------------------------------------------------- 06 Experiments ----
X = C / "_生成脚本"
A("06_Experiments/data/data.json", X / "data.json")
for sub in ("01_原始数据", "02_处理后数据", "03_统计结果"):
    ADIR(f"06_Experiments/data/{sub}", C / sub, (".csv", ".json"), recursive=True)
MEA = C / "04_MEA实验A"
ADIR("06_Experiments/data/MEA_02_处理后数据", MEA / "02_处理后数据", (".csv",))
for n in ("主要终点_LMM对比.csv", "基质对照_G1vsG4.csv",
          "供体级效应量与恢复率.csv", "供体级配对检验.csv", "统计摘要.json"):
    A(f"06_Experiments/data/MEA_03_统计结果/{n}", MEA / "03_统计结果" / n)
A("06_Experiments/data/Figure_PCDH9_perturbation.png", C / "Figure_PCDH9_perturbation.png")
A("06_Experiments/data/Figure5_MEA_A-E.png", MEA / "04_图表" / "Figure5_MEA_A-E.png")
A("06_Experiments/data/PCDH9_总览图.png", C / "06_总览图" / "PCDH9_总览图.png")
A("06_Experiments/scripts/08_mea_figures.py", MEA / "scripts" / "08_mea_figures.py")
A("06_Experiments/scripts/make_figure_S1.py",
  C / "05_图版_顶刊交付_20261031" / "scripts" / "make_figure_S1.py")
A("06_Experiments/scripts/18b_overview_figure_short.py", X / "18b_overview_figure_short.py")
A("06_Experiments/scripts/journal_style.py",
  C / "05_图版_顶刊交付_20261031" / "scripts" / "journal_style.py")

# ------------------------------------------------------ 07 Synovial fluid ----
P7 = C / "07_配对组织-体液验证_20261101"
P8 = C / "08_图版_顶刊交付_20261101"
ADIR("07_SynovialFluid/data/01_数据", P7 / "01_数据", (".csv", ".json"))
for n in ("data.json", "stats.json"):
    A(f"07_SynovialFluid/data/{n}", P7 / "02_脚本" / n)
for n in ("make_figures.py", "make_spec.py", "build_text_layer.py", "journal_style.py"):
    A(f"07_SynovialFluid/scripts/{n}", P8 / "scripts" / n)
A("07_SynovialFluid/scripts/spec.json", P8 / "spec.json")

# ------------------------------------------------------------------ copy ----
print(f"计划复制 {len(PAIRS)} 个文件")
copied = 0
for dst, src in PAIRS:
    if not src.is_file():
        MISSING.append(f"{dst}  <-  {src}")
        continue
    target = OUT / dst
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or target.read_bytes() != src.read_bytes():
        target.write_bytes(src.read_bytes())
    copied += 1
print(f"已复制 {copied} 个；缺失 {len(MISSING)} 个")
for m in MISSING:
    print("  [MISS]", m)

# --------------------------------------------------- 04 便携化（生成脚本）----
mp = OUT / "make_portable.py"
if mp.is_file():
    r = subprocess.run([sys.executable, str(mp)], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    print("\n[make_portable]", r.stdout.strip()[-1200:])
    if r.returncode != 0:
        print("[make_portable STDERR]", r.stderr.strip()[-1200:])

# ------------------------------------------- PANEL_DATA_DEPENDENCIES.csv ----
P03 = "03_NRFB_sc/F3_P08_重绘包_v5/data/"
P04 = "04_Tissue/Figure4_data_package_20261106/data/"

rows: list[list[str]] = []
def R(fig, plate, panel, title, files, note=""):
    rows.append([fig, plate, panel, title, files, note])

# 01
d1 = "01_OAI/data/"
R("01", "OAI A–F", "A", "Baseline covariate balance (lollipop)",
  d1 + "balance_values.csv | " + d1 + "association_values.csv", "donor / knee")
R("01", "OAI A–F", "Balance", "Absolute SMD before/after overlap weighting (heatmap)",
  d1 + "balance_values.csv", "donor / knee")
R("01", "OAI A–F", "B", "Follow-up pain burden (36/48 months)",
  d1 + "pain_values.csv | " + d1 + "endpoints.csv", "ESS 40.2 / 34.3")
R("01", "OAI A–F", "C", "Follow-up function burden trajectory",
  d1 + "function_trajectory.csv", "49 vs 456 knees")
R("01", "OAI A–F", "D", "Repeated discordance -> persistent high pain (OR)",
  d1 + "significance_tests.csv | " + d1 + "association_values.csv", "adjusted OR 4.00")
R("01", "OAI A–F", "E", "Prediction of subsequent pain (R2)",
  d1 + "performance.csv | " + d1 + "increments.csv | " + d1 + "out_of_fold_predictions.csv", "512 obs")
R("01", "OAI A–F", "F", "Prediction of subsequent function limitation (R2)",
  d1 + "performance.csv | " + d1 + "increments.csv | " + d1 + "out_of_fold_predictions.csv", "505 obs")

# 02
x2 = "02_TKA/data/OA初次TKA_453例_合并骨赘候选_20261016.xlsx"
t2 = ["Structure matching / covariate balance", "PPSD distribution and extreme windows",
      "Pain separation at similar structural burden", "Baseline balance of high-PPSD group",
      "Follow-up pain burden", "Follow-up function burden",
      "Continuous PPSD vs persistent pain risk", "Risk difference across adjustment layers",
      "12-month pain prediction", "12-month function prediction", "Persistent stiffness prediction"]
for i, t in enumerate(t2):
    R("02", "TKA A–K", chr(ord("A") + i), t, x2, "single 453-case workbook; sheet 453例术前术后影像总表")

# 03（读取原包内的逐面板清单，避免二次手抄）
f3dep = OUT / "03_NRFB_sc/F3_P08_重绘包_v5/PANEL_DATA_DEPENDENCIES.csv"
if f3dep.is_file():
    with f3dep.open(encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            files = " | ".join(P03 + x.strip() for x in row["minimum_data_files"].split("|") if x.strip())
            R("03", "F3_P08 v5 · A–T", row["new_letter"], row["title"], files,
              row["statistics_recomputed"])
else:
    R("03", "F3_P08 v5 · A–T", "A–T", "18 panels", P03 + "(see in-package PANEL_DATA_DEPENDENCIES.csv)", "MISSING SOURCE")

# 04（按包内 README 第 2 节）
d4 = {
    "A": (P04 + "_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T38_state_diff_cohort_adjusted.csv", "15 states, donor"),
    "B": (P04 + "_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T30_deconv_donor_fractions.csv | " + P04 + "_external/GSE99662_W28_W29_重绘_20261019/source/deconv_v2/T32_deconv_meta.csv", "svr only; donor"),
    "C": (P04 + "_external/GSE99662_W28_W29_重绘_20261019/source/within_cohort_effects.csv | " + P04 + "_external/GSE99662_W28_W29_重绘_20261019/source/random_effects_meta.csv", "8 cohorts, cohort-level"),
    "D": (P04 + "identity_results/bulk_donor_scores.csv | " + P04 + "identity_results/stats_bulk.json", "255 donors"),
    "E": (P04 + "sources/bulk_own_cohort_20261028/Figure7/data/Fig7DE_pooled_z_samplelevel.tsv", "sample"),
    "F": (P04 + "sources/bulk_own_cohort_20261028/Figure7/data/Fig7E_cohort_deltas.tsv | " + P04 + "sources/bulk_own_cohort_20261028/Figure7/data/Fig7_summary_stats.tsv", "7 cohorts"),
    "G": (P04 + "identity_results/bulk_donor_scores.csv | " + P04 + "identity_results/stats_bulk.json", "same 255 donors as D"),
    "H": (P04 + "sources/bulk_own_cohort_20261028/Figure7/data/Fig7A_box_samplelevel.tsv", "P1 (pain) only"),
    "I": (P04 + "derived/x_ppsd_stats.json", "8 rows + random-effects overall"),
    "J": (P04 + "_external/figure_audit/plot_data/figS1_tidy.csv", "protein ~ paired mRNA"),
    "K": (P04 + "_external/figure_audit/plot_data/figS1_tidy.csv", "protein ~ NR-FB score"),
    "L": (P04 + "_external/figure_audit/plot_data/figS1_tidy.csv", "protein ~ WOMAC pain"),
    "M": (P04 + "derived/x_ra_donor_fractions.csv | " + P04 + "derived/x_ra_stats.json", "Normal / OA / RA"),
    "N": (P04 + "derived/y_ra_donor_scores.csv | " + P04 + "derived/y_ra_stats.json", "4 groups incl. RA"),
}
tit4 = {"A": "15-state transcript contribution difference", "B": "NR-FB contribution Control vs OA",
        "C": "CORE20 eight-cohort forest", "D": "PCDH9 ~ CORE20 (255 donors)",
        "E": "PCDH9 across three diagnostic groups", "F": "Per-cohort delta PCDH9",
        "G": "PCDH9 ~ neural module", "H": "PCDH9 High vs Low pain",
        "I": "Eight-row delta PCDH9 forest", "J": "Protein ~ paired mRNA",
        "K": "Protein ~ NR-FB score", "L": "Protein ~ WOMAC pain",
        "M": "NR-FB % Control / OA / RA", "N": "PCDH9 ~ CORE20 with RA"}
for k in "ABCDEFGHIJKLMN":
    R("04", "Figure4 four-column · A–N", k, tit4[k], d4[k][0], d4[k][1])

# 05
s5 = "05_Spatial/data/"
cd = lambda s: f"{s5}figure5_source/{s}_CD_units.csv.gz"
col = s5 + "figure5_source/colour_limits.json"
t5 = s5 + "spatial_tables/"
for i, (s, lab) in enumerate([("Knee2", "high-PPSD"), ("Knee3", "low-PPSD"), ("A4", "control")]):
    R("05", "Spatial A–O", chr(ord("A") + i), f"NR-FB domain mask · {lab}", cd(s) + " | " + col, "section-level")
    R("05", "Spatial A–O", chr(ord("D") + i), f"PCDH9 log1p(CPM) · {lab}", cd(s) + " | " + col, "shared 0–9.35 scale")
    R("05", "Spatial A–O", chr(ord("G") + i), f"Same-spot overlay · {lab}", cd(s) + " | " + col, "white = intersection")
R("05", "Spatial A–O", "J", "PCDH9+ rate among all spots", s5 + "figure5_source/seven_section_summary.csv | " + s5 + "figure5_tables/bar_mean_SD.csv", "5 control vs 2 OA, section-weighted")
R("05", "Spatial A–O", "K", "PCDH9+ rate within NR-FB region", s5 + "figure5_source/seven_section_summary.csv | " + s5 + "figure5_tables/bar_mean_SD.csv", "descriptive only")
R("05", "Spatial A–O", "L", "Neural / myelin transcript budget", t5 + "D_gene_level.csv | " + t5 + "A_section_summary.csv", "15 neural + 6 myelin genes")
R("05", "Spatial A–O", "M", "Knee2 neural transcript density map", t5 + "grid_Knee2.npz | " + t5 + "detect_Knee2.csv", "sigma = 3 bin")
R("05", "Spatial A–O", "N", "Knee3 neural transcript density map", t5 + "grid_Knee3.npz | " + t5 + "detect_Knee3.csv", "shared colour scale with M")
R("05", "Spatial A–O", "O", "Inside/outside rate ratio forest", t5 + "V_domain_ci.csv | " + t5 + "V_two_sided.csv | " + t5 + "P1_pre_specified_panels.csv", "torus-shift null, 2000 permutations")

# 06
d6 = "06_Experiments/data/"
t6 = [
    ("A", "Knockdown efficiency", "03_统计结果/PCDH9敲低效率_患者级.csv | 02_处理后数据/样本级_log2FC_相对NT-siRNA.csv"),
    ("B", "NR-FB programme score", "02_处理后数据/NR-FB_signature_score_患者级.csv | 03_统计结果/signature_score_统计.csv"),
    ("C", "13 target genes donor-wise z heatmap", "02_处理后数据/样本级_log2表达_内参归一化.csv | 02_处理后数据/患者级均值_log2FC.csv"),
    ("D", "Neural-related gene dot plot", "02_处理后数据/Neural_module_score_患者级.csv | 03_统计结果/基因层面_配对检验_BH校正.csv"),
    ("E", "CXCL12 secretion (ELISA)", "02_处理后数据/ELISA_患者级浓度.csv | 03_统计结果/ELISA_统计.csv | 03_统计结果/ELISA_4PL拟合参数.csv"),
    ("F", "Mean firing rate (MEA)", "MEA_02_处理后数据/MEA_孔级_清洗后.csv | MEA_03_统计结果/主要终点_LMM对比.csv"),
    ("G", "Mean inter-spike interval (MEA)", "MEA_02_处理后数据/MEA_孔级_清洗后.csv | MEA_02_处理后数据/MEA_供体级均值.csv"),
    ("H", "Network burst frequency (MEA)", "MEA_02_处理后数据/MEA_孔级_清洗后.csv | MEA_03_统计结果/供体级效应量与恢复率.csv"),
]
for k, t, fl in t6:
    R("06", "Experiment overview · A–H", k, t,
      " | ".join(d6 + f for f in fl.split(" | ")),
      "donor-level (A–E) / well-level (F–H); simulated dataset")

# 07
d7 = "07_SynovialFluid/data/"
main7 = d7 + "data.json | " + d7 + "stats.json"
for i, t in enumerate(["Fluid PCDH9 vs synovial CORE20", "Fluid vs tissue PCDH9",
                       "Fluid PCDH9 vs PPSD discordance", "Fluid PCDH9 vs structural severity",
                       "Group separation / ROC (preset cutpoint)", "Assay calibration summary"]):
    R("07", "Submission Figure 7 / delivered Figure 6 · A–F", chr(ord("A") + i), t,
      main7 + (" | " + d7 + "01_数据/PRM_校准曲线.csv" if i == 5 else ""),
      "n = 31 paired; simulated, seed 4020")
for k, n in [("S1", 6), ("S2", 2), ("S3", 3), ("S4", 2)]:
    R("07", f"Supplementary {k} · A–{chr(ord('A') + n - 1)}", f"{k} (all panels)",
      "Assay validation / robustness / QC / cutpoint sensitivity",
      main7 + " | " + d7 + "01_数据/滑液PRM_肽段级.csv | " + d7 + "01_数据/滑液PRM_患者级.csv",
      "not independent repeats; same 31 pairs")

with (OUT / "PANEL_DATA_DEPENDENCIES.csv").open("w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["figure", "plate_version", "panel", "title", "data_files_in_package", "note"])
    w.writerows(rows)
print(f"\nPANEL_DATA_DEPENDENCIES.csv: {len(rows)} 行")

# ------------------------------------------------------------- check_package ----
CHECK = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""交接自检：依赖表引用的文件是否齐全、MANIFEST 的 MD5 是否与实物一致。"""
from __future__ import annotations
import csv, hashlib, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(__file__).resolve().parent
problems = []
with (P / "PANEL_DATA_DEPENDENCIES.csv").open(encoding="utf-8-sig", newline="") as fh:
    deps = list(csv.DictReader(fh))
refs = set()
for r in deps:
    for f in r["data_files_in_package"].split("|"):
        f = f.strip()
        if f and not f.startswith("("):
            refs.add(f)
missing = sorted(f for f in refs if not (P / f).is_file())
if missing:
    problems.append("依赖表引用了 %d 个不存在的文件" % len(missing))
    for f in missing[:20]: print("  [MISS]", f)
print("逐 panel 依赖: %d 行, %d 个唯一数据文件, 缺失 %d" % (len(deps), len(refs), len(missing)))
with (P / "MANIFEST.csv").open(encoding="utf-8-sig", newline="") as fh:
    man = list(csv.DictReader(fh))
bad = []
for r in man:
    f = P / r["path"]
    if not f.is_file():
        bad.append(r["path"]); continue
    h = hashlib.md5(f.read_bytes()).hexdigest()
    if h != r["md5"] or f.stat().st_size != int(r["size_bytes"]):
        bad.append(r["path"])
if bad:
    problems.append("MANIFEST 不符 %d 个文件" % len(bad))
    for f in bad[:20]: print("  [DIFF]", f)
for d in ("01_OAI", "02_TKA", "03_NRFB_sc", "04_Tissue", "05_Spatial",
          "06_Experiments", "07_SynovialFluid"):
    if not (P / d).is_dir(): problems.append("缺目录 " + d)
print("MANIFEST: %d 个文件, %.2f MB, 不符 %d" %
      (len(man), sum(int(r["size_bytes"]) for r in man)/1e6, len(bad)))
if problems:
    for p in problems: print("[FAIL]", p)
    raise SystemExit(1)
print("ALL CHECKS PASSED")
'''
(OUT / "check_package.py").write_text(CHECK, encoding="utf-8", newline="\n")

# ---------------------------------------------------------------- MANIFEST ----
text_files = ["README.md", "PANEL_DATA_DEPENDENCIES.csv", "check_package.py",
              "build_package.py", "make_portable.py"]
allf = sorted(p for p in OUT.rglob("*")
              if p.is_file() and p.suffix != ".zip" and p.name != "MANIFEST.csv")
with (OUT / "MANIFEST.csv").open("w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["path", "size_bytes", "md5", "kind"])
    for p in allf:
        rel = p.relative_to(OUT).as_posix()
        kind = ("文档/清单" if p.name in text_files or p.suffix in (".md", ".csv") and rel.count("/") == 0
                else "脚本" if p.suffix in (".py", ".R")
                else "成品/参考" if p.suffix in (".png", ".pdf", ".svg", ".jpg")
                else "数据")
        w.writerow([rel, p.stat().st_size, hashlib.md5(p.read_bytes()).hexdigest(), kind])
print(f"MANIFEST.csv: {len(allf)} 个文件, "
      f"{sum(p.stat().st_size for p in allf)/1e6:.2f} MB")

# ---------------------------------------------------------------------- zip ----
zpath = E / "24_图版01-07_最小复现总包_20261106.zip"
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            z.write(p, (OUT.name + "/" + p.relative_to(OUT).as_posix()))
print(f"ZIP: {zpath}  ({zpath.stat().st_size/1e6:.2f} MB)")
if MISSING:
    print(f"\n注意：{len(MISSING)} 个源文件未找到，见上方 [MISS] 列表")
