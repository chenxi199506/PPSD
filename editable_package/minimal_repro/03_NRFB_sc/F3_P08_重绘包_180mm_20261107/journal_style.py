"""顶刊图版统一样式模块 —— NEJM / JAMA 投稿风格。

用法：把本文件复制到出图脚本同目录，`import journal_style as J`。

锁定项（不要在每个脚本里重新调参）
--------------------------------
画幅     180 mm 双栏 / 132 mm 1.5 栏 / 88 mm 单栏
字体     Arial（缺失时回退 DejaVu Sans），最小字号 5.6 pt，PDF 用 Type 42
底色     纯白，无阴影、无网格、无外框
轴线     仅左/下，0.5 pt；刻度朝外 2.4 pt 长
面板    粗体字母 9.2 pt + 句式化说明 7.3 pt + 灰色补充行 6.3 pt
页眉     编号（粗体）+ 标题 8.8 pt + 灰色副标题 6.9 pt
页脚     6.0 pt 灰色，三件事：分析单位 / 方法 / 明确不主张什么
导出     600 dpi PNG + 矢量 PDF（pdf.fonttype = 42）
"""

from __future__ import annotations

import sys

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------- geometry
MM = 1.0 / 25.4
W2 = 180.0   # 双栏
W15 = 132.0  # 1.5 栏
W1 = 88.0    # 单栏

MIN_PT = 5.6  # 期刊常见下限：5–6 pt。任何可见文字不得小于此值。

# ---------------------------------------------------------------- palette
INK = "#1A1A1A"      # 正文墨色，不用纯黑
MUTED = "#6E6E6E"    # 次级说明、页脚
FAINT = "#B3B3B3"
RULE = "#333333"     # 轴线
HAIRLINE = "#C9C9C9" # 0 线、参考线

# 对照组固定配色：全项目统一，不随图变化
HEALTHY = "#4C78A8"  # 健康 / 对照
OA = "#B4482F"       # 疾病组
GRAY = "#8C8C8C"
LIGHT = "#E2E2E2"
ACCENT = "#C1272D"   # 只留给“被检验的那个量”，不要用于装饰
SAGE = "#6B8E6F"
SAND = "#C9A227"
PLUM = "#8E6C8A"

GROUP_COLOR = {"Healthy": HEALTHY, "Control": HEALTHY, "OA": OA, "Disease": OA}
CAT = [HEALTHY, OA, SAGE, PLUM, SAND, GRAY]

# 白->赭，亮度单调，灰度打印仍可读
SEQ = LinearSegmentedColormap.from_list(
    "seq_brick", ["#FFFFFF", "#F6E3DC", "#E7B39F", "#CE7A5E", "#A9432B", "#7A2A19"]
)
SEQ_BLUE = LinearSegmentedColormap.from_list(
    "seq_blue", ["#FFFFFF", "#E4EDF4", "#BCD3E4", "#8FB2CC", "#5A87A8", "#2F5D7C"]
)


# ---------------------------------------------------------------- rc
def apply_rc() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7.0,
            "axes.titlesize": 7.4,
            "axes.labelsize": 7.0,
            "xtick.labelsize": 6.4,
            "ytick.labelsize": 6.4,
            "legend.fontsize": 6.4,
            "axes.linewidth": 0.5,
            "axes.edgecolor": RULE,
            "axes.labelcolor": INK,
            "text.color": INK,
            "xtick.color": RULE,
            "ytick.color": RULE,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "xtick.major.width": 0.5,
            "ytick.major.width": 0.5,
            "xtick.major.size": 2.4,
            "ytick.major.size": 2.4,
            "xtick.minor.width": 0.4,
            "ytick.minor.width": 0.4,
            "legend.frameon": False,
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.bbox": None,   # 绝不用 tight：会改掉画幅物理尺寸
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


apply_rc()


