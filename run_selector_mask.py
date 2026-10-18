"""Fable test 3: 2-4 masking charts chosen by a visual pattern on the 31-column sheet + one continuous keyword.

Table layer pinned as in run_pinned_table.py (keyword, all phases, KA/AZ tableau, Vig/Beau/Var, both orders).
Residual must be an injective map WITHIN each selector class (one chart per class).
Layouts: K4 as on copper/NOVA sheet (starts at column 27), K4 from column 0, K4 from column 1 ('?' at col 0).
checks = sum over classes of (#cribs in class - #distinct mask-side letters in class).
Reported: consistent configs by checks; >= 7 treated as real, 6 as lead (Fable estimate 0.16 chance hits at 6).
"""
import sys
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS
from run_pinned_table import keywords, residual, KAI, KAL, CI, NC

def selectors():
    out = {}
    for lname, start in (("sheet27", 27), ("col0", 0), ("col1", 1)):
        rc = [((i + start) // 31, (i + start) % 31) for i in range(97)]
        fns = {
            "c%2": lambda r, c: c % 2, "c%3": lambda r, c: c % 3, "c%4": lambda r, c: c % 4,
            "(r+c)%2": lambda r, c: (r + c) % 2, "(r+c)%3": lambda r, c: (r + c) % 3, "(r+c)%4": lambda r, c: (r + c) % 4,
            "half": lambda r, c: int(c >= 16), "thirds": lambda r, c: 0 if c < 10 else (1 if c < 20 else 2),
            "(c-r)%2": lambda r, c: (c - r) % 2, "(c-r)%3": lambda r, c: (c - r) % 3, "row%2": lambda r, c: r % 2,
        }
        for fname, fn in fns.items():
            out[f"{lname} {fname}"] = tuple(fn(r, c) for r, c in rc)
    for m in (2, 3, 4):
        out[f"i%{m}"] = tuple(i % m for i in range(97))
    seen, labels, arr = set(), [], []
    for k, v in out.items():
        # canonical relabel to dedupe
        mp, can = {}, []
        for x in v:
            mp.setdefault(x, len(mp)); can.append(mp[x])
        t = tuple(can)
        if t not in seen and len(mp) > 1:
            seen.add(t); labels.append(k); arr.append(can)
    return labels, np.array(arr, dtype=np.int64)


@njit(cache=True)
def class_check(res, sel):
    # injective per class; returns checks or -1
    fwd = np.full((4, 26), -1, dtype=np.int64)
    bwd = np.full((4, 26), -1, dtype=np.int64)
    checks = 0
    for e in range(NC):
        g = sel[CI[e]]
        a = res[e, 0]; b = res[e, 1]
        if fwd[g, a] == -1 and bwd[g, b] == -1:
            fwd[g, a] = b; bwd[g, b] = a
        elif fwd[g, a] == b and bwd[g, b] == a:
            checks += 1
        else:
            return -1
    return checks


@njit(parallel=True, cache=True)
def scan(cti, KW, LENS, SEL, KAI, KAL, hist, hits, nh):
    W = KW.shape[0]
    S = SEL.shape[0]
    loc = np.zeros((W, S, 25), dtype=np.int64)
    for q in prange(W):
        L = LENS[q]
        res = np.zeros((NC, 2), dtype=np.int64)
        for f in range(L):
            for tab in range(2):
                for rule in range(3):
                    for order in range(2):
                        residual(cti, KW[q], L, f, tab, rule, order, KAI, KAL, res)
                        for s in range(S):
                            ch = class_check(res, SEL[s])
                            if ch >= 0:
                                loc[q, s, ch] += 1
                                if ch >= 4:
                                    k = nh[0]
                                    if k < hits.shape[0]:
                                        hits[k, 0] = q; hits[k, 1] = f; hits[k, 2] = tab; hits[k, 3] = rule
                                        hits[k, 4] = order; hits[k, 5] = s; hits[k, 6] = ch
                                    nh[0] = k + 1
    for q in range(W):
        for s in range(S):
            for c in range(25):
                hist[s, c] += loc[q, s, c]


def run(ct, KW, LENS, SEL):
    cti = np.array([ord(c) - 65 for c in ct], dtype=np.int64)
    hist = np.zeros((SEL.shape[0], 25), dtype=np.int64)
    hits = np.zeros((200000, 7), dtype=np.int64)
    nh = np.zeros(1, dtype=np.int64)
    scan(cti, KW, LENS, SEL, KAI, KAL, hist, hits, nh)
    return hist, hits[:min(nh[0], 200000)]


def planted(rng, sel):
    from k4lib import AZ, KA
    kw = "PALIMPSEST"
    masks = [rng.permutation(26) for _ in range(4)]
    pt = rng.integers(0, 26, 97)
    for i, ch in CRIB_POS.items():
        pt[i] = ord(ch) - 65
    out = []
    for i in range(97):
        y = masks[sel[i]][pt[i]]
        xi = KA.index(AZ[y]); ki = KA.index(kw[i % len(kw)])
        out.append(KA[(xi + ki) % 26])   # mask, then KA Vigenere
    return "".join(out), kw


if __name__ == "__main__":
    nnull = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    ks, KW, LENS = keywords()
    labels, SEL = selectors()
    print("keywords", len(ks), "selectors", len(labels), flush=True)
    rng = np.random.default_rng(20261018)
    s0 = labels.index("sheet27 (r+c)%2")
    pct, kw = planted(rng, SEL[s0])
    q = ks.index(kw)
    h, _ = run(pct, KW[q:q + 1], LENS[q:q + 1], SEL[s0:s0 + 1])
    print("planted PALIMPSEST sheet27 (r+c)%2 consistent by checks:", {c: int(v) for c, v in enumerate(h[0]) if v}, flush=True)
    t = time.time()
    hist, hits = run(CT, KW, LENS, SEL)
    print("scan time", round(time.time() - t, 1), flush=True)
    tot = hist.sum(0)
    print("REAL consistent by checks (all selectors):", {c: int(v) for c, v in enumerate(tot) if v}, flush=True)
    for row in hits[:30]:
        q, f, tab, rule, order, s, ch = row
        print(f"  hit {ks[q]} ph{f} {'KA' if tab else 'AZ'} {['vig','beau','var'][rule]} "
              f"{'mask>table' if order == 0 else 'table>mask'} {labels[s]} checks={ch}", flush=True)
    cl = list(CT)
    for s in range(nnull):
        rng.shuffle(cl)
        h2, _ = run("".join(cl), KW, LENS, SEL)
        print(f"NULL{s} consistent by checks:", {c: int(v) for c, v in enumerate(h2.sum(0)) if v}, flush=True)
