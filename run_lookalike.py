"""Look-alike letters: read carved Latin letters as Greek/Cyrillic phonetic values, then rerun tests.

Variants map CT letters (and optionally crib PT letters) through look-alike phonetic tables.
Tests on transformed CT: E1 (identity, routes W2-49, columnar W<=8, fwd+inv) x periodic p1-24 x 12 variants x 2 orders
(cribfilter.check_batch, m>=4), plus single-unknown-alphabet chain/clock keys are skipped (alphabet-agnostic already:
a fixed CT relabelling that is a bijection is absorbed by an unknown alphabet, so only non-bijective maps matter for those).
"""
import numpy as np
import cribfilter as cf
from perms import route_perms, columnar_all, inverse
from k4lib import CT, AZ, to_idx

MAPS = {
    # Greek capital look-alikes -> Latin phonetic (modern / classical choices)
    "greek_modern":   {"B": "V", "H": "I", "P": "R", "Y": "U", "X": "H"},
    "greek_classic":  {"H": "E", "P": "R", "Y": "U", "X": "K"},
    "greek_classic2": {"H": "E", "P": "R", "Y": "Y", "X": "C"},
    # Cyrillic look-alikes -> Latin phonetic
    "cyrillic":       {"B": "V", "C": "S", "H": "N", "P": "R", "Y": "U", "X": "H"},
    "cyrillic_kh":    {"B": "V", "C": "S", "H": "N", "P": "R", "Y": "U", "X": "K"},
    # swaps that keep a bijection (look-alike pairs exchanged)
    "swap_PR_HN_BV":  {"P": "R", "R": "P", "H": "N", "N": "H", "B": "V", "V": "B"},
    "swap_cyr_full":  {"P": "R", "R": "P", "H": "N", "N": "H", "B": "V", "V": "B", "C": "S", "S": "C", "Y": "U", "U": "Y"},
}


def perm_set():
    P = [np.arange(97)] + [p for _, p in route_perms(97)] + [p for _, p in columnar_all(97, 8)]
    P = P + [inverse(p) for p in P]
    return np.array([inverse(p) for p in P])


if __name__ == "__main__":
    invs = perm_set()
    out = np.zeros((100000, 5), dtype=np.int64)
    for name, mp in MAPS.items():
        ct2 = "".join(mp.get(c, c) for c in CT)
        for side in ("CT", "CT+cribPT"):
            cti = to_idx(ct2)
            cl = cf.CRIB_L.copy()
            if side == "CT+cribPT":
                cl = np.array([AZ.index(mp.get(AZ[x], AZ[x])) for x in cf.CRIB_L], dtype=np.int64)
            n = cf.check_batch(invs, 1, 24, cf.KV, cti, cf.CRIB_I, cl, 4, out)
            print(f"{name:15s} {side:10s} survivors m>=4: {n}", flush=True)
            for r in out[:min(n, 5)]:
                print("   ", r.tolist())
