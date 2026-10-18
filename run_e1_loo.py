"""E1 with crib-typo tolerance: drop each of the 24 crib letters in turn (also variant: CT letter in crib zone miscarved)."""
import numpy as np, time
from multiprocessing import Pool
import cribfilter as cf
from perms import route_perms, columnar_all, inverse

P = [np.arange(97)] + [p for _, p in route_perms(97)] + [p for _, p in columnar_all(97, 8)]
P = P + [inverse(p) for p in P]
INVS = np.array([inverse(p) for p in P])

def job(drop):
    keep = [t for t in range(24) if t != drop]
    ci = cf.CRIB_I[keep].copy(); cl = cf.CRIB_L[keep].copy()
    out = np.zeros((10000, 5), dtype=np.int64)
    n = cf.check_batch(INVS, 1, 22, cf.KV, cf.CTI, ci, cl, 5, out)
    return drop, n, out[:n].tolist()

if __name__ == "__main__":
    t = time.time()
    with Pool(8) as pool:
        for drop, n, rows in pool.imap_unordered(job, range(24)):
            print("drop crib", int(cf.CRIB_I[drop]), "survivors", n, rows[:3], flush=True)
    print("done", round(time.time() - t), "s")
