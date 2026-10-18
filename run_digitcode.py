"""Fable test 1: table as letter<->number lookup, mixed-radix digits, periodic digit-wise key, no carry.

n = index of letter in AZ or KA, 0-based or 1-based. n -> digits in radix (b1, b2) (n = d1*b2 + d2) or base 3
(three trits). Cipher digit c_j = (d_j + s_j*k_j[i % p]) mod b_j, CT letter = inverse lookup. Cells that are not
letters (n >= 26, or n == 0 when 1-based) are invalid: every decrypted K4 position must land on a letter.
Each residue class mod p is solved independently (all key digit tuples tried), so phase is irrelevant.
Hit = every class has a key tuple consistent with its cribs and valid at all its positions.
p = 31 is the per-copper-line / 31-column-sheet restart.
"""
import itertools
import numpy as np
from k4lib import CT, CRIB_POS, AZ, KA

RADICES = [(2, 13), (13, 2), (3, 9), (9, 3), (4, 7), (7, 4), (5, 6), (6, 5), (3, 3, 3)]
PERIODS = list(range(1, 27)) + [31]


def to_digits(n, rad):
    ds = []
    for b in reversed(rad):
        ds.append(n % b); n //= b
    return tuple(reversed(ds))


def from_digits(ds, rad):
    n = 0
    for d, b in zip(ds, rad):
        n = n * b + d
    return n


def conventions():
    for alpha in (AZ, KA):
        for base1 in (0, 1):
            enc = {ch: alpha.index(ch) + base1 for ch in AZ}
            dec = {v: k for k, v in enc.items()}
            yield f"{'AZ' if alpha == AZ else 'KA'}{base1}", enc, dec


def test(ct, rad, p, signs, enc, dec):
    """returns (ok, checks)"""
    cdig = [to_digits(enc[c], rad) for c in ct]
    keys = list(itertools.product(*[range(b) for b in rad]))
    checks = 0
    for r in range(p):
        pos = list(range(r, len(ct), p))
        cribs = [i for i in pos if i in CRIB_POS]
        found = False
        for k in keys:
            good = True
            for i in pos:
                ds = tuple((c - s * kk) % b for c, s, kk, b in zip(cdig[i], signs, k, rad))
                n = from_digits(ds, rad)
                if n not in dec:
                    good = False; break
                if i in CRIB_POS and dec[n] != CRIB_POS[i]:
                    good = False; break
            if good:
                found = True; break
        if not found:
            return False, 0
        checks += max(len(cribs) - 1, 0)
    return True, checks


def scan(ct, label):
    hits = []
    n = 0
    for name, enc, dec in conventions():
        for rad in RADICES:
            for signs in itertools.product((1, -1), repeat=len(rad)):
                for p in PERIODS:
                    n += 1
                    ok, ch = test(ct, rad, p, signs, enc, dec)
                    if ok:
                        hits.append((name, rad, signs, p, ch))
    print(f"[{label}] configs {n}, consistent {len(hits)}", flush=True)
    by_p = {}
    for h in hits:
        by_p.setdefault(h[3], 0)
        by_p[h[3]] += 1
    print(f"[{label}] consistent by period: {dict(sorted(by_p.items()))}", flush=True)
    for h in sorted(hits, key=lambda h: -h[4])[:10]:
        print(f"[{label}]   {h}", flush=True)
    return hits


def planted(rng):
    """Plant with a key valid at the crib cells; non-crib PT letters drawn among letters giving valid cells."""
    name, enc, dec = list(conventions())[1]
    rad, p, signs = (5, 6), 11, (1, 1)
    def cell(ch, k):
        ds = to_digits(enc[ch], rad)
        return from_digits(tuple((d + s * kk) % b for d, s, kk, b in zip(ds, signs, k, rad)), rad)
    while True:
        key = [tuple(int(rng.integers(0, b)) for b in rad) for _ in range(p)]
        if all(cell(ch, key[i % p]) in dec for i, ch in CRIB_POS.items()):
            break
    out = []
    for i in range(97):
        if i in CRIB_POS:
            ch = CRIB_POS[i]
        else:
            opts = [c for c in AZ if cell(c, key[i % p]) in dec]
            ch = opts[int(rng.integers(0, len(opts)))]
        out.append(dec[cell(ch, key[i % p])])
    return "".join(out), (name, rad, signs, p)


if __name__ == "__main__":
    rng = np.random.default_rng(20261018)
    pct, truth = planted(rng)
    print("planted truth", truth)
    ok, ch = test(pct, truth[1], truth[3], truth[2], *[c for c in conventions()][1][1:])
    print("planted recovered:", ok, "checks", ch)
    real = scan(CT, "REAL")
    cti = list(CT)
    for s in range(3):
        rng.shuffle(cti)
        scan("".join(cti), f"NULL{s}")
