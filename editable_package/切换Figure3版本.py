#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把合稿 HTML 的 Figure 3 当前版换成 180 mm 无子图标题版（P / Q 可一键切换）。

设计原则
--------
1. 只改 `<section id="f3">` 里「当前版」那一段（section 开头 -> 第一个
   `<details class="f3-archive">`）；下方的 v5 / 9 面板重排 / Figure 1 合并版
   三个历史归档区一个字节都不动。
2. 换掉的是第 0 张内嵌 base64 PNG（f3-p08-v9）；其余 3 张内嵌图保持原样。
3. 所有与该图绑定的文字（eyebrow / h2 / caption / toolbar / figcaption /
   中文图注 / EN legend / 版式验收 details / legend-note）同步改成新版的
   真实数值，避免「文字说 320 mm、图片是 180 mm」自相矛盾。
4. 全局 4 处（title / 配色横幅 / aside small / intro）追加 2026-11-07 说明，
   不改写原有的 11-06 沿革陈述。
5. **始终从字节级原稿备份读取输入**，所以脚本幂等：反复运行、P↔Q 来回切换
   都不会累积改动。`--restore` 导出一份 11-06 原稿（不覆盖当前主文件）。
6. `--work-mode` 时全部路径相对脚本所在目录解析，拷到别的电脑也能跑。

2026-11-08 追加：Figure 6 定稿（F3 配色原生重绘）
--------------------------------------------------
7. Figure 3 补丁之后，追加一层 **Figure 6 定稿补丁**：把第 38 张内嵌 PNG
   （`ms[37]`）换成 `合稿/Figure6_F3配色定稿_20261108/Figure6_F3配色.png`，
   并同步横幅版本行、侧栏沿革、Figure 6 来源说明共 3 处文案。
   旧脚本「只从 11-06 原稿重建」会把这一步冲掉，来回切 P/Q 会丢定稿；
   现在整条链是「原稿 → F3 补丁 → F6 补丁」，幂等且逐字节可复现。
8. `--f6-src` 可指向别的资源目录；PNG 的 md5 有门禁，未定稿的图不会被误嵌。
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PROJ = Path("ppsd_workspace/fig3_20261106")
ORIGINAL_MD5 = "ADA8912CFDE71520F50338D2D51EE14E"
RES_DIR = "Figure3_180mm_20261107"   # HTML 内的相对资源目录

# ---- Figure 6 定稿（2026-11-08） ------------------------------------------
CANONICAL_HTML = "PCDH9_合稿_F6定稿_20261108.html"
F6_DIR = "Figure6_F3配色定稿_20261108"
F6_PNG = "Figure6_F3配色.png"
F6_PNG_MD5 = "4616E4C0C1CD9B332E6CF92BCC517E49"   # v3 配色对账修正（2026-11-08）
F6_PNG_MD5_SUPERSEDED = "B0FDB664317F028E7822196666C62BC7"  # v2 NAVY/TEAL 版，留档在 F6_DIR/Figure6_F3配色_v2_旧色_NAVY_TEAL.png
F6_OLD_ASSET_MD5 = "12330eceb2cb67da4eeb0fa0a8bec24c"   # α 0.45 旧版，拒绝误替换
N_ASSETS = 66
F6_ASSET_INDEX = 37                                        # 第 38 张内嵌图
ASSET_PAT = re.compile(rb'data:(image/[a-z+]+);base64,([A-Za-z0-9+/=\s]+)')

VARIANTS = {
    "P": dict(
        stem="F3_P08_paneltext_P_180mm",
        w_mm=180.0, h_mm=239.6, px=(4251, 5659),
        md5="BEEE9FE85C9411728420187703251903",
        pdf_bytes=175460,
        header="保留整版页眉",
        desc="P 版 · 恢复整版页眉 + 去掉全部子图标题",
    ),
    "Q": dict(
        stem="F3_P08_paneltext_Q_180mm",
        w_mm=180.0, h_mm=229.5, px=(4251, 5421),
        md5="6A118E9200F29DD62CFB611BCFD2A0D3",
        pdf_bytes=171886,
        header="无整版页眉",
        desc="Q 版 · 连整版页眉一并去掉 + 去掉全部子图标题",
    ),
}


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest().upper()


def must_replace(s: str, old: str, new: str, label: str, count: int = 1) -> str:
    n = s.count(old)
    if n != count:
        raise SystemExit(f"[FAIL] {label}: 期望命中 {count} 次，实际 {n} 次\n  片段: {old[:110]}")
    return s.replace(old, new)


