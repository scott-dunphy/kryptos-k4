"""K4 layered on itself (palimpsest).
Maps f: affine i -> (a*i+b) mod 97 (a=1..96, b=0..96; includes reversal 96-i and all cyclic shifts), plus copper-grid
transforms of the 4x31 layout (K4 from col 27): row flip, column mirror, 180 rotation, each with row/col shifts.
(A) key_i = CT[f(i)]  : fixed alphabets (12 variants x key idx AZ/KA x indicator shift) + single unknown alphabet.
(B) key_i = PT[f(i)]  : checkable where i and f(i) are both crib positions (need >=6 such), same variants.
"""
import numpy as np
from numba import njit
import cribfilter as cf
import run_gromark as g
from k4lib import AZ, KA, CT, CRIB_POS

N = 97
IDX = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)
CTA = np.array([ord(c) - 65 for c in CT], dtype=np.int64)


def maps():
    for a in range(1, N):
        for b in range(N):
            if a == 1 and b == 0:
                continue
            yield f"affine a={a} b={b}", np.array([(a * i + b) % N for i in range(N)])
    # copper grid
    cells = [(0, c) for c in range(27, 31)] + [(r, c) for r in range(1, 4) for c in range(31)]
    pos = {x: i for i, x in enumerate(cells)}
    for name, tf in (("rowflip", lambda r, c: (3 - r, c)), ("mirror", lambda r, c: (r, 30 - c)),
                     ("rot180", lambda r, c: (3 - r, 30 - c))):
        for dr in range(4):
            for dc in range(31):
                f = []
                for (r, c) in cells:
                    r2, c2 = tf(r, c)
                    r2 = (r2 + dr) % 4; c2 = (c2 + dc) % 31
                    f.append(pos.get((r2, c2), -1))
                if all(x >= 0 for x in f):
                    yield f"grid {name} dr={dr} dc={dc}", np.array(f)
                else:
                    # partial maps (cells falling in empty part of row 0): keep, mark -1
                    yield f"grid {name} dr={dr} dc={dc} partial", np.array(f)


@njit(cache=True)
def test_A(f, CTA, REQ, IDX, CI, PL, CL):
    res = 0
    for v in range(REQ.shape[0]):
        kx = v % 2
        s = -1; ok = True
        for t in range(CI.shape[0]):
            j = f[CI[t]]
            if j < 0:
                ok = False; break
            d = (REQ[v, t] - IDX[kx, CTA[j]]) % 26
            if s == -1:
                s = d
            elif d != s:
                ok = False; break
        if ok:
            res |= 1
    d97 = np.zeros(97, dtype=np.int64)
    okf = True
    for i in range(97):
        if f[i] < 0:
            okf = False
            break
        d97[i] = CTA[f[i]]
    if okf and g.consistent(d97, 1, PL, CL, CI):
        res |= 2
    return res


def required(cti):
    req = np.zeros((cf.NV * 2, 24), dtype=np.int64)
    for v in range(cf.NV):
        for kx in range(2):
            req[2 * v + kx] = cf.KV[v, cf.CRIB_L, cti[cf.CRIB_I]]
    return req


def run(cta, label):
    REQ = required(cta)
    CLx = cta[cf.CRIB_I]
    hitsA = []; hitsB = []; nB = 0
    crib = {int(i): ord(CRIB_POS[int(i)]) - 65 for i in cf.CRIB_I}
    for name, f in maps():
        r = test_A(f, cta, REQ, IDX, cf.CRIB_I, g.PL, CLx)
        if r:
            hitsA.append((name, r))
        # B: key = PT[f(i)]
        pairs = [(t, crib[int(f[int(i)])]) for t, i in enumerate(cf.CRIB_I) if f[int(i)] >= 0 and int(f[int(i)]) in crib]
        if len(pairs) >= 6:
            nB += 1
            for v in range(REQ.shape[0]):
                kx = v % 2
                ds = {(REQ[v, t] - IDX[kx, k]) % 26 for t, k in pairs}
                if len(ds) == 1:
                    hitsB.append((name, v, len(pairs)))
    print(f"{label}: A(key=CT[f(i)]) hits {len(hitsA)} {hitsA[:5]} | B(key=PT[f(i)]) testable maps {nB}, hits {len(hitsB)} {hitsB[:5]}")


if __name__ == "__main__":
    run(CTA, "REAL")
    rng = np.random.default_rng(0)
    for k in range(3):
        run(rng.permutation(CTA), f"NULL{k}")
    # validation A: synthetic CT built so that key = CT reversed? (self-referential) -> build via PT-key variant instead:
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    f = np.array([(5 * i + 11) % N for i in range(N)])
    syn = [KA[(KA.index(c) + KA.index(PT[f[i]])) % 26] for i, c in enumerate(PT)]
    print("validation B (key = PT[5i+11], KA vig):")
    run(np.array([ord(x) - 65 for x in syn]), "VAL")
