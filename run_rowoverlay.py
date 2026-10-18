"""Per-row physical overlay: each K4 copper row may align with its own source row / horizontal shift / mirror.
Sources: right side (tableau) grid and left side (cipher) grid, 28 rows x 31 cols (torus in columns).
For K4 row 25 (13 cribs, cols 17-29) and row 27 (8 cribs, cols 0-7): key letter = SRC[r', (c+dx) or (dx-c)] .
Score = longest run of consecutive crib letters consistent with one variant & one indicator shift (and full count).
Null: random 28x31 letter grids and shuffled CT.
"""
import numpy as np
from numba import njit
import cribfilter as cf
from k4lib import AZ, KA

W = 31


def load(path):
    rows = [l.rstrip("\n") for l in open(path)]
    G = np.full((len(rows), W), -1, dtype=np.int64)
    for r, l in enumerate(rows):
        for c in range(min(W, len(l))):
            if l[c].isalpha():
                G[r, c] = ord(l[c]) - 65
    return G


IDX = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)


@njit(cache=True)
def best_runs(G, cols, req):
    # req: (nv, n) required key index; returns best longest-run and best full count over all placements
    H = G.shape[0]
    n = cols.shape[0]
    bestrun = 0; bestcnt = 0
    for r in range(H):
        for dx in range(W):
            for mirror in range(2):
                for v in range(req.shape[0]):
                    for kx in range(2):
                        for sh in range(26):
                            run = 0; cnt = 0
                            for t in range(n):
                                c = (cols[t] + dx) % W if mirror == 0 else (dx - cols[t]) % W
                                g = G[r, c]
                                if g >= 0 and (IDX[kx, g] + sh) % 26 == req[v, t]:
                                    run += 1; cnt += 1
                                    if run > bestrun:
                                        bestrun = run
                                else:
                                    run = 0
                            if cnt > bestcnt:
                                bestcnt = cnt
    return bestrun, bestcnt


def row_setup(cti, row):
    ts = [t for t in range(24) if (int(cf.CRIB_I[t]) + 27) // W == row]
    cols = np.array([(int(cf.CRIB_I[t]) + 27) % W for t in ts], dtype=np.int64)
    req = np.array([[cf.KV[v, cf.CRIB_L[t], cti[cf.CRIB_I[t]]] for t in ts] for v in range(cf.NV)], dtype=np.int64)
    return cols, req


if __name__ == "__main__":
    srcs = {"tableau(right)": load("data/sculpture_right.txt"), "cipher(left)": load("data/sculpture_left.txt")}
    rng = np.random.default_rng(0)
    for row, label in ((1, "row25 EASTNORTHEAST (13)"), (3, "row27 LINCLOCK (8)")):
        cols, req = row_setup(cf.CTI, row)
        for sname, G in srcs.items():
            print(f"{label} vs {sname}: best run / best count =", best_runs(G, cols, req), flush=True)
        nulls = [best_runs(rng.integers(0, 26, (28, W)), cols, req) for _ in range(5)]
        print(f"{label} NULL random grids:", nulls)
        sh = rng.permutation(cf.CTI)
        c2, r2 = row_setup(sh, row)
        print(f"{label} NULL shuffled CT vs tableau:", best_runs(srcs['tableau(right)'], c2, r2), flush=True)