# ---------------------------------------------------------------- canvas
def plate(width_mm: float = W2, height_mm: float = 150.0) -> plt.Figure:
    """定尺画布。高度按内容预算，交付清单里记录实际值。"""
    fig = plt.figure(figsize=(width_mm * MM, height_mm * MM))
    fig.patch.set_facecolor("white")
    return fig


def plate_mm(fig: plt.Figure) -> tuple[float, float]:
    w, h = fig.get_size_inches()
    return w / MM, h / MM


_PROP_CACHE: dict = {}


def _resolve_family() -> str:
    """在 rcParams 候选里挑一个系统真有的字体名，避免 findfont 反复告警。"""
    from matplotlib import font_manager as fm

    installed = {f.name for f in fm.fontManager.ttflist}
    for fam in plt.rcParams["font.sans-serif"]:
        if fam in installed:
            return fam
    return "DejaVu Sans"


def _prop(size: float, weight: str = "normal"):
    from matplotlib.font_manager import FontProperties

    key = (size, weight)
    if key not in _PROP_CACHE:
        _PROP_CACHE[key] = FontProperties(family=_resolve_family(), size=size, weight=weight)
    return _PROP_CACHE[key]


def measure_mm(fig: plt.Figure, s: str, size: float, weight: str = "normal") -> float:
    """字符串在给定字号下的物理宽度（mm）。

    用字形轮廓（TextPath）量，不用 fig.text + get_window_extent：
    后者在 fig.dpi=100 的画布上测 6 pt 文字，字形 advance 被取整，
    实测偏窄约 10%，于是按它换行的页脚会被画布裁掉。轮廓测量与 dpi 无关。
    """
    from matplotlib.textpath import TextPath

    if not s:
        return 0.0
    tp = TextPath((0, 0), s, prop=_prop(size, weight), usetex=False)
    return float(tp.get_extents().width) * 0.3528  # pt -> mm


def wrap_mm(fig: plt.Figure, text: str, max_mm: float, size: float,
            weight: str = "normal") -> str:
    """按实测宽度硬换行，返回带 \\n 的字符串。

    为什么必须这么做：matplotlib 没有自动换行，页脚一旦超宽就被画布裁掉，
    而裁掉的是“不主张什么”这类关键限定语。
    """
    if not text:
        return ""
    out = []
    for para in text.split("\n"):
        words, line = para.split(" "), ""
        for w in words:
            trial = f"{line} {w}".strip()
            if line and measure_mm(fig, trial, size, weight) > max_mm:
                out.append(line)
                line = w
                # 单个词就超宽（长基因名/编号）时按字符切
                while measure_mm(fig, line, size, weight) > max_mm and len(line) > 1:
                    cut = len(line)
                    while cut > 1 and measure_mm(fig, line[:cut], size, weight) > max_mm:
                        cut -= 1
                    out.append(line[:cut])
                    line = line[cut:]
            else:
                line = trial
        out.append(line)
    return "\n".join(out)


def equal_rect(fig: plt.Figure, rect, aspect: float):
    """返回一个新的 add_axes 矩形，使面板在图上真实显示长宽比 = aspect（高/宽）。

    为什么需要：`ax.set_aspect('equal')` 只缩小可见数据区，不改变 axes 占位，
    结果组织图像缩在面板左上角、留出大片空白，页脚也随之错位。
    先按数据 bbox 的 aspect 反算矩形高度，再创建 axes，版面才可控。
    rect = [x0, y0, w, h]（图幅比例），保持左上角不动。
    """
    x0, y0, w, h = rect
    fw, fh = fig.get_size_inches()
    h_new = w * fw * aspect / fh
    return [x0, y0 + h - h_new, w, h_new]


