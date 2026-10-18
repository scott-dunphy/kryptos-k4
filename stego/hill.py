"""S2: Hill cipher n=2..4 (the 'HILL' down the tableau's right column), direct and after the
sculpture-row layout. Unknown matrix rows solved by exhaustive search per row (c_j = sum_k M[j,k] p_k mod 26),
checking every full crib block for the given block offset. Numbering AZ or KA, encrypt or decrypt direction."""
import itertools
from common import *

def blocks(n, off, length=97):
    out = []
    for s in range(off, length - n + 1, n):
        if all((s + k) in cf.CRIB_POS if hasattr(cf, 'CRIB_POS') else False for k in range(n)):
            out.append(s)
    return out

from k4lib import CRIB_POS

def run(n, alpha, direction, ct=CT):
    hits = []
    for off in range(n):
        bl = [s for s in range(off, len(ct) - n + 1, n) if all((s + k) in CRIB_POS for k in range(n))]
        if not bl:
            continue
        P = np.array([[alpha.index(CRIB_POS[s + k]) for k in range(n)] for s in bl])
        C = np.array([[alpha.index(ct[s + k]) for k in range(n)] for s in bl])
        X, Y = (P, C) if direction == "enc" else (C, P)   # Y_j = row . X
        combos = np.array(list(itertools.product(range(26), repeat=n)), dtype=np.int64)  # 26^n x n
        lhs = (combos @ X.T) % 26  # 26^n x nblocks
        rows_ok = []
        for j in range(n):
            ok = np.all(lhs == Y[:, j][None, :], axis=1)
            rows_ok.append(combos[ok])
        nsol = [len(r) for r in rows_ok]
        hits.append((off, len(bl), nsol))
    return hits

if __name__ == "__main__":
    for n in (2, 3, 4):
        for aname, al in (("AZ", AZ), ("KA", KA)):
            for d in ("enc", "dec"):
                for ctname, ct in (("CT", CT), ("?CT", "?" + CT)):
                    if ctname == "?CT":
                        continue
                    print(n, aname, d, run(n, al, d))
