"""S4: running keys read out of the sculpture in 2-D orders (columns, reversed columns, boustrophedon,
diagonals) from the left panel CT, the K1-K3 PT laid in place, and the tableau. Any offset, 24 variants,
any Quagmire shift (run_e4.scan). Null: best-of-offsets for a random stream of the same length."""
from common import *
from run_e4 import scan
from overlay import grids

def reads(g):
    R = len(g); W = max(len(r) for r in g)
    cell = lambda r, c: g[r][c] if c < len(g[r]) and g[r][c] in AZ else ""
    out = {}
    out["rows"] = "".join(cell(r, c) for r in range(R) for c in range(W))
    out["cols"] = "".join(cell(r, c) for c in range(W) for r in range(R))
    out["cols_up"] = "".join(cell(r, c) for c in range(W) for r in range(R - 1, -1, -1))
    out["cols_rl"] = "".join(cell(r, c) for c in range(W - 1, -1, -1) for r in range(R))
    out["cols_snake"] = "".join(cell(r if c % 2 == 0 else R - 1 - r, c) for c in range(W) for r in range(R))
    out["diag"] = "".join(cell(r, s - r) for s in range(R + W) for r in range(R) if 0 <= s - r < W)
    out["adiag"] = "".join(cell(r, W - 1 - (s - r)) for s in range(R + W) for r in range(R) if 0 <= s - r < W)
    return out

if __name__ == "__main__":
    G = grids()
    G["top_plate"] = LEFT[:14]; G["bottom_plate"] = LEFT[14:]
    G["tab_top"] = RIGHT[:14]; G["tab_bot"] = RIGHT[14:]
    res = []
    for gname, g in G.items():
        for rname, s in reads(g).items():
            for s2, tag in ((s, ""), (s[::-1], "~rev")):
                if len(s2) < 120: s2 = s2 + s2
                for kname, kal in (("AZ", AZ), ("KA", KA)):
                    S = np.array([kal.index(c) for c in s2], dtype=np.int64)
                    for v in range(cf.NV):
                        best = np.zeros(len(S) - 97, dtype=np.int64)
                        scan(S, REQ[v], cf.CRIB_I, best)
                        res.append((int(best.max()), gname, rname + tag, kname, cf.VARIANTS[v][:3], int(best.argmax()), len(S)))
    res.sort(key=lambda x: -x[0])
    for r in res[:12]: print(r)
    tot = sum(r[-1] - 97 for r in res)
    print("streams x variants", len(res), "total offsets", tot)
    # null: random streams of length 869, same scan
    rng = np.random.default_rng(0); mx = []
    for _ in range(300):
        S = rng.integers(0, 26, 869)
        best = np.zeros(869 - 97, dtype=np.int64); scan(S, REQ[0], cf.CRIB_I, best); mx.append(best.max())
    print("null best per 869-stream:", np.bincount(mx))
