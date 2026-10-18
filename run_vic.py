"""VIC-style keys: keyword -> digits (alphabetical rank mod 10, A=1, A=0) -> chain addition to 97 digits
(lagged-Fibonacci d[i]=d[i-L]+d[i-L+1] or d[i-L]+d[i-1], base 10 or 26), +/- sign.
Test: single unknown mixed alphabet (run_gromark.consistent mode 1) — strong (random pass ~0)."""
import numpy as np, time
from numba import njit, prange
import run_gromark as g
from run_alphapairs import load_words


def ranks(w):
    order = sorted(range(len(w)), key=lambda i: (w[i], i))
    r = [0] * len(w)
    for k, i in enumerate(order):
        r[i] = (k + 1) % 10
    return r


@njit(cache=True)
def expand(seed, L, b, mode):
    d = np.empty(97, dtype=np.int64)
    for i in range(min(L, 97)):
        d[i] = seed[i] % b
    for i in range(L, 97):
        d[i] = (d[i - L] + d[i - L + 1]) % b if mode == 0 else (d[i - L] + d[i - 1]) % b
    return d


@njit(parallel=True, cache=True)
def run(seeds, lens, PL, CL, CI, flags):
    for w in prange(seeds.shape[0]):
        L = lens[w]
        for b in (10, 26):
            for mode in range(2):
                for sign in range(2):
                    d = expand(seeds[w], L, b, mode)
                    if sign == 1:
                        for i in range(97):
                            d[i] = (26 - d[i]) % 26
                    if g.consistent(d, 1, PL, CL, CI):
                        flags[w] += 1


if __name__ == "__main__":
    lore, words = load_words()
    words = sorted(set(w for w in words + lore if 3 <= len(w) <= 20))
    for label, fn in (("rank", ranks), ("A1", lambda w: [ord(c) - 64 for c in w]), ("A0", lambda w: [ord(c) - 65 for c in w])):
        S = np.zeros((len(words), 20), dtype=np.int64); Ls = np.zeros(len(words), dtype=np.int64)
        for i, w in enumerate(words):
            s = fn(w); S[i, :len(s)] = s; Ls[i] = len(s)
        flags = np.zeros(len(words), dtype=np.int64); t = time.time()
        run(S, Ls, g.PL, g.CL, g.CI, flags)
        hits = np.nonzero(flags)[0]
        print(label, "words", len(words), "hits", len(hits), round(time.time() - t, 1), "s", [words[h] for h in hits[:20]])
    rng = np.random.default_rng(0)
    S = rng.integers(0, 10, (200000, 20)); Ls = rng.integers(3, 21, 200000)
    flags = np.zeros(200000, dtype=np.int64); run(S, Ls, g.PL, g.CL, g.CI, flags)
    print("null random seeds 200k hits", int((flags > 0).sum()))
