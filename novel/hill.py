"""Hill n x n direct test (no transposition). For each block alignment, alphabet numbering, and direction
(C = K P  or  P = M C), brute-force each matrix row over 26^n and count rows consistent with all full crib blocks.
A Hill cipher survives only if every row has >=1 solution (and K invertible)."""
import sys, itertools
import numpy as np
sys.path.insert(0, '.')
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet

def blocks(n, off):
    out = []
    s = off
    while s + n <= 97:
        if all((s + j) in CRIB_POS for j in range(n)):
            out.append(s)
        s += n
    return out

def run(alpha, n, off, direction, ct=CT):
    bl = blocks(n, off)
    if len(bl) <= n - 1:
        return None, len(bl)
    idx = {c: i for i, c in enumerate(alpha)}
    P = np.array([[idx[CRIB_POS[s + j]] for j in range(n)] for s in bl])  # (B,n)
    C = np.array([[idx[ct[s + j]] for j in range(n)] for s in bl])
    src, dst = (P, C) if direction == 0 else (C, P)
    rows = np.array(list(itertools.product(range(26), repeat=n)), dtype=np.int64)  # (26^n, n)
    vals = rows @ src.T % 26  # (26^n, B)
    nsol = []
    for r in range(n):
        ok = np.all(vals == dst[:, r][None, :], axis=1)
        nsol.append(int(ok.sum()))
    return nsol, len(bl)

if __name__ == '__main__':
    import random
    alphas = [('AZ', AZ), ('KA', KA)]
    for ct_label, ct in [('REAL', CT)] + [('rand%d' % t, ''.join(random.choice(AZ) for _ in range(97))) for t in range(3)]:
        for an, al in alphas:
            for n in (2, 3, 4):
                for off in range(n):
                    for d in (0, 1):
                        ns, nb = run(al, n, off, d, ct)
                        if ns is None:
                            continue
                        flag = 'ALLROWS' if all(x > 0 for x in ns) else ''
                        if ct_label == 'REAL' or flag:
                            print(ct_label, an, 'n', n, 'off', off, 'dir', d, 'blocks', nb, 'sols/row', ns, flag)
