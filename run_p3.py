"""P3: interrupted key restarting at plaintext word boundaries (direct), on alphabet pairs.
Model A: restart at 21 (EAST), 25 (NORTHEAST), 63 (BERLIN), 69 (CLOCK): key at segment offset x equal across segments.
Model B: restarts at 25, 63, 69 only (EAST belongs to previous segment).
Model C: compound 'EASTNORTHEAST' one segment from 21; BERLIN 63; CLOCK 69.
Equalities on crib key values; FP per pair-rule ~26^-(#eq) (A:15, B:11, C:11)."""
import numpy as np, time
from numba import njit, prange
from k4lib import CT, CRIB_POS, keyed_alphabet
from run_alphapairs import load_words, pos_table

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
CL = np.array([ord(CT[i]) - 65 for i in CI], dtype=np.int64)
idx = {int(p): t for t, p in enumerate(CI)}
def eqs(starts):
    segs = []
    for s in starts:
        e = min([x for x in starts + [34, 74] if x > s] + [99])
        e = 34 if s < 34 and e > 34 else (74 if e > 74 else e)
        segs.append([idx[p] for p in range(s, e) if p in idx])
    pairs = []
    for a in range(len(segs)):
        for b in range(a + 1, len(segs)):
            for x in range(min(len(segs[a]), len(segs[b]))):
                pairs.append((segs[a][x], segs[b][x]))
    return np.array(pairs, dtype=np.int64)
MODELS = {"A": eqs([21, 25, 63, 69]), "B": eqs([25, 63, 69]), "C": eqs([21, 63, 69])}

@njit(parallel=True, cache=True)
def scan(TA, TB, PL, CL, E, flags):
    for b in prange(TB.shape[0]):
        k = np.empty(PL.shape[0], dtype=np.int64)
        for a in range(TA.shape[0]):
            for rule in range(3):
                for t in range(PL.shape[0]):
                    ip = TA[a, PL[t]]; ic = TB[b, CL[t]]
                    k[t] = (ic - ip) % 26 if rule == 0 else ((ic + ip) % 26 if rule == 1 else (ip - ic) % 26)
                ok = True
                for e in range(E.shape[0]):
                    if k[E[e, 0]] != k[E[e, 1]]:
                        ok = False; break
                if ok:
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
    base = alphas(["", "KRYPTOS"]) + alphas(lore); allw = alphas(words)
    TA = np.array([pos_table(a) for _, a in base]); TB = np.array([pos_table(a) for _, a in allw])
    for m, E in MODELS.items():
        for label, X, Y in (("base/dict", TA, TB), ("dict/base", TB, TA)):
            t = time.time(); flags = np.zeros((Y.shape[0], X.shape[0]), dtype=np.int64)
            scan(X, Y, PL, CL, E, flags)
            print("model", m, "eqs", len(E), label, "hits", int((flags > 0).sum()), round(time.time() - t, 1), "s", flush=True)
