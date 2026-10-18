"""Crib-consistency filter for transposition + periodic substitution composites.

Variants: substitution type (vig/beau/varbeau) x (plain alphabet, cipher alphabet) in {AZ,KA}^2.
Orders:
  A ("T then S"): X = transpose(P); C[j] = S(X[j], k[j % p])  -> crib at PT pos i lands at j=inv[i], residue j%p
  B ("S then T", K3 style): Y[i] = S(P[i], k[i % p]); C = transpose(Y) -> residue i%p, cipher letter C[inv[i]]
Here perm convention out[j] = in[perm[j]], so for encryption transpose, the PT index at CT slot j is perm[j]
and PT index i sits at CT slot inv[i].
"""
import numpy as np
from numba import njit
from k4lib import CT, CRIB_POS, AZ, KA, to_idx

VARIANTS = []
for sname in ("vig", "beau", "varbeau"):
    for pa_name, pa in (("AZ", AZ), ("KA", KA)):
        for ca_name, ca in (("AZ", AZ), ("KA", KA)):
            VARIANTS.append((sname, pa_name, ca_name, pa, ca))
NV = len(VARIANTS)

# KV[v, p_letter, c_letter] -> key index
KV = np.zeros((NV, 26, 26), dtype=np.int64)
for v, (s, _, _, pa, ca) in enumerate(VARIANTS):
    for P in range(26):
        for C in range(26):
            ip = pa.index(AZ[P])
            ic = ca.index(AZ[C])
            if s == "vig":
                k = (ic - ip) % 26
            elif s == "beau":
                k = (ic + ip) % 26
            else:
                k = (ip - ic) % 26
            KV[v, P, C] = k

CTI = to_idx(CT)
CRIB_I = np.array(sorted(CRIB_POS), dtype=np.int64)
CRIB_L = np.array([AZ.index(CRIB_POS[i]) for i in CRIB_I], dtype=np.int64)


def decrypt_letter(v, key_idx, c_letter):
    """Inverse of KV for full decryption: given key index and cipher letter (AZ idx), return PT AZ idx."""
    s, _, _, pa, ca = VARIANTS[v]
    ic = ca.index(AZ[c_letter])
    if s == "vig":
        ip = (ic - key_idx) % 26
    elif s == "beau":
        ip = (key_idx - ic) % 26
    else:
        ip = (key_idx + ic) % 26
    return AZ.index(pa[ip])


@njit(cache=True)
def check_batch(invs, pmin, pmax, KV, CTI, CRIB_I, CRIB_L, min_m, out):
    """For each inverse perm, period, order, variant: test consistency. Write survivors to out.
    out rows: perm_idx, p, order, v, m. Returns count."""
    nperm = invs.shape[0]
    nv = KV.shape[0]
    nc = CRIB_I.shape[0]
    cnt = 0
    key = np.empty(128, dtype=np.int64)
    for q in range(nperm):
        inv = invs[q]
        for p in range(pmin, pmax + 1):
            for order in range(2):
                for v in range(nv):
                    for r in range(p):
                        key[r] = -1
                    ok = True
                    distinct = 0
                    for t in range(nc):
                        i = CRIB_I[t]
                        j = inv[i]
                        r = (j % p) if order == 0 else (i % p)
                        k = KV[v, CRIB_L[t], CTI[j]]
                        if key[r] == -1:
                            key[r] = k
                            distinct += 1
                        elif key[r] != k:
                            ok = False
                            break
                    if ok:
                        m = nc - distinct
                        if m >= min_m and cnt < out.shape[0]:
                            out[cnt, 0] = q
                            out[cnt, 1] = p
                            out[cnt, 2] = order
                            out[cnt, 3] = v
                            out[cnt, 4] = m
                            cnt += 1
    return cnt


def full_decrypt(inv, perm, p, order, v, key):
    """key: list length p of key indices (or -1 unknown -> '?')."""
    pt = ["?"] * 97
    for i in range(97):
        j = inv[i]
        r = (j % p) if order == 0 else (i % p)
        if key[r] < 0:
            continue
        pt[i] = AZ[decrypt_letter(v, key[r], CTI[j])]
    return "".join(pt)


