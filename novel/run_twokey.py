"""Two-key / masked models, direct. Models:
 TK(p,q): k_i = A[i%p] + B[i%q]          (two periodic keys added = 'masking' key)
 RC(w):   k_i = R[i//w] + Cc[i%w]         (grid row key + column key)
 RCP(w,p): k_i = R[i//w] + Cc[i%w] + D[i%p]... skipped (too free)
 QD(p):   k_i = A[i%p] + c1*i + c2*i^2    (quadratic drift)
"""
import sys, itertools, math
import numpy as np
sys.path.insert(0, '.')
from novel.linkey import *

def F_tk(p, q):
    F = np.zeros((24, p + q), dtype=np.int64)
    for t, i in enumerate(CI):
        F[t, i % p] = 1; F[t, p + i % q] = 1
    return F

def F_rc(w):
    nr = 97 // w + 1
    F = np.zeros((24, nr + w), dtype=np.int64)
    for t, i in enumerate(CI):
        F[t, i // w] = 1; F[t, nr + i % w] = 1
    return F

def F_qd(p):
    F = np.zeros((24, p + 2), dtype=np.int64)
    for t, i in enumerate(CI):
        F[t, i % p] = 1; F[t, p] = i; F[t, p + 1] = i * i
    return F

models = []
for p in range(1, 31):
    for q in range(p + 1, 31):
        if q % p == 0:
            continue
        models.append((f"TK{p},{q}", F_tk(p, q)))
for w in range(2, 49):
    models.append((f"RC{w}", F_rc(w)))
for p in range(1, 26):
    models.append((f"QD{p}", F_qd(p)))

alphas = base_alphabets()
tabs = [(n, pos_table(a)) for n, a in alphas]
print("alphabets", len(alphas), "models", len(models), flush=True)
rng = np.random.default_rng(1)
rules = ['vig', 'beau', 'var']
# precompute all key vectors
K = []
for na, ta in tabs:
    for nb, tb in tabs:
        for r, k in enumerate(keys_for(ta, tb)):
            K.append((na, nb, rules[r], k))
Kmat = np.array([k for *_, k in K])  # (N,24)
print("key vectors", len(K), flush=True)
tot_exp = 0.0
for name, F in models:
    W2, W13 = model_checks(F)
    d2, d13 = len(W2), len(W13)
    if d13 == 0 and d2 == 0:
        continue
    ok = np.ones(len(K), dtype=bool)
    if d2: ok &= ~np.any(Kmat @ W2.T % 2, axis=1)
    if d13: ok &= ~np.any(Kmat @ W13.T % 13, axis=1)
    R = rng.integers(0, 26, size=(20000, 24))
    okr = np.ones(len(R), dtype=bool)
    if d2: okr &= ~np.any(R @ W2.T % 2, axis=1)
    if d13: okr &= ~np.any(R @ W13.T % 13, axis=1)
    exp = len(K) * 2.0 ** -d2 * 13.0 ** -d13
    tot_exp += exp
    n = int(ok.sum())
    if n or exp > 0.5:
        print(f"{name}: checks d2={d2} d13={d13} expected_random={exp:.3g} rand_rate={okr.mean():.3g} hits={n}", flush=True)
        for j in np.nonzero(ok)[0][:10]:
            print("   ", K[j][:3])
print("total expected random hits", tot_exp)
