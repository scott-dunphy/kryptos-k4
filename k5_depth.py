"""K5 depth attack tool (ready for when K5 ciphertext is released).
Model (Fable theory): both texts share sigma (bijection) and position key k_i in KSET:
   C4_i = sigma(P4_i) + k_i ,  C5_i = sigma(P5_i) + k_i   (AZ arithmetic).
Choosing k_i fixes both plaintext letters at once -> joint Viterbi over k choices, score = qg(P4)+qg(P5);
outer SA over sigma. K4 cribs fixed (and any K5 cribs). Also reports D_i = C4_i - C5_i (key cancels).
Usage: python k5_depth.py <K5_CIPHERTEXT>   (or import and call solve()).
"""
import sys
import numpy as np
from numba import njit
from k4lib import CT as K4, CRIB_POS, load_quadgrams, AZ

QG = load_quadgrams().astype(np.float64)


@njit(cache=True)
def viterbi2(c4, c5, sinv, KSET, cr4, cr5, QG):
    n = c4.shape[0]; K = KSET.shape[0]
    p4 = np.empty((n, K), dtype=np.int64); p5 = np.empty((n, K), dtype=np.int64)
    pen = np.zeros((n, K))
    for i in range(n):
        for j in range(K):
            a = sinv[(c4[i] - KSET[j]) % 26]; b = sinv[(c5[i] - KSET[j]) % 26]
            p4[i, j] = a; p5[i, j] = b
            if cr4[i] >= 0 and a != cr4[i]:
                pen[i, j] -= 6.0
            if cr5[i] >= 0 and b != cr5[i]:
                pen[i, j] -= 6.0
    NEG = -1e18
    dp = np.full((K, K, K), NEG)
    bp = np.zeros((n, K, K, K), dtype=np.int64)
    for a in range(K):
        for b in range(K):
            for c in range(K):
                dp[a, b, c] = pen[0, a] + pen[1, b] + pen[2, c]
    for i in range(3, n):
        nd = np.full((K, K, K), NEG)
        for b in range(K):
            for c in range(K):
                for d in range(K):
                    best = NEG; arg = 0
                    for a in range(K):
                        v0 = dp[a, b, c]
                        if v0 <= NEG / 2:
                            continue
                        q4 = ((p4[i - 3, a] * 26 + p4[i - 2, b]) * 26 + p4[i - 1, c]) * 26 + p4[i, d]
                        q5 = ((p5[i - 3, a] * 26 + p5[i - 2, b]) * 26 + p5[i - 1, c]) * 26 + p5[i, d]
                        v = v0 + QG[q4] + QG[q5] + pen[i, d]
                        if v > best:
                            best = v; arg = a
                    nd[b, c, d] = best; bp[i, b, c, d] = arg
        dp = nd
    best = NEG; bb = 0; bc = 0; bd = 0
    for b in range(K):
        for c in range(K):
            for d in range(K):
                if dp[b, c, d] > best:
                    best = dp[b, c, d]; bb = b; bc = c; bd = d
    idx = np.empty(n, dtype=np.int64); idx[n - 3] = bb; idx[n - 2] = bc; idx[n - 1] = bd
    for i in range(n - 1, 2, -1):
        idx[i - 3] = bp[i, idx[i - 2], idx[i - 1], idx[i]]
    o4 = np.empty(n, dtype=np.int64); o5 = np.empty(n, dtype=np.int64)
    for i in range(n):
        o4[i] = p4[i, idx[i]]; o5[i] = p5[i, idx[i]]
    return best / (2 * (n - 3)), o4, o5


@njit(cache=True)
def anneal2(c4, c5, KSET, cr4, cr5, QG, iters, seed):
    np.random.seed(seed)
    sig = np.random.permutation(26); sinv = np.empty(26, dtype=np.int64)
    for x in range(26):
        sinv[sig[x]] = x
    cur, a4, a5 = viterbi2(c4, c5, sinv, KSET, cr4, cr5, QG)
    best = cur; b4 = a4.copy(); b5 = a5.copy(); bs = sig.copy()
    for it in range(iters):
        T = 0.15 * (1 - it / iters) + 0.002
        a = np.random.randint(0, 26); b = np.random.randint(0, 26)
        sig[a], sig[b] = sig[b], sig[a]; sinv[sig[a]] = a; sinv[sig[b]] = b
        new, n4, n5 = viterbi2(c4, c5, sinv, KSET, cr4, cr5, QG)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new
            if cur > best:
                best = cur; b4[:] = n4; b5[:] = n5; bs[:] = sig
        else:
            sig[a], sig[b] = sig[b], sig[a]; sinv[sig[a]] = a; sinv[sig[b]] = b
    return best, bs, b4, b5


