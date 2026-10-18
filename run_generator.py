"""Themed plaintext generator constrained by the KRYPTOS fingerprint.
Gaps: [0,21), [34,63), [74,97). Beam search over a themed vocabulary + function words; word placed at position s
must satisfy: every KRYPTOS letter within ±2 of CT (hard); non-KRYPTOS letter within ±2 costs a penalty (soft).
Score per word = weight(themed 1.0 / function 0.4) * len^0.5 - 1.5*softviol. Keep top-B partial fills.
Final: assemble full 97-letter texts (cribs fixed), rank by fingerprint stats + word score + quadgrams.
"""
import heapq, itertools
import numpy as np
from k4lib import CT, CRIB_POS, AZ, qscore
from candidate_check import check

KRY = set("KRYPTOS")
THEMED = """NORTH SOUTH EAST WEST NORTHEAST NORTHWEST SOUTHEAST SOUTHWEST DEGREES MINUTES SECONDS LATITUDE LONGITUDE
COMPASS ROSE LODESTONE MAGNETIC BEARING AZIMUTH POSITION LOCATION COORDINATES MERIDIAN HEADING DIRECTION
BERLIN CLOCK WALL GATE CHECKPOINT ALEXANDERPLATZ WORLD TIME HOUR HOURS MIDNIGHT NOON ZONE ZONES CITY CITIES
EGYPT CAIRO LUXOR TOMB CHAMBER CANDLE LIGHT SHADOW SHADOWS DARKNESS FLAME TORCH SUN MOON STAR STARS SAND DESERT
MESSAGE MESSENGER DELIVER DELIVERED COURIER AGENT SECRET SECRETS BURIED BURY DIG DUG HIDDEN HIDE UNDER BENEATH
FIND SEEK LOOK SEE SEEN WATCH WAIT MEET MEETING POINT PLACE SPOT MARK MARKER STONE ROCK TREE WOOD PETRIFIED COPPER
STEPS PACES FEET YARDS METERS ONE TWO THREE FOUR FIVE SIX SEVEN EIGHT NINE TEN TWENTY THIRTY FORTY FIFTY HUNDRED
STRAIGHT TURN LEFT RIGHT FOLLOW GO WALK STAND FACE FACING TOWARD TOWARDS FROM INTO OVER AFTER BEFORE BETWEEN
THROUGH ACROSS ABOVE BELOW BEYOND NEAR FAR AWAY HERE THERE WHERE WHEN WHAT WHICH WHO WHY HOW
ILLUSION LAYER LAYERS TRUTH FREE KNOW KNOWN KNOWLEDGE INVISIBLE VISIBLE EYE EYES OPEN CLOSE CLOSED DOOR WINDOW
FALL FELL FALLEN FALLING WALLS BRIDGE RIVER SPREE GERMANY DIVIDED UNITED FREEDOM PEOPLE CROWD
MEMORY REMEMBER FORGET PAST FUTURE PRESENT YEAR YEARS DAY DAYS NIGHT NIGHTS MORNING EVENING
KRYPTOS CODE CIPHER KEY KEYS ANSWER QUESTION RIDDLE PUZZLE FINAL LAST FIRST NEXT END BEGIN BEGINNING
LANGLEY AGENCY SCULPTURE COURTYARD STATUE PLATE PANEL SCREEN LETTERS WORDS TEXT CARVED CUT
HOUR CLOCKS WATCHES TICK TICKING SLOWLY QUICKLY
""".split()
FUNC = "THE A AN AND OR OF TO IN ON AT BY IS ARE WAS WERE BE BEEN IT ITS THIS THAT THESE THOSE YOU YOUR WE OUR I MY HE SHE THEY THEM THEIR NOT NO SO AS IF THEN WITH FOR ALL ANY SOME MORE MOST ONLY ALSO VERY JUST X".split()
VOCAB = {w: 1.0 for w in THEMED}
for w in FUNC:
    VOCAB.setdefault(w, 0.4)
VOCAB["X"] = 0.3

GAPS = [(0, 21), (34, 63), (74, 97)]


def place_cost(w, s):
    soft = 0
    for j, ch in enumerate(w):
        i = s + j
        d = abs(((ord(CT[i]) - ord(ch) + 13) % 26) - 13)
        if ch in KRY:
            if d > 2:
                return None
        elif d <= 2:
            soft += 1
    return soft


CTX_L = {0: "", 34: "EASTNORTHEAST", 74: "BERLINCLOCK"}
CTX_R = {21: "EASTNORTHEAST", 63: "BERLINCLOCK", 97: ""}


def beam_fill(start, end, B=300):
    beams = {start: [(0.0, [])]}
    for p in range(start, end):
        if p not in beams:
            continue
        cur = heapq.nlargest(B, beams[p])
        for sc, ws in cur:
            for w, wt in VOCAB.items():
                e = p + len(w)
                if e > end:
                    continue
                if len(w) == 1 and any(len(x) == 1 for x in ws[-2:]):
                    continue
                soft = place_cost(w, p)
                if soft is None:
                    continue
                if ws and ws[-1] == w:
                    continue
                txt = CTX_L[start] + "".join(ws) + w
                q = qscore(txt[-max(8, len(w) + 3):]) if len(txt) >= 4 else -5.0
                nsc = sc + (q + 5.5) * len(w) + 0.8 * wt * (len(w) >= 4) - 1.0 * soft
                beams.setdefault(e, []).append((nsc, ws + [w]))
        del beams[p]
    out = []
    for sc, ws in beams.get(end, []):
        txt = "".join(ws)
        kfrac = sum(c in KRY for c in txt) / len(txt)
        if kfrac < 0.22:
            continue
        full = CTX_L[start] + txt + CTX_R[end]
        out.append((qscore(full) * len(txt) + 0.5 * sum(VOCAB[x] * (len(x) >= 4) for x in ws), ws))
    return heapq.nlargest(B, out)


if __name__ == "__main__":
    fills = [beam_fill(s, e) for s, e in GAPS]
    print("fills per gap:", [len(f) for f in fills])
    cands = []
    for a in fills[0][:12]:
        for b in fills[1][:25]:
            for c in fills[2][:12]:
                pt = "".join(a[1]) + "EASTNORTHEAST" + "".join(b[1]) + "BERLINCLOCK" + "".join(c[1])
                assert len(pt) == 97
                cands.append((a[0] + b[0] + c[0], pt, a[1], b[1], c[1]))
    cands.sort(reverse=True)
    from wordscore import wseg
    scored = []
    for sc, pt, a, b, c in cands[:400]:
        r = check(pt, verbose=False)
        scored.append((float(wseg(pt)[0]) + qscore(pt) / 4, r, " ".join(a), " ".join(b), " ".join(c), pt))
    scored.sort(key=lambda x: -x[0])
    for s, r, a, b, c, pt in scored[:15]:
        print(f"\n[{s:.2f}] K-fit {r['k_fit']} nonK-ok {r['nonk_ok']} q {r['q']} word {r.get('word')}\n  {a} | EAST NORTHEAST | {b} | BERLIN CLOCK | {c}\n  {pt}")
