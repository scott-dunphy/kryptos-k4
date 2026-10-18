"""Chaocipher crib test with keyword-keyed starting alphabets (all rotations), decrypt from position 0."""
import sys
import numpy as np
from numba import njit, prange
sys.path.insert(0, '.')
from k4lib import CT, CRIB_POS, AZ, keyed_alphabet
from novel.linkey import base_alphabets

@njit(cache=True)
def chao_dec(left0, right0, ct, n, crib_pos, crib_let, out):
    left = left0.copy(); right = right0.copy()
    tmp = np.empty(26, np.int64)
    nc = 0
    ci = 0
    for t in range(n):
        c = ct[t]
        j = 0
        while left[j] != c: j += 1
        p = right[j]
        out[t] = p
        if ci < crib_pos.shape[0] and crib_pos[ci] == t:
            if p != crib_let[ci]:
                return ci
            ci += 1
        # permute left: rotate so index j at 0
        for x in range(26): tmp[x] = left[(x + j) % 26]
        z = tmp[1]
        for x in range(1, 13): tmp[x] = tmp[x + 1]
        tmp[13] = z
        for x in range(26): left[x] = tmp[x]
        # permute right: rotate so index j+1 at 0
        for x in range(26): tmp[x] = right[(x + j + 1) % 26]
        z = tmp[2]
        for x in range(2, 13): tmp[x] = tmp[x + 1]
        tmp[13] = z
        for x in range(26): right[x] = tmp[x]
    return ci

def enc_check():
    L = np.array([ord(c)-65 for c in 'HXUCZVAMDSLKPEFJRIGTWOBNYQ']); R = np.array([ord(c)-65 for c in 'PTLNBQDEOYSFAVZKGJRIHWXUMC'])
    ct = np.array([ord(c)-65 for c in 'OAHQHCNYNXTSZJRRHJBYHQKSOUJY'])
    out = np.zeros(len(ct), np.int64)
    chao_dec(L, R, ct, len(ct), np.zeros(0, np.int64), np.zeros(0, np.int64), out)
    print(''.join(chr(65+x) for x in out))

@njit(parallel=True, cache=True)
def scan(Ls, Rs, ct, crib_pos, crib_let, best):
    nL = Ls.shape[0]; nR = Rs.shape[0]
    for a in prange(nL):
        out = np.empty(97, np.int64)
        for b in range(nR):
            m = chao_dec(Ls[a], Rs[b], ct, 97, crib_pos, crib_let, out)
            best[a, b] = m

if __name__ == '__main__':
    enc_check()
    import random
    als = [a for _, a in base_alphabets()]
    rots = []
    for a in als:
        for r in range(26):
            rots.append([ord(c) - 65 for c in a[r:] + a[:r]])
    A = np.array(rots, np.int64)
    print('alphabet states', len(A), flush=True)
    cp = np.array(sorted(CRIB_POS), np.int64); cl = np.array([ord(CRIB_POS[i]) - 65 for i in cp], np.int64)
    for lab, ct in [('REAL', CT), ('SHUF', ''.join(random.sample(CT, 97)))]:
        cti = np.array([ord(c) - 65 for c in ct], np.int64)
        best = np.zeros((len(A), len(A)), np.int64)
        scan(A, A, cti, cp, cl, best)
        print(lab, 'distribution of #crib letters matched before first mismatch:', np.bincount(best.ravel()))
        idx = np.argwhere(best >= 6)
        for a, b in idx[:10]:
            print('  ', best[a, b], ''.join(chr(65+x) for x in A[a]), ''.join(chr(65+x) for x in A[b]))
