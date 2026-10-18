"""SOE-silk-style table: 26 arbitrary (unknown) mixed alphabets, row selected by keyword letter.
Direct periodic keyword (dictionary/lore words). Crib test: crib (P->C) pairs grouped by row letter
must form a partial bijection. Null: shuffled CT, same words."""
import sys, os, numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from k4lib import CT, CRIB_POS
from run_alphapairs import load_words
POS = sorted(CRIB_POS)

def ok(w, ct):
    f, g = {}, {}
    for i in POS:
        r = w[i % len(w)]; p = CRIB_POS[i]; c = ct[i]
        if f.setdefault((r, p), c) != c or g.setdefault((r, c), p) != p: return False
    return True

def checks(w):  # number of crib pairs sharing a row with an earlier one
    seen = {}; n = 0
    for i in POS:
        r = w[i % len(w)]; n += r in seen; seen[r] = 1
    return n

if __name__ == "__main__":
    lore, words = load_words(); words = sorted(set(words + lore))
    rng = np.random.default_rng(3)
    shs = []
    for _ in range(5):
        s = list(CT); rng.shuffle(s); shs.append("".join(s))
    real = [w for w in words if ok(w, CT)]
    nulls = [sum(ok(w, s) for w in words) for s in shs]
    strong = [(checks(w), w) for w in real if checks(w) >= 14]
    print("words", len(words), "real pass", len(real), "null passes (5 shuffles)", nulls)
    print("real passes with >=14 shared-row checks", sorted(strong, reverse=True)[:30])
    for s in shs[:2]:
        print("null strong", sorted([(checks(w), w) for w in words if ok(w, s) and checks(w) >= 14], reverse=True)[:10])
