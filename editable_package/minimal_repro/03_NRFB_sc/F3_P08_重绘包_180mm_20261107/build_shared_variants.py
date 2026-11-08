"""F3_P08 v9 · 共享注释 + 按内容分配宽度（2026-11-07 第三轮）。

用户反馈（原话）：
  "其实还可以更窄一点，特别是 D E H M C 和 K 图，然后 A I N Q 的注释和右侧的
   条形图中还有很大的空白，你这样，把 Q 图和 O 图的位置换一下，然后他们共享
   一个注释"

诊断（本轮重新核对数据，见对话记录）：
  * 四个图谱的 UMAP 图例状态集与紧随其后的箱线图状态集**完全一致**，只是顺序
    相反（图例 UNIFIED_ORDER，箱线图 BOX_ORDER = 逆序）：
        G1 10 = 10 · G2 9 = 9 · M2 10 = 10 · L2 9 = 9
  * 但 Q(韧带 L2, 9 状态) 与 O(半月板 M2, 10 状态) 不是同一图谱，直接共用会把
    NR-FB grad. / Sublining / Proliferating 三个状态标错 —— 用户已确认改用
    "配对共享"（方案 A）：顺序仍是 N O Q R T，每张 UMAP 与**它自己**的箱线图
    共用一列注释。
  * 于是 A/I/N/Q 右侧 17–22 mm 的图例栏可以整块取消，改为 2.4 mm 色点列，
    贴在对应箱线图面板左缘、与箱体同一 y 网格。每对省 14–18 mm。

本轮四项改动（只动显示层几何，不动数据 / 数值 / 配色 / 状态名）：
  A. 共享注释：UMAP 不再有独立图例轴；箱线图面板左缘加 2.4 mm 色点列，
     点与箱体逐行对齐（同 ylim / 同 yticks）。一列注释同时充当 UMAP 图例与
     箱线图 y 轴标签。
  B. 宽度按内容分配：UMAP 固定 36 mm 正方形（避免 aspect=equal 的
     datalim 拉伸造成框内空白），其余面板按权重分剩余宽度。
     D / E / H / M / C / K 的权重最低，因此最窄。
  C. GAP 1.0 / 0.8 mm，RIGHT_PAD 1.2，LPAD 用上一轮实测的最小值。
  D. 六个排序面板继续共用 10 行主网格（B/C/J/K/O/R 横线跨行重合）。

仍以 `build_F3_P08_portable.py` 为唯一真源：只做精确字符串补丁，一遍数据
加载 / 一遍 KDE 等值线计算下循环渲染。

运行（在本文件所在目录）：
    python build_shared_variants.py                 # 600 dpi 正式出图
    python build_shared_variants.py --smoke         # 100 dpi 本地自检
    python build_shared_variants.py --only=S2       # 只出一个版本
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE / "build_F3_P08_portable.py"
OUT_ROOT = HERE / "outputs" / "shared_variants"
SMOKE = "--smoke" in sys.argv

# ---------------------------------------------------------------- 版本表
# 宽度阶梯：UMAP 保持正方形，整体靠"其余面板按内容分宽"来压窄。
SHARED = [
    ("S1", 210, 1.0, 33.0, "偏保守：D/E/H/M/C/K 已比上一轮窄 40% 以上"),
    ("S2", 200, 1.0, 33.0, "推荐：整体再窄 10 mm，UMAP 仍 33 mm 正方形"),
    ("S3", 190, 0.8, 33.0, "最窄：T 触底 18.5 mm，UMAP 自动缩到约 31 mm"),
]


def variants():
    out = []
    for name, pw, gap, uw, desc in SHARED:
        out.append(dict(
            name=name, pw=float(pw), gap=float(gap), umap_w=float(uw),
            ph=257.0 + max(0, math.ceil((320.0 - pw) / 8.0)),
            desc=desc,
        ))
    return out


CONFIGS = variants()
_only = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")), None)
if _only:
    CONFIGS = [c for c in CONFIGS if c["name"] == _only]
    assert CONFIGS, f"unknown variant {_only}"

# ---------------------------------------------------------------- 精确补丁
SUBTITLE = (
    "F3_P08 v9 shared {name} - {pw} x {ph} mm - "
    "one state column per UMAP + CORE20 pair - "
    "18 panels, re-drawn from source tables"
)

LPAD_OLD = '''LPAD = {
    "umap": (5.0, 3.0), "core20": (21.0, 17.0), "g1pos": (21.0, 16.0),
    "dot": (22.0, 22.0), "pcdh9": (14.0, 14.0), "corepc": (9.0, 9.0),
    "pctgrp": (13.0, 13.0), "pctoa": (13.0, 13.0), "fit": (15.0, 15.0),
    "tissue": (13.0, 13.0),
}'''

LPAD_NEW = '''# 共享注释版：y 轴文字用上一轮 renderer 实测的最小需求 + 0.8~1.2 mm 余量。
# 实测需求(mm)：core20/g1pos 15.10(第4行 12.88)、dot 19.67、tissue 8.43、
# pcdh9 7.17、corepc 7.15、fit/pctgrp/pctoa 5.98、umap 2.21。
LPAD = {
    "umap": (3.0, 3.0), "core20": (16.0, 14.0), "g1pos": (16.0, 14.0),
    "dot": (20.5, 20.5), "pcdh9": (8.0, 8.0), "corepc": (8.0, 8.0),
    "pctgrp": (7.0, 7.0), "pctoa": (7.0, 7.0), "fit": (7.0, 7.0),
    "tissue": (9.5, 9.5),
}'''

# 共享注释的几何常量 + 每行宽度权重。
# UMAP 固定正方形（aspect=equal + datalim，框比数据宽会在框内留白）；
# 其余面板按权重分剩余宽度 —— D/E/H/M/C/K 权重最低，所以最窄。
SHARE_GEOM = '''RIGHT_PAD = 1.2
DOT_W = 2.4          # 色点列宽（mm）
DOT_GAP = 1.2        # 色点列与 y 轴文字之间的间隙
PAIR_BOX = {"B", "J", "O", "R"}   # 紧跟 UMAP、接收共享注释的箱线图
SHARE_LEGEND = True

# 绘图区最小宽度（mm）：按实测文字 / 箱体需要定的下限，低于它就会挤压或标签相撞。
# tissue 18.5 来自实测 "meniscus"(8.14) + "ligament"(7.33) + 1.2 间隙 = 16.7，
# 再留 1.8 mm 余量；corepc 10 / pctgrp 12 是 2~3 组箱体的可读下限。
PLOT_MIN = {
    "umap": 28.0, "core20": 15.0, "g1pos": 16.0, "pctgrp": 12.0,
    "pctoa": 12.0, "fit": 12.0, "dot": 30.0, "pcdh9": 25.0,
    "corepc": 10.0, "tissue": 18.5,
}

UMAP_W = 33.0        # UMAP 绘图区目标宽度 = 行高（正方形，避免 aspect 留白）
# 保底之外多出来的宽度按权重分配 —— D / E / H / M / C / K 权重最低，所以最窄。
ROW_W = {
    0: {"B": 26.0, "C": 20.0, "D": 12.0, "E": 12.0},
    1: {"F": 40.0, "G": 28.0, "H": 4.0},
    2: {"J": 26.0, "K": 20.0, "L": 12.0, "M": 12.0},
    3: {"O": 20.0, "R": 20.0, "T": 20.0},
}'''

# 覆盖 figstyle_constants.box_h：只把每状态横线放到跨行主网格上；
# 箱体 / 中位线 / 须线 / 颜色 / 状态名逐字沿用原实现。
BOX_H_NEW = '''def box_h(ax, data, states, colors, width=0.62, show_labels=True):
    """共享 10 行主网格版。仅改变每状态横线的 y 位置，数值与画法不变。

    ALIGN_GRID=True 时，n 个状态占主网格最高的 n 行（顶端对齐），
    少于 10 个状态的面板在底部留空槽；因此 B/C/J/K/O/R 的横线
    在第 1/3/4 行完全重合。False 时与 v9 原版逐像素一致。
    """
    n = len(states)
    shift = (MASTER_N - n) if ALIGN_GRID else 0
    pos = np.arange(n)[::-1] + shift
    for p, s in zip(pos, states):
        v = data[s]
        v = v[np.isfinite(v)]
        q1, med, q3 = np.percentile(v, [25, 50, 75])
        lo, hi = np.percentile(v, [2, 98])
        ax.add_patch(Rectangle((q1, p - width / 2), q3 - q1, width,
                               facecolor=colors[s], edgecolor="none",
                               alpha=0.85 if s == NRFB else 0.55, zorder=2))
        ax.plot([med, med], [p - width / 2, p + width / 2], color="white",
                lw=1.1, zorder=3, solid_capstyle="butt")
        ax.plot([lo, hi], [p, p], color=colors[s], lw=0.7, zorder=1,
                alpha=0.8, solid_capstyle="butt")
    ax.set_yticks(pos)
    ax.set_yticklabels([SHORT.get(s, s) for s in states] if show_labels else [])
    ax.set_ylim(-0.7, (MASTER_N if ALIGN_GRID else n) - 0.3)
'''

HELPERS = '''
# ------------------------------------------------- 共享注释 + 几何自检
AX_REC = []
GEOM_REPORT = []


def add_state_dots(fig, ax, x_panel, ytop, h, states):
    """共享注释的色点列：贴在箱线图面板左缘，与箱体逐行同一 y 网格。

    这一列同时是左侧 UMAP 的图例和右侧箱线图的 y 轴标签 —— 只画一次。
    """
    dax = fig.add_axes([(x_panel + 0.5) / PW, (PH - ytop - h) / PH,
                        DOT_W / PW, h / PH])
    dax.set_xlim(0.0, 1.0)
    dax.set_ylim(*ax.get_ylim())
    dax.set_xticks([]); dax.set_yticks([])
    dax.set_axis_off()
    ticks = ax.get_yticks()
    assert len(ticks) == len(states), (len(ticks), len(states))
    for t, s in zip(ticks, states):
        dax.plot([0.5], [t], marker="o", ms=2.7, mec="none",
                 mfc=color_of(s), zorder=3)
    return dax


def text_audit(fig, tol_mm=0.25):
    """全图文字碰撞审计：fig.text + 每个轴的刻度文字 / 轴标题，两两求交。

    `J.check_layout` 只查字号、越界和 CJK 缺字，查不出"上一行的旋转刻度
    文字压到下一行标题"这类竖向碰撞；这里补上。返回重叠对列表。
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    mmpp = 25.4 / fig.dpi
    items = []

    def push(t, tag):
        s = (t.get_text() or "").strip()
        if not s:
            return
        bb = t.get_window_extent(renderer=r)
        rot = float(getattr(t, "get_rotation", lambda: 0)() or 0) % 180.0
        items.append((tag + ":" + s.replace("\\n", "/")[:26],
                      bb.x0 * mmpp, bb.y0 * mmpp, bb.x1 * mmpp, bb.y1 * mmpp,
                      rot))

    for t in fig.texts:
        push(t, "text")
    for k, ax in enumerate(fig.axes):
        for t in ax.get_xticklabels():
            push(t, f"ax{k}x")
        for t in ax.get_yticklabels():
            push(t, f"ax{k}y")
        if ax.xaxis.label.get_text():
            push(ax.xaxis.label, f"ax{k}xlab")
        if ax.yaxis.label.get_text():
            push(ax.yaxis.label, f"ax{k}ylab")
    bad = []
    for i in range(len(items)):
        a = items[i]
        for j in range(i + 1, len(items)):
            b = items[j]
            # 两个都是斜排标签（如 F 的 55° 基因名）时轴对齐包围盒必然相交，
            # 但字形本身不重叠 —— 跳过这类假阳性。
            if a[5] and b[5]:
                continue
            ox = min(a[3], b[3]) - max(a[1], b[1])
            oy = min(a[4], b[4]) - max(a[2], b[2])
            if ox > tol_mm and oy > tol_mm:
                bad.append((a[0], b[0], round(ox, 2), round(oy, 2)))
    return bad


