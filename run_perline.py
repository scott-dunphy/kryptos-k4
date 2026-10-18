"""Per-line keys on the copper layout (K4 at row 24 col 27; rows 25-27 full 31-col lines).
A) per-line constant shift, single unknown mixed alphabet (s25, s26, s27; one absorbed): consistent(mode 1).
B) per-line keyword: row r uses keyword w repeating from col 0 of the row (also from K4-relative start);
   rows tested independently: row 25 (13 cribs), row 27 (8 cribs). 12 variants x key idx AZ/KA, any indicator shift.
"""
import numpy as np
from numba import njit, prange
import cribfilter as cf
import run_gromark as g
from k4lib import AZ, KA
from run_alphapairs import load_words

W = 31; OFF = 27


def rc(i):
    return divmod(i + OFF, W)


def test_A(PL, CL, CI):
    rows = np.array([rc(int(i))[0] for i in CI])
    hits = []
    for s26 in range(26):
        for s27 in range(26):
            d = np.zeros(97, dtype=np.int64)
            for t, i in enumerate(CI):
                r = rows[t]
                d[i] = 0 if r == 1 else (s26 if r == 2 else s27)
            for sign in (1, -1):
                if g.consistent((sign * d) % 26, 1, PL, CL, CI):
                    hits.append((s26, s27, sign))
    return hits


@njit(parallel=True, cache=True)
def test_B(words, wlen, cols, req, IDX, flags):
    # cols: (n,) column (or relative index) of each crib in this row; req: (nv2, n) required key index
    for w in prange(words.shape[0]):
        L = wlen[w]
        for v in range(req.shape[0]):
            kx = v % 2
            sh = -1; ok = True
            for t in range(cols.shape[0]):
                k = IDX[kx, words[w, cols[t] % L]]
                d = (req[v, t] - k) % 26
                if sh == -1:
                    sh = d
                elif d != sh:
                    ok = False
                    break
            if ok:
                flags[w] += 1


if __name__ == "__main__":
    ha = test_A(g.PL, g.CL, g.CI)
    print("A per-line shift, unknown alphabet: hits", len(ha))
    rng = np.random.default_rng(0)
    print("A null:", [len(test_A(g.PL, rng.integers(0, 26, 24), g.CI)) for _ in range(5)])
    lore, words = load_words()
    words = sorted(set(words + lore + ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW", "LAYERTWO"]))
    words = [w for w in words if len(w) <= 20]
    Wd = np.zeros((len(words), 20), dtype=np.int64); wl = np.array([len(w) for w in words])
    for i, w in enumerate(words):
        for j, c in enumerate(w):
            Wd[i, j] = ord(c) - 65
    IDX = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)
    for row in (1, 3):  # row 25 -> 1, row 27 -> 3 (relative to row 24)
        ts = [t for t in range(24) if rc(int(cf.CRIB_I[t]))[0] == row]
        for align in ("rowcol", "k4rel"):
            if align == "rowcol":
                cols = np.array([rc(int(cf.CRIB_I[t]))[1] for t in ts], dtype=np.int64)
            else:
                cols = np.array([int(cf.CRIB_I[t]) - 4 - 31 * (row - 1) for t in ts], dtype=np.int64)
            req = np.zeros((cf.NV * 2, len(ts)), dtype=np.int64)
            for v in range(cf.NV):
                for kx in range(2):
                    req[2 * v + kx] = [cf.KV[v, cf.CRIB_L[t], cf.CTI[cf.CRIB_I[t]]] for t in ts]
            fl = np.zeros(len(words), dtype=np.int64)
            test_B(Wd, wl, cols, req, IDX, fl)
            hits = [words[i] for i in np.nonzero(fl)[0]]
            print(f"B row {24 + row} ({len(ts)} cribs) align={align}: keyword hits {len(hits)}", hits[:15])
            # null: random required values
            fln = np.zeros(len(words), dtype=np.int64)
            test_B(Wd, wl, cols, rng.integers(0, 26, req.shape), IDX, fln)
            print(f"   null hits {int((fln > 0).sum())}")
