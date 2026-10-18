"""TEAM anneal service: screen numeric keystreams (n,97) int .npy under FREE DUAL alphabets.
1) dual-alphabet crib union-find (run_gromark.consistent mode 0; also tests -K = Beaufort-sense is equivalent);
2) anneal survivors (anneal2 mode 1, quadgram objective) + equal number of random crib-consistent null streams
   drawn with the same value distribution; report q, word score, restart convergence.
Usage: screen_streams.py streams.npy label [iters] [max_survivors]"""
import sys, json, time, numpy as np
from anneal2 import run, convergence, txt
from wordscore import wseg
from run_gromark import consistent, PL, CL, CI

def anneal_one(ks, iters, R=4):
    rb, rp, rq, rw, rpt = run(1, 0, ks=np.asarray(ks, dtype=np.int64) % 26, ww=0.0, iters=iters, restarts=R, seed=3, T0=10.0)
    cm, cmax, nc = convergence(rpt, rb, rp)
    j = int(np.argmax(rb)); pt = txt(rpt[j]); w, cov = wseg(pt)
    return dict(q=round(float(rq[j]), 3), pen=int(rp[j]), w=round(w, 3), cov=round(cov, 3), conv=round(cm, 3),
                maxpair=round(cmax, 3), pt=pt)

if __name__ == "__main__":
    S = np.load(sys.argv[1]) % 26; label = sys.argv[2]
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 2_000_000
    maxs = int(sys.argv[4]) if len(sys.argv) > 4 else 60
    surv = [i for i in range(len(S)) if consistent(S[i].astype(np.int64), 0, PL, CL, CI)]
    print(f"{label}: {len(S)} streams, {len(surv)} pass dual crib test (rate {len(surv)/len(S):.2e}; random ~4e-4)", flush=True)
    rng = np.random.default_rng(5); vals = S.ravel(); nul = []
    while len(nul) < min(len(surv), maxs, 40):
        d = rng.choice(vals, 97)
        if consistent(d.astype(np.int64), 0, PL, CL, CI):
            nul.append(d)
    out = open(f"results/anneal/screen_{label}.jsonl", "w")
    for lab, idx, ks in [("CAND", i, S[i]) for i in surv[:maxs]] + [("NULL", -1, d) for d in nul]:
        r = anneal_one(ks, iters); r.update(lab=lab, idx=int(idx))
        out.write(json.dumps(r) + "\n"); out.flush(); print(r, flush=True)
