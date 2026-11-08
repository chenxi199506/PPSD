# -*- coding: utf-8 -*-
"""nc_style.py — Figure 1 / Figure 2 共用的 NC 版面与配色常量。

两图必须逐字同源：改这里，两张图一起变。任何一图单独改配色都会立刻
表现为"两张图不像一套"，这是本轮返工的直接原因。

设计约束
--------
* 三列网格 COL1/COL2/COL3 给出**绘图框**的左右边界（不是画布边界）。
  每一行的三个面板都严格落在这三条列上，所以上下面板的 y 轴天然对齐。
  面板外的 y 轴标签、刻度数字必须自己挤进 (0, COL1[0]) 这段留白里，
  不能靠 add_axes 的 bbox 去撑 —— bbox 只是绘图框。
* 配色是红蓝双极：蓝族 = 结构相关 / 未加权后 / 低 PPSD，红族 = PPSD 相关 /
  高 PPSD，越深 = 模型越完整。灰族只作中性参照。
"""
from __future__ import annotations

# ------------------------------------------------------------------ 画布
W, H = 183.0, 170.0          # mm：NC 双栏满宽 / 单页最大高
DPI = 600

# ------------------------------------------------------------------ 字号（pt）
FS_LETTER = 8.0              # 面板字母：加粗小写
FS_TICK = 5.0
FS_AXIS = 5.2
FS_CELL = 5.0
FS_HDR = 5.0
FS_NOTE = 5.0

# ------------------------------------------------------------------ 线宽
LW_AXIS = 0.35
LW_TICK = 0.35
LW_RULE = 0.6                # 三线表的粗规则线
LW_RULE_THIN = 0.45
LW_CI = 0.8
LW_DASH = 0.5

# ------------------------------------------------------------------ 三列网格（绘图框边界，mm）
# 列间距 11 mm：刚好放得下旋转 y 轴标题(≈4 mm) + 刻度数字(≈4.5 mm) + pad。
# 间距 10 mm 时 Fig. 1 的 b/c 与 a/b 之间只剩 1 mm，视觉上会"粘住"。
COL1 = (24.0, 68.0)
COL2 = (79.0, 123.0)
COL3 = (134.0, 178.0)
COLS = (COL1, COL2, COL3)
COL_W = COL1[1] - COL1[0]    # 44.0
COL_MID = (COL2[0] + COL2[1]) / 2.0   # 101.0 —— 两面板拼幅时用这条接缝

# ------------------------------------------------------------------ 红蓝双极配色
BLUE = "#3B4992"             # 主蓝：结构域 / 加权后 / 低 PPSD
BLUE_LIGHT = "#8FA3CE"       # 浅蓝：单域模型
BLUE_MID = "#6E86B8"
BLUE_SOFT = "#B9C6E0"
BLUE_PALE = "#E2E8F4"

RED = "#D9251C"              # 主红：PPSD / 高 PPSD
RED_LIGHT = "#E4796E"
RED_DARK = "#B04A44"         # 砖红：Reference + PPSD
RED_PALE = "#FAE0DC"

DEEP = "#7E2333"             # 酒红：Full 叠加模型
GREY = "#9CA4AD"             # 中性：Reference 评分 / 加权前
GREY_SOFT = "#CBD5DC"
GRID_GREY = "#D6DCE1"

INK = "#213648"
MUTED = "#64707D"

# ------------------------------------------------------------------ 六个嵌套模型 → 颜色
# 蓝族 = 结构，红族 = PPSD，越深 = 越完整。两图共用同一张映射表。
MODEL_COLORS = {
    "Structure": BLUE_LIGHT,
    "Reference": GREY,
    "ReferenceStructure": BLUE,
    "PPSD": RED,
    "ReferencePPSD": RED_DARK,
    "Full": DEEP,
}
# Figure 2 母脚本里的模型名（带空格）
MODEL_COLORS_F2 = {
    "Structure": BLUE_LIGHT,
    "Reference score": GREY,
    "Reference + structure": BLUE,
    "PPSD": RED,
    "Reference + PPSD": RED_DARK,
    "Full": DEEP,
}


def rc():
    """两图共用的 rcParams。"""
    return {
        "font.family": "Arial",
        "font.size": FS_TICK,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "axes.linewidth": LW_AXIS,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.major.width": LW_TICK,
        "ytick.major.width": LW_TICK,
        "xtick.major.size": 1.4,
        "ytick.major.size": 1.4,
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    }


def panel_letter(fig, ax, s):
    """面板字母：贴绘图框左上角外沿 1.6 mm、上沿 0.7 mm。两图同一规则。

    左缘钳到 0：全宽面板（如 Fig. 1d 森林表从 x=0 起）减去 1.6 mm 会出画布。
    """
    bb = ax.get_position()
    fig.text(max(0.0, bb.x0 - 1.6 / W), bb.y1 + 0.7 / H, s, fontsize=FS_LETTER,
             fontweight="bold", color=INK, ha="left", va="baseline")


def strip_axes(ax, keep=("left", "bottom")):
    """统一去掉上/右（及按需去左）脊线。"""
    for side in ("left", "bottom", "top", "right"):
        if side not in keep:
            ax.spines[side].set_visible(False)


def approx_width_mm(text, fs):
    """粗估 Arial 字符串宽度（mm），用于判断标签能否塞进留白。

    经验值：平均字宽 ≈ 0.52 em，大写与数字略宽。只求量级正确，
    真值用 PDF 内容流复核。
    """
    return len(text) * fs * 0.52 / 72.0 * 25.4


def clip_ticks(fig):
    """删掉落在 xlim/ylim 之外的刻度。

    AutoLocator 会在视窗两端外再生成一个刻度（例如 xlim 到 8.5 却给了 10.0），
    刻度标签不会自动裁剪，会滑到画布外或压进相邻面板的 y 轴标签区。
    投稿图不允许任何出血，所以在 savefig 前统一清掉。
    """
    eps = 1e-9
    for ax in fig.axes:
        if not ax.axison:
            continue
        lo, hi = ax.get_xlim()
        keep = [t for t in ax.get_xticks() if lo - eps <= t <= hi + eps]
        if len(keep) and len(keep) < len(ax.get_xticks()):
            ax.set_xticks(keep)
        lo, hi = ax.get_ylim()
        keep = [t for t in ax.get_yticks() if lo - eps <= t <= hi + eps]
        if len(keep) and len(keep) < len(ax.get_yticks()):
            ax.set_yticks(keep)
