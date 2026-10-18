"""P6(1) split key: k_i = s*W[(i+o) % L] + B[i % b]  (W = lore/dictionary keyword, L<=14, letters indexed AZ or KA,
s=+-1, all phases o; B free periodic, b 2..13), direct, 12 variants (Vig/Beau/Var x {AZ,KA}^2).
Test: d_i = k_i - s*W must be constant on residue classes mod b. Random-keyword null of the same size."""
import sys, time
import numpy as np
from numba import njit, prange
sys.path.insert(0, '.')
import cribfilter as cf
from run_alphapairs import load_words
from k4lib import AZ, KA

REQ = np.array([cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)  # (12,24)
CI = cf.CRIB_I.copy()

@njit(parallel=True, cache=True)
def scan(WI, WL, REQ, CI, bmin, bmax, hits):
    """WI: (nw,14) keyword indices (two indexings stacked by caller); WL lengths. hits[w] counts passing configs;
    first passing config stored in hits[w,1:]."""
    nw = WI.shape[0]; nc = CI.shape[0]
    for w in prange(nw):
        L = WL[w]
        val = np.full(32, -1, np.int64)
        d = np.empty(nc, np.int64)
        for v in range(REQ.shape[0]):
            for s in (1, -1):
                for o in range(L):
                    for t in range(nc):
                        d[t] = (REQ[v, t] - s * WI[w, (CI[t] + o) % L]) % 26
                    for b in range(bmin, bmax + 1):
                        for r in range(b): val[r] = -1
                        ok = True
                        for t in range(nc):
                            r = CI[t] % b
                            if val[r] == -1: val[r] = d[t]
                            elif val[r] != d[t]:
                                ok = False; break
                        if ok:
                            if hits[w, 0] == 0:
                                hits[w, 1] = v; hits[w, 2] = s; hits[w, 3] = o; hits[w, 4] = b
                            hits[w, 0] += 1

def encode(words, al):
    WI = np.zeros((len(words), 14), np.int64); WL = np.zeros(len(words), np.int64)
    for j, w in enumerate(words):
        WL[j] = len(w)
        for i, c in enumerate(w): WI[j, i] = al.index(c)
    return WI, WL

if __name__ == '__main__':
    lore, words = load_words()
    words = sorted({w for w in words if 2 <= len(w) <= 14} | {w for w in lore if len(w) <= 14})
    print('keywords', len(words), flush=True)
    rng = np.random.default_rng(0)
    for an, al in (('AZ', AZ), ('KA', KA)):
        WI, WL = encode(words, al)
        hits = np.zeros((len(words), 5), np.int64)
        t = time.time(); scan(WI, WL, REQ, CI, 2, 13, hits); el = time.time() - t
        # null: random letter strings with the same length distribution
        RW = rng.integers(0, 26, size=WI.shape); hn = np.zeros((len(words), 5), np.int64)
        scan(RW, WL, REQ, CI, 2, 13, hn)
        print(f'{an}-indexed: keywords passing {int((hits[:,0]>0).sum())}, configs {int(hits[:,0].sum())}; '
              f'random-keyword null: {int((hn[:,0]>0).sum())} / {int(hn[:,0].sum())}  ({el:.0f}s)', flush=True)
        for j in np.nonzero(hits[:, 0])[0][:20]:
            v, s, o, b = hits[j, 1:]
            print('   ', words[j], cf.VARIANTS[v][:3], 's', s, 'o', o, 'b', b, 'n', hits[j, 0])
