"""TEAM clock exp 16 (novel's idea a): Weltzeituhr-derived KEYED ALPHABETS + periodic key p1-30 (direct).
Alphabets: keyed_alphabet of ring-order strings (concat names / initials / last letters, starting at each face,
fwd and reversed ring, 1997+1990a) and of each city name; plus reversed alphabets. Pairs: (X,X), (AZ,X), (X,AZ),
(KA,X), (X,KA), and all (X,Y) among ring-string alphabets. Rules vig/beau/var. Report max m (crib collisions) for
consistent configs; random expectation calibrated with random alphabets."""
import numpy as np, itertools, random
import weltzeit as w
from k4lib import AZ, KA, CT, CRIB_POS, keyed_alphabet
CI = sorted(CRIB_POS); P = [CRIB_POS[i] for i in CI]; C = [CT[i] for i in CI]
def kvals(PA, CA, rule):
    out = []
    for p, c in zip(P, C):
        ip, ic = PA.index(p), CA.index(c)
        out.append((ic - ip) % 26 if rule == 0 else (ic + ip) % 26 if rule == 1 else (ip - ic) % 26)
    return out
def best_m(k):
    res = []
    for p in range(1, 31):
        d = {}; ok = True
        for i, v in zip(CI, k):
            r = i % p
            if d.setdefault(r, v) != v: ok = False; break
        if ok: res.append((24 - len(d), p))
    return max(res) if res else (0, 0)
ring = set(); named = {}
for ver in ("1997", "1990a"):
    F = w.faces(ver)
    for s in range(24):
        for d in (1, -1):
            fs = [F[(s + d * j) % 24] for j in range(24)]
            names = [w.norm(c) for f in fs for c in f]
            for tag, st in (("concat", "".join(names)), ("init", "".join(n[0] for n in names)), ("last", "".join(n[-1] for n in names))):
                al = keyed_alphabet(st); named.setdefault(al, f"{ver}/{tag}/s{s}/d{d}")
    for c, _, _ in w.cities(ver):
        al = keyed_alphabet(w.norm(c)); named.setdefault(al, "city " + w.norm(c))
ALS = list(named)
ALS += [a[::-1] for a in ALS]
for a in list(named): named[a[::-1]] = named[a] + "~"
print("alphabets", len(ALS))
def run(alist, pairs_extra=True):
    best = []
    for X in alist:
        for PA, CA in ((X, X), (AZ, X), (X, AZ), (KA, X), (X, KA)):
            for rule in range(3):
                m, p = best_m(kvals(PA, CA, rule))
                if m >= 4: best.append((m, p, rule, named.get(PA, PA[:6]), named.get(CA, CA[:6])))
    return best
best = run(ALS)
ring_als = [a for a in ALS if not named[a].startswith("city")]
for X, Y in itertools.product(ring_als, repeat=2):
    for rule in range(3):
        m, p = best_m(kvals(X, Y, rule))
        if m >= 4: best.append((m, p, rule, named[X], named[Y]))
best.sort(reverse=True); print("hits m>=4:", len(best), best[:10])
# null: random alphabets same count
rnd = []
random.seed(1)
for _ in range(len(ALS)):
    l = list(AZ); random.shuffle(l); rnd.append("".join(l))
named.update({a: "rnd" for a in rnd})
nb = run(rnd); print("null hits m>=4:", len(nb), sorted(nb, reverse=True)[:3])
