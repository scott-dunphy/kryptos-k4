import sys, re, collections
sys.path.insert(0, "/Users/scottdunphy/PycharmProjects/K4")
from k4lib import CT, CRIB_POS, AZ, KA
ka = lambda c: KA.index(c)
def Z(P, k, tab, rule):
    A = KA if tab == "KA" else AZ; x, y = A.index(P), A.index(k)
    return A[[(x + y) % 26, (y - x) % 26, (x - y) % 26][rule]]
def cls(i, lay): return (((i + (1 if lay == "col1" else 0)) % 31) % 4)
hits = []
for line in open("results/selector_mask_detail.log"):
    m = re.match(r"\s+(\w+) ph(\d+) (KA|AZ) (vig|beau|var) table>mask (col[01]) c%4 ch=4", line)
    if m: hits.append((m[1], int(m[2]), m[3], ["vig", "beau", "var"].index(m[4]), m[5]))
pairsets = collections.Counter()
for w, f, tab, rule, lay in hits:
    seen = {}; checks = []
    for i in sorted(CRIB_POS):
        z = Z(CRIB_POS[i], w[(i + f) % len(w)], tab, rule); key = (cls(i, lay), z)
        if key in seen: checks.append((seen[key], i))
        else: seen[key] = i
    pairsets[tuple(checks)] += 1
for ps, n in pairsets.most_common(6):
    print(n, "hits use pairs", [(a, b, CRIB_POS[a] + "/" + CRIB_POS[b], CT[a] + CT[b]) for a, b in ps])
# CT-side structure: equal-CT crib pairs that fall in the same column-mod-4 class, real vs shuffles
import random
def stat(ct, lay):
    pos = sorted(CRIB_POS); n = 0
    for a in range(len(pos)):
        for b in range(a + 1, len(pos)):
            i, j = pos[a], pos[b]
            if ct[i] == ct[j] and cls(i, lay) == cls(j, lay): n += 1
    return n
for lay in ("col0", "col1"):
    real = stat(CT, lay); rng = random.Random(1); cl = list(CT); vals = []
    for _ in range(20000):
        rng.shuffle(cl); vals.append(stat(cl, lay))
    ge = sum(v >= real for v in vals) / len(vals)
    print(lay, "equal-CT crib pairs in the same column-mod-4 class: real", real, "shuffle mean %.2f" % (sum(vals) / len(vals)), "P(>=real) %.4f" % ge)
pos = sorted(CRIB_POS)
print("equal-CT crib pairs (i,j,diff):", [(i, j, j - i, CT[i]) for a, i in enumerate(pos) for j in pos[a + 1:] if CT[i] == CT[j]])
