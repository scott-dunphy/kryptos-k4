"""TEAM clock: test numeric / letter keystreams derived from Berlin clocks against the 24 cribs.

Model (direct, no transposition): key index k[i] = (a * K[o + i] + b) mod 26 for fixed alphabet variant v
(12 variants: Vig/Beau/VarBeau x {AZ,KA}^2). a in UNITS (multiplier; 1 for plain), b = indicator shift.
Score = max over (v, a, b) of #crib positions agreeing (24 = real; FP ~ 26^-23 per test).
"""
import numpy as np
from numba import njit
import cribfilter as cf
from k4lib import AZ, KA, CT, qscore

UNITS = np.array([1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25], dtype=np.int64)
REQ = np.array([cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)  # (12,24)
CI = cf.CRIB_I.copy()


@njit(cache=True)
def scan_num(K, REQ, CI, units, nstart):
    """K: int array (already extended so K[o+96] valid for o<nstart). Returns best[o], and (v,a,b) arg."""
    nv = REQ.shape[0]
    nc = CI.shape[0]
    best = np.zeros(nstart, dtype=np.int64)
    arg = np.zeros((nstart, 3), dtype=np.int64)
    cnt = np.zeros(26, dtype=np.int64)
    for o in range(nstart):
        bb = -1
        for v in range(nv):
            for ai in range(units.shape[0]):
                a = units[ai]
                for x in range(26):
                    cnt[x] = 0
                for t in range(nc):
                    cnt[(REQ[v, t] - a * K[o + CI[t]]) % 26] += 1
                for x in range(26):
                    if cnt[x] > bb:
                        bb = cnt[x]
                        arg[o, 0] = v
                        arg[o, 1] = a
                        arg[o, 2] = x
        best[o] = bb
    return best, arg


def test_seq(K, cyclic=True, units=UNITS, both_dirs=True):
    """Test a sequence at all start offsets (and reversed). Returns (best, offset, dir, v, a, b)."""
    out = (-1,)
    for d in ((0, 1) if both_dirs else (0,)):
        S = np.asarray(K, dtype=np.int64)
        if d:
            S = S[::-1].copy()
        n = len(S)
        if cyclic:
            reps = 97 // n + 2
            E = np.concatenate([S] * reps)
            nstart = n
        else:
            if n < 97:
                continue
            E = S
            nstart = n - 96
        best, arg = scan_num(E, REQ, CI, units, nstart)
        o = int(best.argmax())
        r = (int(best[o]), o, d, *map(int, arg[o]))
        if r[0] > out[0]:
            out = r
    return out


def letters_to_idx(s, alpha=AZ):
    return np.array([alpha.index(c) for c in s], dtype=np.int64)


def decrypt(K, o, d, v, a, b, cyclic=True):
    S = np.asarray(K, dtype=np.int64)
    if d:
        S = S[::-1]
    if cyclic:
        S = np.concatenate([S] * (97 // len(S) + 2))
    pt = []
    for i in range(97):
        k = (a * S[o + i] + b) % 26
        pt.append(AZ[cf.decrypt_letter(v, k, cf.CTI[i])])
    return "".join(pt)


def null_rate(gen, trials=2000, seed=0, **kw):
    """Empirical distribution of best score for random sequences from gen(rng)."""
    rng = np.random.default_rng(seed)
    res = [test_seq(gen(rng), **kw)[0] for _ in range(trials)]
    return np.bincount(res, minlength=25)
