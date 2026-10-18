"""Pinned table layer + masking chart (lead #1, 2026-10-18).

Layer T (pinned, K1/K2 style): keyword W repeated with phase f on tableau A in {KA, AZ}, rule Vig/Beau/Var,
key letter indexed in A. Layer M (free): one fixed substitution chart s (any bijection), optionally followed
by a small "nuance" shift |n_i| <= w in plain AZ or KA numbering.
  order 0 (mask, then table):  C = T(M(P))  ->  Y_i = T^-1(C_i) must equal s(P_i) [+ n_i]
  order 1 (table, then mask):  C = M(T(P))  ->  Z_i = T(P_i);  C_i must equal s(Z_i) [+ n_i]
Tests, each over all keystreams:
  exact   : s injective partial map on the 24 crib pairs, with up to one crib pair dropped (Sanborn slip)
  nuance w: exists injective s with |Y_i - s(P_i)| <= w for all 24 (bipartite matching), w = 1, 2
False-pass rate measured on shuffled ciphertexts; planted encryptions must be found.
"""
import sys
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, AZ, KA
from kryptos_texts import K1_PT, K2_PT, K3_PT, MORSE
from run_alphapairs import load_words

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
NC = CI.shape[0]
KAI = np.array([KA.index(c) for c in AZ], dtype=np.int64)   # AZ letter -> KA index
KAL = np.array([AZ.index(c) for c in KA], dtype=np.int64)   # KA index -> AZ letter
LMAXW = 26


def keywords():
    lore, words = load_words()
    ks = set(w for w in words if len(w) <= LMAXW)
    for t in (K1_PT, K2_PT, K3_PT, MORSE):
        t = t.replace("?", "")
        for L in range(4, 27):
            for s in range(len(t) - L + 1):
                ks.add(t[s:s + L])
    for w in ("PALIMPCEST XLAYERTWO IDBYROWS LAYERTWO EQUAL KRYPTOSABCDEFGHIJLMNQUVWXZ ABCDEFGHIJKLMNOPQRSTUVWXYZ "
              "BERLINWALL FALLOFTHEBERLINWALL WELTZEITUHR WORLDCLOCK ALEXANDERPLATZ NOVEMBER NINETEENEIGHTYNINE "
              "EGYPT NINETEENEIGHTYSIX TUTANKHAMUN HOWARDCARTER DELIVERINGAMESSAGE MESSAGE SANBORN SCHEIDT "
              "EDSCHEIDT JIMSANBORN WEBSTER WILLIAMWEBSTER SHADOW LIGHT NUANCE MASK MASKING").split():
        ks.add(w)
    ks = sorted(k for k in ks if 1 <= len(k) <= LMAXW and k.isalpha())
    arr = np.zeros((len(ks), LMAXW), dtype=np.int64)
    lens = np.zeros(len(ks), dtype=np.int64)
    for i, k in enumerate(ks):
        lens[i] = len(k)
        arr[i, :len(k)] = [ord(c) - 65 for c in k]
    return ks, arr, lens


@njit(cache=True)
def residual(cti, kw, L, f, tab, rule, order, KAI, KAL, out):
    """Fill out[e] = residual letter (AZ index) at crib e; also returns nothing."""
    for e in range(NC):
        i = CI[e]
        k = kw[(i + f) % L]
        if order == 0:
            x = cti[i]
            src = PL[e]
        else:
            x = PL[e]
            src = cti[i]
        if tab == 1:
            xi = KAI[x]; ki = KAI[k]
        else:
            xi = x; ki = k
        if order == 0:      # Y = T^-1(C)
            if rule == 0:
                yi = (xi - ki) % 26
            elif rule == 1:
                yi = (ki - xi) % 26
            else:
                yi = (xi + ki) % 26
        else:               # Z = T(P)
            if rule == 0:
                yi = (xi + ki) % 26
            elif rule == 1:
                yi = (ki - xi) % 26
            else:
                yi = (xi - ki) % 26
        out[e, 0] = src if order == 1 else PL[e]   # domain letter of the mask (PT for order 0, Z for order 1)
        out[e, 1] = KAL[yi] if tab == 1 else yi    # residual letter
        if order == 1:
            out[e, 0] = KAL[yi] if tab == 1 else yi  # domain = Z
            out[e, 1] = src                          # range = C


