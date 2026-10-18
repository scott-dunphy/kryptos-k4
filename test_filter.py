"""Synthetic self-test: encrypt a crib-bearing plaintext with known route+substitution, confirm filter recovers it."""
import random
import numpy as np
import cribfilter as cf
from perms import route_perms, inverse
from k4lib import AZ, to_idx, from_idx

PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
assert PT[21:34] == "EASTNORTHEAST" and PT[63:74] == "BERLINCLOCK"


def enc_letter(v, k, P):
    for C in range(26):
        if cf.KV[v, P, C] == k:
            return C


def encrypt(perm, p, order, v, key):
    P = to_idx(PT)
    n = len(P)
    if order == 0:
        X = P[perm]
        return np.array([enc_letter(v, key[j % p], X[j]) for j in range(n)])
    Y = np.array([enc_letter(v, key[i % p], P[i]) for i in range(n)])
    return Y[perm]


random.seed(1)
perms = list(route_perms(97, widths=[7, 13, 21]))
for trial in range(6):
    label, perm = random.choice(perms)
    p = random.choice([5, 7, 8, 10])
    order = trial % 2
    v = random.randrange(cf.NV)
    key = [random.randrange(26) for _ in range(p)]
    cti = encrypt(perm, p, order, v, key)
    invs = np.array([inverse(pp) for _, pp in perms])
    out = np.zeros((10000, 5), dtype=np.int64)
    n = cf.check_batch(invs, p, p, cf.KV, cti, cf.CRIB_I, cf.CRIB_L, 4, out)
    rows = out[:n]
    target = [i for i, (l, _) in enumerate(perms) if l == label][0]
    found = any(r[0] == target and r[2] == order and r[3] == v for r in rows)
    print(trial, label, p, order, cf.VARIANTS[v][:3], "found" if found else "MISSING", "survivors", n)
