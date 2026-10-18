"""E3: null removal (single position; periodic strides 14-48) then identity/routes/columnar(<=6) + periodic sub p1-26."""
import time
import numpy as np
from multiprocessing import Pool
import cribfilter as cf
from perms import route_perms, columnar_all, inverse
from k4lib import CT, CRIB_POS, to_idx

_cache = {}
def perm_set(n):
    if n not in _cache:
        P = [np.arange(n)] + [p for _, p in route_perms(n)] + [p for _, p in columnar_all(n, 6)]
        P = P + [inverse(p) for p in P]
        _cache[n] = np.array([inverse(p) for p in P])
    return _cache[n]

def job(rem):
    keep = [i for i in range(97) if i not in rem]
    ct2 = to_idx("".join(CT[i] for i in keep))
    ci = np.array([keep.index(i) for i in sorted(CRIB_POS)], dtype=np.int64)
    out = np.zeros((10000, 6), dtype=np.int64)
    n = cf.check_prog(perm_set(len(keep)), 1, 26, 0, cf.KV, ct2, ci, cf.CRIB_L, 5, out)
    return rem, n, out[:n].tolist()

if __name__ == "__main__":
    removals = [(x,) for x in range(97)]
    removals += [tuple(range(o, 97, s)) for s in range(14, 49) for o in range(s)]
    removals += [(0, 96)]
    removals = [r for r in removals if not any(x in CRIB_POS for x in r)]
    t = time.time(); total = 0
    with Pool(8) as pool:
        for rem, n, rows in pool.imap_unordered(job, removals):
            total += n
            if n: print("HIT", rem, n, rows[:3], flush=True)
    print("E3 removals", len(removals), "total survivors", total, round(time.time() - t, 1), "s")
