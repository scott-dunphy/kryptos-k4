"""Historic disk/rotor systems.

T1 single stepping rotor / rotating cipher disk (Hebern, Kryha-regular, Alberti turned per letter):
   C_i = ringC[ R( ringP^-1(P_i) + a*floor(i/m) ) - c*floor(i/m) ]   (constant offsets absorbed into unknown R)
   rings in {AZ, KA}, a,c in 0..25, m in 1..6. Test: each crib gives R(x)=y; consistency = function + injective.
T2 Alberti indicator segments: shift constant within segments, changing at unknown points.
   T2a single unknown alphabet (cpos(C)=ppos(P)+s_seg), <=1 change point per crib run, shifts brute-forced.
   T2b fixed alphabet pairs (base x dictionary, both roles, vig/beau/var): count shift changes inside the two crib
       runs; flag <=2 per run (random expectation ~ 12 + 10 changes).
"""
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet
import run_gromark as g

CI = g.CI; PL = g.PL; CL = g.CL
RINGS = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)  # letter -> ring pos


@njit(cache=True)
def rotor_ok(a, c, m, rp, rc, RINGS, PL, CL, CI):
    fwd = np.full(26, -1, dtype=np.int64)
    bwd = np.full(26, -1, dtype=np.int64)
    for t in range(CI.shape[0]):
        st = CI[t] // m
        x = (RINGS[rp, PL[t]] + a * st) % 26
        y = (RINGS[rc, CL[t]] + c * st) % 26
        if fwd[x] == -1 and bwd[y] == -1:
            fwd[x] = y; bwd[y] = x
        elif fwd[x] != y or bwd[y] != x:
            return False
    return True


@njit(cache=True)
def t1(RINGS, PL, CL, CI, hits):
    n = 0
    for rp in range(2):
        for rc in range(2):
            for m in range(1, 7):
                for a in range(26):
                    for c in range(26):
                        if rotor_ok(a, c, m, rp, rc, RINGS, PL, CL, CI):
                            hits[n, 0] = rp; hits[n, 1] = rc; hits[n, 2] = m; hits[n, 3] = a; hits[n, 4] = c
                            n += 1
    return n


@njit(parallel=True, cache=True)
def t2a(PL, CL, CI, flags):
    # run1 = crib idx 0..12 (pos 21-33), run2 = 13..23 (pos 63-73). change point k1 in 0..12 (0 = none), k2 in 0..10
    for k1 in prange(13):
        d = np.zeros(97, dtype=np.int64)
        for k2 in range(11):
            for s1 in range(26):          # run1 second segment shift (first absorbed = 0)
                for s2 in range(26):      # run2 first segment
                    for s3 in range(26):  # run2 second segment
                        if k1 == 0 and s1 > 0:
                            continue
                        if k2 == 0 and s3 > 0:
                            continue
                        for t in range(24):
                            if t < 13:
                                d[CI[t]] = 0 if (k1 == 0 or t < k1) else s1
                            else:
                                u = t - 13
                                d[CI[t]] = s2 if (k2 == 0 or u < k2) else s3
                        if g.consistent(d, 1, PL, CL, CI):
                            flags[k1, k2] += 1


@njit(parallel=True, cache=True)
def t2b(TA, TB, PL, CL, best):
    for b in prange(TB.shape[0]):
        k = np.empty(24, dtype=np.int64)
        bm = 99
        for a in range(TA.shape[0]):
            for rule in range(3):
                for t in range(24):
                    ip = TA[a, PL[t]]; ic = TB[b, CL[t]]
                    k[t] = (ic - ip) % 26 if rule == 0 else ((ic + ip) % 26 if rule == 1 else (ip - ic) % 26)
                ch1 = 0; ch2 = 0
                for t in range(1, 13):
                    if k[t] != k[t - 1]:
                        ch1 += 1
                for t in range(14, 24):
                    if k[t] != k[t - 1]:
                        ch2 += 1
                tot = max(ch1, ch2)
                if tot < bm:
                    bm = tot
        best[b] = bm


if __name__ == "__main__":
    from run_alphapairs import load_words, pos_table
    # ---- T1 validation: plant rotor
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    rng = np.random.default_rng(4); R = rng.permutation(26); a0, c0, m0 = 1, 3, 1
    syn = []
    for i, ch in enumerate(PT):
        st = i // m0
        y = (R[(AZ.index(ch) + a0 * st) % 26] - c0 * st) % 26
        syn.append(KA[y])
    CLs = np.array([ord(syn[i]) - 65 for i in CI])
    hits = np.zeros((20000, 5), dtype=np.int64)
    n = t1(RINGS, PL, CLs, CI, hits)
    print("T1 validation hits", n, "truth", any((h[0], h[1], h[2], h[3], h[4]) == (0, 1, 1, a0, c0) for h in hits[:n]))
    n = t1(RINGS, PL, CL, CI, hits)
    print("T1 REAL rotor hits", n, hits[:min(n, 10)].tolist())
    nul = [t1(RINGS, PL, rng.integers(0, 26, 24), CI, hits) for _ in range(20)]
    print("T1 null (20 random CT) hits:", nul)
    # ---- T2a
    t = time.time()
    fl = np.zeros((13, 11), dtype=np.int64); t2a(PL, CL, CI, fl)
    print("T2a REAL (unknown alphabet, <=1 change/run) hits", int(fl.sum()), round(time.time() - t), "s")
    fln = np.zeros((13, 11), dtype=np.int64); t2a(PL, rng.integers(0, 26, 24), CI, fln)
    print("T2a null hits", int(fln.sum()))
    # T2a validation: plant segment cipher
    A = rng.permutation(26); Apos = np.argsort(A)
    seg = {i: (0 if i < 27 else 9) for i in range(21, 34)}; seg.update({i: (4 if i < 66 else 17) for i in range(63, 74)})
    synL = [A[(Apos[ord(CRIB_POS[i]) - 65] + seg[i]) % 26] for i in sorted(CRIB_POS)]
    flv = np.zeros((13, 11), dtype=np.int64); t2a(PL, np.array(synL), CI, flv)
    print("T2a validation hits", int(flv.sum()), "at change points", np.argwhere(flv > 0)[:5].tolist())
    # ---- T2b
    lore, words = load_words()
    def alphas(ws):
        res, seen = [], set()
        for w in ws:
            for rev in (0, 1):
                al = keyed_alphabet(w); al = al[::-1] if rev else al
                if al not in seen:
                    seen.add(al); res.append((w + ("~rev" if rev else ""), al))
        return res
    base = alphas(["", "KRYPTOS"] + lore); allw = alphas(words)
    TA = np.array([pos_table(a) for _, a in base]); TB = np.array([pos_table(a) for _, a in allw])
    for lab, X, Y, NY in (("PT=base", TA, TB, allw), ("CT=base", TB, TA, base)):
        best = np.zeros(Y.shape[0], dtype=np.int64); t2b(X, Y, PL, CL, best)
        print("T2b", lab, "min max-changes-per-run", int(best.min()), "count<=2:", int((best <= 2).sum()),
              "count<=4:", int((best <= 4).sum()))
    rand = np.array([np.argsort(rng.permutation(26)) for _ in range(len(allw))])
    best = np.zeros(len(allw), dtype=np.int64); t2b(TA, rand, PL, CL, best)
    print("T2b NULL random alphabets: min", int(best.min()), "count<=2:", int((best <= 2).sum()), "count<=4:", int((best <= 4).sum()))
