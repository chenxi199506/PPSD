#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 04–07 的作图脚本改成包内相对路径，使其能在另一台电脑上直接跑。

只替换路径常量与输出目录，不碰数据、统计量、画法与版式断言。
运行：python make_portable.py   （在本包根目录或任意 cwd 均可）
产物：各图 scripts/*_portable.py，以及 07 的 spec_portable.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
P4 = PKG / "04_Tissue" / "Figure4_data_package_20261106" / "scripts"
P5 = PKG / "05_Spatial" / "scripts"
P6 = PKG / "06_Experiments" / "scripts"
P7 = PKG / "07_SynovialFluid" / "scripts"

P1 = PKG / "01_OAI" / "scripts"
P2 = PKG / "02_TKA" / "scripts"

COUNT = 0


def patch(base: Path, src_name: str, rules: list[tuple]) -> None:
    """rules: (old, new) 替换 1 次；(old, new, -1) 全局替换。"""
    global COUNT
    src = base / src_name
    if not src.is_file():
        print(f"[SKIP] 缺 {src}")
        return
    text = src.read_text(encoding="utf-8")
    for rule in rules:
        old, new = rule[0], rule[1]
        n = rule[2] if len(rule) > 2 else 1
        if old not in text:
            raise SystemExit(f"[FAIL] {src_name}: 找不到待替换片段\n  {old[:100]!r}")
        text = text.replace(old, new) if n < 0 else text.replace(old, new, n)
    dst = base / (src.stem + "_portable" + src.suffix)
    dst.write_text(text, encoding="utf-8", newline="\n")
    COUNT += 1
    print(f"[OK] {base.parent.name}/{src_name} -> {dst.name}  ({len(rules)} 处)")


# ------------------------------------------------------------------ 01 ----
# R 脚本把 h 定在 scripts/，源表在上一级 data/。改为包内 01_OAI/ 后全局改目录名。
# 需要 R + ggplot2 / jsonlite / svglite / ragg；本机无 Rscript，未实测。
patch(P1, "draw_prediction_pair.R", [
    (
        "a<-commandArgs(FALSE);h<-dirname(normalizePath(sub('^--file=','',a[grep('^--file=',a)][1])))",
        "a<-commandArgs(FALSE);h<-dirname(dirname(normalizePath(sub('^--file=','',a[grep('^--file=',a)][1]))))\n"
        "dir.create(file.path(h,'output'),showWarnings=FALSE,recursive=TRUE)",
    ),
    ("h,'source/", "h,'data/", -1),
    ("file.path(h,'figures'", "file.path(h,'output'", -1),
])

# ------------------------------------------------------------------ 04 ----
patch(P4, "build_figure4_4col.py", [
    (
        'ROOT = Path(r"E:/NRFB_atlas_plate_20261104")\n'
        'V7 = ROOT / "scripts/recompose_fig4_v7.py"\n'
        'HERE = Path(__file__).resolve().parent\n'
        'OUT = HERE.parent / "figures"',
        'PKG = Path(__file__).resolve().parents[1]\n'
        'ROOT = PKG / "data"\n'
        'V7 = PKG / "scripts" / "recompose_fig4_v7_portable.py"\n'
        'HERE = Path(__file__).resolve().parent\n'
        'sys.path.insert(0, str(PKG / "scripts"))\n'
        'OUT = PKG / "figures"',
    ),
    (
        'RES = Path(r"experiment_root//09_NRFB身份定义_20261104/02_结果")\n'
        'F7 = ROOT / "sources/bulk_own_cohort_20261028/Figure7/data"\n'
        'XS = json.loads((HERE.parent / "x_ppsd_stats.json").read_text(encoding="utf-8"))\n'
        'XR = json.loads((HERE.parent / "x_ra_stats.json").read_text(encoding="utf-8"))\n'
        'YR = json.loads((HERE.parent / "y_ra_stats.json").read_text(encoding="utf-8"))\n'
        'XRA = pd.read_csv(HERE.parent / "x_ra_donor_fractions.csv")\n'
        'YRA = pd.read_csv(HERE.parent / "y_ra_donor_scores.csv")',
        'RES = ROOT / "identity_results"\n'
        'F7 = ROOT / "sources" / "bulk_own_cohort_20261028" / "Figure7" / "data"\n'
        'DER = ROOT / "derived"\n'
        'XS = json.loads((DER / "x_ppsd_stats.json").read_text(encoding="utf-8"))\n'
        'XR = json.loads((DER / "x_ra_stats.json").read_text(encoding="utf-8"))\n'
        'YR = json.loads((DER / "y_ra_stats.json").read_text(encoding="utf-8"))\n'
        'XRA = pd.read_csv(DER / "x_ra_donor_fractions.csv")\n'
        'YRA = pd.read_csv(DER / "y_ra_donor_scores.csv")',
    ),
    (
        'assert (ROOT / "scripts/journal/journal_style.py").exists()',
        'assert (PKG / "scripts" / "journal_style.py").exists()',
    ),
])
patch(P4, "recompose_fig4_v7.py", [
    (
        'else HERE.parent / "_external/figure_audit/editable")',
        'else HERE.parent / "data" / "_external/figure_audit/editable")',
    ),
    (
        'PROJ = HERE.parents[1]\n'
        '# 服务器上没有图册项目的父级目录，外部兄弟目录回落到项目的 _external/\n'
        'if not (PROJ / "GSE99662_W28_W29_重绘_20261019").is_dir():\n'
        '    PROJ = HERE.parent / "_external"\n'
        'SRC = PROJ / "GSE99662_W28_W29_重绘_20261019" / "source"\n'
        'F7 = HERE.parent / "sources" / "bulk_own_cohort_20261028" / "Figure7" / "data"',
        'PROJ = HERE.parent / "data" / "_external"\n'
        'SRC = PROJ / "GSE99662_W28_W29_重绘_20261019" / "source"\n'
        'F7 = HERE.parent / "data" / "sources" / "bulk_own_cohort_20261028" / "Figure7" / "data"',
    ),
])

# ------------------------------------------------------------------ 05 ----
patch(P5, "05_figures.py", [
    (
        'ROOT = Path(r"E:/NRFB_atlas_plate_20261104/12_空间组神经标记_20261104")\n'
        'TAB = ROOT / "tables"\n'
        'FIG = ROOT / "figures"',
        'ROOT = Path(__file__).resolve().parents[1]\n'
        'TAB = ROOT / "data" / "spatial_tables"\n'
        'FIG = ROOT / "data"',
    ),
])
patch(P5, "18_figure05_upper_journal.py", [
    (
        'ROOT = Path(r"E:/NRFB_atlas_plate_20261104")\n'
        'S = ROOT / "sources" / "figure5" / "source"\n'
        'OUT = ROOT / "12_空间组神经标记_20261104" / "figures"',
        'ROOT = Path(__file__).resolve().parents[1]\n'
        'S = ROOT / "data" / "figure5_source"\n'
        'OUT = ROOT / "data"',
    ),
])
patch(P5, "19_assemble_figure5_journal.py", [
    (
        'ROOT = Path(r"E:/NRFB_atlas_plate_20261104")\n'
        'FIG = ROOT / "12_空间组神经标记_20261104" / "figures"',
        'ROOT = Path(__file__).resolve().parents[1]\n'
        'FIG = ROOT / "data"',
    ),
])

# ------------------------------------------------------------------ 06 ----
patch(P6, "08_mea_figures.py", [
    (
        'ROOT = Path(r"experiment_root//04_MEA实验A")\n'
        'PROC, RES, FIG = ROOT / "02_处理后数据", ROOT / "03_统计结果", ROOT / "04_图表"',
        'ROOT = Path(__file__).resolve().parents[1]\n'
        'PROC, RES, FIG = (ROOT / "data" / "MEA_02_处理后数据",\n'
        '                  ROOT / "data" / "MEA_03_统计结果", ROOT / "output")\n'
        'FIG.mkdir(parents=True, exist_ok=True)',
    ),
])
patch(P6, "make_figure_S1.py", [
    (
        'ROOT = os.path.dirname(HERE)\n'
        'DATA = os.path.join(os.path.dirname(ROOT), "_生成脚本", "data.json")\n'
        'OUT = os.path.join(ROOT, "figures")',
        'ROOT = os.path.dirname(HERE)\n'
        'DATA = os.path.join(ROOT, "data", "data.json")\n'
        'OUT = os.path.join(ROOT, "output")\n'
        'os.makedirs(OUT, exist_ok=True)',
    ),
])
patch(P6, "18b_overview_figure_short.py", [
    (
        'OUT = ROOT / "06_总览图"',
        'OUT = ROOT / "data"',
    ),
    (
        'F1 = Image.open(ROOT / "Figure_PCDH9_perturbation.png").convert("RGB")',
        'F1 = Image.open(ROOT / "data" / "Figure_PCDH9_perturbation.png").convert("RGB")',
    ),
    (
        'F5 = Image.open(ROOT / "04_MEA实验A/04_图表" / "Figure5_MEA_A-E.png").convert("RGB")',
        'F5 = Image.open(ROOT / "data" / "Figure5_MEA_A-E.png").convert("RGB")',
    ),
])

# ------------------------------------------------------------------ 07 ----
patch(P7, "make_figures.py", [
    (
        'HERE = os.path.dirname(os.path.abspath(__file__))\n'
        'ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))\n'
        'FIG = os.path.join(ROOT, "08_图版_顶刊交付_20261101", "figures")\n'
        'DATA = os.path.join(ROOT, "07_配对组织-体液验证_20261101", "01_数据")\n'
        'SCRIPT = os.path.join(ROOT, "07_配对组织-体液验证_20261101", "02_脚本")',
        'HERE = os.path.dirname(os.path.abspath(__file__))\n'
        'ROOT = os.path.abspath(os.path.join(HERE, ".."))\n'
        'FIG = os.path.join(ROOT, "output")\n'
        'DATA = os.path.join(ROOT, "data", "01_数据")\n'
        'SCRIPT = os.path.join(ROOT, "data")',
    ),
])
patch(P7, "make_spec.py", [
    (
        'ROOT = os.path.abspath(os.path.join(HERE, ".."))            # 交付包根目录\n'
        'PROJ = os.path.abspath(os.path.join(ROOT, ".."))            # 分析工程根目录\n'
        'SCRIPT = os.path.join(PROJ, "07_配对组织-体液验证_20261101", "02_脚本")',
        'ROOT = os.path.abspath(os.path.join(HERE, ".."))\n'
        'PROJ = ROOT\n'
        'SCRIPT = os.path.join(ROOT, "data")',
    ),
])
patch(P7, "build_text_layer.py", [
    (
        '    root = Path(spec.get("outdir") or spec_path.parent).resolve()',
        '    root = Path(__file__).resolve().parents[1]   # 07_SynovialFluid/（包内相对，换机不变）',
    ),
])
sp = P7 / "spec.json"
if sp.is_file():
    d = json.loads(sp.read_text(encoding="utf-8"))
    d["outdir"] = ""           # 交给 build_text_layer_portable.py 按脚本位置解析
    d["figdir"] = "output"     # 图直接写在 07_SynovialFluid/output/ 下
    (P7 / "spec_portable.json").write_text(
        json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    COUNT += 1
    print("[OK] 07_SynovialFluid/scripts/spec_portable.json  (figdir -> output/)")


def main() -> None:
    print(f"\n共生成 {COUNT} 个便携产物。原脚本全部保留，未做任何修改。")
    print("各图重跑命令见 README.md 第 3 节。")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
