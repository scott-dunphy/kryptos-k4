"""M-94 cylinder (US Army 1922-43) against K4 cribs.

Model: text split into lines of 25 starting at offset o (line = (i+o)//25, residue r = (i+o)%25).
Disk order sigma: residue -> disk (permutation of 25 disks, unknown). Each line uses generatrix g_line (0..25).
CT_i = D[sigma(r)][(pos_D(P_i) + g_line) % 26]   (decryption direction is the same model with -g).
For each offset o and each assignment of g to the crib-bearing lines: compat[r][d] = disk d satisfies all crib
constraints at residue r; then require an injective residue->disk matching (bipartite matching).
Null: shuffled CT and random disk sets.
"""
import itertools
import numpy as np
from k4lib import CT, CRIB_POS

DISKS = """ABCEIGDJFVUYMHTQKZOLRXSPWN ACDEHFIJKTLMOUVYGZNPQXRWSB ADKOMJUBGEPHSCZINXFYQRTVWL AEDCBIFGJHLKMRUOQVPTNWYXZS
AFNQUKDOPITJBRHCYSLWEMZVXG AGPOCIXLURNDYZHWBJSQFKVMET AHXJEZBNIKPVROGSYDULCFMQTW AIHPJOBWKCVFZLQERYNSUMGTDX
AJDSKQOIVTZEFHGYUNLPMBXWCR AKELBDFJGHONMTPRQSVZUXYWIC ALTMSXVQPNOHUWDIZYCGKRFBEJ AMNFLHQGCUJTBYPZKXISRDVEWO
ANCJILDHBMKGXUZTSWQYVORPFE AODWPKJVIUQHZCTXBLEGNYRSMF APBVHIYKSGUENTCXOWFQDRLJZM AQJNUBTGIMWZRVLXCSHDEOKFPY
ARMYOFTHEUSZJXDPCWGQIBKLNV ASDMCNEQBOZPLGVJRKYTFUIWXH ATOJYLFXNGWHVCMIRBSEKUPDZQ AUTRZXQLYIOVBPESNHJWMDGFCK
AVNKHRGOXEYBFSJMUDQCLZWTIP AWVSFDLIEBHKNRJQZGMXPUCOTY AXKWREVDTUFOYHMLSIQNJCPGBZ AYJPXMVKBQWUGLOSTECHNZFRID
AZDNBUHYFWJLVGRCQMPSOEXTKI""".split()
assert len(DISKS) == 25 and all(sorted(d) == [chr(65 + i) for i in range(26)] for d in DISKS)


def match(compat, residues, ndisk):
    """Bipartite matching: each residue needs a distinct disk. compat: dict r -> list of disks."""
    owner = {}

    def try_r(r, seen):
        for d in compat[r]:
            if d in seen:
                continue
            seen.add(d)
            if d not in owner or try_r(owner[d], seen):
                owner[d] = r
                return True
        return False

    for r in sorted(residues, key=lambda x: len(compat[x])):
        if not try_r(r, set()):
            return False
    return True


def search(ct, disks, L=25):
    """Vectorized: S[t, d, g] = crib t satisfied by disk d at generatrix g."""
    nd = len(disks)
    pos = [{c: k for k, c in enumerate(d)} for d in disks]
    cribs = sorted(CRIB_POS.items())
    S = np.zeros((len(cribs), nd, 26), dtype=bool)
    for t, (i, p) in enumerate(cribs):
        for d in range(nd):
            for g in range(26):
                S[t, d, g] = disks[d][(pos[d][p] + g) % 26] == ct[i]
    hits = []
    for o in range(L):
        lines = sorted(set((i + o) // L for i, _ in cribs))
        nl = len(lines)
        G = np.array(list(itertools.product(range(26), repeat=nl)))  # (ncombo, nl)
        res = {}
        for t, (i, p) in enumerate(cribs):
            r = (i + o) % L
            li = lines.index((i + o) // L)
            arr = S[t][:, G[:, li]]  # (nd, ncombo)
            res[r] = arr if r not in res else (res[r] & arr)
        alive = np.ones(len(G), dtype=bool)
        for r, arr in res.items():
            alive &= arr.any(axis=0)
        for c in np.nonzero(alive)[0]:
            compat = {r: list(np.nonzero(arr[:, c])[0]) for r, arr in res.items()}
            if match(compat, list(compat), nd):
                hits.append((o, tuple(G[c])))
    return hits


def search_slow(ct, disks, L=25):
    pos = [{c: k for k, c in enumerate(d)} for d in disks]
    nd = len(disks)
    hits = []
    for o in range(L):
        # group crib positions by line
        lines = sorted(set((i + o) // L for i in CRIB_POS))
        for gs in itertools.product(range(26), repeat=len(lines)):
            g = dict(zip(lines, gs))
            cons = {}
            for i, p in CRIB_POS.items():
                cons.setdefault((i + o) % L, []).append((p, ct[i], g[(i + o) // L]))
            compat = {}
            ok = True
            for r, lst in cons.items():
                ds = [d for d in range(nd) if all(disks[d][(pos[d][p] + gg) % 26] == c for p, c, gg in lst)]
                if not ds:
                    ok = False
                    break
                compat[r] = ds
            if ok and match(compat, list(cons), nd):
                hits.append((o, gs))
    return hits


if __name__ == "__main__":
    import time
    t = time.time()
    real = search(CT, DISKS)
    print("M-94 real CT: offsets 0-24, all generatrix combos -> consistent configs:", len(real), round(time.time() - t), "s")
    for h in real[:10]:
        print("   offset", h[0], "generatrices", h[1])
    rng = np.random.default_rng(0)
    nulls = []
    for k in range(5):
        sh = "".join(rng.permutation(list(CT)))
        nulls.append(len(search(sh, DISKS)))
    print("null shuffled CT (5 runs) consistent counts:", nulls)
    rnulls = []
    for k in range(3):
        rd = ["".join(rng.permutation(list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))) for _ in range(25)]
        rnulls.append(len(search(CT, rd)))
    print("null random disk sets (3 runs) consistent counts:", rnulls)
