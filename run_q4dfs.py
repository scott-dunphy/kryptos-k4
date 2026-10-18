"""TEAM anneal: exact enumeration of crib-consistent periodic keys for Quagmire IV with FREE alphabets (p>=8),
by DFS over residues with union-find pruning on cribs of assigned residues. Gauge: first residue key = 0.
Usage: run_q4dfs.py p [shuffle_seed]  -> count + keys saved to results/anneal/q4keys_p{p}.npy"""
import sys, time, numpy as np
from numba import njit
from run_gromark import consistent
from k4lib import CT, CRIB_POS

@njit(cache=True)
def dfs(p, order, PLr, CLr, CIr, cnt_r, maxout, out, stop=-1):
    # order: residues sorted; PLr/CLr/CIr: cribs grouped by residue order, cnt_r cumulative counts
    k = np.zeros(p, dtype=np.int64)
    nres = order.shape[0]
    stack = np.zeros(nres + 1, dtype=np.int64)
    level = 1  # level 0 residue fixed to 0
    stack[1] = -1
    n = 0
    d = np.zeros(97, dtype=np.int64)
    while level >= 1:
        stack[level] += 1
        if stack[level] >= 26:
            level -= 1
            continue
        k[order[level]] = stack[level]
        m = cnt_r[level + 1]
        for t in range(m):
            d[CIr[t]] = k[CIr[t] % p]
        if consistent(d, 0, PLr[:m], CLr[:m], CIr[:m]):
            if level == nres - 1:
                if n < maxout:
                    out[n] = k
                n += 1
                if n == stop:
                    return n
            else:
                level += 1
                stack[level] = -1
    return n

def setup(p, ct):
    ci = np.array(sorted(CRIB_POS)); res = ci % p
    rs = sorted(set(res.tolist()), key=lambda r: -np.sum(res == r))
    idx = np.concatenate([ci[res == r] for r in rs])
    PL = np.array([ord(CRIB_POS[i]) - 65 for i in idx]); CL = np.array([ord(ct[i]) - 65 for i in idx])
    cnt = np.cumsum([0] + [int(np.sum(res == r)) for r in rs])
    return np.array(rs), PL, CL, idx.astype(np.int64), cnt.astype(np.int64)

def count(p, ct, maxout=200000, stop=-1):
    order, PL, CL, CI, cnt = setup(p, ct)
    out = np.zeros((maxout, p), dtype=np.int64)
    if len(order) == 1:
        return 1, out[:1]
    n = dfs(p, order, PL, CL, CI, cnt, maxout, out, stop)
    return n, out[:min(n, maxout)]

if __name__ == "__main__":
    p = int(sys.argv[1])
    ct = CT
    if len(sys.argv) > 2:
        rng = np.random.default_rng(int(sys.argv[2])); ct = "".join(rng.permutation(list(CT)))
    t = time.time()
    n, keys = count(p, ct)
    print(f"p={p} shuffle={sys.argv[2] if len(sys.argv)>2 else '-'} consistent_keys={n} (of 26^{p-1}) t={time.time()-t:.1f}s", flush=True)
    if len(sys.argv) == 2:
        np.save(f"results/anneal/q4keys_p{p}.npy", keys)
