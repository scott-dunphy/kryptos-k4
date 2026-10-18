"""Constrained decode under the letter-class model M1.
Model: PT letter p in KRYPTOS -> CT within ±W of p (AZ); other p -> sigma(p) ± W, sigma unknown but consistent:
 all positions with PT = x (non-KRYPTOS) must have CT inside one circular window of width 2W+1.
Cribs fixed (positions 64, 71 exempt from constraints). SA over non-crib PT letters maximizing quadgram score minus
penalty for constraint violations. Null: same on shuffled CT (cribs PT fixed). Report best real vs null.
"""
import numpy as np
from numba import njit
from k4lib import CT, CRIB_POS, load_quadgrams, AZ

QG = load_quadgrams()
KRY = np.zeros(26, dtype=np.int64)
for c in "KRYPTOS":
    KRY[ord(c) - 65] = 1
CRIB = np.full(97, -1, dtype=np.int64)
for i, c in CRIB_POS.items():
    CRIB[i] = ord(c) - 65
EXEMPT = np.zeros(97, dtype=np.int64); EXEMPT[64] = 1; EXEMPT[71] = 1


@njit(cache=True)
def violations(pt, ct, W, KRY, EXEMPT):
    occ = np.zeros((26, 26), dtype=np.int64)
    v = 0
    for i in range(97):
        if EXEMPT[i]:
            continue
        p = pt[i]; c = ct[i]
        if KRY[p]:
            d = (c - p + 13) % 26 - 13
            if d > W or d < -W:
                v += 1
        else:
            occ[p, c] += 1
    for x in range(26):
        if KRY[x]:
            continue
        tot = 0
        for c in range(26):
            tot += occ[x, c]
        if tot == 0:
            continue
        best = 0
        for s in range(26):
            inside = 0
            for d in range(2 * W + 1):
                inside += occ[x, (s + d) % 26]
            if inside > best:
                best = inside
        v += tot - best
    return v


@njit(cache=True)
def score(pt, QG):
    s = 0.0
    for i in range(94):
        s += QG[((pt[i] * 26 + pt[i + 1]) * 26 + pt[i + 2]) * 26 + pt[i + 3]]
    return s / 94.0


@njit(cache=True)
def anneal(ct, W, CRIB, KRY, EXEMPT, QG, iters, seed, pen):
    np.random.seed(seed)
    pt = np.empty(97, dtype=np.int64)
    free = np.empty(97, dtype=np.int64); nf = 0
    for i in range(97):
        if CRIB[i] >= 0:
            pt[i] = CRIB[i]
        else:
            pt[i] = np.random.randint(0, 26); free[nf] = i; nf += 1
    cur = score(pt, QG) - pen * violations(pt, ct, W, KRY, EXEMPT)
    best = cur; bpt = pt.copy()
    for it in range(iters):
        T = 0.5 * (1 - it / iters) + 0.005
        i = free[np.random.randint(0, nf)]
        old = pt[i]; pt[i] = np.random.randint(0, 26)
        new = score(pt, QG) - pen * violations(pt, ct, W, KRY, EXEMPT)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new
            if cur > best:
                best = cur; bpt[:] = pt
        else:
            pt[i] = old
    return best, bpt


def run(ctarr, label, W=3, restarts=12, iters=400000):
    res = []
    for r in range(restarts):
        b, pt = anneal(ctarr, W, CRIB, KRY, EXEMPT, QG, iters, 100 + r, 0.05)
        v = violations(pt, ctarr, W, KRY, EXEMPT)
        res.append((score(pt, QG), v, "".join(AZ[x] for x in pt)))
    res.sort(key=lambda x: (x[1], -x[0]))
    clean = [x for x in res if x[1] == 0]
    bestq = max((x[0] for x in clean), default=None)
    print(f"{label}: constraint-clean restarts {len(clean)}/{restarts}, best clean qscore {bestq}")
    for x in res[:3]:
        print(f"   q={x[0]:.3f} viol={x[1]} {x[2]}")
    return bestq


if __name__ == "__main__":
    cta = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
    real = run(cta, "REAL")
    rng = np.random.default_rng(0)
    nulls = [run(rng.permutation(cta), f"NULL{k}") for k in range(5)]
    print("REAL best", real, "NULL bests", nulls)