@njit(cache=True)
def exact_viol(res, drop):
    # count conflicts of injective partial map dom->rng, skipping crib index `drop`
    fwd = np.full(26, -1, dtype=np.int64)
    bwd = np.full(26, -1, dtype=np.int64)
    for e in range(NC):
        if e == drop:
            continue
        a = res[e, 0]; b = res[e, 1]
        if fwd[a] == -1 and bwd[b] == -1:
            fwd[a] = b; bwd[b] = a
        elif fwd[a] != b or bwd[b] != a:
            return 1
    return 0


@njit(cache=True)
def nuance_ok(res, w, numb, KAI):
    # candidate values for each domain letter: intersection of windows around its residual values
    allow = np.ones((26, 26), dtype=np.bool_)
    used = np.zeros(26, dtype=np.bool_)
    for e in range(NC):
        a = res[e, 0]
        y = res[e, 1] if numb == 0 else KAI[res[e, 1]]
        used[a] = True
        row = np.zeros(26, dtype=np.bool_)
        for d in range(-w, w + 1):
            row[(y + d) % 26] = True
        for v in range(26):
            allow[a, v] = allow[a, v] and row[v]
    # bipartite matching letters -> values (Kuhn)
    match_v = np.full(26, -1, dtype=np.int64)
    for a in range(26):
        if not used[a]:
            continue
        # iterative DFS augment
        seen = np.zeros(26, dtype=np.bool_)
        stack_a = np.zeros(27, dtype=np.int64)
        stack_v = np.zeros(27, dtype=np.int64)
        parent_v = np.full(26, -1, dtype=np.int64)
        # BFS over alternating paths
        queue = np.zeros(26 * 26, dtype=np.int64)
        qh = 0; qt = 0
        queue[qt] = a; qt += 1
        found = -1
        prev_a_of_v = np.full(26, -1, dtype=np.int64)
        while qh < qt and found < 0:
            u = queue[qh]; qh += 1
            for v in range(26):
                if allow[u, v] and not seen[v]:
                    seen[v] = True
                    prev_a_of_v[v] = u
                    if match_v[v] == -1:
                        found = v
                        break
                    queue[qt] = match_v[v]; qt += 1
        if found < 0:
            return False
        # augment
        v = found
        while v != -1:
            u = prev_a_of_v[v]
            # find v' currently matched to u
            pv = -1
            for vv in range(26):
                if match_v[vv] == u:
                    pv = vv
                    break
            match_v[v] = u
            v = pv
    return True


@njit(parallel=True, cache=True)
def scan(cti, KW, LENS, KAI, KAL, counts, hits, nh):
    # counts[t] per test type: 0 exact, 1 exact-1slip, 2 nuance w1 AZ, 3 w1 KA, 4 w2 AZ, 5 w2 KA
    W = KW.shape[0]
    loc = np.zeros((W, 6), dtype=np.int64)
    for q in prange(W):
        L = LENS[q]
        res = np.zeros((NC, 2), dtype=np.int64)
        for f in range(L):
            for tab in range(2):
                for rule in range(3):
                    for order in range(2):
                        residual(cti, KW[q], L, f, tab, rule, order, KAI, KAL, res)
                        code = -1
                        if exact_viol(res, -1) == 0:
                            loc[q, 0] += 1; code = 0
                        else:
                            for d in range(NC):
                                if exact_viol(res, d) == 0:
                                    loc[q, 1] += 1; code = 1
                                    break
                        for w in (1, 2):
                            for numb in range(2):
                                if nuance_ok(res, w, numb, KAI):
                                    loc[q, 2 + (w - 1) * 2 + numb] += 1
                                    if code < 0 and w == 1:
                                        code = 2 + numb
                        if code >= 0:
                            k = nh[0]
                            if k < hits.shape[0]:
                                hits[k, 0] = q; hits[k, 1] = f; hits[k, 2] = tab
                                hits[k, 3] = rule; hits[k, 4] = order; hits[k, 5] = code
                            nh[0] = k + 1
    for q in range(W):
        for t in range(6):
            counts[t] += loc[q, t]


