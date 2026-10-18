"""Word-level scoring: Viterbi segmentation under a unigram word model (numba trie).

wseg(pt) -> (logp_per_char, coverage) where coverage = fraction of letters inside dictionary
words of length >= 3. Unknown letters cost JUNK each. Word log10 probs from Moby Dick + KJV + Smith
(words with count >= MINC) plus a small lore list.
"""
import os, re
from collections import Counter
import numpy as np
from numba import njit

HERE = os.path.dirname(os.path.abspath(__file__))
MINC = 3
MAXW = 16
JUNK = -7.0  # log10 cost per unsegmented letter
LORE = ("KRYPTOS BERLIN CLOCK EAST NORTH NORTHEAST WEST SOUTH CIA LANGLEY SANBORN SCHEIDT EGYPT CAIRO "
        "CARTER TUTANKHAMUN TOMB WALL LAYER SHADOW SHADOWS LUCID MEMORY POSITION DEGREES MINUTES SECONDS "
        "LATITUDE LONGITUDE BURIED UNDERGROUND MAGNETIC FIELD INVISIBLE ILLUSION PALIMPSEST ABSCISSA "
        "WORLD TIME UHR DELIVER MESSAGE SECRET AGENT COMPASS LODESTONE HOUR MINUTE").split()

_TRIE = None


def _corpus_words():
    c = Counter()
    for fn in ("mobydick.txt", "kjv.txt", "tut_smith.txt"):
        txt = open(os.path.join(HERE, "data", fn), encoding="utf-8", errors="ignore").read().upper()
        c.update(re.findall(r"[A-Z]+", txt))
    return c


def build(minc=MINC):
    c = _corpus_words()
    words = {w: n for w, n in c.items() if n >= minc and len(w) <= MAXW and (len(w) > 1 or w in ("A", "I"))}
    for w in LORE:
        words[w] = max(words.get(w, 0), 20)
    total = sum(words.values())
    # trie as arrays: child[node, letter], val[node] = log10 p or 0 (none)
    nodes = [[-1] * 26]
    vals = [0.0]
    for w, n in words.items():
        node = 0
        for ch in w:
            l = ord(ch) - 65
            if nodes[node][l] < 0:
                nodes[node][l] = len(nodes)
                nodes.append([-1] * 26)
                vals.append(0.0)
            node = nodes[node][l]
        vals[node] = np.log10(n / total)
    return np.array(nodes, dtype=np.int32), np.array(vals, dtype=np.float64), len(words)


def get_trie():
    global _TRIE
    if _TRIE is None:
        _TRIE = build()
    return _TRIE


@njit(cache=True)
def wseg_nb(pt, child, val, junk):
    """pt: int array of letters. Returns (total log10, covered letters in words len>=3)."""
    n = pt.shape[0]
    best = np.full(n + 1, -1e18)
    cov = np.zeros(n + 1, dtype=np.int64)
    best[0] = 0.0
    for i in range(n):
        if best[i] < -1e17:
            continue
        # junk letter
        s = best[i] + junk
        if s > best[i + 1]:
            best[i + 1] = s; cov[i + 1] = cov[i]
        node = 0
        for j in range(i, min(n, i + 16)):
            node = child[node, pt[j]]
            if node < 0:
                break
            v = val[node]
            if v != 0.0:
                s = best[i] + v
                L = j - i + 1
                if s > best[j + 1]:
                    best[j + 1] = s
                    cov[j + 1] = cov[i] + (L if L >= 3 else 0)
    return best[n], cov[n]


def wseg(text):
    child, val, _ = get_trie()
    a = np.array([ord(c) - 65 for c in text], dtype=np.int64)
    s, c = wseg_nb(a, child, val, JUNK)
    return s / len(a), c / len(a)


def segment(text):
    """Python Viterbi returning the segmentation (for display)."""
    child, val, _ = get_trie()
    n = len(text)
    best = [-1e18] * (n + 1); back = [None] * (n + 1); best[0] = 0.0
    for i in range(n):
        s = best[i] + JUNK
        if s > best[i + 1]:
            best[i + 1] = s; back[i + 1] = (i, False)
        node = 0
        for j in range(i, min(n, i + MAXW)):
            node = child[node, ord(text[j]) - 65]
            if node < 0:
                break
            if val[node] != 0.0 and best[i] + val[node] > best[j + 1]:
                best[j + 1] = best[i] + val[node]; back[j + 1] = (i, True)
    out = []; j = n
    while j > 0:
        i, isw = back[j]
        out.append(text[i:j] if isw else text[i:j].lower())
        j = i
    return " ".join(reversed(out))
