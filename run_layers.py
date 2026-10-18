"""Layered Kryptos texts as K4 key.
L1: single running keys incl. K3 CT (carved) and full left-side carved text (as read row by row).
L2: key = sA*idx(A[oA+i]) + sB*idx(B[oB+i]) (mod 26) for every pair of Kryptos texts A,B (PT and CT of K0-K3,
    left side, tableau rows), every offset pair, signs (+,+),(+,-), key letters indexed AZ or KA.
Crib test: must equal required key index for all 24 cribs under some variant (12) with any indicator shift.
"""
import numpy as np
from numba import njit, prange
import cribfilter as cf
import kryptos_texts as kt
from k4lib import AZ, KA, CT as K4CT

left = "".join(l.strip() for l in open("data/sculpture_left.txt"))
left = "".join(c for c in left if c.isalpha())
right = "".join(c for c in open("data/sculpture_right.txt").read() if c.isalpha())
k4start = left.find(K4CT)
k3ct = left[left.find("ENDYAHR"):k4start] if left.find("ENDYAHR") >= 0 else ""
TEXTS = {"K0": kt.MORSE, "K1PT": kt.K1_PT, "K2PT": kt.K2_PT, "K3PT": kt.K3_PT, "K1CT": kt.K1_CT, "K2CT": kt.K2_CT,
         "K3CT": k3ct, "LEFT": left[:k4start], "RIGHT": right}


@njit(parallel=True, cache=True)
def pair_scan(A, B, REQ, CI, sb, hits):
    # REQ: (nv, 24) required key idx; any indicator shift allowed -> differences must be constant
    nA = A.shape[0] - 97; nB = B.shape[0] - 97
    for oa in prange(nA + 1):
        for ob in range(nB + 1):
            for v in range(REQ.shape[0]):
                s = -1; ok = True
                for t in range(CI.shape[0]):
                    i = CI[t]
                    k = (A[oa + i] + sb * B[ob + i]) % 26
                    d = (REQ[v, t] - k) % 26
                    if s == -1:
                        s = d
                    elif d != s:
                        ok = False
                        break
                if ok:
                    hits[oa] += 1


def req_matrix(cti):
    return np.array([cf.KV[v, cf.CRIB_L, cti[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)


def wrap(s):
    return s + s[:97]  # allow cyclic use of short texts


def run(cti, label):
    REQ = req_matrix(cti)
    total = 0
    names = list(TEXTS)
    for kal_name, kal in (("AZ", AZ), ("KA", KA)):
        arr = {n: np.array([kal.index(c) for c in wrap(TEXTS[n])], dtype=np.int64) for n in names if len(TEXTS[n]) > 20}
        # single
        for n, A in arr.items():
            Z = np.zeros(1 + 97, dtype=np.int64)  # zero second layer
            h = np.zeros(A.shape[0], dtype=np.int64)
            pair_scan(A, Z, REQ, cf.CRIB_I, 1, h)
            if h.sum():
                print(label, "SINGLE hit", n, kal_name, int(h.sum()))
            total += int(h.sum())
        keys = list(arr)
        for a in range(len(keys)):
            for b in range(a, len(keys)):
                for sb in (1, -1):
                    h = np.zeros(arr[keys[a]].shape[0], dtype=np.int64)
                    pair_scan(arr[keys[a]], arr[keys[b]], REQ, cf.CRIB_I, sb, h)
                    if h.sum():
                        print(label, "PAIR hit", keys[a], keys[b], sb, kal_name, int(h.sum()), flush=True)
                    total += int(h.sum())
    print(label, "total hits", total)
    return total


if __name__ == "__main__":
    print("text lengths", {k: len(v) for k, v in TEXTS.items()})
    # validation: K4-like synthetic with key = K1PT[5+i] + K3CT[40+i] (KA idx), KA Vig
    PT = "THECOMPASSROSEISHEREXEASTNORTHEASTTHISISYOURPOSITIONXCOMMISSIONBERLINCLOCKWHICHISNORTHEASTOFHEREX"
    A = wrap(TEXTS["K1PT"]); B = wrap(TEXTS["K3CT"])
    syn = "".join(KA[(KA.index(c) + KA.index(A[5 + i]) + KA.index(B[40 + i])) % 26] for i, c in enumerate(PT))
    run(np.array([ord(x) - 65 for x in syn]), "VALIDATION")
    run(cf.CTI, "REAL")
    rng = np.random.default_rng(0)
    run(rng.permutation(cf.CTI), "NULL")
