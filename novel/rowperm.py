"""Row-permutation transposition (strip cipher): write PT in rows of width w, reorder full rows, read rows;
short last row fixed at end. Preserves residues mod w => compatible with Bean's width-7/21 CT statistics.
Combined with periodic substitution (p 1-30, 12 variants, both orders). DFS over assignments of crib-bearing rows."""
import sys
import numpy as np
from numba import njit, prange
sys.path.insert(0, '.')
import cribfilter as cf

@njit(cache=True)
def dfs(level, crow_list, nfull, w, p, order, v, used, key, kcnt, KV, CTI, cr_pos, cr_let, cr_start, cr_end, res, maxres, nres, assign):
    if level == crow_list.shape[0]:
        # count m
        distinct = 0
        for r in range(p):
            if kcnt[r] > 0: distinct += 1
        m = cr_pos.shape[0] - distinct
        if m >= 4:
            if nres[0] < maxres:
                k = nres[0]
                res[k, 0] = m
                for t in range(crow_list.shape[0]): res[k, 1 + t] = assign[t]
            nres[0] += 1
        return
    r = crow_list[level]
    for s in range(nfull):
        if used[s]: continue
        # try placing PT row r at CT row s
        ok = True
        placed = 0
        for t in range(cr_start[level], cr_end[level]):
            i = cr_pos[t]
            j = s * w + (i - r * w)
            rr = (j % p) if order == 0 else (i % p)
            kk = KV[v, cr_let[t], CTI[j]]
            if kcnt[rr] == 0:
                key[rr] = kk
            elif key[rr] != kk:
                ok = False
            if not ok:
                break
            kcnt[rr] += 1
            placed += 1
        if ok:
            used[s] = True; assign[level] = s
            dfs(level + 1, crow_list, nfull, w, p, order, v, used, key, kcnt, KV, CTI, cr_pos, cr_let, cr_start, cr_end, res, maxres, nres, assign)
            used[s] = False
        # undo
        for t in range(cr_start[level], cr_start[level] + placed):
            i = cr_pos[t]
            j = s * w + (i - r * w)
            rr = (j % p) if order == 0 else (i % p)
            kcnt[rr] -= 1

def run(w, pmin, pmax, CTI, minm):
    R = -(-97 // w); nfull = 97 // w
    cpos = sorted(cf.CRIB_POS)
    crows = sorted(set(i // w for i in cpos))
    cr_pos, cr_let, cs, ce = [], [], [], []
    for r in crows:
        cs.append(len(cr_pos))
        for i in cpos:
            if i // w == r:
                cr_pos.append(i); cr_let.append(ord(cf.CRIB_POS[i]) - 65)
        ce.append(len(cr_pos))
    args = [np.array(x, np.int64) for x in (crows, cr_pos, cr_let, cs, ce)]
    hits = []
    for p in range(pmin, pmax + 1):
        for order in range(2):
            for v in range(cf.NV):
                res = np.zeros((2000, 1 + len(crows)), np.int64); nres = np.zeros(1, np.int64)
                dfs(0, args[0], nfull, w, p, order, v, np.zeros(nfull, np.bool_), np.zeros(64, np.int64),
                    np.zeros(64, np.int64), cf.KV, CTI, args[1], args[2], args[3], args[4], res, 2000, nres,
                    np.zeros(len(crows), np.int64))
                for k in range(min(nres[0], 2000)):
                    if res[k, 0] >= minm:
                        hits.append((w, p, order, v, int(res[k, 0]), tuple(res[k, 1:].tolist())))
    return hits, crows, nfull

if __name__ == '__main__':
    import random
    from collections import Counter
    wmin, wmax = int(sys.argv[1]), int(sys.argv[2])
    for lab, cti in [('REAL', cf.CTI), ('SHUF', np.array(random.Random(3).sample(list(cf.CTI), 97), np.int64))]:
        for w in range(wmin, wmax + 1):
            hits, crows, nfull = run(w, 1, 30, cti, 4)
            c = Counter((h[4]) for h in hits)
            strong = [h for h in hits if h[4] >= 6 or (h[4] >= 5 and h[1] <= 20)]
            print(lab, 'w', w, 'crib rows', crows, 'full rows', nfull, 'hits m>=4 by m', sorted(c.items()), 'strong', len(strong), flush=True)
            if lab == 'REAL':
                for h in strong[:8]: print('    ', h, cf.VARIANTS[h[3]][:3])
