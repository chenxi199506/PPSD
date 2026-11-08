#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配色文档补丁 —— 把合稿 HTML 里几处**跟不上图**的色表改成与像素一致。

为什么要单独一步
----------------
`切换Figure3版本.py` 每次都从字节级原稿 `PCDH9_合稿_配色统一_20261106_原稿.html`
重建，所以直接手改输出文件会被下一次重建冲掉。本脚本是流水线的**最后一步**，
只做纯文本替换，幂等，可反复运行。

改的五处（全部是「文档说 A、图上是 B」）
--------------------------------------
P1  A.3 调色板的 G1–G5 标签写着 Healthy / OA / Sage / Gray / Plum，
    但这一节服务的是 Figure S1（蛋白）与 Figure 5（功能），
    那五个组是 NT-CM / KD-CM / Rescue / Vehicle / Mock。
    色号本来就对，错的只是标签 —— 所以只改标签，一个色号都不动。
P2  §6.7 美术参数的「组色」行写的还是旧 04_figures.py 的
    #BFBFBF / #8C8C8C / #C0392B / #E39C90 / #2F5D8A，
    现行 Figure 6 一个都不用。改为 draw_figure6_f3.py 的 COL5。
P3  13 基因 × 25 列热图的表头色块，同上，还是旧色。
P4  §6.7 的两条色标行写 RdBu_r ±2.0 / ±0.45，现行是 CMAP_V23 ±2.0 /
    CMAP_V23_D ±0.36。
P5  「改风格的三个入口」指向 04_figures.py 的行号，那个脚本已不在链上。

用法
----
    python3 配色文档补丁.py --work-mode            # 就地修补
    python3 配色文档补丁.py --work-mode --dry-run  # 只看会改什么
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

HTML_NAME = "PCDH9_合稿_F6定稿_20261108.html"

# ------------------------------------------------------------------ 补丁
# (编号, 说明, 旧串, 新串)
PATCHES: list[tuple[str, str, str, str]] = []

PATCHES.append((
    "P1",
    "A.3 调色板 G1–G5 标签（Healthy/OA → NT-CM/KD-CM/Rescue/Vehicle/Mock，色号不动）",
    '<div class="pal"><span class="swatch"><i style="background:#4C78A8"></i>G1 / Healthy'
    '<code>#4C78A8</code></span><span class="swatch"><i style="background:#B4482F"></i>'
    'G2 / OA<code>#B4482F</code></span><span class="swatch"><i style="background:#6B8E6F">'
    '</i>G3 / Sage<code>#6B8E6F</code></span><span class="swatch"><i style="background:'
    '#8C8C8C"></i>G4 / Gray<code>#8C8C8C</code></span><span class="swatch"><i style='
    '"background:#8E6C8A"></i>G5 / Plum<code>#8E6C8A</code></span><span class="swatch">'
    '<i style="background:#C9A227"></i>S and<code>#C9A227</code></span></div>',
    '<div class="pal"><span class="swatch"><i style="background:#4C78A8"></i>G1 / NT-CM'
    '<code>#4C78A8</code></span><span class="swatch"><i style="background:#B4482F"></i>'
    'G2 / KD-CM<code>#B4482F</code></span><span class="swatch"><i style="background:#6B8E6F">'
    '</i>G3 / Rescue<code>#6B8E6F</code></span><span class="swatch"><i style="background:'
    '#8C8C8C"></i>G4 / Vehicle<code>#8C8C8C</code></span><span class="swatch"><i style='
    '"background:#8E6C8A"></i>G5 / Mock<code>#8E6C8A</code></span><span class="swatch">'
    '<i style="background:#C9A227"></i>SAND<code>#C9A227</code></span></div>',
))

PATCHES.append((
    "P2",
    "§6.7 组色行（旧 04_figures.py 五色 → 现行 Figure 6 的 COL5）",
    "<tr><td>组色</td><td>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#BFBFBF'></span>G1 #BFBFBF</span>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#8C8C8C'></span>G2 #8C8C8C</span>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#C0392B'></span>G3 #C0392B</span>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#E39C90'></span>G4 #E39C90</span>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#2F5D8A'></span>G5 #2F5D8A</span>\n"
    "</td><td>G1 灰、G2 深灰、G3 红（主敲低）、G4 浅红（第二条）、G5 蓝（回补）</td></tr>",
    "<tr><td>组色</td><td>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#7FA8C9'></span>G1 #7FA8C9</span>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#4C78A8'></span>G2 #4C78A8</span>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#B4482F'></span>G3 #B4482F</span>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#B4482F'></span>G4 #B4482F</span>\n"
    "<span style='white-space:nowrap;margin-right:14px'><span class='sw' "
    "style='background:#6B8E6F'></span>G5 #6B8E6F</span>\n"
    "</td><td>G1 浅钢蓝（未处理基线，退到最后）、G2 钢蓝（对照）、G3 / G4 砖红"
    "（两条 siRNA，被检验的量）、G5 鼠尾草绿（回补）。与 A.3（Figure S1 / Figure 5）"
    "同组同色：NT-CM / NT siRNA=#4C78A8、KD=#B4482F、Rescue=#6B8E6F</td></tr>",
))