def compact_geometry_check(fig):
    """导出后、关画布前：验证 y 轴文字没有越出本面板左边界，并记录横线位置。"""
    d0 = fig.dpi
    fig.set_dpi(300)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    mmpp = 25.4 / 300.0
    rep = []
    for d in AX_REC:
        ax = d["ax"]
        bb = ax.get_window_extent(renderer=r)
        lefts = [l.get_window_extent(renderer=r).x0
                 for l in ax.get_yticklabels() if l.get_text().strip()]
        if ax.yaxis.label.get_text().strip():
            lefts.append(ax.yaxis.label.get_window_extent(renderer=r).x0)
        need = (bb.x0 - min(lefts)) * mmpp if lefts else 0.0
        rec = dict(letter=d["letter"], kind=d["kind"],
                   need_mm=round(need, 2), lpad_mm=round(d["lpad"], 2),
                   slack_mm=round(d["lpad"] - need, 2),
                   x_mm=round(d["x"], 2), w_mm=round(d["w"], 2),
                   plot_mm=round(d["w"] - d["lpad"] - RIGHT_PAD, 2),
                   bottom_mm=round(PH - bb.y0 * mmpp, 2))
        if d["letter"] in "BCJKOR":
            rec["state_line_mm"] = [
                round((ax.transData.transform((ax.get_xlim()[0], t))[1]
                       - bb.y0) * mmpp, 2) for t in ax.get_yticks()]
        rep.append(rec)
    fig.set_dpi(d0)
    GEOM_REPORT.extend(rep)
    bad = [x for x in rep if x["slack_mm"] < 0.25]
    if bad:
        raise SystemExit("LPAD 不足，y 轴文字越出面板: " + repr(bad[:6]))
    bottoms = {}
    for x in rep:
        for row, letters in ((1, "ABCDE"), (3, "IJKLM"), (4, "NOQRT")):
            if x["letter"] in letters:
                bottoms.setdefault(row, []).append(x["bottom_mm"])
    for row, vals in bottoms.items():
        assert max(vals) - min(vals) < 0.02, (row, vals)
    # 六个排序面板必须共用同一组横线位置
    lines = [tuple(x["state_line_mm"]) for x in rep if "state_line_mm" in x]
    for t in lines:
        assert len(t) in (9, 10), t
    tops = {t[0] for t in lines}
    assert len(tops) == 1, tops
    bad_txt = text_audit(fig)
    if bad_txt:
        raise SystemExit("文字碰撞: " + repr(bad_txt[:8]))
    return rep

