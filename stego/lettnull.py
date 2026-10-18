"""S9: masking by null LETTERS ("random Q's and X's thrown in"): delete every occurrence of a letter set S from CT
(S must avoid the 24 crib CT letters -> S subset of {A,B,C,D,E,H,I,J,O,U,W,X}), |S| = 1..3, then periodic
substitution on the shortened text, with identity / routes W2-40 / columnar W<=7 (fwd+inv) on the shortened length."""
import itertools, time
from common import *
from perms import route_perms, columnar_all, inverse
from k4lib import CRIB_POS

CAND = [c for c in AZ if c not in set(CT[i] for i in CRIB_POS)]
print("candidate null letters", "".join(CAND))

def perms_for(n, cache={}):
    if n not in cache:
        L, I, seen = [], [], set()
        base = [("id", np.arange(n))] + list(route_perms(n, range(2, 41))) + list(columnar_all(n, 7))
        for lab, p in base:
            for tag, q in (("", p), ("inv ", inverse(p))):
                inv = inverse(q); k = inv.tobytes()
                if k in seen: continue
                seen.add(k); L.append(tag + lab); I.append(inv)
        cache[n] = (L, np.array(I))
    return cache[n]

if __name__ == "__main__":
    t = time.time(); out = np.zeros((100000, 5), dtype=np.int64); total = 0
    for k in (1, 2, 3):
        for S in itertools.combinations(CAND, k):
            keep = [i for i in range(97) if CT[i] not in S]
            n = len(keep); newpos = {old: j for j, old in enumerate(keep)}
            cti = np.array([AZ.index(CT[i]) for i in keep], dtype=np.int64)
            CI = np.array([newpos[i] for i in sorted(CRIB_POS)], dtype=np.int64)
            CL = np.array([AZ.index(CRIB_POS[i]) for i in sorted(CRIB_POS)], dtype=np.int64)
            labels, invs = perms_for(n)
            c = cf.check_batch(invs, 1, 24, cf.KV, cti, CI, CL, 5, out)
            for row in out[:c]:
                q, p, order, v, m = row
                print("HIT", "".join(S), n, labels[q], "p", p, "order", order, cf.VARIANTS[v][:3], "m", m, flush=True)
            total += c
    print("total survivors m>=5", total, "time", round(time.time() - t, 1))
