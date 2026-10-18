"""Periodic key with carry/borrow noise: derived key k_i in {K[i%p], K[i%p]+1}. Direct, alphabet pairs from lore list."""
import sys
import numpy as np
sys.path.insert(0, '.')
from novel.linkey import base_alphabets, pos_table, keys_for, CI

def fits(k, p):
    for r in range(p):
        vals = set(int(x) for x in k[CI % p == r])
        if len(vals) <= 1: continue
        if len(vals) > 2: return False
        a, b = vals
        if (a - b) % 26 not in (1, 25): return False
    return True

def nchecks(p):
    return sum(max(0, int((CI % p == r).sum()) - 1) for r in range(p))

alphas = [(n, a) for n, a in base_alphabets() if not n.endswith('~rev')]
tabs = [(n, pos_table(a)) for n, a in alphas]
rng = np.random.default_rng(0)
for p in range(1, 31):
    hits = []
    for na, ta in tabs:
        for nb, tb in tabs:
            for r, k in enumerate(keys_for(ta, tb)):
                if r == 2: continue  # var = -vig, symmetric under carry sign? keep vig/beau
                if fits(k, p): hits.append((na, nb, r))
    rr = np.mean([fits(rng.integers(0, 26, 24), p) for _ in range(3000)])
    exp = rr * len(tabs) ** 2 * 2
    if hits or exp > 0.01:
        print(p, 'checks', nchecks(p), 'hits', len(hits), 'exp_random', round(exp, 2), hits[:5], flush=True)
    else:
        print(p, 'checks', nchecks(p), 'hits 0')
