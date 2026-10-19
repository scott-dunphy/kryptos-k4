"""Lore words translated into Latin, German, Russian, Greek, Arabic, French, Italian, Spanish, Egyptian (romanized;
data/lore_translations.py, 478 words) through the keyword models (2026-10-18). Precedent: the Cyrillic Projector
used the Russian keyword TEN' (shadow) for its alphabet and MEDUSA-derived letters as its key.
  M1 Sanborn signature, exact: tableau = keyed alphabet of word w1 (PT, CT, key all indexed in it), key = word w2
     repeated (every phase), Vig/Beau/Var; hit if <= 3 of 24 cribs mismatch.
  M2 same tableau, ANY periodic key p 1..24 (run_tableau_all kernel, >= 4 repeat checks).
  M3 Quagmire: PT alphabet keyed(w1), CT alphabet keyed(w2), any periodic key p 1..24, >= 4 repeat checks.
  M4 mask + pinned table: keyword w on KA/AZ tableau + one free substitution chart (run_pinned_table, exact / 1 slip).
  M5 keyword chart + aperiodic nuance key (run_chartguess), report max cribs inside window vs random charts.
Words: translations + English lore + KRYPTOS/AZ. Null: shuffled CT. Planted: Projector-style UMBRA/CLAVIS.
"""
import sys
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet
from run_alphapairs import load_words, pos_table
sys.path.insert(0, "data")
from lore_translations import WORDS

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
LMAX = 32


def wordlist():
    lore, _ = load_words()
    return sorted(set(WORDS) | set(lore) | {"KRYPTOS", "PALIMPSEST", "ABSCISSA", "MEDUSA"})


def alphabets(words):
    seen, names, al = set(), [], []
    for w in [""] + words:
        for rev in (0, 1):
            a = keyed_alphabet(w) if w else AZ
            a = a[::-1] if rev else a
            if a not in seen:
                seen.add(a); names.append((w or "AZ") + (" rev" if rev else "")); al.append(a)
    return names, al


def keyarr(words):
    K = np.zeros((len(words), LMAX), dtype=np.int64); L = np.zeros(len(words), dtype=np.int64)
    for i, w in enumerate(words):
        w = w[:LMAX]; L[i] = len(w); K[i, :len(w)] = [ord(c) - 65 for c in w]
    return K, L


@njit(parallel=True, cache=True)
def m1(TB, KW, KL, cti, out):
    # out[b, q] = min mismatches over phase/rule
    for b in prange(TB.shape[0]):
        t = TB[b]
        for q in range(KW.shape[0]):
            L = KL[q]
            best = 99
            for f in range(L):
                for rule in range(3):
                    mm = 0
                    for e in range(CI.shape[0]):
                        i = CI[e]
                        tc = t[cti[i]]; tp = t[PL[e]]; tk = t[KW[q, (i + f) % L]]
                        if rule == 0:
                            ok = (tc - tp - tk) % 26 == 0
                        elif rule == 1:
                            ok = (tc + tp - tk) % 26 == 0
                        else:
                            ok = (tp - tc - tk) % 26 == 0
                        if not ok:
                            mm += 1
                            if mm >= best:
                                break
                    if mm < best:
                        best = mm
            out[b, q] = best


@njit(parallel=True, cache=True)
def m3(TP, TC, cti, out):
    # Quagmire: k_e = tc(C) - tp(P) (and Beaufort tc+tp); periodic residue consistency, out = best repeat checks
    for a in prange(TP.shape[0]):
        key = np.empty(32, dtype=np.int64); k = np.empty(24, dtype=np.int64)
        for b in range(TC.shape[0]):
            best = 0
            for rule in range(2):
                for e in range(24):
                    ip = TP[a, PL[e]]; ic = TC[b, cti[CI[e]]]
                    k[e] = (ic - ip) % 26 if rule == 0 else (ic + ip) % 26
                for p in range(1, 25):
                    for r in range(p):
                        key[r] = -1
                    ok = True; distinct = 0
                    for e in range(24):
                        r = CI[e] % p
                        if key[r] == -1:
                            key[r] = k[e]; distinct += 1
                        elif key[r] != k[e]:
                            ok = False; break
                    if ok and 24 - distinct > best:
                        best = 24 - distinct
            out[a, b] = best


