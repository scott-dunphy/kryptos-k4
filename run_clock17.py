"""TEAM clock exp 17: all clock stream windows (every offset, fwd/rev) -> dual-alphabet union-find (gromark mode 0).
Saves survivors (n,97) int8 + labels for anneal. Multiplier and indicator absorbed by dual alphabets."""
import numpy as np, json
from numba import njit
from run_gromark import consistent, PL, CL, CI
import clockstreams as st


@njit(cache=True)
def filt(E, nstart, PL, CL, CI, out):
    d = np.zeros(97, dtype=np.int64); n = 0
    for o in range(nstart):
        for i in range(97): d[i] = E[o + i] % 26
        if consistent(d, 0, PL, CL, CI):
            if n < out.shape[0]: out[n] = o
            n += 1
    return n


seen = set(); wins = []; labels = []; total = 0
gens = [st.weltzeit_streams(), st.mengen_streams(), st.letter_streams(), st.analog_streams(), st.date_streams()]
buf = np.zeros(200000, dtype=np.int64)
for g in gens:
    for name, K, cyc in g:
        k0 = (K.tobytes(), cyc)
        if k0 in seen: continue
        seen.add(k0)
        for dr in (0, 1):
            S = (K[::-1] if dr else K) % 26
            if cyc:
                E = np.concatenate([S] * (97 // len(S) + 2)); ns = len(S)
            else:
                E = S; ns = len(S) - 96
            E = np.ascontiguousarray(E, dtype=np.int64)
            n = filt(E, ns, PL, CL, CI, buf); total += ns
            for o in buf[:min(n, len(buf))]:
                wins.append(E[o:o + 97].astype(np.int8)); labels.append(f"{name}|dir{dr}|off{int(o)}")
W = np.array(wins); 
_, ui = np.unique(W, axis=0, return_index=True); ui = np.sort(ui)
W = W[ui]; labels = [labels[i] for i in ui]
np.save("results/clock_dual_survivors.npy", W); json.dump(labels, open("results/clock_dual_survivors.json", "w"))
print("windows tested", total, "survivors", len(W), "rate", len(W) / total)
