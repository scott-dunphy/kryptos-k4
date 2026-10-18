"""TEAM clock exp 6: city-name running key under keyed alphabets (lore + city-name keyed, fwd/rev).
Combos: PA=CA=KX=X (Kryptos-tableau style); PA=AZ,CA=X,KX in {AZ,X}; PA=X,CA=AZ,KX in {AZ,X}. 3 rules. Indicator b free."""
import numpy as np
import clocklib as cl, weltzeit as w
from run_alphapairs import load_words
from k4lib import AZ, CT, CRIB_POS, keyed_alphabet
lore, _ = load_words()
cityw = sorted({w.norm(c) for v in w.VERSIONS for c, _, _ in w.cities(v)})
ALS, seen = [], set()
for wd in [""] + lore + cityw + ["URANIAWELTZEITUHR", "MENGENLEHREUHR", "ERICHJOHN", "DATUMSGRENZE"]:
    for rev in (0, 1):
        al = keyed_alphabet(wd); al = al[::-1] if rev else al
        if al not in seen: seen.add(al); ALS.append((wd + ("~" if rev else ""), al))
print("alphabets", len(ALS), flush=True)
CI = np.array(sorted(CRIB_POS)); PL = [CRIB_POS[i] for i in CI]; CLt = [CT[i] for i in CI]
def req(PA, CA, rule):
    r = []
    for p, c in zip(PL, CLt):
        ip, ic = PA.index(p), CA.index(c)
        r.append((ic - ip) % 26 if rule == 0 else (ic + ip) % 26 if rule == 1 else (ip - ic) % 26)
    return np.array([r], dtype=np.int64)
streams = {}
for ver in ("1997", "1990a"):
    names = [w.norm(c) for c, _, _ in w.cities(ver)]
    streams[ver + "concat"] = "".join(names)
    streams[ver + "first"] = "".join(n[0] for n in names)
ONE = np.array([1], dtype=np.int64)
best = []
for xn, X in ALS:
    combos = [(X, X, X, "PA=CA=KX")] + [(AZ, X, KX, "PA=AZ") for KX in (AZ, X)] + [(X, AZ, KX, "CA=AZ") for KX in (AZ, X)]
    for PA, CA, KX, cn in combos:
        for rule in range(3):
            R = req(PA, CA, rule)
            for sn, s in streams.items():
                K = np.array([KX.index(c) for c in s], dtype=np.int64)
                for d in (0, 1):
                    S = K[::-1].copy() if d else K
                    E = np.concatenate([S] * 3)
                    b, arg = cl.scan_num(E, R, cl.CI, ONE, len(S))
                    o = int(b.argmax())
                    best.append((int(b[o]), xn, cn, rule, sn, d, o, int(arg[o, 2]), KX is X))
best.sort(key=lambda x: -x[0])
for b in best[:10]: print(b)
import collections; print(sorted(collections.Counter(x[0] for x in best).items()))
