"""Extension of run_keysplit_mask.py: k1 lengths 15-26 (stage A survivors exist only at L1 >= 11).
k1 candidates: /usr/share/dict words of 15-26 letters + every 15-26-letter substring of K0-K3 plaintext;
also re-runs 11-14 with K-text substrings (the first pass used dictionary words only)."""
import time
import numpy as np
import run_keysplit_mask as ks
from kryptos_texts import K1_PT, K2_PT, K3_PT, MORSE

def long_keys():
    words = set()
    with open("/usr/share/dict/words") as f:
        for w in f:
            w = w.strip().upper()
            if 15 <= len(w) <= 26 and w.isalpha() and w.isascii():
                words.add(w)
    for t in (K1_PT, K2_PT, K3_PT, MORSE):
        t = t.replace("?", "")
        for L in range(11, 27):
            for s in range(len(t) - L + 1):
                words.add(t[s:s + L])
    out = {}
    for L in range(1, 27):
        ws = sorted(w for w in words if len(w) == L)
        out[L] = (ws, np.array([[ord(c) - 65 for c in w] for w in ws], dtype=np.int64).reshape(len(ws), L))
    return out

if __name__ == "__main__":
    D = long_keys()
    print("k1 candidates by length", {L: len(D[L][0]) for L in range(11, 27)}, flush=True)
    rng = np.random.default_rng(20261018)
    # planted: mask + long phrase key + lore key
    from k4lib import CRIB_POS, AZ, KA
    m = rng.permutation(26); pt = rng.integers(0, 26, 97)
    for i, ch in CRIB_POS.items(): pt[i] = ord(ch) - 65
    k1 = D[19][0][7]; k2 = "KRYPTOS"; KA2AZ = [AZ.index(c) for c in KA]
    ct = "".join(AZ[KA2AZ[(m[pt[i]] + ord(k1[i % 19]) - 65 + ord(k2[i % 7]) - 65) % 26]] for i in range(97))
    _, h = ks.run(ct, D, "PLANTED", verbose=False)
    print("planted", k1, "found:", any(x[8] == k1 and x[0] == "KRYPTOS" for x in h), flush=True)
    from k4lib import CT
    t = time.time(); ks.run(CT, D, "REAL"); print("time", round(time.time() - t, 1), flush=True)
    cl = list(CT)
    for s in range(3):
        rng.shuffle(cl); ks.run("".join(cl), D, f"NULL{s}", verbose=False)
