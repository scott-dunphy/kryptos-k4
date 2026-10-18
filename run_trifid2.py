"""T1b: trifid with the 5 non-identity coordinate-role permutations of each keyed cube (layer/row/col roles)."""
import itertools, time, numpy as np, sys
sys.argv = ["x"]
src = open("run_trifid.py").read().split("t = time.time()")[0]
exec(compile(src.replace("cache=True", "cache=False"), "trifid_src", "exec"))
best = np.zeros(len(CUBES), dtype=np.int64); bp = np.zeros((len(CUBES), 2), dtype=np.int64)
for pi, perm in enumerate(itertools.permutations(range(3))):
    if perm == (0, 1, 2): continue
    # new cell index for old cell c=(d0,d1,d2): digits permuted
    idx = np.empty(27, dtype=np.int64)
    for c in range(27):
        d = (c // 9, (c // 3) % 3, c % 3); e = [d[perm[k]] for k in range(3)]
        idx[e[0] * 9 + e[1] * 3 + e[2]] = c
    C2 = CUBES[:, idx].copy()
    out = np.zeros((len(C2), 2), dtype=np.int64); sweep(C2, CTI, CI, CL, out)
    upd = out[:, 0] > best; best[upd] = out[upd, 0]; bp[upd, 0] = out[upd, 1]; bp[upd, 1] = pi
    print(perm, "max", out[:, 0].max(), flush=True)
print("hist", np.bincount(best))
