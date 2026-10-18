"""Two stacked tableau layers with different alphabets (direct, no transposition).
Layer 1: keyword W (from dictionary/lore), tableau T1 in {AZ, KA}, rule r1 in {vig, beau, var}, key letter indexed in T1.
Layer 2: unknown periodic key p2 in 1..22, tableau T2 in {AZ, KA}, rule r2.
Order 0: C = L2(L1(P)): Y_i = L1enc(P_i)  -> k2 = f2(Y_i, C_i) must be periodic.
Order 1: C = L1(L2(P)): Y_i = L1dec(C_i)  -> k2 = f2(P_i, Y_i) must be periodic.
Same-alphabet pairs (T1 == T2) collapse to single periodic layers of period lcm -> skip T1 == T2 with vig/var mix? kept for simplicity.
"""
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, AZ, KA
from run_alphapairs import load_words

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
CL = np.array([ord(CT[i]) - 65 for i in CI], dtype=np.int64)
TABS = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)  # pos of letter
ALPH = np.array([[ord(c) - 65 for c in AZ], [ord(c) - 65 for c in KA]], dtype=np.int64)  # letter at pos


@njit(cache=True)
def enc(rule, T, k, x, TABS, ALPH):
    # encrypt letter x (AZ idx) with key index k in tableau T
    ip = TABS[T, x]
    if rule == 0:
        return ALPH[T, (ip + k) % 26]
    elif rule == 1:
        return ALPH[T, (k - ip) % 26]
    return ALPH[T, (ip - k) % 26]


@njit(cache=True)
def dec(rule, T, k, c, TABS, ALPH):
    ic = TABS[T, c]
    if rule == 0:
        return ALPH[T, (ic - k) % 26]
    elif rule == 1:
        return ALPH[T, (k - ic) % 26]
    return ALPH[T, (ic + k) % 26]


@njit(cache=True)
def keyval(rule, T, p, c, TABS):
    ip = TABS[T, p]; ic = TABS[T, c]
    if rule == 0:
        return (ic - ip) % 26
    elif rule == 1:
        return (ic + ip) % 26
    return (ip - ic) % 26


@njit(parallel=True, cache=True)
def scan(words, wlen, PL, CL, CI, TABS, ALPH, pmax, flags):
    nw = words.shape[0]; nc = PL.shape[0]
    for w in prange(nw):
        Y = np.empty(nc, dtype=np.int64)
        k2 = np.empty(nc, dtype=np.int64)
        key = np.empty(32, dtype=np.int64)
        L = wlen[w]
        for T1 in range(2):
            for r1 in range(3):
                for T2 in range(2):
                    for r2 in range(3):
                        for order in range(2):
                            for t in range(nc):
                                k1 = TABS[T1, words[w, CI[t] % L]]
                                if order == 0:
                                    Y[t] = enc(r1, T1, k1, PL[t], TABS, ALPH)
                                    k2[t] = keyval(r2, T2, Y[t], CL[t], TABS)
                                else:
                                    Y[t] = dec(r1, T1, k1, CL[t], TABS, ALPH)
                                    k2[t] = keyval(r2, T2, PL[t], Y[t], TABS)
                            for p in range(1, pmax + 1):
                                for r in range(p):
                                    key[r] = -1
                                ok = True; distinct = 0
                                for t in range(nc):
                                    r = CI[t] % p
                                    if key[r] == -1:
                                        key[r] = k2[t]; distinct += 1
                                    elif key[r] != k2[t]:
                                        ok = False; break
                                if ok and nc - distinct >= 6:
                                    flags[w] = (((T1 * 3 + r1) * 2 + T2) * 3 + r2) * 2 * 32 + order * 32 + p
                                    break


if __name__ == "__main__":
    lore, words = load_words()
    words = sorted(set(w for w in words + lore if len(w) <= 14))
    W = np.zeros((len(words), 14), dtype=np.int64); wl = np.zeros(len(words), dtype=np.int64)
    for i, w in enumerate(words):
        wl[i] = len(w)
        for j, c in enumerate(w):
            W[i, j] = ord(c) - 65
    flags = np.zeros(len(words), dtype=np.int64)
    t = time.time()
    scan(W, wl, PL, CL, CI, TABS, ALPH, 22, flags)
    hits = np.nonzero(flags)[0]
    print("words", len(words), "hits", len(hits), round(time.time() - t, 1), "s")
    for h in hits[:40]:
        f = int(flags[h]); p = f % 32; order = (f // 32) % 2; rest = f // 64
        print(words[h], "p2", p, "order", order, "code", rest)
