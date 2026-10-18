"""S11: tableau-overlay keystreams with keyed alphabets (Quagmire-style): posC(C_i) - posP(P_i) - s_i = const
(and Beaufort/variant forms). s_i = index of the tableau letter level with K4 cell (rows X,Y,Z,footer; dx -2..2;
mirror; with/without label col), indexed in AZ or KA. Alphabets: (AZ,KA) x 396k dictionary-keyed (+rev), both roles,
and lore x lore. Exact: require 24/24 (report >= 18)."""
import time
from numba import njit, prange
from common import *
from overlay import build
from run_alphapairs import load_words, pos_table
from k4lib import keyed_alphabet

@njit(cache=True)
def kern(SK, TA, TB, PL, CL, minhit, out):
    nS = SK.shape[0]; nA = TA.shape[0]; nB = TB.shape[0]; nc = PL.shape[0]
    cnt = 0; hist = np.zeros(26, dtype=np.int64); best_all = 0
    for s in range(nS):
        for a in range(nA):
            for b in range(nB):
                for rule in range(3):
                    for x in range(26): hist[x] = 0
                    for t in range(nc):
                        if SK[s, t] < 0: continue
                        ip = TA[a, PL[t]]; ic = TB[b, CL[t]]
                        if rule == 0: d = (ic - ip - SK[s, t]) % 26
                        elif rule == 1: d = (ic + ip - SK[s, t]) % 26
                        else: d = (ip - ic - SK[s, t]) % 26
                        hist[d] += 1
                    m = 0
                    for x in range(26):
                        if hist[x] > m: m = hist[x]
                    if m > best_all: best_all = m
                    if m >= minhit and cnt < out.shape[0]:
                        out[cnt, 0] = s; out[cnt, 1] = a; out[cnt, 2] = b; out[cnt, 3] = rule; out[cnt, 4] = m
                        cnt += 1
    return cnt, best_all

if __name__ == "__main__":
    t0 = time.time()
    keys = {}
    for src_name, src in (("tab", RIGHT), ("tabnl", [r[1:] for r in RIGHT]), ("tabup1", RIGHT[1:]+[RIGHT[0]]), ("tabtop", RIGHT[14:]+RIGHT[:14])):
        for dx in range(-2, 3):
            for mirror in (0, 1):
                k = build(src, 0, 0, dx, mirror, "left")
                if sum(k[i] is None for i in cf.CRIB_I) > 3: continue
                for kname, kal in (("AZ", AZ), ("KA", KA)):
                    keys[(src_name, dx, mirror, kname)] = [kal.index(k[i]) if k[i] else -1 for i in cf.CRIB_I]
    names = list(keys); SK = np.array([keys[n] for n in names], dtype=np.int64)
    lore, words = load_words()
    def alphas(ws):
        res, seen = [], set()
        for w in ws:
            for rev in (0, 1):
                al = keyed_alphabet(w); al = al[::-1] if rev else al
                if al not in seen: seen.add(al); res.append((w + ("~rev" if rev else ""), al))
        return res
    base = alphas(["", "KRYPTOS"]) + alphas(lore)
    dic = alphas(words)
    PL = cf.CRIB_L; CL = cf.CTI[cf.CRIB_I]
    out = np.zeros((100000, 5), dtype=np.int64)
    small = [a for n, a in base[:4]]  # AZ, AZrev, KA, KArev
    TA_small = np.array([pos_table(a) for a in small]); TB_dic = np.array([pos_table(a) for _, a in dic])
    TA_base = np.array([pos_table(a) for _, a in base])
    print("keystreams", len(names), "dict alphabets", len(dic), flush=True)
    for label, TA, TB, nA, nB in (("PT small x CT dict", TA_small, TB_dic, small, dic),
                                   ("PT dict x CT small", TB_dic, TA_small, dic, small),
                                   ("lore x lore", TA_base, TA_base, base, base)):
        c, b = kern(SK, TA, TB, PL, CL, 14, out)
        print(label, "best agreement", b, "n>=14:", c, round(time.time() - t0, 1), flush=True)
        for r in out[:min(c, 10)]:
            print("  ", names[r[0]], r[1], r[2], r[3], r[4])
