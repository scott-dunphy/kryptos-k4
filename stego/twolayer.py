"""S8: 'LAYER TWO' -> K4 = K1/K2 method applied twice: C = E2(E1(P, w1), w2), each layer a Vig/Beau/VarBeau
on alphabet AZ or KA (same alphabet for PT and CT of that layer, like K1/K2 KA Vigenere), keywords w1, w2 from
lore + stego words, all key offsets. Exact crib test (count of 24 matching; report >= 20)."""
import time
from numba import njit
from common import *
from run_alphapairs import load_words

STEGO = ("EQUAL QUAE QUAEL LOEI YAR RAY YR RQ SOS HILL LAYERTWO XLAYERTWO IDBYROWS PALIMPCEST DIGETAL "
         "INTERPRETATIT INTERPRETATIU VIRTUALLY SHADOWFORCES LUCIDMEMORY TISYOURPOSITION KOMITET WW WILLIAMWEBSTER "
         "NOVEMBER BERLINCLOCK EASTNORTHEAST ILLUSION DESPARATLY ABSCISSA KRYPTOS OBKR ATTIT POSITION "
         "WONDERFUL WONDERFULTHINGS CANYOUSEEANYTHING HOWARDCARTER TUTANKHAMEN EGYPT CAIRO GIZA NILE "
         "FALLOFTHEWALL WALL MAUER NINETEENEIGHTYNINE DELIVERINGAMESSAGE").split()

@njit(cache=True)
def kern(words, wlen, POS, ALPH, CI, CTc, PL, minhit, out):
    nw = words.shape[0]; nc = CI.shape[0]; cnt = 0
    for a in range(nw):
        pa = wlen[a]
        for b in range(nw):
            pb = wlen[b]
            for o1 in range(pa):
                for o2 in range(pb):
                    for A1 in range(2):
                        for A2 in range(2):
                            for r1 in range(3):
                                for r2 in range(3):
                                    hit = 0
                                    for t in range(nc):
                                        i = CI[t]
                                        k2 = POS[A2, words[b, (i + o2) % pb]]
                                        c = POS[A2, CTc[t]]
                                        # undo layer 2 in alphabet A2
                                        if r2 == 0: x = (c - k2) % 26
                                        elif r2 == 1: x = (k2 - c) % 26
                                        else: x = (c + k2) % 26
                                        xl = ALPH[A2, x]           # letter (AZ idx)
                                        k1 = POS[A1, words[a, (i + o1) % pa]]
                                        y = POS[A1, xl]
                                        if r1 == 0: z = (y - k1) % 26
                                        elif r1 == 1: z = (k1 - y) % 26
                                        else: z = (y + k1) % 26
                                        if ALPH[A1, z] == PL[t]: hit += 1
                                        elif t - hit > nc - minhit: break
                                    if hit >= minhit and cnt < out.shape[0]:
                                        out[cnt, 0] = a; out[cnt, 1] = b; out[cnt, 2] = o1; out[cnt, 3] = o2
                                        out[cnt, 4] = A1 * 2 + A2; out[cnt, 5] = r1 * 3 + r2; out[cnt, 6] = hit
                                        cnt += 1
    return cnt

if __name__ == "__main__":
    lore, _ = load_words()
    ws = sorted(set(lore) | set(STEGO))
    L = max(len(w) for w in ws)
    words = np.zeros((len(ws), L), dtype=np.int64); wlen = np.array([len(w) for w in ws], dtype=np.int64)
    for k, w in enumerate(ws):
        words[k, :len(w)] = [AZ.index(c) for c in w]
    POS = np.array([[AZ.index(c) for c in AZ], [KA.index(c) for c in AZ]], dtype=np.int64)
    ALPH = np.array([[AZ.index(c) for c in AZ], [AZ.index(c) for c in KA]], dtype=np.int64)
    CTc = cf.CTI[cf.CRIB_I]
    out = np.zeros((10000, 7), dtype=np.int64)
    t = time.time()
    c = kern(words, wlen, POS, ALPH, cf.CRIB_I, CTc, cf.CRIB_L, 12, out)
    print("words", len(ws), "time", round(time.time() - t, 1), "hits>=12:", c)
    rows = sorted(out[:c].tolist(), key=lambda r: -r[6])
    from collections import Counter
    print(Counter(r[6] for r in rows))
    for r in rows[:10]:
        print(ws[r[0]], ws[r[1]], r[2:])
