"""S13 (lead task): digit-encoded PT + structured pad mod 10.
PT letter -> 2-digit code (tables: keyed linear 00-25 / 01-26 = 'keyed 10x10' with letters in first cells; keyed
6x6 Polybius rows/cols 0-5 or 1-6, letters then digits), cipher digits = code + s*pad (s=+1/-1) digit-wise mod 10,
CT letter = table^-1(cipher code). Requirement: 24 cribs exact AND all 97 decrypted PT codes valid.
Pads: (a) general periodic digit pad q=1..60 (subsumes lore digit strings 385765/77844/19891109/19901103/1986 and
keyword-rank digits, any phase); (b) chain addition base 10 pad[n]=pad[n-L]+pad[n-L+k], L=2..20, k=1..L-1, ANY primer
(solved linearly mod 2 and mod 5; offset-invariant since the recurrence is invertible); (c) clock digit streams
(results/clock_streams_for_anneal.json, values mod 10 and decimal-digit expansion), all cyclic offsets, fwd/rev.
Null: same pipeline on shuffled CT."""
import json, itertools, sys, time
from common import *
from k4lib import keyed_alphabet, CRIB_POS
from run_alphapairs import load_words
from twolayer import STEGO

CI = np.array(sorted(CRIB_POS)); PLt = [CRIB_POS[i] for i in CI]