# ---------------------------------------------------------------- header / footer
def header(fig: plt.Figure, number: str, title: str, subtitle: str | None = None,
           x: float = 0.008, y: float = 0.988, size: float = 8.8,
           subtitle_size: float = 6.9) -> None:
    """编号粗体 + 标题常规 + 灰色副标题（副标题放范围、n、口径，不放结论）。

    标题若过长会自动折行，副标题按实际行数下移——不要用固定像素偏移，
    否则换一个画幅高度就压在一起。
    """
    pw, ph = plate_mm(fig)
    fig.text(x, y, number, fontsize=size, fontweight="bold", color=INK,
             va="top", ha="left")
    # 轮廓测量不含行尾空格，必须自己加固定间距，否则标题会贴上编号
    pad_mm = measure_mm(fig, number, size, "bold") + 1.6
    pad = pad_mm / pw
    avail = pw * 0.985 - (x * pw + pad_mm)
    title_txt = wrap_mm(fig, title, avail, size)
    fig.text(x + pad, y, title_txt, fontsize=size, color=INK, va="top",
             ha="left", linespacing=1.30)
    if subtitle:
        n_lines = title_txt.count("\n") + 1
        drop = (n_lines * size * 1.30 * 0.3528 + 1.1) / ph
        fig.text(x, y - drop, subtitle, fontsize=subtitle_size, color=MUTED,
                 va="top", ha="left")


def footer(fig: plt.Figure, text: str, x: float = 0.008, y: float = 0.010,
           width_mm: float | None = None, size: float = 6.0,
           linespacing: float = 1.55) -> None:
    """页脚固定三段：分析单位（n 是什么）、方法、明确不主张什么。

    不要写“代表性图像”这类空话；不要在这里新增结论。
    """
    if not text:
        return
    # 留 2 mm 保险：轮廓测量不含右侧字侧距，实测仍可能贴边
    w_mm = width_mm if width_mm is not None else plate_mm(fig)[0] - 2 * x * plate_mm(fig)[0]
    w_mm = max(40.0, w_mm - 2.0)
    fig.text(x, y, wrap_mm(fig, text, w_mm, size), fontsize=size, color=MUTED,
             va="bottom", ha="left", linespacing=linespacing)


def tag(fig: plt.Figure, ax: plt.Axes, letter: str, title: str | None = None,
        note: str | None = None, gap_mm: float = 1.8, tx_mm: float = 3.4,
        size_letter: float = 9.2, size_title: float = 7.3,
        size_note: float = 6.3, max_mm: float | None = None) -> None:
    """面板字母 + 句式化说明 + 灰色补充行，自 axes 上沿向上生长。

    说明行写成完整句子（"Detection rises with depth"），不要写成名词短语标签；
    只有名词短语时读者需要自己回去读图注。所有位移用 mm 计算，换画幅高度不串位。
    """
    bb = ax.get_position()
    pw, ph = plate_mm(fig)
    if max_mm is None:
        max_mm = max(28.0, pw * 0.98 - (bb.x0 + tx_mm / pw) * pw)

    title_txt = wrap_mm(fig, title, max_mm, size_title) if title else ""
    note_txt = wrap_mm(fig, note, max_mm, size_note) if note else ""
    n_title = title_txt.count("\n") + 1 if title_txt else 0
    n_note = note_txt.count("\n") + 1 if note_txt else 0

    # 整个标题块的上沿：从 axes 顶边往上一段 gap
    block_h = n_title * size_title * 1.35 * 0.3528 + 0.9 + n_note * size_note * 1.35 * 0.3528
    y_top = bb.y1 + (gap_mm + block_h) / ph

    fig.text(bb.x0, y_top, letter, fontsize=size_letter, fontweight="bold",
             color=INK, va="top", ha="left")
    if title_txt:
        fig.text(bb.x0 + tx_mm / pw, y_top, title_txt, fontsize=size_title,
                 color=INK, va="top", ha="left", linespacing=1.35)
    if note_txt:
        y_note = y_top - (n_title * size_title * 1.35 * 0.3528 + 0.9) / ph
        fig.text(bb.x0 + tx_mm / pw, y_note, note_txt, fontsize=size_note,
                 color=MUTED, va="top", ha="left", linespacing=1.35)


