"""Ground-shadow overlap test using the 3D model geometry.
Both faces (cipher S-half with K4 at rows 24-27, tableau S-half) are half-cylinders of radius R, height H, joined in an S.
For sun direction (az, el): project every letter cell centre onto the ground along the sun ray. For each K4 cell, find the
nearest tableau cell shadow within tolerance; key letter = that tableau letter. Test 24 cribs under 12 variants x key index
AZ/KA x indicator shift (max agreeing count). Sweep az 0..358 (step 2), el 2..86 (step 2). Heading is equivalent to az.
Null: shuffled CT at crib positions.
"""
import numpy as np
from numba import njit, prange
import cribfilter as cf
from k4lib import CT, CRIB_POS, AZ, KA

H, R, ROWS, COLS = 3.66, 1.52, 28, 32
rows = [l.rstrip("\n") for l in open("data/sculpture_right.txt")]
tab_cells = []  # (u, v, letter)
for r, l in enumerate(rows):
    for k in range(min(COLS, len(l))):
        if l[k].isalpha():
            tab_cells.append(((k + 0.5) / COLS, 1 - (r + 0.5) / ROWS, ord(l[k]) - 65))
tab_uv = np.array([(u, v) for u, v, _ in tab_cells]); tab_let = np.array([c for _, _, c in tab_cells], dtype=np.int64)
# K4 cells on the cipher face: index i -> row 24 col 27+i for i<4, else row 25+(i-4)//31, col (i-4)%31
k4_uv = np.array([(((27 + i) if i < 4 else (i - 4) % 31) + 0.5) / COLS for i in range(97)]), \
        np.array([1 - ((24 if i < 4 else 25 + (i - 4) // 31) + 0.5) / ROWS for i in range(97)])
k4_uv = np.stack(k4_uv, axis=1)


def arc(uv, sign, offx):
    a = np.pi * (1 - uv[:, 0])
    return np.stack([sign * R * np.cos(a) + offx, uv[:, 1] * H, sign * R * np.sin(a)], axis=1)


P_k4 = arc(k4_uv, 1, -R)       # cipher half
P_tab = arc(tab_uv, -1, R)     # tableau half
cell_w = np.pi * R / COLS; cell_h = H / ROWS
IDX = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)
REQ = np.array([cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)


@njit(cache=True)
def best_fit(keys, has, REQ, IDX, CI):
    best = 0
    for v in range(REQ.shape[0]):
        for kx in range(2):
            cnt = np.zeros(26, dtype=np.int64)
            for t in range(CI.shape[0]):
                i = CI[t]
                if has[i]:
                    cnt[(REQ[v, t] - IDX[kx, keys[i]]) % 26] += 1
            m = 0
            for x in range(26):
                if cnt[x] > m:
                    m = cnt[x]
            if m > best:
                best = m
    return best


@njit(parallel=True, cache=True)
def sweep(P_k4, P_tab, tab_let, REQ, IDX, CI, azs, els, tol, out):
    for ai in prange(azs.shape[0]):
        az = azs[ai] * np.pi / 180
        for ei in range(els.shape[0]):
            el = els[ei] * np.pi / 180
            sx = np.cos(el) * np.sin(az); sy = np.sin(el); sz = -np.cos(el) * np.cos(az)
            # ground projections
            gk = np.empty((97, 2)); gt = np.empty((P_tab.shape[0], 2))
            for i in range(97):
                t = P_k4[i, 1] / sy; gk[i, 0] = P_k4[i, 0] - sx * t; gk[i, 1] = P_k4[i, 2] - sz * t
            for j in range(P_tab.shape[0]):
                t = P_tab[j, 1] / sy; gt[j, 0] = P_tab[j, 0] - sx * t; gt[j, 1] = P_tab[j, 2] - sz * t
            keys = np.zeros(97, dtype=np.int64); has = np.zeros(97, dtype=np.int64); n = 0
            for i in range(97):
                bd = tol * tol; bj = -1
                for j in range(P_tab.shape[0]):
                    d = (gk[i, 0] - gt[j, 0]) ** 2 + (gk[i, 1] - gt[j, 1]) ** 2
                    if d < bd:
                        bd = d; bj = j
                if bj >= 0:
                    keys[i] = tab_let[bj]; has[i] = 1; n += 1
            ncrib = 0
            for t in range(CI.shape[0]):
                ncrib += has[CI[t]]
            out[ai, ei, 0] = ncrib
            out[ai, ei, 1] = best_fit(keys, has, REQ, IDX, CI) if ncrib >= 12 else 0


if __name__ == "__main__":
    azs = np.arange(0, 360, 2.0); els = np.arange(2, 88, 2.0)
    tol = 0.5 * cell_w  # within half a cell on the ground (shadows stretch, so this is generous near the base)
    out = np.zeros((len(azs), len(els), 2), dtype=np.int64)
    sweep(P_k4, P_tab, tab_let, REQ, IDX, cf.CRIB_I, azs, els, tol, out)
    cov = out[:, :, 0]; fit = out[:, :, 1]
    print("sun positions with >=12 crib letters overlapping tableau shadows:", int((cov >= 12).sum()), "of", cov.size)
    i, j = np.unravel_index(fit.argmax(), fit.shape)
    print(f"REAL best crib agreement {fit.max()} (of {cov[i, j]} overlapping) at az {azs[i]:.0f} el {els[j]:.0f}")
    rng = np.random.default_rng(0)
    for k in range(3):
        sh = rng.permutation(cf.CTI)
        REQ2 = np.array([cf.KV[v, cf.CRIB_L, sh[cf.CRIB_I]] for v in range(cf.NV)], dtype=np.int64)
        o2 = np.zeros_like(out); sweep(P_k4, P_tab, tab_let, REQ2, IDX, cf.CRIB_I, azs, els, tol, o2)
        print(f"NULL{k} best agreement {o2[:, :, 1].max()}")
