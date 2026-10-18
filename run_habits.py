"""Sanborn-habit tests (all direct, positional).
T1 slipped key row: periodic keyword (all words + names) with ONE phase slip of d in {±1,±2,±3} at any position s;
   tableau alphabet T in {AZ, KA} (PT, CT, key indexed in T), rules vig/beau/var. Require all 24 cribs.
T2 key written down the 31-wide worksheet (column order, snake, diagonal) then read by rows; sheet starts at K4 pos 0
   (and with '?' at col 0). Keyword cycles through the cells in that order. All words+names, AZ/KA, 3 rules, exact.
T3 neighbour mixing: C = a*P_i + b*P_{i+d} + c (mod 26), d in {-1,+1}, a in units, b in 0..25, c in 0..25, AZ and KA
   numbering. 22 checks inside crib runs.
T4 key = next plaintext letter (lag -1, -2), AZ/KA, 3 rules, any indicator shift.
T5 proper names as periodic keys (also covered within T1 slip test) and as keyed alphabets vs AZ/KA periodic p<=24.
T6 position-number keys: k_i = f(i) for f in {i mod m (m 2..30), digit sum of i, i*i mod 26, (i+1) mod m, i//m}, ±, AZ/KA.
"""
import numpy as np
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet
from run_alphapairs import load_words
import cribfilter as cf

pos = sorted(CRIB_POS)
NAMES = """WILLIAMWEBSTER WEBSTER WILLIAM EDWARDSCHEIDT EDSCHEIDT SCHEIDT EDWARD JAMESSANBORN JIMSANBORN SANBORN JAMES JIM
HOWARDCARTER CARTER HOWARD CARNARVON LORDCARNARVON TUTANKHAMUN TUTANKHAMEN ERICHJOHN SCHABOWSKI GORBACHEV REAGAN
RONALDREAGAN KENNEDY JOHNKENNEDY HONECKER KOHL HELMUTKOHL BUSH GEORGEBUSH GATES ROBERTGATES CASEY WILLIAMCASEY
COLBY HELMS DULLES ALLENDULLES DONOVAN YARDLEY FRIEDMAN KAHN DAVIDKAHN ELONKA DUNIN GILLOGLY STEIN DAVIDSTEIN
KRYPTOS LANGLEY MCLEAN VIRGINIA WASHINGTON POTOMAC ALEXANDERPLATZ BRANDENBURG CHARLIE CHECKPOINTCHARLIE
URANIA WELTZEITUHR MENGENLEHREUHR JEFFERSON WASHINGTONDC CIA KGB STASI MOSSAD NSA""".split()


def tab_key_letters(T, rule):
    out = []
    for i in pos:
        ip, ic = T.index(CRIB_POS[i]), T.index(CT[i])
        k = (ic - ip) % 26 if rule == 0 else ((ic + ip) % 26 if rule == 1 else (ip - ic) % 26)
        out.append(T[k])
    return out


def t1_slip(words):
    """Vectorized: slip position classes = 0 (none) and every crib position (slip just before it)."""
    hits = []
    byL = {}
    for w in words:
        byL.setdefault(len(w), []).append(w)
    WL = {L: np.array([[ord(c) - 65 for c in ws] for ws in lst], dtype=np.int8) for L, lst in byL.items()}
    P = np.array(pos)
    sclasses = [0] + pos[1:]
    for T in (AZ, KA):
        for rule in range(3):
            req = np.array([ord(x) - 65 for x in tab_key_letters(T, rule)], dtype=np.int8)
            for L, W in WL.items():
                for ph in range(L):
                    for d in (0, -3, -2, -1, 1, 2, 3):
                        for s in (sclasses if d else [0]):
                            idx = (P + ph + np.where(P >= s, d, 0)) % L if d else (P + ph) % L
                            ok = np.all(W[:, idx] == req[None, :], axis=1)
                            for g in np.nonzero(ok)[0]:
                                hits.append((byL[L][g], f"slip {d:+d} before {s}" if d else "no-slip", T == KA, rule))
    return hits


