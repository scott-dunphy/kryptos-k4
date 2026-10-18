"""Pilot for the 1989-letter brief: arbitrary mask (unknown substitution) + K1/K2-style
keyword key row on the AZ/KA table (Vig/Beau), mask on PT side or CT side.
Also: mask + key read off the carved tableau (overlay / flat) and a few sanity facts.
Exact union-find-free formulation: residual r_i must be a function of P_i (PT-side mask)
or of C_i (CT-side mask) and injective. Reports configs with <= TOL disagreements.
"""
import sys, numpy as np, itertools, random
sys.path.insert(0, "/Users/scottdunphy/PycharmProjects/K4")
from k4lib import CT, CRIB_POS, AZ, KA

TOL = int(sys.argv[1]) if len(sys.argv) > 1 else 2
pos = np.array(sorted(CRIB_POS)); P = "".join(CRIB_POS[p] for p in pos); C = "".join(CT[p] for p in pos)
alph = {"AZ": AZ, "KA": KA}
idx = {n: {c: i for i, c in enumerate(a)} for n, a in alph.items()}

def pairs(letters):
    """spanning same-letter pairs (checks) and cross-group pairs (injectivity)"""
    groups = {}
    for i, c in enumerate(letters): groups.setdefault(c, []).append(i)
    same = [(g[0], j) for g in groups.values() for j in g[1:]]
    reps = [g[0] for g in groups.values()]
    diff = list(itertools.combinations(reps, 2))
    return np.array(same), np.array(diff)

sameP, diffP = pairs(P); sameC, diffC = pairs(C)
print("cribs", len(pos), "distinct P", len(set(P)), "checks", len(sameP), "| distinct C", len(set(C)), "checks", len(sameC))

# ---- sanity facts
print("self-enc:", [(int(p), P[i], C[i]) for i, p in enumerate(pos) if P[i] == C[i]])
print("42-apart collisions:", [(int(a), int(b), P[list(pos).index(a)], P[list(pos).index(b)], C[list(pos).index(a)]) for a in pos for b in pos if b - a == 42 and C[list(pos).index(a)] == C[list(pos).index(b)]])
# W=42 grid key C = P + a_col + b_row additive (either sign): rows differ by const for both pairs?
for name, f in [("vig", lambda p, c: (c - p) % 26), ("beau", lambda p, c: (c + p) % 26)]:
    d = []
    for a in pos:
        if a + 42 in CRIB_POS:
            i, j = list(pos).index(a), list(pos).index(a + 42)
            d.append((int(a), (f(idx["AZ"][P[j]], idx["AZ"][C[j]]) - f(idx["AZ"][P[i]], idx["AZ"][C[i]])) % 26))
    print("W=42 row+col additive key,", name, ": row-difference implied by each 42-pair:", d, "-> consistent" if len({x for _, x in d}) == 1 else "-> CONTRADICTION")

def score(R, side):
    """R: (n,24) residuals. returns (#check disagreements, #injectivity violations)"""
    same, diff = (sameP, diffP) if side == "PT" else (sameC, diffC)
    bad = (R[:, same[:, 0]] != R[:, same[:, 1]]).sum(1)
    inj = (R[:, diff[:, 0]] == R[:, diff[:, 1]]).sum(1)
    return bad, inj

def residuals(K, ka, ca, rule, side):
    """K: (n,24) key indices. side PT: r = idx_ca(C) -/+ k ; side CT: r = idx_pa(P) +/- k"""
    if side == "PT":
        c = np.array([idx[ca][x] for x in C])
        return (c - K) % 26 if rule == "vig" else (K - c) % 26
    else:
        p = np.array([idx[ca][x] for x in P])
        return (p + K) % 26 if rule == "vig" else (K - p) % 26

def test_keys(K, label, ka, tag):
    hits = []
    for ca in alph:
        for rule in ("vig", "beau"):
            for side in ("PT", "CT"):
                R = residuals(K, ka, ca, rule, side)
                bad, inj = score(R, side)
                tot = bad + inj
                w = np.where(tot <= TOL)[0]
                for i in w: hits.append((int(bad[i]), int(inj[i]), ca, rule, side, label(i), tag))
    return hits

