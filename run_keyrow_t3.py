"""Fable plan #3: dictionary keyword key rows x keyed tableaus, tolerating up to 3 altered CT letters.
Tableau alphabet T (PT, CT and key letters all indexed in T, as on a keyed Vigenere tableau), rules vig/beau/var.
Required key letter at crib t: T[KV_T(P_t, C_t)]. Key row = keyword w repeated, (a) continuous from K4 pos 0,
(b) restarting at each copper line (K4 pos 0, 4, 35, 66). Hit if mismatches <= 3 (FP ~ C(24,3)*26^-21 per test).
Tableaus: AZ, KA, lore + themed keyword alphabets, structured alphabets (run_altalpha families), fwd/rev.
"""
import time
import numpy as np
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet
from run_alphapairs import load_words

pos = np.array(sorted(CRIB_POS))
P = [CRIB_POS[i] for i in pos]; C = [CT[i] for i in pos]
STARTS = np.array([0, 4, 35, 66])


def tableaus():
    from run_altalpha import families
    lore, _ = load_words()
    themed = ("COORDINATE BEARING AZIMUTH MERIDIAN LATITUDE LONGITUDE ABSCISSA PALIMPSEST PALIMPCEST KRYPTOS BERLIN "
              "CLOCK WELTZEITUHR ALEXANDERPLATZ SHADOW LUCID MEMORY LAYERTWO EQUAL SANBORN SCHEIDT WEBSTER LANGLEY "
              "COMPASS LODESTONE MAGNETIC NORTHEAST EAST CARTER TUTANKHAMUN EGYPT CAIRO WALL CHECKPOINT").split()
    out = {"AZ": AZ, "KA": KA}
    for w in set(lore + themed):
        out["kw_" + w] = keyed_alphabet(w)
    fam = families(sorted(set(lore + themed)))
    out.update(fam)
    res = {}
    for n, a in out.items():
        res[n] = a; res[n + "~rev"] = a[::-1]
    return res


if __name__ == "__main__":
    lore, words = load_words()
    words = sorted(set(w for w in words + lore if 3 <= len(w) <= 20))
    byL = {}
    for w in words:
        byL.setdefault(len(w), []).append(w)
    WL = {L: np.array([[ord(c) - 65 for c in ws] for ws in lst], dtype=np.int8) for L, lst in byL.items()}
    NL = {L: lst for L, lst in byL.items()}
    T = tableaus()
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        seen = set(T.values())
        for w in words:
            for rev in (0, 1):
                a = keyed_alphabet(w); a = a[::-1] if rev else a
                if a not in seen:
                    seen.add(a); T[f"dict_{w}{'~rev' if rev else ''}"] = a
    print("tableaus", len(T), "words", len(words), flush=True)
    # relative positions for per-line restart
    rel = np.array([i - STARTS[STARTS <= i].max() for i in pos])
    hits = []; t0 = time.time()
    for n_done, (tn, ta) in enumerate(T.items()):
        if n_done % 20000 == 0:
            print(f"  progress {n_done}/{len(T)} {time.time() - t0:.0f}s hits so far {len(hits)}", flush=True)
        idx = {c: k for k, c in enumerate(ta)}
        for rule in range(3):
            req = []
            for p, c in zip(P, C):
                ip, ic = idx[p], idx[c]
                k = (ic - ip) % 26 if rule == 0 else ((ic + ip) % 26 if rule == 1 else (ip - ic) % 26)
                req.append(ord(ta[k]) - 65)
            req = np.array(req, dtype=np.int8)
            for mode, positions in (("cont", pos), ("perline", rel)):
                for L, W in WL.items():
                    cols = positions % L
                    mism = (W[:, cols] != req[None, :]).sum(axis=1)
                    good = np.nonzero(mism <= 3)[0]
                    for g in good:
                        hits.append((tn, rule, mode, NL[L][g], int(mism[g])))
    print(f"done {time.time() - t0:.0f}s; hits (<=3 mismatches of 24): {len(hits)}")
    for h in hits[:20]:
        print("  ", h)
