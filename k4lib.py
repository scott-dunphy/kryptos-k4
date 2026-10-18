"""Core K4 utilities: ciphertext, cribs, alphabets, quadgram scoring."""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

CT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
N = len(CT)
assert N == 97

CRIBS = {21: "EASTNORTHEAST", 63: "BERLINCLOCK"}
CRIB_POS = {}
for s, w in CRIBS.items():
    for i, ch in enumerate(w):
        CRIB_POS[s + i] = ch

AZ = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"


def keyed_alphabet(key, base=AZ):
    seen = []
    for c in key + base:
        if c not in seen:
            seen.append(c)
    return "".join(seen)


def to_idx(s, alpha=AZ):
    return np.array([alpha.index(c) for c in s], dtype=np.int64)


def from_idx(a, alpha=AZ):
    return "".join(alpha[int(i)] for i in a)


_QG = None
_FLOOR = None


def load_quadgrams():
    global _QG, _FLOOR
    if _QG is not None:
        return _QG
    tbl = np.zeros(26 ** 4, dtype=np.float64)
    total = 0
    path = os.path.join(HERE, "data", "quadgrams.txt")
    with open(path) as f:
        for line in f:
            q, c = line.split()
            c = int(c)
            total += c
            a = [ord(x) - 65 for x in q]
            tbl[((a[0] * 26 + a[1]) * 26 + a[2]) * 26 + a[3]] = c
    _FLOOR = np.log10(0.01 / total)
    with np.errstate(divide="ignore"):
        lt = np.log10(tbl / total)
    lt[tbl == 0] = _FLOOR
    _QG = lt.astype(np.float32)
    return _QG


def qscore(text):
    """Mean log10 quadgram probability per quadgram (English ~ -4.3 .. -4.6, random ~ -6.5+)."""
    qg = load_quadgrams()
    a = to_idx(text)
    if len(a) < 4:
        return -10.0
    idx = ((a[:-3] * 26 + a[1:-2]) * 26 + a[2:-1]) * 26 + a[3:]
    return float(qg[idx].mean())


def ioc(text):
    from collections import Counter
    c = Counter(text)
    n = len(text)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def vig_dec(c, k, alpha=AZ):
    return alpha[(alpha.index(c) - alpha.index(k)) % 26]


def beau_dec(c, k, alpha=AZ):
    return alpha[(alpha.index(k) - alpha.index(c)) % 26]


def varbeau_dec(c, k, alpha=AZ):
    return alpha[(alpha.index(c) + alpha.index(k)) % 26]


def crib_hits(pt):
    return sum(1 for i, ch in CRIB_POS.items() if i < len(pt) and pt[i] == ch)
