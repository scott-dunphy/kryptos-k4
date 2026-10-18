"""Crib dragging under the KRYPTOS-letter fingerprint.
Fingerprint (from 24 known letters): PT letter in KRYPTOS -> CT within ±2 (AZ); PT letter not in KRYPTOS ->
CT NOT within ±2 (observed 0 of 14 non-KRYPTOS cribs inside ±2 except E@21 +1, E@30 +2 -> so weaker: allow).
Test: for each candidate word and each start position (non-overlapping with known cribs), count
  hitsK = KRYPTOS letters of word with |C-P|<=2, nK = count of KRYPTOS letters; also non-K letters inside ±2 (nonK_in).
Score = hitsK/nK with nK>=3. Null: same word on shuffled non-crib CT (1000 shuffles) -> P(score>=observed).
Reports placements with all KRYPTOS letters fitting and P<0.05.
"""
import numpy as np
from k4lib import CT, CRIB_POS, AZ

CTA = np.array([ord(c) - 65 for c in CT])
KRY = set("KRYPTOS")
crib_idx = set(CRIB_POS)
WORDS = """
NORTH SOUTH WEST NORTHWEST SOUTHEAST SOUTHWEST NORTHEAST DEGREES MINUTES SECONDS LATITUDE LONGITUDE COMPASS ROSE
LODESTONE MAGNETIC BEARING AZIMUTH POSITION LOCATION COORDINATES MERIDIAN
BERLIN CLOCK WALL GATE CHECKPOINT ALEXANDERPLATZ WORLDCLOCK TIME HOUR MIDNIGHT NOON ZONE EAST WEST
EGYPT CAIRO LUXOR TOMB CHAMBER CANDLE LIGHT SHADOW DARKNESS FLAME TORCH SUN MOON STAR
MESSAGE DELIVER DELIVERED COURIER AGENT SECRET BURIED DIG HIDDEN UNDER BENEATH FIND SEEK LOOK SEE
THE AND THAT WITH FROM THIS WHERE WHEN WHAT WHICH THERE THEIR THEN THEY HAVE WILL YOUR
KRYPTOS SANBORN SCHEIDT WEBSTER LANGLEY CIA AGENCY
ILLUSION PALIMPSEST ABSCISSA LAYER TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN TWENTY THIRTY FORTY FIFTY
STEPS PACES FEET METERS YARDS DEGREE POINT MARK MARKER BENCHMARK STONE ROCK TREE WOOD PETRIFIED COPPER
ONLY ALSO MORE THAN INTO OVER AFTER BEFORE BETWEEN THROUGH TOWARD TOWARDS ACROSS ABOVE BELOW
STRAIGHT TURN LEFT RIGHT FOLLOW GO WALK STAND FACE
""".split()
WORDS = sorted(set(WORDS))
MIN_K = 3


def fits(word, start, cta):
    hk = nk = nin = 0
    for j, ch in enumerate(word):
        i = start + j
        d = ((int(cta[i]) - (ord(ch) - 65) + 13) % 26) - 13
        if ch in KRY:
            nk += 1
            if abs(d) <= 2:
                hk += 1
        elif abs(d) <= 2:
            nin += 1
    return hk, nk, nin


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    noncrib = np.array([i for i in range(97) if i not in crib_idx])
    shuffles = []
    for _ in range(400):
        a = CTA.copy(); a[noncrib] = rng.permutation(a[noncrib]); shuffles.append(a)
    results = []
    for w in WORDS:
        nk_total = sum(ch in KRY for ch in w)
        if nk_total < MIN_K:
            continue
        for s in range(0, 97 - len(w) + 1):
            span = set(range(s, s + len(w)))
            if span & crib_idx:
                continue
            hk, nk, nin = fits(w, s, CTA)
            if hk < nk:
                continue
            # null: fraction of shuffles where this placement has all K letters fitting
            cnt = 0
            for a in shuffles:
                h2, _, _ = fits(w, s, a)
                cnt += (h2 == nk)
            # placements tried for this word (look-elsewhere): number of legal starts
            results.append((w, s, nk, nin, cnt / len(shuffles)))
    results.sort(key=lambda r: (r[4], -r[2]))
    print("word start nK nonK_inside p_null")
    for r in results[:40]:
        print(f"{r[0]:14s} {r[1]:3d}  {r[2]}  {r[3]}  {r[4]:.3f}")
    # expected number of 'all-K-fit' placements overall under null
    tot_real = len(results)
    tot_null = []
    for a in shuffles[:100]:
        c = 0
        for w in WORDS:
            nk_total = sum(ch in KRY for ch in w)
            if nk_total < MIN_K:
                continue
            for s in range(0, 97 - len(w) + 1):
                if set(range(s, s + len(w))) & crib_idx:
                    continue
                hk, nk, _ = fits(w, s, a)
                c += (hk == nk)
        tot_null.append(c)
    print(f"\nTOTAL all-KRYPTOS-letters-fit placements: real {tot_real}; null mean {np.mean(tot_null):.1f} sd {np.std(tot_null):.1f}")
