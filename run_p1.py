"""P1: crib-error tolerance t<=2 over E1 space (identity, routes, columnar<=8), p1-20."""
import numpy as np, time
from multiprocessing import Pool
import cribfilter as cf
from perms import route_perms, columnar_all, inverse
from k4lib import qscore

P = [np.arange(97)] + [p for _, p in route_perms(97)] + [p for _, p in columnar_all(97, 8)]
P = P + [inverse(p) for p in P]
INVS = np.array([inverse(p) for p in P])

def job(chunk):
    lo, hi = chunk
    out = np.zeros((200000, 6), dtype=np.int64)
    n = cf.check_tolerant(INVS[lo:hi], 1, 20, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 2, 6, out)
    rows = out[:n].copy(); rows[:, 0] += lo
    return rows

if __name__ == "__main__":
    t = time.time()
    chunks = [(i, min(i + 2000, len(INVS))) for i in range(0, len(INVS), 2000)]
    with Pool(8) as pool:
        rows = np.concatenate(pool.map(job, chunks))
    print("survivors", len(rows), round(time.time() - t), "s")
    from collections import Counter
    print("by (err, m-err):", sorted(Counter(zip(rows[:, 5].tolist(), (rows[:, 4] - rows[:, 5]).tolist())).items())[:30])
    res = []
    for q, p, o, v, m, e in rows:
        inv = INVS[q]; perm = np.argsort(inv)
        key = [-1] * p
        # mode key per residue
        from collections import defaultdict
        d = defaultdict(list)
        for tt in range(24):
            i = int(cf.CRIB_I[tt]); j = int(inv[i]); r = (j % p) if o == 0 else (i % p)
            d[r].append(int(cf.KV[v, cf.CRIB_L[tt], cf.CTI[j]]))
        for r, ks in d.items():
            key[r] = max(set(ks), key=ks.count)
        free = [r for r in range(p) if key[r] < 0]
        for r in free: key[r] = 0
        best = qscore(cf.full_decrypt(inv, perm, p, o, v, key))
        for _ in range(2):
            for r in free:
                for k in range(26):
                    old = key[r]; key[r] = k
                    s = qscore(cf.full_decrypt(inv, perm, p, o, v, key))
                    if s > best: best = s
                    else: key[r] = old
        res.append((best, int(q), int(p), int(o), cf.VARIANTS[v][:3], int(m), int(e), cf.full_decrypt(inv, perm, p, o, v, key)))
    res.sort(reverse=True)
    import json
    with open("results/p1_tolerant.jsonl", "w") as f:
        for r in res: f.write(json.dumps(r) + "\n")
    for r in res[:15]: print(round(r[0], 3), r[1:7], r[7])
