"""Two-layer test: transposition (K3-style families) + arbitrary mask alphabet + periodic key (K1/K2-style).

Model, one side free (Scheidt "mask" = arbitrary substitution; K1/K2 = periodic tableau key):
  PT-free:  A^-1(C_j) = s(P_i) + k_r      s arbitrary bijection, A in {AZ, KA} numbers the CT side
  CT-free:  t(C_j)    = A^-1(P_i) + k_r   t arbitrary bijection, A numbers the PT side
Vig/Beau/Var collapse into these (sign absorbed by the free alphabet and the free key).
Transposition: PT position i lands at CT position j = inv[i]; residue r = i % L (substitute, then transpose)
or j % L (transpose, then substitute). Exact test: union-find with potentials mod 26, plus injectivity
of the free alphabet inside each component. "checks" = number of cycle-closing equations.
Identity permutation reproduces Barney's direct mask result (PT-free dead at L=1-12,14,15,17,21,22).
"""
import sys
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, AZ, KA
from perms import route_perms, columnar_all, columnar_keywords, inverse

N = 97
CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
KAI = np.array([KA.index(c) for c in AZ], dtype=np.int64)  # AZ letter -> KA index
LMAX = 26


def double_rotations(n, wmax=48):
    """K3 process: write rows of width W1, rotate 90 deg CW, write result in rows of W2, rotate again.
    Ragged last row; empty cells skipped. Rotating CW = read columns left to right, bottom to top."""
    def rot(seq, W):
        R = -(-len(seq) // W)
        out = []
        for c in range(W):
            for r in range(R - 1, -1, -1):
                k = r * W + c
                if k < len(seq):
                    out.append(seq[k])
        return out
    for W1 in range(2, wmax + 1):
        a = rot(list(range(n)), W1)
        for W2 in range(2, wmax + 1):
            yield f"dblrot {W1}x{W2}", np.array(rot(a, W2), dtype=np.int64)


def decimations(n):
    for a in range(2, n - 1):
        for b in range(n):
            yield f"decim a{a} b{b}", np.array([(a * j + b) % n for j in range(n)], dtype=np.int64)


def build_perms():
    labels, perms = ["identity"], [np.arange(N)]
    gens = (route_perms(N), columnar_all(N, 8), double_rotations(N), decimations(N),
            columnar_keywords(N, "KRYPTOS PALIMPSEST ABSCISSA BERLIN CLOCK LAYERTWO SHADOW".split()))
    for g in gens:
        for l, p in g:
            labels.append(l + " fwd"); perms.append(p)
            labels.append(l + " inv"); perms.append(inverse(p))
    # dedupe
    seen, L2, P2 = set(), [], []
    for l, p in zip(labels, perms):
        key = p.tobytes()
        if key not in seen:
            seen.add(key); L2.append(l); P2.append(p)
    invs = np.array([inverse(p) for p in P2])  # invs[q][i] = CT position of PT position i
    return L2, invs


@njit(cache=True)
def find(par, off, x):
    # returns root, offset pot[x]-pot[root]
    o = 0
    r = x
    while par[r] != r:
        o = (o + off[r]) % 26
        r = par[r]
    # path compression
    y = x
    oy = o
    while par[y] != y:
        nxt = par[y]
        ny = (oy - off[y]) % 26
        par[y] = r
        off[y] = oy
        y = nxt
        oy = ny
    return r, o


@njit(cache=True)
def test_model(inv, cti, L, order, side, alph, PL, CI, KAI):
    """returns checks (>=0) if consistent, -1 if inconsistent."""
    par = np.arange(26 + LMAX)
    off = np.zeros(26 + LMAX, dtype=np.int64)
    checks = 0
    for e in range(CI.shape[0]):
        i = CI[e]
        j = inv[i]
        r = (i if order == 0 else j) % L
        p = PL[e]
        c = cti[j]
        if side == 0:      # PT free: node = PT letter, value = numbered CT
            u = p
            val = c if alph == 0 else KAI[c]
        else:              # CT free: node = CT letter, value = numbered PT
            u = c
            val = p if alph == 0 else KAI[p]
        v = 26 + r
        ru, ou = find(par, off, u)
        rv, ov = find(par, off, v)
        # want pot[u] - pot[v] = val
        if ru == rv:
            if (ou - ov - val) % 26 != 0:
                return -1
            checks += 1
        else:
            # attach ru under rv: pot[ru] - pot[rv] = val + ov - ou
            par[ru] = rv
            off[ru] = (val + ov - ou) % 26
    # injectivity: distinct letters in a component need distinct potentials
    seen = np.full((26 + LMAX, 26), -1, dtype=np.int64)
    for x in range(26):
        rx, ox = find(par, off, x)
        if rx == x and par[x] == x:
            # singleton or root; still check below
            pass
        if seen[rx, ox] >= 0:
            # only letters that occurred matter; singletons never collide
            return -1
        seen[rx, ox] = x
    return checks


@njit(parallel=True, cache=True)
def scan(invs, cti, PL, CI, KAI, out):
    # out[q, order, side, alph, L] = checks or -1
    Q = invs.shape[0]
    for q in prange(Q):
        for order in range(2):
            for side in range(2):
                for alph in range(2):
                    for L in range(1, LMAX + 1):
                        out[q, order, side, alph, L - 1] = test_model(invs[q], cti, L, order, side, alph, PL, CI, KAI)


def summarize(out, labels, tag, min_checks=3, show=10):
    cons = out >= 0
    print(f"[{tag}] consistent models: {int(cons.sum())} of {out.size}", flush=True)
    for thr in (1, 2, 3, 4, 5, 6, 8):
        print(f"[{tag}]   checks>={thr}: {int((out >= thr).sum())}", flush=True)
    idx = np.argwhere(out >= min_checks)
    order = np.argsort(-out[tuple(idx.T)]) if len(idx) else []
    for k in list(order)[:show]:
        q, o, s, a, L = idx[k]
        print(f"[{tag}]   {labels[q]} | {'sub>trans' if o == 0 else 'trans>sub'} | {'PT' if s == 0 else 'CT'}-free | "
              f"{'AZ' if a == 0 else 'KA'} | L={L + 1} | checks={out[q, o, s, a, L]}", flush=True)


def identity_table(out):
    print("identity (direct) consistent periods:")
    for s in range(2):
        for a in range(2):
            Ls = [L + 1 for L in range(LMAX) if out[0, 0, s, a, L] >= 0]
            print(f"  {'PT' if s == 0 else 'CT'}-free {'AZ' if a == 0 else 'KA'}: {Ls}")


def planted(labels, invs, rng):
    """Encrypt a synthetic message with a random family perm, random mask, random period key; check detection."""
    import random
    ok = 0
    trials = 6
    for t in range(trials):
        q = rng.integers(1, len(invs))
        L = int(rng.integers(3, 9))
        order = int(rng.integers(0, 2))
        side = int(rng.integers(0, 2))
        alph = int(rng.integers(0, 2))
        pt = rng.integers(0, 26, N)
        for i, ch in CRIB_POS.items():
            pt[i] = ord(ch) - 65
        mask = rng.permutation(26)
        key = rng.integers(0, 26, L)
        inv = invs[q]
        ct = np.zeros(N, dtype=np.int64)
        KA2AZ = np.array([AZ.index(c) for c in KA])
        for i in range(N):
            j = inv[i]
            r = (i if order == 0 else j) % L
            if side == 0:
                v = (mask[pt[i]] + key[r]) % 26          # numbered CT value
                ct[j] = v if alph == 0 else KA2AZ[v]
            else:
                pv = pt[i] if alph == 0 else KAI[pt[i]]
                ct[j] = mask[(pv + key[r]) % 26]
        res = test_model(inv, ct, L, order, side, alph, PL, CI, KAI)
        print(f"  planted {labels[q]} L={L} order={order} side={side} alph={alph}: checks={res}")
        ok += res >= 0
    print(f"planted recovered {ok}/{trials}")


if __name__ == "__main__":
    nnull = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    labels, invs = build_perms()
    print("perms (deduped, incl. inverses):", len(invs), flush=True)
    rng = np.random.default_rng(20261018)
    planted(labels, invs, rng)
    cti = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
    out = np.zeros((len(invs), 2, 2, 2, LMAX), dtype=np.int64)
    t = time.time()
    scan(invs, cti, PL, CI, KAI, out)
    print("scan time", round(time.time() - t, 1), flush=True)
    identity_table(out)
    summarize(out, labels, "REAL", show=25)
    np.save("results/mask_trans_real.npy", out)
    nullstats = []
    for s in range(nnull):
        sh = rng.permutation(cti)
        o2 = np.zeros_like(out)
        scan(invs, sh, PL, CI, KAI, o2)
        summarize(o2, labels, f"NULL{s}", show=0)
        nullstats.append([int((o2 >= thr).sum()) for thr in (0, 1, 2, 3, 4, 5, 6, 8)])
    ns = np.array(nullstats)
    real = [int((out >= thr).sum()) for thr in (0, 1, 2, 3, 4, 5, 6, 8)]
    print("thr      :", [0, 1, 2, 3, 4, 5, 6, 8])
    print("REAL     :", real)
    print("NULL mean:", ns.mean(0).round(1).tolist())
    print("NULL max :", ns.max(0).tolist())
