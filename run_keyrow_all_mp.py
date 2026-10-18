"""Parallel version of run_keyrow_t3.py all: tableau chunks across worker processes."""
import time, numpy as np
from multiprocessing import Pool
from k4lib import keyed_alphabet
from run_alphapairs import load_words
import run_keyrow_t3 as kr

lore, words = load_words()
WORDS = sorted(set(w for w in words + lore if 3 <= len(w) <= 20))
byL = {}
for w in WORDS:
    byL.setdefault(len(w), []).append(w)
WL = {L: np.array([[ord(c) - 65 for c in ws] for ws in lst], dtype=np.int8) for L, lst in byL.items()}
NL = {L: lst for L, lst in byL.items()}
REL = np.array([i - kr.STARTS[kr.STARTS <= i].max() for i in kr.pos])


def work(chunk):
    hits = []
    for tn, ta in chunk:
        idx = {c: k for k, c in enumerate(ta)}
        for rule in range(3):
            req = np.array([ord(ta[((idx[c] - idx[p]) % 26 if rule == 0 else ((idx[c] + idx[p]) % 26 if rule == 1 else (idx[p] - idx[c]) % 26))]) - 65 for p, c in zip(kr.P, kr.C)], dtype=np.int8)
            for mode, positions in (("cont", kr.pos), ("perline", REL)):
                for L, W in WL.items():
                    mism = (W[:, positions % L] != req[None, :]).sum(axis=1)
                    for g in np.nonzero(mism <= 3)[0]:
                        hits.append((tn, rule, mode, NL[L][g], int(mism[g])))
    return hits


if __name__ == "__main__":
    T = kr.tableaus(); seen = set(T.values())
    for w in WORDS:
        for rev in (0, 1):
            a = keyed_alphabet(w); a = a[::-1] if rev else a
            if a not in seen:
                seen.add(a); T[f"dict_{w}{'~rev' if rev else ''}"] = a
    items = list(T.items()); print("tableaus", len(items), flush=True)
    chunks = [items[i:i + 2000] for i in range(0, len(items), 2000)]
    t0 = time.time(); hits = []
    with Pool(6) as pool:
        for k, h in enumerate(pool.imap_unordered(work, chunks)):
            hits += h
            if k % 20 == 0:
                print(f"  progress {k * 2000}/{len(items)} {time.time() - t0:.0f}s hits {len(hits)}", flush=True)
    print(f"done {time.time() - t0:.0f}s; hits (<=3 mismatches): {len(hits)}", flush=True)
    for h in hits[:30]:
        print("  ", h)
