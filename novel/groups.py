"""Non-cyclic 'language base' groups: letter -> vector in (Z2)^5 or (Z3)^3 (digit-wise, no carry), C = P (+) K.
Labelings: A=0.., A=1.., KA-order, ITA2 Baudot. Check key periodicity p<=30 (direct), and key-letter English score."""
import sys
import numpy as np
sys.path.insert(0, '.')
from k4lib import CT, CRIB_POS, AZ, KA, qscore

ITA2 = {'A':0b11000,'B':0b10011,'C':0b01110,'D':0b10010,'E':0b10000,'F':0b10110,'G':0b01011,'H':0b00101,'I':0b01100,
'J':0b11010,'K':0b11110,'L':0b01001,'M':0b00111,'N':0b00110,'O':0b00011,'P':0b01101,'Q':0b11101,'R':0b01010,'S':0b10100,
'T':0b00001,'U':0b11100,'V':0b01111,'W':0b11001,'X':0b10111,'Y':0b10101,'Z':0b10001}

def digits(v, b, n):
    return tuple((v // b ** j) % b for j in range(n))

def labelings():
    for name, al in (('AZ', AZ), ('KA', KA)):
        for off in (0, 1):
            yield f'{name}+{off} b2', {c: digits(i + off, 2, 5) for i, c in enumerate(al)}, 2
            yield f'{name}+{off} b3', {c: digits(i + off, 3, 3) for i, c in enumerate(al)}, 3
    yield 'ITA2 b2', {c: digits(v, 2, 5) for c, v in ITA2.items()}, 2

def key_vec(lab, b, P, C, mode):
    p, c = lab[P], lab[C]
    if mode == 0: return tuple((x - y) % b for x, y in zip(c, p))  # C = P + K
    return tuple((x + y) % b for x, y in zip(c, p))                # C = K - P (beaufort-like)

if __name__ == '__main__':
    import random
    cribs = sorted(CRIB_POS)
    for name, lab, b in labelings():
        inv = {v: k for k, v in lab.items()}
        for mode in (0, 1):
            if b == 2 and mode == 1: continue
            K = {i: key_vec(lab, b, CRIB_POS[i], CT[i], mode) for i in cribs}
            pers = []
            for p in range(1, 31):
                d = {}
                ok = True
                for i in cribs:
                    r = i % p
                    if r in d and d[r] != K[i]: ok = False; break
                    d[r] = K[i]
                if ok: pers.append(p)
            ks = ''.join(inv.get(K[i], '#') for i in cribs)
            print(name, mode, 'periods', pers[:5], 'keyletters', ks[:13], ks[13:])
