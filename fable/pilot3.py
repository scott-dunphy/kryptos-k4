"""Pilot 3: (a) mask + keyword restarting at each copper line / sheet row (key index = column + phase);
(b) keyword PATTERN with arbitrary key alphabet (systematically misspelled key row), fixed AZ/KA PT & CT, 3 rules;
(c) two masks selected by column parity / checkerboard / i mod 3 + continuous keyword."""
import sys, itertools, numpy as np
sys.path.insert(0, "/Users/scottdunphy/PycharmProjects/K4")
from k4lib import CT, CRIB_POS, AZ, KA
exec(open(sys.argv[0].replace("pilot3.py", "pilot_common.py")).read())

def run_mask_keyword(colfun, same, diff, tol, tag):
    col = np.array([colfun(int(p)) for p in pos]); hits = []
    for L, ws in sorted(bylen.items()):
        for ka in ("AZ", "KA"):
            W = np.array([[idx[ka][c] for c in w] for w in ws])
            for ph in range(L):
                K = W[:, (col + ph) % L]
                for ca in ("AZ", "KA"):
                    c = np.array([idx[ca][x] for x in C])
                    for rule, R in (("vig", (c - K) % 26), ("beau", (K - c) % 26)):
                        bad = (R[:, same[:, 0]] != R[:, same[:, 1]]).sum(1); inj = (R[:, diff[:, 0]] == R[:, diff[:, 1]]).sum(1)
                        for i in np.where(bad + inj <= tol)[0]: hits.append((int(bad[i]), int(inj[i]), ws[i], ph, ka, ca, rule))
    hits.sort(); print(tag, "hits:", len(hits), hits[:15]); return hits

# (a) per-line restart
copper_col = lambda i: (27 + i) if i < 4 else (i - 4) % 31
sheet_col = lambda i: i % 31
sheetq_col = lambda i: (i + 1) % 31
run_mask_keyword(copper_col, sameP, diffP, 2, "(a) copper-line restart, tol2")
run_mask_keyword(sheet_col, sameP, diffP, 2, "(a) sheet-row restart, tol2")
run_mask_keyword(sheetq_col, sameP, diffP, 2, "(a) sheet-row restart with ?, tol2")

# (b) keyword pattern, arbitrary key alphabet: positions sharing a key letter must share C-P (vig), C+P (beau) in the chosen alphabets
hits = []
for L, ws in sorted(bylen.items()):
    Wl = np.array([[ord(c) - 65 for c in w] for w in ws])
    for ph in range(L):
        KL = Wl[:, (pos + ph) % L]  # key letters (n,24)
        for pa in ("AZ", "KA"):
            for ca in ("AZ", "KA"):
                p = np.array([idx[pa][x] for x in P]); c = np.array([idx[ca][x] for x in C])
                for rule, V in (("vig", (c - p) % 26), ("beau", (c + p) % 26), ("var", (p - c) % 26)):
                    # for each row: for all pairs (i,j) with KL equal, V must be equal; distinct key letters -> V may differ (no injectivity needed for Vig)
                    eq = KL[:, :, None] == KL[:, None, :]
                    bad = (eq & (V[:, None] != V[None, :])).sum((1, 2)) // 2
                    chk = eq.sum((1, 2)) // 2 - 0  # pairs incl self: subtract 24 later
                    for i in np.where(bad == 0)[0]:
                        nchk = (eq[i].sum() - 24) // 2
                        if nchk >= 8: hits.append((int(nchk), ws[i], ph, pa, ca, rule))
hits.sort(reverse=True); print("(b) keyword pattern + arbitrary key alphabet, exact, >=8 checks:", len(hits), hits[:15])

# (c) selector masks + continuous keyword
def selector_pairs(sel):
    groups = {}
    for i, ch in enumerate(P): groups.setdefault((ch, sel(int(pos[i]))), []).append(i)
    same = [(g[0], j) for g in groups.values() for j in g[1:]]
    reps = {}
    for (ch, s), g in groups.items(): reps.setdefault(s, []).append(g[0])
    diff = [(a, b) for r in reps.values() for a, b in itertools.combinations(r, 2)]
    return np.array(same), np.array(diff)
for name, sel in [("copper col parity", lambda i: copper_col(i) % 2), ("sheet col parity", lambda i: sheet_col(i) % 2),
                  ("i parity", lambda i: i % 2), ("i mod 3", lambda i: i % 3),
                  ("copper checkerboard", lambda i: (copper_col(i) + (25 if i < 4 else 25 + (i - 4) // 31)) % 2)]:
    same, diff = selector_pairs(sel)
    print("(c)", name, "checks", len(same))
    run_mask_keyword(lambda i: i, same, diff, 0, f"(c) {name} two masks + keyword, exact")
