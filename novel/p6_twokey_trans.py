"""P6(2) split key over the E1 transposition set: key at position x is A[x%a] + B[x%b] (a<b, a+b<=17, b%a != 0),
x = CT slot j (order A: transpose then substitute) or PT index i (order B). 12 variants. Consistency by Gaussian
elimination mod 2 and mod 13 on the 24 x (a+b) system with 12 RHS columns at once."""
import sys, time
import numpy as np
from numba import njit, prange
sys.path.insert(0, '.')
import cribfilter as cf
from perms import route_perms, columnar_all, columnar_keywords, inverse

@njit(cache=True)
def consistent_mod(xs, a, b, RHS, m, okv):
    """xs: (24,) positions; RHS: (24,V). okv[v] &= consistent mod m."""
    n = xs.shape[0]; u = a + b; V = RHS.shape[1]
    M = np.zeros((n, u + V), np.int64)
    for t in range(n):
        M[t, xs[t] % a] = 1; M[t, a + xs[t] % b] = 1
        for v in range(V): M[t, u + v] = RHS[t, v] % m
    r = 0
    for c in range(u):
        pr = -1
        for i in range(r, n):
            if M[i, c] % m != 0:
                pr = i; break
        if pr < 0: continue
        if pr != r:
            for k in range(u + V):
                tmp = M[r, k]; M[r, k] = M[pr, k]; M[pr, k] = tmp
        inv = 1
        for z in range(1, m):
            if (M[r, c] * z) % m == 1: inv = z; break
        for k in range(u + V): M[r, k] = (M[r, k] * inv) % m
        for i in range(n):
            if i != r and M[i, c] != 0:
                f = M[i, c]
                for k in range(u + V): M[i, k] = (M[i, k] - f * M[r, k]) % m
        r += 1
    for i in range(r, n):
        for v in range(V):
            if M[i, u + v] != 0: okv[v] = False
    return n - r  # number of checks

@njit(parallel=True, cache=True)
def scan(invs, pairs, KV, CTI, CI, CL, out, chk):
    nP = invs.shape[0]; V = KV.shape[0]; nc = CI.shape[0]
    for q in prange(nP):
        inv = invs[q]
        xs = np.empty(nc, np.int64); RHS = np.empty((nc, V), np.int64); okv = np.empty(V, np.bool_)
        for t in range(nc):
            for v in range(V): RHS[t, v] = KV[v, CL[t], CTI[inv[CI[t]]]]
        for order in range(2):
            for t in range(nc): xs[t] = inv[CI[t]] if order == 0 else CI[t]
            for pi in range(pairs.shape[0]):
                a = pairs[pi, 0]; b = pairs[pi, 1]
                for v in range(V): okv[v] = True
                c2 = consistent_mod(xs, a, b, RHS, 2, okv)
                c13 = consistent_mod(xs, a, b, RHS, 13, okv)
                for v in range(V):
                    if okv[v]:
                        out[q, order, pi] += 1
                        chk[q, order, pi] = min(c2, c13)

def perm_set():
    WORDS = ("KRYPTOS PALIMPSEST ABSCISSA BERLIN CLOCK WELTZEITUHR ALEXANDERPLATZ SANBORN SCHEIDT WEBSTER "
             "LANGLEY SHADOW LAYERTWO EGYPT CAIRO NILE PYRAMID MESSAGE ANTIPODES IQLUSION UNDERGROUND "
             "LUCID MEMORY TUTANKHAMUN CARTER HOWARDCARTER VIRGINIA CIA URANIA WORLDCLOCK TIME HOUR "
             "MAGNETIC COMPASS NORTHEAST EAST DELIVERINGAMESSAGE LIGHT WALL BERLINWALL ALEX TWENTYFOUR ZEIT "
             "WELT UHR SECRET HIDDEN INVISIBLE SLOWLY DESPERATELY ENIGMA CODE CIPHER").split()
    perms = [np.arange(97)]
    for gen in (route_perms(97), columnar_all(97, 8), columnar_keywords(97, WORDS)):
        for l, p in gen: perms.append(p)
    P2 = []
    for p in perms: P2 += [p, inverse(p)]
    return np.array([inverse(p) for p in P2])

if __name__ == '__main__':
    import random
    pairs = np.array([(a, b) for a in range(2, 17) for b in range(a + 1, 17) if a + b <= 17 and b % a != 0], np.int64)
    invs = perm_set()
    if len(sys.argv) > 1: invs = invs[:int(sys.argv[1])]
    print('perms', len(invs), 'pairs', len(pairs), flush=True)
    for lab, cti in [('REAL', cf.CTI), ('SHUF', np.array(random.Random(11).sample(list(cf.CTI), 97), np.int64))]:
        out = np.zeros((len(invs), 2, len(pairs)), np.int32); chk = np.zeros((len(invs), 2, len(pairs)), np.int32)
        t = time.time(); scan(invs, pairs, cf.KV, cti, cf.CRIB_I, cf.CRIB_L, out, chk)
        hits = np.argwhere(out > 0)
        print(lab, 'time', round(time.time() - t), 's; consistent (perm,order,pair) cells', len(hits),
              'variant-hits', int(out.sum()), flush=True)
        from collections import Counter
        print('   by checks:', sorted(Counter(chk[tuple(hits.T)].tolist()).items()) if len(hits) else [])
        for q, o, pi in hits[:15]:
            print('   ', q, 'order', o, 'pair', tuple(pairs[pi]), 'checks', chk[q, o, pi], 'nvar', out[q, o, pi])
