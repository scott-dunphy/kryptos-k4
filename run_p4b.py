"""TEAM anneal P4b: Quagmire IV free alphabets + periodic key, crib-repair annealer (anneal2), real vs 3 shuffled-CT nulls.
Search objective = quadgrams only; word-Viterbi score (wordscore) computed post hoc as an unoptimised discriminator.
Per restart output -> results/anneal/p4b.jsonl
"""
import sys, json, time, numpy as np
from anneal2 import run, convergence, txt, CTA
from wordscore import wseg

periods = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else list(range(1, 31))
iters = int(sys.argv[2]) if len(sys.argv) > 2 else 4_000_000
R = 8
out = open("results/anneal/p4b.jsonl", "a")
rng = np.random.default_rng(2026)
cts = [("REAL", CTA)] + [(f"NULL{j}", rng.permutation(CTA)) for j in range(3)]
for p in periods:
    for lab, ct in cts:
        t = time.time()
        rb, rp, rq, rw, rpt = run(0, p, cta=ct, ww=0.0, iters=iters, restarts=R, seed=11 * p, T0=10.0)
        cm, cmax, nc = convergence(rpt, rb, rp)
        recs = []
        for i in range(R):
            pt = txt(rpt[i]); w, cov = wseg(pt)
            recs.append(dict(q=round(float(rq[i]), 3), pen=int(rp[i]), w=round(w, 3), cov=round(cov, 3), pt=pt))
        clean = [r for r in recs if r["pen"] == 0]
        bq = max([r["q"] for r in clean], default=None); bw = max([r["w"] for r in clean], default=None)
        out.write(json.dumps(dict(p=p, lab=lab, conv=round(cm, 3), maxpair=round(cmax, 3), clean=nc, recs=recs)) + "\n"); out.flush()
        print(f"p={p:2d} {lab:5s} clean={nc}/{R} bestq={bq} bestw={bw} conv={cm:.2f} maxpair={cmax:.2f} {time.time()-t:.0f}s", flush=True)