'''

PATCHES: list[tuple[str, str, int]] = [
    # 1) KDE 等值线只算一次（与几何无关）
    ("OUTLINE_STATS = {}\nELLIPSE_V5_STATS = {}",
     "OUTLINE_STATS = {}\nELLIPSE_V5_STATS = {}\n_EDGE_CACHE = {}", 1),
    ("""    p = u[m]
    xy, info = kde_edge_contour(p, u, m)
    OUTLINE_STATS[key] = info
    ELLIPSE_V5_STATS[key] = ellipse_v5_stats(p, u, m)""",
     """    p = u[m]
    if key not in _EDGE_CACHE:
        _EDGE_CACHE[key] = (kde_edge_contour(p, u, m),
                            ellipse_v5_stats(p, u, m))
    (xy, info), _ell = _EDGE_CACHE[key]
    OUTLINE_STATS[key] = info
    ELLIPSE_V5_STATS[key] = _ell""", 1),
    # 2) 收紧内边距 + 共享注释几何常量
    (LPAD_OLD, LPAD_NEW, 1),
    # 2b) 行高 36 -> 33、行距 50 -> 53：窄面板标题会折成两行，标题块约
    #     11.5 mm + 下方 x 轴文字约 6.5 mm，需要 20 mm 竖向空隙才不撞上一行。
    ("ROW_H = 36.0", "ROW_H = 33.0", 1),
    ("ROW_TOP = [26.0, 76.0, 136.0, 186.0]",
     "ROW_TOP = [26.0, 79.0, 138.0, 191.0]", 1),
    ("RIGHT_PAD = 2.0", SHARE_GEOM, 1),
    # 3) 共享主网格：替换 box_h 绑定 + g1pos 的 y 位置
    ("box_h = F.box_h\n", BOX_H_NEW, 1),
    ("    yy = np.arange(len(states))[::-1]\n",
     "    yy = np.arange(len(states))[::-1] + "
     "((MASTER_N - len(states)) if ALIGN_GRID else 0)\n", 1),
    ("    ax.set_ylim(-0.7, len(states) - 0.3)\n",
     "    ax.set_ylim(-0.7, (MASTER_N if ALIGN_GRID else len(states)) - 0.3)\n", 1),
    # 4) UMAP 不再画独立图例；没有图例轴时也不要画框内兜底图例
    ("    else:  # 兜底：没有独立图例轴时仍画在绘图轴内下方",
     "    elif not SHARE_LEGEND:  # 兜底：没有独立图例轴时仍画在绘图轴内下方", 1),
    # 5) 页脚排版
    ("J.footer(fig, FOOTER, size=5.8, linespacing=1.35)",
     "J.footer(fig, FOOTER, size=5.6, linespacing=1.20)", 1),
    # 6) 导出 DPI / meta 名称
    ('fig.savefig(OUT_PNG, dpi=600, facecolor="white")',
     'fig.savefig(OUT_PNG, dpi=VARIANT_DPI, facecolor="white")', 1),
    ('        id="F3_P08", version="v9", stem="F3_P08_four_rows_A-T_v9",\n'
     '        png="outputs/F3_P08_four_rows_A-T_v9.png",\n'
     '        pdf="outputs/F3_P08_four_rows_A-T_v9.pdf",\n'
     '        width_mm=PW, height_mm=PH, dpi=600,',
     '        id="F3_P08", version="v9-shared-" + VARIANT_CFG["name"],\n'
     '        stem=OUT_PNG.stem, png=OUT_PNG.name, pdf=OUT_PDF.name,\n'
     '        compact_variant=dict(VARIANT_CFG),\n'
     '        width_mm=PW, height_mm=PH, dpi=VARIANT_DPI,', 1),
    ('        umap_legend="single column in a 22 mm right-side gutter for A, I, N and Q",',
     '        umap_legend="removed: each UMAP shares one state column (2.4 mm dots + '
     'the CORE20 box y labels) with its own box panel in B, J, O and R",\n'
     '        shared_annotation=dict(pairs=[["A", "B"], ["I", "J"], ["N", "O"], '
     '["Q", "R"]],\n'
     '                               note="one column serves the UMAP legend and the '
     'adjacent box y labels; same state set, BOX_ORDER",\n'
     '                               dot_column_mm=2.4),', 1),
    # 7) 窄面板灰色副注短式（数值不变）
    ("""            note = (f"2nd = {display_name(second)}; Cliff's d = {d:.2f}"
                    if not narrow else f"Cliff's d = {d:.2f}")""",
     """            note = (f"2nd = {display_name(second)}; Cliff's d = {d:.2f}"
                    if not narrow and w >= 48.0 else f"Cliff's d = {d:.2f}")""", 1),
    ("""            note = (f"rank {gd['rank']} of {nstate}; {TISSUE_NOTE[arg]}"
                    if not narrow else f"rank {gd['rank']}/{nstate}")""",
     """            note = (f"rank {gd['rank']} of {nstate}; {TISSUE_NOTE[arg]}"
                    if not narrow and w >= 48.0 else f"rank {gd['rank']}/{nstate}")""", 1),
    ('            note = f"{arg}; {n} donors with PPSD score"',
     '            note = (f"{arg}; {n} donors with PPSD score" if w >= 48.0\n'
     '                    else f"{arg}; n = {n}")', 1),
    ('            note = "2 control / 5 OA donors"',
     '            note = ("2 control / 5 OA donors" if w >= 48.0\n'
     '                    else "2 Ctrl / 5 OA")', 1),
    ('            note = f"{n_men} meniscus / {n_lig} ligament samples"',
     '            note = (f"{n_men} meniscus / {n_lig} ligament samples" if w >= 48.0\n'
     '                    else f"{n_men} / {n_lig} samples")', 1),
    # 8) UMAP 绘图区不再让出图例栏
    ("""        is_umap = kind == "umap"
        leg_ax = None
        if is_umap:
            # 绘图区右侧让出 LEG_W 作为竖排图例栏（含 1 mm 间隔）
            leg_ax = add_ax(fig, x + w - RIGHT_PAD - LEG_W + LEG_GAP,
                            ytop, LEG_W - LEG_GAP, h=plot_h)
            leg_ax.set_xticks([]); leg_ax.set_yticks([])
            leg_ax.set_axis_off()
        ax = add_ax(fig, x + lpad, ytop,
                    w - lpad - RIGHT_PAD - (LEG_W if is_umap else 0.0),
                    h=plot_h)""",
     """        is_umap = kind == "umap"
        leg_ax = None
        if is_umap and not SHARE_LEGEND:
            leg_ax = add_ax(fig, x + w - RIGHT_PAD - LEG_W + LEG_GAP,
                            ytop, LEG_W - LEG_GAP, h=plot_h)
            leg_ax.set_xticks([]); leg_ax.set_yticks([])
            leg_ax.set_axis_off()
        # 共享注释：UMAP 绘图区吃掉整格宽度（没有图例栏）
        ax = add_ax(fig, x + lpad, ytop,
                    w - lpad - RIGHT_PAD
                    - (LEG_W if (is_umap and not SHARE_LEGEND) else 0.0),
                    h=plot_h)""", 1),
    # 9) 共享注释的箱线图为色点列预留宽度
    ("        lpad = LPAD[kind][1 if narrow else 0]",
     "        lpad = LPAD[kind][1 if narrow else 0] + "
     "(DOT_W + DOT_GAP if letter in PAIR_BOX else 0.0)", 1),
    # 10) 记录每个轴 + 画色点列 + 导出后几何自检
    ("        clip_xticks(ax)\n",
     '        AX_REC.append(dict(letter=letter, kind=kind, ax=ax,\n'
     '                           x=x, w=w, lpad=lpad, ytop=ytop,\n'
     '                           plot_h=plot_h))\n'
     '        if SHARE_LEGEND and letter in PAIR_BOX:\n'
     '            add_state_dots(fig, ax, x, ytop, plot_h,\n'
     '                           [s for s in BOX_ORDER\n'
     '                            if s in set(obs(arg)["state"])])\n'
     '        clip_xticks(ax)\n', 1),
    ("    fig.savefig(OUT_PDF, facecolor=\"white\")\n    plt.close(fig)",
     "    fig.savefig(OUT_PDF, facecolor=\"white\")\n"
     "    compact_geometry_check(fig)\n    plt.close(fig)", 1),
]


def patched_source() -> str:
    s = BASE.read_text(encoding="utf-8")
    for old, new, n in PATCHES:
        cnt = s.count(old)
        assert cnt == n, f"patch mismatch ({cnt} != {n}): {old[:76]!r}"
        s = s.replace(old, new)

    # 模块级助手（共享注释 / 几何自检）插到 main() 之前
    marker = "\ndef main():\n"
    assert s.count(marker) == 1
    s = s.replace(marker, "\n" + HELPERS + "\ndef main():\n", 1)

    # positions() 整段替换：UMAP 固定正方形，其余按权重分剩余宽度
    pat = re.compile(r"def positions\(\):.*?\n    return out\n", re.S)
    assert len(pat.findall(s)) == 1
    s = pat.sub(lambda m: '''def positions():
    """共享注释版逐行分配：先保底，再按权重加宽。

    每格宽度 = 标签块 + 绘图区。标签块 = LPAD（含色点列）+ RIGHT_PAD。
    绘图区里每个非 UMAP 面板先拿 PLOT_MIN 保底，UMAP 取
    min(UMAP_W, 剩余 / UMAP 数)，剩下的按 ROW_W 权重加给非 UMAP 面板 ——
    权重最低的 D / E / H / M / C / K 因此最窄。
    """
    cfg = VARIANT_CFG
    gap = cfg["gap"]
    CW = PW - 2 * MG
    rows = [list("ABCDE"), list("FGH"), list("IJKLM"), list("NOQRT")]
    kinds = {L: k for L, _r, _s, _sp, _t, k, _a in PANEL_MAP}
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
        uw = min(cfg["umap_w"], left / len(umaps)) if umaps else 0.0
        if umaps:
            assert uw >= PLOT_MIN["umap"], (cfg["name"], ri, round(uw, 2))
            left -= uw * len(umaps)
        tot = sum(ROW_W[ri][L] for L in var)
        plot = {L: base[L] + left * ROW_W[ri][L] / tot for L in var}
        for L in umaps:
            plot[L] = uw
        x = MG
        for L in letters:
            out[L] = (x, ytop, plot[L] + lab[L])
            x += plot[L] + lab[L] + gap
        assert abs((x - gap) - (MG + CW)) < 1e-6, (cfg["name"], ri, x)
    return out
