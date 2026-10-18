"""TEAM clock exp 14: clock-derived letter->number tables L(x) used as autokey shifts:
CT-autokey k_i = L(C[i-lag]) (+b), PT-autokey k_i = L(P[i-lag]) for lag<=12 within cribs.
Tables from Weltzeituhr (face idx/UTC of first/last city with initial x, #cities with initial x, ...).
Fixed alphabets (12 variants, multiplier a) + unknown single alphabet (Vig/Beau) for CT-autokey."""
import numpy as np
import cribfilter as cf, clocksingle as cs, weltzeit as w
from k4lib import CT, CRIB_POS, AZ
from run_gromark import PL, CL, CI
REQ = np.array([cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]] for v in range(cf.NV)])
UN = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]
tables = {}
for ver in ("1997", "1990a"):
    C = w.cities(ver); names = [w.norm(c) for c, _, _ in C]
    for tag, sel in (("first", lambda n: n[0]), ("last", lambda n: n[-1])):
        fi = {}; fl = {}; cnt = {}
        for (c, f, u), n in zip(C, names):
            x = sel(n); cnt[x] = cnt.get(x, 0) + 1
            fi.setdefault(x, (f, u)); fl[x] = (f, u)
        tables[f"{ver}/{tag}/faceidx_firstcity"] = [fi.get(x, (0, 0))[0] for x in AZ]
        tables[f"{ver}/{tag}/utc_firstcity"] = [fi.get(x, (0, 0))[1] for x in AZ]
        tables[f"{ver}/{tag}/faceidx_lastcity"] = [fl.get(x, (0, 0))[0] for x in AZ]
        tables[f"{ver}/{tag}/count"] = [cnt.get(x, 0) for x in AZ]
    # letter -> number of occurrences in all names / in face of Berlin
    allc = "".join(names)
    tables[f"{ver}/lettercount"] = [allc.count(x) for x in AZ]
# Mengenlehreuhr: letter value n (A=0/1) displayed as minutes/hours -> lamp count
for base in (0, 1):
    tables[f"mengen_minutes_lit_A{base}"] = [(v + base) // 5 + (v + base) % 5 for v in range(26)]
    tables[f"mengen_hours_lit_A{base}"] = [((v + base) % 24) // 5 + ((v + base) % 24) % 5 for v in range(26)]
CTI = cf.CTI
best = []
for tn, T in tables.items():
    T = np.array(T, dtype=np.int64)
    for lag in range(1, 13):
        # CT autokey: key at crib pos i = T[C[i-lag]]
        K = np.array([T[CTI[i - lag]] if i >= lag else 0 for i in range(97)], dtype=np.int64)
        for v in range(12):
            for a in UN:
                vals = (REQ[v] - a * K[CI]) % 26
                best.append((int(np.bincount(vals).max()), tn, "CTauto", lag, v, a))
        d = K % 26
        for b in range(26):
            dd = (d + b) % 26
            if cs.consistent(dd, 1, PL, CL, CI): print("HIT single vig", tn, lag, b)
            if cs.consistent_beau(dd, PL, CL, CI): print("HIT single beau", tn, lag, b)
        # PT autokey within cribs
        pos = {i: AZ.index(c) for i, c in CRIB_POS.items()}
        idx = [t for t, i in enumerate(CI) if (i - lag) in pos]
        if len(idx) >= 6:
            Kp = np.array([T[pos[CI[t] - lag]] for t in idx])
            for v in range(12):
                for a in UN:
                    vals = (REQ[v][idx] - a * Kp) % 26
                    best.append((int(np.bincount(vals).max()) + 100 * 0, tn, f"PTauto(n={len(idx)})", lag, v, a))
best.sort(key=lambda x: -x[0])
for b in best[:8]: print(b)
print("tests", len(best))
