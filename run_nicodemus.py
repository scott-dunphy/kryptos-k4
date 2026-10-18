"""Nicodemus (ACA): PT in rows of width W under keyword; each column Vigenère-enciphered with its keyword letter
(key residue = i mod W); columns reordered by keyword order; CT read down columns in blocks of B rows.
Perm built per (W, column order, B); crib test = cribfilter.check_batch order 1 (sub-then-transpose, residue i%W),
period fixed = W, 12 substitution variants. All column orders for W<=9; dictionary keywords for W 10-14.
B in {5 (standard), 4, 6, 3, full height}.
"""
import itertools
import time
import numpy as np
import cribfilter as cf
from perms import keyword_order, inverse
from run_alphapairs import load_words

N = 97


def nico_perm(W, order, B):
    rows = -(-N // W)
    perm = []
    for b0 in range(0, rows, B):
        for c in order:
            for r in range(b0, min(b0 + B, rows)):
                i = r * W + c
                if i < N:
                    perm.append(i)
    return np.array(perm, dtype=np.int64)


def run_width(W, orders, B, out):
    invs = np.array([inverse(nico_perm(W, list(o), B)) for o in orders])
    n = cf.check_batch(invs, W, W, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 4, out)
    # keep only order==1 (sub then transpose) matches, the Nicodemus order; order 0 reported separately
    rows = out[:n]
    return rows


if __name__ == "__main__":
    out = np.zeros((200000, 5), dtype=np.int64)
    t = time.time()
    total = {0: 0, 1: 0}
    for B in (5, 4, 6, 3, 999):
        for W in range(2, 10):
            orders = list(itertools.permutations(range(W)))
            rows = run_width(W, orders, B, out)
            for r in rows:
                total[int(r[2])] += 1
            if len(rows):
                print("B", B, "W", W, "survivors", len(rows), rows[:3].tolist(), flush=True)
        print("B", B, "done W2-9 all orders", round(time.time() - t), "s", flush=True)
    lore, words = load_words()
    for W in range(10, 15):
        ws = sorted(set(w for w in words + lore if len(w) == W))
        orders = sorted(set(tuple(keyword_order(w)) for w in ws))
        for B in (5, 999):
            rows = run_width(W, orders, B, out)
            for r in rows:
                total[int(r[2])] += 1
            print("keywords W", W, "B", B, "orders", len(orders), "survivors", len(rows), flush=True)
    print("TOTAL survivors by order (1 = true Nicodemus order):", total, round(time.time() - t), "s")
