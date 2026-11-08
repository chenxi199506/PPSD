#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合稿 HTML · Figure 3 180 mm 更新终检（2026-11-07）。

检查内容
--------
1. 11-06 字节级原稿备份完好；更新后的 HTML 与之可比。
2. `<section id="f3">` 的「当前版」区域确实换成 180 mm 版；
   第一个 `<details class="f3-archive">` 之后的全部历史归档区**逐字符不变**。
3. 内嵌 PNG 数量不变；当前版内嵌图 = 指定 variant 的 PNG（逐字节、md5 一致）；
   另一个 variant 的 base64 不在文件里。
4. 当前版区域里所有 v9 口径的旧数值 / 旧说法清干净；全局 4 处修订说明到位。
5. `Figure3_180mm_20261107/...` 工具条链接指向的文件真实存在。
6. **2026-11-08 追加**：Figure 6 定稿（第 38 张内嵌 PNG）逐字节等于
   `合稿/Figure6_F3配色定稿_20261108/Figure6_F3配色.png`；横幅 / 侧栏 / 来源说明
   三处版本文案到位；旧的 α 0.45 版 Figure 6 未被残留。

   归档完整性检查采用「差分还原」：先把 F6 定稿的两处尾部改动（内嵌图替换 +
   来源说明段）在内存里还原，再与 11-06 原稿逐字符比对，
   这样既保留「除已知更新外一字未动」的强断言，又不会把 F6 定稿误判成归档被改。

用法
----
    python3 校验_Figure3合稿.py --work-mode                 # 默认检查 P 版
    python3 校验_Figure3合稿.py --work-mode --variant Q
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJ = Path("ppsd_workspace/fig3_20261106")
ORIGINAL_MD5 = "ADA8912CFDE71520F50338D2D51EE14E"
RES_DIR = "Figure3_180mm_20261107"
CANONICAL_HTML = "PCDH9_合稿_F6定稿_20261108.html"

# ---- Figure 6 定稿（2026-11-08） ------------------------------------------
F6_DIR = "Figure6_F3配色定稿_20261108"
F6_PNG = "Figure6_F3配色.png"
F6_PNG_MD5 = "4616E4C0C1CD9B332E6CF92BCC517E49"   # v3 配色对账修正（2026-11-08）
F6_PNG_MD5_SUPERSEDED = "B0FDB664317F028E7822196666C62BC7"  # v2 NAVY/TEAL 版
F6_OLD_ASSET_MD5 = "12330eceb2cb67da4eeb0fa0a8bec24c"
N_ASSETS = 66
F6_ASSET_INDEX = 37
ASSET_PAT = re.compile(rb'data:(image/[a-z+]+);base64,([A-Za-z0-9+/=\s]+)')
F6_PROV_P = (
    '<p class="muted">2026-11-08 更新：当前图版为整幅原生重绘（180 × 158 mm · 600 dpi），'
    '数据取自 <code>plot_data/*.csv</code>，配色沿用 Figure 3 B 的单一强调色语法；'
    'A–H 八个面板的数据、统计量、显著性标注与面板对应关系均未改。</p>'
)

VARIANTS = {
    "P": dict(stem="F3_P08_paneltext_P_180mm",
              md5="BEEE9FE85C9411728420187703251903",
              px=(4251, 5659), mm=(180.0, 239.6)),
    "Q": dict(stem="F3_P08_paneltext_Q_180mm",
              md5="6A118E9200F29DD62CFB611BCFD2A0D3",
              px=(4251, 5421), mm=(180.0, 229.5)),
}

problems: list[str] = []
checks = 0


def md5_bytes(b: bytes) -> str:
    return hashlib.md5(b).hexdigest().upper()


def load_palette_patches() -> list[tuple[str, str, str, str]]:
    """从同目录的 `配色文档补丁.py` 取补丁表，供归档比对时反向还原。

    补丁脚本不存在或读不出时返回空表——那样校验会退回到「只还原 F6 两处」的
    旧行为，仍然安全（只是若文件已打过补丁，这项会如实报 FAIL）。
    """
    p = Path(__file__).resolve().parent / "配色文档补丁.py"
    if not p.exists():
        return []
    try:
        spec = importlib.util.spec_from_file_location("_palette_patch_mod", p)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)          # 只取常量，主函数不会执行
        return list(getattr(mod, "PATCHES", []))
    except Exception as exc:                   # noqa: BLE001
        print(f"  [WARN] 读不出配色文档补丁.py：{exc}")
        return []


def ck(cond: bool, label: str, detail: str = "") -> None:
    global checks
    checks += 1
    if cond:
        print(f"  [OK]   {label}" + (f"  {detail}" if detail else ""))
    else:
        problems.append(label + ("  " + detail if detail else ""))
        print(f"  [FAIL] {label}" + (f"  {detail}" if detail else ""))


