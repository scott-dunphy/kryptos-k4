"""P4: simulated annealing, Quagmire IV with free PT/CT alphabets + periodic key, cribs as soft-hard penalty.
Decrypt: P_i = PA[(CApos[C_i] - k[i % p]) mod 26]. (Beaufort/Variant are equivalent under free alphabets.)
Null calibration: same search on shuffled CT (crib positions keep their CT letters? no: shuffle whole CT).
"""
import sys, time
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, load_quadgrams, AZ

QG = load_quadgrams()
CTA = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
CRIB = np.full(97, -1, dtype=np.int64)
for i, c in CRIB_POS.items():
    CRIB[i] = ord(c) - 65


@njit(cache=True)
def evaluate(PA, CAinv, k, p, CTA, CRIB, QG, pt):
    n = CTA.shape[0]
    pen = 0
    for i in range(n):
        x = PA[(CAinv[CTA[i]] - k[i % p]) % 26]
        pt[i] = x
        if CRIB[i] >= 0 and CRIB[i] != x:
            pen += 1
    s = 0.0
    for i in range(n - 3):
        s += QG[((pt[i] * 26 + pt[i + 1]) * 26 + pt[i + 2]) * 26 + pt[i + 3]]
    return s - 25.0 * pen, pen, s / (n - 3)


@njit(cache=True)
def anneal(p, CTA, CRIB, QG, iters, seed):
    np.random.seed(seed)
    PA = np.random.permutation(26)
    CA = np.random.permutation(26)
    CAinv = np.empty(26, dtype=np.int64)
    for i in range(26):
        CAinv[CA[i]] = i
    k = np.random.randint(0, 26, p)
    pt = np.empty(97, dtype=np.int64)
    cur, pen, q = evaluate(PA, CAinv, k, p, CTA, CRIB, QG, pt)
    best = cur; bpen = pen; bq = q
    bPA = PA.copy(); bCA = CAinv.copy(); bk = k.copy()
    T0 = 8.0
    for it in range(iters):
        T = T0 * (1.0 - it / iters) + 0.05
        mv = np.random.randint(0, 3)
        if mv == 0:
            a = np.random.randint(0, 26); b = np.random.randint(0, 26)
            PA[a], PA[b] = PA[b], PA[a]
        elif mv == 1:
            a = np.random.randint(0, 26); b = np.random.randint(0, 26)
            CAinv[a], CAinv[b] = CAinv[b], CAinv[a]
        else:
            r = np.random.randint(0, p); old = k[r]; k[r] = np.random.randint(0, 26)
        new, npen, nq = evaluate(PA, CAinv, k, p, CTA, CRIB, QG, pt)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new; pen = npen; q = nq
            if cur > best:
                best = cur; bpen = pen; bq = q
                bPA[:] = PA; bCA[:] = CAinv; bk[:k.shape[0]] = k
        else:
            if mv == 0:
                PA[a], PA[b] = PA[b], PA[a]
            elif mv == 1:
                CAinv[a], CAinv[b] = CAinv[b], CAinv[a]
            else:
                k[r] = old
    evaluate(bPA, bCA, bk, p, CTA, CRIB, QG, pt)
    return best, bpen, bq, pt.copy()


@njit(parallel=True, cache=True)
def multi(p, CTA, CRIB, QG, iters, restarts, base_seed, res_score, res_pen, res_q, res_pt):
    for r in prange(restarts):
        b, pen, q, pt = anneal(p, CTA, CRIB, QG, iters, base_seed + r)
        res_score[r] = b; res_pen[r] = pen; res_q[r] = q; res_pt[r] = pt


def run(cta, label, periods, iters=3000000, restarts=16):
    out = []
    for p in periods:
        rs = np.zeros(restarts); rp = np.zeros(restarts, dtype=np.int64); rq = np.zeros(restarts)
        rpt = np.zeros((restarts, 97), dtype=np.int64)
        multi(p, cta, CRIB, QG, iters, restarts, 1000 * p, rs, rp, rq, rpt)
        ok = np.where(rp == 0)[0]
        if len(ok):
            j = ok[np.argmax(rq[ok])]
            out.append((p, rq[j], "".join(AZ[x] for x in rpt[j])))
        else:
            out.append((p, None, ""))
        print(label, "p", p, "best crib-clean mean qg", None if not len(ok) else round(rq[j], 3),
              "clean restarts", len(ok), "/", restarts, out[-1][2], flush=True)
    return out


if __name__ == "__main__":
    periods = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else list(range(1, 31))
    t = time.time()
    real = run(CTA, "REAL", periods)
    rng = np.random.default_rng(7)
    null = run(rng.permutation(CTA), "NULL", periods)
    print("elapsed", round(time.time() - t), "s")
