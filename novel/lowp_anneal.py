"""For (perm, p<=5, order) passing the arbitrary-alphabet crib test, solve the p independent monoalphabetic
substitutions by annealing (quadgrams), crib letters pinned. Null: same on shuffled CT with its own passing perms."""
import sys, time
import numpy as np
from numba import njit, prange
sys.path.insert(0, '.')
import cribfilter as cf
from perms import route_perms, columnar_all, inverse
from k4lib import load_quadgrams, AZ
from novel.anypoly import scan
QG = load_quadgrams()

@njit(cache=True)
def qs(pt, QG):
    s = 0.0
    for i in range(pt.shape[0] - 3):
        s += QG[((pt[i] * 26 + pt[i + 1]) * 26 + pt[i + 2]) * 26 + pt[i + 3]]
    return s

@njit(cache=True)
def anneal_one(X, col, p, pin, QG, iters, seed):
    """X: transposed CT in PT order (X[i] = CT letter feeding PT position i); col[i] residue.
    key[r, c] = PT letter for CT letter c in column r (a permutation per column). pin[r,c] = forced PT or -1."""
    np.random.seed(seed)
    n = X.shape[0]
    key = np.empty((p, 26), np.int64)
    for r in range(p):
        perm = np.random.permutation(26)
        # enforce pins by swapping
        for c in range(26):
            if pin[r, c] >= 0:
                # find where pin value currently is
                for c2 in range(26):
                    if perm[c2] == pin[r, c]:
                        perm[c2] = perm[c]; perm[c] = pin[r, c]; break
        key[r] = perm
    pt = np.empty(n, np.int64)
    for i in range(n): pt[i] = key[col[i], X[i]]
    cur = qs(pt, QG); best = cur; bestpt = pt.copy()
    for it in range(iters):
        T = 2.0 * (1 - it / iters) + 0.02
        r = np.random.randint(0, p); a = np.random.randint(0, 26); b = np.random.randint(0, 26)
        if a == b or pin[r, a] >= 0 or pin[r, b] >= 0: continue
        key[r, a], key[r, b] = key[r, b], key[r, a]
        for i in range(n):
            if col[i] == r and (X[i] == a or X[i] == b): pt[i] = key[r, X[i]]
        new = qs(pt, QG)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new
            if cur > best: best = cur; bestpt[:] = pt
        else:
            key[r, a], key[r, b] = key[r, b], key[r, a]
            for i in range(n):
                if col[i] == r and (X[i] == a or X[i] == b): pt[i] = key[r, X[i]]
    return best / (n - 3), bestpt

def prep(inv, p, order, cti):
    X = np.array([cti[inv[i]] for i in range(97)], np.int64)
    col = np.array([(inv[i] % p) if order == 0 else (i % p) for i in range(97)], np.int64)
    pin = -np.ones((p, 26), np.int64)
    for t in range(len(cf.CRIB_I)):
        i = int(cf.CRIB_I[t]); pin[col[i], X[i]] = int(cf.CRIB_L[t])
    return X, col, pin

if __name__ == '__main__':
    import random
    PS = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else [3, 4, 5]
    perms = [np.arange(97)]
    for gen in (route_perms(97), columnar_all(97, 8)):
        for l, p in gen: perms.append(p)
    P2 = []
    for p in perms: P2 += [p, inverse(p)]
    invs = np.array([inverse(p) for p in P2])
    for lab, cti in [('REAL', cf.CTI), ('SHUF', np.array(random.Random(9).sample(list(cf.CTI), 97), np.int64))]:
        out = np.zeros((len(invs), 31, 2), np.int8); chk = np.zeros((len(invs), 31, 2), np.int16)
        scan(invs, 5, cti, cf.CRIB_I, cf.CRIB_L, out, chk)
        res = []
        t = time.time()
        for p in PS:
            for order in (0, 1):
                qs_ = np.nonzero(out[:, p, order])[0]
                for q in qs_:
                    X, col, pin = prep(invs[q], p, order, cti)
                    b = max(anneal_one(X, col, p, pin, QG, 60000, s) for s in range(3))
                    res.append((b[0], p, order, int(q), ''.join(AZ[x] for x in b[1])))
        res.sort(key=lambda r: -r[0])
        print(lab, 'n', len(res), 'time', round(time.time() - t), flush=True)
        for r in res[:8]: print('  ', round(r[0], 3), r[1:4], r[4])