def resolve(args):
    if args.work_mode:
        base = Path(__file__).resolve().parent
        g = base / "合稿"
        return (args.html or g / CANONICAL_HTML,
                args.backup or g / "PCDH9_合稿_配色统一_20261106_原稿.html",
                args.res or g / RES_DIR,
                args.pngs or g / RES_DIR)
    return (args.html or PROJ / "delivery" / CANONICAL_HTML,
            args.backup or PROJ / "delivery/_原稿备份_20261107/PCDH9_合稿_配色统一_20261106_原稿.html",
            args.res or PROJ / "delivery/" / RES_DIR,
            args.pngs or PROJ / "width_variants/v180pt_delivery/figures")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=("P", "Q"), default="P")
    ap.add_argument("--work-mode", action="store_true")
    ap.add_argument("--html", type=Path)
    ap.add_argument("--backup", type=Path)
    ap.add_argument("--res", type=Path, help="Figure3_180mm_20261107 资源目录")
    ap.add_argument("--pngs", type=Path, help="P/Q PNG 所在目录")
    ap.add_argument("--f6-src", type=Path,
                    help=f"Figure 6 定稿资源目录（含 {F6_PNG}）")
    args = ap.parse_args()

    html, backup, res, pngs = resolve(args)
    f6_src = args.f6_src or (
        Path(__file__).resolve().parent / "合稿" / F6_DIR
        if args.work_mode else PROJ.parent / "fig6_redraw_20261107" / "out_f3")
    v = VARIANTS[args.variant]
    other = VARIANTS["Q" if args.variant == "P" else "P"]

    print(f"HTML   : {html}")
    print(f"备份   : {backup}")
    print(f"资源   : {res}")
    print(f"F6 源  : {f6_src}")
    print(f"变体   : {args.variant}  {v['stem']}")
    print()

    # ---------------------------------------------------------------- 原稿 ----
    ck(backup.is_file(), "11-06 字节级原稿备份存在")
    if not backup.is_file():
        raise SystemExit(1)
    orig_b = backup.read_bytes()
    ck(md5_bytes(orig_b) == ORIGINAL_MD5, "原稿 md5 仍为 ADA8912C…", md5_bytes(orig_b))
    ck(html.is_file(), "更新后的合稿 HTML 存在")
    if not html.is_file():
        raise SystemExit(1)
    out_b = html.read_bytes()
    ck(md5_bytes(out_b) != ORIGINAL_MD5, "合稿 HTML 已确实更新（md5 变化）",
       md5_bytes(out_b))

    original = orig_b.decode("utf-8")
    out = out_b.decode("utf-8")

    # 两侧都取第 38 张内嵌图的 base64，用于「差分还原」归档比对
    ms_o = list(ASSET_PAT.finditer(orig_b))
    ms_n = list(ASSET_PAT.finditer(out_b))
    ck(len(ms_o) == N_ASSETS and len(ms_n) == N_ASSETS,
       "原稿 / 合稿的内嵌资源数均为 66",
       f"原稿 {len(ms_o)} 张 · 合稿 {len(ms_n)} 张")
    old_b64 = (re.sub(rb"\s+", b"", ms_o[F6_ASSET_INDEX].group(2)).decode("ascii")
               if len(ms_o) == N_ASSETS else "")
    new_b64 = (re.sub(rb"\s+", b"", ms_n[F6_ASSET_INDEX].group(2)).decode("ascii")
               if len(ms_n) == N_ASSETS else "")

    # ------------------------------------------------------------ 归档完整性 ----
    # F6 定稿在「首个归档区之后」只动了两处：第 38 张内嵌图 + 图前来源说明段。
    # 配色文档补丁（最后一步）又会动六处色表文字，同样落在归档区之后。
    # 把这些**已知更新**全部反向还原回 11-06 原稿再逐字符比对，就能继续保留
    # 「除已知更新外一字未动」的强断言，而不是把断言放宽。
    out_reverted = out.replace(new_b64, old_b64, 1)
    out_reverted = out_reverted.replace(F6_PROV_P, "", 1)

    n_pal_reverted = 0
    for _tag, _desc, _old, _new in load_palette_patches():
        if _new in out_reverted:
            out_reverted = out_reverted.replace(_new, _old, 1)
            n_pal_reverted += 1

    a0 = original.find('<section id="f3">')
    b0 = original.find('<details class="f3-archive"', a0)
    a1 = out.find('<section id="f3">')
    b1 = out.find('<details class="f3-archive"', a1)
    b1r = out_reverted.find('<details class="f3-archive"', a1)
    ck(min(a0, b0, a1, b1, b1r) >= 0, "两侧都能定位 f3 section / 首个归档区")
    if min(a0, b0, a1, b1, b1r) < 0:
        raise SystemExit(1)
    ck(original[b0:] == out_reverted[b1r:],
       "还原 F6 两处 + 配色文档补丁后，历史归档区及其后全文逐字符不变",
       f"{len(original[b0:]):,} 字符 · 已还原 {2 + n_pal_reverted} 处已知更新")
    ck(out.count('<section id="f3">') == 1, "全文只有一个 f3 section")
    ck(out.count('data:image/png;base64,') == original.count('data:image/png;base64,'),
       "内嵌 PNG 总数不变", f"{out.count('data:image/png;base64,')} 张")
    for key in ('data-figure="f3-p08-v5"', 'data-figure="f3-submission"',
                'data-figure="f3-merged"'):
        ck(key in out, f"归档图仍在  {key}")
    ck('600decbf561c2780715a2e84d868085d' in out, "v9 md5 归档说明仍在")
    ck('历史版本归档' in out, "历史版本归档标题仍在")
    ck(out.count('<figure') == original.count('<figure'),
       "figure 标签总数不变", f"{out.count('<figure')} 个")
    ck(out.count('<details') == original.count('<details'),
       "details 标签总数不变", f"{out.count('<details')} 个")

    # -------------------------------------------------------------- 当前版图 ----
    cur = out[a1:b1]
    ck('<figure data-figure="f3-p08-180mm"' in cur, "当前版 figure 已换成 f3-p08-180mm")
    ck('data-figure="f3-p08-v9"' not in cur, "当前版不再挂 v9 的 figure key")
    ck('id="captions-f3-p08-180mm"' in cur, "图注容器 id 已更新")
    ck('id="captions-f3-p08-v9"' not in cur, "旧图注容器 id 已清除")

    png = pngs / f"{v['stem']}.png"
    ck(png.is_file(), f"variant {args.variant} 源 PNG 存在", png.name)
    if png.is_file():
        raw = png.read_bytes()
        ck(md5_bytes(raw) == v["md5"], "源 PNG md5 与预期一致", md5_bytes(raw))
        b64 = base64.b64encode(raw).decode("ascii")
        ck(out.count(b64) == 1, "合稿内嵌 base64 与源 PNG 完全一致且只出现一次")
        m = re.search(r'<figure data-figure="f3-p08-180mm".*?<img src="data:image/png;base64,([^"]+)"',
                      cur, re.S)
        ck(bool(m) and m.group(1) == b64, "当前版那一张内嵌图就是所选 variant")
        other_png = pngs / f"{other['stem']}.png"
        if other_png.is_file():
            ob64 = base64.b64encode(other_png.read_bytes()).decode("ascii")
            ck(ob64 not in out, f"另一 variant ({other['stem']}) 未被误嵌")
        if m:
            got = base64.b64decode(m.group(1))
            ck(md5_bytes(got) == v["md5"], "反解内嵌图 md5 = 主图 md5")
        ck(f'width="{v["px"][0]}" height="{v["px"][1]}"' in cur,
           "img 宽高标注与 600 dpi 像素一致", f'{v["px"][0]}×{v["px"][1]}')

    # -------------------------------------------------- 当前版旧口径清除 ----
    stale = [
        ("UMAP state legends sit in a 22 mm right-side gutter", "旧 EN 图注「22 mm 独立图例栏」"),
        ("A / I / N / Q 四个 UMAP 的状态图例置于点位右侧单列", "旧中文图注「右侧单列图例」"),
        ("7559 × 5905", "v9 像素 7559×5905"),
        ("画幅 320 × 250 mm（工作稿横版）", "v9 画幅说明"),
        ("展开版式、验收与必须保留的证据边界（v9）", "v9 版式验收折叠块"),
        ("主图 md5 前缀 <code>600decbf</code>", "v9 主图 md5 前缀"),
        ("MERGED WORKING PLATE 2026.11.06", "v9 eyebrow"),
        ("中文图注与简短结果（F3_P08 v9", "v9 中文图注 h3"),
        ("展开逐面板说明与来源（F3_P08 v9", "v9 逐面板 summary"),
        ("26_F3_P08_v9_20261106/outputs/F3_P08_面板映射_v9.csv</code> 与",
         "v9 映射路径（当前版）"),
    ]
    for s, label in stale:
        ck(s not in cur, f"当前版已清除：{label}")
    ck('formal submission to 180 mm must split' not in out,
       "全文不再有「180 mm 必须拆两张图」的旧结论")

    # ---------------------------------------------------------- 新口径到位 ----
    fresh = [
        (f'{v["mm"][0]:.1f} × {v["mm"][1]:.1f} mm', "期刊 180 mm 画幅"),
        (v["md5"].lower(), "主图 md5"),
        ("全部子图标题已删", "子图标题删除说明"),
        ("共用一列 2.4 mm 色点", "共享状态注释说明"),
        ("展开版式、验收与必须保留的证据边界（180 mm 期刊版）", "新版版式验收块"),
        ("check_layout: 0 problems", "check_layout 结论"),
        ("ρ = 0.456 / P = 0.01462 (n = 28)", "右侧 1.6 mm 墨迹归因"),
    ]
    for s, label in fresh:
        ck(s in cur, f"当前版包含：{label}")

    # ------------------------------------------------------------ 全局四处 ----
    glob = [
        ("Figure 3 180 mm 期刊版 ＋ Figure 4 修订 12 面板 A–L · 2026-11-07", "<title> 已更新"),
        ("2026-11-07 追加更新 Figure 3", "配色统一横幅已加说明"),
        ("2026.11.07 · Figure 3 → 180 mm 期刊版", "侧栏日期线已加说明"),
        ("2026-11-07 修订（Figure 3）", "intro 追加段存在"),
    ]
    for s, label in glob:
        ck(s in out[:a1], f"全局：{label}")
    ck("Figure 3 v9 ＋ Figure 4 修订" not in out[:a1], "全局：旧 title 已替换")
    ck("Figure 3 / 4 / 7 未改动。" not in out[:a1], "全局：旧横幅断言已替换")

    # ------------------------------------------------------------ 资源链接 ----
    hrefs = sorted(set(re.findall(r'href="(' + re.escape(RES_DIR) + r'/[^"]+)"', cur)))
    ck(len(hrefs) >= 8, "工具条含 180 mm 资源链接", f"{len(hrefs)} 条")
    for h in hrefs:
        ck((res.parent / h).is_file(), f"资源存在  {h[len(RES_DIR)+1:]}")

    # ------------------------------------------------------- Figure 6 定稿 ----
    f6_png = f6_src / F6_PNG
    ck(f6_png.is_file(), "Figure 6 定稿源 PNG 存在", str(f6_png))
    if f6_png.is_file():
        f6_raw = f6_png.read_bytes()
        ck(md5_bytes(f6_raw) == F6_PNG_MD5, "Figure 6 定稿源 PNG md5 正确",
           md5_bytes(f6_raw))
        ck(out.count(base64.b64encode(f6_raw).decode("ascii")) == 1,
           "合稿内嵌第 38 张 = 定稿 PNG（逐字节，且只出现一次）")
        ck(md5_bytes(base64.b64decode(new_b64)) == F6_PNG_MD5,
           "反解第 38 张内嵌图 md5 = 定稿 PNG md5")
        ck(old_b64 not in out, "旧的 α 0.45 版 Figure 6 未被残留")
    ck(out.count(F6_PROV_P) == 1, "Figure 6 图前来源说明段恰好一处")
    ck("（11-08 定稿 Figure 6）" in out[:a1], "横幅已标 11-08 定稿 Figure 6")
    ck("2026.11.08 · Figure 6 → F3 配色定稿重绘" in out[:a1],
       "侧栏版本沿革已加 11-08 一条")
    ck("← 返回替换前版本（可回滚）</a>" in out[:a1], "回滚链接已指向替换前版本")
    ck((html.parent / "PCDH9_合稿_配色统一_20261106.html").is_file(),
       "回滚目标（11-07 版合稿）真实存在")

    # ------------------------------------------------------------------ 汇总 ----
    print()
    if problems:
        print(f"[FAIL] {len(problems)} / {checks} 项未通过：")
        for p in problems:
            print("   -", p)
        raise SystemExit(1)
    print(f"ALL HTML-FIGURE3 CHECKS PASSED  ({checks} 项 · variant {args.variant} · "
          f"HTML md5 {md5_bytes(out_b)})")

    rec = dict(variant=args.variant, checks=checks, html_md5=md5_bytes(out_b),
               html_bytes=len(out_b), canonical_html=html.name,
               embedded_png_md5=v["md5"],
               f6_png_md5=F6_PNG_MD5, f6_asset_index=F6_ASSET_INDEX + 1,
               original_md5=ORIGINAL_MD5, archive_chars_unchanged=len(original[b0:]),
               resource_links=len(hrefs))
    out_json = Path(__file__).resolve().parent / "_合稿终检记录.json"
    out_json.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"记录：{out_json}")


if __name__ == "__main__":
    main()
