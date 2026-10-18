"""Sexagesimal / 'change the language base' tests (direct, single unknown mixed alphabet + sign flip).

S1  base-60 chain addition: d[i] = d[i-L] + d[i-L+1] (mod 60) or d[i-L]+d[i-1], primer L=2..4, shift = d mod 26.
S2  clock-time keys: time t0 + i*step (seconds, wrap 86400), shift = f(H,M,S) for several f, all t0, many steps.
S3  base-b digit-wise addition: letter value v (0..25) written as k digits in base b (b^k >= 26), add key digits
    digit-wise mod b, read back -> value w; valid only if w < 26 for all 97 positions (non-bijective otherwise,
    so checked separately). Key digits from chain addition base b (primer L<=4) .
Crib test for S1/S2: run_gromark.consistent(mode=1) (single unknown alphabet: cpos(C) = ppos(P) + shift).
Validation: planted examples. Null: random shifts (known pass rate ~0).
"""
import time
import numpy as np
from numba import njit, prange
import run_gromark as g
from k4lib import CT, CRIB_POS

CTA = np.array([ord(c) - 65 for c in CT], dtype=np.int64)


@njit(cache=True)
def test_shift(d, PL, CL, CI):
    if g.consistent(d, 1, PL, CL, CI):
        return 1
    e = np.empty(97, dtype=np.int64)
    for i in range(97):
        e[i] = (26 - d[i]) % 26
    if g.consistent(e, 1, PL, CL, CI):
        return 2
    return 0


@njit(parallel=True, cache=True)
def s1(L, rule, PL, CL, CI, flags):
    total = 60 ** L
    for code in prange(total):
        d60 = np.empty(97, dtype=np.int64)
        c = code + 0
        for i in range(L):
            d60[L - 1 - i] = c % 60
            c = c // 60
        for i in range(L, 97):
            if rule == 0:
                d60[i] = (d60[i - L] + d60[i - L + 1]) % 60
            else:
                d60[i] = (d60[i - L] + d60[i - 1]) % 60
        d = np.empty(97, dtype=np.int64)
        for i in range(97):
            d[i] = d60[i] % 26
        flags[code] = test_shift(d, PL, CL, CI)


@njit(parallel=True, cache=True)
def s2(steps, PL, CL, CI, flags):
    # flags[t0, step_idx, f]
    for t0 in prange(86400):
        d = np.empty(97, dtype=np.int64)
        for si in range(steps.shape[0]):
            st = steps[si]
            for f in range(8):
                for i in range(97):
                    t = (t0 + i * st) % 86400
                    H = t // 3600; M = (t // 60) % 60; S = t % 60
                    if f == 0:
                        v = H
                    elif f == 1:
                        v = M
                    elif f == 2:
                        v = S
                    elif f == 3:
                        v = H + M
                    elif f == 4:
                        v = H + M + S
                    elif f == 5:
                        v = (H % 12)
                    elif f == 6:
                        v = M // 5          # minute-hand hour mark
                    else:
                        v = (H * 60 + M)    # minutes since midnight
                    d[i] = v % 26
                r = test_shift(d, PL, CL, CI)
                if r:
                    flags[t0, si, f] = r


@njit(cache=True)
def baseb_valid_and_consistent(b, k, keyd, PTI, CTA, CI):
    """Direct digit-wise check at crib positions only: enc(P) must equal C. keyd: (97, k) digits.
    Returns number of crib positions matching (24 = consistent)."""
    m = 0
    for t in range(CI.shape[0]):
        i = CI[t]
        v = PTI[t]
        w = 0; mult = 1
        for j in range(k):
            dig = (v // mult) % b
            w += ((dig + keyd[i, j]) % b) * mult
            mult *= b
        if w == CTA[i]:
            m += 1
    return m


@njit(parallel=True, cache=True)
def s3(b, k, L, PTI, CTA, CI, best):
    total = b ** L
    for code in prange(total):
        n = 97 * k
        d = np.empty(n, dtype=np.int64)
        c = code + 0
        for i in range(L):
            d[L - 1 - i] = c % b
            c = c // b
        for i in range(L, n):
            d[i] = (d[i - L] + d[i - L + 1]) % b
        keyd = d.reshape(97, k)
        best[code] = baseb_valid_and_consistent(b, k, keyd, PTI, CTA, CI)


if __name__ == "__main__":
    PL, CL, CI = g.PL, g.CL, g.CI
    # ---- validation for S1: plant base-60 chain key under a random single alphabet
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    rng = np.random.default_rng(5)
    alpha = rng.permutation(26); pos = np.argsort(alpha)
    d60 = [17, 42, 5]
    for i in range(3, 97):
        d60.append((d60[i - 3] + d60[i - 2]) % 60)
    syn = np.array([alpha[(pos[ord(c) - 65] + d60[i] % 26) % 26] for i, c in enumerate(PT)])
    CLs = syn[CI]
    fl = np.zeros(60 ** 3, dtype=np.int64); s1(3, 0, PL, CLs, CI, fl)
    print("S1 validation planted (17,42,5) found:", bool(fl[(17 * 60 + 42) * 60 + 5]), "total syn hits", int((fl > 0).sum()))
    # ---- S1 real
    for L in (2, 3, 4):
        for rule in (0, 1):
            t = time.time()
            fl = np.zeros(60 ** L, dtype=np.int64)
            s1(L, rule, PL, CL, CI, fl)
            print(f"S1 base60 chain L={L} rule={rule} primers={60 ** L} hits={int((fl > 0).sum())} {time.time() - t:.1f}s", flush=True)
    # ---- S2 clock time keys
    steps = np.array(sorted(set([1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 45, 60, 90, 120, 180, 300, 360, 600, 720, 900,
                                 1200, 1800, 2700, 3600, 5400, 7200, 10800, 14400, 21600, 43200, 3599, 3601, 61, 59,
                                 86399, 86340, 86100])), dtype=np.int64)
    t = time.time()
    fl2 = np.zeros((86400, len(steps), 8), dtype=np.int8)
    s2(steps, PL, CL, CI, fl2)
    print(f"S2 clock-time keys: streams={86400 * len(steps) * 8} hits={int((fl2 > 0).sum())} {time.time() - t:.1f}s", flush=True)
    # ---- S3 base-b digitwise addition with chain keys
    PTI = PL.copy()
    for b, k in ((6, 2), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2), (12, 2), (3, 3), (4, 3), (5, 3), (2, 5)):
        for L in (2, 3, 4, 5):
            if b ** L > 3_000_000:
                continue
            best = np.zeros(b ** L, dtype=np.int64)
            s3(b, k, L, PTI, CTA, CI, best)
            print(f"S3 base{b} k={k} chain L={L} keys={b ** L} max crib matches={int(best.max())}/24", flush=True)
