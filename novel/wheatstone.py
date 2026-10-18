"""Wheatstone/Wadsworth cryptograph ("cipher clock"): outer ring N_o cells (plain A-Z + blanks), inner ring 26 mixed letters (FREE),
two geared hands; long hand always moves clockwise to the next letter on the outer ring (full turn if same cell),
S = cumulative steps; inner letter = inner[(S + o) mod 26].
Mode PT-outer: S increments from consecutive PT letters (known only inside cribs) -> relative inner positions of CT letters
  per crib (two unknown offsets). Mode CT-outer: increments from consecutive CT letters (known everywhere) -> inner positions
  of PT letters known up to ONE global offset. Union-find + injectivity on the free inner alphabet. Outer alphabets: AZ, KA, + reversals."""
import sys
import numpy as np
sys.path.insert(0, '.')
from k4lib import CT, CRIB_POS, AZ, KA

def find(par, off, x):
    o = 0
    while par[x] != x:
        o += off[x]; x = par[x]
    return x, o % 26

def uf_test(cons):
    """cons: list of (letter, position) meaning inner[pos] = letter, with positions relative within groups:
    list of groups; each group is list of (letter, relpos). Different groups have independent offsets."""
    par = list(range(26)); off = [0] * 26
    for g in cons:
        a0, p0 = g[0]
        for a, p in g[1:]:
            k = (p - p0) % 26  # pos(a) - pos(a0) = k
            ra, oa = find(par, off, a0); rb, ob = find(par, off, a)
            if ra == rb:
                if (ob - oa - k) % 26: return False
            else:
                par[rb] = ra; off[rb] = (k + oa - ob) % 26
    seen = set()
    letters = {a for g in cons for a, _ in g}
    for x in letters:
        r, o = find(par, off, x)
        if (r, o) in seen: return False
        seen.add((r, o))
    return True

def outer_ring(alpha, No, blankpos):
    ring = [None] * No
    j = 0
    for c in range(No):
        if c in blankpos: continue
        ring[c] = alpha[j]; j += 1
    return {ch: i for i, ch in enumerate(ring) if ch}

def steps(seq, opos, No, start=0):
    S = [];
    cur = start; tot = 0
    for ch in seq:
        d = (opos[ch] - cur) % No
        if d == 0: d = No
        tot += d; cur = opos[ch]; S.append(tot)
    return S

def test(ct, No, opos, mode):
    cribs = [(21, "EASTNORTHEAST"), (63, "BERLINCLOCK")]
    if mode == 0:
        groups = []
        for s, w in cribs:
            S = steps(w, opos, No, start=opos[w[0]])  # relative: first letter step irrelevant
            groups.append([(ord(ct[s + j]) - 65, S[j]) for j in range(len(w))])
        return uf_test(groups)
    else:
        res = []
        for st in range(No):  # starting hand position
            S = steps(ct, opos, No, start=st)
            g = [(ord(CRIB_POS[i]) - 65, S[i]) for i in sorted(CRIB_POS)]
            if uf_test([g]): res.append(st)
        return res

if __name__ == '__main__':
    import random
    rnd = random.Random(0)
    ctl = [('REAL', CT)] + [('SHUF%d' % t, ''.join(rnd.sample(CT, 97))) for t in range(30)]
    for lab, ct in ctl:
        hits = []
        for an, al in (('AZ', AZ), ('KA', KA), ('AZr', AZ[::-1]), ('KAr', KA[::-1])):
            for No in range(27, 40):
                for bp in ({0}, {No - 1}, set(range(26, No)), set(range(0, No - 26))):
                    if len(bp) != No - 26: continue
                    opos = outer_ring(al, No, bp)
                    for mode in (0, 1):
                        r = test(ct, No, opos, mode)
                        if r: hits.append((an, No, min(bp), mode, r if mode else ''))
        if lab == 'REAL' or hits:
            print(lab, 'hits', len(hits), hits[:6])
