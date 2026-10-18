"""Direction-driven walks on the physical Kryptos tableau (data/sculpture_right.txt, 28x31 incl. header/footer/side).

Key letter for position i = grid letter at walk step i; walk starts at any cell, moves by a periodic pattern of
compass steps (length 1-4 over 8 directions), toroidal wrap; non-letter cells (corner spaces) are skipped.
Decryption: 12 variants (cribfilter.KV) x key index in AZ or KA. Crib test: all 24 crib key indices must match.
Also: walks that change direction per plaintext word are not modelled (unknown word boundaries).
"""
import itertools
import numpy as np
from numba import njit, prange
import cribfilter as cf
from k4lib import AZ, KA

rows = [l.rstrip("\n") for l in open("data/sculpture_right.txt")]
H = len(rows); W = 31
GRID = np.full((H, W), -1, dtype=np.int64)
for r, l in enumerate(rows):
    for c in range(min(W, len(l))):
        if l[c].isalpha():
            GRID[r, c] = ord(l[c]) - 65
DIRS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]  # N NE E SE S SW W NW
NAMES = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
PATS = [p for L in range(1, 5) for p in itertools.product(range(8), repeat=L)]
PAT = np.full((len(PATS), 4), -1, dtype=np.int64); PLEN = np.array([len(p) for p in PATS], dtype=np.int64)
for k, p in enumerate(PATS):
    PAT[k, :len(p)] = p
DR = np.array([d[0] for d in DIRS], dtype=np.int64); DC = np.array([d[1] for d in DIRS], dtype=np.int64)
IDX = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)  # letter -> index


@njit(parallel=True, cache=True)
def scan(GRID, PAT, PLEN, DR, DC, IDX, REQ, CI, hits):
    H, W = GRID.shape
    npat = PAT.shape[0]
    nreq = REQ.shape[0]
    for start in prange(H * W):
        r0 = start // W; c0 = start % W
        if GRID[r0, c0] < 0:
            continue
        keys = np.empty(97, dtype=np.int64)
        for p in range(npat):
            r = r0; c = c0
            # generate walk letters for positions 0..73 (max crib pos 73)
            ok = True
            step = 0
            for i in range(74):
                keys[i] = GRID[r, c]
                # move (skip non-letter cells)
                while True:
                    d = PAT[p, step % PLEN[p]]
                    step += 1
                    r = (r + DR[d]) % H; c = (c + DC[d]) % W
                    if GRID[r, c] >= 0:
                        break
            for v in range(nreq):          # variant x key-index alphabet
                kx = v % 2
                good = True
                for t in range(CI.shape[0]):
                    if IDX[kx, keys[CI[t]]] != REQ[v, t]:
                        good = False
                        break
                if good:
                    hits[start, p] += 1


def required(cti):
    req = np.zeros((cf.NV * 2, 24), dtype=np.int64)
    for v in range(cf.NV):
        for kx in range(2):
            for t in range(24):
                req[v * 2 + kx, t] = cf.KV[v, cf.CRIB_L[t], cti[cf.CRIB_I[t]]]
    return req


if __name__ == "__main__":
    # validation: plant walk start (5,7), pattern E,NE, KA-Vig (variant index for vig KA/KA), key index KA
    v_kaka = [i for i, x in enumerate(cf.VARIANTS) if x[:3] == ("vig", "KA", "KA")][0]
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    r, c, step, keys = 5, 7, 0, []
    pat = (2, 1)
    for i in range(97):
        keys.append(GRID[r, c])
        while True:
            d = pat[step % 2]; step += 1
            r = (r + DIRS[d][0]) % H; c = (c + DIRS[d][1]) % W
            if GRID[r, c] >= 0:
                break
    syn = [KA[(KA.index(ch) + KA.index(AZ[keys[i]])) % 26] for i, ch in enumerate(PT)]
    cti_s = np.array([ord(x) - 65 for x in syn])
    hits = np.zeros((H * W, len(PATS)), dtype=np.int64)
    scan(GRID, PAT, PLEN, DR, DC, IDX, required(cti_s), cf.CRIB_I, hits)
    print("validation hits", int((hits > 0).sum()), "truth", bool(hits[5 * W + 7, PATS.index(pat)]))
    hits[:] = 0
    scan(GRID, PAT, PLEN, DR, DC, IDX, required(cf.CTI), cf.CRIB_I, hits)
    nz = np.argwhere(hits > 0)
    print("REAL hits", len(nz))
    for s, p in nz[:20]:
        print("   start", divmod(int(s), W), "pattern", [NAMES[d] for d in PATS[p]])
    rng = np.random.default_rng(0)
    for k in range(3):
        hits[:] = 0
        scan(GRID, PAT, PLEN, DR, DC, IDX, required(rng.permutation(cf.CTI)), cf.CRIB_I, hits)
        print("null shuffled CT hits", int((hits > 0).sum()))
