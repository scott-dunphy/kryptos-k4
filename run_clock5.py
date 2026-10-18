"""TEAM clock exp 5: (a) hour-ring readings: per-city/per-letter local hour (u+T) mod 24 / mod 12, all T;
(b) polynomial 'clock-drift' keys k(i)=b+d*i+e*i^2 (+ cubic) mod 26; (c) mod-24 progressive k=(b+d*i) mod 24 + c*floor(i/24)."""
import numpy as np
import clocklib as cl, weltzeit as w
ONE = np.array([1], dtype=np.int64)
res = []
for ver in ("1997", "1990a"):
    C = w.cities(ver)
    names = [w.norm(c) for c, _, _ in C]
    fu = np.array([u for _, _, u in C]); L = [len(n) for n in names]
    for T in range(24):
        for mod, base in ((24, 0), (24, 1), (12, 0), (12, 1)):
            K = (fu + T) % mod + base
            r = cl.test_seq(K, units=ONE); res.append((r, f"{ver}/city/hour mod{mod}+{base} T{T}"))
            KL = np.repeat(K, L)
            r = cl.test_seq(KL, units=ONE); res.append((r, f"{ver}/letter/hour mod{mod}+{base} T{T}"))
i = np.arange(97)
# polynomial keys: b handled by scan; vary d,e,f
best = []
for d in range(26):
    for e in range(26):
        for f3 in range(26):
            K = (d * i + e * i * i + f3 * i ** 3) % 26
            # direct check only offset 0 (non-cyclic, exactly 97)
            r = cl.test_seq(K, cyclic=False, units=ONE, both_dirs=False)
            best.append((r, f"poly d{d} e{e} f{f3}"))
best.sort(key=lambda x: -x[0][0]); res += best[:5]
res.sort(key=lambda x: -x[0][0])
for r in res[:12]: print(r)
# null for poly: random 97-key, single offset: chance
print("null single-offset random:", cl.null_rate(lambda g: g.integers(0, 26, 97), trials=3000, units=ONE, cyclic=False, both_dirs=False))
