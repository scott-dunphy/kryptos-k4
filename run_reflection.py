"""Reflecting-pool readings of K4 (user idea, 2026-10-18).

Water mirror = vertical flip: plate rows appear bottom-to-top, columns unchanged, letters flipped top-bottom.
Letters symmetric under a vertical flip: B C D E H I K O X; M<->W swap; the rest are not letters.
Variants of the carved K4 (copper layout: OBKR at row 24 cols 27-30, then rows 25-27 of 31):
  carved / carved + M<->W / reflected order (rows 27,26,25,24) / reflected order + M<->W.
Each goes through run_pinned_table (keyword table layer x fixed mask, exact / 1 slip / nuance) with planted check
already validated there. Cribs stay at their published positions in the new reading order.
"""
import numpy as np
from k4lib import CT
from run_pinned_table import keywords, run

rows = [CT[0:4], CT[4:35], CT[35:66], CT[66:97]]
refl = rows[3] + rows[2] + rows[1] + rows[0]
mw = str.maketrans("MW", "WM")
variants = {"carved": CT, "carved M<->W": CT.translate(mw), "reflected": refl, "reflected M<->W": refl.translate(mw)}
ks, KW, LENS = keywords()
names = ["exact", "exact<=1slip", "nuance1 AZ", "nuance1 KA", "nuance2 AZ", "nuance2 KA"]
rng = np.random.default_rng(5)
for name, ct in variants.items():
    cti = np.array([ord(c) - 65 for c in ct], dtype=np.int64)
    c, h = run(cti, KW, LENS)
    print(name, ct[:20] + "...", dict(zip(names, c.tolist())), flush=True)
    for row in h[:5]:
        print("   hit", ks[row[0]], row.tolist(), flush=True)
c2, _ = run(rng.permutation(cti), KW, LENS)
print("NULL (shuffled reflected)", dict(zip(names, c2.tolist())))
