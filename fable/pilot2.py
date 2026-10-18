"""Pilot 2: (i) mask + keyword consistent with EASTNORTHEAST alone (K4 'partly by the table' = line 25 only);
(ii) mask + sum of two lore keywords; (iii) mask + numeric lore digit strings as Gronsfeld keys;
(iv) per-copper-line masks + one continuous keyword."""
import sys, itertools, numpy as np
sys.path.insert(0, "/Users/scottdunphy/PycharmProjects/K4")
from k4lib import CT, CRIB_POS, AZ, KA
exec(open(sys.argv[0].replace("pilot2.py", "pilot_common.py")).read())

# (i) crib-1 only
pos1 = [p for p in pos if p < 40]; sel1 = np.array([list(pos).index(p) for p in pos1])
P1 = "".join(P[i] for i in sel1); C1 = "".join(C[i] for i in sel1)
same1, diff1 = pairs(P1)
print("(i) crib1 only: checks", len(same1))
hits = []
for L, ws in sorted(bylen.items()):
    for ka in ("AZ", "KA"):
        W = np.array([[idx[ka][c] for c in w] for w in ws])
        for ph in range(L):
            K = W[:, (np.array(pos1) + ph) % L]
            for ca in ("AZ", "KA"):
                c = np.array([idx[ca][x] for x in C1])
                for rule, R in (("vig", (c - K) % 26), ("beau", (K - c) % 26)):
                    bad = (R[:, same1[:, 0]] != R[:, same1[:, 1]]).sum(1); inj = (R[:, diff1[:, 0]] == R[:, diff1[:, 1]]).sum(1)
                    w = np.where(bad + inj == 0)[0]
                    for i in w: hits.append((ws[i], ph, ka, ca, rule))
print("(i) exact hits (mask on PT side, crib 1 only):", len(hits), hits[:30])
# null: shuffled C1 letters
rng = np.random.default_rng(1); nulls = []
for t in range(3):
    Cn = "".join(rng.permutation(list(C1))); cnt = 0
    for L, ws in sorted(bylen.items()):
        W = np.array([[idx["AZ"][c] for c in w] for w in ws])
        for ph in range(L):
            K = W[:, (np.array(pos1) + ph) % L]; c = np.array([idx["AZ"][x] for x in Cn])
            for R in ((c - K) % 26, (K - c) % 26):
                bad = (R[:, same1[:, 0]] != R[:, same1[:, 1]]).sum(1); inj = (R[:, diff1[:, 0]] == R[:, diff1[:, 1]]).sum(1)
                cnt += int((bad + inj == 0).sum())
    nulls.append(cnt)
print("(i) null (shuffled crib-1 CT, AZ only, 2 rules):", nulls)

# (ii) two lore keywords summed, mask on PT side, both cribs
L2 = sorted(set(lore)); hits2 = []
for a, b in itertools.product(L2, repeat=2):
    for ka in ("AZ", "KA"):
        ka_ = [idx[ka][ch] for ch in a]; kb_ = [idx[ka][ch] for ch in b]
        for pa in range(len(a)):
            Ka = np.array([ka_[(p + pa) % len(a)] for p in pos])
            for pb in range(len(b)):
                Kb = np.array([kb_[(p + pb) % len(b)] for p in pos])
                for sgn in (1, -1):
                    K = (Ka + sgn * Kb) % 26
                    for ca in ("AZ", "KA"):
                        c = np.array([idx[ca][x] for x in C])
                        for R in ((c - K) % 26, (K - c) % 26):
                            bad = (R[sameP[:, 0]] != R[sameP[:, 1]]).sum(); inj = (R[diffP[:, 0]] == R[diffP[:, 1]]).sum()
                            if bad + inj <= 1: hits2.append((a, pa, b, pb, sgn, ka, ca, int(bad), int(inj)))
print("(ii) two summed lore keywords + mask, <=1 bad:", len(hits2), hits2[:10])

# (iii) numeric strings as Gronsfeld digit keys + mask (digits add to masked letter), periodic, all phases, both signs
nums = ["3857650778844", "385765778844", "38576577844", "3857657784", "19891109", "19901103", "1989", "1990", "1986", "1988", "11091989", "09111989",
        "03111990", "9111989", "97", "31", "26", "42", "1570", "3141592653589793", "2718281828459045", "1414213562", "1618033988", "20200111", "20181231",
        "131", "13", "243", "2437", "0352", "012345678901234567890123456789", "1234567890", "0987654321", "386", "1735", "865", "867", "869", "2000"]
hits3 = []
for s in nums:
    d = [int(ch) for ch in s]; L = len(d)
    for ph in range(L):
        K = np.array([d[(p + ph) % L] for p in pos])
        for sgn in (1, -1):
            for ca in ("AZ", "KA"):
                c = np.array([idx[ca][x] for x in C]); R = (c - sgn * K) % 26
                bad = (R[sameP[:, 0]] != R[sameP[:, 1]]).sum(); inj = (R[diffP[:, 0]] == R[diffP[:, 1]]).sum()
                if bad + inj <= 1: hits3.append((s, ph, sgn, ca, int(bad), int(inj)))
print("(iii) numeric Gronsfeld + mask, <=1 bad:", len(hits3), hits3[:10])
# zero-parameter bound for any digit key 0..9 + mask: same-letter CT differences must be within +-9
diffs = [(P[i], int(pos[i]), int(pos[j]), (idx["AZ"][C[i]] - idx["AZ"][C[j]] + 13) % 26 - 13) for i, j in sameP]
print("(iii) same-PT-letter CT differences (need |d|<=9 for any 0-9 digit key with mask):", diffs)

# (iv) per-copper-line masks (line of pos: 25 for 4..34, 26 for 35..65, 27 for 66..96) + one continuous keyword
line = {int(p): (25 if p < 35 else 26 if p < 66 else 27) for p in pos}
same4 = np.array([(i, j) for i, j in sameP if line[int(pos[i])] == line[int(pos[j])]])
groups = {}
for i, ch in enumerate(P): groups.setdefault((ch, line[int(pos[i])]), []).append(i)
reps = {}
for (ch, ln), g in groups.items(): reps.setdefault(ln, []).append(g[0])
diff4 = np.array([(a, b) for ln, r in reps.items() for a, b in itertools.combinations(r, 2)])
print("(iv) per-line masks: checks", len(same4), "inj pairs", len(diff4))
hits4 = []
for L, ws in sorted(bylen.items()):
    for ka in ("AZ", "KA"):
        W = np.array([[idx[ka][c] for c in w] for w in ws])
        for ph in range(L):
            K = W[:, (pos + ph) % L]
            for ca in ("AZ", "KA"):
                c = np.array([idx[ca][x] for x in C])
                for rule, R in (("vig", (c - K) % 26), ("beau", (K - c) % 26)):
                    bad = (R[:, same4[:, 0]] != R[:, same4[:, 1]]).sum(1); inj = (R[:, diff4[:, 0]] == R[:, diff4[:, 1]]).sum(1)
                    w = np.where(bad + inj == 0)[0]
                    for i in w: hits4.append((ws[i], ph, ka, ca, rule))
print("(iv) per-line masks + keyword, exact:", len(hits4), hits4[:30])
