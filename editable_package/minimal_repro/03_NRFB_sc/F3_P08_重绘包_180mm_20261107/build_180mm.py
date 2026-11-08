"""F3_P08 v9 · 180 mm 期刊宽度上限版（2026-11-07 第四轮）。

用户反馈（原话）：
  "Fig3 期刊要求的是 180mm 之内 你看看 A 图、I 和 N 图还和旁边的图可以有一点
   距离，另外整个图的旁边是否也可以省出一点距离"

诊断（对 600 dpi 成图做逐像素墨迹测量，见 build/inspect）：
  * A / I 的绘图区宽 34.2 mm，点云墨迹只占 24.9 mm —— 左右共空 9.2 mm（27%）。
    N / Q 空 4.0 mm。这不是面板间距（GAP 3.0）的问题，而是两件事叠加：
      - `set_aspect("equal", adjustable="datalim")` 下框比数据宽，datalim 只能
        在框内把数据居中，多出来的部分就是框内空白；
      - 自动坐标范围带 matplotlib 默认 5% 边距，又吃掉约 9%。
  * 外页边 MG = 6.0 mm，左右合计 12 mm 是纯空白。

本轮三项改动（仍只动显示层几何，不动数据 / 数值 / 配色 / 状态名）：
  A. UMAP 绘图区宽度 = 行高 × 该图谱 UMAP 的实测宽高比（G1 0.822 / G2 0.826 /
     M2 1.160 / L2 1.112），坐标范围显式收到点云外接框 + 0.6% 留白。
     于是点云恰好贴住框的四边，框内横向空白归零；A / I 的云还比原来大 9%。
  B. 外页边 MG 6.0 -> 3.2，GAP 3.0 -> 2.6，省下 7.2 mm。
  C. 页脚里"In the four UMAPs the legend sits right of the embedding"这句
     从第三轮起已经不成立（图例已并入箱线图左缘的色点列），本轮改为如实描述。

仍以 `build_F3_P08_portable.py` 为唯一真源：复用 build_shared_variants 的补丁表，
在其后再追加本轮补丁，一遍数据加载 / 一遍 KDE 计算下渲染。

运行（在本文件所在目录）：
    python build_180mm.py            # 600 dpi 正式出图
    python build_180mm.py --smoke    # 100 dpi 自检
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_shared_variants as BS  # noqa: E402

BASE = BS.BASE
OUT_ROOT = HERE / "outputs" / "v180"
SMOKE = "--smoke" in sys.argv

# ---------------------------------------------------------------- 版本参数
PW = 180.0
PH = 268.0
MG = 3.2
GAP = 2.6
UMAP_CAP = 34.0          # 单张 UMAP 绘图区宽度上限（防止 M2/L2 撑开整行）
NAME = "V180"

CFG = dict(name=NAME, pw=PW, ph=PH, gap=GAP, umap_w=UMAP_CAP,
           mg=MG, desc="期刊 180 mm 上限：UMAP 框贴合数据宽高比，外页边 3.2 mm")

SUBTITLE = (
    "F3_P08 v9 180 mm - {pw} x {ph} mm - one state column per UMAP + CORE20 pair - "
    "18 panels, re-drawn from source tables"
)

# ---------------------------------------------------------------- 追加补丁
# 说明：BS.PATCHES 已把 LPAD / ROW_H / ROW_TOP / SHARE_GEOM / box_h / 共享色点列
# 全部打好，这里只在其后追加本轮的三项改动，避免与已有补丁的目标字符串冲突。
EXTRA: list[tuple[str, str, int]] = [
    # 1) 外页边 6.0 -> 3.2
    ("MG = 6.0", f"MG = {MG}", 1),
    # 2) UMAP 坐标范围收到点云外接框 + 0.6% 留白；框宽由 positions() 按宽高比给定，
    #    于是 set_aspect(equal) 不再需要 datalim 在框内补空白。
    ("""    ax.set_aspect("equal", adjustable="datalim")""",
     """    # 180 mm 版：把自动边距从默认 5% 收到 0.6%，框宽 = 行高 x 数据宽高比
    # （见 positions()）。两轴等比收边距，宽高比不变，set_aspect(equal) 因此
    # 不再需要 datalim 在框内补空白，点云恰好贴住框的四边。
    ax.margins(0.006)
    ax.set_aspect("equal", adjustable="datalim")""", 1),
    # 3) 页脚事实性修正：图例已不再是"绘图区右侧"
    ('"follow v3 numbering with P and S removed. In the four UMAPs the legend '
     'sits right of the embedding; "',
     '"follow v3 numbering with P and S removed. In the four UMAPs the state '
     'legend appears once only, as the 2.4 mm dot column at the left edge of the '
     'adjacent CORE20 panel, which doubles as that panel\'s y labels; "', 1),
    # 4) 页眉 / 页脚与面板块统一到同一条 3.2 mm 边线（原来在 1.5 mm，
    #    与面板左缘差 1.7 mm，放大到印刷尺寸能看出错位）
    ("    J.header(fig, *HEADER)",
     "    J.header(fig, *HEADER, x=MG / PW)", 1),
    ("    J.footer(fig, FOOTER, size=5.6, linespacing=1.20)",
     "    J.footer(fig, FOOTER, x=MG / PW, size=5.6, linespacing=1.20)", 1),
]

POSITIONS = '''def umap_aspect(key):
    """UMAP 点云外接框的宽高比（宽 / 高）。框宽取 ROW_H x 它，点云就填满框。"""
    u = umap(key)
    return float((u[:, 0].max() - u[:, 0].min()) / (u[:, 1].max() - u[:, 1].min()))


def positions():
    """180 mm 版逐行分配。

    每格宽度 = 标签块 + 绘图区；标签块 = LPAD（含共享色点列）+ RIGHT_PAD。
    UMAP 绘图区宽 = 行高 x 该图谱实测宽高比（封顶 UMAP_CAP），点云因此填满框、
    框内没有横向空白；一行放不下时退化为等分。非 UMAP 面板先拿 PLOT_MIN 保底，
    剩余宽度按 ROW_W 权重加给 B / C / F / G / J / K / L / M / O / R / T。
    """
    cfg = VARIANT_CFG
    gap = cfg["gap"]
    CW = PW - 2 * MG
    rows = [list("ABCDE"), list("FGH"), list("IJKLM"), list("NOQRT")]
    kinds = {L: k for L, _r, _s, _sp, _t, k, _a in PANEL_MAP}
    arg = {L: a for L, _r, _s, _sp, _t, _k, a in PANEL_MAP}
    out = {}
    for ri, letters in enumerate(rows):
        ytop = ROW_TOP[ri]
        narrow = (ri == 3)
        lab = {L: LPAD[kinds[L]][1 if narrow else 0]
               + (DOT_W + DOT_GAP if L in PAIR_BOX else 0.0)
               + RIGHT_PAD for L in letters}
        plot_avail = CW - gap * (len(letters) - 1) - sum(lab.values())
        umaps = [L for L in letters if kinds[L] == "umap"]
        var = [L for L in letters if kinds[L] != "umap"]
        base = {L: PLOT_MIN[kinds[L]] for L in var}
        left = plot_avail - sum(base.values())
        assert left > 0, (cfg["name"], ri, left)
        plot = {L: min(ROW_H * umap_aspect(arg[L]), cfg["umap_w"]) for L in umaps}
        if umaps and sum(plot.values()) > left:
            for L in umaps:
                plot[L] = left / len(umaps)
        rest = left - sum(plot[L] for L in umaps)
        tot = sum(ROW_W[ri][L] for L in var)
        for L in var:
            plot[L] = base[L] + rest * ROW_W[ri][L] / tot
        x = MG
        for L in letters:
            out[L] = (x, ytop, plot[L] + lab[L])
            x += plot[L] + lab[L] + gap
        assert abs((x - gap) - (MG + CW)) < 1e-6, (cfg["name"], ri, x)
    return out
'''


def patched_source() -> str:
    s = BASE.read_text(encoding="utf-8")
    for old, new, n in list(BS.PATCHES) + EXTRA:
        cnt = s.count(old)
        assert cnt == n, f"patch mismatch ({cnt} != {n}): {old[:76]!r}"
        s = s.replace(old, new)

    marker = "\ndef main():\n"
    assert s.count(marker) == 1
    s = s.replace(marker, "\n" + BS.HELPERS + "\ndef main():\n", 1)

    pat = re.compile(r"def positions\(\):.*?\n    return out\n", re.S)
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: POSITIONS, s, count=1)
    return s


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    src = patched_source()
    (HERE / "_patched_v180_preview.py").write_text(src, encoding="utf-8")

    ns = {"__name__": "_f3_v180_mod", "__file__": str(BASE),
          "MASTER_N": 10, "ALIGN_GRID": True, "SHARE_LEGEND": True}
    exec(compile(src, str(BASE), "exec"), ns)

    ns["VARIANT_DPI"] = 100 if SMOKE else 600
    ns["VARIANT_CFG"] = CFG
    ns["PW"] = PW
    ns["PH"] = PH
    ns["ALIGN_GRID"] = True
    ns["MASTER_N"] = 10
    ns["SHARE_LEGEND"] = True
    ns["AX_REC"] = []
    ns["GEOM_REPORT"] = []
    ns["HEADER"] = (
        "Figure 3 · F3_P08",
        "The NR-FB state across four single-cell atlases, and what defines it",
        SUBTITLE.format(pw=int(PW), ph=int(PH)),
    )
    stem = f"F3_P08_v180_{int(PW)}mm"
    ns["OUT_PNG"] = OUT_ROOT / f"{stem}.png"
    ns["OUT_PDF"] = OUT_ROOT / f"{stem}.pdf"
    ns["OUT_MAP"] = OUT_ROOT / f"{stem}_面板映射.csv"
    ns["OUT_META"] = OUT_ROOT / f"{stem}_meta.json"

    pos = ns["positions"]()
    print(f"=== {NAME}  PW={PW}  PH={PH}  MG={MG}  GAP={GAP} ===", flush=True)
    for L in "ABCDEFGHIJKLMNOQRT":
        print(f"  {L}  x={pos[L][0]:7.2f}  w={pos[L][2]:6.2f}", flush=True)

    ns["main"]()

    from PIL import Image
    with Image.open(ns["OUT_PNG"]) as im:
        px = im.size
    geom = list(ns["GEOM_REPORT"])
    (OUT_ROOT / "geometry_report.json").write_text(
        json.dumps({NAME: geom}, ensure_ascii=False, indent=2), encoding="utf-8")
    rec = dict(CFG, status="ok", stem=stem,
               png_bytes=ns["OUT_PNG"].stat().st_size,
               png_md5=hashlib.md5(ns["OUT_PNG"].read_bytes()).hexdigest().upper(),
               pdf_bytes=ns["OUT_PDF"].stat().st_size,
               width_px=px[0], height_px=px[1],
               widths={L: round(pos[L][2], 2) for L in pos},
               plot={r["letter"]: r["plot_mm"] for r in geom})
    (OUT_ROOT / "v180_summary.json").write_text(
        json.dumps([rec], ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT_ROOT / "面板宽度.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["panel", "x_mm", "w_mm"])
        for L in "ABCDEFGHIJKLMNOQRT":
            w.writerow([L, round(pos[L][0], 2), round(pos[L][2], 2)])
    print(f"\nOK {stem}  {px[0]}x{px[1]} px  md5={rec['png_md5']}", flush=True)


if __name__ == "__main__":
    main()
