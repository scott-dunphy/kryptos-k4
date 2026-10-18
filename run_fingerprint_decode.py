"""Fingerprint-constrained decode.
Constraint F: at every position, PT letter in KRYPTOS  <=>  |C - P| <= 2 (AZ). (Both directions; the forward direction
is the strong one: 9/10 cribs; the reverse is weaker: 12/14 non-K cribs outside ±2.)
Candidate letters per non-crib position i: K-letters within ±2 of C[i]  U  non-K letters NOT within ±2 of C[i].
Search: SA over the 73 free positions with quadgram score; then word-score. Cribs fixed. Null: non-crib CT shuffled.
Also prints the per-position allowed KRYPTOS letters (the 'map').
"""
import numpy as np
from numba import njit
from k4lib import CT, CRIB_POS, load_quadgrams, AZ
from wordscore import wseg

QG = load_quadgrams()
KRY = "KRYPTOS"
CTA = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
CRIB = np.full(97, -1, dtype=np.int64)
for i, c in CRIB_POS.items():
    CRIB[i] = ord(c) - 65


def allowed(cta, strict_nonk=True):
    A = np.zeros((97, 26), dtype=np.bool_)
    for i in range(97):
        if CRIB[i] >= 0:
            A[i, CRIB[i]] = True
            continue
        for p in range(26):
            d = abs(((int(cta[i]) - p + 13) % 26) - 13)
            isk = AZ[p] in KRY
            if isk and d <= 2:
                A[i, p] = True
            elif (not isk) and (d > 2 or not strict_nonk):
                A[i, p] = True
    return A


@njit(cache=True)
def score(pt, QG):
    s = 0.0
    for i in range(94):
        s += QG[((pt[i] * 26 + pt[i + 1]) * 26 + pt[i + 2]) * 26 + pt[i + 3]]
    return s / 94.0


@njit(cache=True)
def anneal(A, CRIB, QG, iters, seed):
    np.random.seed(seed)
    pt = np.empty(97, dtype=np.int64)
    opts = np.zeros((97, 26), dtype=np.int64); nopt = np.zeros(97, dtype=np.int64)
    for i in range(97):
        m = 0
        for p in range(26):
            if A[i, p]:
                opts[i, m] = p; m += 1
        nopt[i] = m
        pt[i] = CRIB[i] if CRIB[i] >= 0 else opts[i, np.random.randint(0, m)]
    free = np.array([i for i in range(97) if CRIB[i] < 0])
    cur = score(pt, QG); best = cur; bpt = pt.copy()
    for it in range(iters):
        T = 0.4 * (1 - it / iters) + 0.003
        i = free[np.random.randint(0, free.shape[0])]
        old = pt[i]; pt[i] = opts[i, np.random.randint(0, nopt[i])]
        new = score(pt, QG)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new
            if cur > best:
                best = cur; bpt[:] = pt
        else:
            pt[i] = old
    return best, bpt


def run(cta, label, restarts=10, iters=300000, strict=True):
    A = allowed(cta, strict)
    outs = []
    for r in range(restarts):
        b, pt = anneal(A, CRIB, QG, iters, 300 + r)
        s = "".join(AZ[x] for x in pt)
        outs.append((b, float(wseg(s)[0]), s))
    outs.sort(reverse=True)
    nc = [i for i in range(97) if CRIB[i] < 0]
    agree = np.mean([np.mean([outs[a][2][k] == outs[b][2][k] for k in nc]) for a in range(4) for b in range(a + 1, 4)])
    print(f"{label}: best q {outs[0][0]:.3f} word {max(o[1] for o in outs):.3f} top-4 agreement {agree:.2f}\n   {outs[0][2]}\n   {outs[1][2]}", flush=True)
    return outs[0][0], max(o[1] for o in outs), agree


if __name__ == "__main__":
    A = allowed(CTA)
    print("Per-position allowed KRYPTOS letters (non-crib positions):")
    line = []
    for i in range(97):
        if CRIB[i] >= 0:
            line.append(f"{i}:[{CRIB_POS[i]}]")
        else:
            ks = "".join(AZ[p] for p in range(26) if A[i, p] and AZ[p] in KRY)
            line.append(f"{i}:{ks or '-'}")
    print(" ".join(line))
    print("free letters per position (mean):", np.mean([A[i].sum() for i in range(97) if CRIB[i] < 0]).round(1))
    real = run(CTA, "REAL")
    rng = np.random.default_rng(0); nc = np.array([i for i in range(97) if CRIB[i] < 0])
    nulls = []
    for k in range(5):
        a = CTA.copy(); a[nc] = rng.permutation(a[nc]); nulls.append(run(a, f"NULL{k}"))
    print("REAL", real, "\nNULLS", nulls)
