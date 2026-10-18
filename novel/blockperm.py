"""Block (in-row) transposition: write rows of width W, permute columns of every row by the same sigma, read rows.
Last partial row: existing cells read in sigma order. + periodic substitution (cribfilter.check_batch, p1-30)."""
import sys, itertools
import numpy as np
sys.path.insert(0, '.')
import cribfilter as cf
from perms import inverse
from collections import Counter

def block_perm(n, sigma):
    W = len(sigma); perm = []
    for s in range(0, n, W):
        for c in sigma:
            if s + c < n: perm.append(s + c)
    return np.array(perm, np.int64)

if __name__ == '__main__':
    Wmax = int(sys.argv[1])
    tot = Counter()
    for W in range(2, Wmax + 1):
        invs = []
        for sigma in itertools.permutations(range(W)):
            p = block_perm(97, sigma)
            invs.append(inverse(p)); invs.append(p)
        invs = np.array(invs)
        out = np.zeros((2_000_000, 5), np.int64)
        n = cf.check_batch(invs, 1, 30, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 4, out)
        rows = out[:n]
        c = Counter(zip(rows[:, 4].tolist(), rows[:, 1].tolist()))
        strong = rows[(rows[:, 4] >= 6) | ((rows[:, 4] >= 5) & (rows[:, 1] <= 20))]
        print('W', W, 'perms', len(invs), 'survivors m>=4', n, 'by m', sorted(Counter(rows[:, 4].tolist()).items()),
              'strong', len(strong), flush=True)
        for q, p, o, v, m in strong[:10]:
            print('   m', m, 'p', p, 'order', o, cf.VARIANTS[v][:3])
