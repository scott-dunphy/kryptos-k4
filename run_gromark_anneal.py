"""TEAM anneal: anneal free dual alphabets for fixed Gromark keystreams (mode 1) — Bean's 39 b10/L5 survivors vs
random-primer keystreams (null; random primers mostly fail cribs, so also a random-but-crib-consistent null)."""
import sys, json, time, numpy as np
from anneal2 import run, convergence, txt
from synth2 import gromark
from wordscore import wseg
from run_gromark import consistent, PL, CL, CI

iters = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
R = 4
out = open("results/anneal/gromark_anneal.jsonl", "a")
surv = np.load("results/gromark_m0_b10_L5.npy")
def digits(c): return [int(x) for x in f"{int(c):05d}"]
jobs = [("BEAN", digits(c)) for c in surv]
rng = np.random.default_rng(99); nul = []
while len(nul) < 39:  # null: random 97-digit (non-Gromark) keystreams that pass the dual crib test
    d = rng.integers(0, 10, 97)
    if consistent(d, 0, PL, CL, CI):
        nul.append(d)
jobs += [("NULL", d) for d in nul]
for lab, pr in jobs:
    ks = gromark(pr) if lab == "BEAN" else np.asarray(pr)
    t = time.time()
    rb, rp, rq, rw, rpt = run(1, 0, ks=ks, ww=0.0, iters=iters, restarts=R, seed=3, T0=10.0)
    cm, cmax, nc = convergence(rpt, rb, rp)
    j = int(np.argmax(rb)); pt = txt(rpt[j]); w, cov = wseg(pt)
    rec = dict(lab=lab, primer="".join(map(str, pr[:5])) if lab == "BEAN" else "rand", q=round(float(rq[j]), 3),
               pen=int(rp[j]), w=round(w, 3), cov=round(cov, 3), conv=round(cm, 3), maxpair=round(cmax, 3), pt=pt)
    out.write(json.dumps(rec) + "\n"); out.flush()
    print(rec, f"{time.time()-t:.0f}s", flush=True)
