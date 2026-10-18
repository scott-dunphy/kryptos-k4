"""TEAM clock exp 10 (side check): running-key texts (AZ- or KA-indexed key letters) vs UNKNOWN single mixed
alphabet for PT/CT (Vig/Var union-find + Beaufort signed union-find). Sources from run_e4 (+K3 PT fixed by stego)."""
import time, numpy as np
import clocksingle as cs
from run_e4 import sources
from k4lib import AZ, KA
ONE = np.array([1], dtype=np.int64)
srcs = sources()
for name, s in srcs.items():
    if name.endswith("~rev"): continue  # test_* does both dirs
    t = time.time()
    for an, al in (("AZ", AZ), ("KA", KA)):
        K = np.array([al.index(c) for c in s], dtype=np.int64)
        cyc = len(K) < 2000
        h1 = cs.test_single(K, cyclic=cyc, units=ONE)
        h2 = cs.test_beau(K, cyclic=cyc)
        print(name, an, len(K), "vig hits", h1[:5], "beau hits", h2[:5], round(time.time() - t), flush=True)