PATCHES.append((
    "P3",
    "13 基因 × 25 列热图的表头色块（同上）",
    "<th colspan='5' style='background:#BFBFBF;color:#2b2b2b'>Untreated</th>\n"
    "<th colspan='5' style='background:#8C8C8C;color:#ffffff'>NT siRNA</th>\n"
    "<th colspan='5' style='background:#C0392B;color:#ffffff'>siRNA-1</th>\n"
    "<th colspan='5' style='background:#E39C90;color:#2b2b2b'>siRNA-2</th>\n"
    "<th colspan='5' style='background:#2F5D8A;color:#ffffff'>Rescue</th>",
    "<th colspan='5' style='background:#7FA8C9;color:#2b2b2b;"
    "border-right:2px solid #fff'>Untreated</th>\n"
    "<th colspan='5' style='background:#4C78A8;color:#ffffff;"
    "border-right:2px solid #fff'>NT siRNA</th>\n"
    "<th colspan='5' style='background:#B4482F;color:#ffffff;"
    "border-right:2px solid #fff'>siRNA-1</th>\n"
    "<th colspan='5' style='background:#B4482F;color:#ffffff;"
    "border-right:2px solid #fff'>siRNA-2</th>\n"
    "<th colspan='5' style='background:#6B8E6F;color:#ffffff'>Rescue</th>",
))

PATCHES.append((
    "P4a",
    "§6.7 热图色标行（RdBu_r → CMAP_V23）",
    "<tr><td>热图色标</td><td><code>RdBu_r</code>，vmin −2.0 / vmax 2.0</td>",
    "<tr><td>热图色标</td><td><code>CMAP_V23</code>"
    "（#4C78A8→#C9D9E6→#F3F0EE→#DCAE9C→#B4482F），vmin −2.0 / vmax 2.0</td>",
))

PATCHES.append((
    "P4b",
    "§6.7 点图色标行（RdBu_r ±0.45 → CMAP_V23_D ±0.36）",
    "<tr><td>点图色标</td><td><code>RdBu_r</code>，vmin −0.45 / vmax 0.45</td>"
    "<td>神经基因的 log2FC 都在 ±0.45 内，用热图那套 ±2.0 会全变白</td>",
    "<tr><td>点图色标</td><td><code>CMAP_V23_D</code>（中点压深到 #E4DFDA），"
    "vmin −0.36 / vmax 0.36</td>"
    "<td>神经基因的 log2FC 都在 ±0.36 内，用热图那套 ±2.0 会全变白</td>",
))

PATCHES.append((
    "P6",
    "A.3 强调 ACCENT 行补使用范围与裁决理由（2026-11-08 决定保留旧红）",
    "<tr><td>强调 ACCENT</td><td>#C1272D</td>"
    "<td>只留给被检验的那个量，不做装饰</td></tr>",
    "<tr><td>强调 ACCENT</td><td>#C1272D</td>"
    "<td>只留给被检验的那个量，不做装饰。<b>现行由 Figure 3 使用</b>"
    "（NR-FB core 状态身份，实测约 1.42 万像素）。它与 <code>#B4482F</code> "
    "分属两个语义层，<b>不是色板残留，勿按残留清理</b>。"
    "2026-11-08 已实跑并入 <code>#B4482F</code> 的替代版并做 CIEDE2000 量化："
    "与 AP-1 stress 橙 <code>#E08A5F</code> 在 α≈0.5 的观感档只剩 ΔE 8.9"
    "（旧红 16.1），UMAP 密集小点会糊在一起，故 <b>决定 Figure 3 保留旧红</b></td></tr>",
))

PATCHES.append((
    "P5",
    "「改风格的三个入口」指向已不在链上的 04_figures.py",
    "<div class='box'><b>改风格的三个入口。</b>① 组色改 <code>04_figures.py</code> "
    "第 41 行的 <code>COL</code> 字典，供体灰阶改第 43 行 <code>DCOL</code>；"
    "② 色标范围改 D 面板第 234 行、E 面板第 287 行的 <code>vmin/vmax</code>；"
    "③ 字号与线宽改第 15–31 行的 <code>rcParams</code>。这三处改完重跑脚本，"
    "数据一个字节都不动——数据都在本节。A 面板没有数据（纯示意），"
    "它的框线坐标写在第 131–184 行，换风格时直接改坐标即可。</div>",
    "<div class='box'><b>改风格的三个入口。</b>现行 Figure 6 由 "
    "<code>Figure6_F3配色定稿_20261108/src/draw_figure6_f3.py</code> 单脚本绘制，"
    "不再是 <code>04_figures.py</code>。① 组色改脚本顶部的 <code>BRICK / CONTROL / "
    "SAGE / GREY_BOX / STEEL / PLUM</code> 六个常量，以及其下的 <code>COL5</code>"
    "（五个培养条件）与 <code>COL_M</code>（五个 MEA 组）两个字典；"
    "② 色标改 <code>CMAP_V23</code> / <code>CMAP_V23_D</code> 与 C、D 面板的 "
    "<code>vmin/vmax</code>；③ 字号与线宽改 <code>src/style.py</code> 的 "
    "<code>FS</code> 与 <code>W_*</code>。改完重跑 "
    "<code>python3 src/draw_figure6_f3.py</code>，数据一个字节都不动——"
    "数据在 <code>plot_data/</code>。换出来的 PNG 要把 md5 同步进 "
    "<code>切换Figure3版本.py</code> 与 <code>校验_Figure3合稿.py</code>，"
    "否则合稿流水线会拒绝嵌入。</div>",
))

