"""TEAM clock exp 4: clock-geometry transpositions + periodic substitution (cribfilter check_batch, p1-30).
(a) Mengenlehreuhr blocks: 97 = 1 + 4*24 lamps; block lengths cycle over row sizes; read grouped by row type.
(b) width-24 grid (Weltzeituhr faces as columns) read in face orders (rotations/dir, keyed by city data).
(c) columnar keyed by city names / clock words."""
import itertools, numpy as np
from collections import Counter
import cribfilter as cf, weltzeit as w
from perms import columnar_perm, columnar_keywords, keyword_order, inverse
labels, perms = [], []
def add(l, p):
    p = np.asarray(p, dtype=np.int64)
    assert sorted(p.tolist()) == list(range(97)), l
    labels.append(l); perms.append(p)
# (a) Mengenlehreuhr
rows_variants = {"S4 4 11 4": [1, 4, 4, 11, 4], "4 4 11 4 S": [4, 4, 11, 4, 1]}
for rn, R in rows_variants.items():
    # assign each text index to (cycle, rowtype, k). layouts: seconds lamp once at start or end, rest 4 cycles of 23
    for layout in ("cyc24",):
        cells = []  # (rowtype, cycle, k) per text index
        if layout == "cyc24":
            i = 0; cyc = 0
            while i < 97:
                for rt, ln in enumerate(R):
                    for k in range(ln):
                        if i < 97: cells.append((rt, cyc, k)); i += 1
                cyc += 1
        else:
            R2 = [x for x in R if x != 1] if R.count(1) == 1 else R
            rt_ids = [j for j, x in enumerate(R) if not (x == 1)]
            sid = R.index(1)
            body = []
            for cyc in range(4):
                for rt, ln in zip(rt_ids, R2):
                    for k in range(ln):
                        body.append((rt, cyc, k))
            cells = ([(sid, 0, 0)] + body) if layout == "S+4x23" else (body + [(sid, 0, 0)])
        assert len(cells) == 97
        nrt = len(R)
        for order in itertools.permutations(range(nrt)):
            for inner in ("cyc-major", "k-major"):
                for rev in (0, 1):
                    key = lambda i: (order.index(cells[i][0]),
                                     (cells[i][1], cells[i][2]) if inner == "cyc-major" else (cells[i][2], cells[i][1]))
                    p = sorted(range(97), key=key)
                    if rev:
                        # reverse within each row type group
                        grp = {}
                        for j in p: grp.setdefault(cells[j][0], []).append(j)
                        p = sum((grp[rt][::-1] for rt in order if rt in grp), [])
                    add(f"mengen {rn} {layout} {order} {inner} rev{rev}", p)
# (b) width-24 grid, columns = faces; read orders
F = w.faces("1997")
colorders = {}
for s in range(24):
    colorders[f"rot{s}"] = [(s + j) % 24 for j in range(24)]
    colorders[f"rot{s}r"] = [(s - j) % 24 for j in range(24)]
sizes = [len(f) for f in F]
colorders["bysize"] = sorted(range(24), key=lambda j: (-sizes[j], j))
colorders["bysize_asc"] = sorted(range(24), key=lambda j: (sizes[j], j))
colorders["byfirstcity"] = sorted(range(24), key=lambda j: w.norm(F[j][0]))
colorders["bylastcity"] = sorted(range(24), key=lambda j: w.norm(F[j][-1]))
colorders["byutc"] = sorted(range(24), key=lambda j: (w.FACE_UTC[j], j))
for W in (24,):
    for cn, o in colorders.items():
        for up in (0, 1):
            add(f"grid24 {cn} up{up}", columnar_perm(97, o, read_up=bool(up)))
# (c) columnar keywords = city names + clock words
words = sorted({w.norm(c) for v in w.VERSIONS for c, _, _ in w.cities(v)} |
               {"WELTZEITUHR", "URANIA", "URANIAWELTZEITUHR", "MENGENLEHREUHR", "ALEXANDERPLATZ", "ERICHJOHN",
                "BINNINGER", "KURFURSTENDAMM", "BERLINCLOCK", "WORLDCLOCK", "WORLDTIMECLOCK", "SETTHEORYCLOCK",
                "ALEX", "BERLINERUHR", "ZEITZONE", "ZEITZONEN", "TIMEZONE", "DATUMSGRENZE", "WELTZEIT", "MITTELEUROPAEISCHEZEIT"})
for l, p in columnar_keywords(97, words):
    add(l, p)
L2, P2 = [], []
for l, p in zip(labels, perms):
    L2 += [l + " fwd", l + " inv"]; P2 += [p, inverse(p)]
invs = np.array([inverse(p) for p in P2])
print("perms", len(invs), flush=True)
out = np.zeros((2_000_000, 5), dtype=np.int64)
n = cf.check_batch(invs, 1, 30, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 4, out)
rows = out[:n]
print("survivors m>=4:", n, sorted(Counter(rows[:, 4].tolist()).items()))
print("by p:", sorted(Counter(rows[:, 1].tolist()).items()))
for q, p, order, v, m in rows[rows[:, 4] >= 5][:20]:
    inv = invs[q]; perm = P2[q]
    key, s = cf.complete_key(inv, perm, int(p), int(order), int(v), sweeps=2)
    print(m, p, order, cf.VARIANTS[v][:3], L2[q], round(s, 3), cf.full_decrypt(inv, perm, int(p), int(order), int(v), key))