# ---------------------------------------------------------------- axes
def style_axis(ax: plt.Axes, xlabel: str | None = None, ylabel: str | None = None,
               zero: bool = False, bottom_only: bool = False,
               labelpad: float = 3.0) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_visible(True)
        ax.spines[side].set_color(RULE)
        ax.spines[side].set_linewidth(0.5)
    if bottom_only:
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0)
    ax.tick_params(direction="out", length=2.4, width=0.5, colors=RULE,
                   labelcolor=INK, pad=2.0)
    ax.grid(False)
    if zero:
        ax.axhline(0, color=HAIRLINE, lw=0.55, ls=(0, (4, 2)), zorder=0)
    if xlabel:
        ax.set_xlabel(xlabel, labelpad=labelpad, color=INK)
    if ylabel:
        ax.set_ylabel(ylabel, labelpad=labelpad, color=INK)


def rotated_xticks(ax: plt.Axes, labels, rotation: float = 38.0, size: float = 6.4) -> None:
    """长标签的标准写法。少 rotation_mode 会让标签整体右移、压住下一个刻度。"""
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=rotation, ha="right",
                       rotation_mode="anchor", fontsize=size, color=INK)


def no_frame(ax: plt.Axes) -> None:
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])


def scalebar(ax: plt.Axes, xy: np.ndarray, length_um: float = 1000.0,
             label: str | None = None,
             frac_xy: tuple[float, float] = (0.06, 0.045)) -> None:
    """数据坐标下的比例尺（图像 y 轴反向时可直接用）。"""
    x0 = xy[:, 0].min() + frac_xy[0] * np.ptp(xy[:, 0])
    y0 = xy[:, 1].max() - frac_xy[1] * np.ptp(xy[:, 1])
    ax.plot([x0, x0 + length_um], [y0, y0], color=INK, lw=1.8,
            solid_capstyle="butt", zorder=20)
    ax.text(x0 + length_um / 2, y0 + 0.012 * np.ptp(xy[:, 1]),
            label or f"{length_um / 1000:g} mm", ha="center", va="top",
            fontsize=6.0, color=INK, zorder=20)


def strip_legend(ax: plt.Axes, items, ncol: int = 1, loc: str = "upper left",
                 handle: str = "s", ms: float = 4.0, **kw):
    """点/方块图例。不画图例框；图例不得压在数据或组织上。"""
    handles = [
        Line2D([], [], marker=handle, linestyle="", markersize=ms,
               markerfacecolor=c, markeredgecolor=c, label=l)
        for l, c in items
    ]
    leg = ax.legend(handles=handles, loc=loc, ncol=ncol, handletextpad=0.5,
                    borderpad=0.2, labelspacing=0.45, frameon=False,
                    fontsize=6.3, **kw)
    for t in leg.get_texts():
        t.set_color(INK)
    return leg


def annotate_cbar(fig: plt.Figure, ax: plt.Axes, im, label: str,
                  width: float = 0.010, side: str = "right"):
    """细竖色标，贴紧面板外侧。"""
    bb = ax.get_position()
    x = bb.x1 + 0.006 if side == "right" else bb.x0 - 0.006 - width
    cax = fig.add_axes([x, bb.y0 + bb.height * 0.16, width, bb.height * 0.68])
    cb = fig.colorbar(im, cax=cax)
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=2.0, width=0.5, labelsize=6.0, pad=1.6, colors=RULE)
    for t in cb.ax.get_yticklabels():
        t.set_color(INK)
    cb.set_label(label, fontsize=6.2, color=INK, labelpad=3.0)
    return cb


