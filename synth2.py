"""TEAM anneal: synthetic power test for non-periodic keystream modes (1 fixed/Gromark, 2-5 autokey)."""
import sys, numpy as np
from synth import PTS
from anneal2 import run, convergence, txt, NONCRIB

def gromark(primer, b=10, L=5):
    d = list(primer)
    while len(d) < 97:
        d.append((d[-L] + d[-L + 1]) % b)
    return np.array(d, dtype=np.int64)

def encrypt(pt, mode, p, seed, ks=None):
    rng = np.random.default_rng(seed)
    PA = rng.permutation(26); CAinv = rng.permutation(26)
    PAinv = np.argsort(PA); CA = np.argsort(CAinv)  # CA[j] = letter at CT-alphabet position j
    k = rng.integers(0, 26, max(p, 1))
    P = [ord(c) - 65 for c in pt]; C = []; X = []
    for i in range(97):
        if mode == 1: K = ks[i]
        elif i < p: K = k[i]
        elif mode == 2: K = X[i - p]
        elif mode == 3: K = CAinv[P[i - p]]
        elif mode == 4: K = CAinv[C[i - p]]
        else: K = PAinv[C[i - p]]
        x = PAinv[P[i]]; X.append(x)
        C.append(int(CA[(x + K) % 26]))
    return np.array(C, dtype=np.int64)

if __name__ == "__main__":
    mode = int(sys.argv[1]); p = int(sys.argv[2]); iters = int(sys.argv[3])
    for si, pt in enumerate(PTS):
        truth = np.array([ord(c) - 65 for c in pt])
        ks = gromark(np.random.default_rng(si).integers(0, 10, 5)) if mode == 1 else None
        ct = encrypt(pt, mode, p, 300 + si, ks)
        rb, rp, rq, rw, rpt = run(mode, p, cta=ct, ks=ks, ww=0.0, iters=iters, restarts=4, seed=5, T0=10.0)
        accs = [(rpt[i][NONCRIB] == truth[NONCRIB]).mean() for i in range(4)]
        cm, cmax, nc = convergence(rpt, rb, rp)
        print(f"mode={mode} p={p} pt{si} accs={np.round(accs,2).tolist()} q={np.round(rq,2).tolist()} pen={rp.tolist()} conv={cm:.2f}", flush=True)
