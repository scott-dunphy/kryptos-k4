# Prior work by two parallel teams (read before starting any new experiment)

Reviewed 2026-10-18 from fresh clones:
- **Barney** — https://github.com/barneyjm/kryptos-k4 (last commit 2026-10-18 08:21 -0400), map at https://barneyjm.github.io/kryptos-k4/. Large exact sweeps, numpy + multiprocessing, every tester validated on a planted solution, shuffled-CT baselines.
- **Reggie** — https://github.com/reggiechan74/kryptos-k4 (last commit 2026-10-18 11:03 -0400). Small, preregistered, standard-library runs with exact proofs and hash-pinned artifacts. Also contains a code review of *this* repo (`docs/prior-art-barney-scott-review.md`, pinned to our commit 3ce19e3).

Neither team solved K4 or found a positive signal beyond what is listed under "Signals" below. Positions below are **0-indexed** (cribs at 21-33 and 63-73) unless marked 1-based; Reggie writes 1-based (22-34, 64-74).

Before running something, grep this file as well as NOTES.md. "Ruled out" means within the stated bounds; the gaps each team flagged are listed at the end.

---

## 1. Barney — ruled out, no transposition

Periodic / keyword families
- Periodic Vigenère and Beaufort, key length 1-26, AZ and KA alphabets, plus ~13k keyword-alphabet (Quagmire) pairs; exact and with 1-2 crib errors.
- Correction they made: their first periodic pass silently dropped lengths 17, 18, 23-26 (it required >= 8 independent checks). Re-run (`longper.py`): 17, 18, 23, 24 give 0 fits across 1.8M alphabets; 25 and 26 are inconsistent for every standard alphabet pairing.
- Hand-modified alphabets: 1,850 AZ/KA variants with one letter moved or two letters swapped.
- One-slip tolerance: repeating (1-26) and progressive keys with any single crib letter treated as an error × 1,801,032 alphabets: 0.
- "Divided Berlin": separate periodic keys for the two halves, same or independent alphabets (13,456 pairs): neither half alone fits length 1-9 (east) or 1-7 (west).

Linear / compound keys
- Any linear rule mod 26 combining up to 5 of P[i], P[i±1..2], C[i±1..2], i, i², constant (1,544 rules).
- Polynomial keys mod 26/24/12/60, progressive keys.
- Two added periodic keys, lengths 2-26 each (Scheidt "key split"); clue-word pairs and triples at every phase; QUAE + two unknown splits.
- Grid keys (row key + column key), widths 2-30, every offset.
- 288 linear key models (repeating, progressive, grid W2-30, two combined keys, linear/quadratic formulas) × 842,006 dictionary-keyword alphabets × 10 arrangements × Vig/Beau: 0 (shuffled baselines also 0). Same models × 959,024 further constructed alphabets (decimated AZ/KA, keyword + reversed remainder, keyword + continue-from-last, 19,535 German words in four constructions): 0.
- Keyword-through-grid keys (keyword len 1-26 written into width 2-30 grid, read by columns either way), block-constant keys (new setting every n=2-30 letters, any phase), keyword + per-letter drift: 3,366 models × 1.8M alphabets × 10 arrangements: 148 fits vs 197 expected by chance, all decrypt to gibberish.
- Periodic affine C = a_i·P + b_i and mixed Vigenère/Beaufort by position: 0 for L <= 10; undecidable above.

