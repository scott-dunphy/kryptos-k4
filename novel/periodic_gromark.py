"""ACA Periodic Gromark, keyword-determined, direct. Validated on ACA ENIGMA example.
C = CTA[(off_g + P + s*d_i) mod 26], off_g = pos in CTA of header[g % n], g = i // n.
Counts crib matches per keyword/variant; null = same words vs shuffled CT."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from k4lib import CT, CRIB_POS, AZ
from run_alphapairs import load_words

def build(w):
    hdr = "".join(dict.fromkeys(w))
    n = len(hdr)
    keyed = "".join(dict.fromkeys(hdr + AZ))
    order = sorted(range(n), key=lambda j: hdr[j])
    cta = "".join(keyed[j::n] for j in order)
    rank = [0] * n
    for k, j in enumerate(order):
        rank[j] = (k + 1) % 10
    return hdr, n, cta, rank

def digits(rank, n, N=97):
    d = list(rank)
    while len(d) < N:
        i = len(d)
        d.append((d[i - n] + d[i - n + 1]) % 10)
    return d[:N]

def enc(pt, w):
    hdr, n, cta, rank = build(w); d = digits(rank, n, len(pt))
    return "".join(cta[(cta.index(hdr[(i // n) % n]) + AZ.index(c) + d[i]) % 26] for i, c in enumerate(pt))

assert enc("WINTRYSHOWERSWILLCONTINUEFORTHENEXTFEWDAYSACCORDINGTOTHEFORECAST", "ENIGMA") == \
    "RHNAAXNRUZBNIUARXCRTPATBRLIGDSVCIRCVOYPVRAAZZMUSREQYEVMMURGWTLUD", "validation failed"

POS = sorted(CRIB_POS)
def score(w, ct):
    hdr, n, cta, rank = build(w)
    if n < 2: return 0
    d = digits(rank, n)
    pa = {c: i for i, c in enumerate(cta)}
    best = 0
    for so in (1, -1):        # offset sign
        for sd in (1, -1):    # digit sign
            for pm in (0, 1): # PT index in AZ (0) or in CTA (1, single-alphabet variant)
                m = 0
                for i in POS:
                    p = AZ.index(CRIB_POS[i]) if pm == 0 else pa[CRIB_POS[i]]
                    off = pa[hdr[(i // n) % n]]
                    if cta[(so * off + p + sd * d[i]) % 26] == ct[i]: m += 1
                best = max(best, m)
    return best

if __name__ == "__main__":
    lore, words = load_words()
    words = sorted(set(w for w in words + lore if 3 <= len(w) <= 26))
    rng = np.random.default_rng(1)
    sh = list(CT); rng.shuffle(sh); sh = "".join(sh)
    from collections import Counter
    real, null = Counter(), Counter(); top = []
    for w in words:
        s = score(w, CT); real[s] += 1
        if s >= 7: top.append((s, w))
        null[score(w, sh)] += 1
    print("words", len(words)); print("real hist", sorted(real.items())); print("null hist", sorted(null.items()))
    print("top", sorted(top, reverse=True)[:20])
