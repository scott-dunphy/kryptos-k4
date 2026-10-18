import sys, random
sys.path.insert(0, '.')
from novel.wheatstone import outer_ring, steps, test
from k4lib import AZ, CRIB_POS, keyed_alphabet
rnd = random.Random(3)
inner = keyed_alphabet('CLOCKWORK')
pt = [rnd.choice(AZ) for _ in range(97)]
for i, c in CRIB_POS.items(): pt[i] = c
pt = ''.join(pt)
No = 27; opos = outer_ring(AZ, No, {0})
# mode 0: PT on outer
S = steps(pt, opos, No, start=0); o = 5
ct0 = ''.join(inner[(s + o) % 26] for s in S)
print('mode0 planted ->', test(ct0, No, opos, 0))
# mode 1: CT on outer: choose CT so that inner[S] = PT -- decryption device: CT moves hand, PT read on inner.
# encryption: for each PT letter, choose next CT letter (outer) such that inner[(S+d+o)%26]==PT; d in 1..27 -> pick smallest
ct = []; cur = 0; tot = 0
inv_outer = {v: k for k, v in opos.items()}
for ch in pt:
    for d in range(1, 3 * No):
        pos = (cur + d) % No
        if pos in inv_outer and inner[(tot + d + o) % 26] == ch:
            break
    tot += d; cur = pos; ct.append(inv_outer[pos])
ct1 = ''.join(ct)
print('mode1 planted ->', test(ct1, No, opos, 1))
S = steps(ct1, opos, No, start=0)
dec = ''.join(inner[(s + o) % 26] for s in S)
print(sum(a == b for a, b in zip(dec, pt)), 'of 97 decrypt ok')
