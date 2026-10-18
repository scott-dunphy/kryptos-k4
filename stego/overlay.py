"""S1: physical overlay keys. K4 cell (r,c) on left panel -> letter at an aligned cell of another grid
(tableau, top plate, K1/K2/K3 PT laid in place). Variants: row offset dy, vertical flip, col shift dx,
mirror, source alignment (left/right flush), with/without tableau row-label column."""
from common import *
import kryptos_texts as kt

def grids():
    G = {}
    G["tableau"] = RIGHT
    G["tableau_nolabel"] = [row[1:] for row in RIGHT]
    G["left"] = LEFT
    # PT laid into CT layout: K1 = first 63 letters, K2 next 369(+?), K3 336 letters ...
    flat = [(r, c) for r in range(28) for c in range(len(LEFT[r]))]
    letters = [(r, c) for (r, c) in flat if LEFT[r][c] != "?"]
    k2 = kt.K2_PT  # carved PT (with the S omission the CT is 1 shorter; PT here has XLAYERTWO)
    pt = kt.K1_PT + k2 + kt.K3_PT
    for name, seq in (("ptlay", pt),):
        g = [list(" " * len(LEFT[r])) for r in range(28)]
        for (r, c), ch in zip(letters, seq):
            g[r][c] = ch
        G[name] = ["".join(x) for x in g]
    G["morse_tbl"] = None
    del G["morse_tbl"]
    return G

def build(src, dy, flip, dx, mirror, align):
    key = []
    for (r, c) in K4_CELLS:
        rr = (27 - r if flip else r) + dy
        if not (0 <= rr < len(src)):
            key.append(None); continue
        row = src[rr]
        W = len(row)
        cc = c + dx
        if align == "right":
            cc = cc - (31 - W)  # K4 rows are 31 wide; right-flush source
        if mirror:
            cc = W - 1 - cc
        key.append(row[cc] if 0 <= cc < W and row[cc] in AZ else None)
    return key

if __name__ == "__main__":
    res = []
    G = grids()
    n = 0
    for gname, src in G.items():
        for dy in range(-27, 28):
            for flip in (0, 1):
                for dx in range(-4, 5):
                    for mirror in (0, 1):
                        for align in ("left", "right"):
                            key = build(src, dy, flip, dx, mirror, align)
                            b = test_key(key, min_known=16)
                            n += 1
                            if b[0]:
                                res.append((b[0], b[1], gname, dy, flip, dx, mirror, align, b[2], cf.VARIANTS[b[3]][:3]))
    res.sort(key=lambda x: (-x[0], -x[1]))
    print("variants tested", n, "scored", len(res))
    for r in res[:15]:
        print(r)
    import collections
    print(collections.Counter(r[0] for r in res))
