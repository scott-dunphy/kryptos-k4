"""TEAM clock exp 2: numeric keystreams from Weltzeituhr city ring (per-city and per-letter), k=a*K+b."""
import numpy as np
import clocklib as cl, weltzeit as w
REAL = {"Casablanca":1,"Ankara":3,"Istanbul":3,"Minsk":3,"Nischnij Nowgorod":3,"Teheran":3.5,"Kabul":4.5,
        "Taschkent":5,"Bischkek":6,"New Delhi":5.5,"Colombo":5.5,"Rangun":6.5,"Nowosibirsk":7,
        "Chabarowsk":10,"Wladiwostok":10,"Sydney":10,"Canberra":10,"Melbourne":10,"Kap Deschnew":12,
        "Apia":13,"Marquesas In.":-9.5,"Datumsgrenze":12}
res = []
def add(tag, K, cyclic=True):
    r = cl.test_seq(np.array(K, dtype=np.int64) % 26, cyclic=cyclic)
    res.append((r, tag, len(K)))
for ver in w.VERSIONS:
    for dl in (True, False):
        C = w.cities(ver, dl)
        names = [w.norm(c) for c, _, _ in C]
        fi = [f for _, f, _ in C]
        fu = [u for _, _, u in C]
        real = [REAL.get(c, u) for c, _, u in C]
        realh = [int(np.floor(x)) for x in real]
        real2 = [int(round(2 * x)) for x in real]
        L = [len(n) for n in names]
        # rank within face
        rk = []; prev = None; r = 0
        for f in fi:
            r = r + 1 if f == prev else 1; prev = f; rk.append(r)
        fsize = [fi.count(f) for f in fi]
        tag = f"{ver}/dl{int(dl)}"
        for nm, K in (("faceidx", fi), ("faceidx1", [f + 1 for f in fi]), ("faceutc", fu), ("realutc_h", realh),
                      ("realutc_2x", real2), ("namelen", L), ("rank", rk), ("fsize", fsize),
                      ("utc+len", [a + b for a, b in zip(fu, L)]), ("cumlen", np.cumsum(L)),
                      ("diffutc", np.diff(fu + fu[:1])), ("hour24", [(u + 24) % 24 for u in fu]),
                      ("cetdiff", [u - 1 for u in fu]), ("berlintime", [(u - 1) % 24 for u in fu])):
            add(tag + "/city/" + nm, list(K))
        # per letter of concatenated names
        pl_f = sum(([f] * l for f, l in zip(fi, L)), [])
        pl_u = sum(([u] * l for u, l in zip(fu, L)), [])
        pl_ci = sum(([i] * l for i, l in zip(range(len(L)), L)), [])
        pl_pos = sum((list(range(l)) for l in L), [])
        pl_rk = sum(([r] * l for r, l in zip(rk, L)), [])
        for nm, K in (("faceidx", pl_f), ("faceutc", pl_u), ("cityidx", pl_ci), ("posinname", pl_pos), ("rank", pl_rk)):
            add(tag + "/letter/" + nm, K)
res.sort(key=lambda x: -x[0][0])
for r in res[:12]: print(r)
print("n", len(res))
print("null(147,num0-23):", cl.null_rate(lambda g: g.integers(0, 24, 147), trials=300))
print("null(1134,num0-23):", cl.null_rate(lambda g: g.integers(0, 24, 1134), trials=60))
