"""E4: running key (direct, no transposition) from candidate source texts.

Require: keyidx(src[o + i]) - KV[v, P_i, C_i] == const (mod 26) for crib positions i (const allows
Quagmire indicator shift). Score each offset by the size of the largest agreeing group (max 24).
Random baseline best-of-26 group ~ 4-5. Report anything >= 12.
"""
import re
import sys
import numpy as np
from numba import njit
import cribfilter as cf
from k4lib import AZ, KA, HERE
import kryptos_texts as kt


@njit(cache=True)
def scan(S, req, CI, best_out):
    n = S.shape[0] - 97
    nc = CI.shape[0]
    cnt = np.zeros(26, dtype=np.int64)
    for o in range(max(n, 0)):
        for x in range(26):
            cnt[x] = 0
        for t in range(nc):
            cnt[(S[o + CI[t]] - req[t]) % 26] += 1
        b = 0
        for x in range(26):
            if cnt[x] > b:
                b = cnt[x]
        best_out[o] = b


def letters(s):
    return re.sub("[^A-Z]", "", s.upper())


def sources():
    out = {}
    k = {"K1PT": kt.K1_PT, "K2PT": kt.K2_PT, "K3PT": kt.K3_PT, "K1CT": kt.K1_CT, "K2CT": kt.K2_CT,
         "MORSE": kt.MORSE}
    k["K123PT"] = kt.K1_PT + kt.K2_PT + kt.K3_PT
    k["K12CT"] = kt.K1_CT + kt.K2_CT
    for f in ("mobydick.txt", "kjv.txt", "tut_smith.txt"):
        k[f] = letters(open(f"{HERE}/data/{f}", errors="ignore").read())
    for name, s in list(k.items()):
        out[name] = s
        out[name + "~rev"] = s[::-1]
    return out


if __name__ == "__main__":
    srcs = sources()
    report = []
    for name, s in srcs.items():
        s = s + s[:97] if len(s) < 200 else s  # wrap short sources
        for kname, kal in (("AZ", AZ), ("KA", KA)):
            S = np.array([kal.index(c) for c in s], dtype=np.int64)
            for v in range(cf.NV):
                req = cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]]
                best = np.zeros(max(len(S) - 97, 1), dtype=np.int64)
                scan(S, req, cf.CRIB_I, best)
                o = int(best.argmax())
                report.append((int(best.max()), name, kname, cf.VARIANTS[v][:3], o, len(S)))
    report.sort(reverse=True)
    for r in report[:25]:
        print(r)
    print("max agreeing crib letters over all:", report[0][0], "/24")
