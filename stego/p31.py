"""S6: Sanborn's worksheets are 31-column grids (K1/K2 charts, 14x31 panel-4 grid). Long periods tied to the chart
(p=31 column key; generally p=25..48) are barely constrained by crib collisions, so instead: derive key at the
crib residues, decrypt every position whose residue is pinned, score the pinned plaintext by quadgrams over
fully-known 4-windows. Null = same with shuffled CT (crib-consistency not required in null scoring)."""
from common import *
from k4lib import load_quadgrams, CRIB_POS
QG = load_quadgrams()

def pinned_score(ct_idx, p, v, rowrestart=None):
    key = {}
    for t, i in enumerate(cf.CRIB_I):
        r = i % p if rowrestart is None else ((i + rowrestart[0]) % rowrestart[1]) % p
        k = cf.KV[v, cf.CRIB_L[t], ct_idx[i]]
        if r in key and key[r] != k:
            return None
        key[r] = k
    pt = []
    for i in range(97):
        r = i % p if rowrestart is None else ((i + rowrestart[0]) % rowrestart[1]) % p
        pt.append(cf.decrypt_letter(v, key[r], ct_idx[i]) if r in key else -1)
    sc = []; 
    for i in range(94):
        w = pt[i:i+4]
        if min(w) >= 0 and not all((i + k) in CRIB_POS for k in range(4)):
            sc.append(QG[((w[0]*26+w[1])*26+w[2])*26+w[3]])
    if len(sc) < 10: return None
    return float(np.mean(sc)), len(sc), "".join(AZ[x] if x >= 0 else "." for x in pt)

if __name__ == "__main__":
    real = []
    for p in range(25, 49):
        for v in range(cf.NV):
            r = pinned_score(cf.CTI, p, v)
            if r: real.append((r[0], r[1], p, cf.VARIANTS[v][:3], r[2]))
    # row-restart keys in a 31-col chart: key index = ((i+o) % 31) % p, p 2..30
    rr = []
    for o in range(31):
        for p in range(2, 31):
            for v in range(cf.NV):
                r = pinned_score(cf.CTI, p, v, (o, 31))
                if r: rr.append((r[0], r[1], o, p, cf.VARIANTS[v][:3], r[2]))
    real.sort(key=lambda x: -x[0]); rr.sort(key=lambda x: -x[0])
    print("periodic p25-48 consistent:", len(real))
    for x in real[:8]: print(x)
    print("row-restart (31-col chart) consistent:", len(rr))
    for x in rr[:8]: print(x)
    rng = np.random.default_rng(3); nullp = []; nullr = []
    for _ in range(200):
        sh = rng.permutation(cf.CTI)
        for p in range(25, 49):
            for v in range(cf.NV):
                r = pinned_score(sh, p, v)
                if r: nullp.append(r[0])
    nullp = np.array(nullp)
    print("null periodic: n", len(nullp), "mean", nullp.mean().round(3), "99.9pct", np.percentile(nullp, 99.9).round(3), "max", nullp.max().round(3))
