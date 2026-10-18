"""Book-cipher style running keys from initial letters: first letter of each word / line / sentence / paragraph,
last letter of each word. Sources: Carter 1923 vol I (archive.org djvu text with original line breaks), K1-K3 PT,
Smith Tutankhamen, KJV, Moby Dick.
Tests per offset & direction: (a) fixed alphabets: run_e4.scan (12 variants, key idx AZ/KA, any indicator shift),
best agreeing crib count (need 24); (b) single unknown mixed alphabet: run_gromark.consistent(mode 1) with
shift = key index (AZ or KA numbering), both signs.
"""
import html
import re
import numpy as np
from numba import njit, prange
import cribfilter as cf
import run_gromark as g
from run_e4 import scan
from k4lib import AZ, KA
import kryptos_texts as kt


def carter_lines():
    raw = open("data/carter/raw.html", encoding="utf-8", errors="ignore").read()
    m = re.search(r"<pre[^>]*>(.*?)</pre>", raw, re.S)
    return html.unescape(m.group(1)).splitlines()


def streams_from_text(text, lines=None):
    out = {}
    words = re.findall(r"[A-Za-z]+", text)
    out["word_first"] = "".join(w[0] for w in words).upper()
    out["word_last"] = "".join(w[-1] for w in words).upper()
    sents = [s for s in re.split(r"[.!?]+", text) if re.search(r"[A-Za-z]", s)]
    out["sent_first"] = "".join(re.search(r"[A-Za-z]", s).group(0) for s in sents).upper()
    paras = [p for p in re.split(r"\n\s*\n", text) if re.search(r"[A-Za-z]", p)]
    out["para_first"] = "".join(re.search(r"[A-Za-z]", p).group(0) for p in paras).upper()
    if lines is not None:
        ls = [l for l in lines if re.search(r"[A-Za-z]", l)]
        out["line_first"] = "".join(re.search(r"[A-Za-z]", l).group(0) for l in ls).upper()
        out["line_last"] = "".join(re.findall(r"[A-Za-z]", l)[-1] for l in ls).upper()
    return out


@njit(parallel=True, cache=True)
def single_alpha_scan(S, PL, CL, CI, flags):
    n = S.shape[0] - 97
    for o in prange(max(n, 0)):
        d = np.empty(97, dtype=np.int64)
        for sign in range(2):
            for i in range(97):
                d[i] = S[o + i] if sign == 0 else (26 - S[o + i]) % 26
            if g.consistent(d, 1, PL, CL, CI):
                flags[o] += 1


def test_stream(name, s):
    if len(s) < 120:
        s = s + s[:97]
    best_fixed = 0
    single_hits = 0
    for st in (s, s[::-1]):
        for kal in (AZ, KA):
            S = np.array([kal.index(c) for c in st], dtype=np.int64)
            for v in range(cf.NV):
                req = cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]]
                b = np.zeros(max(len(S) - 97, 1), dtype=np.int64)
                scan(S, req, cf.CRIB_I, b)
                best_fixed = max(best_fixed, int(b.max()))
            fl = np.zeros(max(len(S) - 97, 1), dtype=np.int64)
            single_alpha_scan(S, g.PL, g.CL, g.CI, fl)
            single_hits += int((fl > 0).sum())
    print(f"{name:28s} len={len(s):7d} fixed-alphabet best={best_fixed}/24  single-unknown-alphabet hits={single_hits}", flush=True)
    return best_fixed, single_hits


if __name__ == "__main__":
    lines = carter_lines()
    ctext = "\n".join(lines)
    sources = {"carter1923": (ctext, lines)}
    sources["K1-K3PT"] = (" ".join([kt.K1_PT, kt.K2_PT, kt.K3_PT]), None)  # no word breaks -> only letters
    for f in ("tut_smith.txt", "kjv.txt", "mobydick.txt"):
        t = open("data/" + f, errors="ignore").read()
        sources[f] = (t, t.splitlines())
    # K3 with real word breaks (book passage as on sculpture paraphrase)
    k3words = ("SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER PART OF THE DOORWAY "
               "WAS REMOVED WITH TREMBLING HANDS I MADE A TINY BREACH IN THE UPPER LEFT HAND CORNER AND THEN WIDENING "
               "THE HOLE A LITTLE I INSERTED THE CANDLE AND PEERED IN THE HOT AIR ESCAPING FROM THE CHAMBER CAUSED THE "
               "FLAME TO FLICKER BUT PRESENTLY DETAILS OF THE ROOM WITHIN EMERGED FROM THE MIST X CAN YOU SEE ANYTHING Q")
    sources["K3words"] = (k3words, None)
    print("Carter lines:", len(lines))
    for name, (text, ls) in sources.items():
        for sname, s in streams_from_text(text, ls).items():
            if len(s) >= 30:
                test_stream(f"{name}:{sname}", s)
    # null: random letter stream
    rng = np.random.default_rng(0)
    test_stream("NULL random 200k", "".join(AZ[x] for x in rng.integers(0, 26, 200000)))
