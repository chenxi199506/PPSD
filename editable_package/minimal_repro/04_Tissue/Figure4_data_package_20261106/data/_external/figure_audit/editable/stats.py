"""
stats.py — 图版上出现的每一个统计量，都在这里现算，不写死。

包含：
    rank()                 平均秩（并列取中秩）
    spearman()             Spearman ρ（对秩做 Pearson）
    exact_spearman_p()     n = 10 的双侧精确置换 P（子集 DP，不枚举 10!）
    bootstrap_rho_ci()     5000 次 Bootstrap 百分位 95% CI
    partial_rank_corr()    秩偏相关
    t_p_two_sided()        偏相关的 t 近似双侧 P（df = n − 2，与正文口径一致）

为什么要 DP：n = 10 时秩序共 10! = 3 628 800 种。由
    D² = Σ(i − pᵢ)² = 2Σi² − 2Σ i·pᵢ
可知 ρ 只依赖 S = Σ i·pᵢ，于是按「已占用秩的子集」做 2ⁿ 状态动态规划即可
得到精确分布（2¹⁰ = 1024 个状态），结果是精确的，不是近似。
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np


# ---------------------------------------------------------------- 秩
def rank(a) -> np.ndarray:
    """平均秩：并列取中秩（与 R 的 rank() / scipy 的 average 一致）。"""
    a = np.asarray(a, float)
    order = np.argsort(a)
    r = np.empty(len(a), float)
    sa = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sa[j + 1] == sa[i]:
            j += 1
        r[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return r


def spearman(x, y) -> float:
    rx, ry = rank(x), rank(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def _rank_sum_dist(n: int) -> dict[int, int]:
    """S = Σ i·pᵢ 在全部 n! 种秩序上的精确计数（子集 DP）。"""
    dist = [defaultdict(int) for _ in range(1 << n)]
    dist[0][0] = 1
    for mask in range(1 << n):
        k = bin(mask).count("1")
        if k == n or not dist[mask]:
            continue
        i = k + 1
        for j in range(n):
            if mask >> j & 1:
                continue
            nm = mask | (1 << j)
            add = i * (j + 1)
            d_nm = dist[nm]
            for S, c in dist[mask].items():
                d_nm[S + add] += c
    return dist[(1 << n) - 1]


def _rho_of_sum(S: float, n: int) -> float:
    """无并列时 ρ 与 S 的换算：ρ = 12S/(n³−n) − 3(n+1)/(n−1)。"""
    return 12 * S / (n ** 3 - n) - 3 * (n + 1) / (n - 1)


def critical_rho(n: int = 10, alpha: float = 0.05) -> float:
    """双侧精确置换的临界 |ρ|：使双侧 P ≤ α 的最小 |ρ|。n = 10、α = 0.05 时为 0.6485。"""
    full = _rank_sum_dist(n)
    tot = sum(full.values())
    vals = defaultdict(int)
    for S, c in full.items():
        vals[round(_rho_of_sum(S, n), 4)] += c
    for r in sorted({abs(k) for k in vals}):
        p = sum(c for k, c in vals.items() if abs(k) >= r - 1e-9) / tot
        if p <= alpha:
            return r
    return 1.0


# ---------------------------------------------------------------- 精确置换
def exact_spearman_p(x, y) -> float:
    """双侧精确置换 P（含并列时同样精确）。

    并列的处理：y 的秩多集中有重复值，把它当作可分配的值逐位放入 1..n，
    重复值造成的 2! 倍重复计数对每个排列是同一个常数，故比例不变。
    """
    rx, ry = rank(x), rank(y)
    n = len(rx)
    items = list(ry)
    obs = float((rx * ry).sum())

    dist = [defaultdict(int) for _ in range(1 << n)]
    dist[0][0] = 1
    for mask in range(1 << n):
        k = bin(mask).count("1")
        if k == n or not dist[mask]:
            continue
        i = k + 1                      # 第 i 个位置（x 的秩）
        for j in range(n):
            if mask >> j & 1:
                continue
            nm = mask | (1 << j)
            add = i * items[j]
            d_nm = dist[nm]
            for S, c in dist[mask].items():
                d_nm[S + add] += c

    full = dist[(1 << n) - 1]
    tot = sum(full.values())
    mean = sum(S * c for S, c in full.items()) / tot
    dev = abs(obs - mean)
    cnt = sum(c for S, c in full.items() if abs(S - mean) >= dev - 1e-9)
    return cnt / tot


def bootstrap_rho_ci(x, y, n_boot: int = 5000, seed: int = 20261031):
    """Bootstrap 百分位 95% CI。"""
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(x), size=(n_boot, len(x)))
    vals = [spearman(x[i], y[i]) for i in idx]
    return float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


# ---------------------------------------------------------------- 偏相关
def partial_rank_corr(x, y, z) -> float:
    """秩偏相关：控制 z 之后 x 与 y 的秩相关。"""
    rx, ry, rz = rank(x), rank(y), rank(z)
    rxy = np.corrcoef(rx, ry)[0, 1]
    rxz = np.corrcoef(rx, rz)[0, 1]
    ryz = np.corrcoef(ry, rz)[0, 1]
    return float((rxy - rxz * ryz) / np.sqrt((1 - rxz ** 2) * (1 - ryz ** 2)))


def t_p_two_sided(r: float, df: int) -> float:
    """t = r·√df / √(1 − r²) 的双侧 P。

    正文的口径是 df = n − 2（对偏相关略保守）。脚本照抄这个口径，
    只为让图上的数字与正文一致；要改成 df = n − 3 只需改这一处。
    """
    try:
        from scipy import stats as st
        t = r * np.sqrt(df) / np.sqrt(1 - r ** 2)
        return float(2 * st.t.sf(abs(t), df))
    except Exception:                       # 没有 scipy 时退化为正态近似
        from math import erfc, sqrt
        t = r * np.sqrt(df) / np.sqrt(1 - r ** 2)
        return float(erfc(abs(t) / sqrt(2)))
