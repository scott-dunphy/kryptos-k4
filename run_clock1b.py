"""TEAM clock exp 1b: city running key allowing unknown deletions (skip up to S cities between names).
Per crib segment, longest matched crib run (contiguous from segment start-any)."""
import numpy as np, sys
import cribfilter as cf, weltzeit as w
from k4lib import AZ, KA
S = 3
REQ = [cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]] for v in range(cf.NV)]
def best_match(names, T):
    """max L such that T[0:L] equals concat of names[j][q:], names[j2], ... with skips<=S; also T suffix partial."""
    best = 0
    n = len(names)
    def ext(j, q, t):
        nonlocal best
        nm = names[j]
        while q < len(nm) and t < len(T):
            if nm[q] != T[t]:
                if t > best: best = t
                return
            q += 1; t += 1
        if t > best: best = t
        if t == len(T): return
        for j2 in range(j + 1, min(n, j + 2 + S)):
            ext(j2, 0, t)
    for j in range(n):
        for q in range(len(names[j])):
            if names[j][q] == T[0]:
                ext(j, q, 0)
    return best
out = []
for ver in ("1997", "1990a"):
    for mode in ("strip",):
        base = [w.norm(c, mode) for c, _, _ in w.cities(ver)]
        for dname, names in (("fwd", base), ("rev", [x[::-1] for x in base[::-1]])):
            for an, al in (("AZ", AZ), ("KA", KA)):
                for v in range(cf.NV):
                    for b in range(26):
                        k = (REQ[v] - b) % 26
                        T1 = "".join(al[x] for x in k[:13]); T2 = "".join(al[x] for x in k[13:])
                        m1 = best_match(names, T1); m2 = best_match(names, T2)
                        out.append((m1 + m2, m1, m2, ver, dname, an, v, b, T1, T2))
out.sort(reverse=True)
for o in out[:10]: print(o)
