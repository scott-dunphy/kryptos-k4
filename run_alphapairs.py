"""Alphabet-pair diagnosis (direct, no transposition).

For plain alphabet PA and cipher alphabet CA (keyword-keyed, fwd or reversed), compute 24 crib key values
k_i = CA.index(C_i) - PA.index(P_i) (Vig; Beaufort/Variant via sign changes). Flag:
  (a) cyclic range of key values < b  (small digit key, Gromark/Gronsfeld-like), b in 5..12
  (b) consistent with period p<=30 (Quagmire with dictionary-keyed alphabets)
  (c) few distinct key values (<=6)
Random baselines: (a) b=10 ~ 26*(10/26)^24 ~ 3e-9 per pair-rule.
"""
import sys
import numpy as np
from numba import njit
from k4lib import CT, CRIB_POS, AZ, keyed_alphabet

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
CL = np.array([ord(CT[i]) - 65 for i in CI], dtype=np.int64)


def load_words():
    lore = ("KRYPTOS PALIMPSEST ABSCISSA IQLUSION UNDERGRUUND UNDERGROUND BERLIN CLOCK WELTZEITUHR "
            "MENGENLEHREUHR ALEXANDERPLATZ SANBORN SCHEIDT WEBSTER LANGLEY SHADOW CARTER TUTANKHAMUN "
            "EGYPT CAIRO BERLINWALL WORLDCLOCK URANIA LAYERTWO VIRGINIA MESSAGE DELIVER COMPASS LODESTONE "
            "ANTIPODES HIRSHHORN CIA KGB STASI CHECKPOINT CHARLIE MAGNETIC NORTHEAST EAST TIME ZEIT "
            "WELT UHR HOUR LUCID MEMORY INVISIBLE SECRET TOMB CANDLE MIST SLOWLY DESPERATELY").split()
    words = set(lore)
    with open("/usr/share/dict/words") as f:
        for w in f:
            w = w.strip().upper()
            if 3 <= len(w) <= 14 and w.isalpha() and w.isascii():
                words.add(w)
    return lore, sorted(words)


def pos_table(alpha):
    t = np.empty(26, dtype=np.int64)
    for i, c in enumerate(alpha):
        t[ord(c) - 65] = i
    return t


@njit(cache=True)
def diag(PT_tabs, CT_tabs, PL, CL, CI, out):
    """PT_tabs: (A,26) position tables; CT_tabs: (B,26). For each pair & rule, compute stats.
    out rows: a, b, rule, cyclic_range, distinct, min_period_consistent(0 if none<=30)."""
    nA = PT_tabs.shape[0]; nB = CT_tabs.shape[0]; nc = PL.shape[0]
    cnt = 0
    k = np.empty(nc, dtype=np.int64)
    seen = np.empty(26, dtype=np.int64)
    key = np.empty(32, dtype=np.int64)
    for a in range(nA):
        for b in range(nB):
            for rule in range(3):
                for t in range(nc):
                    ip = PT_tabs[a, PL[t]]; ic = CT_tabs[b, CL[t]]
                    if rule == 0:
                        k[t] = (ic - ip) % 26
                    elif rule == 1:
                        k[t] = (ic + ip) % 26
                    else:
                        k[t] = (ip - ic) % 26
                for x in range(26):
                    seen[x] = 0
                for t in range(nc):
                    seen[k[t]] = 1
                distinct = 0
                for x in range(26):
                    distinct += seen[x]
                # cyclic range = 26 - longest run of unseen (circular)
                longest = 0; run = 0
                for x in range(52):
                    if seen[x % 26] == 0:
                        run += 1
                        if run > longest:
                            longest = run
                    else:
                        run = 0
                if longest > 26:
                    longest = 26
                crange = 26 - longest
                per = 0
                for p in range(1, 31):
                    for r in range(p):
                        key[r] = -1
                    ok = True
                    for t in range(nc):
                        r = CI[t] % p
                        if key[r] == -1:
                            key[r] = k[t]
                        elif key[r] != k[t]:
                            ok = False
                            break
                    if ok:
                        per = p
                        break
                if (crange <= 13 or distinct <= 8 or (per > 0 and per <= 22)) and cnt < out.shape[0]:
                    out[cnt, 0] = a; out[cnt, 1] = b; out[cnt, 2] = rule
                    out[cnt, 3] = crange; out[cnt, 4] = distinct; out[cnt, 5] = per
                    cnt += 1
    return cnt


if __name__ == "__main__":
    lore, words = load_words()
    def alphas(ws):
        res, seen = [], set()
        for w in ws:
            for rev in (0, 1):
                al = keyed_alphabet(w)
                if rev:
                    al = al[::-1]
                if al not in seen:
                    seen.add(al); res.append((w + ("~rev" if rev else ""), al))
        return res
    base = alphas(["", "KRYPTOS"]) + alphas(lore)
    allw = alphas(words)
    print("base alphabets", len(base), "dict alphabets", len(allw), flush=True)
    names_A = [n for n, _ in base]; tabs_A = np.array([pos_table(a) for _, a in base])
    names_B = [n for n, _ in allw]; tabs_B = np.array([pos_table(a) for _, a in allw])
    out = np.zeros((1_000_000, 6), dtype=np.int64)
    rules = ["vig", "beau", "var"]
    for label, TA, NA, TB, NB in (("PT=base,CT=dict", tabs_A, names_A, tabs_B, names_B),
                                   ("PT=dict,CT=base", tabs_B, names_B, tabs_A, names_A)):
        n = diag(TA, TB, PL, CL, CI, out)
        rows = out[:n]
        print(label, "flagged", n)
        for r in rows[np.argsort(rows[:, 3])][:40]:
            print("  PT", NA[r[0]], "CT", NB[r[1]], rules[r[2]], "range", r[3], "distinct", r[4], "period", r[5])
