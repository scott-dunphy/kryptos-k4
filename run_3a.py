"""3A: key-fragment pattern mining. For alphabet pairs, derive crib key letters (13 at 21-33, 11 at 63-73),
render as letters via key alphabet X in {PA, CA, AZ}, score fragments with quadgrams (sum over both fragments).
Calibrate: same on random alphabet pairs -> threshold = best of null."""
import numpy as np, time
from numba import njit, prange
from k4lib import CT, CRIB_POS, keyed_alphabet, load_quadgrams
from run_alphapairs import load_words, pos_table

QG = load_quadgrams()
CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
CL = np.array([ord(CT[i]) - 65 for i in CI], dtype=np.int64)

@njit(parallel=True, cache=True)
def scan(TA, TB, AA, AB, PL, CL, QG, best, arg):
    # TA/TB: pos tables; AA/AB: letter-at-pos tables. best[b] = best score over a,rule,keyalph; arg packs a,rule,kx
    for b in prange(TB.shape[0]):
        kl = np.empty(24, dtype=np.int64)
        bs = -1e9; ba = -1
        for a in range(TA.shape[0]):
            for rule in range(3):
                for kx in range(3):
                    for t in range(24):
                        ip = TA[a, PL[t]]; ic = TB[b, CL[t]]
                        k = (ic - ip) % 26 if rule == 0 else ((ic + ip) % 26 if rule == 1 else (ip - ic) % 26)
                        kl[t] = AA[a, k] if kx == 0 else (AB[b, k] if kx == 1 else k)
                    s = 0.0
                    for t in range(10):  # fragment 1: t 0..12 -> quadgrams starting 0..9
                        s += QG[((kl[t]*26+kl[t+1])*26+kl[t+2])*26+kl[t+3]]
                    for t in range(13, 21):  # fragment 2: t 13..23 -> starts 13..20
                        s += QG[((kl[t]*26+kl[t+1])*26+kl[t+2])*26+kl[t+3]]
                    if s > bs:
                        bs = s; ba = (a * 3 + rule) * 3 + kx
        best[b] = bs / 18.0; arg[b] = ba

def tabs(alphas):
    T = np.array([pos_table(a) for a in alphas]); A = np.array([[ord(c) - 65 for c in a] for a in alphas])
    return T, A

if __name__ == "__main__":
    lore, words = load_words()
    def alphas(ws):
        res, seen = [], set()
        for w in ws:
            for rev in (0, 1):
                al = keyed_alphabet(w); al = al[::-1] if rev else al
                if al not in seen: seen.add(al); res.append((w + ("~rev" if rev else ""), al))
        return res
    base = alphas(["", "KRYPTOS"] + lore); allw = alphas(words)
    rng = np.random.default_rng(1)
    rand = [("rand", "".join(chr(65 + x) for x in rng.permutation(26))) for _ in range(len(allw) // 8)]
    TAb, AAb = tabs([a for _, a in base])
    for label, Y in (("NULL-random", rand), ("REAL-dict", allw)):
        TB, AB = tabs([a for _, a in Y])
        for role in ("PT=base", "CT=base"):
            t = time.time()
            best = np.zeros(len(Y)); arg = np.zeros(len(Y), dtype=np.int64)
            if role == "PT=base":
                scan(TAb, TB, AAb, AB, PL, CL, QG, best, arg)
            else:
                # swap roles: base alphabets as CT, Y as PT: call with TA=Y? keep loop over b = Y as PT
                scan(TB, TAb, AB, AAb, PL, CL, QG, best2 := np.zeros(len(base)), arg2 := np.zeros(len(base), dtype=np.int64))
                best, arg = best2, arg2
            o = np.argsort(-best)[:5]
            print(label, role, "n", len(best), "max", round(best.max(), 3), "p99.9", round(np.quantile(best, 0.999), 3), round(time.time() - t), "s", flush=True)
            for j in o:
                a, rule, kx = arg[j] // 9, (arg[j] // 3) % 3, arg[j] % 3
                if role == "PT=base":
                    print("   PT", base[a][0], "CT", Y[j][0], rule, kx, round(best[j], 3))
                else:
                    print("   PT", Y[a][0], "CT", base[j][0], rule, kx, round(best[j], 3))
