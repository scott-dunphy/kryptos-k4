"""Transposition + periodic polyalphabetic with ARBITRARY per-column alphabets: necessary condition = per-column
injectivity of crib PT->CT letters. E1 perm set (identity, routes W2-49, columnar W<=8, fwd+inv), p 1-30, 2 orders.
Reports, per p, number of perms passing and number of 'checks' (crib letters beyond first in each column)."""
import sys, time
import numpy as np
from numba import njit, prange
sys.path.insert(0, '.')
import cribfilter as cf
from perms import route_perms, columnar_all, inverse

@njit(parallel=True, cache=True)
def scan(invs, pmax, CTI, CI, CL, out, chk):
    for q in prange(invs.shape[0]):
        inv = invs[q]
        fwd = np.empty((64, 26), np.int64); bwd = np.empty((64, 26), np.int64)
        for p in range(1, pmax + 1):
            for order in range(2):
                for r in range(p):
                    for x in range(26):
                        fwd[r, x] = -1; bwd[r, x] = -1
                ok = True; n = 0
                for t in range(CI.shape[0]):
                    i = CI[t]; j = inv[i]
                    r = (j % p) if order == 0 else (i % p)
                    P = CL[t]; C = CTI[j]
                    if fwd[r, P] == -1 and bwd[r, C] == -1:
                        fwd[r, P] = C; bwd[r, C] = P
                    elif fwd[r, P] == C:
                        n += 1
                    else:
                        ok = False; break
                if ok:
                    out[q, p, order] = 1
                    chk[q, p, order] = n

if __name__ == '__main__':
    perms = [np.arange(97)]
    for gen in (route_perms(97), columnar_all(97, 8)):
        for l, p in gen: perms.append(p)
    P2 = []
    for p in perms: P2 += [p, inverse(p)]
    invs = np.array([inverse(p) for p in P2])
    print('perms', len(invs), flush=True)
    out = np.zeros((len(invs), 31, 2), np.int8); chk = np.zeros((len(invs), 31, 2), np.int16)
    t = time.time()
    scan(invs, 30, cf.CTI, cf.CRIB_I, cf.CRIB_L, out, chk)
    print('time', round(time.time() - t), flush=True)
    # random-CT control on a subsample
    rng = np.random.default_rng(0)
    for p in range(1, 31):
        print('p', p, 'pass order A', int(out[:, p, 0].sum()), 'order B', int(out[:, p, 1].sum()))
    np.save('results/novel_anypoly_pass.npy', out)
