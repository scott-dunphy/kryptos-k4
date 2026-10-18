"""Dictionary-keyword columnar (word length >=9, beyond exhaustive W<=8) and Myszkowski (any word with repeated letters)
transpositions, fwd+inv, + periodic substitution p1-24, 12 variants (AZ/KA), 2 orders."""
import sys, time
import numpy as np
sys.path.insert(0, '.')
import cribfilter as cf
from perms import columnar_perm, keyword_order, inverse
from run_alphapairs import load_words
from collections import Counter

def myszkowski(n, key):
    W = len(key); perm = []
    for ch in sorted(set(key)):
        cols = [c for c in range(W) if key[c] == ch]
        for r in range(0, n, W):
            for c in cols:
                if r + c < n: perm.append(r + c)
    return np.array(perm, np.int64)

lore, words = load_words()
seen = set(); perms = []; labels = []
for w in words:
    if len(w) >= 9:
        o = tuple(keyword_order(w))
        if ('c', o) not in seen:
            seen.add(('c', o)); perms.append(columnar_perm(97, list(o))); labels.append('col ' + w)
    if len(set(w)) < len(w):
        # canonical rank pattern
        pat = tuple(sorted(set(w)).index(c) for c in w)
        if ('m', pat) not in seen:
            seen.add(('m', pat)); perms.append(myszkowski(97, w)); labels.append('mysz ' + w)
for p in perms: assert sorted(p.tolist()) == list(range(97))
P2 = []; L2 = []
for l, p in zip(labels, perms):
    P2 += [p, inverse(p)]; L2 += [l + ' fwd', l + ' inv']
invs = np.array([inverse(p) for p in P2])
print('perms', len(invs), flush=True)
t = time.time(); out = np.zeros((2_000_000, 5), np.int64); mh = Counter(); CH = 50000
for s in range(0, len(invs), CH):
    n = cf.check_batch(invs[s:s + CH], 1, 24, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 4, out)
    for q, p, o, v, m in out[:n]:
        mh[(int(m), int(p))] += 1
        if m >= 5:
            inv = invs[s + q]; perm = P2[s + q]
            key, sc = cf.complete_key(inv, perm, int(p), int(o), int(v), sweeps=2)
            print('HIT m', m, 'p', p, o, cf.VARIANTS[v][:3], L2[s + q], round(sc, 3), cf.full_decrypt(inv, perm, int(p), int(o), int(v), key), flush=True)
print('time', round(time.time() - t), 'm>=4 by (m,p)', sorted(mh.items()))
