"""Fable #3: chart-structured decode. Model C_i = sigma(P_i) + k_i (AZ arithmetic), sigma a bijection,
k_i in KSET (one-sided 0..4, or -2..2). Cribs fixed (64, 71 exempt from consistency).
Outer SA over sigma (swap moves); inner exact Viterbi over plaintext with quadgram scores, candidates per position
= sigma^-1(C_i - k) for k in KSET. Penalty for crib inconsistency. Restart agreement + non-crib-shuffled null.
"""
import sys
import numpy as np
from numba import njit
from k4lib import CT, CRIB_POS, load_quadgrams, AZ

QG = load_quadgrams().astype(np.float64)
CRIB = np.full(97, -1, dtype=np.int64)
for i, c in CRIB_POS.items():
    CRIB[i] = ord(c) - 65
EXEMPT = np.zeros(97, dtype=np.int64); EXEMPT[64] = 1; EXEMPT[71] = 1


@njit(cache=True)
def viterbi(ct, sinv, KSET, CRIB, QG):
    """Return best plaintext score (sum quadgrams) and plaintext. Candidates per position: list of letters."""
    nk = KSET.shape[0]
    n = 97
    cand = np.empty((n, nk), dtype=np.int64)
    ncand = np.empty(n, dtype=np.int64)
    for i in range(n):
        if CRIB[i] >= 0:
            cand[i, 0] = CRIB[i]; ncand[i] = 1
        else:
            m = 0
            for j in range(nk):
                p = sinv[(ct[i] - KSET[j]) % 26]
                dup = False
                for q in range(m):
                    if cand[i, q] == p:
                        dup = True
                if not dup:
                    cand[i, m] = p; m += 1
            ncand[i] = m
    # DP over triples (a,b,c) indices at positions i-2,i-1,i
    NEG = -1e18
    K = nk
    dp = np.full((K, K, K), NEG)
    bp = np.zeros((n, K, K, K), dtype=np.int64)
    for a in range(ncand[0]):
        for b in range(ncand[1]):
            for c in range(ncand[2]):
                dp[a, b, c] = 0.0
    for i in range(3, n):
        nd = np.full((K, K, K), NEG)
        for b in range(ncand[i - 2]):
            for c in range(ncand[i - 1]):
                for d in range(ncand[i]):
                    best = NEG; arg = 0
                    for a in range(ncand[i - 3]):
                        if dp[a, b, c] <= NEG / 2:
                            continue
                        q = ((cand[i - 3, a] * 26 + cand[i - 2, b]) * 26 + cand[i - 1, c]) * 26 + cand[i, d]
                        v = dp[a, b, c] + QG[q]
                        if v > best:
                            best = v; arg = a
                    nd[b, c, d] = best; bp[i, b, c, d] = arg
        dp = nd
    best = NEG; bb = 0; bc = 0; bd = 0
    for b in range(ncand[n - 3]):
        for c in range(ncand[n - 2]):
            for d in range(ncand[n - 1]):
                if dp[b, c, d] > best:
                    best = dp[b, c, d]; bb = b; bc = c; bd = d
    pt = np.empty(n, dtype=np.int64)
    idx = np.empty(n, dtype=np.int64)
    idx[n - 3] = bb; idx[n - 2] = bc; idx[n - 1] = bd
    for i in range(n - 1, 2, -1):
        idx[i - 3] = bp[i, idx[i - 2], idx[i - 1], idx[i]]
    for i in range(n):
        pt[i] = cand[i, idx[i]]
    return best / 94.0, pt


@njit(cache=True)
def crib_pen(ct, sig, KSET, CRIB, EXEMPT):
    pen = 0
    for i in range(97):
        if CRIB[i] < 0 or EXEMPT[i]:
            continue
        d = (ct[i] - sig[CRIB[i]]) % 26
        ok = False
        for j in range(KSET.shape[0]):
            if (KSET[j] % 26) == d:
                ok = True
        if not ok:
            pen += 1
    return pen


@njit(cache=True)
def anneal(ct, KSET, CRIB, EXEMPT, QG, iters, seed):
    np.random.seed(seed)
    sig = np.random.permutation(26)
    sinv = np.empty(26, dtype=np.int64)
    for x in range(26):
        sinv[sig[x]] = x
    q, pt = viterbi(ct, sinv, KSET, CRIB, QG)
    cur = q - 0.3 * crib_pen(ct, sig, KSET, CRIB, EXEMPT)
    best = cur; bsig = sig.copy(); bpt = pt.copy()
    for it in range(iters):
        T = 0.15 * (1 - it / iters) + 0.002
        a = np.random.randint(0, 26); b = np.random.randint(0, 26)
        sig[a], sig[b] = sig[b], sig[a]
        sinv[sig[a]] = a; sinv[sig[b]] = b
        q, pt2 = viterbi(ct, sinv, KSET, CRIB, QG)
        new = q - 0.3 * crib_pen(ct, sig, KSET, CRIB, EXEMPT)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new
            if cur > best:
                best = cur; bsig[:] = sig; bpt[:] = pt2
        else:
            sig[a], sig[b] = sig[b], sig[a]
            sinv[sig[a]] = a; sinv[sig[b]] = b
    return best, bsig, bpt


def run(ct, KSET, label, restarts=8, iters=6000):
    from wordscore import wseg
    outs = []
    for r in range(restarts):
        b, sig, pt = anneal(ct, KSET, CRIB, EXEMPT, QG, iters, 1000 + r)
        pen = crib_pen(ct, sig, KSET, CRIB, EXEMPT)
        s = "".join(AZ[x] for x in pt)
        outs.append((b, pen, s, float(wseg(s)[0])))
    clean = [o for o in outs if o[1] == 0] or outs
    bq = max(o[0] for o in clean)
    bw = max(o[3] for o in clean)
    nc = [i for i in range(97) if CRIB[i] < 0]
    texts = [o[2] for o in clean]
    agree = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            agree.append(np.mean([texts[i][k] == texts[j][k] for k in nc]))
    ag = float(np.mean(agree)) if agree else 0.0
    top = max(clean, key=lambda o: o[0])
    print(f"{label} K={KSET.tolist()}: clean {sum(o[1]==0 for o in outs)}/{restarts} best q {bq:.3f} best word {bw:.3f} "
          f"restart agreement {ag:.2f}\n    {top[2]}", flush=True)
    return bq, bw, ag


if __name__ == "__main__":
    cta = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
    nc = np.array([i for i in range(97) if CRIB[i] < 0])
    rng = np.random.default_rng(5)
    for KSET in (np.array([0, 1, 2, 3, 4]), np.array([-2, -1, 0, 1, 2])):
        real = run(cta, KSET, "REAL")
        nulls = []
        for k in range(3):
            a = cta.copy(); a[nc] = rng.permutation(a[nc])
            nulls.append(run(a, KSET, f"NULL{k}"))
        print("SUMMARY", KSET.tolist(), "real", real, "nulls", nulls, flush=True)
