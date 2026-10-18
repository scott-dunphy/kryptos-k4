"""E2: double route transposition (K3-style) + periodic substitution p 1..24, 12 variants, 2 orders."""
import time
import numpy as np
from multiprocessing import Pool
import cribfilter as cf
from perms import cell_orders, inverse


def base_routes(n=97, widths=range(2, 50)):
    """Fill row-major, read in each of 16 orders, blanks at end/start; plus inverses."""
    res = []
    for W in widths:
        R = -(-n // W)
        blanks = R * W - n
        orders = cell_orders(R, W)
        for bpos in ("end", "start") if blanks else ("end",):
            if bpos == "end":
                valid = {(r, c) for r in range(R) for c in range(W) if r * W + c < n}
            else:
                valid = {(r, c) for r in range(R) for c in range(W) if r * W + c >= blanks}
            fc = [x for x in orders["row"] if x in valid]
            pos = {cell: i for i, cell in enumerate(fc)}
            for rname, rcells in orders.items():
                if rname == "row":
                    continue
                p = np.array([pos[x] for x in rcells if x in valid], dtype=np.int64)
                res.append((f"W{W}{bpos[0]}{rname}", p))
                res.append((f"W{W}{bpos[0]}{rname}^-1", inverse(p)))
    return res


R = base_routes()
RP = np.array([p for _, p in R])


def job(a):
    comp = RP[a][RP]                 # composed perms: apply R[a] then R[b]
    invs = np.argsort(comp, axis=1)  # inverse perms
    out = np.zeros((1000, 5), dtype=np.int64)
    n = cf.check_batch(invs, 1, 24, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 5, out)
    return a, [(R[a][0], R[int(q)][0], int(p), int(o), int(v), int(m)) for q, p, o, v, m in out[:n]]


if __name__ == "__main__":
    print("base routes", len(R), "pairs", len(R) ** 2, flush=True)
    t = time.time(); hits = []
    with Pool(7) as pool:
        for k, (a, h) in enumerate(pool.imap_unordered(job, range(len(R)), chunksize=4)):
            hits += h
            if h:
                print("HIT", h[:3], flush=True)
            if k % 200 == 0:
                print("progress", k, len(R), round(time.time() - t), "s", flush=True)
    print("done; survivors", len(hits), round(time.time() - t), "s")
    import json
    json.dump(hits, open("results/e2_hits.json", "w"))
