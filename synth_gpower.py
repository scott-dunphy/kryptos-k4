"""TEAM anneal: power of mode-1 (fixed Gromark keystream, free dual alphabets) at the settings used on K4 (2M iters x4)."""
import numpy as np
from synth import PTS
from synth2 import gromark, encrypt
from anneal2 import run, NONCRIB
hits = 0; n = 0
for s in range(3):
    for si, pt in enumerate(PTS):
        truth = np.array([ord(c) - 65 for c in pt])
        ks = gromark(np.random.default_rng(50 + s).integers(0, 10, 5))
        ct = encrypt(pt, 1, 0, 700 + 10 * s + si, ks)
        rb, rp, rq, rw, rpt = run(1, 0, cta=ct, ks=ks, ww=0.0, iters=2_000_000, restarts=4, seed=3, T0=10.0)
        j = int(np.argmax(rb)); acc = (rpt[j][NONCRIB] == truth[NONCRIB]).mean()
        n += 1; hits += acc > 0.8
        print(f"s{s} pt{si} best q={rq[j]:.3f} acc={acc:.2f}", flush=True)
print(f"power {hits}/{n}")
