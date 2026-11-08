"""F3_P08 v9 · 180 mm 宽 / 无标题版（2026-11-07 第五轮）。

用户反馈（原话）：
  "很好，请你去掉所有的标题和副标题"

本版在 `build_180mm.py`（第四轮 180 mm 版）之上只做一件事：
去掉整版页眉，也就是 `J.header()` 画的那三行文字 ——
  ① "Figure 3 · F3_P08"（编号）
  ② "The NR-FB state across four single-cell atlases, and what defines it"（主标题）
  ③ "F3_P08 v9 180 mm - ... - re-drawn from source tables"（副标题）

三行合计占掉画布顶部 10.6 mm。删掉后如果不动行位置，顶部会留一条 11.2 mm 的
空白带 —— 比左右页边（3.2 mm）大三倍多，肉眼一眼能看出。所以同步把四行整体
上移，并把画布高度收掉同样的量：

  Δ = 14.44 mm（第 1 行标题块顶）− 3.20 mm（目标页边）= 11.24 mm
  ROW_TOP  26.0 / 79.0 / 138.0 / 191.0  →  14.8 / 67.8 / 126.8 / 179.8
  PH       268.0  →  256.8 mm

行间距、行高、面板宽度分配、UMAP 框宽、共享色点列全部沿用第四轮，逐字节等价。
副作用是整版高度降到 256.8 mm，正好落进 A4 正文区（约 257 mm）。

保留的部分（不是标题，未删）：
  * 每个面板的字母 + 分图标题 + 小注（如 "A / NR-FB forms a region"）—— 这是
    分图标签，不是整版标题；
  * 页脚那段方法学说明（"Analysis unit / Methods / Does not support"）。

运行（在本文件所在目录）：
    python build_180mm_notitle.py            # 600 dpi 正式出图
    python build_180mm_notitle.py --smoke    # 100 dpi 自检
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_shared_variants as BS   # noqa: E402
import build_180mm as B180           # noqa: E402

BASE = BS.BASE
OUT_ROOT = HERE / "outputs" / "v180nt"
SMOKE = "--smoke" in sys.argv

# ---------------------------------------------------------------- 版本参数
PW = 180.0
PH = 256.8               # 268.0 − 11.2（页眉腾出来的高度）
MG = 3.2
GAP = 2.6
UMAP_CAP = 34.0
NAME = "V180NT"

# 四行整体上移 11.2 mm；行内相对关系与第四轮完全一致
ROW_TOP_NT = [14.8, 67.8, 126.8, 179.8]

CFG = dict(name=NAME, pw=PW, ph=PH, gap=GAP, umap_w=UMAP_CAP,
           mg=MG, desc="180 mm 宽 · 无标题副标题版（页眉整块删除）")

# ---------------------------------------------------------------- 追加补丁
# B180.EXTRA 共 5 条：0 外页边、1 UMAP 边距、2 页脚事实性修正、
# 3 页眉 x 对齐、4 页脚 x 对齐。本版不要第 3 条（页眉整块删掉），
# 改为把 J.header 调用直接抹掉，并重设 ROW_TOP。
EXTRA: list[tuple[str, str, int]] = [
    *B180.EXTRA[:3],
    B180.EXTRA[4],
    # 页眉整块删除（连带前导换行一起去掉，避免留空行）
    ("    fig = J.plate(PW, PH)\n    J.header(fig, *HEADER)\n",
     "    fig = J.plate(PW, PH)\n", 1),
    # 四行上移，补偿页眉腾出的高度
    ("ROW_TOP = [26.0, 79.0, 138.0, 191.0]",
     f"ROW_TOP = {ROW_TOP_NT}", 1),
]


def patched_source() -> str:
    s = BASE.read_text(encoding="utf-8")
    for old, new, n in list(BS.PATCHES) + EXTRA:
        cnt = s.count(old)
        assert cnt == n, f"patch mismatch ({cnt} != {n}): {old[:76]!r}"
        s = s.replace(old, new)

    marker = "\ndef main():\n"
    assert s.count(marker) == 1
    s = s.replace(marker, "\n" + BS.HELPERS + "\ndef main():\n", 1)

    # 沿用第四轮的 positions()：UMAP 框宽 = 行高 x 数据宽高比
    import re
    pat = re.compile(r"def positions\(\):.*?\n    return out\n", re.S)
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: B180.POSITIONS, s, count=1)

    # 自检：页眉确实不在了
    assert "J.header(" not in s, "页眉未被删除"
    return s


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    src = patched_source()
    (HERE / "_patched_v180nt_preview.py").write_text(src, encoding="utf-8")

    ns = {"__name__": "_f3_v180nt_mod", "__file__": str(BASE),
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
    ns["HEADER"] = ()      # 无标题：meta 里的 header 落成空 dict
    stem = f"F3_P08_v180nt_{int(PW)}mm"
    ns["OUT_PNG"] = OUT_ROOT / f"{stem}.png"
    ns["OUT_PDF"] = OUT_ROOT / f"{stem}.pdf"
    ns["OUT_MAP"] = OUT_ROOT / f"{stem}_面板映射.csv"
    ns["OUT_META"] = OUT_ROOT / f"{stem}_meta.json"

    pos = ns["positions"]()
    print(f"=== {NAME}  PW={PW}  PH={PH}  MG={MG}  GAP={GAP}  (无页眉) ===",
          flush=True)
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
               header="removed: no title, no subtitle, no figure number",
               png_bytes=ns["OUT_PNG"].stat().st_size,
               png_md5=hashlib.md5(ns["OUT_PNG"].read_bytes()).hexdigest().upper(),
               pdf_bytes=ns["OUT_PDF"].stat().st_size,
               width_px=px[0], height_px=px[1],
               widths={L: round(pos[L][2], 2) for L in pos},
               plot={r["letter"]: r["plot_mm"] for r in geom})
    (OUT_ROOT / "v180nt_summary.json").write_text(
        json.dumps([rec], ensure_ascii=False, indent=2), encoding="utf-8")
    with (OUT_ROOT / "面板宽度.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["panel", "x_mm", "w_mm"])
        for L in "ABCDEFGHIJKLMNOQRT":
            w.writerow([L, round(pos[L][0], 2), round(pos[L][2], 2)])
    print(f"\nOK {stem}  {px[0]}x{px[1]} px  md5={rec['png_md5']}", flush=True)


if __name__ == "__main__":
    main()
