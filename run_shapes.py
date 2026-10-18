"""Shape paths over the physical Kryptos tableau as key sources: compass rose (8/16 rays), 24-point circle and
star polygons {24/k}, cross. Key letter for K4 position i = path[(s + i) mod len] (cyclic start s, both directions).
Tests: fixed alphabets (12 variants x key idx AZ/KA, exact 24/24) and single unknown alphabet (consistent mode 1).
"""
import math
import numpy as np
from numba import njit, prange
import cribfilter as cf
import run_gromark as g
from k4lib import AZ, KA

rows = [l.rstrip("\n") for l in open("data/sculpture_right.txt")]
H = len(rows); W = 31
GRID = np.full((H, W), -1, dtype=np.int64)
for r, l in enumerate(rows):
    for c in range(min(W, len(l))):
        if l[c].isalpha():
            GRID[r, c] = ord(l[c]) - 65
IDX = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)


def cell(r, c):
    return GRID[r % H, c % W]


def line_cells(r0, c0, r1, c1):
    n = max(abs(r1 - r0), abs(c1 - c0))
    return [(round(r0 + (r1 - r0) * t / n), round(c0 + (c1 - c0) * t / n)) for t in range(n)] if n else [(r0, c0)]


def paths():
    D8 = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
    D16 = [(-2, 0), (-2, 1), (-1, 1), (-1, 2), (0, 2), (1, 2), (1, 1), (2, 1), (2, 0), (2, -1), (1, -1), (1, -2),
           (0, -2), (-1, -2), (-1, -1), (-2, -1)]
    for r0 in range(H):
        for c0 in range(W):
            if GRID[r0, c0] < 0:
                continue
            for L in range(3, 14):
                for dname, D in (("rose8", D8), ("rose16", D16)):
                    for rot in (1, -1):
                        Ds = D[::rot]
                        # ray by ray (outward), ring by ring
                        seq = [cell(r0, c0)] + [cell(r0 + dr * k, c0 + dc * k) for dr, dc in Ds for k in range(1, L + 1)]
                        yield f"{dname} ray c=({r0},{c0}) L={L} rot={rot}", seq
                        seq = [cell(r0, c0)] + [cell(r0 + dr * k, c0 + dc * k) for k in range(1, L + 1) for dr, dc in Ds]
                        yield f"{dname} ring c=({r0},{c0}) L={L} rot={rot}", seq
                # cross: N,E,S,W arms
                seq = [cell(r0, c0)] + [cell(r0 + dr * k, c0 + dc * k) for dr, dc in ((-1, 0), (0, 1), (1, 0), (0, -1)) for k in range(1, L + 1)]
                yield f"cross c=({r0},{c0}) L={L}", seq
                # 24-point circle / stars
                R = L
                pts = [(r0 + round(-R * math.cos(2 * math.pi * k / 24)), c0 + round(R * math.sin(2 * math.pi * k / 24))) for k in range(24)]
                for step in (1, 5, 7, 11):
                    order = [(k * step) % 24 for k in range(24)]
                    seq = [cell(*pts[k]) for k in order]
                    yield f"star24/{step} pts c=({r0},{c0}) R={R}", seq
                    lseq = []
                    for a, b in zip(order, order[1:] + order[:1]):
                        lseq += [cell(r, c) for r, c in line_cells(*pts[a], *pts[b])]
                    yield f"star24/{step} lines c=({r0},{c0}) R={R}", lseq


@njit(cache=True)
def test_seq(seq, REQ, CI, PL, CL, IDX):
    n = seq.shape[0]
    d = np.empty(97, dtype=np.int64)
    res = 0
    for direction in range(2):
        for s in range(n):
            # fixed alphabets
            for v in range(REQ.shape[0]):
                kx = v % 2
                ok = True
                for t in range(CI.shape[0]):
                    i = CI[t]
                    j = (s + i) % n if direction == 0 else (s - i) % n
                    if IDX[kx, seq[j]] != REQ[v, t]:
                        ok = False
                        break
                if ok:
                    res |= 1
            # single unknown alphabet (AZ numbering)
            for i in range(97):
                j = (s + i) % n if direction == 0 else (s - i) % n
                d[i] = seq[j]
            if g.consistent(d, 1, PL, CL, CI):
                res |= 2
    return res


def required(cti):
    req = np.zeros((cf.NV * 2, 24), dtype=np.int64)
    for v in range(cf.NV):
        for kx in range(2):
            req[v * 2 + kx] = cf.KV[v, cf.CRIB_L, cti[cf.CRIB_I]]
    return req


def run(cti, CLx, label):
    REQ = required(cti)
    n = 0; hits = []
    for name, seq in paths():
        s = np.array([x for x in seq if x >= 0], dtype=np.int64)
        if len(s) < 8:
            continue
        n += 1
        r = test_seq(s, REQ, cf.CRIB_I, g.PL, CLx, IDX)
        if r:
            hits.append((name, r))
    print(f"{label}: paths tested {n}, hits {len(hits)}", hits[:10], flush=True)
    return hits


if __name__ == "__main__":
    # validation: plant key from one path
    target = None
    for name, seq in paths():
        if name.startswith("star24/7 lines c=(14,15) R=9"):
            target = np.array([x for x in seq if x >= 0]); break
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    syn = "".join(KA[(KA.index(ch) + KA.index(AZ[target[(3 + i) % len(target)]])) % 26] for i, ch in enumerate(PT))
    cti_s = np.array([ord(x) - 65 for x in syn])
    h = run(cti_s, cti_s[cf.CRIB_I], "VALIDATION")
    print("validation truth found:", any(x[0].startswith("star24/7 lines c=(14,15) R=9") for x in h))
    run(cf.CTI, g.CL, "REAL")
    rng = np.random.default_rng(0)
    sh = rng.permutation(cf.CTI)
    run(sh, sh[cf.CRIB_I], "NULL shuffled")