def tables():
    lore, _ = load_words()
    words = [""] + sorted(set(lore) | set(STEGO))
    out = []
    seen = set()
    for w in words:
        al = keyed_alphabet(w)
        for rev in (0, 1):
            a = al[::-1] if rev else al
            if a in seen: continue
            seen.add(a)
            name = (w or "AZ") + ("~rev" if rev else "")
            for lay in ("lin0", "lin1", "poly0", "poly1"):
                code = {}
                for i, ch in enumerate(a):
                    if lay == "lin0": code[ch] = (i // 10, i % 10)
                    elif lay == "lin1": code[ch] = ((i + 1) // 10, (i + 1) % 10)
                    elif lay == "poly0": code[ch] = (i // 6, i % 6)
                    else: code[ch] = (i // 6 + 1, i % 6 + 1)
                out.append((name + "/" + lay, code))
    return out

def prep(code, ct, sign):
    """Return pinned pad digits (dict digit_pos -> value), code arrays of CT (194), valid mask table 10x10."""
    cd = np.array([d for ch in ct for d in code[ch]])
    valid = np.zeros((10, 10), dtype=bool)
    for (a, b) in code.values(): valid[a, b] = True
    pin = {}
    for i, p in zip(CI, PLt):
        for k in range(2):
            # c = p + s*pad  -> pad = s*(c - p)
            pin[2 * i + k] = (sign * (cd[2 * i + k] - code[p][k])) % 10
    return pin, cd, valid

def check_full(pad, cd, valid, sign):
    pt = (cd - sign * pad) % 10
    return bool(valid[pt[0::2], pt[1::2]].all())

# ---------- (a) periodic ----------
def periodic(code, ct, sign, qmax=60):
    pin, cd, valid = prep(code, ct, sign)
    hits = []
    for q in range(1, qmax + 1):
        res = {}
        ok = True
        for pos, v in pin.items():
            r = pos % q
            if res.setdefault(r, v) != v: ok = False; break
        if not ok: continue
        # CSP over free residues: each PT code (2 digits at 2i,2i+1) must be valid
        free = [r for r in range(q) if r not in res]
        pad = np.array([res.get(j % q, -1) for j in range(194)])
        # quick pinned validity
        bad = False
        for i in range(97):
            a, b = pad[2 * i], pad[2 * i + 1]
            if a >= 0 and b >= 0 and not valid[(cd[2*i] - sign*a) % 10, (cd[2*i+1] - sign*b) % 10]:
                bad = True; break
        if bad: continue
        # per free residue: domain filtering by arc consistency, then brute if small
        dom = {r: set(range(10)) for r in free}
        changed = True
        while changed:
            changed = False
            for i in range(97):
                r1, r2 = (2 * i) % q, (2 * i + 1) % q
                d1 = dom.get(r1, {res.get(r1)}); d2 = dom.get(r2, {res.get(r2)})
                if r1 == r2:
                    n1 = {x for x in d1 if valid[(cd[2*i]-sign*x) % 10, (cd[2*i+1]-sign*x) % 10]}; n2 = n1
                else:
                    n1 = {x for x in d1 if any(valid[(cd[2*i]-sign*x) % 10, (cd[2*i+1]-sign*y) % 10] for y in d2)}
                    n2 = {y for y in d2 if any(valid[(cd[2*i]-sign*x) % 10, (cd[2*i+1]-sign*y) % 10] for x in n1)}
                for r, n, d in ((r1, n1, d1), (r2, n2, d2)):
                    if r in dom and n != dom[r]:
                        dom[r] = n; changed = True
                if not n1 or not n2: break
            if any(len(d) == 0 for d in dom.values()): break
        if any(len(d) == 0 for d in dom.values()): continue
        hits.append((q, {r: sorted(d) for r, d in dom.items()}))
    return hits

# ---------- (b) chain addition, any primer ----------
def gen_matrix(L, k, n=194):
    G = np.zeros((n, L), dtype=np.int64)
    for j in range(L): G[j, j] = 1
    for j in range(L, n): G[j] = G[j - L] + G[j - L + k]
    return G

def solve_mod(A, b, p):
    A = A.copy() % p; b = b.copy() % p
    m, n = A.shape; row = 0; piv = []
    for c in range(n):
        r = next((r for r in range(row, m) if A[r, c] % p), None)
        if r is None: continue
        A[[row, r]] = A[[r, row]]; b[[row, r]] = b[[r, row]]
        inv = pow(int(A[row, c]), -1, p)
        A[row] = A[row] * inv % p; b[row] = b[row] * inv % p
        for r2 in range(m):
            if r2 != row and A[r2, c]:
                f = A[r2, c]; A[r2] = (A[r2] - f * A[row]) % p; b[r2] = (b[r2] - f * b[row]) % p
        piv.append(c); row += 1
        if row == m: break
    if any(b[r] % p for r in range(row, m)): return None
    free = [c for c in range(n) if c not in piv]
    x0 = np.zeros(n, dtype=np.int64)
    for i, c in enumerate(piv): x0[c] = b[i]
    basis = []
    for f in free:
        v = np.zeros(n, dtype=np.int64); v[f] = 1
        for i, c in enumerate(piv): v[c] = (-A[i, f]) % p
        basis.append(v)
    return x0, basis

def chain(code, ct, sign, Gs, cap=200000):
    pin, cd, valid = prep(code, ct, sign)
    rows = sorted(pin); bvec = np.array([pin[r] for r in rows])
    hits = []; nsol_total = 0
    for (L, k), G in Gs.items():
        A = G[rows]
        s2 = solve_mod(A, bvec, 2)
        if s2 is None: continue
        s5 = solve_mod(A, bvec, 5)
        if s5 is None: continue
        n2, n5 = len(s2[1]), len(s5[1])
        cnt = 2 ** n2 * 5 ** n5
        nsol_total += cnt
        if cnt > cap:
            hits.append(("CAP", L, k, cnt)); continue
        sols2 = [(s2[0] + sum(c * v for c, v in zip(cs, s2[1]))) % 2 for cs in itertools.product(range(2), repeat=n2)]
        sols5 = [(s5[0] + sum(c * v for c, v in zip(cs, s5[1]))) % 5 for cs in itertools.product(range(5), repeat=n5)]
        for a in sols2:
            for b in sols5:
                prim = (5 * a + 6 * b) % 10
                pad = (G @ prim) % 10
                if check_full(pad, cd, valid, sign):
                    hits.append(("HIT", L, k, "".join(map(str, prim))))
    return hits, nsol_total

# ---------- (c) fixed streams ----------
def clock_streams():
    d = json.load(open(os.path.join(HERE, "results", "clock_streams_for_anneal.json")))
    for name, v in d.items():
        v = [int(x) for x in v]
        yield name + "/mod10", np.array(v) % 10
        yield name + "/digits", np.array([int(c) for x in v for c in str(abs(x))])
    for s in ("385765", "77844", "3857657784", "385765577844", "19891109", "19901103", "1986", "11091989", "09111989",
              "1986198911", "38576577844"):
        yield "lore " + s, np.array([int(c) for c in s])

def fixed(code, ct, sign, streams):
    pin, cd, valid = prep(code, ct, sign)
    rows = np.array(sorted(pin)); want = np.array([pin[r] for r in rows])
    hits = []
    for name, S in streams:
        for dr in (0, 1):
            T = S[::-1] if dr else S
            E = np.concatenate([T] * (194 // len(T) + 2))
            for o in range(len(T)):
                if np.array_equal(E[o + rows], want):
                    pad = E[o:o + 194]
                    hits.append((name, dr, o, check_full(pad, cd, valid, sign)))
    return hits

if __name__ == "__main__":
    t0 = time.time()
    TB = tables(); print("tables", len(TB), flush=True)
    Gs = {(L, k): gen_matrix(L, k) for L in range(2, 21) for k in range(1, L)}
    streams = list(clock_streams())
    which = sys.argv[1] if len(sys.argv) > 1 else "real"
    rng = np.random.default_rng(11)
    cts = [("real", CT)] if which == "real" else [(f"null{j}", "".join(rng.permutation(list(CT)))) for j in range(int(which))]
    for cname, ct in cts:
        np_, nc, nf, ncap, nsol = 0, 0, 0, 0, 0
        for tname, code in TB:
            for sign in (1, -1):
                ph = periodic(code, ct, sign)
                for q, dom in ph:
                    np_ += 1
                    if cname == "real": print("PERIODIC", tname, sign, q, {r: d for r, d in list(dom.items())[:8]}, flush=True)
                ch, ns = chain(code, ct, sign, Gs); nsol += ns
                for h in ch:
                    if h[0] == "CAP": ncap += 1
                    else:
                        nc += 1
                        if cname == "real": print("CHAIN", tname, sign, h, flush=True)
                for h in fixed(code, ct, sign, streams):
                    nf += 1
                    if cname == "real": print("FIXED", tname, sign, h, flush=True)
        print(cname, "periodic", np_, "chain", nc, "chain-capped", ncap, "chain-solutions-tested", nsol, "fixed", nf,
              round(time.time() - t0, 1), flush=True)
