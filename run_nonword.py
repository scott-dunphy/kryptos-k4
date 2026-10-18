"""Non-keyword key rows: small-number streams derived from texts.
Derivations per letter of a source text: Morse element count (1-4), Morse dots, Morse dashes, dots-dashes,
phone keypad digit (2-9), 5x5 Polybius row / column (I=J), letter index mod 5 / mod 10, vowel(1)/consonant(0).
Models: (a) single unknown mixed alphabet cpos(C)=ppos(P)+k (run_gromark.consistent mode 1, both signs, k and k*s);
        (b) half-free: sigma(P) = pos_X(C) - k  (free PT substitution, CT alphabet AZ or KA) and mirror (run_fable2).
Sources: K0 Morse text, K1-K3 PT, all corpora in data/ (Carter, KJV, speeches, Egyptian, crypto manuals...), fwd/rev.
"""
import glob, re
import numpy as np
from numba import njit, prange
import run_gromark as g
import cribfilter as cf
from run_fable2 import halffree_scan, IDXT
import kryptos_texts as kt

MORSE = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....", "I": "..",
         "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
         "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--.."}
PHONE = {}
for d, ls in (("2", "ABC"), ("3", "DEF"), ("4", "GHI"), ("5", "JKL"), ("6", "MNO"), ("7", "PRS"), ("8", "TUV"), ("9", "WXY"), ("0", "QZ")):
    for c in ls:
        PHONE[c] = int(d)
POLY = "ABCDEFGHIKLMNOPQRSTUVWXYZ"


def derivations():
    D = {}
    D["morse_len"] = {c: len(m) for c, m in MORSE.items()}
    D["morse_dots"] = {c: m.count(".") for c, m in MORSE.items()}
    D["morse_dashes"] = {c: m.count("-") for c, m in MORSE.items()}
    D["morse_dotminusdash"] = {c: m.count(".") - m.count("-") for c, m in MORSE.items()}
    D["phone"] = PHONE
    D["poly_row"] = {c: POLY.index("I" if c == "J" else c) // 5 for c in MORSE}
    D["poly_col"] = {c: POLY.index("I" if c == "J" else c) % 5 for c in MORSE}
    D["mod5"] = {c: (ord(c) - 65) % 5 for c in MORSE}
    D["mod10"] = {c: (ord(c) - 65) % 10 for c in MORSE}
    D["vowel"] = {c: int(c in "AEIOU") for c in MORSE}
    return D


@njit(parallel=True, cache=True)
def single_scan(S, PL, CL, CI, mult, flags):
    n = S.shape[0] - 97
    for o in prange(max(n, 0)):
        d = np.empty(97, dtype=np.int64)
        for sign in range(2):
            for i in range(97):
                v = (S[o + i] * mult) % 26
                d[i] = v if sign == 0 else (26 - v) % 26
            if g.consistent(d, 1, PL, CL, CI):
                flags[o] += 1


def sources():
    T = {"K0": kt.MORSE, "K1PT": kt.K1_PT, "K2PT": kt.K2_PT, "K3PT": kt.K3_PT, "K123": kt.K1_PT + kt.K2_PT + kt.K3_PT}
    for f in glob.glob("data/*.txt") + glob.glob("data/texts2/*.txt") + glob.glob("data/memtexts/*.txt") + ["data/carter/carter_vol1_letters.txt"]:
        if "quadgram" in f or "sculpture" in f:
            continue
        T[f.split("/")[-1]] = re.sub("[^A-Z]", "", open(f, errors="ignore").read().upper())
    return T


def run(ctl_cri, label):
    D = derivations(); T = sources()
    tot_a = tot_b = 0
    for tn, txt in T.items():
        if len(txt) < 120:
            txt = txt * (120 // len(txt) + 2)
        for dn, mp in D.items():
            for st in (txt, txt[::-1]):
                S = np.array([mp[c] for c in st], dtype=np.int64)
                for mult in (1, 2, 3):
                    fl = np.zeros(max(len(S) - 97, 1), dtype=np.int64)
                    single_scan(S, g.PL, ctl_cri, g.CI, mult, fl)
                    h = int((fl > 0).sum()); tot_a += h
                    if h:
                        print(f"  {label} (a) hit {tn} {dn} x{mult}: {h}")
                S26 = (S % 26).astype(np.int64)
                fl = np.zeros(max(len(S) - 97, 1), dtype=np.int64)
                halffree_scan(S26, cf.CRIB_I, cf.CRIB_L, ctl_cri, IDXT, fl)
                h = int((fl > 0).sum()); tot_b += h
                if h:
                    print(f"  {label} (b) hit {tn} {dn}: {h}")
    print(f"{label}: (a) single-unknown-alphabet hits {tot_a}; (b) half-free hits {tot_b}", flush=True)


if __name__ == "__main__":
    # validation: plant key = Morse length of K0 text from offset 7 under a random single alphabet
    rng = np.random.default_rng(2); A = rng.permutation(26); Ap = np.argsort(A)
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    src = kt.MORSE * 3
    k = [len(MORSE[c]) for c in src[7:7 + 97]]
    syn = np.array([A[(Ap[ord(p) - 65] + k[i]) % 26] for i, p in enumerate(PT)])
    S = np.array([len(MORSE[c]) for c in src], dtype=np.int64)
    fl = np.zeros(len(S) - 97, dtype=np.int64)
    single_scan(S, g.PL, syn[cf.CRIB_I], g.CI, 1, fl)
    print("validation planted Morse-length key found at offset 7:", bool(fl[7]), "total", int((fl > 0).sum()))
    run(cf.CTI[cf.CRIB_I], "REAL")
    run(rng.permutation(cf.CTI)[cf.CRIB_I], "NULL")
