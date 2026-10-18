"""Periodic Quagmire with ONE keyed alphabet (dictionary/lore keyword, fwd/rev) and the OTHER alphabet completely FREE.
side 0: X (PT alphabet) keyed, Y (CT) free: for crib positions i,j with i%p==j%p:  Y(C_j)-Y(C_i) = X(P_j)-X(P_i)
side 1: Y keyed, X free:                                                    X(P_j)-X(P_i) = Y(C_j)-Y(C_i)
Weighted union-find on 26 free-alphabet letters + injectivity. Vig/Var/Beaufort all covered via fwd+rev keyed alphabet.
Direct (no transposition). Random calibration with random permutations as the keyed alphabet."""
import sys, time
import numpy as np
from numba import njit, prange
sys.path.insert(0, '.')
from k4lib import CT, CRIB_POS, keyed_alphabet
from run_alphapairs import load_words, pos_table

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
CL = np.array([ord(CT[i]) - 65 for i in CI], dtype=np.int64)

@njit(cache=True)
def find(par, off, x):
    o = 0
    while par[x] != x:
        o += off[x]; x = par[x]
    return x, o % 26

@njit(cache=True)
def check(tab, side, p, PL, CL, CI):
    """tab: position table of the keyed alphabet. Returns True if consistent."""
    par = np.arange(26); off = np.zeros(26, np.int64)
    last = np.full(64, -1, np.int64)
    if side == 0:
        free = CL; known = PL
    else:
        free = PL; known = CL
    for t in range(CI.shape[0]):
        r = CI[t] % p
        s = last[r]
        last[r] = t
        if s < 0:
            continue
        a = free[s]; b = free[t]
        k = (tab[known[t]] - tab[known[s]]) % 26  # pos(b) - pos(a) = k
        ra, oa = find(par, off, a); rb, ob = find(par, off, b)
        if ra == rb:
            if (ob - oa - k) % 26 != 0:
                return False
        else:
            par[rb] = ra; off[rb] = (k + oa - ob) % 26
    # injectivity
    seen = np.full((26, 26), 0, np.int64)
    for x in range(26):
        r, o = find(par, off, x)
        if seen[r, o]:
            return False
        seen[r, o] = 1
    return True

@njit(parallel=True, cache=True)
def scan(TABS, pmin, pmax, PL, CL, CI, out):
    for a in prange(TABS.shape[0]):
        for side in range(2):
            for p in range(pmin, pmax + 1):
                if check(TABS[a], side, p, PL, CL, CI):
                    out[a, side, p] = 1

if __name__ == '__main__':
    lore, words = load_words()
    names, tabs, seen = [], [], set()
    for w in [""] + lore + words:
        al = keyed_alphabet(w)
        for rev in (0, 1):
            a = al[::-1] if rev else al
            if a in seen: continue
            seen.add(a); names.append(w + ('~' if rev else '')); tabs.append(pos_table(a))
    TABS = np.array(tabs)
    print('alphabets', len(TABS), flush=True)
    PMAX = 26
    rng = np.random.default_rng(0)
    R = np.array([np.argsort(rng.permutation(26)) for _ in range(200000)])
    outR = np.zeros((len(R), 2, PMAX + 1), np.int8)
    scan(R, 1, PMAX, PL, CL, CI, outR)
    t = time.time()
    out = np.zeros((len(TABS), 2, PMAX + 1), np.int8)
    scan(TABS, 1, PMAX, PL, CL, CI, out)
    print('time', round(time.time() - t, 1), flush=True)
    for side in range(2):
        for p in range(1, PMAX + 1):
            rr = outR[:, side, p].mean()
            n = int(out[:, side, p].sum())
            print(f"side {side} ({'PT keyed, CT free' if side == 0 else 'CT keyed, PT free'}) p={p}: hits {n}  random rate {rr:.2e} -> expected {rr * len(TABS):.1f}", flush=True)
            if 0 < n <= 15:
                print('    ', [names[a] for a in np.nonzero(out[:, side, p])[0]])