Autokey
- PT and CT autokey, lags 1-96 (but see Reggie's note in §4: effective lags only CT 1-33, PT 1-8 in `autokey_dict.py`), key value read in plain/cipher/AZ/KA alphabets × dictionary alphabets: 0 exact. Near-miss version (707M configs): K4 best 10/24, shuffled 10-11/24.
- Backward autokey (key from 1-96 letters later in CT or PT), std + clue + dictionary alphabets: 0.

Running keys
- K1-K3 PT and CT, tableau (read 7 ways), Morse text, as running keys.
- English/German running text with keyword-mixed alphabets (842,006 dictionary alphabets, straight/transposed/reversed, all Quagmire arrangements): K4 best -5.17 en / -5.10 de, inside shuffled range -4.86..-5.21.
- Exact-lookup running key (`rkidx_run.py`): 8.9M-letter corpus (5 English + 5 German books, Sanborn's 2009 Smithsonian oral history, K1-K3, panel, tableau, Carter & Mace *Tomb of Tut-ankh-Amen* vol. 1), forward and reversed × 1,801,146 alphabets × 5 arrangements × 3 conventions × 3 indicator alphabets = 81M configs: 0 full and 0 single-block (13- or 11-letter) hits.
- Keys derived from K1-K3 by rule (initials, finals, letters after X, word lengths, every n-th letter; 90 strings) as running/periodic keys and as keyword alphabets: 0.

Digit / clock streams
- π, e, √2, φ, K2 coordinates, 1986/1989 as digit streams.
- Gronsfeld/Gromark/clock digit keys × dictionary-keyword alphabets: no alphabet brings all 24 implied key values below 16 (phrase alphabets: none <= 12).
- 1.35M clock-derived streams (Berlin-clock lamp counts/rows/bits/HHMM at every start minute and step, time-zone offset cycles, K2 coordinate and date digit cycles) × 8.45M implied-key vectors (dictionary/clue alphabets as Quagmire I-IV, Vig, Beau) × sign × offset: 0 on K4 and both shuffles; best 10/24 everywhere.

Gromark / chain addition (both alphabets free)
- Two-term recurrence, bases 3-26, primers 2-8 digits, every lag pair (2.78B primers; capped at base^len <= 2e7, see §4). Reproduces Bean 2021 exactly (39 survivors base 10 primer 5; 00351/00537 base 8). 804,684 survivors, none explains the width-21 rhythm (best 3 of 11 repeats = chance).
- Three-term chain, bases 3-26, primers <= 8 (2.27B, capped at 1.2e7): 790,052 survivors, best 3/11 = chance.
- Vimark/VIC-style chain addition primed by any of 221,577 dictionary or clue words, every two-lag rule: 6,976 chance survivors, none > 2/11.
- Raised letters (DYAHR, YAR) and clue numbers as primers.

Sanborn-phrase keys
- 192,569 runs of 1-5 words from the 2009 oral history, K1-K3, Morse, clue quotes → 613,440 phrase alphabets. Tested as Quagmire alphabets with periodic keys <= 26, as alphabets for an English running key (K4 -5.29 vs shuffled -4.99..-5.22), as digit-key alphabets, as the full-length key itself (none >= 15/24), × the 288 linear models (0), × autokey both sides lags 1-96 (0).

Masks (arbitrary substitution solved algebraically) — directly relevant to our working theory
- Arbitrary monoalphabetic mask on PT or CT side + periodic key: **inconsistent for L = 1-12, 14, 15, 17, 21, 22** (CT side also 18, 25). L = 13, 16, 19, 20, 23, 24, 26 are underdetermined with 24 cribs.
- Arbitrary mask + autokey, either side, all lags: 0.
- Arbitrary injective mask either side + grid keys (W2-30, column key free or repeating H2-13), two combined keys (L1<L2<=26), progressive keys, keyword-through-grid (14,408 models): 9,382 exactly inconsistent, 178 consistent (126 only because positions 27 and 65 are both R→P; 52 carry one parity check), shuffled CTs give 4-91 such survivors. Nothing stands out.
- Crib extension: 3,497 candidate words at the 4 crib edges re-testing the underdetermined mask periods: real words fit *less* often than random strings (24 vs 54 of 503,568); no fit reads.
- Independent alphabet per residue class (M-138-A strips / DRYAD sheets, any alphabets): impossible for periods dividing 42 (1, 2, 3, 6, 7, 14, 21, 42) plus 4, 5, 9, 10, 15, 17, 25.

Devices and odd bases
- Hill 2×2, 3×3, 4×4 at every alignment, with and without '?'; the 4×4 keys forced by the cribs are all non-invertible.
- M-94: 25 published disks, all disk orders via bipartite matching, all line offsets, all alignments: 0.
- Chaocipher: 116×116 clue alphabets, every dictionary+clue alphabet (842,054) on either disk against AZ/KA and reverses, 1M random dictionary pairs, × 26 relative rotations × 2 directions (402M rows): 0; then full 116 clue × 842,054 dictionary both disk assignments (1.02e10 rows): 0 exact, K4 best 11/24 vs shuffled 11 and 13.
- Wheatstone cryptograph (27-cell outer ring with blank vs 26-letter inner ring, 21.9M structured outer rings, inner solved exactly): 0.
- Base-27 additive (Z27, Z3³ trifid cube, Z9×Z3; 22.7M alphabet orders; periodic 1-23 and autokey 1-26): 0.
- Two-stage polyalphabetic with different tableaux (nonlinear composition, solved by connected components): std/KA in all roles L1,L2 <= 26: 0; clue × clue tableaux L <= 10 (5.3M): 0; stage 1 AZ/KA + stage 2 any of 842,006 dictionary alphabets (1.8e9 per role, L1,L2 <= 12) and 56 clue × 421,003 dictionary (1.26e10): hit counts equal the shuffled baseline (102 vs 120; 673 vs 665).
- Interrupted / event-driven keyword keys (restart/advance/pause on CT-letter triggers, PT word separators, words, carved lines): 11,077 models × 842k alphabets × 5 arrangements + Quagmire IV over 116² clue pairs: 0.
- Physical layout as key: tableau letter at same row/col (plain, mirrored, row ±3, col ±6); letter 1-27 rows above/below in same column on either half (4,368 configs): best 5/24. Skip-codes (every k-th letter) through the combined panels: noise.
- Excluded by single facts: any 5×5 Polybius system that outputs letters (all 26 letters occur in K4); Porta, Playfair, Bifid, Enigma-like (K→K at position 73).

## 2. Barney — ruled out, with transposition
- Columnar (both directions) before or after periodic substitution, exhaustive widths 2-11; widths 12-13 pruned with key period <= 14.
- 1,282 simple hand transpositions (reversal, boustrophedon, column/row reads W2-48, the carved 31-wide layout, decimations, rail fence), each with periodic, Hill, Quagmire and running keys.
- K3-style double grid rotations of K4, ?K4 and padded K4.
- Double keyword columnar with ~56 English + ~56 German clue words.
- English/German running keys behind columnar up to width 11: best = shuffled null.

## 3. Reggie — exact results and finite rejections

Proofs (cheap, worth quoting)
- **Pure transposition is impossible, any composition:** the cribs need 3 E's (2 in EASTNORTHEAST, 1 in BERLINCLOCK); K4 CT has only 2. No permutation-only pipeline works without substitution, insertion or deletion.
- Periodic bijective substitution at unchanged alignment (any alphabets) is contradicted for exactly p = **1-7, 9, 10, 14, 15, 17, 21, 25, 34, 42, 43, 45, 50** in 1-96 (witness: 1-based 25/67, T and L both → V). Matches our novel-batch2 list.
- **Clock-reset proof:** if the key restarts at the start of both cribs with the identical sequence of position-wise bijections (any key length, any alphabet), offset 3 gives T→V and L→V: impossible. Kills "restart keyword at EAST… and at BERLIN…" in every form that isn't content-dependent.
- Direct Enigma with standard reflector: impossible (K→K at 1-based 74).
- Direct autokey, exact, threshold-free, same alphabet both sides (AZ, KA), 3 equations, arbitrary primer: PT autokey rejected for lags **1-26 and 30-52**, CT autokey rejected for lags **1-73**; all other lags compatible only vacuously (zero checks). PT lag 26 is rejected through the chain 22→48→74, which immediate-neighbour checks (ours and Barney's) miss.
- No injective map from the 48 Shavian letters into 26 Latin letters; a 2-letters-per-symbol code cannot produce odd length 97 without a framing rule.

Finite rejections (narrow scope)
- ROUTE-001: 66 distinct routes (6 widths × 8 readings, inverses) × both orders × AZ/KA × 3 equations, periods 1-16 (identity route 1-96): no non-identity survivor. 282 identity-route "fits" at periods 27-29 and 53-96 are vacuous (every crib in its own phase).
- RUNKEY-001: corrected K2, K3, and K1+K2+K3 (PT and CT), every non-wrapping 97-letter window, both directions, AZ/KA, 3 equations (28,488 cases): 0; best 6/24.
- TRIFID-001: AZ+? and KA+? cubes, block periods 1-32, 42, 49, 63, 97, both directions: 0; best 4/24.
- MASK-AUTO-001: 12 fixed-primer autokey "masking" pipelines (KRYPTOS/PALIMPSEST/ABSCISSA primers): all fail cribs.
- MASK-FM-001: two literal Fractionated Morse maps: both streams contain invalid internal "xxx".
- WORD-SCRAMBLE-001: endpoint-preserving word-interior scrambling before a cipher, 24 fixed combinations: all fail.
- PHONETIC-SUBSET-001: W→V, word-final D→T / G→K respelling: changes none of the clue words, rescues nothing.
- LANG-001: GOST 1981 Russian transliteration layer (37,060 round trips): literal/fixed-substitution transport models fail.
- GROMARK-ALPHABET-001: one Barney survivor (base 16, lags 5/6, primer 6,12,12,4,4,8) has complete bijective alphabets satisfying all 24 cribs, but two different valid completions decode the non-crib text differently: **Gromark survivors are not identifiable from 24 cribs**, so passing the crib filter means nothing.
- STAT-001: Bean's width-21 repeated pairs reproduced (11 duplicate excess); fixed-width p ≈ 0.0004, corrected for max over widths 1-48 p ≈ 0.011.

Research-only (no cipher run): World Clock geography (Neptunbrunnen → Weltzeituhr bearing 68.25°, 471 m, i.e. roughly ENE 67.5°); Neptune/Le Verrier → Berlin history; KRASNOJARSK (11 letters, like BERLINCLOCK) as a weak coincidence; dated 1972/1984/1989/2015 photographs of the clock's city panels (1972 lower line PEKING/HANOI/MANILA; true-ENE panel and full 1989 list still unknown); Egyptian sign lists (no reversible mapping exists to test).

## 4. Problems the reviews found (ours and theirs)

In **our** repo (from Reggie's review, verified locally 2026-10-18):
- `run_e4.py:18` uses `n = S.shape[0] - 97`, so the last valid 97-letter window of every source is never tested; standalone K3 CT and the full K1+K2+K3 CT concatenation were not in E4. Reggie's RUNKEY-001 covers those windows (0 hits), so the gap is closed, but the off-by-one remains in the code.
- `run_e1.py:33-38` keeps survivors at m >= 5; NOTES E1 says m >= 4. Low-constraint tuples below the threshold are unexamined, not excluded.
- `results/anneal/q4dfs_real.log` is 0 bytes: the Quagmire-IV exact-DFS result in NOTES (no consistent key p = 1-7, 9-12) has no retained completion log. Re-run before citing it.
- `run_p2.py` PT-autokey lags only 1-7: does not cover primer lengths 8 (ABSCISSA) or 10 (PALIMPSEST). Reggie's exact audit now covers PT lags 1-26 and 30-52 for AZ/KA, not for dictionary alphabets.
- `run_alphapairs.py` reads unbundled `/usr/share/dict/words`; dictionary not reproducible. Keyrow scripts use keyword phase 0 only.
- Fingerprint: the KRYPTOS-letter ±2 rule has three crib exceptions as a biconditional (1-based 22 E→F and 31 E→G are within 2 but outside KRYPTOS; 72 O→F is inside but distance 9). Only K, O, R, S, T are represented (no P, Y). The corrected p = 0.0029 in `run_signal.py` is for the 15-statistic family, not for this exact rule. Barney gets p = 0.14 for "minor differences" over all 24 letters and 1 in 4,500 for the post-hoc KRYPTOS subset. **Do not use the fingerprint as a hard filter on candidates.**

In **Barney's** repo (from Reggie):
- `autokey_dict.py` skips lags with < 12 checks (PT < 8): effective lags CT 1-33, PT 1-8, not 1-96.
- Gromark sweeps skip base/length pairs over 2e7 (2-term) / 1.2e7 (3-term) states: "bases 3-26, primers 2-8" is not a full rectangle.
- The width-21 "explains k of 11 repeats" ranking is a heuristic, not a necessary condition.

## 5. Signals — what each team thinks is real

- **7/21 rhythm (Barney's one surviving fingerprint).** 11 repeated vertical bigrams at width 21: 1 in ~4,000 raw, ~1 in 210 after best-of-widths (Reggie: 0.011). Mostly carried by the ciphertext doublets: excluding doublet-stacked pairs it falls to ~1 in 10. In the known plaintext every column-5→6 step at width 7 is a CT doublet (NO→QQ, ST→SS, IN→TT; plaintext gaps +1, +1, +5). No grid key, compound key or Gromark key reproduces it. Note: independent alphabets per class are *impossible* at periods 7, 14, 21, 42, so the rhythm cannot come from a direct period-7/21 cipher.
- **Key is nonlinear.** CT entropy 4.55 bits/letter in 97-letter windows (random ceiling; K1/K2 4.35-4.39, K3 3.95). Implied crib keystreams have random-like linear complexity (Berlekamp-Massey mod 2 and mod 13) under all 8.42M alphabet variants; no single linear recurrence generates both crib runs. A short memorable key would need a nonlinear expansion step.
- **Mask + periodic nuance key is dead at most periods** (§1 Masks). Our working theory's "small nuance key" must be aperiodic (or periodic at 13, 16, 19, 20, 23, 24, 26 only), not autokey, not grid, not progressive.
- **Reggie: nothing.** Explicit position: no branch is favoured until it has an independent source-based motivation; expanding alphabets or keystreams to get readable output is not progress.

## 6. Facts and sources they surfaced
- Sanborn on BERLINCLOCK: "plain B taken, has the encipherment done to it, and out pops a cipher N" — Barney reads this as no transposition. Reggie flags the no-transposition premise as disputed testimony (Bob B comment 4 vs Elonka's account, Klausis Krypto Kolumne 2019-03-15).
- 2009 Smithsonian oral history (Barney has the text: `data/sanborn_oral_history.txt` in their repo): near 01:26:00 Sanborn describes cutting English sentences into strips, rearranging them and gluing them onto pages for CIA content review.
- RR Auction: Kobek and Byrne found five pages of scrambled text in Sept 2025 and reconstructed plaintext without the method; RR Auction video 2025-11-14 mentions the World Clock, the Egypt trip, the Berlin Wall fall, and K5 as a surviving alternate ending.
- Paradigm: verifier is SHA256 + Google Cloud KMS HMAC, $1 per guess; K5 (97 characters) announced for future release. All ten $1,000 CTF puzzles already solved (PK1 KA-Vigenère key PROVENANCE; PK2 columnar width 7; PK3 KA-Vigenère with 40-letter random key).
- Crib release dates per Paradigm: BERLIN Nov 2010, CLOCK Nov 2014, NORTHEAST Jan 2020, EAST Apr 2020 (public Aug 2020).

## 7. Gaps both teams list as still open
- Sanborn-phrase alphabets × interrupted keys, clock streams, Chaocipher (only clue/dictionary alphabets run).
- Chaocipher full dictionary × dictionary (~1e13 rows); non-keyword alphabets.
- Two-stage with longer periods (L > 12) or three stages.
- Mask + periodic at L = 13, 16, 19, 20, 23, 24, 26; mask + grid above W ≈ 11; both alphabets free with long keys — all undecidable with 24 cribs.
- Real M-209, M-138-A strip sets, SOE tables, one-time key sheets: no published material to test against.
- Fully constrained Gromark completion and identifiability (Reggie's next step: which plaintext letters are forced at position 1 under one survivor).
- Running key behind transposition wider than 11.
- Reggie: K3 photograph transcription; the World Clock's true-ENE panel and its full 1989 city list.

## 8. What they covered that we never ran (checked against NOTES.md, TEAM_BOARD.md, data/*.md on 2026-10-18)

New ground (not in our log at all):
- Arbitrary monoalphabetic mask solved algebraically + periodic / autokey / grid / progressive / two-key / keyword-through-grid keys (Barney `mask.py`, `mask_autokey.py`, `mg_mask_grid.py`).
- Hand-modified alphabets: 1,850 AZ/KA with one letter moved or two swapped (Barney).
- Sanborn-phrase alphabets: 613k from the 2009 Smithsonian oral history, clue quotes, K1-K3, against every key model (Barney).
- Backward autokey: key taken 1-96 letters later (Barney `backak.py`).
- German running texts (5 German books) and German clue words in double columnar (Barney).
- Crib extension: 3,497 words at the crib edges (Barney).
- Keyword-through-grid keys and keyword + per-letter drift (Barney `keyperm.py`).
- Running key behind columnar up to width 11; exhaustive columnar widths 9-11 (we did all keyed widths 2-8 plus dictionary/Myszkowski only).
- Mod-27 Vigenère and Z9×Z3 (we did only Z3³ and 5-bit XOR).
- Linear complexity (Berlekamp-Massey mod 2/13) of the crib keystreams and 97-letter-window entropy (Barney `bm.py`).
- Pure-transposition E-count proof; identical-restart-at-cribs proof; exact autokey lags up to 96 with chain propagation (Reggie).
- Language/encoding layers: GOST Russian transliteration, Shavian, word-interior scrambling, phonetic respelling (Reggie).
- Literal Fractionated Morse parse of K4 (Reggie; we only dismissed it structurally by length).
- Gromark completion identifiability: survivors have multiple valid alphabet completions (Reggie).
- World Clock bearing/photos research and Neptune history (Reggie; no cipher run).

Same family, far larger scale than ours:
- Chaocipher: their 1e10 clue × dictionary rows vs our lore-keyed wheels.
- Gromark/chain addition: 2.78B two-term + 2.27B three-term primers, bases 3-26, both alphabets free; Vimark with 221k dictionary primers (we did Bean's base-10 primers + VIC keyword expansion).
- Two-stage, different tableaux: dictionary × AZ/KA up to 1.26e10 configs (we did lore-word two-layer only).
- Clock streams: 1.35M streams × 8.45M dictionary implied-key vectors (we did unknown-alphabet clock tests, which are stronger per stream, on fewer streams).
- Linear key models × 1.8M constructed alphabets.
