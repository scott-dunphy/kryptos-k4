"""Linear key-model consistency test over Z26 (direct, no transposition).
Key model: k_i = F[i,:] . x  (x unknown), with k_i = crib key under (PT alphabet X, CT alphabet Y, rule).
Consistency iff for every left-null vector w of F (mod 2 and mod 13): w.k == 0.
"""
import sys
import numpy as np
sys.path.insert(0, '.')
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
CL = np.array([ord(CT[i]) - 65 for i in CI], dtype=np.int64)


def left_null(F, m):
    """Basis of {w : w F = 0 mod m}, m prime. F: (n,u)."""
    A = (F.T % m).astype(np.int64)  # (u,n): solve A w = 0
    u, n = A.shape
    A = A.copy(); piv = []; r = 0
    for c in range(n):
        pr = None
        for i in range(r, u):
            if A[i, c] % m:
                pr = i; break
        if pr is None:
            continue
        A[[r, pr]] = A[[pr, r]]
        inv = pow(int(A[r, c]), -1, m)
        A[r] = A[r] * inv % m
        for i in range(u):
            if i != r and A[i, c]:
                A[i] = (A[i] - A[i, c] * A[r]) % m
        piv.append(c); r += 1
        if r == u:
            break
    free = [c for c in range(n) if c not in piv]
    basis = []
    for f in free:
        w = np.zeros(n, dtype=np.int64); w[f] = 1
        for i, c in enumerate(piv):
            w[c] = (-A[i, f]) % m
        basis.append(w)
    return np.array(basis, dtype=np.int64).reshape(len(basis), n)


def model_checks(F):
    W2 = left_null(F, 2); W13 = left_null(F, 13)
    return W2, W13


def consistent(k, W2, W13):
    return (not len(W2) or not np.any(W2 @ k % 2)) and (not len(W13) or not np.any(W13 @ k % 13))


def pos_table(alpha):
    t = np.empty(26, dtype=np.int64)
    for i, c in enumerate(alpha):
        t[ord(c) - 65] = i
    return t


def keys_for(ptab, ctab):
    ip = ptab[PL]; ic = ctab[CL]
    return [(ic - ip) % 26, (ic + ip) % 26, (ip - ic) % 26]


LORE = ("KRYPTOS PALIMPSEST ABSCISSA IQLUSION UNDERGRUUND BERLIN CLOCK BERLINCLOCK WELTZEITUHR "
        "MENGENLEHREUHR ALEXANDERPLATZ SANBORN SCHEIDT WEBSTER LANGLEY SHADOW CARTER TUTANKHAMUN "
        "EGYPT CAIRO WORLDCLOCK URANIA LAYERTWO VIRGINIA COMPASS LODESTONE EASTNORTHEAST "
        "ANTIPODES HIRSHHORN NORTHEAST EAST TIME ZEIT UHR HOUR LUCID MEMORY INVISIBLE SECRET TOMB "
        "DESPARATLY DIGETAL POINT ILLUSION FIVE SEVEN NORTH WEST QUAGMIRE VIGENERE MASK MASKING").split()


def base_alphabets():
    res, seen = [], set()
    for w in [""] + LORE:
        for rev in (0, 1):
            al = keyed_alphabet(w)
            if rev:
                al = al[::-1]
            if al not in seen:
                seen.add(al); res.append(((w or "AZ") + ("~rev" if rev else ""), al))
    return res
