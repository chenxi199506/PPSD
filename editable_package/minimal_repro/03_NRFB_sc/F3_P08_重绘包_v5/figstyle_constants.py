# -*- coding: utf-8 -*-
"""F3_P08 便携包的最小样式常量。

从 10_图版_NRFB身份_20261104/scripts/03_figures.py 原样抽取
NRFB / STATE_ORDER / SHORT / C_ACCENT / C_OTHER 与 box_h()。
原模块顶层会读取 stats_sc.json 与 stats_bulk.json 并建目录，
本模块只保留绘图真正用到的定义，因此包内不需要那两个 JSON，
也无需 duckdb / pyarrow。数值与画法与 v5 完全一致。
"""
import numpy as np
from matplotlib.patches import Rectangle
import journal_style as J

NRFB = "NR-FB core"
STATE_ORDER = ["PRG4+ lining", "Sublining", "DKK3+ intermediate", "COMP+ transitional",
               "Transitional activated", "Remodeling", "AP-1 stress", "Inflammatory",
               "Proliferating", "NR-FB core"]
SHORT = {"PRG4+ lining": "PRG4+ lining", "Sublining": "Sublining",
         "DKK3+ intermediate": "DKK3+ interm.", "COMP+ transitional": "COMP+ transit.",
         "Transitional activated": "Trans. activated", "Remodeling": "Remodeling",
         "AP-1 stress": "AP-1 stress", "Inflammatory": "Inflammatory",
         "Proliferating": "Proliferating", "NR-FB core": "NR-FB core",
         "Lining-1": "Lining-1", "Lining-2": "Lining-2", "Lining-3": "Lining-3",
         "Myofibroblast": "Myofibroblast", "MHCII": "MHCII",
         "NR-FB gradient": "NR-FB gradient"}

# 单一强调色 + 一组低饱和色：被检验的状态永远是红色，其它状态不抢视线
C_ACCENT = J.ACCENT
C_OTHER = ["#4C78A8", "#7FA8C9", "#A9C0D4", "#6B8E6F", "#8E6C8A",
           "#C9A227", "#E08A5F", "#9C9C9C", "#B3B3B3"]


def box_h(ax, data, states, colors, width=0.62, show_labels=True):
    """水平箱线 + 中位线；不画离群点（几万个细胞画出来就是一团墨）。"""
    pos = np.arange(len(states))[::-1]
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
    ax.set_ylim(-0.7, len(states) - 0.3)