def solve(k5, kset=(0, 1, 2, 3, 4), restarts=8, iters=30000, k5_cribs=None):
    c4 = np.array([ord(c) - 65 for c in K4], dtype=np.int64)
    c5 = np.array([ord(c) - 65 for c in k5], dtype=np.int64)
    cr4 = np.full(97, -1, dtype=np.int64)
    for i, c in CRIB_POS.items():
        cr4[i] = ord(c) - 65
    cr5 = np.full(97, -1, dtype=np.int64)
    for i, c in (k5_cribs or {}).items():
        cr5[i] = ord(c) - 65
    D = "".join(AZ[(a - b) % 26] for a, b in zip(c4, c5))
    print("D = C4 - C5 (A = identical position):", D)
    res = []
    for r in range(restarts):
        b, s, o4, o5 = anneal2(c4, c5, np.array(kset), cr4, cr5, QG, iters, 500 + r)
        res.append((b, "".join(AZ[x] for x in o4), "".join(AZ[x] for x in o5)))
    res.sort(reverse=True)
    for b, t4, t5 in res[:3]:
        print(f"score {b:.3f}\n  K4: {t4}\n  K5: {t5}")
    return res


if __name__ == "__main__":
    if len(sys.argv) > 1:
        solve(sys.argv[1].upper())


# ---- period-31 column-key mode: k_i = KC[(i + off) % 31] (copper column), SA over sigma and KC ----
@njit(cache=True)
def score_col(c4, c5, sinv, KC, off, cr4, cr5, QG):
    n = c4.shape[0]
    p4 = np.empty(n, dtype=np.int64); p5 = np.empty(n, dtype=np.int64)
    pen = 0.0
    for i in range(n):
        k = KC[(i + off) % 31]
        p4[i] = sinv[(c4[i] - k) % 26]; p5[i] = sinv[(c5[i] - k) % 26]
        if cr4[i] >= 0 and p4[i] != cr4[i]:
            pen -= 6.0
        if cr5[i] >= 0 and p5[i] != cr5[i]:
            pen -= 6.0
    s = 0.0
    for i in range(n - 3):
        s += QG[((p4[i] * 26 + p4[i + 1]) * 26 + p4[i + 2]) * 26 + p4[i + 3]]
        s += QG[((p5[i] * 26 + p5[i + 1]) * 26 + p5[i + 2]) * 26 + p5[i + 3]]
    return (s + pen) / (2 * (n - 3)), p4, p5


@njit(cache=True)
def anneal_col(c4, c5, KSET, off, cr4, cr5, QG, iters, seed):
    np.random.seed(seed)
    sig = np.random.permutation(26); sinv = np.empty(26, dtype=np.int64)
    for x in range(26):
        sinv[sig[x]] = x
    KC = np.empty(31, dtype=np.int64)
    for j in range(31):
        KC[j] = KSET[np.random.randint(0, KSET.shape[0])]
    cur, a4, a5 = score_col(c4, c5, sinv, KC, off, cr4, cr5, QG)
    best = cur; b4 = a4.copy(); b5 = a5.copy()
    for it in range(iters):
        T = 0.15 * (1 - it / iters) + 0.002
        if np.random.random() < 0.5:
            a = np.random.randint(0, 26); b = np.random.randint(0, 26)
            sig[a], sig[b] = sig[b], sig[a]; sinv[sig[a]] = a; sinv[sig[b]] = b
            mv = 0
        else:
            j = np.random.randint(0, 31); old = KC[j]; KC[j] = KSET[np.random.randint(0, KSET.shape[0])]
            mv = 1
        new, n4, n5 = score_col(c4, c5, sinv, KC, off, cr4, cr5, QG)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new
            if cur > best:
                best = cur; b4[:] = n4; b5[:] = n5
        else:
            if mv == 0:
                sig[a], sig[b] = sig[b], sig[a]; sinv[sig[a]] = a; sinv[sig[b]] = b
            else:
                KC[j] = old
    return best, b4, b5
