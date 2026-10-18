"""Periodic affine (multiplicative Vigenere) direct: Y.idx(C) = a_r*X.idx(P) + b_r, a_r unit, r = i % p.
Also decimation-type with key in exponent skipped. Lore alphabets both sides. Count residue-consistent tuples."""
import sys, itertools
import numpy as np
sys.path.insert(0, '.')
from novel.linkey import base_alphabets, pos_table, CI, PL, CL
UNITS = [1,3,5,7,9,11,15,17,19,21,23,25]
alphas = [(n, a) for n, a in base_alphabets()]
tabs = [(n, pos_table(a)) for n, a in alphas]
rng = np.random.default_rng(0)

def ok_res(xs, ys):
    for a in UNITS:
        b = (ys[0] - a * xs[0]) % 26
        if all((y - a * x - b) % 26 == 0 for x, y in zip(xs, ys)):
            return True
    return False

def test(xp, yc, p):
    for r in range(p):
        m = CI % p == r
        if m.sum() >= 2 and not ok_res(xp[m], yc[m]):
            return False
    return True

for p in range(1, 27):
    hits = 0; tried = 0
    for na, ta in tabs:
        for nb, tb in tabs:
            tried += 1
            if test(ta[PL], tb[CL], p):
                hits += 1; print('  HIT p', p, na, nb)
    rr = np.mean([test(rng.integers(0, 26, 24), rng.integers(0, 26, 24), p) for _ in range(2000)])
    print('p', p, 'tried', tried, 'hits', hits, 'expected', round(rr * tried, 3), flush=True)