# ---- T1: dictionary keyword key rows, continuous, all phases
lore = ("KRYPTOS PALIMPSEST PALIMPCEST ABSCISSA IQLUSION UNDERGRUUND UNDERGROUND BERLIN CLOCK WELTZEITUHR MENGENLEHREUHR "
        "ALEXANDERPLATZ SANBORN SCHEIDT WEBSTER LANGLEY SHADOW CARTER TUTANKHAMUN EGYPT CAIRO BERLINWALL WORLDCLOCK URANIA "
        "LAYERTWO VIRGINIA MESSAGE DELIVER COMPASS LODESTONE ANTIPODES HIRSHHORN MAGNETIC NORTHEAST EASTNORTHEAST TIME ZEIT "
        "WELT UHR HOUR LUCID MEMORY INVISIBLE SECRET TOMB CANDLE MIST SLOWLY DESPERATELY DESPARATLY BERLINCLOCK VIRTUALLY "
        "DIGETAL DIGITAL INTERPRETATION SHADOWFORCES LUCIDMEMORY POSITION SOS WILLIAMWEBSTER EDWARDSCHEIDT JIMSANBORN").split()
words = set(lore)
for fn in ("/usr/share/dict/words", "/usr/share/dict/web2", "/usr/share/dict/propernames"):
    try:
        for w in open(fn):
            w = w.strip().upper()
            if 3 <= len(w) <= 26 and w.isalpha() and w.isascii(): words.add(w)
    except FileNotFoundError: pass
words = sorted(words)
print("words", len(words))
bylen = {}
for w in words: bylen.setdefault(len(w), []).append(w)

# planted self-test: random mask on PT then KA-Vig with SHADOW
rng = random.Random(1); perm = list(range(26)); rng.shuffle(perm)
def plant(word, ka="KA", rule="vig"):
    k = [idx[ka][word[i % len(word)]] for i in pos]
    return "".join(alph["KA"][(perm[idx["AZ"][P[j]]] + k[j]) % 26] for j in range(len(pos)))
Cplant = plant("SHADOW")

hits = []
for L, ws in sorted(bylen.items()):
    W = np.array([[idx["AZ"][c] for c in w] for w in ws]); WK = np.array([[idx["KA"][c] for c in w] for w in ws])
    for ph in range(L):
        cols = (pos + ph) % L
        for ka, Wa in (("AZ", W), ("KA", WK)):
            K = Wa[:, cols]
            hits += test_keys(K, lambda i, ws=ws, ph=ph, L=L: f"{ws[i]} ph{ph}", ka, "T1")
            # planted check once
            if L == 6 and ph == 0 and ka == "KA":
                Csave = C; C = Cplant
                h = test_keys(K, lambda i, ws=ws: ws[i], ka, "PLANT")
                C = Csave
                print("planted SHADOW/KA/vig/PT-mask recovered:", [x for x in h if x[5] == "SHADOW"][:2])
hits.sort()
print("T1 hits (bad,inj,ctalpha,rule,side,key):", len(hits))
for h in hits[:40]: print("  ", h)

# ---- T2: key read off the carved tableau (overlay addressing and flat reading)
right = [l.rstrip("\n") for l in open("/Users/scottdunphy/PycharmProjects/K4/data/sculpture_right.txt")]
flat = "".join(ch for l in right for ch in l if ch.isalpha())
print("tableau rows", len(right), "letters", len(flat))
layouts = {"copper": [(24, 27 + i) if i < 4 else (25 + (i - 4) // 31, (i - 4) % 31) for i in range(97)],
           "sheet": [(i // 31, i % 31) for i in range(97)],
           "sheetQ": [((i + 1) // 31, (i + 1) % 31) for i in range(97)]}
keys2 = []
for lname, lay in layouts.items():
    for dr in range(-27, 28):
        for dc in range(-8, 9):
            k = []
            ok = True
            for p in pos:
                r, c = lay[p]; r += dr; c += dc
                if 0 <= r < len(right) and 0 <= c < len(right[r]) and right[r][c].isalpha(): k.append(right[r][c])
                else: ok = False; break
            if ok: keys2.append((f"{lname} dr{dr} dc{dc}", "".join(k)))
for off in range(len(flat)):
    for d, s in (("fwd", flat), ("rev", flat[::-1])):
        if off + 97 <= len(s): keys2.append((f"flat {d} off{off}", "".join(s[off + p] for p in pos)))
# tableau rows as per-line keys: K4 line j (copper rows 24-27) keyed by tableau row r_j, column = copper column
print("T2 keys", len(keys2))
hits2 = []
for ka in alph:
    K = np.array([[idx[ka][c] for c in k] for _, k in keys2])
    hits2 += test_keys(K, lambda i: keys2[i][0], ka, "T2")
hits2.sort()
print("T2 hits:", len(hits2))
for h in hits2[:20]: print("  ", h)
# null calibration for T2: random keys
Kn = np.random.default_rng(0).integers(0, 26, (200000, 24))
hn = test_keys(Kn, lambda i: i, "AZ", "NULL")
print("null: random 24-letter keys x 8 configs:", 200000 * 8, "tests ->", len(hn), "with <=TOL")
