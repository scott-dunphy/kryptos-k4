"""TEAM clock exp 12: analog-clock hand streams + calendar-date digit streams (1989-1991):
fixed alphabets (clocklib, a*K+b) + unknown single alphabet Vig/Var + Beaufort."""
import numpy as np
import clocklib as cl, clocksingle as cs, clockstreams as st
ONE = np.array([1], dtype=np.int64)
best = []
for g in (st.analog_streams, st.date_streams):
    for name, K, cyc in g():
        r = cl.test_seq(K % 26, cyclic=cyc); best.append((r[0], name, r))
        h1 = cs.test_single(K, cyclic=cyc, units=ONE); h2 = cs.test_beau(K, cyclic=cyc)
        if h1 or h2: print("HIT", name, h1[:3], h2[:3], flush=True)
best.sort(key=lambda x: -x[0])
print("fixed-alphabet best:", best[:6]); print("n", len(best))
