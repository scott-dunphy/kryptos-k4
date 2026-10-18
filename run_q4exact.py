"""TEAM anneal: exact crib-consistency for Quagmire IV with FREE PT/CT alphabets + periodic key, p<=7.
Enumerate k (k[0]=0 gauge) and run run_gromark.consistent (weighted union-find, dual alphabets).
Random-keystream calibration: fraction of random 97-digit keystreams (base 26) passing = 4.3e-4 (E-G)."""
import sys, time, numpy as np
from numba import njit, prange
from run_gromark import consistent, PL, CL, CI

@njit(parallel=True, cache=True)
def sweep(p, total, cta_pl, cta_cl, ci, flags):
    for code in prange(total):
        k = np.zeros(p, dtype=np.int64)
        c = code + 0
        for j in range(1, p):
            k[j] = c % 26; c //= 26
        d = np.empty(97, dtype=np.int64)
        for i in range(97):
            d[i] = k[i % p]
        flags[code] = 1 if consistent(d, 0, cta_pl, cta_cl, ci) else 0

if __name__ == "__main__":
    for p in [int(x) for x in sys.argv[1].split(",")]:
        total = 26 ** (p - 1); t = time.time()
        flags = np.zeros(total, dtype=np.uint8)
        sweep(p, total, PL, CL, CI, flags)
        n = int(flags.sum())
        print(f"p={p} keys={total} consistent={n} rate={n/total:.2e} t={time.time()-t:.1f}s ex={np.nonzero(flags)[0][:5].tolist()}", flush=True)