def build_figure_block(v: dict, variant: str, src: Path) -> str:
    """重建当前版 eyebrow -> </figure>（含内嵌 base64）。"""
    stem = v["stem"]
    png = src / f"{stem}.png"
    raw = png.read_bytes()
    assert hashlib.md5(raw).hexdigest().upper() == v["md5"], f"PNG md5 不符 {png}"
    b64 = base64.b64encode(raw).decode("ascii")

    eyebrow = (
        "FIGURE 03 · JOURNAL-READY PLATE 2026.11.07 · F3_P08 180 MM · A–T "
        "(18 PANELS · 180 mm WIDTH · NO PANEL TITLES · SHARED STATE ANNOTATION · "
        "FULL-DATA REDRAW · 600 DPI)"
    )
    h2 = "NR-FB 成纤维细胞状态：四个单细胞图谱中的位置、疼痛关联与分子身份（180 mm 期刊版）"
    caption = (
        '<p class="caption">2026-11-07 本节主图由 <b>F3_P08 v9（320 × 250 mm 工作稿）'
        f'更新为 180 mm 期刊宽度版 · {v["desc"]}</b>。仍是<b>四行十八面板（A–T，P / S 已删，故跳号）</b>，'
        '18 个面板全部由原始表逐点 / 逐柱 / 逐箱原生重绘，<b>裁剪 / 贴图面板 0 / 18</b>；'
        '字母、面板取舍、数据源、统计口径与所有数值（Cliff\'s d、ρ、P、n）、配色、状态名与 UMAP 点坐标'
        '自 v5 起一字未动，<b>只改显示层几何</b>。相对 v9 的四步：'
        '<b>① 共享状态注释</b>——每张 UMAP 与紧邻的 CORE20 箱线图共用一列 2.4 mm 色点'
        '（既是 UMAP 图例，也是箱线图 y 轴标签，只画一次，语义上两处状态集完全相等）；'
        '<b>② UMAP 框贴合数据宽高比</b>——A / I 框内横向空白由 8.1 mm 降到 0.1 mm，点云反而大 9%；'
        '<b>③ 外页边 6.0 → 3.2 mm、面板间距 3.0 → 2.6 mm</b>；'
        '<b>④ 删掉全部 18 个子图的句式化标题与灰色副注（合计 36 行），只保留面板字母 A–T</b>，'
        '四行按实测墨迹同步压紧，画布高随之收掉。'
        f'本图为 <b>{v["header"]}</b> 的 {variant} 版，<b>{v["w_mm"]:.1f} × {v["h_mm"]:.1f} mm</b>、'
        f'{v["px"][0]} × {v["px"][1]} px @ 600 dpi，落进期刊 180 mm 宽度上限与 A4 正文区。'
        'v9 及更早版本（含 9 面板投稿重排版、Figure 1 合并版）完整保留在下方归档区与 '
        '<code>26_F3_P08_v9_20261106/</code>，未删除。'
        '图版本体纯英文；中文说明见下方图注与逐面板对照表。</p>'
    )
    toolbar = (
        '<div class="toolbar">'
        f'<a href="{RES_DIR}/{stem}.pdf">主图 PDF（当前版 180 mm · {variant}）</a>'
        f'<a href="{RES_DIR}/{stem}.png">600 dpi PNG（当前版 180 mm · {variant}）</a>'
        f'<a href="{RES_DIR}/{stem}_meta.json">元数据 JSON（含 md5）</a>'
        f'<a href="{RES_DIR}/{stem}_面板映射.csv">18 格面板映射 CSV</a>'
        f'<a href="{RES_DIR}/对照_改前改后.jpg">改前 / 改后整版对照</a>'
        f'<a href="{RES_DIR}/对照_子图标题删除.jpg">子图标题删除对照</a>'
        f'<a href="{RES_DIR}/对照_UMAP留白.jpg">UMAP 框内留白对照</a>'
        f'<a href="{RES_DIR}/32_复现包/README.md">自包含复现包说明</a>'
        '<a href="26_F3_P08_v9_20261106/outputs/F3_P08_four_rows_A-T_v9.png">上一版 v9 主图（归档 · 320 × 250 mm）</a>'
        '<a href="PCDH9_Figure3_预览_v9_20261106.html">Figure 3 单独预览页（v9 归档）</a>'
        '</div>'
    )
    alt = (
        "Figure 3, F3_P08 180 mm journal plate, 18 panels A-T, four single-cell atlases. "
        "All panel titles removed; only panel letters remain. Each UMAP shares one 2.4 mm "
        "coloured state-dot column with the adjacent CORE20 boxplot. Re-drawn from source "
        "tables; NR-FB core placed first in the six state-ordering panels; unified state "
        "names and colours; KDE density-edge UMAP outlines; plate text in English."
    )
    figure = (
        '<figure data-figure="f3-p08-180mm" style="margin:18px 0;max-width:100%">'
        f'<img src="data:image/png;base64,{b64}" alt="{alt}" '
        f'width="{v["px"][0]}" height="{v["px"][1]}" '
        'style="display:block;width:100%;height:auto;max-width:100%;border:0">'
        f'<figcaption><b>Figure 3</b>｜F3_P08 180 mm 期刊版（{variant} · {v["header"]}），'
        '四行十八面板（A–T，缺 P / S），'
        f'<b>{v["w_mm"]:.1f} × {v["h_mm"]:.1f} mm</b> · {v["px"][0]} × {v["px"][1]} px · 600 dpi · '
        '18/18 面板由原始表原生重绘，裁剪面板 0 / 18 · 全部子图标题已删，仅留面板字母 · '
        'UMAP 与相邻 CORE20 箱线图共享一列状态注释 · <code>check_layout: 0 problems</code> · '
        f'主图 md5 <code>{v["md5"].lower()}</code>。'
        '分析单位：A–C、F、G、I–K、N、O、Q、R 为细胞；D、E、H、L、M、T 为供体。'
        '图版本体纯英文；Supports / Does-not-support 与完整图注见下方。</figcaption></figure>'
    )
    return (
        f'<div class="eyebrow">{eyebrow}</div>\n'
        f'<h2>{h2}</h2>\n{caption}\n{toolbar}\n{figure}\n'
    )


