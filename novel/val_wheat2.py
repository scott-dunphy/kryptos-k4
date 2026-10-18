import sys, random
sys.path.insert(0, '.')
import novel.wheatstone as W
from k4lib import AZ, keyed_alphabet
rnd = random.Random(5)
inner = keyed_alphabet('CLOCKWORK'); No = 27; opos = W.outer_ring(AZ, No, {0}); o = 11
ct = ''.join(rnd.choice(AZ) for _ in range(97))
S = W.steps(ct, opos, No, start=4)
pt = ''.join(inner[(s + o) % 26] for s in S)
W.CRIB_POS = {i: pt[i] for i in list(range(21, 34)) + list(range(63, 74))}
print('mode1 planted ->', W.test(ct, No, opos, 1))
