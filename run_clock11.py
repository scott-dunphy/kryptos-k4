"""TEAM clock exp 11: segment-constant keys: key constant within segments whose lengths follow a clock sequence
(face sizes, Mengenlehreuhr rows, ...), arbitrary value per segment. Fixed alphabets (12 variants).
Test: required crib key values equal within each segment. Report #equalities checked (m) for passing configs."""
import numpy as np
import cribfilter as cf, weltzeit as w
REQ = np.array([cf.KV[v, cf.CRIB_L, cf.CTI[cf.CRIB_I]] for v in range(cf.NV)])
CI = cf.CRIB_I
seqs = {}
for ver in w.VERSIONS:
    seqs[f"facesize{ver}"] = [len(f) for f in w.faces(ver)]
    seqs[f"namelen{ver}"] = [len(w.norm(c)) for c, _, _ in w.cities(ver)]
seqs["mengen"] = [1, 4, 4, 11, 4]; seqs["mengen_s_last"] = [4, 4, 11, 4, 1]
seqs["face_utc_abs+1"] = [abs(u) + 1 for u in w.FACE_UTC]
res = []
for sn, S in seqs.items():
    for d in (0, 1):
        L = S[::-1] if d else S
        # segment id per position for each start shift (start inside the sequence at unit offset s)
        unit = []
        for si, l in enumerate(L):
            unit += [si] * l
        U = len(unit)
        for o in range(U):
            seg = [unit[(o + i) % U] + ((o + i) // U) * len(L) for i in range(97)]
            groups = {}
            for t, i in enumerate(CI):
                groups.setdefault(seg[i], []).append(t)
            m = sum(len(g) - 1 for g in groups.values())
            if m < 4: continue
            for v in range(12):
                if all(len(set(REQ[v, g])) == 1 for g in groups.values()):
                    res.append((m, sn, d, o, v))
res.sort(reverse=True)
print(len(res), res[:10])
