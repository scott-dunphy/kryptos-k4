"""Misspelling positions / shifts as numeric keys (user lead, 2026-10-18).

Sanborn: misspellings matter for "their orientation or positioning". Build numeric keys from where the
misspellings sit and how far the letters moved, and test them as the K4 key:
  fixed : C = A[(A^-1(P) +/- k_i + const) mod 26], A in AZ/KA (count crib hits at best const)
  mask  : arbitrary substitution on PT side or CT side + key (exact: function + injective on 24 cribs)
Keys: value lists (mod 26) in every order, and their decimal-digit expansions, cyclic with every phase.
Note: any periodic key of length <= 24 is already dead with fixed alphabets (E1), and with a free mask
at L <= 12, 14, 15, 17, 21, 22 (Barney / run_mask_trans) -- only long digit strings are new.
"""
import itertools
import numpy as np
from k4lib import CT, CRIB_POS, AZ, KA
from kryptos_texts import K1_PT, K2_PT, K3_PT, MORSE

CI = sorted(CRIB_POS)
PLs = [CRIB_POS[i] for i in CI]

i1 = K1_PT.find("IQLUSION") + 1          # Q
i2 = K2_PT.find("UNDERGRUUND") + 7       # second U
i3 = K3_PT.find("DESPARATLY") + 4        # A for E
i3e = K3_PT.find("DESPARATLY") + 8       # missing E
i0 = MORSE.find("DIGETAL") + 3           # E for I
SETS = {
    "text idx0": [i1, i2, i3, i0], "text idx1": [i1 + 1, i2 + 1, i3 + 1, i0 + 1],
    "text idx0 +E": [i1, i2, i3, i3e, i0], "text idx0 K123": [i1, i2, i3],
    "stream idx0": [i1, 63 + i2, 63 + len(K2_PT) + i3], "stream idx1": [i1 + 1, 64 + i2, 64 + len(K2_PT) + i3],
    "word idx0": [1, 7, 4, 3], "word idx1": [2, 8, 5, 4], "word idx1 +C": [2, 8, 5, 4, 7], "word idx0 +C": [1, 7, 4, 3, 6],
    "copper rc": [1, 24, 5, 23, 16, 27], "copper rc +K4": [1, 24, 5, 23, 16, 27, 26, 29, 27, 5],
    "copper cols": [24, 23, 27], "copper rows": [1, 5, 16],
    "AZ shifts": [5, 6, 22, 22], "AZ shifts +C": [5, 6, 22, 22, 10],
    "KA shifts": [(KA.index(b) - KA.index(a)) % 26 for a, b in ("LQ", "OU", "EA", "IE")],
    "KA shifts +C": [(KA.index(b) - KA.index(a)) % 26 for a, b in ("LQ", "OU", "EA", "IE", "SC")],
    "wrong AZ": [16, 20, 0, 4], "right AZ": [11, 14, 4, 8],
}


def keys():
    seen = set()
    for name, vals in SETS.items():
        perms = itertools.permutations(vals) if len(vals) <= 6 else (tuple(vals), tuple(vals[::-1]))
        for perm in perms:
            for enc, k in (("val", [v % 26 for v in perm]), ("digits", [int(d) for d in "".join(map(str, perm))])):
                t = tuple(k)
                if t not in seen:
                    seen.add(t)
                    yield f"{name} {enc} {perm}", t


def test(key, ct, alph, sign):
    """returns (best fixed-const hits, mask_ok_ptside, mask_ok_ctside) maximised over phase."""
    A = alph
    best, mp, mc = 0, False, False
    L = len(key)
    cidx = [A.index(ct[i]) for i in CI]
    pidx = [A.index(p) for p in PLs]
    for f in range(L):
        k = [sign * key[(i + f) % L] for i in CI]
        d = [(c - p - kk) % 26 for c, p, kk in zip(cidx, pidx, k)]
        best = max(best, max(d.count(x) for x in set(d)))
        # PT-side mask: s(P) = A^-1(C) - k
        for side in (0, 1):
            fwd, bwd, ok = {}, {}, True
            for c, p, kk, pl, cl in zip(cidx, pidx, k, PLs, (ct[i] for i in CI)):
                a, b = (pl, (c - kk) % 26) if side == 0 else (cl, (p + kk) % 26)
                if fwd.setdefault(a, b) != b or bwd.setdefault(b, a) != a:
                    ok = False
                    break
            if ok:
                if side == 0: mp = True
                else: mc = True
    return best, mp, mc


def scan(ct, show=False):
    hits, top, n = [], 0, 0
    for name, key in keys():
        for alph in (AZ, KA):
            for sign in (1, -1):
                n += 1
                b, mp, mc = test(key, ct, alph, sign)
                top = max(top, b)
                if mp or mc or b >= 20:
                    hits.append((name, "AZ" if alph == AZ else "KA", sign, b, mp, mc))
    return n, top, hits


if __name__ == "__main__":
    rng = np.random.default_rng(20261018)
    # planted: digits of "word idx1 +C" order as given, PT-side mask, KA, sign +
    key = [int(d) for d in "28547"]
    s = list(rng.permutation(26))
    pt = [AZ[x] for x in rng.integers(0, 26, 97)]
    for i, ch in CRIB_POS.items(): pt[i] = ch
    pct = "".join(KA[(s[AZ.index(p)] + key[i % 5]) % 26] for i, p in enumerate(pt))
    n, top, h = scan(pct)
    print("planted 28547 KA mask: found", any(x[0].endswith("(2, 8, 5, 4, 7)") and x[1] == "KA" and x[4] for x in h))
    n, top, h = scan(CT)
    print(f"REAL tests {n}, best fixed-const hits {top}/24, mask/>=20 hits {len(h)}")
    for x in h[:20]: print("  ", x)
    for t in range(5):
        n, top2, h2 = scan("".join(rng.permutation(list(CT))))
        print(f"NULL{t} best {top2}/24, hits {len(h2)}")