def patch_current_region(cur: str, v: dict, variant: str, src: Path) -> str:
    """在「当前版」区域内做精确替换；归档区不在此字符串里。"""
    stem = v["stem"]

    # 1) eyebrow + h2 + caption + toolbar + figure 整块换掉（到第一个 </figure>）
    i = cur.find('<div class="eyebrow">')
    j = cur.find('</figure>', i)
    if i < 0 or j < 0:
        raise SystemExit("[FAIL] 找不到当前版 eyebrow / </figure>")
    cur = cur[:i] + build_figure_block(v, variant, src) + cur[j + len('</figure>'):]

    cur = must_replace(cur, '<div class="figure-legend" id="captions-f3-p08-v9"',
                       '<div class="figure-legend" id="captions-f3-p08-180mm"',
                       "figure-legend id")
    cur = must_replace(
        cur, '<h3>中文图注与简短结果（F3_P08 v9 · 四行 18 面板 A–T）</h3>',
        '<h3>中文图注与简短结果（F3_P08 180 mm 期刊版 · 四行 18 面板 A–T）</h3>',
        "中文图注 h3")
    cur = must_replace(
        cur,
        'A / I / N / Q 四个 UMAP 的状态图例置于点位右侧单列，core 细胞边缘用 KDE 5% 分位密度等值线勾勒。',
        'A / I / N / Q 四个 UMAP 的状态图例不再单列，而是与紧邻的 CORE20 箱线图共用一列 2.4 mm 色点'
        '（同时充当箱线图的 y 轴标签），core 细胞边缘用 KDE 5% 分位密度等值线勾勒。',
        "中文图注 · 图例位置")
    cur = must_replace(
        cur, 'UMAP state legends sit in a 22 mm right-side gutter;',
        'each UMAP shares a single 2.4 mm coloured state-dot column with the adjacent CORE20 '
        "boxplot (doubling as that panel's y labels);",
        "EN legend · 图例位置")
    cur = must_replace(
        cur, 'Figure 3 · F3_P08 v9. The NR-FB state is visible',
        f'Figure 3 · F3_P08 180 mm journal plate ({variant}, {v["header"]}). '
        'All 18 panel titles and grey notes have been removed; only panel letters remain. '
        'The NR-FB state is visible',
        "EN legend · 版本说明")

    # 2) 逐面板表：标注「图内英文标题」在 180 mm 版已删除
    cur = must_replace(
        cur, '<th style="padding:6px 8px">图内英文标题</th>',
        '<th style="padding:6px 8px">图内英文标题<br><small>（v9 有 · 180 mm 版已删）</small></th>',
        "逐面板表头")
    cur = must_replace(
        cur,
        '<summary>展开逐面板说明与来源（F3_P08 v9 · 18 格 A–T；P / S 已删）</summary>',
        '<summary>展开逐面板说明与来源（F3_P08 180 mm · 18 格 A–T；P / S 已删）</summary>',
        "逐面板 details summary")
    cur = must_replace(
        cur,
        'v9 机器可读映射见 <code>26_F3_P08_v9_20261106/outputs/F3_P08_面板映射_v9.csv</code> 与 '
        '<code>26_F3_P08_v9_20261106/outputs/F3_P08_meta_v9.json</code>；跨图谱统一状态字典见 '
        '<code>26_F3_P08_v9_20261106/F3_P08_状态统一表_v9.csv</code>。',
        f'180 mm 版机器可读映射见 <code>{RES_DIR}/{stem}_面板映射.csv</code> 与 '
        f'<code>{RES_DIR}/{stem}_meta.json</code>；跨图谱统一状态字典仍见 '
        '<code>26_F3_P08_v9_20261106/F3_P08_状态统一表_v9.csv</code>（沿用未改）。',
        "逐面板表尾 · 映射路径")

    # 3) 版式验收 details 整块重写（旧块的 320 mm / 7559 px / 600decbf / 8 Image XObject
    #    全是 v9 的数值，留着会与 180 mm 主图自相矛盾）
    ds = cur.find('<summary>展开版式、验收与必须保留的证据边界（v9）</summary>')
    if ds < 0:
        raise SystemExit("[FAIL] 找不到版式验收 details")
    d0 = cur.rfind('<details', 0, ds)
    d1 = cur.find('</details>', ds) + len('</details>')
    new_details = f'''<details style="margin:12px 0"><summary>展开版式、验收与必须保留的证据边界（180 mm 期刊版）</summary>
<p><b>版式与验收。</b>4 行 / 18 面板，行结构 5 / 3 / 5 / 5；<b>{v["w_mm"]:.1f} × {v["h_mm"]:.1f} mm</b> · {v["px"][0]} × {v["px"][1]} px @ 600 dpi · <code>check_layout: 0 problems</code> · 全图文字两两碰撞审计 0 命中 · 六个状态排序面板共用同一套 10 行主网格 · 裁剪面板 0 / 18 · PNG md5 <code>{v["md5"].lower()}</code>。四边墨迹留白左 3.17 / 右 1.61 / 上 2.84 / 下 2.62 mm（右侧 1.6 mm 是 M 面板图内统计注记 <code>ρ = 0.456 / P = 0.01462 (n = 28)</code> 单行外伸，历代版本都有）。PDF 为 {v["pdf_bytes"]:,} bytes：坐标轴、文字、色点列、轮廓及其余 14 格均为矢量，只有四个高密度 UMAP 点云按脚本 <code>rasterized=True</code> 栅格化以控制体积（无 Type3 字体）——<b>因此本版 PDF 不宜称为「全矢量」</b>。复现：进 <code>{RES_DIR}/32_复现包/</code> 跑 <code>python build_180mm_paneltext.py</code>，一次重出 P / Q 两版，PNG 逐字节一致（PDF 因 /CreationDate 时间戳会变）。E ρ = 0.7619 / P = 0.0280 / n = 8、M ρ = 0.4565 / P = 0.0146 / n = 28 与 v9 完全一致。</p>
<p><b>本版相对 v9 的显示层改动。</b>① UMAP 不再开 22 mm 右侧图例栏，改在相邻 CORE20 箱线图左缘画 2.4 mm 色点列，ylim 直接取箱线轴、逐行与箱体同一 y 网格；四个图谱里 UMAP 图例状态集与相邻箱线图状态集完全相等（G1 10=10、G2 9=9、M2 10=10、L2 9=9，仅顺序相反），所以共享在语义上是严格的。② UMAP 绘图区宽 = 行高 × 该图谱实测宽高比（G1 0.822 / G2 0.826 / M2 1.160 / L2 1.112），A / I 框 33.0 → 27.1 mm，框内空白 8.1 → 0.1 mm；<code>ax.margins(0.006)</code> 消掉默认 5% 坐标边距。③ 外页边 6.0 → 3.2 mm、面板间距 3.0 → 2.6 mm，页眉页脚 x 统一到同一条 3.2 mm 边线。④ <code>J.tag()</code> 传空 title / note，删掉 18 个面板共 36 行句式标题与灰色副注，只留字母；<code>gap_mm</code> 1.5 → 4.1，四行行顶同步上移，画布高 268.0 → {v["h_mm"]:.1f} mm。<b>数据、统计量、颜色、状态名、点坐标一律未动。</b></p>
<p><b>必须保留的证据边界。</b>① 这是 180 mm 期刊宽度版，<b>不是</b>把 320 mm 工作稿整体缩放：面板宽度重新分配、UMAP 框贴合数据宽高比、状态注释合并成一列，字号未跌破 5.6 pt；但拆并版式改变了面板间的相对比例，做跨版本像素级对比时须注意。② G1 / G2 的 CORE20 是基因级 z、M2 / L2 是 log-normalized，跨行绝对值不可比。③ v7 的 UMAP 虚线是<b>描述性的密度边缘标注</b>，不是置信区间、不是聚类边界；「圈内纯度」不是分类精度。④ v8 的名称 / 配色统一只作用于<b>显示层</b>：没有合并细胞、没有重聚类；滑膜与半月板 / 韧带是独立注释的两套图谱，<b>跨图同色不代表状态等价</b>。⑤ v9 的行序倒转只是<b>排版改动</b>，NR-FB core 排第一不代表效应最强。⑥ g1_pos 在发现集 G1 上按 r &gt; 0 挑选，无阈值、无显著性检验、无多重校正；C / K 与 G1 循环，删去 P / S 后仍不构成独立验证。⑦ 删掉子图标题只是显示层改动，<b>不新增证据</b>；本图与 F3_P01–P07 是同一批数据的不同视图，计数时不得重复计入。</p>
<p><b>Supports:</b> The NR-FB state is visible across four single-cell atlases, but no single gene set uniquely defines its neural programme. <b>Does not support:</b> CORE20 是 NR-FB 唯一有效的定义；PCDH9 因果驱动该程序；NR-FB 与神经纤维发生物理接触；g1_pos 变体构成独立验证；临床关联等同因果；十个状态是离散细胞类型；跨图同色即状态等价；NR-FB core 置顶即效应最强。本图不含空间或干预数据，也未新增分析。</p>
</details>'''
    cur = cur[:d0] + new_details + cur[d1:]

    # 4) 两处 legend-note
    cur = must_replace(
        cur,
        '画幅 320 × 250 mm（工作稿横版）· 600 dpi（7559 × 5905 px）· 四行 18 面板（A–T，缺 P / S）· '
        '18/18 面板原生重绘 · 裁剪面板 0/18 · 最小字号 5.6 pt · 主图 md5 前缀 <code>600decbf</code> · '
        '版式体检 0 条问题。',
        f'画幅 <b>{v["w_mm"]:.1f} × {v["h_mm"]:.1f} mm</b>（期刊 180 mm 宽度版）· 600 dpi'
        f'（{v["px"][0]} × {v["px"][1]} px）· 四行 18 面板（A–T，缺 P / S）· 18/18 面板原生重绘 · '
        '裁剪面板 0/18 · 全部子图标题已删，仅留面板字母 · UMAP / CORE20 共享一列状态注释 · '
        f'最小字号 5.6 pt · 主图 md5 前缀 <code>{v["md5"][:8].lower()}</code> · 版式体检 0 条问题。',
        "末尾 legend-note 画幅")
    cur = must_replace(
        cur,
        '上一版 F3_P08 v5 保留在 <code>23_Figure3_合并稿v5_20261106/</code>；更早已折叠归档于本节下方'
        '（9 面板投稿重排版 A–I 与 Figure 1 合并版），未删除。',
        '上一版 F3_P08 v9（320 × 250 mm）主图与整节说明已折叠归档于本节下方，'
        '更早已折叠归档的 9 面板投稿重排版 A–I、Figure 1 合并版与 F3_P08 v5 也都在，未删除。',
        "末尾 legend-note 归档说明")
    return cur