def run_all(ct, names, al, words, show=True):
    cti = np.array([ord(c) - 65 for c in ct], dtype=np.int64)
    TB = np.array([pos_table(a) for a in al])
    KW, KL = keyarr(words)
    o1 = np.zeros((len(al), len(words)), dtype=np.int64)
    m1(TB, KW, KL, cti, o1)
    from run_tableau_all import scan as m2scan
    CL = np.array([ord(ct[i]) - 65 for i in CI])
    o2 = np.zeros(len(al), dtype=np.int64)
    m2scan(TB, PL, CL, CI, o2)
    o3 = np.zeros((len(al), len(al)), dtype=np.int64)
    m3(TB, TB, cti, o3)
    import run_pinned_table as RP
    KW4 = np.zeros((len(words), RP.LMAXW), dtype=np.int64); L4 = np.zeros(len(words), dtype=np.int64)
    for i, w in enumerate(words):
        w = w[:RP.LMAXW]; L4[i] = len(w); KW4[i, :len(w)] = [ord(c) - 65 for c in w]
    c4, h4 = RP.run(cti, KW4, L4)
    import run_chartguess as CG
    S = []
    for a in al:
        for B in (AZ, KA):
            sig = [0] * 26
            for x, y in zip(B, a):
                sig[ord(x) - 65] = ord(y) - 65
            S.append(sig); S.append(list(np.argsort(sig)))
    S = np.array(S, dtype=np.int64)
    b5 = CG.run(S, ct)
    res = {"M1 min mismatches": int(o1.min()), "M1 hits<=3": int((o1 <= 3).sum()),
           "M2 hits": int((o2 > 0).sum()), "M3 max checks": int(o3.max()), "M3 >=4": int((o3 >= 4).sum()),
           "M4 exact": int(c4[0]), "M4 1slip": int(c4[1]),
           "M5 max w5": int(b5[..., 0].max()), "M5 max w7": int(b5[..., 1].max())}
    if show:
        i, j = np.unravel_index(np.argmin(o1), o1.shape)
        res["M1 best"] = f"{names[i]} / {words[j]}"
        if o3.max() >= 4:
            a, b = np.unravel_index(np.argmax(o3), o3.shape); res["M3 best"] = f"{names[a]} x {names[b]}"
    return res


if __name__ == "__main__":
    words = wordlist()
    names, al = alphabets(words)
    print("words", len(words), "alphabets", len(al), flush=True)
    rng = np.random.default_rng(20261018)
    # planted Projector style: tableau UMBRA, key CLAVIS, Vigenere
    T = keyed_alphabet("UMBRA"); key = "CLAVIS"
    pt = [AZ[x] for x in rng.integers(0, 26, 97)]
    for i, ch in CRIB_POS.items():
        pt[i] = ch
    pct = "".join(T[(T.index(p) + T.index(key[i % 6])) % 26] for i, p in enumerate(pt))
    print("PLANTED UMBRA/CLAVIS:", run_all(pct, names, al, words), flush=True)
    t = time.time()
    print("REAL:", run_all(CT, names, al, words), round(time.time() - t, 1), "s", flush=True)
    for s in range(3):
        print(f"NULL{s}:", run_all("".join(rng.permutation(list(CT))), names, al, words, show=False), flush=True)
    R = [ "".join(AZ[x] for x in rng.permutation(26)) for _ in range(len(al)) ]
    print("REAL with random alphabets (M3/M5 baseline):", run_all(CT, ["rnd"] * len(R), R, words, show=False), flush=True)
