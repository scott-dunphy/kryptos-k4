"""TEAM anneal: fraction of shuffled-CT nulls that admit ANY crib-consistent free-alphabet Quagmire IV key at period p."""
import sys, time, numpy as np
from k4lib import CT
import run_q4dfs as q
p = int(sys.argv[1]); S = int(sys.argv[2])
real = q.count(p, CT, maxout=1, stop=1)[0] > 0
hits = 0; t = time.time()
for s in range(S):
    ct = "".join(np.random.default_rng(1000 + s).permutation(list(CT)))
    hits += q.count(p, ct, maxout=1, stop=1)[0] > 0
print(f"p={p} real_consistent={real} null_consistent={hits}/{S} t={time.time()-t:.0f}s", flush=True)
