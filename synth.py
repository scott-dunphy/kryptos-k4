"""TEAM anneal: synthetic power test for anneal2 (out-of-corpus plaintexts with cribs in place)."""
import sys, time, numpy as np
from anneal2 import run, convergence, txt, CRIB, NONCRIB
from k4lib import qscore
from wordscore import wseg

def mk(a, b, c):
    a = (a * 3)[:21]; b = (b * 3)[:29]; c = (c * 3)[:23]
    return a + "EASTNORTHEAST" + b + "BERLINCLOCK" + c

PTS = [mk("SHEWALKEDQUICKLYTOTHE", "CORNEROFTHEPLAZAANDWAITEDBYTHE", "UNTILTHESIGNALLIGHTSWENTOUT"),
       mk("FROMTHEROOFYOUCOULDSEE", "ACROSSTHERIVERTOWARDSTHEOLDWALL", "TOWERWHERETHEMEETINGWASHELD"),
       mk("WEFOLLOWEDTHESHADOWTO", "BEYONDTHEGATESOFTHECITYNEARTHE", "WHICHCHIMEDATMIDNIGHTAGAIN")]

def encrypt(pt, p, seed, mode=0):
    rng = np.random.default_rng(seed)
    PA = rng.permutation(26); CA = rng.permutation(26)  # P = PA[x] ; CAinv maps C->pos
    PAinv = np.argsort(PA); CAarr = np.argsort(CA)  # treat CA as CAinv: C letter at position j is CAarr[j]
    k = rng.integers(0, 26, p)
    ct = []
    for i, ch in enumerate(pt):
        x = PAinv[ord(ch) - 65]
        j = (x + k[i % p]) % 26
        ct.append(CAarr[j])
    return np.array(ct, dtype=np.int64)

if __name__ == "__main__":
    ps = [int(x) for x in sys.argv[1].split(",")]
    ww = float(sys.argv[2]); iters = int(sys.argv[3]); R = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    for p in ps:
        for si, pt in enumerate(PTS):
            truth = np.array([ord(c) - 65 for c in pt])
            ct = encrypt(pt, p, 100 + si)
            t = time.time()
            rb, rp, rq, rw, rpt = run(0, p, cta=ct, ww=ww, iters=iters, restarts=R, seed=7)
            j = int(np.argmax(rb - 1e6 * rp))
            acc = (rpt[j][NONCRIB] == truth[NONCRIB]).mean()
            cm, cmax, nc = convergence(rpt, rb, rp)
            accs = [(rpt[i][NONCRIB] == truth[NONCRIB]).mean() for i in range(R)]
            print(f"p={p} pt{si} ww={ww} best q={rq[j]:.3f} w={rw[j]:.3f} acc={acc:.2f} accs={np.round(sorted(accs)[::-1],2).tolist()} "
                  f"conv(best-vs-rest)={cm:.2f} maxpair={cmax:.2f} clean={nc}/{R} truthq={qscore(pt):.3f} truthw={wseg(pt)[0]:.3f} {time.time()-t:.0f}s", flush=True)
            print("   ", txt(rpt[j]))
