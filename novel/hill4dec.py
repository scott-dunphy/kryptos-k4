import sys, itertools
import numpy as np
sys.path.insert(0, '.')
from k4lib import CT, CRIB_POS, AZ, KA, qscore
from novel.hill import blocks
for an, al in [('AZ', AZ), ('KA', KA)]:
    idx = {c: i for i, c in enumerate(al)}
    for off in (0, 3):
        n = 4; bl = blocks(n, off)
        P = np.array([[idx[CRIB_POS[s + j]] for j in range(n)] for s in bl]); C = np.array([[idx[CT[s + j]] for j in range(n)] for s in bl])
        rows = np.array(list(itertools.product(range(26), repeat=n)))
        vals = rows @ C.T % 26
        sols = [rows[np.all(vals == P[:, r][None, :], axis=1)] for r in range(n)]
        if not all(len(s) for s in sols): continue
        for M in itertools.product(*sols):
            M = np.array(M); pt = []
            for s in range(off - n * (off // n) if off else 0, 97 - n + 1, n):
                pass
            # decrypt every full block with alignment off
            out = ['?'] * 97
            s = off % n
            while s + n <= 97:
                v = M @ np.array([idx[CT[s + j]] for j in range(n)]) % 26
                for j in range(n): out[s + j] = al[v[j]]
                s += n
            txt = ''.join(out)
            print(an, off, qscore(txt.replace('?', '')), txt)
