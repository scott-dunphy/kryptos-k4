import sys, random
import numpy as np
sys.path.insert(0, '.')
import cribfilter as cf
from novel.rowperm import run
from k4lib import AZ, CRIB_POS
rnd = random.Random(4)
w = 8; nfull = 97 // w
pt = [rnd.randrange(26) for _ in range(97)]
for i, c in CRIB_POS.items(): pt[i] = ord(c) - 65
perm_rows = list(range(nfull)); rnd.shuffle(perm_rows)  # CT row s holds PT row perm_rows[s]
X = []
for s in range(nfull): X += pt[perm_rows[s] * w:(perm_rows[s] + 1) * w]
X += pt[nfull * w:]
key = [rnd.randrange(26) for _ in range(11)]
ct = np.array([(X[j] + key[j % 11]) % 26 for j in range(97)], np.int64)  # vig AZ, order A (transpose then sub)
hits, crows, _ = run(w, 11, 11, ct, 4)
print('true assign', [perm_rows.index(r) for r in crows])
print([h for h in hits if h[3] == 0])
