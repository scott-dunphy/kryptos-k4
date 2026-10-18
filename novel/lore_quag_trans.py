"""E1 perm set (identity, routes W2-49, all columnar W<=8, lore columnar; fwd+inv) x periodic Quagmire with
lore-keyword alphabets: (PT,CT) alphabets in {(A,A),(A,AZ),(AZ,A),(A~rev,AZ),(AZ,A~rev)} x vig/beau/var, p 1-24, 2 orders."""
import sys, time
import numpy as np
sys.path.insert(0, '.')
import cribfilter as cf
from perms import route_perms, columnar_all, columnar_keywords, inverse
from k4lib import AZ, KA, keyed_alphabet
from novel.linkey import LORE
WORDS = ("KRYPTOS PALIMPSEST ABSCISSA BERLIN CLOCK WELTZEITUHR ALEXANDERPLATZ SANBORN SCHEIDT WEBSTER "
         "LANGLEY SHADOW LAYERTWO EGYPT CAIRO NILE PYRAMID MESSAGE ANTIPODES IQLUSION UNDERGROUND "
         "LUCID MEMORY TUTANKHAMUN CARTER HOWARDCARTER VIRGINIA CIA URANIA WORLDCLOCK TIME HOUR "
         "MAGNETIC COMPASS NORTHEAST EAST DELIVERINGAMESSAGE KRYPTOSABCDEFGHIJLMNQUVWXZ LIGHT "
         "WALL BERLINWALL ALEX TWENTYFOUR ZEIT WELT UHR SECRET HIDDEN INVISIBLE SLOWLY DESPERATELY "
         "ENIGMA CODE CIPHER JIMSANBORN EDSCHEIDT ED JIM").split()

def kv_table(pa, ca, s):
    T = np.zeros((26, 26), np.int64)
    for P in range(26):
        for C in range(26):
            ip = pa.index(AZ[P]); ic = ca.index(AZ[C])
            T[P, C] = [(ic - ip), (ic + ip), (ip - ic)][s] % 26
    return T

pairs, seen = [], set()
for w in LORE:
    A = keyed_alphabet(w)
    if A in (AZ, KA):
        continue
    for pa, ca, lab in ((A, A, 'AA'), (A, AZ, 'A-AZ'), (AZ, A, 'AZ-A'), (A[::-1], AZ, 'Ar-AZ'), (AZ, A[::-1], 'AZ-Ar')):
        if (pa, ca) in seen: continue
        seen.add((pa, ca)); pairs.append((w, lab, pa, ca))
VARS = [(w, lab, s) for (w, lab, pa, ca) in pairs for s in range(3)]
KV = np.array([kv_table(pa, ca, s) for (w, lab, pa, ca) in pairs for s in range(3)])

if __name__ == '__main__':
    perms = [np.arange(97)]
    for gen in (route_perms(97), columnar_all(97, 8), columnar_keywords(97, WORDS)):
        for l, p in gen:
            perms.append(p)
    P2 = []
    for p in perms:
        P2 += [p, inverse(p)]
    invs = np.array([inverse(p) for p in P2])
    print('perms', len(invs), 'variants', len(KV), flush=True)
    t = time.time()
    out = np.zeros((2_000_000, 5), np.int64)
    tot = 0
    CH = 20000
    from collections import Counter
    mh = Counter()
    for s in range(0, len(invs), CH):
        n = cf.check_batch(invs[s:s + CH], 1, 24, KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 5, out)
        for q, p, o, v, m in out[:n]:
            mh[int(m)] += 1
            if m >= 6 or (m >= 5 and p <= 20):
                print('HIT', s + q, p, o, VARS[v], m, flush=True)
        tot += n
        print('chunk', s, 'survivors', n, round(time.time() - t), 's', flush=True)
    print('total m>=5', tot, sorted(mh.items()))
