"""TEAM clock exp 7: 'clock-arithmetic' transpositions + periodic substitution p1-30:
affine decimation around a 97-circle i->(a*i+c) mod 97; Josephus counting-out (step k, start s);
decimation on a 98/96-circle with a null/dropped slot. Both perm and inverse, check_batch."""
import numpy as np
from collections import Counter
import cribfilter as cf
from perms import inverse
P, L = [], []
for a in range(2, 97):
    for c in range(97):
        P.append(np.array([(a * i + c) % 97 for i in range(97)])); L.append(f"affine a{a} c{c}")
for k in range(2, 98):
    for s in range(97):
        circ = list(range(97)); idx = s; out = []
        while circ:
            idx = (idx + k - 1) % len(circ); out.append(circ.pop(idx))
        P.append(np.array(out)); L.append(f"josephus k{k} s{s}")
for n in (98, 100, 104):  # decimate on n-circle, skip slots >=97
    for a in range(2, n):
        if np.gcd(a, n) != 1: continue
        for c in range(n):
            seq = [(a * i + c) % n for i in range(n)]
            P.append(np.array([x for x in seq if x < 97])); L.append(f"dec{n} a{a} c{c}")
L2, P2 = [], []
for l, p in zip(L, P):
    L2 += [l + " fwd", l + " inv"]; P2 += [p, inverse(p)]
invs = np.array([inverse(p) for p in P2])
print("perms", len(invs), flush=True)
out = np.zeros((2_000_000, 5), dtype=np.int64)
n = cf.check_batch(invs, 1, 30, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 4, out)
rows = out[:n]
print("survivors m>=4:", n, sorted(Counter(rows[:, 4].tolist()).items()))
print("by p:", sorted(Counter(rows[:, 1].tolist()).items()))
res = []
for q, p, order, v, m in rows[rows[:, 4] >= 5]:
    inv = invs[q]; perm = P2[q]
    key, s = cf.complete_key(inv, perm, int(p), int(order), int(v), sweeps=2)
    res.append((round(s, 3), int(m), int(p), int(order), cf.VARIANTS[v][:3], L2[q], cf.full_decrypt(inv, perm, int(p), int(order), int(v), key)))
res.sort(reverse=True)
for r in res[:15]: print(r)
