"""TEAM clock exp 1: Weltzeituhr city-name running keys (direct)."""
import numpy as np, itertools
import clocklib as cl, weltzeit as w
from k4lib import AZ, KA
ONE = np.array([1], dtype=np.int64)
res = []
def streams():
    for ver in w.VERSIONS:
        for dl in (True, False):
            for mode in ("strip", "ue"):
                C = w.cities(ver, dl)
                F = w.faces(ver)
                names = [w.norm(c, mode) for c, _, _ in C]
                tag = f"{ver}/dl{int(dl)}/{mode}"
                yield tag + "/concat", "".join(names)
                yield tag + "/namesrev", "".join(n[::-1] for n in names)
                # faces reversed order, names inside forward
                fr = []
                for f in F[::-1]:
                    fr += [w.norm(c, mode) for c in f if dl or c != "Datumsgrenze"]
                yield tag + "/facesrev", "".join(fr)
                fr2 = []
                for f in F:
                    fr2 += [w.norm(c, mode) for c in f[::-1] if dl or c != "Datumsgrenze"]
                yield tag + "/infacerev", "".join(fr2)
                yield tag + "/first", "".join(n[0] for n in names)
                yield tag + "/last", "".join(n[-1] for n in names)
                yield tag + "/second", "".join(n[1] for n in names)
seen = set()
for tag, s in streams():
    if s in seen: continue
    seen.add(s)
    for an, al in (("AZ", AZ), ("KA", KA)):
        K = cl.letters_to_idx(s, al)
        r = cl.test_seq(K, cyclic=True, units=ONE)
        res.append((r, tag, an, len(s)))
res.sort(key=lambda x: -x[0][0])
for r in res[:15]: print(r)
print("n streams", len(res))
# null: random letter strings same length 1134
print("null(1134,letters):", cl.null_rate(lambda g: g.integers(0, 26, 1134), trials=200, units=ONE))
print("null(146,letters):", cl.null_rate(lambda g: g.integers(0, 26, 146), trials=500, units=ONE))
