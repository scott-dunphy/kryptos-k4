"""P2: autokey on keyword-keyed alphabet pairs (direct, no transposition).
k_i (from crib) = rule(PA.index(P_i), CA.index(C_i)); key letter = PT[i-L] (PT-autokey) or CT[i-L] (CT-autokey);
key index = X.index(keyletter) with X in {PA, CA}; allow constant indicator shift s: k_i - keyidx_i == s for all checks.
"""
import numpy as np, time
from numba import njit, prange
from k4lib import CT, CRIB_POS, keyed_alphabet
from run_alphapairs import load_words, pos_table

N = 97
PTK = np.full(N, -1, dtype=np.int64)
for i, c in CRIB_POS.items():
    PTK[i] = ord(c) - 65
CTA = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
CI = np.array(sorted(CRIB_POS), dtype=np.int64)

@njit(parallel=True, cache=True)
def scan(TA, TB, PTK, CTA, CI, LPT, LCT, flags):
    nA = TA.shape[0]; nB = TB.shape[0]
    for b in prange(nB):
        for a in range(nA):
            for rule in range(3):
                for ksrc in range(2):
                    for mode in range(2):
                        Lmax = LPT if mode == 0 else LCT
                        for L in range(1, Lmax + 1):
                            s = -1; ok = True; n = 0
                            for t in range(CI.shape[0]):
                                i = CI[t]
                                if i - L < 0:
                                    continue
                                kl = PTK[i - L] if mode == 0 else CTA[i - L]
                                if kl < 0:
                                    continue
                                ip = TA[a, PTK[i]]; ic = TB[b, CTA[i]]
                                if rule == 0:
                                    k = (ic - ip) % 26
                                elif rule == 1:
                                    k = (ic + ip) % 26
                                else:
                                    k = (ip - ic) % 26
                                ki = TA[a, kl] if ksrc == 0 else TB[b, kl]
                                d = (k - ki) % 26
                                n += 1
                                if s == -1:
                                    s = d
                                elif d != s:
                                    ok = False
                                    break
                            if ok and n >= 10:
                                flags[b, a] += 1

if __name__ == "__main__":
    lore, words = load_words()
    def alphas(ws):
        res, seen = [], set()
        for w in ws:
            for rev in (0, 1):
                al = keyed_alphabet(w); al = al[::-1] if rev else al
                if al not in seen:
                    seen.add(al); res.append((w + ("~rev" if rev else ""), al))
        return res
    base = alphas(["", "KRYPTOS"]) + alphas(lore)
    allw = alphas(words)
    TA = np.array([pos_table(a) for _, a in base]); TB = np.array([pos_table(a) for _, a in allw])
    for label, X, Y, nx, ny in (("PT=base,CT=dict", TA, TB, base, allw), ("PT=dict,CT=base", TB, TA, allw, base),
                                ("PT=base,CT=base", TA, TA, base, base)):
        t = time.time()
        flags = np.zeros((Y.shape[0], X.shape[0]), dtype=np.int64)
        scan(X, Y, PTK, CTA, CI, 7, 40, flags)
        hits = np.argwhere(flags > 0)
        print(label, "hits", len(hits), round(time.time() - t, 1), "s", flush=True)
        for b, a in hits[:30]:
            print("   PT alph", nx[a][0], "CT alph", ny[b][0], flags[b, a])
