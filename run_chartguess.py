"""Guess the chart: keyword-mixed substitution as the masking chart + small aperiodic nuance key (2026-10-18).

The letter-class signal (NOTES "SIGNAL: small-shift") fits a fixed substitution sigma + small key, but a FREE
sigma cannot be decoded. Here sigma is restricted to structured hand charts (few parameters), so the 24 cribs decide:
  sigma : plain alphabet B (AZ or KA) written over a keyword-mixed alphabet T (and the inverse chart)
  model X (chart, then shift):  num(C)        = num(sigma(P)) + c + k_i
  model Y (shift, then chart):  num(sigma^-1(C)) = num(P)    + c + k_i
  num in AZ or KA; global offset c free; nuance k_i in a window of width 5 (0..4 / +-2) or 7 (+-3), aperiodic.
Pass = at most `fault` cribs outside the window. Width 5: chance per crib 5/26, so >=22/24 by chance ~1e-13 per config.
Nulls: random sigmas (same count) and shuffled CT. Planted: keyword chart + random 0..4 key must be found.
"""
import sys
import time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet
from run_alphapairs import load_words

CI = np.array(sorted(CRIB_POS), dtype=np.int64)
PL = np.array([ord(CRIB_POS[i]) - 65 for i in CI], dtype=np.int64)
NUM = np.array([[i for i in range(26)], [KA.index(c) for c in AZ]], dtype=np.int64)  # NUM[n][letter] -> number


def charts():
    lore, words = load_words()
    seen, names, S = set(), [], []
    for w in words + lore:
        for rev in (0, 1):
            T = keyed_alphabet(w)
            T = T[::-1] if rev else T
            for bname, B in (("AZ", AZ), ("KA", KA)):
                sig = [0] * 26
                for b, t in zip(B, T):
                    sig[ord(b) - 65] = ord(t) - 65
                for inv in (0, 1):
                    s = sig if not inv else list(np.argsort(sig))
                    k = tuple(s)
                    if k not in seen:
                        seen.add(k)
                        names.append(f"{w}{' rev' if rev else ''} {bname}>T{' inv' if inv else ''}")
                        S.append(s)
    return names, np.array(S, dtype=np.int64)


@njit(parallel=True, cache=True)
def scan(S, cti, NUM, best):
    # best[q, model, num, wid] = max over c of #cribs inside window
    for q in prange(S.shape[0]):
        sig = S[q]
        inv = np.empty(26, dtype=np.int64)
        for a in range(26):
            inv[sig[a]] = a
        for model in range(2):
            for n in range(2):
                hist = np.zeros(26, dtype=np.int64)
                for e in range(CI.shape[0]):
                    c = cti[CI[e]]
                    if model == 0:
                        r = (NUM[n, c] - NUM[n, sig[PL[e]]]) % 26
                    else:
                        r = (NUM[n, inv[c]] - NUM[n, PL[e]]) % 26
                    hist[r] += 1
                for wi in range(2):
                    wid = 5 if wi == 0 else 7
                    m = 0
                    for c0 in range(26):
                        s = 0
                        for d in range(wid):
                            s += hist[(c0 + d) % 26]
                        if s > m:
                            m = s
                    best[q, model, n, wi] = m


def run(S, ct):
    cti = np.array([ord(x) - 65 for x in ct], dtype=np.int64)
    best = np.zeros((S.shape[0], 2, 2, 2), dtype=np.int64)
    scan(S, cti, NUM, best)
    return best


def report(tag, best):
    for wi, wid in enumerate((5, 7)):
        b = best[:, :, :, wi]
        print(f"[{tag}] width {wid}: max {b.max()}/24; count >=22: {(b >= 22).sum()}, >=20: {(b >= 20).sum()}, "
              f">=18: {(b >= 18).sum()}", flush=True)


if __name__ == "__main__":
    names, S = charts()
    print("charts", len(names), flush=True)
    rng = np.random.default_rng(20261018)
    # planted: SHADOW chart (AZ>T), model X, AZ numbering, key 0..4
    q = names.index("SHADOW AZ>T")
    pt = rng.integers(0, 26, 97)
    for i, ch in CRIB_POS.items():
        pt[i] = ord(ch) - 65
    pct = "".join(AZ[(S[q][p] + int(rng.integers(0, 5))) % 26] for p in pt)
    pb = run(S[q:q + 1], pct)
    print("planted SHADOW AZ>T model X AZ width5:", pb[0, 0, 0, 0], "/24", flush=True)
    t = time.time()
    best = run(S, CT)
    print("scan", round(time.time() - t, 1), "s", flush=True)
    report("REAL", best)
    top = np.argsort(-best.reshape(len(S), -1).max(1))[:15]
    for k in top:
        b = best[k]
        idx = np.unravel_index(np.argmax(b), b.shape)
        print(f"  {names[k]}: {b.max()}/24 model {'XY'[idx[0]]} num {'AZ KA'.split()[idx[1]]} width {(5, 7)[idx[2]]}")
    R = np.array([rng.permutation(26) for _ in range(len(S))], dtype=np.int64)
    report("NULL random charts", run(R, CT))
    for s in range(int(sys.argv[1]) if len(sys.argv) > 1 else 2):
        report(f"NULL shuffled CT {s}", run(S, "".join(rng.permutation(list(CT)))))
