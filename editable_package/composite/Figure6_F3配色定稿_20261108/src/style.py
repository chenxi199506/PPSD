"""
style.py — 全局样式。改配色 / 字号 / 尺寸 / 水印，只动这一个文件。

所有图版共用：
    C          调色板
    BAR_ALPHA  柱体填充透明度（0.18 与原件一致）
    FS         字号表
    STAMP      图版水印文字（None = 不印）
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# ---------------------------------------------------------------- 画布
MM = 1 / 25.4                 # 毫米 → 英寸
FIG_W_MM = 180.0              # 双栏宽，与原件一致

# ---------------------------------------------------------------- 配色
C = {
    # 五个功能组（与正文 §附录 A.2 的色卡一致）
    "nt":        "#4C78A8",
    "kd":        "#B4482F",
    "rescue":    "#6B8E6F",
    "vehicle":   "#8C8C8C",
    "mock":      "#8E6C8A",
    # 蛋白部分的五个处理组
    "untreated": "#9AA5B1",
    # 中性
    "ink":       "#1A1A1A",
    "muted":     "#5A5A5A",
    "faint":     "#8A8A8A",
    "grid":      "#D9D9D9",
    "axis":      "#333333",
    # 强调
    "accent":    "#B4482F",
    "navy":      "#2F5D8A",
}

BAR_ALPHA = 0.18              # 柱体填充透明度
DOT_ALPHA = 0.85

# ---------------------------------------------------------------- 字号（pt）
FS = {
    "figtitle": 9.6,          # 整版大标题
    "panel":  9.0,            # 面板字母 A/B/C
    "title":  8.0,            # 面板标题
    "sub":    6.6,            # 面板副标题
    "axis":   7.4,            # 轴标题
    "tick":   6.8,            # 刻度
    "annot":  6.4,            # 图上注记
    "star":   7.0,            # 显著性星号
    "small":  5.8,            # 极小字（表头、图例）
    "foot":   5.0,            # 页脚方法学段落
}

# ---------------------------------------------------------------- 水印
# 数据已确认为真实实验数据（2026-11-01 用户确认），不印水印。
# 若要临时加回，把下面这行改成字符串即可，例如：
#     STAMP = "SIMULATED DATA — not for publication"
STAMP = None
STAMP_COLOR = "#B4482F"


# ---------------------------------------------------------------- rcParams
def apply() -> None:
    mpl.rcParams.update({
        "font.family":      "sans-serif",
        "font.sans-serif":  ["Arial", "Helvetica", "Helvetica Neue", "DejaVu Sans"],
        "font.size":        FS["tick"],
        "axes.linewidth":   0.7,
        "axes.edgecolor":   C["axis"],
        "axes.labelcolor":  C["ink"],
        "axes.labelsize":   FS["axis"],
        "axes.titlesize":   FS["title"],
        "axes.spines.top":  False,
        "axes.spines.right": False,
        "xtick.color":      C["axis"],
        "ytick.color":      C["axis"],
        "xtick.labelsize":  FS["tick"],
        "ytick.labelsize":  FS["tick"],
        "xtick.major.width": 0.7,
        "ytick.major.width": 0.7,
        "xtick.major.size": 2.6,
        "ytick.major.size": 2.6,
        "xtick.direction":  "out",
        "ytick.direction":  "out",
        "legend.frameon":   False,
        "legend.fontsize":  FS["small"],
        "savefig.dpi":      300,
        "savefig.bbox":     "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype":     42,     # Type 42，可编辑文字
        "ps.fonttype":      42,
        "figure.facecolor": "white",
        "axes.facecolor":   "white",
        "lines.linewidth":  0.9,
    })


def figure(width_mm: float = FIG_W_MM, height_mm: float = 100.0):
    """按毫米建画布。"""
    return plt.figure(figsize=(width_mm * MM, height_mm * MM))


# ---------------------------------------------------------------- 组件
def panel_head(ax, letter: str, title: str, subtitle: str | None = None,
               x: float = 0.0, pad: float = 6.0, fs_title: float | None = None) -> None:
    """面板标题：粗体字母 + 标题 + 可选副标题。

    位置用「点」偏移（不是轴比例），所以高矮不同的面板看起来一样齐。
    副标题含换行时，标题会自动再抬高，避免压字。
    """
    n = subtitle.count("\n") + 1 if subtitle else 0
    top = pad + (11.0 if n <= 1 else 9.6 * n + 2.5) if n else pad
    ax.annotate(letter, xy=(x, 1.0), xycoords="axes fraction",
                xytext=(-1.0, top), textcoords="offset points",
                ha="left", va="bottom", annotation_clip=False,
                fontsize=FS["panel"], fontweight="bold", color=C["ink"])
    ax.annotate(title, xy=(x, 1.0), xycoords="axes fraction",
                xytext=(7.5, top), textcoords="offset points",
                ha="left", va="bottom", annotation_clip=False,
                fontsize=fs_title or FS["title"], color=C["ink"])
    if subtitle:
        ax.annotate(subtitle, xy=(x, 1.0), xycoords="axes fraction",
                    xytext=(-1.0, pad), textcoords="offset points",
                    ha="left", va="bottom", annotation_clip=False,
                    fontsize=FS["sub"], color=C["faint"], linespacing=1.45)


def bracket(ax, x1: float, x2: float, y: float, label: str,
            h: float, lw: float = 0.7, color: str | None = None,
            fs: float | None = None) -> None:
    """显著性括号。y 为横线高度，h 为向下两腿长度（数据单位）。"""
    color = color or C["axis"]
    fs = fs or FS["star"]
    ax.plot([x1, x1, x2, x2], [y - h, y, y, y - h],
            lw=lw, color=color, solid_capstyle="butt", clip_on=False, zorder=6)
    ax.text((x1 + x2) / 2, y + h * 0.18, label, ha="center", va="bottom",
            fontsize=fs, color=color, zorder=6)


def style_axis(ax, ylabel: str | None = None, xlabel: str | None = None) -> None:
    if ylabel:
        ax.set_ylabel(ylabel, labelpad=3)
    if xlabel:
        ax.set_xlabel(xlabel, labelpad=3)
    ax.tick_params(pad=2)


def strip_spines(ax, keep=("left", "bottom")) -> None:
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(s in keep)


def rounded_box(ax, x, y, w, h, text, fs=None, fill="#F4F6F8",
                edge="#9AA5B1", weight="normal", lw=0.7):
    """示意图用的圆角框。坐标用 0–1 的轴坐标。"""
    fs = fs or FS["small"]
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.004,rounding_size=0.02",
                                linewidth=lw, edgecolor=edge, facecolor=fill,
                                transform=ax.transAxes, clip_on=False, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=C["ink"], linespacing=1.45,
            transform=ax.transAxes, zorder=3, weight=weight)


def arrow(ax, x1, y1, x2, y2, lw=0.7, color=None, style="-|>", ms=5.5):
    color = color or C["faint"]
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2),
                                 arrowstyle=style, mutation_scale=ms,
                                 linewidth=lw, color=color,
                                 transform=ax.transAxes, clip_on=False, zorder=1))


def blank(ax):
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)


def stamp(fig, text: str | None = None) -> None:
    """图版水印（右下角）。text=None 时用 style.STAMP。"""
    t = STAMP if text is None else text
    if not t:
        return
    fig.text(0.995, 0.004, t, ha="right", va="bottom",
             fontsize=FS["small"] + 0.4, color=STAMP_COLOR, style="italic")


def fig_head(fig, title: str, subtitle: str | None = None,
             x: float = 0.006, y: float = 0.996, dy: float = 0.0225) -> None:
    """整版大标题 + 灰色副标题（figure 坐标，左上角）。"""
    fig.text(x, y, title, ha="left", va="top",
             fontsize=FS["figtitle"], fontweight="bold", color=C["ink"])
    if subtitle:
        fig.text(x, y - dy, subtitle, ha="left", va="top",
                 fontsize=FS["sub"], color=C["faint"])


def footnote(fig, text: str, x: float = 0.006, y: float = 0.006,
             width_mm: float = 177.0, fs: float | None = None,
             color: str | None = None) -> None:
    """页脚方法学段落。按版心宽度自动折行（不靠手动加 \\n）。"""
    import textwrap
    fs = fs or FS["foot"]
    color = color or C["faint"]
    chars = max(60, int(width_mm / (fs * 0.3528 * 0.475)))
    fig.text(x, y, textwrap.fill(text, chars), ha="left", va="bottom",
             fontsize=fs, color=color, linespacing=1.55)
