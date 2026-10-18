"""E1/E2b: single route / columnar transposition + periodic substitution (12 variants, 2 orders)."""
import json
import sys
import time
import numpy as np
import cribfilter as cf
from perms import route_perms, columnar_all, columnar_keywords, inverse
from k4lib import qscore

WORDS = ("KRYPTOS PALIMPSEST ABSCISSA BERLIN CLOCK WELTZEITUHR ALEXANDERPLATZ SANBORN SCHEIDT WEBSTER "
         "LANGLEY SHADOW LAYERTWO EGYPT CAIRO NILE PYRAMID MESSAGE ANTIPODES IQLUSION UNDERGROUND "
         "LUCID MEMORY TUTANKHAMUN CARTER HOWARDCARTER VIRGINIA CIA URANIA WORLDCLOCK TIME HOUR "
         "MAGNETIC COMPASS NORTHEAST EAST DELIVERINGAMESSAGE KRYPTOSABCDEFGHIJLMNQUVWXZ LIGHT "
         "WALL BERLINWALL ALEX TWENTYFOUR ZEIT WELT UHR SECRET HIDDEN INVISIBLE SLOWLY DESPERATELY "
         "ENIGMA CODE CIPHER JIMSANBORN EDSCHEIDT ED JIM").split()

pmin, pmax = 1, int(sys.argv[1]) if len(sys.argv) > 1 else 30
labels, perms = ["identity"], [np.arange(97)]
for gen in (route_perms(97), columnar_all(97, 8), columnar_keywords(97, WORDS)):
    for l, p in gen:
        labels.append(l); perms.append(p)
# test both directions
L2, P2 = [], []
for l, p in zip(labels, perms):
    L2.append(l + " fwd"); P2.append(p)
    L2.append(l + " inv"); P2.append(inverse(p))
invs = np.array([inverse(p) for p in P2])
print("perms", len(invs), flush=True)

t = time.time()
out = np.zeros((2_000_000, 5), dtype=np.int64)
n = cf.check_batch(invs, pmin, pmax, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 5, out)
print("survivors(m>=5)", n, "time", round(time.time() - t, 1), flush=True)
rows = out[:n]
from collections import Counter
print("m histogram", sorted(Counter(rows[:, 4]).items()))

# score survivors with m>=5: complete key, record
res = []
for q, p, order, v, m in rows:
    inv = invs[q]; perm = P2[q]
    key, s = cf.complete_key(inv, perm, int(p), int(order), int(v), sweeps=2)
    pt = cf.full_decrypt(inv, perm, int(p), int(order), int(v), key)
    res.append(dict(perm=L2[q], p=int(p), order=int(order), var=cf.VARIANTS[v][:3], m=int(m), score=s, pt=pt))
res.sort(key=lambda r: -r["score"])
with open("results/e1.jsonl", "w") as f:
    for r in res:
        f.write(json.dumps(r) + "\n")
for r in res[:25]:
    print(round(r["score"], 3), r["m"], r["p"], r["order"], r["var"], r["perm"], r["pt"])
