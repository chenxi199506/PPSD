"""F3_P08 v9 · 第六轮：去掉所有子图标题（2026-11-07）。

用户澄清（原话）：
  "不是，我是说去掉所有的子图的标题"

上一轮把"标题和副标题"理解成整版页眉 `J.header()` 那三行，删错了对象。
本轮据此修正：

  * 恢复整版页眉（P 版）；另出 Q 版保留上一轮的"无页眉"状态，供用户选。
  * 删除的是每个子图上方的说明块，也就是 `PANEL_MAP` 里的句式化 `title`
    （"NR-FB forms a region" 之类）加上灰色副注 `note`
    （"G1; 8 donors" / "Cliff's d = 0.42" 之类）。18 个面板一共 36 行文字。
  * 保留面板字母 A..T —— 期刊图注要用它们指认面板，且页脚方法学说明
    逐字引用了 A-C / F / G / I-K 等字母，删掉会让页脚失去指代。

删掉标题块后必须同步重排四行，否则每行上方会留 11.6 mm 空白带。
按 600 dpi 成图实测的墨迹边界重算（见 build/inspect）：
  上一行墨迹底 = 该行 ytop + 38.6 mm（第 2 行因 F 的斜排基因名是 +44.3）
  本行字母顶   = 该行 ytop - 5.0 mm
  两者留 2.6 mm 空隙（= 水平 GAP）
  P 版还要让页眉墨迹底（10.3 mm）与第 1 行字母顶留 3.0 mm

  ROW_TOP  P = [18.3, 64.5, 116.4, 162.6]   PH = 239.6 mm
  ROW_TOP  Q = [ 8.2, 54.4, 106.3, 152.5]   PH = 229.5 mm
  （第四轮是 [26.0, 79.0, 138.0, 191.0] / PH = 268.0）

行高、行内水平分配、UMAP 框宽、共享色点列全部沿用第四轮，逐格宽度不变；
页脚因锚在画布底部，随 PH 同步上移，与第 4 行的空隙仍是 6.9 mm。

运行（在本文件所在目录）：
    python build_180mm_paneltext.py            # 600 dpi 正式出图
    python build_180mm_paneltext.py --smoke    # 100 dpi 自检
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

import build_shared_variants as BS   # noqa: E402
import build_180mm as B180           # noqa: E402

BASE = BS.BASE
OUT_ROOT = HERE / "outputs" / "v180pt"
SMOKE = "--smoke" in sys.argv

PW = 180.0
MG = 3.2
GAP = 2.6
UMAP_CAP = 34.0

# J.tag 在 title / note 都为空时 block_h = 0.9 mm，故 gap 4.1 + 0.9 = 5.0 mm：
# 面板字母顶正好落在 axes 上沿 5.0 mm 处，字形底边距 axes 还有约 2.4 mm。
LETTER_GAP_MM = 5.0

TAG_OLD = '''def tag(ax, letter, title, w, note=None):
    # 来源图的副注在标题正下方一行；放进 J.tag 的 note 槽，不再浮在图内右上角压标题
    J.tag(ax.figure, ax, letter, title, note=note,
          gap_mm=1.5, tx_mm=3.4, size_letter=9.0, size_title=6.6,
          size_note=6.0, max_mm=max(20.0, w - 4.2))
'''

TAG_NEW = '''def tag(ax, letter, title, w, note=None):
    # 第六轮：子图句式标题 + 灰色副注整块删除，只保留面板字母
    # title/note 传空后 J.tag 的 block_h = 0.9 mm，gap 4.1 + 0.9 = 5.0 mm，
    # 字母顶距 axes 上沿 5.0 mm，字形底距 axes 约 2.4 mm，不压绘图区。
    J.tag(ax.figure, ax, letter, None, note=None,
          gap_mm=4.1, tx_mm=3.4, size_letter=9.0, size_title=6.6,
          size_note=6.0, max_mm=max(20.0, w - 4.2))
'''

# ---------------------------------------------------------------- 两个版本
VARIANTS = [
    dict(key="P", name="V180PT_P", ph=239.6,
         row_top=[18.3, 64.5, 116.4, 162.6],
         header=True,
         stem="F3_P08_paneltext_P_180mm",
         desc="恢复整版页眉 + 保留面板字母 + 删除全部子图标题与副注"),
    dict(key="Q", name="V180PT_Q", ph=229.5,
         row_top=[8.2, 54.4, 106.3, 152.5],
         header=False,
         stem="F3_P08_paneltext_Q_180mm",
         desc="延续上一轮的无页眉状态 + 保留面板字母 + 删除全部子图标题与副注"),
]


def patched_source(v: dict) -> str:
    s = BASE.read_text(encoding="utf-8")

    extra = list(B180.EXTRA) if v["header"] else list(B180.EXTRA[:3]) + [B180.EXTRA[4]]
    if not v["header"]:
        # 页眉整块删除（连带前导换行一起去掉，避免留空行）
        extra.append(("    fig = J.plate(PW, PH)\n    J.header(fig, *HEADER)\n",
                      "    fig = J.plate(PW, PH)\n", 1))
    extra += [
        (TAG_OLD, TAG_NEW, 1),
        ("ROW_TOP = [26.0, 79.0, 138.0, 191.0]",
         f"ROW_TOP = {v['row_top']}", 1),
    ]

    for old, new, n in list(BS.PATCHES) + extra:
        cnt = s.count(old)
        assert cnt == n, f"patch mismatch ({cnt} != {n}): {old[:76]!r}"
        s = s.replace(old, new)

    marker = "\ndef main():\n"
    assert s.count(marker) == 1
    s = s.replace(marker, "\n" + BS.HELPERS + "\ndef main():\n", 1)

    # 沿用第四轮 positions()：UMAP 框宽 = 行高 x 数据宽高比
    pat = re.compile(r"def positions\(\):.*?\n    return out\n", re.S)
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: B180.POSITIONS, s, count=1)

    assert "letter, None, note=None" in s, "子图标题未删除"
    assert ("J.header(" in s) == v["header"], "页眉状态不符"
    return s


def run_one(v: dict):
    src = patched_source(v)
    (HERE / f"_patched_v180pt_{v['key']}_preview.py").write_text(src, encoding="utf-8")

    ns = {"__name__": f"_f3_v180pt_{v['key']}_mod", "__file__": str(BASE),
          "MASTER_N": 10, "ALIGN_GRID": True, "SHARE_LEGEND": True}
    exec(compile(src, str(BASE), "exec"), ns)

    PH = v["ph"]
    ns["VARIANT_DPI"] = 100 if SMOKE else 600
    ns["VARIANT_CFG"] = dict(name=v["name"], pw=PW, ph=PH, gap=GAP,
                             umap_w=UMAP_CAP, mg=MG, desc=v["desc"])
    ns["PW"] = PW
    ns["PH"] = PH
    ns["ALIGN_GRID"] = True
    ns["MASTER_N"] = 10
    ns["SHARE_LEGEND"] = True
    ns["AX_REC"] = []
    ns["GEOM_REPORT"] = []
    if v["header"]:
        ns["HEADER"] = (
            "Figure 3 · F3_P08",
            "The NR-FB state across four single-cell atlases, and what defines it",
            (f"F3_P08 v9 180 mm - {PW:.0f} x {PH:.1f} mm - one state column per "
             "UMAP + CORE20 pair - 18 panels, re-drawn from source tables"),
        )
    else:
        ns["HEADER"] = ()
    stem = v["stem"]
    ns["OUT_PNG"] = OUT_ROOT / f"{stem}.png"
    ns["OUT_PDF"] = OUT_ROOT / f"{stem}.pdf"
    ns["OUT_MAP"] = OUT_ROOT / f"{stem}_面板映射.csv"
    ns["OUT_META"] = OUT_ROOT / f"{stem}_meta.json"

    pos = ns["positions"]()
    print(f"=== {v['name']}  PW={PW}  PH={PH}  ROW_TOP={v['row_top']}  "
          f"header={'yes' if v['header'] else 'no'} ===", flush=True)
    for L in "ABCDEFGHIJKLMNOQRT":
        print(f"  {L}  x={pos[L][0]:7.2f}  w={pos[L][2]:6.2f}", flush=True)

    ns["main"]()

    from PIL import Image
    with Image.open(ns["OUT_PNG"]) as im:
        px = im.size
    geom = list(ns["GEOM_REPORT"])
    (OUT_ROOT / f"geometry_report_{v['key']}.json").write_text(
        json.dumps({v["name"]: geom}, ensure_ascii=False, indent=2), encoding="utf-8")
    rec = dict(ns["VARIANT_CFG"], status="ok", stem=stem,
               header="kept" if v["header"] else "removed",
               panel_titles="removed (18 titles + 18 grey notes)",
               panel_letters="kept",
               row_top=v["row_top"],
               png_bytes=ns["OUT_PNG"].stat().st_size,
               png_md5=hashlib.md5(ns["OUT_PNG"].read_bytes()).hexdigest().upper(),
               pdf_bytes=ns["OUT_PDF"].stat().st_size,
               width_px=px[0], height_px=px[1],
               widths={L: round(pos[L][2], 2) for L in pos},
               plot={r["letter"]: r["plot_mm"] for r in geom})
    (OUT_ROOT / f"v180pt_summary_{v['key']}.json").write_text(
        json.dumps([rec], ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT_ROOT / f"面板宽度_{v['key']}.csv").open(
            "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["panel", "x_mm", "w_mm"])
        for L in "ABCDEFGHIJKLMNOQRT":
            w.writerow([L, round(pos[L][0], 2), round(pos[L][2], 2)])
    print(f"\nOK {stem}  {px[0]}x{px[1]} px  md5={rec['png_md5']}", flush=True)
    return rec


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    recs = [run_one(v) for v in VARIANTS]
    (OUT_ROOT / "v180pt_summary.json").write_text(
        json.dumps(recs, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
