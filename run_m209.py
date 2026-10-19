"""Hagelin M-209 test for K4 (2026-10-18).

Machine: six pinwheels (26,25,23,21,19,17), each steps once per letter; pin of wheel w at message position i is
b_w[i mod L_w] (start positions absorbed into the pin labels). 27 bars; a bar's lugs face 0, 1 or 2 wheels, so the
lug cage reduces to counts n_S for S = {}, {w}, {w1,w2} (22 types, sum 27). Key k_i = sum of n_S over types with an
active pin under any lug. Beaufort on plain AZ: C = 25 - P + k (+ c, c free to absorb the letter convention).
The two cribs share many pins (gaps 34, 38, 42, 46, 50, 51, 52 = multiples of 17, 19, 21, 23, 25, 17, 26), so a
crib-fitting machine forces most other plaintext letters.
Search: simulated annealing over pins + lug counts + c, score = quadgram log-prob of the full decrypt + crib penalty.
Controls: planted M-209 encryption of English with the same cribs; fair nulls = K4 with the 73 non-crib CT letters
shuffled (crib CT kept, so crib fitting is equally easy). Success needs real >> null and restart agreement.
"""
import sys
import numpy as np
from numba import njit
from k4lib import CT, CRIB_POS, load_quadgrams

LW = np.array([26, 25, 23, 21, 19, 17], dtype=np.int64)
TYPES = [()] + [(w,) for w in range(6)] + [(a, b) for a in range(6) for b in range(a + 1, 6)]
TW = np.full((22, 2), -1, dtype=np.int64)
for t, s in enumerate(TYPES):
    for j, w in enumerate(s):
        TW[t, j] = w
QG = load_quadgrams().astype(np.float64)
CRIB = np.full(97, -1, dtype=np.int64)
for i, ch in CRIB_POS.items():
    CRIB[i] = ord(ch) - 65
ITERS1 = 200000


@njit(cache=True)
def decrypt(cti, pins, n, c, out):
    for i in range(97):
        k = 0
        for t in range(1, 22):
            if n[t] == 0:
                continue
            a = TW[t, 0]; b = TW[t, 1]
            if pins[a, i % LW[a]] == 1 or (b >= 0 and pins[b, i % LW[b]] == 1):
                k += n[t]
        out[i] = (25 - cti[i] + k + c) % 26


@njit(cache=True)
def score(p, crib, qg, lam):
    s = 0.0
    for i in range(94):
        s += qg[((p[i] * 26 + p[i + 1]) * 26 + p[i + 2]) * 26 + p[i + 3]]
    bad = 0
    for i in range(97):
        if crib[i] >= 0 and p[i] != crib[i]:
            bad += 1
    return s * (lam < 1e5) - lam * bad, bad


@njit(cache=True)
def anneal(cti, crib, qg, iters, seed, iters1):
    np.random.seed(seed)
    pins = np.zeros((6, 26), dtype=np.int64)
    for w in range(6):
        for r in range(LW[w]):
            pins[w, r] = np.random.randint(0, 2)
    n = np.zeros(22, dtype=np.int64)
    for _ in range(27):
        n[np.random.randint(0, 22)] += 1
    c = np.random.randint(0, 26)
    p = np.zeros(97, dtype=np.int64)
    decrypt(cti, pins, n, c, p)
    lam = 1e6
    cur, bad = score(p, crib, qg, lam)
    best = cur; bpins = pins.copy(); bn = n.copy(); bc = c
    for it in range(iters1 + iters):
        if it < iters1:
            T = 1e6 * 0.6 * (0.05 / 0.6) ** (it / iters1)
        else:
            if it == iters1:
                if bad > 0:
                    break
                lam = 50.0
                decrypt(cti, pins, n, c, p)
                cur, bad = score(p, crib, qg, lam)
                best = cur; bpins[:, :] = pins; bn[:] = n; bc = c
            T = 3.0 * (0.02 / 3.0) ** ((it - iters1) / iters)
        r = np.random.random()
        if r < 0.7:
            w = np.random.randint(0, 6); q = np.random.randint(0, LW[w])
            pins[w, q] ^= 1
            mv = 0
        elif r < 0.97:
            a = np.random.randint(0, 22)
            while n[a] == 0:
                a = np.random.randint(0, 22)
            b = np.random.randint(0, 22)
            n[a] -= 1; n[b] += 1
            mv = 1
        else:
            oc = c; c = np.random.randint(0, 26)
            mv = 2
        decrypt(cti, pins, n, c, p)
        new, nb = score(p, crib, qg, lam)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new; bad = nb
            if cur > best:
                best = cur; bpins[:, :] = pins; bn[:] = n; bc = c
        else:
            if mv == 0:
                pins[w, q] ^= 1
            elif mv == 1:
                n[a] += 1; n[b] -= 1
            else:
                c = oc
    decrypt(cti, bpins, bn, bc, p)
    s, nb = score(p, crib, qg, 50.0)
    return s, nb, p.copy()


