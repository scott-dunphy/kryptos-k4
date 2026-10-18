"""Two separate ciphers on two parts of K4 (Fable test 3) + M1 letter-class consistency null (Fable test 2).
Test 3: part A = positions [0, B), part B = [B, 97) for every boundary B in 34..63 (plus copper rows as parts).
 Each part: own periodic key, period p 1..12, restarting at part start; alphabets: AZ, KA, lore-keyed (both roles),
 Vig/Beau/Var. Check residue consistency within each part's cribs; record parts with >=4 checks passing.
 Success needs BOTH parts consistent (each with >=4 checks) under some (possibly different) setting.
Test 2: M1: KRYPTOS-PT letters need |k|<=w; other PT letters: all occurrences of same letter within a window 2w+1.
 Count failures; null shuffled CT.
"""
import numpy as np
from k4lib import CT, CRIB_POS, AZ, KA, keyed_alphabet
import cribfilter as cf

pos = sorted(CRIB_POS)
LORE = ["", "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW", "LUCID", "EGYPT", "WELTZEITUHR",
        "ALEXANDERPLATZ", "SANBORN", "SCHEIDT", "LAYERTWO", "EQUAL", "COMPASS", "LODESTONE", "NORTHEAST"]
ALPHS = []
for w in LORE:
    a = keyed_alphabet(w)
    ALPHS += [a, a[::-1]]


def keyvals(ct, pa, ca, rule):
    out = {}
    for i in pos:
        ip = pa.index(CRIB_POS[i]); ic = ca.index(ct[i])
        out[i] = (ic - ip) % 26 if rule == 0 else ((ic + ip) % 26 if rule == 1 else (ip - ic) % 26)
    return out


def part_ok(kv, idxs, start, p):
    seen = {}; checks = 0
    for i in idxs:
        r = (i - start) % p
        if r in seen:
            checks += 1
            if seen[r] != kv[i]:
                return False, checks
        else:
            seen[r] = kv[i]
    return True, checks


def test3(ct):
    hits = []
    combos = [(pa, ca, rule) for pa in ALPHS for ca in (AZ, KA, *ALPHS[:4]) for rule in range(3)]
    kvs = [keyvals(ct, *c) for c in combos]
    parts_sets = [(f"B={B}", [(0, [i for i in pos if i < B]), (B, [i for i in pos if i >= B])]) for B in range(34, 64)]
    parts_sets.append(("copper rows", [(4, [i for i in pos if 4 <= i < 35]), (35, [i for i in pos if 35 <= i < 66]),
                                       (66, [i for i in pos if i >= 66])]))
    for pname, parts in parts_sets:
        part_good = []
        for start, idxs in parts:
            good = []
            for ci, kv in enumerate(kvs):
                for p in range(1, 13):
                    ok, checks = part_ok(kv, idxs, start, p)
                    if ok and checks >= 4:
                        good.append((ci, p, checks))
            part_good.append(good)
        if all(len(g) > 0 for g in part_good if True) and all(
                any(True for _ in g) for g in part_good):
            hits.append((pname, [len(g) for g in part_good]))
    return hits


def test2(ct, w):
    k = {i: ((ord(ct[i]) - ord(CRIB_POS[i])) % 26 + 13) % 26 - 13 for i in pos}
    fails = 0
    byletter = {}
    for i in pos:
        L = CRIB_POS[i]
        if L in "KRYPTOS":
            if abs(k[i]) > w:
                fails += 1
        else:
            byletter.setdefault(L, []).append(k[i])
    for L, ks in byletter.items():
        if len(ks) < 2:
            continue
        # circular window check
        ok = any(all(((x - c + 13) % 26 - 13) in range(-w, w + 1) for x in ks) for c in range(26))
        if not ok:
            fails += 1
    return fails


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    real3 = test3(CT)
    print("T3 two-part periodic: partitions where EVERY part has a consistent setting (>=4 checks):", real3)
    nulls = []
    for _ in range(20):
        sh = "".join(rng.permutation(list(CT)))
        nulls.append(len(test3(sh)))
    print("T3 null (20 shuffled CTs) count of such partitions:", nulls)
    for w in (2, 3, 4):
        r = test2(CT, w)
        nl = np.array([test2("".join(rng.permutation(list(CT))), w) for _ in range(20000)])
        print(f"T2 M1 letter-class w={w}: real failures {r}; null P(fail<=real)={(nl <= r).mean():.4f} (null mean {nl.mean():.2f})")
