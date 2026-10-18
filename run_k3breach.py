"""Literal K3 instruction: 'tiny breach in the upper left-hand corner ... widening the hole' as a reading order.
Grid layouts: copper (31 wide, K4 starts at col 27 of first row) and plain widths 2-49 (ragged last row).
Orders growing from a corner: square shells max(r,c)=k (several traversals of each L-shell) and anti-diagonals r+c=k
(both zigzag directions). All 4 corners. Each order -> perm; test with periodic substitution p1-24, 12 variants,
2 orders (cribfilter.check_batch, m>=4), fwd + inverse perms.
"""
import numpy as np
import cribfilter as cf
from perms import inverse

N = 97


def layouts():
    # copper: row0 has cells at cols 27-30, rows 1-3 full 31
    cop = [(0, c) for c in range(27, 31)] + [(r, c) for r in range(1, 4) for c in range(31)]
    yield "copper31", cop, 4, 31
    for W in range(2, 50):
        R = -(-N // W)
        yield f"W{W}", [(i // W, i % W) for i in range(N)], R, W


def orders(cells, R, W):
    pos = {cell: i for i, cell in enumerate(cells)}
    for corner in range(4):
        def tr(rc):
            r, c = rc
            if corner & 1:
                c = W - 1 - c
            if corner & 2:
                r = R - 1 - r
            return r, c
        tcells = {tr(x): pos[x] for x in cells}
        K = max(R, W)
        # square shells
        for variant in range(4):
            seq = []
            for k in range(K + max(R, W)):
                col_part = [(r, k) for r in range(0, k + 1)]      # down the new column
                row_part = [(k, c) for c in range(0, k)]          # along the new row
                if variant == 0:
                    shell = row_part + col_part[::-1]
                elif variant == 1:
                    shell = col_part + row_part[::-1]
                elif variant == 2:
                    shell = row_part[::-1] + col_part           # from corner (k,0)->(k,k)->(0,k)? approx
                else:
                    shell = col_part[::-1] + row_part
                for x in shell:
                    if x in tcells:
                        seq.append(tcells[x])
            if len(seq) == N:
                yield f"shell{variant} corner{corner}", seq
        # anti-diagonals
        for zig in range(3):
            seq = []
            for k in range(R + W):
                diag = [(r, k - r) for r in range(0, k + 1)]
                if zig == 1 or (zig == 2 and k % 2):
                    diag = diag[::-1]
                for x in diag:
                    if x in tcells:
                        seq.append(tcells[x])
            if len(seq) == N:
                yield f"diag{zig} corner{corner}", seq


if __name__ == "__main__":
    labels, P = [], []
    for lname, cells, R, W in layouts():
        for oname, seq in orders(cells, R, W):
            p = np.array(seq, dtype=np.int64)
            labels.append(f"{lname} {oname}"); P.append(p)
            labels.append(f"{lname} {oname} inv"); P.append(inverse(p))
    invs = np.array([inverse(p) for p in P])
    print("perms", len(invs))
    out = np.zeros((100000, 5), dtype=np.int64)
    n = cf.check_batch(invs, 1, 24, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 4, out)
    print("survivors m>=4:", n)
    for r in out[:n][:10]:
        print("  ", labels[r[0]], r[1:].tolist())
    rng = np.random.default_rng(0)
    sh = rng.permutation(cf.CTI)
    n2 = cf.check_batch(invs, 1, 24, cf.KV, sh, cf.CRIB_I, cf.CRIB_L, 4, out)
    print("null shuffled survivors:", n2)