''', s, count=1)
    return s


def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    src = patched_source()
    (HERE / "_patched_shared_preview.py").write_text(src, encoding="utf-8")

    ns = {"__name__": "_f3_shared_mod", "__file__": str(BASE),
          "MASTER_N": 10, "ALIGN_GRID": True, "SHARE_LEGEND": True,
          "UMAP_W": 33.0}
    exec(compile(src, str(BASE), "exec"), ns)

    ns["VARIANT_DPI"] = 100 if SMOKE else 600
    (HERE / "outputs").mkdir(parents=True, exist_ok=True)
    ns["OUT_STATES"] = OUT_ROOT / "_shared" / "F3_P08_状态统一表_v9.csv"
    ns["OUT_STATES"].parent.mkdir(parents=True, exist_ok=True)

    rows, summary, geom_all = [], [], {}
    for cfg in CONFIGS:
        print(f"\n=== {cfg['name']}  PW={cfg['pw']}  PH={cfg['ph']}  "
              f"GAP={cfg['gap']}  UMAP_W={cfg['umap_w']} ===", flush=True)
        ns["VARIANT_CFG"] = cfg
        ns["PW"] = cfg["pw"]
        ns["PH"] = cfg["ph"]
        ns["ALIGN_GRID"] = True
        ns["MASTER_N"] = 10
        ns["SHARE_LEGEND"] = True
        ns["UMAP_W"] = cfg["umap_w"]
        ns["AX_REC"] = []
        ns["GEOM_REPORT"] = []
        ns["HEADER"] = (
            "Figure 3 · F3_P08",
            "The NR-FB state across four single-cell atlases, and what defines it",
            SUBTITLE.format(name=cfg["name"], pw=int(cfg["pw"]),
                            ph=int(cfg["ph"]), uw=int(cfg["umap_w"])),
        )
        stem = f"F3_P08_shared_{cfg['name']}_{int(cfg['pw'])}mm"
        ns["OUT_PNG"] = OUT_ROOT / f"{stem}.png"
        ns["OUT_PDF"] = OUT_ROOT / f"{stem}.pdf"
        ns["OUT_MAP"] = OUT_ROOT / f"{stem}_面板映射.csv"
        ns["OUT_META"] = OUT_ROOT / f"{stem}_meta.json"

        pos = ns["positions"]()
        for L in sorted(pos):
            rows.append(dict(variant=cfg["name"], panel=L,
                             x_mm=round(pos[L][0], 2),
                             w_mm=round(pos[L][2], 2)))

        try:
            ns["main"]()
        except SystemExit as e:
            print(f"  !! {cfg['name']} FAILED: {e}", flush=True)
            summary.append(dict(**cfg, status=f"failed: {e}"))
            continue

        png = ns["OUT_PNG"]
        if not png.exists():
            summary.append(dict(**cfg, status="no_png"))
            continue
        from PIL import Image
        with Image.open(png) as im:
            px = im.size
        geom_all[cfg["name"]] = list(ns["GEOM_REPORT"])
        rec = dict(**cfg, status="ok", stem=stem,
                   png_bytes=png.stat().st_size,
                   png_md5=hashlib.md5(png.read_bytes()).hexdigest().upper(),
                   pdf_bytes=ns["OUT_PDF"].stat().st_size,
                   width_px=px[0], height_px=px[1],
                   widths={L: round(v[2], 2) for L, v in pos.items()},
                   plot={r["letter"]: r["plot_mm"] for r in ns["GEOM_REPORT"]})
        summary.append(rec)
        print(f"  OK {stem}  {px[0]}x{px[1]} px  md5={rec['png_md5']}", flush=True)

    with (OUT_ROOT / "面板宽度对照_共享注释版.csv").open(
            "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["variant", "panel", "x_mm", "w_mm"])
        w.writeheader(); w.writerows(rows)
    (OUT_ROOT / "shared_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_ROOT / "geometry_report.json").write_text(
        json.dumps(geom_all, ensure_ascii=False, indent=2), encoding="utf-8")
    ok = sum(1 for r in summary if r["status"] == "ok")
    print(f"\n=== DONE: {ok}/{len(CONFIGS)} shared variants ===")


if __name__ == "__main__":
    main()
