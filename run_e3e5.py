"""E5: progressive periodic keys (drift d per cycle) over identity+routes+columnar.
E3: single/double null removal (and periodic null strides) + routes on reduced text, periodic & progressive."""
import sys, time, itertools
import numpy as np
import cribfilter as cf
from perms import route_perms, columnar_all, inverse
from k4lib import CT, CRIB_POS, AZ, to_idx

def perm_set(n, wmax_col=7):
    P = [np.arange(n)]
    for _, p in route_perms(n):
        P.append(p)
    for _, p in columnar_all(n, wmax_col):
        P.append(p)
    P = P + [inverse(p) for p in P]
    return np.array([inverse(p) for p in P])

mode = sys.argv[1]
out = np.zeros((1_000_000, 6), dtype=np.int64)
if mode == "e5":
    invs = perm_set(97)
    t = time.time()
    n = cf.check_prog(invs, 1, 30, 25, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 5, out)
    print("E5 perms", len(invs), "survivors m>=5:", n, round(time.time()-t,1), "s")
    for r in out[:n][:20]: print(r)
elif mode == "e3":
    # remove k positions (single nulls everywhere; pairs; periodic strides), run identity+routes, periodic+progressive
    removals = [(x,) for x in range(97)]
    removals += [tuple(range(o, 97, s)) for s in range(14, 49) for o in range(s)]
    removals = [r for r in removals if not any(x in CRIB_POS for x in r)]
    cache = {}
    total = 0; t = time.time()
    for rem in removals:
        keep = [i for i in range(97) if i not in rem]
        n2 = len(keep)
        ct2 = to_idx("".join(CT[i] for i in keep))
        ci = np.array([keep.index(i) for i in sorted(CRIB_POS)], dtype=np.int64)
        if n2 not in cache:
            cache[n2] = perm_set(n2, 6)
        invs = cache[n2]
        n = cf.check_prog(invs, 1, 26, 0 if len(rem) > 1 else 25, cf.KV, ct2, ci, cf.CRIB_L, 5, out)
        total += n
        if n:
            print("HIT rem", rem, n, out[:min(n,5)])
    print("E3 removals", len(removals), "total survivors", total, round(time.time()-t,1), "s")
