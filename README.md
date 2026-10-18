# Kryptos K4 — cryptanalysis log

A systematic attack on K4, the unsolved 97-letter section of Jim Sanborn's *Kryptos* sculpture at CIA headquarters, carried out in October 2026 with Claude (Fable planning, Opus execution, a four-agent team phase). No solution was found. What the work establishes:

- **Eliminated, with validated code and null calibration:** every textbook and historic hand-cipher family a 1988–90 designer could plausibly have used — periodic, autokey, running-key, Gromark/VIC chain addition, split keys, every transposition family (single, double, route, decimation, grille-like), Hill, Chaocipher, M-94, Ragbaby, Nicodemus, rotors and Alberti disks, keyed tableaus with all ~396k dictionary keywords (with up to 3 carving slips), Berlin-clock and World-Clock keystreams, sculpture overlays and shadow projections, Sanborn's own published chart material, and the community's published reconstruction. See `NOTES.md` for every experiment with exact bounds.
- **One real statistical structure:** plaintext letters of the word KRYPTOS encrypt to within ±2 of themselves in the plain alphabet (9 of 10 known cases; shuffled-ciphertext null 0/5000). Everything else behaves like a hand-made substitution ("mask") followed by a small, aperiodic key. No construction from the tableau, keywords or geometry reproduces it exactly (best 17/24).
- **Working theory:** K4 was made by hand in two passes on Sanborn's 31-column worksheet — a personal masking chart plus a small "nuance" key — which cannot be recovered from 24 known letters. The decisive input is K5 (Paradigm holds it); `k5_depth.py` is built and validated for the day it appears.

## Layout

| Path | What |
|---|---|
| `NOTES.md` | The experiment log: hypothesis, bounds, result, verdict for ~180 tests. Start here. |
| `PLAN.md`, `TEAM_BOARD.md` | Planning rounds and the agent team's shared board. |
| `k4lib.py` | Ciphertext, cribs, alphabets, quadgram scorer. |
| `cribfilter.py`, `perms.py` | Numba crib-consistency kernels and transposition generators. |
| `candidate_check.py` | Score any 97-letter candidate plaintext (cribs, KRYPTOS fingerprint, English quality). |
| `k5_depth.py` | Depth attack for when the K5 ciphertext is released (`python k5_depth.py <K5CT>`). |
| `run_*.py` | One script per experiment family (names match NOTES.md headings). |
| `novel/`, `stego/`, `clock*.py`, `anneal2.py`, `wordscore.py` | Agent-team code (novel families, sculpture research, clock keystreams, annealing). |
| `data/` | Sculpture letter grids, research notes (charts, benchmark, Antipodes, Weltzeituhr, historic methods), quadgram table. |
| `results/` | Logs from every run. |

Interactive pages built during the work: a 3-D sun/shadow model of the sculpture and a 31-column worksheet of K4 in Sanborn's chart format (published as Claude artifacts; source in the session scratchpad).

## Running

```
python3 -m venv .venv && .venv/bin/pip install numpy numba pillow
.venv/bin/python candidate_check.py "YOUR97LETTERCANDIDATE..."
```

Large public-domain corpora used as running keys are not committed; `run_e4.py` and `run_initials.py` expect `data/kjv.txt`, `data/mobydick.txt`, `data/tut_smith.txt` and `data/texts2/*.txt` from Project Gutenberg / archive.org.

## Facts relied on

Ciphertext `OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR`; known plaintext EASTNORTHEAST at 0-indexed 21–33 and BERLINCLOCK at 63–73 (Sanborn); plaintext exactly 97 letters with cribs exactly placed (Kobek/Byrne 2025); Sanborn's K1/K2 coding charts (NYT 2010); Antipodes shows the copper's letters at positions 64 and 71.
