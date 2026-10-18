"""S7: K3's transposition is a decimation: CT_index = (192*PT_index + 191) mod 337 (n+1 prime, missing value = n).
'Instructions in earlier text' -> apply the same family to K4: j = (a*i + b) mod M, compacted to 0..96 (values >= 97
skipped in order), M in 97..110, all a coprime to M, all b; perm used as both PT->CT and CT->PT, x periodic p1-26 x 12
variants x 2 orders. Also pure transposition check (no sub) via crib letter match."""
import math, time
from common import *
from perms import inverse

def affine_perms(n=97):
    seen = set()
    for M in range(97, 111):
        for a in range(1, M):
            if math.gcd(a, M) != 1: continue
            for b in range(M):
                vals = [(a * i + b) % M for i in range(M)]
                vals = [v for v in vals if v < n]          # PT index i (sequence position) -> CT slot, compacted
                if len(vals) != n: continue
                # vals[k] = CT slot of k-th PT letter; ranks give permutation
                order = np.argsort(vals)  # CT slot j holds PT index order[j]  -> perm convention out[j]=in[perm[j]]
                perm = order.astype(np.int64)
                k = perm.tobytes()
                if k in seen: continue
                seen.add(k)
                yield f"M{M} a{a} b{b}", perm

if __name__ == "__main__":
    t = time.time()
    labels, invs = [], []
    seen = set()
    for lab, p in affine_perms():
        for tag, q in (("", p), ("inv ", inverse(p))):
            inv = inverse(q); k = inv.tobytes()
            if k in seen: continue
            seen.add(k); labels.append(tag + lab); invs.append(inv)
    invs = np.array(invs)
    print("perms", len(invs), round(time.time() - t, 1), flush=True)
    out = np.zeros((100000, 5), dtype=np.int64)
    tot = 0
    for s in range(0, len(invs), 20000):
        c = cf.check_batch(invs[s:s+20000], 1, 26, cf.KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 4, out)
        for row in out[:c]:
            q, p, order, v, m = row
            print("HIT", labels[s+q], "p", p, "order", order, cf.VARIANTS[v][:3], "m", m)
        tot += c
    print("survivors m>=4:", tot, "time", round(time.time() - t, 1))
