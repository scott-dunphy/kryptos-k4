"""S5: the '?' before OBKR as part of K4 -> 98 = 7x14 = 2x49 symbols, exact rectangles for K3-style rotation.
Treat '?' as a non-constraining symbol. PT crib offset s in {0,1}. Transpositions: routes W2-49 (both ragged blank
positions), all columnar W<=8, K3-style double rotations on exact grids (fill rows, rotate cw/ccw, re-cut, rotate) and
their pairwise compositions with routes on exact grids. x periodic p1-26 x 12 variants x 2 orders."""
import time, itertools
from numba import njit
from common import *
from perms import route_perms, columnar_all, inverse
from k4lib import CRIB_POS

CT98 = "?" + CT
CTI98 = np.array([-1] + [AZ.index(c) for c in CT], dtype=np.int64)

@njit(cache=True)
def check98(invs, pmin, pmax, KV, CTI, CI, CL, min_m, out):
    nperm = invs.shape[0]; nv = KV.shape[0]; nc = CI.shape[0]; cnt = 0
    key = np.empty(128, dtype=np.int64)
    for q in range(nperm):
        inv = invs[q]
        for p in range(pmin, pmax + 1):
            for order in range(2):
                for v in range(nv):
                    for r in range(p): key[r] = -1
                    ok = True; distinct = 0; used = 0
                    for t in range(nc):
                        i = CI[t]; j = inv[i]
                        if CTI[j] < 0: continue
                        used += 1
                        r = (j % p) if order == 0 else (i % p)
                        k = KV[v, CL[t], CTI[j]]
                        if key[r] == -1:
                            key[r] = k; distinct += 1
                        elif key[r] != k:
                            ok = False; break
                    if ok:
                        m = used - distinct
                        if m >= min_m and cnt < out.shape[0]:
                            out[cnt, 0] = q; out[cnt, 1] = p; out[cnt, 2] = order; out[cnt, 3] = v; out[cnt, 4] = m
                            cnt += 1
    return cnt

def rot_perm(R, W, cw=True):
    """perm for reading an R x W row-major grid after rotating 90 deg: out[j] = in[perm[j]]."""
    idx = np.arange(R * W).reshape(R, W)
    g = np.rot90(idx, -1 if cw else 1)
    return g.flatten()

def k3_doubles(n):
    out = []
    facs = [w for w in range(2, n) if n % w == 0]
    for W1 in facs:
        for cw1 in (True, False):
            p1 = rot_perm(n // W1, W1, cw1)
            for W2 in facs:
                for cw2 in (True, False):
                    p2 = rot_perm(n // W2, W2, cw2)
                    out.append((f"K3dbl W{W1}{'cw' if cw1 else 'ccw'} W{W2}{'cw' if cw2 else 'ccw'}", p1[p2]))
            out.append((f"rot W{W1}{'cw' if cw1 else 'ccw'}", p1))
    return out

if __name__ == "__main__":
    t = time.time()
    n = 98
    base = list(route_perms(n)) + list(columnar_all(n, 8)) + k3_doubles(n)
    labels, invs, seen = [], [], set()
    for lab, p in base:
        for tag, q in (("", p), ("inv ", inverse(p))):
            inv = inverse(q); k = inv.tobytes()
            if k in seen: continue
            seen.add(k); labels.append(tag + lab); invs.append(inv)
    invs = np.array(invs)
    print("perms", len(invs), flush=True)
    out = np.zeros((100000, 5), dtype=np.int64)
    for s in (0, 1):
        CI = np.array(sorted(i + s for i in CRIB_POS), dtype=np.int64)
        CL = np.array([AZ.index(CRIB_POS[i - s]) for i in CI], dtype=np.int64)
        tot = 0
        for b in range(0, len(invs), 20000):
            c = check98(invs[b:b+20000], 1, 26, cf.KV, CTI98, CI, CL, 5, out)
            for row in out[:c]:
                q, p, order, v, m = row
                print("HIT s", s, labels[b+q], "p", p, "order", order, cf.VARIANTS[v][:3], "m", m)
            tot += c
        print("offset", s, "survivors m>=5:", tot, flush=True)
    print("time", time.time() - t)
