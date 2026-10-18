"""Fable two-layer shortlist, cheap decisive items.
#2  half-free alphabet + running key: pos_CA(C_i) = X^-1(P_i) + s*idx(K[o+i])  (X free PT alphabet; CA in {AZ,KA})
    and mirror: pos_X(C_i) = pos_PA(P_i) + s*idx(K[o+i]) (X free CT alphabet). Consistency per letter + injectivity.
#7  key_i = T[(a*i+b) mod len(T)] for K3 PT / K3 CT (len 336/337 with '?'), all a coprime, all b; fixed alphabets.
#6  mirrored reading of copper rows (reverse columns within each row) + periodic p1-30 (cribfilter).
"""
import glob, re
import numpy as np
from numba import njit, prange
import cribfilter as cf
import kryptos_texts as kt
from k4lib import AZ, KA, CT, CRIB_POS
from perms import inverse

CI = cf.CRIB_I
PLt = cf.CRIB_L
CTL = cf.CTI[CI]
IDXT = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)


@njit(parallel=True, cache=True)
def halffree_scan(S, CI, PLt, CTL, IDXT, flags):
    """S: key indices array. For each offset, side (0: free PT alphabet, 1: free CT alphabet), fixed alph a in {AZ,KA},
    sign: consistency of letter->value map + injectivity."""
    n = S.shape[0] - 97
    for o in prange(max(n, 0)):
        val = np.empty(26, dtype=np.int64)
        used = np.empty(26, dtype=np.int64)
        for side in range(2):
            for a in range(2):
                for sg in range(2):
                    for x in range(26):
                        val[x] = -1; used[x] = -1
                    ok = True
                    for t in range(CI.shape[0]):
                        k = S[o + CI[t]]
                        if sg == 1:
                            k = (26 - k) % 26
                        if side == 0:      # X^-1(P) = pos_CA(C) - k
                            letter = PLt[t]; v = (IDXT[a, CTL[t]] - k) % 26
                        else:              # pos_X(C) = pos_PA(P) + k
                            letter = CTL[t]; v = (IDXT[a, PLt[t]] + k) % 26
                        if val[letter] == -1:
                            if used[v] != -1 and used[v] != letter:
                                ok = False; break
                            val[letter] = v; used[v] = letter
                        elif val[letter] != v:
                            ok = False; break
                    if ok:
                        flags[o] += 1


def texts():
    T = {"K0": kt.MORSE, "K1PT": kt.K1_PT, "K2PT": kt.K2_PT, "K3PT": kt.K3_PT, "K1CT": kt.K1_CT, "K2CT": kt.K2_CT}
    left = "".join(c for c in open("data/sculpture_left.txt").read() if c.isalpha())
    T["LEFT"] = left[:left.find(CT)]
    T["RIGHT"] = "".join(c for c in open("data/sculpture_right.txt").read() if c.isalpha())
    T["KEYS"] = "PALIMPSESTABSCISSAKRYPTOS" * 6
    for f in glob.glob("data/*.txt") + glob.glob("data/texts2/*.txt") + glob.glob("data/memtexts/*.txt") + ["data/carter/carter_vol1_letters.txt"]:
        if "quadgram" in f or "sculpture" in f:
            continue
        T[f.split("/")[-1]] = re.sub("[^A-Z]", "", open(f, errors="ignore").read().upper())
    return T


def run2(label, ctl):
    tot = 0
    for name, s in texts().items():
        if len(s) < 120:
            s = s + s
        for kal in (AZ, KA):
            for st in (s, s[::-1]):
                S = np.array([kal.index(c) for c in st], dtype=np.int64)
                fl = np.zeros(max(len(S) - 97, 1), dtype=np.int64)
                halffree_scan(S, CI, PLt, ctl, IDXT, fl)
                h = int((fl > 0).sum()); tot += h
                if h:
                    print(f"  {label} #2 hit {name} {h}")
    print(f"{label} #2 half-free + running key: total hits {tot}", flush=True)


def run7():
    left = "".join(c for c in open("data/sculpture_left.txt").read() if c.isalpha() or c == "?")
    k3ct = left[left.find("ENDYAHR"):left.find(CT)].replace("?", "")
    hits = 0
    for name, T in (("K3PT", kt.K3_PT), ("K3CT", k3ct), ("K3PT?", kt.K3_PT + "Q"), ("K3CT?", k3ct + "Q")):
        L = len(T)
        for kal in (AZ, KA):
            Ti = np.array([kal.index(c) for c in T])
            for a in range(1, L):
                if np.gcd(a, L) != 1:
                    continue
                for b in range(L):
                    key = Ti[(a * CI + b) % L]
                    for v in range(cf.NV):
                        d = (cf.KV[v, PLt, CTL] - key) % 26
                        if (d == d[0]).all():
                            hits += 1
                            print("  #7 hit", name, a, b, cf.VARIANTS[v][:3])
    print("#7 K3-addressed keys (all affine maps on K3 PT/CT): hits", hits, flush=True)


def run6():
    cells = [(0, c) for c in range(27, 31)] + [(r, c) for r in range(1, 4) for c in range(31)]
    pos = {x: i for i, x in enumerate(cells)}
    perms = []
    for mode in ("mirror", "rot180", "rowflip"):
        f = []
        for (r, c) in cells:
            r2, c2 = (r, 30 - c) if mode == "mirror" else ((3 - r, 30 - c) if mode == "rot180" else (3 - r, c))
            f.append(pos.get((r2, c2), -1))
        # read cells in mirrored order: order of original indices sorted by transformed position (skip empties)
        order = sorted(range(97), key=lambda i: (f[i] if f[i] >= 0 else 1000 + i))
        p = np.array(order); perms += [p, inverse(p)]
    invs = np.array([inverse(p) for p in perms])
    out = np.zeros((1000, 5), dtype=np.int64)
    n = cf.check_batch(invs, 1, 30, cf.KV, cf.CTI, CI, PLt, 4, out)
    print("#6 mirrored/rotated copper reading + periodic p1-30: survivors", n, flush=True)


if __name__ == "__main__":
    # validation #2: free PT alphabet (random) + KA vig with running key K2PT offset 50
    rng = np.random.default_rng(3)
    X = rng.permutation(26); Xinv = np.argsort(X)
    K = kt.K2_PT
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    syn = [AZ[(Xinv[ord(p) - 65] + AZ.index(K[50 + i])) % 26] for i, p in enumerate(PT)]
    S = np.array([AZ.index(c) for c in K], dtype=np.int64)
    fl = np.zeros(len(S) - 97, dtype=np.int64)
    halffree_scan(S, CI, PLt, np.array([ord(syn[i]) - 65 for i in CI]), IDXT, fl)
    print("validation #2 planted offset 50 found:", bool(fl[50]), "total", int((fl > 0).sum()))
    run2("REAL", CTL)
    run2("NULL", rng.permutation(cf.CTI)[CI])
    run7()
    run6()
