"""Block-held key: k_i = K[((i+o)//n) % p] (each key letter used for n consecutive letters), n 2-12, p 1-26, o<n.
Lore alphabets both sides x vig/beau/var, linear consistency (exact: class equality). Random calibration."""
import sys
import numpy as np
sys.path.insert(0, '.')
from novel.linkey import base_alphabets, pos_table, keys_for, CI

alphas = [(n, a) for n, a in base_alphabets() if not n.endswith('~rev')]
tabs = [(n, pos_table(a)) for n, a in alphas]
K = []
for na, ta in tabs:
    for nb, tb in tabs:
        for r, k in enumerate(keys_for(ta, tb)[:2]):
            K.append((na, nb, r, k))
Kmat = np.array([k for *_, k in K])
rng = np.random.default_rng(0)
R = rng.integers(0, 26, (200000, 24))
tot_hits = 0; tot_exp = 0
for n in range(2, 13):
    for p in range(1, 27):
        for o in range(n):
            cls = ((CI + o) // n) % p
            # checks: pairs within class must have equal k
            ok = np.ones(len(Kmat), bool); okr = np.ones(len(R), bool); nchk = 0
            for c in np.unique(cls):
                idx = np.nonzero(cls == c)[0]
                for j in idx[1:]:
                    ok &= Kmat[:, j] == Kmat[:, idx[0]]; okr &= R[:, j] == R[:, idx[0]]; nchk += 1
            h = int(ok.sum()); e = okr.mean() * len(Kmat)
            tot_hits += h; tot_exp += e
            if h and (nchk >= 5 or h > 3 * e + 2):
                print('n', n, 'p', p, 'o', o, 'checks', nchk, 'hits', h, 'exp', round(e, 2), [K[j][:3] for j in np.nonzero(ok)[0][:4]], flush=True)
print('total hits', tot_hits, 'total expected', round(tot_exp, 1))