def crib_key(inv, p, order, v):
    key = [-1] * p
    for t in range(len(CRIB_I)):
        i = int(CRIB_I[t]); j = int(inv[i])
        r = (j % p) if order == 0 else (i % p)
        key[r] = int(KV[v, CRIB_L[t], CTI[j]])
    return key


def complete_key(inv, perm, p, order, v, sweeps=3):
    """Fill unpinned residues greedily by qscore."""
    from k4lib import qscore
    key = crib_key(inv, p, order, v)
    free = [r for r in range(p) if key[r] < 0]
    for r in free:
        key[r] = 0
    best = qscore(full_decrypt(inv, perm, p, order, v, key))
    for _ in range(sweeps):
        improved = False
        for r in free:
            for k in range(26):
                old = key[r]
                key[r] = k
                s = qscore(full_decrypt(inv, perm, p, order, v, key))
                if s > best:
                    best = s; improved = True
                else:
                    key[r] = old
        if not improved:
            break
    return key, best


@njit(cache=True)
def check_prog(invs, pmin, pmax, dmax, KV, CTI, CRIB_I, CRIB_L, min_m, out):
    """Progressive periodic key: k(x) = K[x % p] + d * (x // p), x = key index position.
    d=0 reduces to check_batch. out rows: perm_idx, p, order, v, m, d."""
    nperm = invs.shape[0]
    nv = KV.shape[0]
    nc = CRIB_I.shape[0]
    cnt = 0
    key = np.empty(128, dtype=np.int64)
    for q in range(nperm):
        inv = invs[q]
        for p in range(pmin, pmax + 1):
            for order in range(2):
                for v in range(nv):
                    for d in range(dmax + 1):
                        for r in range(p):
                            key[r] = -1
                        ok = True
                        distinct = 0
                        for t in range(nc):
                            i = CRIB_I[t]
                            j = inv[i]
                            x = j if order == 0 else i
                            r = x % p
                            k = (KV[v, CRIB_L[t], CTI[j]] - d * (x // p)) % 26
                            if key[r] == -1:
                                key[r] = k
                                distinct += 1
                            elif key[r] != k:
                                ok = False
                                break
                        if ok:
                            m = nc - distinct
                            if m >= min_m and cnt < out.shape[0]:
                                out[cnt, 0] = q
                                out[cnt, 1] = p
                                out[cnt, 2] = order
                                out[cnt, 3] = v
                                out[cnt, 4] = m
                                out[cnt, 5] = d
                                cnt += 1
    return cnt


@njit(cache=True)
def check_tolerant(invs, pmin, pmax, KV, CTI, CRIB_I, CRIB_L, max_err, min_eff, out):
    """Allow up to max_err crib letters to disagree. err = sum over residues (count - mode count).
    Survivor if err <= max_err and effective constraints (m - err) >= min_eff.
    out rows: perm_idx, p, order, v, m, err."""
    nperm = invs.shape[0]; nv = KV.shape[0]; nc = CRIB_I.shape[0]
    cnt = 0
    tab = np.zeros((64, 26), dtype=np.int64)
    rcount = np.zeros(64, dtype=np.int64)
    for q in range(nperm):
        inv = invs[q]
        for p in range(pmin, pmax + 1):
            for order in range(2):
                for v in range(nv):
                    for r in range(p):
                        rcount[r] = 0
                        for x in range(26):
                            tab[r, x] = 0
                    for t in range(nc):
                        i = CRIB_I[t]; j = inv[i]
                        r = (j % p) if order == 0 else (i % p)
                        tab[r, KV[v, CRIB_L[t], CTI[j]]] += 1
                        rcount[r] += 1
                    err = 0; distinct = 0
                    for r in range(p):
                        if rcount[r] > 0:
                            distinct += 1
                            mx = 0
                            for x in range(26):
                                if tab[r, x] > mx:
                                    mx = tab[r, x]
                            err += rcount[r] - mx
                    m = nc - distinct
                    if err <= max_err and m - err >= min_eff and cnt < out.shape[0]:
                        out[cnt, 0] = q; out[cnt, 1] = p; out[cnt, 2] = order
                        out[cnt, 3] = v; out[cnt, 4] = m; out[cnt, 5] = err
                        cnt += 1
    return cnt
