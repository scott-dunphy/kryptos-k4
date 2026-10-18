"""Ragbaby (26-letter variant; ACA's 24-letter J/X-less form is impossible since K4 CT has J and X).

Shift for letter j (0-based) of word w = n_w + j (word numbers consecutive). Encryption C = A[(pos(P) + s) mod 26]
with a single keyed alphabet A (unknown). Also tested: s = n_w - j, s = -(n_w + j) (Beaufort-like sign), and
word-only shift s = n_w (interrupted).
Crib segmentations into words; unknown word numbers n1 (for first crib run) and n2 (second run) brute-forced (26^2);
test with run_gromark.consistent(mode=1) = single unknown mixed alphabet (covers every keyword alphabet, AZ, KA).
"""
import itertools
import numpy as np
import run_gromark as g

SEG1 = {"EAST|NORTHEAST": [4, 9], "EASTNORTHEAST": [13], "EAST|NORTH|EAST": [4, 5, 4]}
SEG2 = {"BERLIN|CLOCK": [6, 5], "BERLINCLOCK": [11]}
START1, START2 = 21, 63


def rel_shifts(seg, mode):
    out = []
    for w, L in enumerate(seg):
        for j in range(L):
            if mode == "n+j":
                out.append((w, j))
            elif mode == "n-j":
                out.append((w, -j))
            elif mode == "n":
                out.append((w, 0))
    return out  # (word offset, letter term)


def run(PL, CL, CI):
    hits = []
    for (s1n, s1), (s2n, s2) in itertools.product(SEG1.items(), SEG2.items()):
        for mode in ("n+j", "n-j", "n"):
            r1 = rel_shifts(s1, mode); r2 = rel_shifts(s2, mode)
            for sign in (1, -1):
                for n1 in range(26):
                    for n2 in range(26):
                        d = np.zeros(97, dtype=np.int64)
                        for k, (w, j) in enumerate(r1):
                            d[START1 + k] = (sign * (n1 + w + j)) % 26
                        for k, (w, j) in enumerate(r2):
                            d[START2 + k] = (sign * (n2 + w + j)) % 26
                        if g.consistent(d, 1, PL, CL, CI):
                            hits.append((s1n, s2n, mode, sign, n1, n2))
    return hits


if __name__ == "__main__":
    from k4lib import keyed_alphabet
    # validation: plant Ragbaby with keyed alphabet
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    A = keyed_alphabet("SHADOW")
    # words for synthetic: treat cribs per segmentation EAST|NORTHEAST, BERLIN|CLOCK with n1=7, n2=15
    ct = list(PT)
    for k, (w, j) in enumerate(rel_shifts([4, 9], "n+j")):
        i = START1 + k; ct[i] = A[(A.index(PT[i]) + 7 + w + j) % 26]
    for k, (w, j) in enumerate(rel_shifts([6, 5], "n+j")):
        i = START2 + k; ct[i] = A[(A.index(PT[i]) + 15 + w + j) % 26]
    CLs = np.array([ord(ct[i]) - 65 for i in g.CI])
    hs = run(g.PL, CLs, g.CI)
    print("validation hits", len(hs), "truth found", any(h[:6] == ("EAST|NORTHEAST", "BERLIN|CLOCK", "n+j", 1, 7, 15) for h in hs))
    real = run(g.PL, g.CL, g.CI)
    print("REAL hits", len(real), real[:10])
    rng = np.random.default_rng(0)
    nh = []
    for _ in range(20):
        nh.append(len(run(g.PL, rng.integers(0, 26, 24), g.CI)))
    print("null random CT at cribs (20 runs) hits:", nh)