def m209_encrypt(pt, rng):
    pins = rng.integers(0, 2, (6, 26))
    n = np.zeros(22, dtype=np.int64)
    for _ in range(27):
        n[rng.integers(0, 22)] += 1
    ct = []
    for i, x in enumerate(pt):
        k = sum(n[t] for t in range(1, 22) if any(pins[w, i % LW[w]] for w in TYPES[t]))
        ct.append((25 - x + k) % 26)
    return np.array(ct, dtype=np.int64)


def planted_pt():
    a = "WESAWTHEFAINTLIGHTMOV"            # 21
    b = "INGSLOWLYACROSSTHEOLDSTONEWALL"[:63 - 34]
    c = "TOWERWHEREWEWAITEDFORTHEM"[:97 - 74]
    s = a + "EASTNORTHEAST" + b + "BERLINCLOCK" + c
    assert len(s) == 97 and s[21:34] == "EASTNORTHEAST" and s[63:74] == "BERLINCLOCK"
    return s


def campaign(tag, cti, restarts, iters, truth=None):
    res = []
    for r in range(restarts):
        s, nb, p = anneal(cti, CRIB, QG, iters, 1000 + r, ITERS1)
        res.append((s, nb, p))
    res.sort(key=lambda x: -x[0])
    top = res[:4]
    agree = np.mean([np.mean(top[0][2] == x[2]) for x in top[1:]])
    nonc = [i for i in range(97) if CRIB[i] < 0]
    q = np.mean([QG[((x[2][i] * 26 + x[2][i + 1]) * 26 + x[2][i + 2]) * 26 + x[2][i + 3]] for x in top[:1] for i in range(94)])
    line = f"[{tag}] best {top[0][0]:.1f} crib-misses {top[0][1]} mean-q {q:.2f} top4-agreement {agree:.2f}"
    if truth is not None:
        line += f" acc {np.mean(top[0][2][nonc] == truth[nonc]):.2f}"
    print(line, flush=True)
    print("   ", "".join(chr(65 + v) for v in top[0][2]), flush=True)
    return top[0][0]


if __name__ == "__main__":
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 400000
    rng = np.random.default_rng(20261018)
    pts = planted_pt()
    pt = np.array([ord(x) - 65 for x in pts], dtype=np.int64)
    for k in range(2):
        pct = m209_encrypt(pt, rng)
        campaign(f"PLANTED{k}", pct, restarts, iters, truth=pt)
    cti = np.array([ord(x) - 65 for x in CT], dtype=np.int64)
    campaign("REAL", cti, restarts, iters)
    nonc = np.array([i for i in range(97) if CRIB[i] < 0])
    for s in range(3):
        sh = cti.copy(); sh[nonc] = rng.permutation(cti[nonc])
        campaign(f"NULL{s}", sh, restarts, iters)
