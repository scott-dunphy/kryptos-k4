"""Light/shadow and Egypt.
(1) Shadow projection: K4 cell (r, c) on the copper (rows 24-27, cols 0-30; K4 starts row 24 col 27) casts a shadow onto
    the tableau grid (data/sculpture_right.txt, 28 x 31) at (r', c') = (round(sy*r + hy*c + ty), round(sx*c + hx*r + tx)),
    scale sx, sy in [0.6, 1.6], shear hx, hy in [-0.5, 0.5], all translations; mirrored or not (light from behind).
    Key letter = tableau letter under the shadow; 12 variants (KV) x key index AZ/KA x indicator shift. Need >= 22/24.
(2) Egyptian uniliteral alphabet order as alphabet: tableau (PT=CT=key alphabet) periodic p1-24; PT/CT pairing with
    AZ/KA (small-key range, periodic); letter-class masking. Variants for placing letters without hieroglyphs.
"""
import itertools
import numpy as np
from numba import njit, prange
import cribfilter as cf
from k4lib import CT, CRIB_POS, AZ, KA
from run_alphapairs import pos_table, diag, PL, CL, CI

rows = [l.rstrip("\n") for l in open("data/sculpture_right.txt")]
H, W = len(rows), 31
GRID = np.full((H, W), -1, dtype=np.int64)
for r, l in enumerate(rows):
    for c in range(min(W, len(l))):
        if l[c].isalpha():
            GRID[r, c] = ord(l[c]) - 65
pos = np.array(sorted(CRIB_POS))
RC = np.array([((i + 27) // 31 + 24, (i + 27) % 31) for i in pos], dtype=np.float64)  # copper (row, col)
IDX = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)
REQ = np.array([cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)


@njit(parallel=True, cache=True)
def shadow_scan(GRID, RC, REQ, IDX, sxs, sys_, hs, best_out):
    H, W = GRID.shape
    n = RC.shape[0]
    for a in prange(sxs.shape[0]):
        sx = sxs[a]
        bestc = 0
        for sy in sys_:
            for hx in hs:
                for hy in hs:
                    for mirror in range(2):
                        for ty in range(-40, 40):
                            for tx in range(-40, 40):
                                # key letters
                                keys = np.empty(n, dtype=np.int64)
                                ok = True
                                for t in range(n):
                                    r = RC[t, 0]; c = RC[t, 1]
                                    if mirror == 1:
                                        c = 30.0 - c
                                    rr = int(np.floor(sy * r + hy * c + ty + 0.5))
                                    cc = int(np.floor(sx * c + hx * r + tx + 0.5))
                                    if rr < 0 or rr >= H or cc < 0 or cc >= W or GRID[rr, cc] < 0:
                                        ok = False
                                        break
                                    keys[t] = GRID[rr, cc]
                                if not ok:
                                    continue
                                for v in range(REQ.shape[0]):
                                    for kx in range(2):
                                        cnt = np.zeros(26, dtype=np.int64)
                                        for t in range(n):
                                            cnt[(REQ[v, t] - IDX[kx, keys[t]]) % 26] += 1
                                        m = 0
                                        for x in range(26):
                                            if cnt[x] > m:
                                                m = cnt[x]
                                        if m > bestc:
                                            bestc = m
        best_out[a] = bestc


def egypt_alphabets():
    core = "AIYWBPFMNRHSQKGTD"          # Gardiner uniliteral order mapped to Latin (aleph->A, i->I, y->Y, w->W, ... , d->D)
    extra_sets = {
        "rest_AZ": "".join(c for c in AZ if c not in core),
        "rest_rev": "".join(c for c in AZ if c not in core)[::-1],
        "rest_KA": "".join(c for c in KA if c not in core),
    }
    out = {}
    for nm, rest in extra_sets.items():
        a = core + rest
        out["egy_" + nm] = a
        out["egy_" + nm + "~rev"] = a[::-1]
        # alternative: L with R (Egyptian has no L), O with W, U with W, E with A/I, C with K, V with F, Z with S, X, J
    for c_ins in itertools.permutations("ELO", 3):
        a = "A" + c_ins[0] + "IYW" + "BPFMN" + "R" + c_ins[1] + "HSQKGTD" + c_ins[2]
        rest = "".join(c for c in AZ if c not in a)
        out["egyins_" + "".join(c_ins)] = a + rest
    return out


if __name__ == "__main__":
    # (1) shadow projection
    sxs = np.round(np.arange(0.6, 1.61, 0.1), 2); sys_ = np.round(np.arange(0.6, 1.61, 0.1), 2); hs = np.round(np.arange(-0.5, 0.51, 0.1), 2)
    best = np.zeros(len(sxs), dtype=np.int64)
    shadow_scan(GRID, RC, REQ, IDX, sxs, sys_, hs, best)
    print("(1) shadow projection: best crib agreement", int(best.max()), "/24 (need >=22)", flush=True)
    rng = np.random.default_rng(0)
    nb = []
    for _ in range(2):
        sh = rng.permutation(cf.CTI)
        req2 = np.array([cf.KV[v, cf.CRIB_L, sh[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)
        b2 = np.zeros(len(sxs), dtype=np.int64); shadow_scan(GRID, RC, req2, IDX, sxs, sys_, hs, b2); nb.append(int(b2.max()))
    print("    null (shuffled CT) best:", nb, flush=True)
    # (2) Egypt alphabets
    E = egypt_alphabets()
    names = list(E); TA = np.array([pos_table(E[n]) for n in names])
    partners = {"AZ": AZ, "KA": KA, "AZ~rev": AZ[::-1], "KA~rev": KA[::-1]}; partners.update(E)
    pn = list(partners); TB = np.array([pos_table(partners[n]) for n in pn])
    out = np.zeros((100000, 6), dtype=np.int64)
    for lab, X, Y in (("PT=egypt", TA, TB), ("CT=egypt", TB, TA)):
        n = diag(X, Y, PL, CL, CI, out); r = out[:n]
        strong = r[(r[:, 3] <= 12) | ((r[:, 5] > 0) & (r[:, 5] <= 22))]
        print(f"(2) {lab}: flagged {n} strong {len(strong)} min range {int(r[:,3].min()) if n else None}")
    # tableau (same alphabet both sides) periodic
    import run_tableau_all as rt
    o = np.zeros(len(TA), dtype=np.int64); rt.scan(TA, rt.PL, rt.CL, rt.CI, o)
    print("(2) Egyptian alphabet as tableau x periodic p1-24: hits", int((o > 0).sum()), "of", len(TA))
