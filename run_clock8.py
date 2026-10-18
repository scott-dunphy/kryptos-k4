"""TEAM clock exp 8: all clock numeric streams vs UNKNOWN single mixed alphabet (Vig/Var sense), indicator b."""
import sys, time, numpy as np
import clocksingle as cs, clockstreams as st
ONE = np.array([1], dtype=np.int64)
gen = st.weltzeit_streams() if sys.argv[1] == "w" else st.mengen_streams()
n = 0; t = time.time(); seen = set()
for name, K, cyc in gen:
    key = (K.tobytes(), cyc)
    if key in seen: continue
    seen.add(key); n += 1
    h = cs.test_single(K, cyclic=cyc, units=ONE)
    if h: print("HIT", name, h[:5], flush=True)
print("streams", n, "time", round(time.time() - t), flush=True)