# ------------------------------------------------------------------ P7 图片
# 合稿里的 Figure 4 是一张 base64 内嵌 PNG（35 张内嵌图之一，
# 挂在 <figure data-figure="f4-submission"> 下）。
# 2026-11-08 把 Figure 4 的 ACCENT 由 #C1272D 并入主题砖红 #B4482F，
# 图换了，但合稿内嵌的还是旧字节 —— 这一步把内嵌 PNG 一并换掉。
#
# old 串不是硬编码，而是从本目录里那份旧图副本重算：
#   _P7_fig4_old_ACCENT-C1272D_686cdf14.png（1,840,331 B，md5 686cdf14…）
# 该文件的字节与合稿内嵌的那段 base64 **逐位一致**，所以能精确命中 1 次。
# 换成文件读取而不是硬编码 2.4 MB 字符串，是为了脚本可读、可 diff。
#
# 幂等性沿用文本补丁的判据：合稿里出现 new 串就跳过；出现 old 串 1 次就替换；
# 两者都不出现则报 FAIL 并拒绝写入。
_F4_OLD_PNG = Path(__file__).with_name("_P7_fig4_old_ACCENT-C1272D_686cdf14.png")
_F4_NEW_PNG = Path(
    "project_root/01_正文图/20261107_投稿图版可编辑包/"
    "最小复现总包/24_图版01-07_最小复现总包_20261106/04_Tissue/"
    "Figure4_data_package_20261106/figures/Figure4_12panel_AL_180mm.png"
)

if _F4_OLD_PNG.exists() and _F4_NEW_PNG.exists():
    _old_md5 = hashlib.md5(_F4_OLD_PNG.read_bytes()).hexdigest()
    _new_md5 = hashlib.md5(_F4_NEW_PNG.read_bytes()).hexdigest()
    assert _old_md5 == "686cdf14cdfd2a5d9e95e9e4ba940f69", (
        f"旧图副本被改动过（md5={_old_md5}），补丁的 old 串将无法命中合稿"
    )
    PATCHES.append((
        "P7",
        f"合稿内嵌 Figure 4 换成 ACCENT 并入砖红后的新产物"
        f"（{_old_md5[:8]} → {_new_md5[:8]}）",
        base64.b64encode(_F4_OLD_PNG.read_bytes()).decode("ascii"),
        base64.b64encode(_F4_NEW_PNG.read_bytes()).decode("ascii"),
    ))
else:
    print("[WARN] P7 跳过：缺少旧图副本或新 Figure 4 产物", file=sys.stderr)


def md5_of(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work-mode", action="store_true", help="路径相对脚本所在目录")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    base = Path(__file__).resolve().parent if args.work_mode else Path.cwd()
    html = base / "合稿" / HTML_NAME
    if not html.exists():
        raise SystemExit(f"[FAIL] 找不到合稿文件：{html}")

    raw = html.read_bytes()
    before_md5 = md5_of(raw)
    s = raw.decode("utf-8")

    print(f"输入  {html.name}  {len(raw):,} bytes  md5={before_md5}")
    changed = 0
    skipped = 0
    fail = 0
    for tag, desc, old, new in PATCHES:
        n = s.count(old)
        if n == 1:
            s = s.replace(old, new, 1)
            changed += 1
            print(f"  [{tag}] 已改   {desc}")
        elif n == 0 and s.count(new) == 1:
            skipped += 1
            print(f"  [{tag}] 已是最新 {desc}")
        else:
            fail += 1
            print(f"  [{tag}] [FAIL] 旧串命中 {n} 次（应为 1），未改动：{desc}")

    if fail:
        raise SystemExit(f"[FAIL] {fail} 处未命中，文件未写入。旧串可能与现行 HTML 已不一致。")

    new_raw = s.encode("utf-8")
    after_md5 = md5_of(new_raw)
    if changed == 0:
        print("无改动，文件未写入。")
        return 0
    if args.dry_run:
        print(f"dry-run：{len(raw):,} -> {len(new_raw):,} bytes  md5={after_md5}")
        return 0

    bak = html.with_suffix(html.suffix + ".bak_before_palette_patch")
    shutil.copy2(html, bak)
    html.write_bytes(new_raw)
    print(f"已写入  {html.name}  {len(new_raw):,} bytes  md5={after_md5}")
    print(f"备份    {bak.name}")
    print(f"合计 {changed} 处修改 / {skipped} 处已是目标状态")
    return 0


if __name__ == "__main__":
    sys.exit(main())
