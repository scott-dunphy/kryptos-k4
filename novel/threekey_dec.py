import sys, itertools
import numpy as np
sys.path.insert(0, '.')
from novel.linkey import *
def F_multi(periods):
    F = np.zeros((24, sum(periods)), dtype=np.int64); off = 0
    for p in periods:
        for t, i in enumerate(CI): F[t, off + i % p] = 1
        off += p
    return F
from k4lib import CT, keyed_alphabet, qscore, AZ
X = keyed_alphabet('EGYPT'); Y = keyed_alphabet('WELTZEITUHR')
tx, ty = pos_table(X), pos_table(Y)
k = keys_for(tx, ty)[1]  # beau
F = F_multi((2, 7, 13))
# brute solve: fix gauge A[0]=0, B[0]=0; solve via search over Z26 using least structure: gaussian over integers by brute on A[1]
sols = []
from itertools import product
# solve with simple elimination mod 26 by brute force on 2 free vars is heavy; use iterative propagation
def solve():
    n = F.shape[1]
    for a1 in range(26):
        x = [None] * n; x[0] = 0; x[1] = a1; x[2] = 0
        changed = True
        while changed:
            changed = False
            for t in range(24):
                idx = np.nonzero(F[t])[0]
                unk = [j for j in idx if x[j] is None]
                if len(unk) == 1:
                    x[unk[0]] = (k[t] - sum(x[j] for j in idx if x[j] is not None)) % 26; changed = True
        if None in x: continue
        if all(sum(x[j] for j in np.nonzero(F[t])[0]) % 26 == k[t] for t in range(24)):
            yield x
for x in solve():
    A, B, C = x[:2], x[2:9], x[9:22]
    pt = ''
    for i in range(97):
        kk = (A[i % 2] + B[i % 7] + C[i % 13]) % 26
        pt += X[(kk - ty[ord(CT[i]) - 65]) % 26]  # beau: ic = k - ip
    print(round(qscore(pt), 3), pt)
