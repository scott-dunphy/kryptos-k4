"""Running key from Carter & Mace, The Tomb of Tut.ankh.Amen vol I (1923; K3's source), letters indexed AZ and KA,
fwd/rev, all offsets; fixed 12 variants with k=a*K+b (clocklib) and unknown single mixed alphabet (clocksingle)."""
import sys
import numpy as np
sys.path.insert(0, '.')
import clocklib as cl, clocksingle as cs
from k4lib import AZ, KA
L = open('data/carter/carter_vol1_letters.txt').read()
for an, al in (('AZ', AZ), ('KA', KA)):
    K = np.array([al.index(c) for c in L], np.int64)
    r = cl.test_seq(K, cyclic=False)
    print(an, 'fixed variants best', r, flush=True)
K = np.array([AZ.index(c) for c in L], np.int64)
h = cs.test_single(K, cyclic=False, units=np.array([1], np.int64))
print('unknown single alphabet (a=1) hits', len(h), h[:5])
# null calibration on shuffled text
rng = np.random.default_rng(0)
Ks = rng.permutation(K)
print('null fixed best', cl.test_seq(Ks, cyclic=False)[0])
