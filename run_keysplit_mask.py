"""Fable test 2: mask + key split (dictionary keyword + lore keyword summed), exact.

PT-side mask:  A^-1(C_i) = m(P_i) + s1*k1_i + s2*k2_i      (A numbers the CT side: AZ or KA)
CT-side mask:  m(C_i)    = A^-1(P_i) + s1*k1_i + s2*k2_i    (A numbers the PT side)
k1 = dictionary word (length L1, any phase), k2 = lore word (any phase), key letters indexed AZ or KA.
Stage A (necessary): with k2 pinned, k1 replaced by an ARBITRARY period-L1 key -> union-find + injectivity
(as run_mask_trans.py, identity perm). Stage B: for surviving (k2 stream, L1), every dictionary word of
length L1, all phases, both signs and key indexings, exact injectivity of the residual map.
"""
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, AZ, KA
from run_alphapairs import load_words
from run_mask_trans import find

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
NC = CI.shape[0]
KAI = np.array([KA.index(c) for c in AZ], dtype=np.int64)
LMAX = 26


@njit(cache=True)
def stageA(dom, val, L):
    """dom[e] = mask-side letter, val[e] = known side number minus pinned keys. Arbitrary period-L key."""
    par = np.arange(26 + LMAX)
    off = np.zeros(26 + LMAX, dtype=np.int64)
    checks = 0
    for e in range(NC):
        u = dom[e]; v = 26 + CI[e] % L
        ru, ou = find(par, off, u)
        rv, ov = find(par, off, v)
        if ru == rv:
            if (ou - ov - val[e]) % 26 != 0:
                return -1
            checks += 1
        else:
            par[ru] = rv
            off[ru] = (val[e] + ov - ou) % 26
    seen = np.full((26 + LMAX, 26), -1, dtype=np.int64)
    for x in range(26):
        rx, ox = find(par, off, x)
        if seen[rx, ox] >= 0:
            return -1
        seen[rx, ox] = x
    return checks


@njit(cache=True)
def inj_ok(dom, res):
    fwd = np.full(26, -1, dtype=np.int64)
    bwd = np.full(26, -1, dtype=np.int64)
    for e in range(NC):
        a = dom[e]; b = res[e]
        if fwd[a] == -1 and bwd[b] == -1:
            fwd[a] = b; bwd[b] = a
        elif fwd[a] != b or bwd[b] != a:
            return False
    return True


@njit(parallel=True, cache=True)
def stageB(dom, val, words, L, KAI):
    W = words.shape[0]
    cnt = np.zeros(W, dtype=np.int64)
    for q in prange(W):
        res = np.zeros(NC, dtype=np.int64)
        for f in range(L):
            for kidx in range(2):
                for s1 in (1, -1):
                    for e in range(NC):
                        k = words[q, (CI[e] + f) % L]
                        if kidx == 1:
                            k = KAI[k]
                        res[e] = (val[e] - s1 * k) % 26
                    if inj_ok(dom, res):
                        cnt[q] += 1
    return cnt


def lore_words():
    lore, _ = load_words()
    extra = "PALIMPCEST XLAYERTWO IDBYROWS EQUAL QUAE KRYPTOSABCDEFGHIJLMNQUVWXZ WEBSTER NOVEMBER".split()
    return sorted(set(lore + extra))


def dict_by_len():
    _, words = load_words()
    out = {}
    for L in range(1, LMAX + 1):
        ws = [w for w in words if len(w) == L]
        arr = np.array([[ord(c) - 65 for c in w] for w in ws], dtype=np.int64).reshape(len(ws), L)
        out[L] = (ws, arr)
    return out


def run(ct, D, label, verbose=True):
    cti = np.array([ord(c) - 65 for c in ct], dtype=np.int64)
    ctc = cti[CI]
    nA = survA = 0
    hits = []
    for w2 in lore_words():
        k2w = np.array([ord(c) - 65 for c in w2])
        for f2 in range(len(w2)):
            k2 = k2w[(CI + f2) % len(w2)]
            for k2idx in range(2):
                kk = KAI[k2] if k2idx else k2
                for s2 in (1, -1):
                    for side in range(2):
                        for num in range(2):
                            if side == 0:
                                dom = PL
                                known = ctc if num == 0 else KAI[ctc]
                                val = (known - s2 * kk) % 26
                            else:
                                dom = ctc
                                known = PL if num == 0 else KAI[PL]
                                val = (known + s2 * kk) % 26
                            for L1 in range(1, LMAX + 1):
                                nA += 1
                                ch = stageA(dom, val, L1)
                                if ch < 0:
                                    continue
                                survA += 1
                                ws, arr = D[L1]
                                if len(ws) == 0:
                                    continue
                                cnt = stageB(dom, val, arr, L1, KAI)
                                for q in np.nonzero(cnt)[0]:
                                    hits.append((w2, f2, k2idx, s2, side, num, L1, ch, ws[q], int(cnt[q])))
    print(f"[{label}] stageA configs {nA}, survivors (>=1 check) {survA}, stageB word hits {len(hits)}", flush=True)
    if verbose:
        for h in sorted(hits, key=lambda h: -h[7])[:20]:
            print(f"[{label}]   lore {h[0]} ph{h[1]} {'KA' if h[2] else 'AZ'} s2={h[3]} {'PT' if h[4] == 0 else 'CT'}-mask "
                  f"num {'KA' if h[5] else 'AZ'} L1={h[6]} checks={h[7]} word {h[8]} x{h[9]}", flush=True)
    return survA, hits


def planted(rng, D):
    # PT-side mask, CT numbered KA, k1 = SHADOW (AZ idx), k2 = KRYPTOS (AZ idx), both +
    m = rng.permutation(26)
    pt = rng.integers(0, 26, 97)
    for i, ch in CRIB_POS.items():
        pt[i] = ord(ch) - 65
    k1 = [ord(c) - 65 for c in "SHADOW"]; k2 = [ord(c) - 65 for c in "KRYPTOS"]
    KA2AZ = [AZ.index(c) for c in KA]
    ct = "".join(AZ[KA2AZ[(m[pt[i]] + k1[i % 6] + k2[i % 7]) % 26]] for i in range(97))
    return ct


if __name__ == "__main__":
    D = dict_by_len()
    print("lore words", len(lore_words()), "dict sizes", {L: len(D[L][0]) for L in (5, 8, 10, 13, 16)}, flush=True)
    rng = np.random.default_rng(20261018)
    t = time.time()
    _, h = run(planted(rng, D), D, "PLANTED", verbose=False)
    print("planted: SHADOW found:", any(x[8] == "SHADOW" and x[0] == "KRYPTOS" for x in h), "time", round(time.time() - t, 1), flush=True)
    t = time.time()
    run(CT, D, "REAL")
    print("time", round(time.time() - t, 1), flush=True)
    cl = list(CT)
    for s in range(3):
        rng.shuffle(cl)
        run("".join(cl), D, f"NULL{s}", verbose=False)
