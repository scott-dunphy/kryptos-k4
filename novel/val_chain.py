import sys, random
import numpy as np
sys.path.insert(0, '.')
from novel.run_chain import build, test
from novel.linkey import pos_table
from k4lib import AZ, KA, CRIB_POS, keyed_alphabet
X, Y = KA, keyed_alphabet('BERLIN')
tx, ty = pos_table(X), pos_table(Y)
rnd = random.Random(2)
pt = [rnd.choice(AZ) for _ in range(97)]
for i, c in CRIB_POS.items(): pt[i] = c
a, b, c, d = 3, 5, 2, 7
ct = []
for i in range(97):
    k = (a * tx[ord(pt[i-1])-65] + b * ty[ord(ct[i-1])-65] + c * i + d) % 26 if i else 4
    ct.append(Y[(tx[ord(pt[i])-65] + k) % 26])
ct = ''.join(ct)
for rule in range(3):
    F, k = build(tx, ty, rule, (1,), ct)
    print(rule, test(F, k))
F, k = build(tx, pos_table(AZ), 0, (1,), ct); print('wrong alpha', test(F, k))