def run(cti, KW, LENS):
    counts = np.zeros(6, dtype=np.int64)
    hits = np.zeros((20000, 6), dtype=np.int64)
    nh = np.zeros(1, dtype=np.int64)
    scan(cti, KW, LENS, KAI, KAL, counts, hits, nh)
    return counts, hits[:min(nh[0], 20000)]


def encrypt_planted(rng, kw, tab, rule, order, w):
    pt = rng.integers(0, 26, 97)
    for i, ch in CRIB_POS.items():
        pt[i] = ord(ch) - 65
    s = rng.permutation(26)
    A = KA if tab else AZ
    ia = lambda x: A.index(AZ[x])
    la = lambda v: AZ.index(A[v % 26])
    ct = np.zeros(97, dtype=np.int64)
    for i in range(97):
        k = ord(kw[i % len(kw)]) - 65
        nu = int(rng.integers(-w, w + 1))
        if order == 0:
            y = (s[pt[i]] + nu) % 26
            xi, ki = ia(y), ia(k)
            c = [xi + ki, ki - xi, xi - ki][rule]
            ct[i] = la(c)
        else:
            xi, ki = ia(pt[i]), ia(k)
            z = la([xi + ki, ki - xi, xi - ki][rule])
            ct[i] = (s[z] + nu) % 26
    return ct


if __name__ == "__main__":
    nnull = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    ks, KW, LENS = keywords()
    nstreams = int(LENS.sum())
    print(f"keywords {len(ks)}, keystreams (word x phase) {nstreams}, tests x12 = {nstreams * 12}", flush=True)
    rng = np.random.default_rng(20261018)
    # planted: pick lore words, plant, scan only that word
    for kw, tab, rule, order, w in (("SHADOW", 1, 0, 0, 0), ("PALIMPSEST", 1, 0, 1, 0), ("ABSCISSA", 0, 1, 0, 1),
                                    ("LAYERTWO", 1, 2, 1, 1), ("BERLINWALL", 1, 0, 0, 2)):
        ct = encrypt_planted(rng, kw, tab, rule, order, w)
        q = ks.index(kw)
        c, h = run(ct, KW[q:q + 1], LENS[q:q + 1])
        print(f"planted {kw} tab={'KA' if tab else 'AZ'} rule={rule} order={order} nuance={w}: counts {c.tolist()}", flush=True)
    cti = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
    t = time.time()
    c, h = run(cti, KW, LENS)
    print("scan time", round(time.time() - t, 1), flush=True)
    names = ["exact", "exact<=1slip", "nuance1 AZ", "nuance1 KA", "nuance2 AZ", "nuance2 KA"]
    print("REAL ", dict(zip(names, c.tolist())), flush=True)
    for row in h[:40]:
        q, f, tab, rule, order, code = row
        print(f"  hit {ks[q]} phase {f} {'KA' if tab else 'AZ'} {['vig','beau','var'][rule]} "
              f"{'mask>table' if order == 0 else 'table>mask'} {names[code]}", flush=True)
    nulls = []
    for s in range(nnull):
        c2, _ = run(rng.permutation(cti), KW, LENS)
        nulls.append(c2)
        print(f"NULL{s}", dict(zip(names, c2.tolist())), flush=True)
    ns = np.array(nulls)
    print("NULL mean", dict(zip(names, ns.mean(0).round(1).tolist())))
    print("NULL max ", dict(zip(names, ns.max(0).tolist())))
