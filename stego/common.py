"""Shared helpers for team-stego experiments: sculpture grids, K4 cell coordinates, keystream crib tester."""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cribfilter as cf
from k4lib import AZ, KA, CT, HERE

LEFT = open(os.path.join(HERE, "data", "sculpture_left.txt")).read().split("\n")[:28]
RIGHT = open(os.path.join(HERE, "data", "sculpture_right.txt")).read().split("\n")[:28]

# K4 index -> (row, col) on left panel
K4_CELLS = [(24, 27 + i) for i in range(4)] + [(25 + (i // 31), i % 31) for i in range(93)]
assert "".join(LEFT[r][c] for r, c in K4_CELLS) == CT

REQ = {}  # (v) -> required key index per crib (array over CRIB_I)
for v in range(cf.NV):
    REQ[v] = cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]]


def test_key(key, min_known=12):
    """key: string/list len 97 of letters (None/'?' unknown). Returns best (agree, known, kal, v, shift).
    Agreement = largest group of cribs whose (keyidx - required) agree mod 26 (allows Quagmire indicator shift)."""
    best = (0, 0, None, None, None)
    idx = [i for i in cf.CRIB_I if key[i] is not None and key[i] in AZ]
    known = len(idx)
    if known < min_known:
        return best
    sel = np.array([t for t, i in enumerate(cf.CRIB_I) if key[i] is not None and key[i] in AZ])
    for kname, kal in (("AZ", AZ), ("KA", KA)):
        K = np.array([kal.index(key[i]) for i in cf.CRIB_I[sel]])
        for v in range(cf.NV):
            d = (K - REQ[v][sel]) % 26
            cnt = np.bincount(d, minlength=26)
            b = int(cnt.max())
            if b > best[0]:
                best = (b, known, kname, v, int(cnt.argmax()))
    return best


def null_dist(n_known=24, trials=20000, seed=1):
    """Empirical distribution of best agreement for random keys (same 24-variant max)."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(trials):
        key = [None] * 97
        for i in cf.CRIB_I[:n_known]:
            key[i] = AZ[rng.integers(26)]
        out.append(test_key(key)[0])
    return np.bincount(out)
