"""Split keys (lead request): k_i = A[i%a] + B[i%b] + C[i%c], a<b<c, a+b+c-2 < 24; and
fixed-keyword variant: k_i = s*W[(i+o)%L] + A[i%a] + B[i%b] with W a lore keyword (AZ or KA indexed, s=+-1, all phases o).
Linear consistency over Z26 (left null space mod 2 and 13). Only models with >=3 checks per prime are informative.
Same alphabet set as run_twokey (AZ, KA, 53 lore words, fwd/rev, both roles, vig/beau/var)."""
import sys
import numpy as np
sys.path.insert(0, '.')
from novel.linkey import *
from k4lib import AZ, KA

def F_multi(periods):
    F = np.zeros((24, sum(periods)), dtype=np.int64)
    off = 0
    for p in periods:
        for t, i in enumerate(CI):
            F[t, off + i % p] = 1
        off += p
    return F

alphas = base_alphabets()
tabs = [(n, pos_table(a)) for n, a in alphas]
rules = ['vig', 'beau', 'var']
K = []
for na, ta in tabs:
    for nb, tb in tabs:
        for r, k in enumerate(keys_for(ta, tb)):
            K.append((na, nb, rules[r]))
Kmat = np.array([k for na, ta in tabs for nb, tb in tabs for k in keys_for(ta, tb)])
N = len(Kmat)
rng = np.random.default_rng(7)
R = rng.integers(0, 26, size=(200000, 24))

def apply(M, W2, W13):
    ok = np.ones(len(M), dtype=bool)
    if len(W2): ok &= ~np.any(M @ W2.T % 2, axis=1)
    if len(W13): ok &= ~np.any(M @ W13.T % 13, axis=1)
    return ok

print('key vectors', N, flush=True)
# ---- Part 1: three free keys
tot_h = tot_e = 0; nmod = 0
for a in range(1, 31):
    for b in range(a + 1, 31):
        for c in range(b + 1, 31):
            if a + b + c - 2 >= 24: continue
            W2, W13 = model_checks(F_multi((a, b, c)))
            if len(W2) < 3 or len(W13) < 3: continue
            nmod += 1
            ok = apply(Kmat, W2, W13); h = int(ok.sum())
            e = N * 2.0 ** -len(W2) * 13.0 ** -len(W13)
            er = apply(R, W2, W13).mean() * N
            tot_h += h; tot_e += e
            if h:
                print(f'3key {a},{b},{c} d2={len(W2)} d13={len(W13)} hits={h} exp={e:.3g} emp_exp={er:.3g}', [K[j] for j in np.nonzero(ok)[0][:4]], flush=True)
print(f'PART1 informative models {nmod}, total hits {tot_h}, total expected {tot_e:.3g}', flush=True)

# ---- Part 2: fixed keyword + two free keys
WORDS = ['KRYPTOS', 'PALIMPSEST', 'ABSCISSA', 'BERLIN', 'CLOCK', 'SHADOW', 'LAYERTWO']
models = []
for a in range(1, 31):
    for b in range(a + 1, 31):
        if a + b - 1 >= 21: continue
        W2, W13 = model_checks(F_multi((a, b)))
        if len(W2) >= 3 and len(W13) >= 3:
            models.append(((a, b), W2, W13))
# also single free key + keyword
for a in range(1, 21):
    W2, W13 = model_checks(F_multi((a,)))
    if len(W2) >= 3 and len(W13) >= 3:
        models.append(((a,), W2, W13))
print('part2 models', len(models), flush=True)
tot_h = tot_e = 0; nvar = 0
for w in WORDS:
    L = len(w)
    for an, al in (('AZ', AZ), ('KA', KA)):
        wv = np.array([al.index(ch) for ch in w])
        for s in (1, -1):
            for o in range(L):
                kw = np.array([wv[(i + o) % L] for i in CI])
                M = (Kmat - s * kw[None, :]) % 26
                nvar += 1
                for per, W2, W13 in models:
                    ok = apply(M, W2, W13); h = int(ok.sum())
                    e = N * 2.0 ** -len(W2) * 13.0 ** -len(W13)
                    tot_h += h; tot_e += e
                    if h and (h > 3 * e + 2 or len(W13) >= 5):
                        print(f'kw {w} {an} s={s} o={o} free{per} d2={len(W2)} d13={len(W13)} hits={h} exp={e:.3g}', [K[j] for j in np.nonzero(ok)[0][:3]], flush=True)
print(f'PART2 keyword variants {nvar} x models {len(models)}: total hits {tot_h}, total expected {tot_e:.3g}', flush=True)