def patch_global(s: str, v: dict, variant: str) -> str:
    s = must_replace(
        s,
        '<title>NRFB · 图册与 PCDH9 实验合稿（11 图版 ＋ S4/S5）· Figure 3 v9 ＋ Figure 4 修订 12 面板 A–L · 2026-11-06</title>',
        '<title>NRFB · 图册与 PCDH9 实验合稿（11 图版 ＋ S4/S5）· Figure 3 180 mm 期刊版 ＋ Figure 4 修订 12 面板 A–L · 2026-11-07</title>',
        "title")
    s = must_replace(
        s,
        '仅 Figure 1 / 2 / 5-O 的分组色、Figure 5 图注文字，以及 Figure 6 柱形填充不透明度改动；'
        'Figure 3 / 4 / 7 未改动。',
        '配色统一时仅 Figure 1 / 2 / 5-O 的分组色、Figure 5 图注文字，以及 Figure 6 柱形填充不透明度改动；'
        '<b>2026-11-07 追加更新 Figure 3</b>：换成 180 mm 期刊宽度版（去掉全部子图标题，'
        'UMAP 与 CORE20 共享一列状态注释），Figure 4 / 7 仍与配色统一版一致、未改动。',
        "配色统一横幅")
    s = must_replace(
        s, '2026.11.06 · Figure 3 更新 v9<br>',
        '2026.11.06 · Figure 3 更新 v9<br>2026.11.07 · Figure 3 → 180 mm 期刊版<br>',
        "aside small")
    old_intro_end = 'Figure 4 的 12 面板 A–L 修订与全文其他章节未改动。</p>'
    new_intro = old_intro_end + (
        '<p class="intro"><b>2026-11-07 修订（Figure 3）</b>：本节主图由 <b>F3_P08 v9（320 × 250 mm 工作稿）'
        f'更新为 180 mm 期刊宽度版</b>（{v["desc"]}），画幅 <b>{v["w_mm"]:.1f} × {v["h_mm"]:.1f} mm</b>、'
        f'{v["px"][0]} × {v["px"][1]} px @ 600 dpi，主图 md5 <code>{v["md5"].lower()}</code>。'
        '四行十八面板 A–T、字母、面板取舍、数据源、统计口径与所有数值（Cliff\'s d、ρ、P、n）、'
        '配色、状态名、UMAP 点坐标一字未动，<b>只改显示层几何</b>：UMAP 与相邻 CORE20 箱线图共享一列'
        '状态注释、UMAP 框贴合数据宽高比、外页边与面板间距收紧、删掉全部子图标题与灰色副注'
        '（仅保留面板字母）。v9 及更早版本完整折叠归档于本节下方，可随时回滚；'
        '全文其他图版与其他章节未改动。</p>')
    s = must_replace(s, old_intro_end, new_intro, "intro 追加段")
    return s


