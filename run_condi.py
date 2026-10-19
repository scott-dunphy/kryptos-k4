"""CONDI-type keys (2026-10-18): shift of each letter = position of an earlier letter in the keyed alphabet.

ACA CONDI: keyed alphabet T; C_i = T[t(P_i) + t(P_{i-1}) + c] (t = position in T). Generalised here:
  t(C_i) -/+ t(P_i) = a * t(D_{i-lag}) + c      rule: Vig-like (C - P) or Beaufort-like (C + P)
  D = PT (CONDI proper, autokey-like) or CT (ciphertext-driven), lag 1..6, a = +1/-1, c free.
T = every dictionary + lore keyword alphabet, forward and reversed (+ AZ, KA).
Checks: every crib whose driver letter is known (PT driver: crib-internal pairs; CT driver: all 24).
Pass = all checkable residuals equal, allowing <= 1 fault; needs >= 12 checks. Chance ~ 26^-11 per config.
"""
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet
from run_alphapairs import load_words, pos_table

PTF = np.full(97, -1, dtype=np.int64)
for i, ch in CRIB_POS.items():
    PTF[i] = ord(ch) - 65
CI = np.array(sorted(CRIB_POS), dtype=np.int64)


@njit(parallel=True, cache=True)
def scan(TB, cti, ptf, out):
    # out[b] = best (checks - faults) code of a passing config, encoded; 0 if none
    for b in prange(TB.shape[0]):
        t = TB[b]
        vals = np.empty(24, dtype=np.int64)
        for drv in range(2):
            for lag in range(1, 7):
                for a in (1, -1):
                    for rule in range(2):
                        n = 0
                        for e in range(CI.shape[0]):
                            i = CI[e]
                            j = i - lag
                            if j < 0:
                                continue
                            d = ptf[j] if drv == 0 else cti[j]
                            if d < 0:
                                continue
                            tc = t[cti[i]]; tp = t[ptf[i]]
                            r = (tc - tp) if rule == 0 else (tc + tp)
                            vals[n] = (r - a * t[d]) % 26
                            n += 1
                        if n < 12:
                            continue
                        cnt = np.zeros(26, dtype=np.int64)
                        for k in range(n):
                            cnt[vals[k]] += 1
                        m = cnt.max()
                        if m >= n - 1:
                            out[b] = 1000000 + drv * 100000 + lag * 1000 + (a + 1) * 10 + rule


def alphabets():
    lore, words = load_words()
    seen, al = set(), []
    for w in ["", "KRYPTOS"] + words + lore:
        for rev in (0, 1):
            a = keyed_alphabet(w) if w else AZ
            a = a[::-1] if rev else a
            if a not in seen:
                seen.add(a); al.append((w or "AZ", rev, a))
    return al


def run(TB, ct):
    cti = np.array([ord(c) - 65 for c in ct], dtype=np.int64)
    out = np.zeros(TB.shape[0], dtype=np.int64)
    scan(TB, cti, PTF, out)
    return out


if __name__ == "__main__":
    al = alphabets()
    TB = np.array([pos_table(a) for _, _, a in al])
    print("alphabets", len(al), flush=True)
    # planted CONDI: SHADOW alphabet, PT driver lag 1, a=+1, Vig rule, c=7
    rng = np.random.default_rng(20261018)
    q = [x[0] for x in al].index("SHADOW")
    T = al[q][2]
    pt = [int(x) for x in rng.integers(0, 26, 97)]
    for i, ch in CRIB_POS.items():
        pt[i] = ord(ch) - 65
    pct = "".join(T[(T.index(AZ[pt[i]]) + (T.index(AZ[pt[i - 1]]) if i else 0) + 7) % 26] for i in range(97))
    print("planted SHADOW CONDI found:", bool(run(TB[q:q + 1], pct)[0]), flush=True)
    # planted CT-driven: KA, lag 2, Beaufort-like, a=-1
    q2 = [x[2] for x in al].index(KA)
    ct2 = [0] * 97
    for i in range(97):
        d = KA.index(AZ[ct2[i - 2]]) if i >= 2 else 0
        ct2[i] = AZ.index(KA[(-KA.index(AZ[pt[i]]) - d + 3) % 26])
    print("planted KA CT-driven lag2 found:", bool(run(TB[q2:q2 + 1], "".join(AZ[x] for x in ct2))[0]), flush=True)
    t0 = time.time()
    o = run(TB, CT)
    print("REAL hits", int((o > 0).sum()), "time", round(time.time() - t0, 1), flush=True)
    for h in np.nonzero(o)[0][:20]:
        print("  ", al[h][0], al[h][1], o[h])
    for s in range(3):
        o2 = run(TB, "".join(rng.permutation(list(CT))))
        print(f"NULL{s} hits", int((o2 > 0).sum()), flush=True)
