"""S3: 'upper left hand corner ... widening the hole' (K3 instructions?) -> spiral and diagonal routes,
not covered by E1 (which used row/col/snake/flip traversals). Fill/read pairs where at least one traversal is
spiral or diagonal, widths 2-49, ragged blanks end/start (W31 blanks-start = sculpture layout), fwd + inverse,
x periodic Vig/Beau/VarBeau x {AZ,KA}^2 x both orders, p 1-26."""
import time
from common import *
from perms import cell_orders, inverse

def spirals(R, W):
    out = {}
    for corner in range(4):
        for cw in (0, 1):
            # build inward spiral from (0,0) clockwise on R x W, then transform
            cells = []
            top, bot, lef, rig = 0, R - 1, 0, W - 1
            while top <= bot and lef <= rig:
                for c in range(lef, rig + 1): cells.append((top, c))
                for r in range(top + 1, bot + 1): cells.append((r, rig))
                if top < bot:
                    for c in range(rig - 1, lef - 1, -1): cells.append((bot, c))
                if lef < rig:
                    for r in range(bot - 1, top, -1): cells.append((r, lef))
                top += 1; bot -= 1; lef += 1; rig -= 1
            if not cw:  # counter-clockwise = transpose-ish: swap roles via reflection across main diagonal only valid if square; use column-first spiral
                cells2 = []
                top, bot, lef, rig = 0, R - 1, 0, W - 1
                while top <= bot and lef <= rig:
                    for r in range(top, bot + 1): cells2.append((r, lef))
                    for c in range(lef + 1, rig + 1): cells2.append((bot, c))
                    if lef < rig:
                        for r in range(bot - 1, top - 1, -1): cells2.append((r, rig))
                    if top < bot:
                        for c in range(rig - 1, lef, -1): cells2.append((top, c))
                    top += 1; bot -= 1; lef += 1; rig -= 1
                cells = cells2
            def tf(rc):
                r, c = rc
                if corner & 1: c = W - 1 - c
                if corner & 2: r = R - 1 - r
                return (r, c)
            cells = [tf(x) for x in cells]
            out[f"spin{corner}{'cw' if cw else 'ccw'}"] = cells
            out[f"spout{corner}{'cw' if cw else 'ccw'}"] = cells[::-1]
    return out

def diagonals(R, W):
    out = {}
    for corner in range(4):
        for zig in (0, 1):
            for dirn in (0, 1):
                cells = []
                for s in range(R + W - 1):
                    d = [(r, s - r) for r in range(R) if 0 <= s - r < W]
                    if dirn: d = d[::-1]
                    if zig and s % 2: d = d[::-1]
                    cells.extend(d)
                def tf(rc):
                    r, c = rc
                    if corner & 1: c = W - 1 - c
                    if corner & 2: r = R - 1 - r
                    return (r, c)
                out[f"diag{corner}{zig}{dirn}"] = [tf(x) for x in cells]
    return out

def gen(n=97):
    for W in range(2, 50):
        R = -(-n // W); blanks = R * W - n
        base = cell_orders(R, W)
        new = {**spirals(R, W), **diagonals(R, W)}
        allo = {**base, **new}
        for bpos in (("end", "start") if blanks else ("end",)):
            if bpos == "end":
                valid = {(r, c) for r in range(R) for c in range(W) if r * W + c < n}
            else:
                valid = {(r, c) for r in range(R) for c in range(W) if r * W + c >= blanks}
            for fname, fcells in allo.items():
                fc = [x for x in fcells if x in valid]
                pos = {cell: i for i, cell in enumerate(fc)}
                for rname, rcells in allo.items():
                    if rname == fname or (fname not in new and rname not in new):
                        continue
                    perm = np.array([pos[x] for x in rcells if x in valid], dtype=np.int64)
                    yield f"W{W} {bpos} {fname}->{rname}", perm

if __name__ == "__main__":
    t = time.time()
    labels, invs = [], []
    seen = set()
    for lab, p in gen():
        for tag, q in (("", p), ("inv ", inverse(p))):
            inv = inverse(q)
            k = inv.tobytes()
            if k in seen: continue
            seen.add(k); labels.append(tag + lab); invs.append(inv)
    invs = np.array(invs)
    print("perms", len(invs), time.time() - t, flush=True)
    out = np.zeros((200000, 5), dtype=np.int64)
    tot = 0
    for s in range(0, len(invs), 20000):
        c = cf.check_batch(invs[s:s+20000], 1, 26, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 5, out)
        for row in out[:c]:
            q, p, order, v, m = row
            print("HIT", labels[s+q], "p", p, "order", order, cf.VARIANTS[v][:3], "m", m, flush=True)
        tot += c
    print("total survivors m>=5:", tot, "time", time.time() - t)
