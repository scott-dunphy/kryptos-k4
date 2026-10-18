import sys, itertools
import numpy as np
sys.path.insert(0, '.')
import cribfilter as cf
from perms import inverse
from novel.blockperm import block_perm
W = 9
invs = []; perms = []; labs = []
for sigma in itertools.permutations(range(W)):
    p = block_perm(97, sigma)
    invs += [inverse(p), p]; perms += [p, inverse(p)]; labs += [(sigma, 'fwd'), (sigma, 'inv')]
invs = np.array(invs)
out = np.zeros((1000, 5), np.int64)
n = cf.check_batch(invs, 21, 21, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 6, out)
for q, p, o, v, m in out[:n]:
    key, s = cf.complete_key(invs[q], perms[q], int(p), int(o), int(v), sweeps=3)
    print(labs[q], m, round(s, 3), cf.full_decrypt(invs[q], perms[q], int(p), int(o), int(v), key))