def t2_vertical(words):
    hits = []
    orders = {}
    for qmark in (0, 1):
        cells = [(i + qmark) for i in range(97)]            # sheet index of K4 position i
        rows = 4; W = 31
        def rc(x): return x // W, x % W
        # column-major order index of each cell
        col_major = {}; n = 0
        for c in range(W):
            for r in range(rows):
                x = r * W + c
                if 0 <= x - qmark < 97: col_major[x] = n; n += 1
        snake = {}; n = 0
        for r in range(rows):
            cols = range(W) if r % 2 == 0 else range(W - 1, -1, -1)
            for c in cols:
                x = r * W + c
                if 0 <= x - qmark < 97: snake[x] = n; n += 1
        colsnake = {}; n = 0
        for c in range(W):
            rs = range(rows) if c % 2 == 0 else range(rows - 1, -1, -1)
            for r in rs:
                x = r * W + c
                if 0 <= x - qmark < 97: colsnake[x] = n; n += 1
        diag = {}; n = 0
        for dsum in range(rows + W):
            for r in range(rows):
                c = dsum - r
                if 0 <= c < W:
                    x = r * W + c
                    if 0 <= x - qmark < 97: diag[x] = n; n += 1
        for nm, m in (("col", col_major), ("snake", snake), ("colsnake", colsnake), ("diag", diag)):
            orders[f"{nm}{'?' if qmark else ''}"] = [m[i + qmark] for i in range(97)]
    byL = {}
    for w in words:
        byL.setdefault(len(w), []).append(w)
    WL = {L: np.array([[ord(c) - 65 for c in ws] for ws in lst], dtype=np.int8) for L, lst in byL.items()}
    for T in (AZ, KA):
        for rule in range(3):
            req = np.array([ord(x) - 65 for x in tab_key_letters(T, rule)], dtype=np.int8)
            for oname, idx in orders.items():
                I = np.array([idx[i] for i in pos])
                for L, W in WL.items():
                    for ph in range(L):
                        ok = np.all(W[:, (I + ph) % L] == req[None, :], axis=1)
                        for g in np.nonzero(ok)[0]:
                            hits.append((byL[L][g], oname, T == KA, rule))
    return hits


def t3_neighbour():
    hits = []
    for T in (AZ, KA):
        P = {i: T.index(CRIB_POS[i]) for i in pos}; C = {i: T.index(CT[i]) for i in pos}
        for d in (-1, 1):
            pairs = [i for i in pos if i + d in P]
            for a in range(1, 26):
                if np.gcd(a, 26) != 1: continue
                for b in range(26):
                    for c in range(26):
                        if all((a * P[i] + b * P[i + d] + c) % 26 == C[i] for i in pairs):
                            hits.append((T == KA, d, a, b, c, len(pairs)))
    return hits


def t4_forward_autokey():
    hits = []
    for T in (AZ, KA):
        for rule in range(3):
            req = tab_key_letters(T, rule)
            for lag in (1, 2, 3):
                checks = [(r, CRIB_POS[i + lag]) for i, r in zip(pos, req) if i + lag in CRIB_POS]
                for sh in range(26):
                    if all(T[(T.index(kl) + sh) % 26] == r for r, kl in checks):
                        hits.append((T == KA, rule, lag, sh, len(checks)))
    return hits


def t6_position_keys():
    hits = []
    fs = {}
    for m in range(2, 31):
        fs[f"i mod {m}"] = [i % m for i in range(97)]; fs[f"(i+1) mod {m}"] = [(i + 1) % m for i in range(97)]
        fs[f"i div {m}"] = [i // m for i in range(97)]
    fs["digitsum"] = [sum(map(int, str(i))) for i in range(97)]; fs["digitsum+1"] = [sum(map(int, str(i + 1))) for i in range(97)]
    fs["i*i"] = [i * i for i in range(97)]; fs["tri"] = [i * (i + 1) // 2 for i in range(97)]
    for T in (AZ, KA):
        for rule in range(3):
            req = [T.index(x) for x in tab_key_letters(T, rule)]
            for nm, f in fs.items():
                for sg in (1, -1):
                    for sh in range(26):
                        if all((sg * f[i] + sh) % 26 == r for i, r in zip(pos, req)):
                            hits.append((nm, sg, sh, T == KA, rule))
    return hits


if __name__ == "__main__":
    lore, words = load_words()
    allw = sorted(set(w for w in words + lore + NAMES if 3 <= len(w) <= 20))
    print("words+names:", len(allw))
    h1 = t1_slip(allw); print("T1 slipped key row:", len(h1), h1[:10], flush=True)
    h2 = t2_vertical(allw); print("T2 vertical/snake/diagonal key on 31-wide sheet:", len(h2), h2[:10], flush=True)
    h3 = t3_neighbour(); print("T3 neighbour mixing C=aP+bP(i±1)+c:", len(h3), h3[:10], flush=True)
    h4 = t4_forward_autokey(); print("T4 key = next PT letter:", len(h4), h4[:10], flush=True)
    h6 = t6_position_keys(); print("T6 position-number keys:", len(h6), h6[:10], flush=True)
    # T5 names as keyed alphabets vs AZ/KA periodic
    from perms import inverse
    from k4lib import to_idx
    out = np.zeros((1000, 5), dtype=np.int64); n5 = 0
    for nm in NAMES:
        for rev in (0, 1):
            a = keyed_alphabet(nm); a = a[::-1] if rev else a
            KV = np.zeros((2, 26, 26), dtype=np.int64)
            for P_ in range(26):
                for C_ in range(26):
                    KV[0, P_, C_] = (a.index(AZ[C_]) - a.index(AZ[P_])) % 26
                    KV[1, P_, C_] = (a.index(AZ[C_]) + a.index(AZ[P_])) % 26
            n5 += cf.check_batch(np.array([np.arange(97)]), 1, 24, KV, cf.CTI, cf.CRIB_I, cf.CRIB_L, 4, out)
    print("T5 name-keyed tableaus x periodic p1-24:", n5)