def apply_figure6_final(out_b: bytes, f6_src: Path) -> bytes:
    """Figure 3 补丁之后，追加 Figure 6 定稿（第 38 张内嵌图 + 3 处文案）。

    操作的是 bytes，不改其余任何一个字节；所有替换都带「命中恰好 1 次」门禁，
    输入不是预期的中间态就直接失败，不会悄悄产出半新半旧的合稿。
    """
    png = f6_src / F6_PNG
    if not png.is_file():
        raise SystemExit(f"[FAIL] 缺少 Figure 6 定稿 PNG: {png}")
    raw = png.read_bytes()
    got = hashlib.md5(raw).hexdigest().upper()
    if got != F6_PNG_MD5:
        raise SystemExit(f"[FAIL] Figure 6 定稿 PNG md5 不符: {got}（预期 {F6_PNG_MD5}）")

    ms = list(ASSET_PAT.finditer(out_b))
    if len(ms) != N_ASSETS:
        raise SystemExit(f"[FAIL] 内嵌资源数应为 {N_ASSETS}，实际 {len(ms)}")
    m = ms[F6_ASSET_INDEX]
    if m.group(1) != b"image/png":
        raise SystemExit(f"[FAIL] 第 {F6_ASSET_INDEX + 1} 张不是 PNG: {m.group(1)!r}")
    old_b64 = re.sub(rb"\s+", b"", m.group(2))
    old_md5 = hashlib.md5(base64.b64decode(old_b64)).hexdigest()
    if old_md5 != F6_OLD_ASSET_MD5:
        raise SystemExit(f"[FAIL] 第 {F6_ASSET_INDEX + 1} 张不是预期的旧 Figure 6"
                         f"（md5 {old_md5}），拒绝替换")

    out_b = (out_b[:m.start()] + b"data:image/png;base64,"
             + base64.b64encode(raw) + out_b[m.end():])

    def rep(old: str, new: str, label: str) -> None:
        nonlocal out_b
        o, n = old.encode("utf-8"), new.encode("utf-8")
        c = out_b.count(o)
        if c != 1:
            raise SystemExit(f"[FAIL] F6 文案 {label}: 期望命中 1 次，实际 {c} 次")
        out_b = out_b.replace(o, n, 1)

    # 1) 横幅：版本行 + 回滚链接
    rep(
        '<strong>配色统一版 · 2026-11-06</strong><span style="color:#8C8C8C">（11-07 增补 Figure 6）</span>　'
        '配色统一时仅 Figure 1 / 2 / 5-O 的分组色、Figure 5 图注文字，以及 Figure 6 柱形填充不透明度改动；'
        '<b>2026-11-07 追加更新 Figure 3</b>：换成 180 mm 期刊宽度版（去掉全部子图标题，UMAP 与 CORE20 共享一列状态注释），'
        'Figure 4 / 7 仍与配色统一版一致、未改动。'
        '<a href="PCDH9_合稿_F3v9_F4_12panel_20261106.html" style="color:#B4482F;white-space:nowrap">← 返回原稿（可回滚）</a>',
        '<strong>配色统一版 · 2026-11-06</strong><span style="color:#8C8C8C">（11-08 定稿 Figure 6）</span>　'
        '配色统一时仅 Figure 1 / 2 / 5-O 的分组色与 Figure 5 图注文字；'
        '<b>2026-11-08 定稿更新 Figure 6</b>：整幅按 Figure 3 B 的「单一强调色」语法、由原始 CSV 原生重绘'
        '（砖红主角 + 低饱和配角，180 × 158 mm · 600 dpi），替换掉此前的 α 0.45 调色版本；'
        '<b>2026-11-07 追加更新 Figure 3</b>：换成 180 mm 期刊宽度版（去掉全部子图标题，UMAP 与 CORE20 共享一列状态注释），'
        'Figure 4 / 7 仍与配色统一版一致、未改动。'
        '<a href="PCDH9_合稿_配色统一_20261106.html" style="color:#B4482F;white-space:nowrap">← 返回替换前版本（可回滚）</a>',
        "横幅版本行 + 回滚链接",
    )
    # 2) 侧栏版本沿革
    rep(
        '2026.11.07 · Figure 3 → 180 mm 期刊版<br>',
        '2026.11.07 · Figure 3 → 180 mm 期刊版<br>2026.11.08 · Figure 6 → F3 配色定稿重绘<br>',
        "侧栏版本沿革",
    )
    # 3) Figure 6 图前来源说明
    rep(
        '<!--F9_DROP_V4NOTE_20261104--><div class="pcdh9x"><figure class="ovfig">',
        '<!--F9_DROP_V4NOTE_20261104-->'
        '<p class="muted">2026-11-08 更新：当前图版为整幅原生重绘（180 × 158 mm · 600 dpi），'
        '数据取自 <code>plot_data/*.csv</code>，配色沿用 Figure 3 B 的单一强调色语法；'
        'A–H 八个面板的数据、统计量、显著性标注与面板对应关系均未改。</p>'
        '<div class="pcdh9x"><figure class="ovfig">',
        "Figure 6 来源说明",
    )

    # 出口断言：66 张资源仍是 66 张，且第 38 张确实等于定稿 PNG
    ms2 = list(ASSET_PAT.finditer(out_b))
    assert len(ms2) == N_ASSETS, "F6 补丁后内嵌资源数变化"
    assert base64.b64decode(re.sub(rb"\s+", b"", ms2[F6_ASSET_INDEX].group(2))) == raw, \
        "F6 补丁后第 38 张不是定稿 PNG"
    return out_b


