"""TEAM anneal: (a) power test, planted PT with clock's real low-variety streams + free dual alphabets;
(b) clock's 9 canonical streams (results/clock_streams_for_anneal.json), real CT vs shuffled-CT null."""
import json, numpy as np
from synth import PTS
from synth2 import encrypt
from anneal2 import run, convergence, txt, NONCRIB, CTA
from screen_streams import anneal_one
S = np.load("results/clock_dual_survivors.npy").astype(np.int64)
for si, idx in enumerate([0, 60, 120]):
    ks = S[idx]; pt = PTS[si]; truth = np.array([ord(c) - 65 for c in pt])
    ct = encrypt(pt, 1, 0, 900 + si, ks)
    rb, rp, rq, rw, rpt = run(1, 0, cta=ct, ks=ks, ww=0.0, iters=2_000_000, restarts=4, seed=3, T0=10.0)
    accs = [(rpt[i][NONCRIB] == truth[NONCRIB]).mean() for i in range(4)]
    cm, cmax, nc = convergence(rpt, rb, rp)
    print(f"POWER stream{idx} distinct={len(set(ks.tolist()))} accs={np.round(accs,2).tolist()} q={np.round(rq,3).tolist()} conv={cm:.2f}", flush=True)
J = json.load(open("results/clock_streams_for_anneal.json"))
null_ct = np.random.default_rng(31).permutation(CTA)
for name, ks in J.items():
    ks = np.array(ks, dtype=np.int64) % 26
    for lab, ct in (("REAL", CTA), ("NULL", null_ct)):
        rb, rp, rq, rw, rpt = run(1, 0, cta=ct, ks=ks, ww=0.0, iters=2_000_000, restarts=4, seed=3, T0=10.0)
        cm, cmax, nc = convergence(rpt, rb, rp)
        j = int(np.argmax(rb - 1e6 * rp))
        from wordscore import wseg
        w, cov = wseg(txt(rpt[j]))
        print(f"{name} {lab} clean={nc}/4 q={rq[j]:.3f} pen={rp[j]} w={w:.3f} conv={cm:.2f} {txt(rpt[j])}", flush=True)
