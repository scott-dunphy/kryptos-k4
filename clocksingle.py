"""TEAM clock: numeric keystream vs UNKNOWN single mixed alphabet (Vig-sense: pos(C)=pos(P)+a*K+b).
Uses run_gromark.consistent (mode 1, union-find + injectivity). Scans all offsets/dirs/a/b of a sequence."""
import numpy as np
from numba import njit
from run_gromark import consistent, PL, CL, CI

UNITS = np.array([1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25], dtype=np.int64)


@njit(cache=True)
def scan_single(E, nstart, units, PL, CL, CI, hits):
    d = np.zeros(97, dtype=np.int64)
    nh = 0
    for o in range(nstart):
        for ai in range(units.shape[0]):
            a = units[ai]
            for b in range(26):
                for t in range(CI.shape[0]):
                    d[CI[t]] = (a * E[o + CI[t]] + b) % 26
                if consistent(d, 1, PL, CL, CI):
                    if nh < hits.shape[0]:
                        hits[nh, 0] = o; hits[nh, 1] = a; hits[nh, 2] = b
                    nh += 1
    return nh


def test_single(K, cyclic=True, units=UNITS):
    hits = np.zeros((1000, 4), dtype=np.int64)
    found = []
    for dr in (0, 1):
        S = np.asarray(K, dtype=np.int64) % 26
        if dr: S = S[::-1].copy()
        if cyclic:
            E = np.concatenate([S] * (97 // len(S) + 2)); ns = len(S)
        else:
            if len(S) < 97: continue
            E = S; ns = len(S) - 96
        nh = scan_single(E, ns, units, PL, CL, CI, hits)
        for h in hits[:min(nh, 1000)]:
            found.append((dr, int(h[0]), int(h[1]), int(h[2])))
    return found


@njit(cache=True)
def _sfind(par, sg, off, x):
    S = 1
    O = 0
    while par[x] != x:
        # pos(x) = sg[x]*pos(par) + off[x]
        O = (O + S * off[x]) % 26
        S = S * sg[x]
        x = par[x]
    return x, S, O


@njit(cache=True)
def consistent_beau(d, PL, CL, CI):
    """Single unknown alphabet, Beaufort sense: pos(C) = d - pos(P). Signed union-find; root-fixing
    constraints (2R = c) tracked mod 13; injectivity checked where decidable. Conservative (never rejects truth)."""
    par = np.arange(26); sg = np.ones(26, dtype=np.int64); off = np.zeros(26, dtype=np.int64)
    fix = np.full(26, -1, dtype=np.int64)  # root value mod 13 if fixed
    for t in range(CI.shape[0]):
        k = d[CI[t]]; a = PL[t]; b = CL[t]
        ra, Sa, Oa = _sfind(par, sg, off, a)
        rb, Sb, Ob = _sfind(par, sg, off, b)
        # need pos(b) = -pos(a) + k
        if ra != rb:
            s = -Sa * Sb
            o = (Sb * (-Oa + k - Ob)) % 26
            # merging fixed constraints: pos(rb)= s*pos(ra)+o ; if rb fixed (mod13) -> constraint on ra
            if fix[rb] >= 0:
                # s*R + o = fix[rb] (mod 13) -> R = s*(fix[rb]-o) mod 13
                v = (s * (fix[rb] - o)) % 13
                if fix[ra] >= 0 and fix[ra] != v:
                    return False
                fix[ra] = v
            par[rb] = ra; sg[rb] = s; off[rb] = o
        else:
            if Sb == -Sa:
                if (Ob - (-Oa + k)) % 26 != 0:
                    return False
            else:
                c = (-Oa + k - Ob) % 26  # 2*Sb*R = c
                if c % 2 == 1:
                    return False
                v = (Sb * (c // 2)) % 13
                if fix[ra] >= 0 and fix[ra] != v:
                    return False
                fix[ra] = v
    # injectivity
    used = np.zeros(26, dtype=np.int64)
    for t in range(CI.shape[0]):
        used[PL[t]] = 1; used[CL[t]] = 1
    for x in range(26):
        if used[x] == 0: continue
        rx, Sx, Ox = _sfind(par, sg, off, x)
        for y in range(x + 1, 26):
            if used[y] == 0: continue
            ry, Sy, Oy = _sfind(par, sg, off, y)
            if rx != ry: continue
            if Sx == Sy:
                if (Ox - Oy) % 26 == 0: return False
            elif fix[rx] >= 0:
                # R in {f, f+13}: collision iff (Sx-Sy)R = Oy-Ox for both candidates
                f = fix[rx]
                c1 = ((Sx - Sy) * f - (Oy - Ox)) % 26 == 0
                c2 = ((Sx - Sy) * (f + 13) - (Oy - Ox)) % 26 == 0
                if c1 and c2: return False
    return True


@njit(cache=True)
def scan_beau(E, nstart, PL, CL, CI, hits):
    d = np.zeros(97, dtype=np.int64)
    nh = 0
    for o in range(nstart):
        for b in range(26):
            for t in range(CI.shape[0]):
                d[CI[t]] = (E[o + CI[t]] + b) % 26
            if consistent_beau(d, PL, CL, CI):
                if nh < hits.shape[0]:
                    hits[nh, 0] = o; hits[nh, 1] = 1; hits[nh, 2] = b
                nh += 1
    return nh


def test_beau(K, cyclic=True):
    hits = np.zeros((1000, 4), dtype=np.int64)
    found = []
    for dr in (0, 1):
        S = np.asarray(K, dtype=np.int64) % 26
        if dr: S = S[::-1].copy()
        if cyclic:
            E = np.concatenate([S] * (97 // len(S) + 2)); ns = len(S)
        else:
            if len(S) < 97: continue
            E = S; ns = len(S) - 96
        nh = scan_beau(E, ns, PL, CL, CI, hits)
        for h in hits[:min(nh, 1000)]:
            found.append((dr, int(h[0]), int(h[1]), int(h[2])))
    return found
