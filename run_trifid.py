"""TEAM clock exp T1: Trifid (Delastelle, 3x3x3, base-3 'language base') direct decryption with keyword-keyed cubes.
Cube = keyed 27-symbol alphabet (26 letters + '#' filler at end or start; fwd/rev); periods 1..97.
Score = # crib letters matched (24 = real). Also mixed-radix 'Mengenlehre' variant not here."""
import time, numpy as np
from numba import njit, prange
from run_alphapairs import load_words
import weltzeit as w
from k4lib import CT, CRIB_POS, keyed_alphabet
CTI = np.array([ord(c) - 65 for c in CT]); CI = np.array(sorted(CRIB_POS)); CL = np.array([ord(CRIB_POS[i]) - 65 for i in CI])


@njit(parallel=True, cache=True)
def sweep(CUBES, CTI, CI, CL, out):
    N = CUBES.shape[0]
    for q in prange(N):
        cube = CUBES[q]
        pos = np.empty(27, dtype=np.int64)
        for c in range(27): pos[cube[c]] = c
        dig = np.empty(3 * 97, dtype=np.int64)
        for i in range(97):
            p = pos[CTI[i]]
            dig[3 * i] = p // 9; dig[3 * i + 1] = (p // 3) % 3; dig[3 * i + 2] = p % 3
        pt = np.empty(97, dtype=np.int64)
        best = 0; bp = 0
        for n in range(1, 98):
            for g0 in range(0, 97, n):
                m = min(n, 97 - g0)
                base = 3 * g0
                for j in range(m):
                    L = dig[base + j]; R = dig[base + m + j]; C = dig[base + 2 * m + j]
                    pt[g0 + j] = cube[L * 9 + R * 3 + C]
            s = 0
            for t in range(CI.shape[0]):
                if pt[CI[t]] == CL[t]: s += 1
            if s > best: best = s; bp = n
        out[q, 0] = best; out[q, 1] = bp


lore, words = load_words()
cityw = sorted({w.norm(c) for v in w.VERSIONS for c, _, _ in w.cities(v)})
A27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
cubes, names, seen = [], [], set()
for wd in [""] + lore + cityw + words:
    al = keyed_alphabet(wd)
    for rev in (0, 1):
        a = al[::-1] if rev else al
        for fill in ("end", "start"):
            s = a + "[" if fill == "end" else "[" + a
            if s in seen: continue
            seen.add(s); cubes.append([ord(c) - 65 for c in s]); names.append(f"{wd}{'~' if rev else ''}/{fill}")
CUBES = np.array(cubes, dtype=np.int64)
# validation: planted trifid
def enc(pt, cube, n):
    pos = {c: i for i, c in enumerate(cube)}; out = []
    for g0 in range(0, len(pt), n):
        grp = pt[g0:g0 + n]; m = len(grp)
        rows = [[pos[c] // 9 for c in grp], [(pos[c] // 3) % 3 for c in grp], [pos[c] % 3 for c in grp]]
        d = rows[0] + rows[1] + rows[2]
        out += [cube[d[3 * k] * 9 + d[3 * k + 1] * 3 + d[3 * k + 2]] for k in range(m)]
    return out
cube = cubes[names.index("KRYPTOS/end")]
ptv = [ord(c) - 65 for c in ("XXXXXXXXXXXXXXXXXXXXX" + "EASTNORTHEAST" + "Q" * 29 + "BERLINCLOCK" + "Z" * 23)]
fake = np.array(enc(ptv, cube, 7)); o = np.zeros((1, 2), dtype=np.int64)
sweep(np.array([cube]), fake, CI, CL, o); print("validation (expect 24, n=7):", o)
print("cubes", len(CUBES), flush=True)
t = time.time(); out = np.zeros((len(CUBES), 2), dtype=np.int64)
sweep(CUBES, CTI, CI, CL, out)
print("time", round(time.time() - t))
print("best-score histogram:", np.bincount(out[:, 0]))
for q in np.argsort(-out[:, 0])[:8]: print(names[q], out[q])
