"""TEAM clock exp 13: Kryptos-tableau-style running key from city names: PA=CA=KX=X for every dictionary/lore
keyed alphabet X (fwd/rev, ~800k), rules vig/beau/var, all offsets fwd/rev, indicator free. Early-exit equality test."""
import sys, time, numpy as np
from numba import njit, prange
import weltzeit as w
from run_alphapairs import load_words, pos_table
from k4lib import keyed_alphabet, CT, CRIB_POS
CI = np.array(sorted(CRIB_POS)); PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI]); CLt = np.array([ord(CT[i]) - 65 for i in CI])


@njit(parallel=True, cache=True)
def sweep(TABS, STR, CI, PL, CL, minhit, out):
    nA = TABS.shape[0]; ns = STR.shape[0]; n = STR.shape[1] - 97
    flags = np.zeros((nA, 4), dtype=np.int64)
    for a in prange(nA):
        T = TABS[a]
        for s in range(ns):
            for rule in range(3):
                for o in range(n):
                    good = 0
                    v0 = 0
                    for t in range(CI.shape[0]):
                        ip = T[PL[t]]; ic = T[CL[t]]; ik = T[STR[s, o + CI[t]]]
                        if rule == 0: v = (ic - ip - ik) % 26
                        elif rule == 1: v = (ic + ip - ik) % 26
                        else: v = (ip - ic - ik) % 26
                        if t == 0: v0 = v
                        elif v != v0: break
                        good += 1
                    if good >= minhit:
                        flags[a, 0] = good; flags[a, 1] = s; flags[a, 2] = rule; flags[a, 3] = o
    return flags


if __name__ == "__main__":
    lore, words = load_words()
    cityw = sorted({w.norm(c) for v in w.VERSIONS for c, _, _ in w.cities(v)})
    ALS, seen = [], set()
    for wd in [""] + lore + cityw + words:
        for rev in (0, 1):
            al = keyed_alphabet(wd); al = al[::-1] if rev else al
            if al not in seen: seen.add(al); ALS.append((wd + ("~" if rev else ""), al))
    TABS = np.array([pos_table(a) for _, a in ALS])
    strs = []
    for ver in ("1997", "1990a"):
        s = "".join(w.norm(c) for c, _, _ in w.cities(ver))
        for d in (s, s[::-1]):
            e = (d + d)[:1100 + 97]
            strs.append([ord(c) - 65 for c in e[:1197]])
    STR = np.array(strs, dtype=np.int64)
    print("alphabets", len(ALS), "streams", STR.shape, flush=True)
    t = time.time()
    out = None
    flags = sweep(TABS, STR, CI, PL, CLt, 13, out)
    print("time", round(time.time() - t))
    hits = np.nonzero(flags[:, 0])[0]
    print("configs with >=13 consecutive-equal crib values:", len(hits))
    for a in hits[:20]: print(ALS[a][0], flags[a])
