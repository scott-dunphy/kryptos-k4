"""Nihilist-style coordinate addition in a 26-cell letter matrix (2x13 or 13x2, keyword fill),
mod each coordinate. Z2xZ13 = Z26 (CRT) so this equals Vigenere/Beaufort over alphabet
X[n] = grid[n mod R][n mod C]. Test: periodic key consistency at cribs (direct), p in 1..24."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from k4lib import CT, CRIB_POS, AZ, keyed_alphabet
from run_alphapairs import load_words
POS = np.array(sorted(CRIB_POS)); P = [CRIB_POS[i] for i in POS]; C = [CT[i] for i in POS]

def crt_alpha(kw, R, Cc):
    g = keyed_alphabet(kw)          # row-major fill of R x Cc grid
    return "".join(g[(n % R) * Cc + (n % Cc)] for n in range(26))

def maxm(X, ct):
    inv = {c: i for i, c in enumerate(X)}
    pi = np.array([inv[c] for c in P]); ci = np.array([inv[c] for c in ct])
    out = []
    for k in ((ci - pi) % 26, (ci + pi) % 26):     # vig, beau
        for p in range(1, 25):
            r = POS % p; ok = True; coll = 0
            for res in np.unique(r):
                v = k[r == res]
                if len(v) > 1:
                    coll += len(v) - 1
                    if (v != v[0]).any(): ok = False; break
            if ok and coll >= 4: out.append((p, coll))
    return out

if __name__ == "__main__":
    lore, words = load_words()
    words = sorted(set(words + lore))
    rng = np.random.default_rng(2); sh = list(CT); rng.shuffle(sh); shc = [sh[i] for i in POS]
    # validate: planted Vigenere over crt alphabet, period 9
    X = crt_alpha("BERLIN", 2, 13); key = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    import random; random.seed(0); pt = "".join(random.choice(AZ) for _ in range(97))
    pt = pt[:21] + "EASTNORTHEAST" + pt[34:63] + "BERLINCLOCK" + pt[74:]
    fake = "".join(X[(X.index(c) + key[i % 9]) % 26] for i, c in enumerate(pt))
    assert any(p == 9 for p, _ in maxm(X, [fake[i] for i in POS])), "validation failed"
    hits, nh = [], 0
    for w in words:
        for R, Cc in ((2, 13), (13, 2)):
            X = crt_alpha(w, R, Cc)
            for X2 in (X, X[::-1]):
                h = maxm(X2, C)
                if h: hits.append((w, R, h))
                if maxm(X2, shc): nh += 1
    print("words", len(words), "real hits", len(hits), hits[:20], "null hits", nh)
