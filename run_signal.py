"""Tests of the 'small shift' crib-key signal (Fable deep dive).
T1 look-elsewhere MC: min-p over the whole family of statistics we looked at, real vs 1e4-1e5 CT permutations.
T2 IC prediction: English 97-letter samples enciphered with small-key models -> IC distribution vs K4 IC 0.0361.
"""
import numpy as np
from k4lib import CT, CRIB_POS, ioc
import kryptos_texts as kt

pos = np.array(sorted(CRIB_POS))
PTc = np.array([ord(CRIB_POS[i]) - 65 for i in pos])
KRY = np.array([c in "KRYPTOS" for c in (CRIB_POS[i] for i in pos)])
AM = PTc < 13
SEG = pos < 40
ROW = (pos + 27) // 31
PAR = pos % 2 == 0
VOW = np.array([CRIB_POS[i] in "AEIOU" for i in pos])
PARTS = {"none": np.zeros(24, bool), "seg": SEG, "AM": AM, "KRY": KRY, "row25": ROW == 1, "par": PAR, "vow": VOW}


def stats(cta):
    """Return dict stat -> value (bigger = more extreme), for the family of statistics."""
    k = (cta[pos] - PTc) % 26
    out = {}
    for m in (26, 13, 12, 11):
        s = ((k % m) + m // 2) % m - m // 2
        for w in (2, 3):
            out[f"mod{m}w{w}"] = int((np.abs(s) <= w).sum())
    for pname, mask in PARTS.items():
        if pname == "none":
            continue
        best = 0
        for c0 in range(26):
            for c1 in range(26):
                off = np.where(mask, c0, c1)
                r = ((k - off) + 13) % 26 - 13
                best = max(best, int((np.abs(r) <= 3).sum()))
        out[f"two-offset {pname}"] = best
    sk = np.abs(((k + 13) % 26) - 13)
    obs = np.array([(sk <= 3).sum(), ((sk >= 4) & (sk <= 8)).sum(), (sk >= 9).sum()])
    exp = 24 * np.array([7, 10, 9]) / 26
    out["chi2_3bin"] = float(((obs - exp) ** 2 / exp).sum())
    return out


if __name__ == "__main__":
    cta = np.array([ord(c) - 65 for c in CT])
    real = stats(cta)
    rng = np.random.default_rng(1)
    N = 20000
    null = {key: [] for key in real}
    for _ in range(N):
        s = stats(rng.permutation(cta))
        for key in real:
            null[key].append(s[key])
    null = {k: np.array(v) for k, v in null.items()}
    pvals = {k: (null[k] >= real[k]).mean() for k in real}
    print("T1 per-statistic p (real value):")
    for k in real:
        print(f"   {k:22s} real={real[k]!s:6} p={pvals[k]:.4f}")
    # min-p over family, calibrated: compute each null sample's min-p using null ranks
    keys = list(real)
    ranks = np.zeros((N, len(keys)))
    for j, k in enumerate(keys):
        v = null[k]
        order = np.argsort(np.argsort(-v, kind="stable"), kind="stable")
        # p for each null sample = fraction of null >= its value
        srt = np.sort(v)
        ranks[:, j] = 1 - np.searchsorted(srt, v, side="left") / N
    null_minp = ranks.min(axis=1)
    real_minp = min(pvals.values())
    print(f"T1 family-corrected: real min-p {real_minp:.4f}; fraction of null with min-p <= that: {(null_minp <= real_minp).mean():.4f}")

    # T2 IC prediction
    eng = (kt.K1_PT + kt.K2_PT + kt.K3_PT)
    import re
    eng += re.sub("[^A-Z]", "", open("data/carter/carter_vol1_letters.txt").read())[:200000]
    E = np.array([ord(c) - 65 for c in eng])
    def ic_of(a):
        cnt = np.bincount(a, minlength=26); n = len(a)
        return (cnt * (cnt - 1)).sum() / (n * (n - 1))
    res = {}
    for model in ("uniform26", "small_all", "observed_mix", "small_half_seg"):
        ics = []
        for _ in range(5000):
            o = rng.integers(0, len(E) - 97); p = E[o:o + 97]
            if model == "uniform26":
                k = rng.integers(0, 26, 97)
            elif model == "small_all":
                k = rng.integers(-3, 4, 97)
            elif model == "observed_mix":   # 12/24 small, 3/24 mid, 9/24 large
                u = rng.random(97)
                k = np.where(u < 0.5, rng.integers(-3, 4, 97),
                             np.where(u < 0.625, rng.choice([4, 5, 6, 7, 8, -4, -5, -6, -7, -8], 97),
                                      rng.choice([9, 10, 11, 12, 13, -9, -10, -11, -12], 97)))
            else:  # small key on first half only
                k = rng.integers(0, 26, 97); k[:48] = rng.integers(-3, 4, 48)
            ics.append(ic_of((p + k) % 26))
        ics = np.array(ics)
        res[model] = ics
        print(f"T2 {model:15s} IC mean {ics.mean():.4f}  2.5%={np.quantile(ics, 0.025):.4f}  P(IC<=0.0361)={(ics <= 0.0361).mean():.4f}")
    print("K4 IC", round(ioc(CT), 4))
