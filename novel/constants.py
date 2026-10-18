"""Mathematical-constant digit keystreams (pi, e, sqrt2, sqrt3, phi, ln2) as Gronsfeld digits, 2-digit numbers mod 26,
and base-26 expansions; tested with clocklib.test_seq (fixed AZ/KA variants, k=a*K+b) and clocksingle (unknown single alphabet)."""
import sys
from decimal import Decimal, getcontext
import numpy as np
sys.path.insert(0, '.')
import clocklib as cl
import clocksingle as cs

getcontext().prec = 1300

def pi_dec():
    # Machin
    def arctan_inv(x):
        x = Decimal(x); s = Decimal(0); t = 1 / x; n = 1; x2 = x * x; sign = 1
        while True:
            term = t / n
            if term < Decimal(10) ** (-1290): break
            s += sign * term; t /= x2; n += 2; sign = -sign
        return s
    return 4 * (4 * arctan_inv(5) - arctan_inv(239))

def e_dec():
    s = Decimal(0); t = Decimal(1); n = 0
    while t > Decimal(10) ** (-1290):
        s += t; n += 1; t /= n
    return s

consts = {'pi': pi_dec(), 'e': e_dec(), 'sqrt2': Decimal(2).sqrt(), 'sqrt3': Decimal(3).sqrt(),
          'phi': (1 + Decimal(5).sqrt()) / 2, 'ln2': Decimal(2).ln(), 'sqrt5': Decimal(5).sqrt()}

def digits10(x, n=1200):
    s = format(x, 'f').replace('.', '')
    return [int(c) for c in s[:n]]

def digits_b(x, b, n=400):
    out = []; f = x - int(x); ip = int(x)
    for _ in range(n):
        f *= b; d = int(f); out.append(d); f -= d
    return [ip % b] + out

if __name__ == '__main__':
    for name, x in consts.items():
        d = digits10(x)
        streams = {'dig': d, 'pairs': [(10 * d[i] + d[i + 1]) % 26 for i in range(0, len(d) - 1, 2)],
                   'b26': digits_b(x, 26), 'b13': digits_b(x, 13)}
        for sn, K in streams.items():
            r = cl.test_seq(np.array(K), cyclic=False)
            s1 = cs.test_single(np.array(K), cyclic=False)
            print(name, sn, 'fixed-variant best', r[0], '/24  unknown-alphabet hits', len(s1), flush=True)
