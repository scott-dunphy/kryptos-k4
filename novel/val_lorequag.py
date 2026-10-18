import sys, random
import numpy as np
sys.path.insert(0, '.')
import cribfilter as cf
from novel.lore_quag_trans import KV, VARS
from perms import columnar_perm, inverse
from k4lib import AZ, CRIB_POS, keyed_alphabet
rnd = random.Random(1)
A = keyed_alphabet('BERLIN')
pt = [rnd.randrange(26) for _ in range(97)]
for i, c in CRIB_POS.items(): pt[i] = ord(c) - 65
perm = columnar_perm(97, [3, 0, 4, 1, 5, 2])
key = [rnd.randrange(26) for _ in range(9)]
Y = [A.index(AZ[pt[i]]) for i in range(97)]
Y = [A[(Y[i] + key[i % 9]) % 26] for i in range(97)]  # order B: sub then transpose (Quag III vig)
ct = ''.join(Y[perm[j]] for j in range(97))
cti = np.array([ord(c) - 65 for c in ct], np.int64)
invs = np.array([inverse(perm), perm])
out = np.zeros((100, 5), np.int64)
n = cf.check_batch(invs, 1, 24, KV, cti, cf.CRIB_I, cf.CRIB_L, 5, out)
for r in out[:n]: print(r, VARS[r[3]])
