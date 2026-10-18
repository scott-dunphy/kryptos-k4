"""Tableau read-out keys: key index k_t = a*(t mod w) + b*(t div w) + s (mod 26), t = i + o.
Models reading the Kryptos tableau (rows = shifted KA, width w=31 incl. extra cols, or 26/32/33) row by row,
column by column (swap), or any 2D linear walk. 12 variants (Vig/Beau/Var x {AZ,KA}^2). Max crib agreement."""
import sys
import numpy as np
from numba import njit, prange
sys.path.insert(0, '.')
import cribfilter as cf

REQ = np.array([cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)
CI = cf.CRIB_I.copy()

@njit(parallel=True, cache=True)
def scan(REQ, CI, wmax, out):
    for w in prange(2, wmax + 1):
        cnt = np.zeros(26, np.int64)
        best = 0; bo = 0; ba = 0; bb = 0; bv = 0
        for v in range(REQ.shape[0]):
            for o in range(26 * w):
                for a in range(26):
                    for b in range(26):
                        for x in range(26): cnt[x] = 0
                        for t in range(CI.shape[0]):
                            tt = CI[t] + o
                            cnt[(REQ[v, t] - a * (tt % w) - b * (tt // w)) % 26] += 1
                        m = 0
                        for x in range(26):
                            if cnt[x] > m: m = cnt[x]
                        if m > best:
                            best = m; bo = o; ba = a; bb = b; bv = v
        out[w, 0] = best; out[w, 1] = bv; out[w, 2] = o; out[w, 3] = ba; out[w, 4] = bb

if __name__ == '__main__':
    import random
    W = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    out = np.zeros((W + 1, 5), np.int64)
    scan(REQ, CI, W, out)
    print('REAL best agreement by w:', out[2:, 0].tolist())
    for w in range(2, W + 1):
        if out[w, 0] >= 10: print(' w', w, out[w].tolist())
    # null: shuffled CT
    rnd = random.Random(1)
    cts = list(cf.CTI); rnd.shuffle(cts); cts = np.array(cts)
    REQ2 = np.array([cf.KV[v, cf.CRIB_L, cts[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)
    out2 = np.zeros((W + 1, 5), np.int64)
    scan(REQ2, CI, W, out2)
    print('NULL best agreement by w:', out2[2:, 0].tolist())
