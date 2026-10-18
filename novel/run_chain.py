"""Chained / self-keyed linear systems, direct.
C_i = Y[X.idx(P_i) (+/-) k_i] with k_i = a*X.idx(P_{i-L}) + b*Y.idx(C_{i-L}) [+ e*X.idx(P_{i-L2}) + f*Y.idx(C_{i-L2})] + c*i + d
All of a,b,c,d(,e,f) unknown in Z26 -> linear consistency over the consecutive-crib equations.
Covers: PT/CT autokey with any multiplier, 'sum' keys (P+C of previous), tableau walks on KRYPTOS tableau (X=Y=KA),
progressive drift. Random calibration via shuffled CT positions."""
import sys
import numpy as np
sys.path.insert(0, '.')
from novel.linkey import *
from k4lib import CRIB_POS, CT

def build(ptab, ctab, rule, lags, ct=CT):
    rows, ks = [], []
    for i in sorted(CRIB_POS):
        if not all((i - L) in CRIB_POS for L in lags):
            continue
        ip = ptab[ord(CRIB_POS[i]) - 65]; ic = ctab[ord(ct[i]) - 65]
        k = [(ic - ip), (ic + ip), (ip - ic)][rule] % 26
        f = []
        for L in lags:
            f += [ptab[ord(CRIB_POS[i - L]) - 65], ctab[ord(ct[i - L]) - 65]]
        f += [i, 1]
        rows.append(f); ks.append(k)
    return np.array(rows, dtype=np.int64), np.array(ks, dtype=np.int64)

def test(F, k):
    W2 = left_null(F, 2); W13 = left_null(F, 13)
    ok = (not len(W2) or not np.any(W2 @ k % 2)) and (not len(W13) or not np.any(W13 @ k % 13))
    return ok, len(W2), len(W13)

if __name__ == '__main__':
    import random
    alphas = base_alphabets()
    # reversed alphabets with 3 rules are redundant; keep fwd only but all 3 rules
    alphas = [(n, a) for n, a in alphas if not n.endswith('~rev')]
    tabs = [(n, pos_table(a)) for n, a in alphas]
    lagsets = [(1,), (2,), (3,), (4,), (5,), (7,), (1, 2), (1, 3), (2, 3)]
    rules = ['vig', 'beau', 'var']
    ctx = [('REAL', CT)]
    rnd = random.Random(5)
    for t in range(2):
        l = list(CT); rnd.shuffle(l); ctx.append((f'shuf{t}', ''.join(l)))
    for lab, ct in ctx:
        for lags in lagsets:
            hits = 0; tried = 0; dmin = 99
            for na, ta in tabs:
                for nb, tb in tabs:
                    for r in range(3):
                        F, k = build(ta, tb, r, lags, ct)
                        ok, d2, d13 = test(F, k)
                        tried += 1; dmin = min(dmin, d13)
                        if ok:
                            hits += 1
                            if lab == 'REAL':
                                print('  HIT', lags, na, nb, rules[r], 'checks', d2, d13, flush=True)
            print(lab, 'lags', lags, 'tried', tried, 'hits', hits, 'min d13 checks', dmin, flush=True)