def resolve(args):
    if args.work_mode:
        base = Path(__file__).resolve().parent
        g = base / "合稿"
        return (args.html or g / CANONICAL_HTML,
                args.backup or g / "PCDH9_合稿_配色统一_20261106_原稿.html",
                args.src or g / RES_DIR,
                args.meta or base / "_Figure3当前版本.json",
                args.f6_src or g / F6_DIR)
    return (args.html or PROJ / "delivery" / CANONICAL_HTML,
            args.backup or PROJ / "delivery/_原稿备份_20261107/PCDH9_合稿_配色统一_20261106_原稿.html",
            args.src or PROJ / "width_variants/v180pt_delivery/figures",
            args.meta or PROJ / "width_variants/build/_合稿更新记录.json",
            args.f6_src or PROJ.parent / "fig6_redraw_20261107" / "out_f3")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=("P", "Q"), default="P")
    ap.add_argument("--restore", action="store_true",
                    help="导出一份 11-06 原稿到 合稿/PCDH9_合稿_还原_11-06原稿.html（不覆盖主文件）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--work-mode", action="store_true", help="路径相对脚本所在目录（拷走也能跑）")
    ap.add_argument("--html", type=Path)
    ap.add_argument("--backup", type=Path)
    ap.add_argument("--src", type=Path)
    ap.add_argument("--meta", type=Path)
    ap.add_argument("--f6-src", type=Path,
                    help=f"Figure 6 定稿资源目录（含 {F6_PNG}；默认 合稿/{F6_DIR}/）")
    args = ap.parse_args()

    html, backup, src, meta, f6_src = resolve(args)
    if args.restore:
        if not backup.exists():
            raise SystemExit(f"[FAIL] 备份不存在 {backup}")
        dst = html.parent / "PCDH9_合稿_还原_11-06原稿.html"
        shutil.copy2(backup, dst)
        print(f"已导出 11-06 原稿：{dst}  md5={md5(dst)}")
        print(f"当前主文件 {html.name} 未被覆盖；重跑 --variant P 可一键重建 F6 定稿版。")
        return

    if not backup.exists():
        raise SystemExit(f"[FAIL] 缺少字节级原稿备份 {backup}（请先备份 11-06 原稿）")
    assert md5(backup) == ORIGINAL_MD5, f"原稿备份 md5 异常: {md5(backup)}"

    # 始终从原稿读，保证幂等
    original = backup.read_text(encoding="utf-8")
    orig_bytes = backup.stat().st_size
    v = VARIANTS[args.variant]
    a = original.find('<section id="f3">')
    cur0 = a + len('<section id="f3">')
    arch = original.find('<details class="f3-archive"', cur0)
    if a < 0 or arch < 0:
        raise SystemExit("[FAIL] 找不到 f3 section / 第一个归档区")

    head = original[:cur0]
    cur = original[cur0:arch]
    tail = original[arch:]
    out = patch_global(head + patch_current_region(cur, v, args.variant, src) + tail,
                       v, args.variant)

    # 结构断言：其余 3 张内嵌图与三个历史归档区都还在
    assert out.count('data:image/png;base64,') == original.count('data:image/png;base64,'), "内嵌图数量变化"
    for key in ('data-figure="f3-p08-v5"', 'data-figure="f3-submission"', 'data-figure="f3-merged"'):
        assert key in out, f"归档图丢失 {key}"
    assert '600decbf561c2780715a2e84d868085d' in out, "v9 md5 归档说明被误删"
    assert '历史版本归档' in out, "归档区被误删"
    assert out.count('<section id="f3">') == 1
    assert base64.b64encode((src / f'{v["stem"]}.png').read_bytes()).decode() in out, "内嵌图未替换"

    # ---- Figure 6 定稿补丁（在 Figure 3 结构断言全部通过之后） -------------
    out_b = out.encode("utf-8")
    out_b = apply_figure6_final(out_b, f6_src)

    if args.dry_run:
        print(f"dry-run OK  {args.variant}  {orig_bytes:,} -> {len(out_b):,} bytes"
              f"  md5={hashlib.md5(out_b).hexdigest()}")
        return
    html.parent.mkdir(parents=True, exist_ok=True)
    html.write_bytes(out_b)
    rec = dict(variant=args.variant, html=str(html), html_md5=md5(html),
               html_bytes=html.stat().st_size, original_md5=ORIGINAL_MD5,
               original_bytes=backup.stat().st_size, embedded_png_md5=v["md5"],
               f6_png_md5=F6_PNG_MD5, f6_asset_index=F6_ASSET_INDEX + 1,
               canonical=True,
               note="工作模式：python3 切换Figure3版本.py --work-mode --variant Q"
                    "（P/Q 切换均保留 Figure 6 定稿）")
    meta.parent.mkdir(parents=True, exist_ok=True)
    meta.write_text(json.dumps(rec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已更新 {html}")
    print(f"  variant={args.variant}  {v['w_mm']}×{v['h_mm']} mm  F3 内嵌 PNG md5={v['md5']}")
    print(f"  Figure 6 定稿已嵌入第 {F6_ASSET_INDEX + 1} 张  PNG md5={F6_PNG_MD5.lower()}")
    print(f"  {orig_bytes:,} -> {len(out_b):,} bytes  新 HTML md5={md5(html)}")


if __name__ == "__main__":
    main()
