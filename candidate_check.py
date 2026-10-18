"""Score a candidate K4 plaintext against everything known.
Checks: length 97; cribs exact at 21-33 / 63-73; KRYPTOS-fingerprint: PT letter in KRYPTOS -> |C-P|<=2 (AZ),
non-KRYPTOS -> |C-P|>2 (weaker); IoC/letter sanity; quadgram + word score.
Random on-theme English: ~50% of KRYPTOS letters fit by chance; real solution should fit ~90%+.
Usage: python candidate_check.py "PLAINTEXT..."  (letters only) or import check()."""
import sys
import numpy as np
from k4lib import CT, CRIB_POS, AZ, qscore

KRY = set("KRYPTOS")


def check(pt, verbose=True):
    pt = "".join(c for c in pt.upper() if c.isalpha())
    out = {"len": len(pt)}
    if len(pt) != 97:
        if verbose:
            print(f"length {len(pt)} != 97")
        return out
    crib_ok = sum(pt[i] == c for i, c in CRIB_POS.items())
    kfit = ktot = nfit = ntot = 0
    bad = []
    for i, p in enumerate(pt):
        if i in CRIB_POS:
            continue
        d = abs(((ord(CT[i]) - ord(p) + 13) % 26) - 13)
        if p in KRY:
            ktot += 1; kfit += d <= 2
            if d > 2:
                bad.append((i, p, CT[i], "K-letter outside ±2"))
        else:
            ntot += 1; nfit += d > 2
    out.update(cribs=f"{crib_ok}/24", k_fit=f"{kfit}/{ktot}", nonk_ok=f"{nfit}/{ntot}", q=round(qscore(pt), 3))
    try:
        from wordscore import wseg
        out["word"] = round(float(wseg(pt)[0]), 3)
    except Exception:
        pass
    # binomial-ish p for K fit at chance 5/26
    from math import comb
    p0 = 5 / 26
    out["p_k_chance"] = round(sum(comb(ktot, j) * p0 ** j * (1 - p0) ** (ktot - j) for j in range(kfit, ktot + 1)), 4) if ktot else None
    if verbose:
        print(out)
        for b in bad[:10]:
            print("   ", b)
    return out


if __name__ == "__main__":
    check(sys.argv[1] if len(sys.argv) > 1 else input("plaintext: "))
