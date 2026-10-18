"""Fable 'artist' sigma generators, scored against cribs with small key.
Model: C_i = sigma(P_i) + k_i (AZ arithmetic), k_i in KSET. Score = # cribs satisfiable (24 total; also excl 64,71).
H1 slide: sigma_d(P) = S2[(S1.index(P) + d) % 26], S1,S2 in {AZ, KA, rev AZ, rev KA}; global d or per-copper-row d.
H2 stencil: 31- or 26-cell row, KRYPTOS letters fixed at their AZ cells, remaining 19 letters (AZ or KA order) written
   from start cell s in direction +/-, wrapping over W cells, skipping filled; sigma(P) = row[AZ.index(P)].
H3 dial: KRYPTOS pinned; the 19 other letters rotated r steps (in AZ order or KA order); also full-AZ rotation with
   KRYPTOS pinned.
Null: same family maxima on shuffled CT (non-crib + crib letters permuted).
"""
import numpy as np
from k4lib import CT, CRIB_POS, AZ, KA

pos = sorted(CRIB_POS)
P = np.array([AZ.index(CRIB_POS[i]) for i in pos])
ROW = np.array([(i + 27) // 31 for i in pos])          # copper row 1,2,3 (=25,26,27)
EXC = np.array([i not in (64, 71) for i in pos])
KRY = "KRYPTOS"
OTHERS_AZ = [c for c in AZ if c not in KRY]
OTHERS_KA = [c for c in KA if c not in KRY]


def sigmas():
    S = {"AZ": AZ, "KA": KA, "AZr": AZ[::-1], "KAr": KA[::-1]}
    for n1, s1 in S.items():
        for n2, s2 in S.items():
            for d in range(26):
                yield ("H1", n1, n2, d), np.array([AZ.index(s2[(s1.index(AZ[x]) + d) % 26]) for x in range(26)])
    for W in (26, 31):
        for order_name, others in (("AZ", OTHERS_AZ), ("KA", OTHERS_KA)):
            for s in range(W):
                for direc in (1, -1):
                    row = [None] * W
                    for c in KRY:
                        row[AZ.index(c)] = c
                    cell = s
                    for c in others:
                        guard = 0
                        while row[cell % W] is not None and guard < W:
                            cell += direc; guard += 1
                        row[cell % W] = c
                        cell += direc
                    sig = np.array([AZ.index(row[x]) if row[x] is not None else -1 for x in range(26)])
                    yield ("H2", W, order_name, s, direc), sig
    for order_name, others in (("AZ", OTHERS_AZ), ("KA", OTHERS_KA)):
        for r in range(19):
            sig = np.arange(26)
            for j, c in enumerate(others):
                sig[AZ.index(c)] = AZ.index(others[(j + r) % 19])
            yield ("H3", order_name, r), sig
    for r in range(26):
        sig = np.array([x if AZ[x] in KRY else (x + r) % 26 for x in range(26)])
        yield ("H3full", r), sig


SIGS = list(sigmas())


def score_all(cta, kset):
    C = cta[pos]
    best = {}
    for name, sig in SIGS:
        sp = sig[P]
        ok = np.array([(sp[t] >= 0) and (((C[t] - sp[t]) % 26) in kset) for t in range(24)])
        fam = name[0]
        best.setdefault(fam, [0, 0, None])
        a, b = int(ok.sum()), int(ok[EXC].sum())
        if (b, a) > (best[fam][1], best[fam][0]):
            best[fam] = [a, b, name]
    # H1 per-row: choose d per copper row independently (same S1,S2)
    S = {"AZ": AZ, "KA": KA, "AZr": AZ[::-1], "KAr": KA[::-1]}
    pr = [0, 0, None]
    for n1, s1 in S.items():
        for n2, s2 in S.items():
            tot = 0; tote = 0
            for rr in (1, 2, 3):
                m = ROW == rr
                bb = (0, 0)
                for d in range(26):
                    sig = np.array([AZ.index(s2[(s1.index(AZ[x]) + d) % 26]) for x in range(26)])
                    ok = np.array([((C[t] - sig[P[t]]) % 26) in kset for t in range(24)])
                    bb = max(bb, (int((ok & m & EXC).sum()), int((ok & m).sum())))
                tote += bb[0]; tot += bb[1]
            if (tote, tot) > (pr[1], pr[0]):
                pr = [tot, tote, (n1, n2)]
    best["H1perrow"] = pr
    return best


if __name__ == "__main__":
    cta = np.array([ord(c) - 65 for c in CT])
    rng = np.random.default_rng(0)
    for kset in ({0, 1, 2, 3, 4}, {24, 25, 0, 1, 2}):
        real = score_all(cta, kset)
        print("KSET", sorted(kset), "sigmas", len(SIGS))
        nulls = [score_all(rng.permutation(cta), kset) for _ in range(40)]
        for fam in real:
            nb = np.array([n[fam][1] for n in nulls])
            print(f"  {fam:9s} real best {real[fam][0]}/24 ({real[fam][1]}/22 excl 64,71) {real[fam][2]}  | null excl-best mean {nb.mean():.1f} max {nb.max()}  P(null>=real)={np.mean(nb >= real[fam][1]):.3f}", flush=True)
