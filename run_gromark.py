"""Generalized Gromark / VIC chain-addition keystream with unknown mixed alphabets.

Keystream digits: primer of length L in base b, then d[i] = (d[i-L] + d[i-L+1]) mod b  (Gromark is b=10, L=5).
Encryption model: cpos(C_i) = ppos(P_i) + d_i  (mod 26), ppos/cpos unknown permutations.
Crib test: weighted union-find over letter nodes; reject on cycle contradiction or on two distinct
letters of the same alphabet forced to the same position. mode 0 = dual alphabets (52 nodes),
mode 1 = single alphabet (ppos == cpos, 26 nodes).
Beaufort-sense keys are equivalent under dual alphabets (reverse an alphabet), so not tested separately.
"""
import sys
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
CL = np.array([ord(CT[i]) - 65 for i in CI], dtype=np.int64)


@njit(cache=True)
def find(par, off, x):
    # returns root, offset of x relative to root (pos(x) = pos(root) + off)
    o = 0
    while par[x] != x:
        o += off[x]
        x = par[x]
    return x, o % 26


@njit(cache=True)
def consistent(d, mode, PL, CL, CI):
    nn = 52
    par = np.arange(nn)
    off = np.zeros(nn, dtype=np.int64)
    for t in range(CI.shape[0]):
        k = d[CI[t]]
        a = PL[t]
        b = CL[t] + (26 if mode != 1 else 0)
        # constraint: pos(b) - pos(a) = k
        ra, oa = find(par, off, a)
        rb, ob = find(par, off, b)
        if ra == rb:
            if (ob - oa - k) % 26 != 0:
                return False
        else:
            # attach rb under ra: pos(rb) = pos(ra) + x ; need ob + x - oa = k
            par[rb] = ra
            off[rb] = (k + oa - ob) % 26
    # injectivity: same-alphabet letters in same component need distinct offsets
    seen = np.full((nn, 26), -1, dtype=np.int64)
    used = np.zeros(nn, dtype=np.int64)
    for t in range(CI.shape[0]):
        used[PL[t]] = 1
        used[CL[t] + (26 if mode != 1 else 0)] = 1
    for x in range(nn):
        if used[x] == 0:
            continue
        r, o = find(par, off, x)
        side = 0 if (x < 26 or mode == 1) else 1
        if side == 0:
            if seen[r, o] != -1 and seen[r, o] != x:
                return False
            seen[r, o] = x
    seen2 = np.full((nn, 26), -1, dtype=np.int64)
    if mode != 1:
        for x in range(26, 52):
            if used[x] == 0:
                continue
            r, o = find(par, off, x)
            if seen2[r, o] != -1 and seen2[r, o] != x:
                return False
            seen2[r, o] = x
    return True


@njit(parallel=True, cache=True)
def sweep(b, L, mode, PL, CL, CI, total, hits_out):
    flags = np.zeros(total, dtype=np.uint8)
    for code in prange(total):
        d = np.empty(97, dtype=np.int64)
        cc = code + 0
        for i in range(L):
            d[L - 1 - i] = cc % b
            cc = cc // b
        for i in range(L, 97):
            d[i] = (d[i - L] + d[i - L + 1]) % b
        if consistent(d, mode, PL, CL, CI):
            flags[code] = 1
    n = 0
    for code in range(total):
        if flags[code] and n < hits_out.shape[0]:
            hits_out[n] = code
            n += 1
    return n


def digits(code, b, L):
    out = []
    for _ in range(L):
        out.append(code % b); code //= b
    return out[::-1]


if __name__ == "__main__":
    configs = [(10, 5), (10, 4), (10, 6), (10, 7), (8, 5), (8, 6), (8, 7), (12, 5), (12, 6), (5, 5), (5, 7),
               (5, 8), (6, 6), (7, 6), (9, 6), (24, 4), (24, 5), (26, 4), (26, 5), (2, 20), (3, 12), (4, 10)]
    hits_out = np.zeros(2_000_000, dtype=np.int64)
    for mode in (1, 0):
        for b, L in configs:
            total = b ** L
            if total > 30_000_000:
                continue
            t = time.time()
            n = sweep(b, L, mode, PL, CL, CI, total, hits_out)
            ex = [digits(int(c), b, L) for c in hits_out[:min(n, 5)]]
            print(f"mode={'single' if mode == 1 else 'dual'} base={b} L={L} primers={total} survivors={n} "
                  f"rate={n / total:.2e} t={time.time() - t:.1f}s ex={ex}", flush=True)
            np.save(f"results/gromark_m{mode}_b{b}_L{L}.npy", hits_out[:n].copy())
