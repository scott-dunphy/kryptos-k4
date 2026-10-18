"""S12 (with clock): small set of sculpture-motivated transpositions x clock's most plausible keystreams,
unknown single mixed alphabet (clocksingle scan_single / scan_beau, null 0 in 2.4e7)."""
import sys, os, time, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import *
from perms import cell_orders, inverse
from spiral import spirals, diagonals
from clocksingle import scan_single, scan_beau, UNITS
import clockstreams as cs
from run_gromark import PL, CI
from k4lib import CRIB_POS

def motivated_perms(n=97):
    out = []
    W = 31; R = 4; blanks = R * W - n
    valid = {(r, c) for r in range(R) for c in range(W) if r * W + c >= blanks}
    allo = {**cell_orders(R, W), **spirals(R, W), **diagonals(R, W)}
    rowo = allo["row"]
    fc = [x for x in rowo if x in valid]; pos = {cell: i for i, cell in enumerate(fc)}
    for rname, rcells in allo.items():
        if rname == "row": continue
        out.append((f"W31 panel row->{rname}", np.array([pos[x] for x in rcells if x in valid])))
    M = 98
    for a in range(1, M):
        if math.gcd(a, M) != 1: continue
        b = (97 * (1 - a)) % M
        vals = [(a * i + b) % M for i in range(n)]
        if max(vals) >= n: continue
        out.append((f"K3dec a{a}", np.argsort(vals)))
    res = []
    for lab, p in out:
        res.append((lab, p)); res.append(("inv " + lab, inverse(p)))
    return res

def streams():
    for name, K, cyc in cs.letter_streams(("1997", "1990a")):
        if "concat" in name: yield name, K
    for name, K, cyc in cs.mengen_streams([1]):
        if name.endswith("/lit"): yield name, K
    for name, K, cyc in cs.weltzeit_streams(("1997", "1990a")):
        if name.endswith("city/faceutc") or name.endswith("letter/faceutc"): yield name, K

if __name__ == "__main__":
    t = time.time()
    P = motivated_perms(); S = list(streams())
    print("perms", len(P), "streams", len(S), [s[0] for s in S], flush=True)
    hits = np.zeros((1000, 4), dtype=np.int64); tot = 0
    for lab, perm in P:
        inv = inverse(perm)  # PT index i sits at CT slot inv[i]
        cl_at = np.array([AZ.index(CT[inv[i]]) for i in CI], dtype=np.int64)
        for order in (0, 1):
            ci = np.array([inv[i] for i in CI], dtype=np.int64) if order == 0 else CI.copy()
            for sname, K in S:
                for dr in (0, 1):
                    Sx = K[::-1].copy() if dr else K.copy()
                    E = np.concatenate([Sx % 26] * (97 // len(Sx) + 2)); ns = len(Sx)
                    nh = scan_single(E, ns, UNITS, PL, cl_at, ci, hits)
                    nb = scan_beau(E, ns, PL, cl_at, ci, hits)
                    if nh or nb:
                        print("HIT", lab, order, sname, dr, nh, nb, flush=True); tot += 1
    print("total hits", tot, "time", round(time.time() - t, 1))
