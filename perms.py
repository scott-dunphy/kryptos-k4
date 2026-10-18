"""Transposition permutation generators.

Convention: a permutation `perm` of length n means out[j] = in[perm[j]].
Every generator yields (label, perm). Callers test both perm and its inverse.
"""
import itertools
import numpy as np


def cell_orders(R, W):
    """16 traversal orders of an R x W grid (row/col major, flips, snake)."""
    orders = {}
    for major in ("row", "col"):
        for rflip in (0, 1):
            for cflip in (0, 1):
                for snake in (0, 1):
                    cells = []
                    outer = range(R) if major == "row" else range(W)
                    inner_n = W if major == "row" else R
                    for oi, o in enumerate(outer):
                        inner = list(range(inner_n))
                        if snake and oi % 2 == 1:
                            inner = inner[::-1]
                        for ii in inner:
                            r, c = (o, ii) if major == "row" else (ii, o)
                            if rflip:
                                r = R - 1 - r
                            if cflip:
                                c = W - 1 - c
                            cells.append((r, c))
                    orders[f"{major}{'R' if rflip else ''}{'C' if cflip else ''}{'S' if snake else ''}"] = cells
    return orders


def route_perms(n, widths=range(2, 50)):
    """Write sequence into grid in one order, read in another. Ragged grid: blanks at end or start."""
    for W in widths:
        R = -(-n // W)
        blanks = R * W - n
        orders = cell_orders(R, W)
        for bpos in ("end", "start") if blanks else ("end",):
            if bpos == "end":
                valid = {(r, c) for r in range(R) for c in range(W) if r * W + c < n}
            else:
                valid = {(r, c) for r in range(R) for c in range(W) if r * W + c >= blanks}
            for fname, fcells in orders.items():
                fc = [x for x in fcells if x in valid]
                pos = {cell: i for i, cell in enumerate(fc)}
                for rname, rcells in orders.items():
                    if rname == fname:
                        continue
                    perm = np.array([pos[x] for x in rcells if x in valid], dtype=np.int64)
                    yield f"route W{W} {bpos} {fname}->{rname}", perm


def columnar_perm(n, order, read_up=False):
    """Classic columnar: write rows of width len(order), read columns in `order` (list of col indices)."""
    W = len(order)
    perm = []
    for c in order:
        col = list(range(c, n, W))
        if read_up:
            col = col[::-1]
        perm.extend(col)
    return np.array(perm, dtype=np.int64)


def keyword_order(key):
    """Column read order from keyword (stable ties left-to-right)."""
    return [i for _, i in sorted((ch, i) for i, ch in enumerate(key))]


def columnar_all(n, wmax=8):
    for W in range(2, wmax + 1):
        for order in itertools.permutations(range(W)):
            yield f"col W{W} {''.join(map(str, order))}", columnar_perm(n, list(order))


def columnar_keywords(n, words):
    for w in words:
        if len(w) < 2:
            continue
        o = keyword_order(w)
        yield f"colkw {w}", columnar_perm(n, o)
        yield f"colkw {w} up", columnar_perm(n, o, read_up=True)


def inverse(perm):
    inv = np.empty_like(perm)
    inv[perm] = np.arange(len(perm))
    return inv
