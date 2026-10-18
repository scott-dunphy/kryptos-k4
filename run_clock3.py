"""TEAM clock exp 3: Mengenlehreuhr (Berlin set-theory clock) lamp-derived keystreams over time sequences."""
import numpy as np, math
import clocklib as cl
def state(t):  # t minutes since midnight
    h, m = divmod(t % 1440, 60)
    return h // 5, h % 5, m // 5, m % 5, h, m
F = {
 "n1": lambda s: s[0], "n2": lambda s: s[1], "n3": lambda s: s[2], "n4": lambda s: s[3],
 "lit": lambda s: s[0] + s[1] + s[2] + s[3], "h": lambda s: s[4], "m": lambda s: s[5],
 "h+m": lambda s: s[4] + s[5], "hm": lambda s: s[4] * 60 + s[5], "h12": lambda s: s[4] % 12,
 "lit_h": lambda s: s[0] + s[1], "lit_m": lambda s: s[2] + s[3], "unlit": lambda s: 23 - (s[0] + s[1] + s[2] + s[3]),
 "hdig": lambda s: s[4] // 10 + s[4] % 10 + s[5] // 10 + s[5] % 10,
}
res = []
for step in list(range(1, 61)) + [90, 120, 7, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 97, 144]:
    n = 1440 // math.gcd(1440, step)
    seq = [state(i * step) for i in range(n)]
    for fn, f in F.items():
        K = np.array([f(s) for s in seq], dtype=np.int64)
        if len(set(K.tolist())) < 2: continue
        r = cl.test_seq(K % 26, cyclic=True)
        res.append((r, f"step{step}/{fn}", n))
    # digit streams: concatenated base-5 lamp counts (n1 n2 n3 n4) per tick, and with seconds lamp
    for dn, dig in (("n1234", lambda s: [s[0], s[1], s[2], s[3]]), ("hhmm", lambda s: [s[4] // 10, s[4] % 10, s[5] // 10, s[5] % 10]),
                    ("hm2", lambda s: [s[4], s[5]])):
        K = np.array(sum((dig(s) for s in seq), []), dtype=np.int64)
        if len(K) > 6000: K = K[:6000]
        r = cl.test_seq(K % 26, cyclic=len(K) < 6000)
        res.append((r, f"step{step}/digits_{dn}", len(K)))
res.sort(key=lambda x: -x[0][0])
for r in res[:15]: print(r)
print("n", len(res))
