"""TEAM clock: generator of numeric clock-derived keystreams (name, K, cyclic)."""
import math
import numpy as np
import weltzeit as w
REAL = {"Casablanca": 1, "Ankara": 3, "Istanbul": 3, "Minsk": 3, "Nischnij Nowgorod": 3, "Teheran": 3.5, "Kabul": 4.5,
        "Taschkent": 5, "Bischkek": 6, "New Delhi": 5.5, "Colombo": 5.5, "Rangun": 6.5, "Nowosibirsk": 7,
        "Chabarowsk": 10, "Wladiwostok": 10, "Sydney": 10, "Canberra": 10, "Melbourne": 10, "Kap Deschnew": 12,
        "Apia": 13, "Marquesas In.": -9.5, "Datumsgrenze": 12}


def weltzeit_streams(versions=("1997", "1990a", "1990b", "1990c", "1990d")):
    for ver in versions:
        for dl in (True, False):
            C = w.cities(ver, dl)
            names = [w.norm(c) for c, _, _ in C]
            fi = [f for _, f, _ in C]; fu = [u for _, _, u in C]
            real = [REAL.get(c, u) for c, _, u in C]
            L = [len(n) for n in names]
            rk = []; prev = None; r = 0
            for f in fi:
                r = r + 1 if f == prev else 1; prev = f; rk.append(r)
            fsize = [fi.count(f) for f in fi]
            tag = f"{ver}/dl{int(dl)}"
            city = {"faceidx": fi, "faceutc": fu, "realutc_h": [math.floor(x) for x in real],
                    "realutc_2x": [round(2 * x) for x in real], "namelen": L, "rank": rk, "fsize": fsize,
                    "utc+len": [a + b for a, b in zip(fu, L)], "cumlen": list(np.cumsum(L)),
                    "diffutc": list(np.diff(fu + fu[:1])), "rank_rev": [s - r + 1 for s, r in zip(fsize, rk)]}
            for T in range(24):
                city[f"hour24T{T}"] = [(u + T) % 24 for u in fu]
                city[f"hour12T{T}"] = [(u + T) % 12 for u in fu]
            for nm, K in city.items():
                yield f"{tag}/city/{nm}", np.array(K, dtype=np.int64), True
                if not nm.startswith("hour12"):
                    yield f"{tag}/letter/{nm}", np.repeat(np.array(K, dtype=np.int64), L), True
            yield f"{tag}/letter/posinname", np.array(sum((list(range(l)) for l in L), []), dtype=np.int64), True
            yield f"{tag}/letter/posinname_rev", np.array(sum((list(range(l))[::-1] for l in L), []), dtype=np.int64), True


def mengen_state(t):
    h, m = divmod(t % 1440, 60)
    return h // 5, h % 5, m // 5, m % 5, h, m


MF = {"n1": lambda s: s[0], "n2": lambda s: s[1], "n3": lambda s: s[2], "n4": lambda s: s[3],
      "lit": lambda s: s[0] + s[1] + s[2] + s[3], "h": lambda s: s[4], "m": lambda s: s[5],
      "h+m": lambda s: s[4] + s[5], "hm": lambda s: s[4] * 60 + s[5], "h12": lambda s: s[4] % 12,
      "lit_h": lambda s: s[0] + s[1], "lit_m": lambda s: s[2] + s[3], "m-h": lambda s: s[5] - s[4],
      "hdig": lambda s: s[4] // 10 + s[4] % 10 + s[5] // 10 + s[5] % 10}
MD = {"n1234": lambda s: [s[0], s[1], s[2], s[3]], "hhmm": lambda s: [s[4] // 10, s[4] % 10, s[5] // 10, s[5] % 10],
      "hm2": lambda s: [s[4], s[5]], "n12_34": lambda s: [s[0] * 5 + s[1], s[2] * 5 + s[3]],
      "s_n1234": lambda s: [1, s[0], s[1], s[2], s[3]]}


def mengen_streams(steps=None):
    if steps is None:
        steps = list(range(1, 61)) + [90, 120, 61, 97, 144]
    for step in steps:
        n = 1440 // math.gcd(1440, step)
        seq = [mengen_state(i * step) for i in range(n)]
        for fn, f in MF.items():
            K = np.array([f(s) for s in seq], dtype=np.int64)
            if len(set(K.tolist())) > 1:
                yield f"mengen step{step}/{fn}", K, True
        for dn, dig in MD.items():
            K = np.array(sum((dig(s) for s in seq), []), dtype=np.int64)
            yield f"mengen step{step}/digits_{dn}", K, True


def letter_streams(versions=("1997", "1990a")):
    """City-name letter streams as numbers (key letters indexed in AZ or KA while PT/CT alphabet unknown)."""
    from k4lib import AZ, KA
    for ver in versions:
        names = [w.norm(c) for c, _, _ in w.cities(ver)]
        F = w.faces(ver)
        S = {"concat": "".join(names), "first": "".join(n[0] for n in names), "last": "".join(n[-1] for n in names),
             "facesrev": "".join(w.norm(c) for f in F[::-1] for c in f), "namesrev": "".join(n[::-1] for n in names)}
        for sn, s in S.items():
            for an, al in (("AZ", AZ), ("KA", KA)):
                yield f"{ver}/{sn}/{an}", np.array([al.index(c) for c in s], dtype=np.int64), True


def analog_streams(steps=(1, 2, 3, 4, 5, 6, 7, 10, 12, 13, 15, 17, 20, 30, 45, 60, 61, 67, 73, 97)):
    """Analog clock: minute-hand mark, hour-hand mark (0-59), hour 1-12 face number, hand angle/6, etc."""
    for step in steps:
        n = 720 // math.gcd(720, step)
        ts = [i * step for i in range(n)]
        F = {"minmark": [t % 60 for t in ts], "hourmark": [(t % 720) // 12 for t in ts],
             "hour12": [((t // 60) % 12) or 12 for t in ts], "hourpoint": [(t % 720) // 60 for t in ts],
             "angle6": [abs((t % 720) // 2 - 6 * (t % 60)) // 6 for t in ts],  # degrees/6 between hands
             "gapmarks": [((t % 60) - (t % 720) // 12) % 60 for t in ts]}
        for fn, K in F.items():
            yield f"analog step{step}/{fn}", np.array(K, dtype=np.int64), True


def date_streams():
    """Consecutive calendar dates from 1989-01-01 .. 1991-12-31 as digit streams / day numbers (non-cyclic)."""
    import datetime as dt
    d0 = dt.date(1985, 1, 1)
    days = [d0 + dt.timedelta(days=i) for i in range(365 * 7)]
    fm = {"DDMMYY": "%d%m%y", "MMDDYY": "%m%d%y", "YYMMDD": "%y%m%d", "DDMM": "%d%m", "MMDD": "%m%d",
          "DDMMYYYY": "%d%m%Y", "YYYYMMDD": "%Y%m%d"}
    for fn, f in fm.items():
        yield f"date digits {fn}", np.array([int(c) for d in days for c in d.strftime(f)], dtype=np.int64), False
    yield "date dom", np.array([d.day for d in days], dtype=np.int64), False
    yield "date dow", np.array([d.weekday() for d in days], dtype=np.int64), False
    yield "date doy", np.array([d.timetuple().tm_yday for d in days], dtype=np.int64), False
    yield "date dom+mon", np.array([d.day + d.month for d in days], dtype=np.int64), False