def cbar_below(fig: plt.Figure, ax: plt.Axes, im, label: str,
               height: float = 0.012, width_frac: float = 0.55,
               label_side: str = "right"):
    """横向色标放在面板下方：组织铺满整个面板时用它，别在图上开洞。"""
    bb = ax.get_position()
    w = bb.width * width_frac
    cax = fig.add_axes([bb.x0 + bb.width * 0.02, bb.y0 - height - 0.030, w, height])
    cb = fig.colorbar(im, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.tick_params(length=2.0, width=0.5, labelsize=6.0, pad=1.6, colors=RULE)
    for t in cb.ax.get_xticklabels():
        t.set_color(INK)
    if label_side == "right":
        cb.set_label(label, fontsize=6.2, color=INK, labelpad=2.0, loc="right")
    return cb


# ---------------------------------------------------------------- guard
def _has_cjk(s: str) -> bool:
    return any("\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f"
               or "\uff00" <= ch <= "\uffef" for ch in s)


def check_layout(fig: plt.Figure, margin_mm: float = 0.6) -> list[str]:
    """导出前自动体检：文字越界、字号过小、混入中文。

    返回问题列表（空 = 通过）。这三条正是人工目视最容易漏掉、而期刊最容易退回的问题。
    """
    problems = []
    # 必须在高 dpi 下量：100 dpi 画布上 6 pt 文字会窄 10%，会漏报越界
    old_dpi = fig.dpi
    if old_dpi < 300:
        fig.set_dpi(300)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    fw, fh = fig.bbox.width, fig.bbox.height
    pad_x = margin_mm / plate_mm(fig)[0]
    pad_y = margin_mm / plate_mm(fig)[1]

    texts = list(fig.texts)
    for ax in fig.axes:
        texts += [ax.title, ax.xaxis.label, ax.yaxis.label]
        texts += ax.get_xticklabels() + ax.get_yticklabels()
        if ax.get_legend() is not None:
            texts += ax.get_legend().get_texts()

    for t in texts:
        s = t.get_text()
        if not s.strip():
            continue
        if _has_cjk(s):
            problems.append(f"CJK 混入图版（会渲染成方框）: {s[:30]!r}")
        size = t.get_fontsize()
        if size and size < MIN_PT - 0.05:
            problems.append(f"字号 {size:.1f} pt < {MIN_PT} pt: {s[:30]!r}")
        try:
            bb = t.get_window_extent(renderer=renderer)
        except Exception:
            continue
        if not t.get_visible():
            continue
        left, right = bb.x0 / fw, bb.x1 / fw
        bottom, top = bb.y0 / fh, bb.y1 / fh
        if left < -0.001 or right > 1 + 0.001 or bottom < -0.001 or top > 1 + 0.001:
            problems.append(f"越出画布: {s[:40]!r}  x[{left:.3f},{right:.3f}] y[{bottom:.3f},{top:.3f}]")
        elif right > 1 - pad_x or left < pad_x:
            problems.append(f"贴边（<{margin_mm} mm）: {s[:40]!r}  right={right:.3f}")
    # 去重保序
    seen, out = set(), []
    for p in problems:
        if p not in seen:
            seen.add(p)
            out.append(p)
    fig.set_dpi(old_dpi)
    return out


# ---------------------------------------------------------------- export
def save(fig: plt.Figure, outdir, stem: str, dpi: int = 600,
         strict: bool = False) -> None:
    """双输出：PNG 供审稿系统预览，PDF 供排版。导出前自动跑 check_layout。"""
    from pathlib import Path

    problems = check_layout(fig)
    if problems:
        print(f"  !! {stem}: {len(problems)} 处版式问题", flush=True)
        for p in problems[:12]:
            print(f"     - {p}", flush=True)
        if strict:
            plt.close(fig)
            raise SystemExit(f"{stem}: 版式体检未通过")

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    fig.savefig(outdir / f"{stem}.png", dpi=dpi, facecolor="white")
    fig.savefig(outdir / f"{stem}.pdf", facecolor="white")
    w, h = plate_mm(fig)
    plt.close(fig)
    print(f"  saved {stem}.png / .pdf  [{w:.0f} x {h:.0f} mm @ {dpi} dpi]", flush=True)
