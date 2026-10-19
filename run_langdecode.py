"""Extinct/other-language plaintext test (2026-10-18). Chart model of run_chartdecode.py (bijective sigma +
nuance key k in 0..4, cribs fixed, 64/71 exempt), decoded with letter 4-gram models of Latin, Old English, German,
Middle Egyptian (TLA transliteration flattened to A-Z) and an English baseline built the same way (data/lang/).
If the 73 non-crib letters are in language X, REAL should beat its non-crib-shuffled nulls under X's model more
than under the others. Planted: a held-out passage of X with the cribs pasted in, enciphered with a random chart.
"""
import sys
import numpy as np
from k4lib import CT, CRIB_POS
from run_chartdecode import anneal, crib_pen, CRIB, EXEMPT

LANGS = ["en", "la", "ang", "de", "egy"]
QGS = {l: np.load(f"data/lang/qg_{l}.npy").astype(np.float64) for l in LANGS}
KSET = np.array([0, 1, 2, 3, 4])
NC = np.array([i for i in range(97) if CRIB[i] < 0])


def decode(ct, qg, restarts, iters):
    outs = []
    for r in range(restarts):
        b, sig, pt = anneal(ct, KSET, CRIB, EXEMPT, qg, iters, 1000 + r)
        outs.append((b, crib_pen(ct, sig, KSET, CRIB, EXEMPT), pt))
    clean = [o for o in outs if o[1] == 0] or outs
    top = max(clean, key=lambda o: o[0])
    ag = np.mean([np.mean(clean[i][2][NC] == clean[j][2][NC]) for i in range(len(clean)) for j in range(i + 1, len(clean))]) if len(clean) > 1 else 0
    return top[0], ag, top[2]


def planted(lang, rng):
    s = open(f"data/lang/{lang}_letters.txt").read()
    o = int(rng.integers(len(s) // 2, len(s) - 200))
    pt = np.array([ord(c) - 65 for c in s[o:o + 97]], dtype=np.int64)
    for i, ch in CRIB_POS.items():
        pt[i] = ord(ch) - 65
    sig = rng.permutation(26)
    return np.array([(sig[p] + int(rng.integers(0, 5))) % 26 for p in pt], dtype=np.int64), pt


if __name__ == "__main__":
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
    nnull = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    langs = sys.argv[4].split(",") if len(sys.argv) > 4 else LANGS
    rng = np.random.default_rng(20261018)
    cta = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
    nulls = []
    for k in range(nnull):
        a = cta.copy(); a[NC] = rng.permutation(a[NC]); nulls.append(a)
    for lang in langs:
        qg = QGS[lang]
        pct, ppt = planted(lang, rng)
        pb, pag, ppt2 = decode(pct, qg, restarts, iters)
        pacc = np.mean(ppt2[NC] == ppt[NC])
        pn = decode(nulls[0], qg, restarts, iters)[0]
        rb, rag, rpt = decode(cta, qg, restarts, iters)
        ns = [decode(a, qg, restarts, iters) for a in nulls]
        nb = [x[0] for x in ns]
        print(f"[{lang}] PLANTED score {pb:.3f} acc {pacc:.2f} agree {pag:.2f} | REAL {rb:.3f} agree {rag:.2f} | "
              f"NULLS {' '.join(f'{x:.3f}' for x in nb)} agree {np.mean([x[1] for x in ns]):.2f} | "
              f"REAL-nullmax {rb - max(nb):+.3f}", flush=True)
        print(f"    REAL  {''.join(chr(65 + v) for v in rpt)}", flush=True)
        print(f"    PLANT {''.join(chr(65 + v) for v in ppt2)}", flush=True)
