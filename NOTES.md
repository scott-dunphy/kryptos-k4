# K4 Attack Notes

Running log: what was tried, what worked, what failed. Newest entries at bottom of each section.

## Setup
- 2026-10-17: venv has numpy 2.5.4, numba 0.68.0.
- Quadgram stats: `data/quadgrams.txt` (389k quadgrams, from torognes/enigma). Corpus: `data/mobydick.txt`.
- Plan drafted by Fable planning agent (pending); execution by Opus.

## PRIMARY OBJECTIVE (standing)
- Obtain K5 ciphertext -> depth-2 pad-reuse attack (Sanborn 2025: K5 shares coded words at same positions). Secondary: auctioned coding charts/worksheets, more plaintext.
- Compute rationing: no new family unless (a) 1990 hand method Scheidt would teach AND (b) crib test with calibrated false-positive rate.

## Inherited claims (Gemini, unverified)
- Treated skeptically. Key unproven assumption: "no transposition".
- Claimed eliminated: direct periodic Vig/Beau/Quag3 p1-49, autokey, K1-K3 running key, Hill 2x2, base-5 Gromark.
- Claimed survivors: dual-alphabet Gromark primers (Bean 2021), no English found.

## Experiments
(entries: hypothesis | search space | result | verdict)

## What worked

## What didn't work

## Open ideas

### E0 — verify direct keystreams (sanity)
- Direct (no transposition) crib keystreams reproduce Gemini table: AZ-Vig BLZCDCYYGCKAZ / MUYKLGKORNA; KA-Vig RDUMRIYWOYNKY / ELYOIECBAQK. Confirmed. No visible keyword.
- Scorer calibrated: English text ≈ -4.4 mean log10/quadgram; K4 CT = -8.03; IoC CT = 0.0361.

### E1 — single transposition + periodic substitution (DONE, negative)
- Framework: `cribfilter.py` (numba residue-consistency kernel), `perms.py` (generators). Self-test `test_filter.py`: 6/6 synthetic route+Vig/Beau/Quagmire encryptions recovered.
- Space: 138,778 perms (identity; route grids W2-49 ragged blank start/end, 16x15 fill/read traversal pairs incl. snake/flips; ALL keyed columnar W2-8; lore-keyword columnar; each fwd+inverse) x periods 1-30 x 12 variants (Vig/Beau/VarBeau x {AZ,KA} PT/CT alphabets = Quagmire I-IV) x 2 orders (sub-then-transpose, transpose-then-sub). ~200M tuples, 18 s.
- Result: ZERO tuples consistent with all 24 cribs at m>=4 collisions. Full-route m distribution: m=0..3 only (2.09M / 57k / 428 / 8) = noise.
- Verdict: eliminated for p<=24 (cribs give m>=4 in >92% of tuples; p<=20 100%). p 26-30 weakly constrained, needs scoring (not done).
- Caveat: assumes cribs exact (no Sanborn typo in crib zone) and 97 letters, no nulls.

### E5 — progressive periodic key k(x)=K[x%p]+d*floor(x/p) (DONE, negative)
- Space: 57,906 perms (identity, routes W2-49, all columnar W2-7, fwd+inv) x p 1-30 x d 0-25 x 12 variants x 2 orders. 451 s.
- Result: zero survivors at m>=5. Verdict: progressive/Trithemius-drift Vigenère with simple transposition eliminated for p<=~24.

### Planner revision (Fable, after reading Bean 2021 + Scheidt quotes)
- Bean "minor differences" (crib PT letters in KRYPTOS map to CT letters ~2 apart in AZ) + vertical bigram stats argue AGAINST transposition, FOR positional cipher with near-AZ cipher alphabet and small key values / numeric base ("change the language base").
- New priority: alphabet-pair diagnosis — scan keyed alphabets for crib keystreams that are small digits / periodic / running-key matches.

### E3 — null removal + transposition + periodic (DONE, negative)
- Space: removals = every single non-crib position (73) + periodic null strides 14-48 at all offsets avoiding cribs + {0,96}; each x (identity + routes W2-49 + all columnar W2-6, fwd+inv) x p 1-26 x 12 variants x 2 orders.
- Result: 21 weak survivors, all p=23 m=5, same perm class (Beaufort KA/AZ, removal before pos 21). Best completed-key score -6.72 (gibberish). Noise.
- Verdict: single null / periodic nulls + simple transposition + periodic substitution eliminated (p<=~22).

### User question: other languages?
- Plaintext English (cribs English; Sanborn confirmed Kobek/Byrne English PT). Scheidt "masked the English language", wanted extinct language but CIA refused. Plan: test masked/misspelled English with lenient scoring; German words as keys/alphabets. German scoring = optional side check.

### E4 — running key, direct (DONE, negative)
- Validated: K1/K2 CT regenerated exactly from carved PT + KA Vigenère PALIMPSEST/ABSCISSA (`kryptos_texts.py`).
- Sources (fwd + reversed): K1/K2/K3 PT, K1+K2+K3 PT, K1/K2 CT, Morse text, Moby Dick, KJV Bible, Smith "Tutankhamen and the Discovery of His Tomb" (Carter's own book not on Gutenberg). Key letters indexed AZ and KA, 12 variants, any indicator shift.
- Result: best 12/24 crib agreement (KJV reversed) — noise level for ~10^8 offsets; needs 24/24. Kryptos-internal sources lower.
- Verdict: direct running key from these texts eliminated. Carter's actual book (The Tomb of Tut.ankh.Amen, 1923) still untested — need text.

### E2 — double route transposition (K3-style) + periodic substitution (DONE, negative)
- Space: 2,880 base routes (fill rows W2-49, read 15 other traversals, blanks end/start, + inverses) composed pairwise = 8.29M double transpositions x p 1-24 x 12 variants x 2 orders ≈ 4.8B tuples, 156 s on 7 cores.
- Result: 2 survivors, both p=24 m=5 (mirror pair) = expected noise.
- Verdict: K3-style double rotation + periodic Vig/Beau/Quagmire(KA) eliminated for p<=~22.

### Alphabet-pair diagnosis run 1 (inconclusive -> rerun)
- 110 lore/base alphabets x 395,948 dictionary-keyed alphabets (fwd/rev), both roles, 3 rules. Output buffer flooded by trivial period-26 matches (pos 21 & 73 share residue mod 26). Best cyclic key range seen 14 (need <=10ish for digit key). Rerun with tighter flags in progress -> results/alphapairs.txt.

### E-G — generalized Gromark/VIC chain-addition keystream, unknown alphabets (DONE)
- Code: `run_gromark.py`. Keystream d[i]=(d[i-L]+d[i-L+1]) mod b; crib test = weighted union-find on letter-position equations + injectivity.
- VALIDATED: base 10, L=5, dual alphabets -> exactly Bean's 39 primers (incl. 26717, 84393, 98800).
- Single alphabet (PT alphabet == CT alphabet): ZERO survivors for every config: b10 L4-7, b8 L5-7, b12 L5-6, b5 L5/7/8, b6,7,9 L6, b24 L4-5, b26 L4-5, b2 L20, b3 L12, b4 L10.
- Dual alphabets: survivors at rate 1e-4..4.5e-4 for every base (e.g. b10L7 3834, b26L5 4860).
- KEY RESULT: random uniform keystreams pass the dual test at 3.6e-4 (b10) / 4.3e-4 (b26). So Bean's 39 survivors (and Gemini's "viable" b8/b10/b12 primers) are EXACTLY chance level -> no evidence for Gromark. Dual-alphabet crib test has almost no discriminating power (24 cribs vs 2 free alphabets). Single-alphabet test is strong (random rate 0 in 300k).
- Implication: any "positional cipher + unknown dual alphabets" hypothesis cannot be confirmed by cribs alone; needs language scoring over alphabets (annealing) — expensive, low yield.

### E1-LOO — single-typo tolerance (DONE, negative)
- Drop each of 24 crib letters in turn (models one miscarved/misspelled letter), rerun E1 space (identity, routes W2-49, all columnar W<=8, fwd+inv) x p1-22 x 12 variants x 2 orders.
- Result: zero survivors at m>=5 for all 24 drops. Single-typo does not rescue route/columnar + periodic.

### P2 — autokey on keyword-keyed alphabet pairs (DONE, negative)
- Space: (110 lore/base alphabets x 395,948 dictionary-keyed alphabets, both roles, + lore x lore) x Vig/Beau/Var x key letter indexed in PT or CT alphabet x any indicator shift x {PT-autokey L1-7 (>=10 checks), CT-autokey L1-40 (24 checks)}. ~210 s.
- Validation: planted PT-autokey (L4) and CT-autokey (L17) with KA/HOLIDAY alphabets both detected.
- Result: zero hits. Autokey with KRYPTOS/lore/dictionary-keyed alphabets eliminated (direct).

### P3 — interrupted key restarting at word boundaries (DONE, negative)
- Models: A restarts at 21/25/63/69 (28 equalities), B at 25/63/69 (16), C at 21/63/69 (16). Over 110 lore x 396k dict alphabets both roles x 3 rules.
- Result: zero hits all models. Word-restart keyword Quagmire eliminated (direct).

### P1 — two-error crib tolerance (DONE, negative)
- Kernel `check_tolerant`: err = sum over residues (count - modal count). Space: E1 perms (identity, routes W2-49, columnar W<=8, fwd+inv) x p1-20 x 12 variants x 2 orders, t<=2, require m-err>=6.
- Result: zero survivors (20 s). Sanity: relaxed m-err>=2 on 20k perms gives 153 low-constraint noise hits, so kernel live.
- Verdict: up to 2 carving errors in crib zone do not rescue route/columnar + periodic.

### P5 — Weltzeituhr city ring (BLOCKED)
- Clock: 24 faces (time zones), 146 city names + date line (de.wikipedia). 1997 restoration added 20 cities and renamed others -> 1990 layout differs from current.
- Ordered list not available online. Need photo/list of faces (ideally pre-1997). Periodic zone-offset keys already covered by period-24 tests (E1).

### P4 — annealing, Quagmire IV free alphabets + periodic key (RUNNING)
- Annealer validated on synthetic Lacy-text encryption: p=3 recovers near-correct PT (-4.20); p=7 finds a WRONG crib-clean text at -4.61 -> overfitting: free dual alphabets manufacture English-like text. Real vs null (shuffled CT) comparison mandatory; raw score meaningless.
- Full run p1-30, 3M iters x 16 restarts, real + shuffled-null -> results/p4.log.

### Stego idea queue (from user question re Scheidt "a bit of stego")
- Misspelling letters (IQLUSION Q/L, UNDERGRUUND U/O, DESPARATLY A/E, PALIMPCEST C/S) as key/alphabet/period.
- Physical anomalies: raised YAR in K2 section, extra tableau letters, K4 line breaks on copper.
- Second layer within K4 PT (acrostic/nth letter) — not testable without PT.

### Alphabet-pair diagnosis rerun (DONE, negative)
- Flags: cyclic key range <=13, or <=8 distinct key values, or periodic p<=22. Over 110 lore x 395,948 dict alphabets both roles x 3 rules.
- Result: only 30 weak "distinct=8, period 27" hits (WELTZEITUHR/PARALYSES etc.) = chance. No digit key (min range 15), no period<=22.

### Stego words as alphabet keys (DONE, negative)
- EQUAL, QUAE, YAR, RQ, SOS, misspelled words (IQLUSION, UNDERGRUUND, DESPARATLY, PALIMPCEST, DIGETAL), Morse phrases, IDBYROWS/XLAYERTWO: as PT or CT keyed alphabets vs full dict+lore. No digit-key range (min 18), no period<=22.

### Weltzeituhr data (research agent)
- `data/weltzeituhr_cities.md`: post-1997 24-face list in ring order (Hungarian Wikipedia, 147 entries incl. Datumsgrenze) + official offsets. Pre-1997 layout (~80 names) NOT found.

## TEAM PHASE (started 2026-10-17)
- 4 Opus agents, messaging each other + TEAM_BOARD.md:
  - clock: Weltzeituhr city-ring / Mengenlehreuhr / time-zone keystreams
  - stego: sculpture anomalies (misspellings, raised letters, tableau extras, K4 copper layout) -> keys/grids
  - anneal: P4 free-alphabet annealing, null calibration, restart-convergence discriminator
  - novel: untested hand-cipher families (numeric base layers, tableau chaining, two-key masking, Bean minor-difference model) + team skeptic/code reviewer

### TEAM clock — C1..C6 Weltzeituhr / Mengenlehreuhr direct keystreams (DONE, negative)
Infra: `clocklib.py` (scan k=a*K[o+i]+b over 12 variants, a in 12 units, all offsets, fwd/rev; null_rate), `weltzeit.py` (1997 face list [HU] + 1990 reconstructions 1990a-d: drop Oslo/Jerusalem/Tel Aviv/Kapstadt/Seoul, Leningrad/Alma Ata/Bratislava, Kiew on Moscow face at 4 positions; other 15 1997 additions unknown).
- C1 city running key | 5 versions x dateline y/n x {strip,ue} x {concat, names reversed, faces reversed, in-face reversed, first/second/last letters} x AZ/KA x 12 var x all offsets fwd/rev | best 8/24 | null (random 1134-letter cyclic) best 7-9 | NEGATIVE.
- C1b deletion-tolerant city running key (skip up to 3 cities between names, models unknown 1990 removals) | longest crib-prefix match per segment | best 4+2 letters | NEGATIVE.
- C2 numeric per-city / per-letter streams (face idx, nominal/real UTC, hour-of-Berlin, name length, rank in face, face size, cumlen, diffs) k=a*K+b | best 11 (per-letter rank: long constant runs vs Beau-AZ repeated key values 10/6 — artifact), others <=9 | null 147-num best 7-10 | NEGATIVE.
- C3 Mengenlehreuhr: time sequences t0+i*step (step 1-60 min + primes etc., all t0) x {lamp counts per row, total lit/unlit, h, m, h+m, h*60+m,...} + digit streams (n1n2n3n4, hhmm, h m) | 1306 seqs, best 10/24 | NEGATIVE (noise for 5760-long streams x 12 units).
- C4 clock-geometry transpositions + periodic sub p1-30 (check_batch): Mengenlehreuhr block layout 97=4x(1+4+4+11+4)+1 read by row type (all 5! row orders, 2 inner orders, rev), width-24 grid with face-derived column orders (48 rotations/dirs, by size/utc/first city), columnar keyed by all 150 city names + clock words; fwd+inv | 2808 perms | ZERO survivors at m>=4 | NEGATIVE.
- C5 hour-ring readings (u+T) mod 24/12 (+0/+1) per city & per letter, all T; polynomial drift keys b+d*i+e*i^2+f*i^3 mod 26 (p=26 is barely constrained by E1) | best 9 (constant-run artifact); poly <=8 (null single offset: P(>=8)~3e-4 x 17576 tests) | NEGATIVE.
- C6 city running key with keyed alphabets: 410 alphabets (lore + 146 city names + clock words, fwd/rev) x {PA=CA=KX=X, PA=AZ/CA=X, PA=X/CA=AZ with KX in AZ/X} x 3 rules x {1997,1990a} x {concat,first} x fwd/rev | 49k tests, best 10/24, histogram smooth (9:73, 10:9) | NEGATIVE.
- Note: every key that is a function of face only (24-periodic in face order) or of a single date/time (short repeating digits) is already dead by E1 identity p<=24.

### TEAM novel — batch 1: new direct families (all DONE, negative). Code in novel/
- Hill nxn (novel/hill.py): brute-force each matrix row over 26^n against full crib blocks, AZ and KA numbering, every block alignment, both C=KP and P=MC. n=2,3: zero row solutions in all cases (eliminated). n=4: alignments 1,2 eliminated; alignments 0,3 have exactly 4 blocks = no checks (random CT also "passes"); decrypting all such solutions gives qscore -7.1..-7.9 gibberish.
- Two-key additive masks (novel/run_twokey.py, linear consistency over Z26 via left-null-space mod 2 and mod 13): k_i = A[i%p]+B[i%q] (p<q<=30), grid row+col key R[i//w]+C[i%w] (w 2-48), quadratic drift A[i%p]+c1*i+c2*i^2 (p<=25). Alphabets: 53 lore keywords + AZ, fwd/rev, both roles, vig/beau/var (33,708 key vectors). Every model with >=3 checks per prime: hits equal random expectation (empirical random rates match 2^-d2*13^-d13). No signal. Models with <=2 checks are uninformative.
- Chained / self-keyed (novel/run_chain.py, validated on planted KA/BERLIN cipher): k_i = a*X(P_{i-L}) + b*Y(C_{i-L}) [+ second lag] + c*i + d with a,b,c,d all free in Z26; lags 1,2,3,4,5,7,(1,2),(1,3),(2,3). Covers PT/CT autokey with any multiplier, P+C "sum" keys, walks on KRYPTOS tableau (X=Y=KA), with drift. 2809 lore alphabet pairs x 3 rules: ZERO hits (6-18 checks each). Shuffled-CT controls also zero.
- Digit-wise group ciphers "language base" (novel/groups.py): letters -> 5-bit vectors XOR (A=0/1, KA order, ITA2 Baudot = Vernam) and 3-trit vectors added mod 3 (Z3^3). No key period <=26; key letters unreadable. Eliminated (direct).
- Chaocipher (novel/chao.py, validated on Byrne test vector): starting alphabets = all 26 rotations of 106 lore-keyed alphabets for each wheel (7.6M pairs), decrypt from pos 0. Max 3 crib letters matched, same as shuffled-CT control. Eliminated for keyword alphabets.
- Periodic key with carry/borrow (+0/+1 noise per letter, "addition with carry"/base change) (novel/carry.py): p<=24 zero hits over lore alphabet pairs, random expectation <0.01.
- Bean "minor differences" stats check: AZ-Vigenere crib shifts within +-2 of zero: 11/24 (expected 4.6; binomial p~0.002 if zero-centred is a priori; but best 5-wide window anywhere p=0.047, 6-wide p=0.056 vs both uniform and CT-frequency nulls). KRYPTOS-letter subset 9/10 within +-2 is a post-hoc split. Weak evidence; note O->F (-9) breaks any pure small-shift model, and E maps to F,G,Y (+1,+2,-6) so no fixed substitution + |key|<=2 model fits.

### TEAM stego — S0 research: sculpture anomalies catalogue (DONE)
- `data/sculpture_anomalies.md` (sources inside); verbatim grids `data/sculpture_left.txt` (869 = 865+4 '?') and `data/sculpture_right.txt` (867), Elonka/Gwyn transcript, counts match Wikipedia.
- K4 = left row 24 cols 27-30 + rows 25-27 (31 each). BERLIN straddles the row 26/27 break (BER|LIN). K4 rows level with tableau rows X,Y,Z,footer. YAR superscripts and the extra tableau L are both on row 14 (first line of the lower plates).
- Misspelling cells: K1 IQLUSION Q -> CT K at (1,24); K2 UNDERGRUUND U -> CT R at (5,23); K3 DESPARATLY A -> CT (16,27).
- New statements: 2025 open letter (Egypt 1986 trip + 1989 Berlin Wall fall; World Clock; "delivering a message"; "Who says it is even a math solution?"); RR lot lists "original coding system for K4" and "plain texts used for screen cutting K4 (2 pieces)"; K5 CT held by Paradigm, unreleased, shares coded words in same positions as K4.
- BUG: kryptos_texts.K3_PT missing "OF" (DETAILSOFTHEROOMWITHIN). Correct 336-letter K3 PT reproduces carved K3 CT via rotation perm (saved stego/k3perm.npy).

### TEAM stego — S1 physical overlay keystreams (DONE, negative)
- Key(i) = letter at K4 cell (r,c) transferred onto tableau / tableau w/o label col / left panel / K1-K3 PT laid in place; row offset dy -27..27, vertical flip, dx -4..4, mirror, left/right flush. 15,840 keystreams x 24 (variant, AZ/KA key index), any Quagmire shift.
- Best 8/24 agreeing cribs; random-key null P(>=8) = 6e-4 per stream -> expected ~4 at this volume. Noise. (stego/overlay.py)

### TEAM stego — S2 Hill cipher n=2,3,4 direct ("HILL" down the tableau's right column) (DONE, negative)
- AZ and KA numbering, enc and dec matrix, all block offsets. n=2 (11 crib blocks) and n=3 (6-7 blocks): ZERO consistent matrices. n=4: only 4-5 blocks (offset 0/3 exactly determined) -> 16+ solutions all decrypt to gibberish (qscore -7.1..-7.9). n=1,2,3,4 eliminated direct. (stego/hill.py)

### TEAM stego — S3 spiral & diagonal routes + periodic (DONE, negative)
- K3 "upper left hand corner ... widening the hole" -> spiral (4 corners x cw/ccw x in/out) and diagonal (4 corners x zigzag x dir) traversals, paired with each other and the 16 E1 traversals, W2-49, blanks end/start, fwd+inv: 71,044 perms x p1-26 x 12 variants x 2 orders. Zero survivors at m>=5. Planted spiral+Vig self-test recovered. (stego/spiral.py)

### TEAM stego — S4 2-D running keys from the sculpture (DONE, negative)
- Streams: left CT, K1-K3 PT in place, tableau, each plate; read rows/cols/cols-up/cols-RL/col-snake/diag/antidiag, fwd+rev; all offsets, 24 variants. Best 9/24; null per stream max 7-9. Noise. (stego/runkey2d.py)

### TEAM stego — S5 '?' as 98th K4 symbol (98=7x14) (DONE, negative)
- '?' non-constraining; PT crib offset 0/1; routes W2-49 + columnar W<=8 + K3-style double rotations on exact 98 grids (and inverses), 98,876 perms x p1-26 x 12 x 2 orders. Zero survivors m>=5. (stego/q98.py)
- Tableau linear read-out keys (novel/tabwalk.py): k_t = a*(t mod w) + b*(t div w) + s, t=i+o, all a,b,s, offsets o<26w, w 2-36, 12 variants (models reading the KA tableau row-wise/col-wise incl. 31-wide rows). Best crib agreement 9/24 vs shuffled-CT null 10/24. Eliminated.
- Periodic affine C = a_r*P + b_r (multiplicative Vigenere), lore alphabets both sides (11,236 pairs): p<=15 zero hits (random exp 0); p16-24 hits ~ chance. Eliminated p<=15.
- Porta (standard 13-alphabet reciprocal): impossible directly — E->F at pos 21 maps first-half to first-half, which Porta never does.

### P4 result (lead) — free-alphabet Quagmire IV annealing p1-30 (DONE, no signal)
- Real vs one shuffled-CT null: crib-clean solutions only for some p; where both exist, real-null gap -0.09..+0.26 (below 0.3 alert). p>=19 both real and null reach -4.5..-4.7 "English" = overfit floor. Many p (1-7, 9, 11, 12...) no crib-clean solution found in either.
- Verdict: no evidence for periodic Quagmire IV with non-word alphabets. Handed to anneal agent for multi-shuffle null + convergence test.

### TEAM stego — S6 Sanborn's 31-column worksheets -> long period / row-restart keys (DONE, negative)
- Fact: K1/K2 coding charts (NYT 2010, kryptools Sheets) are 31-column grids (PT row / key row / CT row, key continues across rows, '?' does not consume key; rows numbered by panel line 1..). NOVA 2007 shows the panel-4 worksheet as exactly 14 lines x 31 = K3(336)+?+K4(97) = 434. So K4 lives at worksheet row 10 col 27 (0-idx) — same as sculpture.
- Test: periodic p=25..48 direct (E1 only went to 30 and only by collisions): pin key at crib residues, decrypt pinned positions, quadgram-score non-crib windows. Best -7.12 (p29 Beau KA/KA) vs shuffled-CT null max -6.78 -> noise. Row-restart key (key idx = ((i+o) mod 31) mod p, p2-30, all o): zero crib-consistent. (stego/p31.py)

### TEAM stego — S7 K3-style decimation transposition on K4 (DONE, negative)
- Fact: K3 transposition is exactly CT_idx = (192*PT_idx + 191) mod 337 (n+1 = 337 prime; missing value = 336). Verified on carved CT.
- Test: j = (a*i+b) mod M compacted to 97, M=97..110, all a coprime, all b, + inverses = 143,520 perms x p1-26 x 12 variants x 2 orders. Zero survivors at m>=4. Planted self-test detected. (stego/affine.py)

### TEAM clock — C7..C12 clock arithmetic perms, unknown-single-alphabet keystream tests (DONE, negative)
- C7 'clock arithmetic' transpositions + periodic sub p1-30: affine decimation i->(a*i+c) mod 97 (all a,c), Josephus counting-out (k 2-97, all starts), decimation on 98/100/104-circles dropping slots>=97; fwd+inv, 62,666 perms | ZERO survivors at m>=4 | NEGATIVE.
- NEW TOOL `clocksingle.py`: numeric keystream vs UNKNOWN single mixed alphabet (PT alph = CT alph = X, like Kryptos tableau with unknown keyword). Vig/Var: pos(C)=pos(P)+K[o+i]+b via run_gromark.consistent mode 1 (multiplier absorbed by X). Beaufort: pos(C)=K+b-pos(P) via new signed union-find (`consistent_beau`, conservative). Validated on planted WELTZEITUHR-alphabet keys (exact offset recovered). Null: 0 hits in 2.4e7 random-key Vig tests (uniform and base-5) and 0 in 2e6 Beau tests.
- C8/C9 all Weltzeituhr numeric streams (402: per city/letter face, UTC nominal/real, hour mod 24/12 all T, lengths, ranks...) + Mengenlehreuhr streams (1107: lamp counts, h/m, digit streams, steps 1-60+) + city-name letter streams AZ/KA-indexed (20) vs unknown single alphabet, Vig/Var + Beau, all offsets/dirs/indicator | ZERO hits | NEGATIVE.
- C10 (side check, E4 extension) running-key texts with key letters AZ/KA-indexed and UNKNOWN single PT/CT alphabet (Vig/Var + Beau): K1/K2/K3 PT, K1/K2 CT, K123 PT, Morse, Moby Dick, KJV, Smith Tut | see results/clock10.log (Kryptos texts + Moby Dick: zero hits).
- C11 segment-constant keys (arbitrary value per segment, segment lengths = face sizes / city-name lengths / Mengenlehreuhr rows 1,4,4,11,4, all phases, fwd/rev), fixed alphabets | ZERO consistent with m>=4 | NEGATIVE.
- C12 analog clock-hand streams (minute/hour marks, hour 1-12, hand angle, steps 1-97 min) + consecutive calendar dates 1989-1991 as digit streams (DDMMYY etc.), day-of-month/week/year | fixed best 10/24 (null), unknown-single-alphabet Vig/Beau ZERO hits | NEGATIVE.

### TEAM stego — S8 "LAYER TWO": double keyword encryption (DONE, negative)
- C = E2(E1(P,w1),w2), each layer Vig/Beau/VarBeau on AZ or KA (same alphabet PT/CT per layer, K1/K2 style), w1,w2 from 96 lore+stego words (EQUAL, QUAE, YAR, RQ, SOS, HILL, LAYERTWO, PALIMPCEST, KOMITET, ...), all offsets: ~2e7 configs. Best 9/24 crib letters (noise; planted KRYPTOS+ABSCISSA recovered 24/24). (stego/twolayer.py)
- Also: bottom-plate letters displaced vs the 14x31 worksheet (A row14, T row17->18, T row19->20, IT row22->23) = "A T T IT"; probably aesthetic (S-curve). Not pursued.

### TEAM clock — C13 tableau-style city running key over dictionary alphabets; T1 Trifid (DONE, negative)
- C13 Kryptos-tableau style running key from Weltzeituhr names: PA=CA=key-index alphabet=X for every lore/city/dictionary keyed alphabet (396,172 incl. reversed), Vig/Beau/Var, city concat 1997/1990a fwd/rev, all ~1100 offsets, indicator free; test = all 13 EASTNORTHEAST crib values equal (FP 26^-12 x 1.4e10 tests ~ 1e-4) | ZERO | planted SCHWARZ-alphabet key recovered 24/24 | NEGATIVE.
- T1 Trifid (Delastelle 3x3x3, base 3 = "language base"), direct decryption: cube = keyed 27-symbol alphabet (all 396k lore/city/dict keywords, fwd/rev, filler at start/end) x 6 coordinate-role permutations x periods 1-97 (~4.6e8 decrypts) | best 10/24 crib letters, smooth histogram (10:4, 9:40, 8:528) = noise; planted KRYPTOS cube n=7 recovered 24/24 | NEGATIVE (keyword cubes). Code run_trifid.py / run_trifid2.py.
- C10 completed sources so far: K1-K3 PT/CT, K123PT, Morse, Moby Dick (AZ+KA idx) — zero hits vs unknown single alphabet (Vig+Beau). KJV/Smith still running -> results/clock10.log.

### TEAM clock — C14 clock letter->number tables as autokey (DONE, negative)
- Tables L(x): Weltzeituhr face idx / UTC of first or last city with initial (or final) letter x, #cities per initial, letter frequency in all names (1997, 1990a); Mengenlehreuhr lamp count of letter value as minutes/hours (A=0/1). CT-autokey k_i=a*L(C[i-lag])+b, lag 1-12, 12 variants x 12 multipliers (24 checks) + unknown single alphabet Vig/Beau; PT-autokey within cribs (6-11 checks). 66k fixed tests best 8/24 (null); single-alphabet ZERO hits | NEGATIVE.
- C10 COMPLETE: KJV (3.2M letters) and Smith Tut text also zero hits (AZ and KA key indexing, Vig/Var + Beaufort, unknown single PT/CT alphabet, all offsets fwd/rev, indicator free). Running key from these texts with any single mixed alphabet ELIMINATED (direct).
- C15 (from stego): date streams extended to 1985-1991 (covers 1986 Egypt trip, 1989-11-09) and K4 worksheet geometry (row=10+(i+27)//31, col=(i+27)%31) clock functions (col, row, UTC[col mod 24], (row*31+col) mod 24, Mengenlehreuhr lamps of row:col, ...): fixed best 10/24, unknown-single-alphabet Vig/Beau ZERO | NEGATIVE. Single fixed dates as digit keys = short periodic -> already dead by E1.
- STRUCTURAL FACT (novel): direct periodic substitution with ARBITRARY per-column alphabets (any Quagmire, free alphabets, any per-column monoalphabet) is impossible at p in {1-7, 9, 10, 14, 15, 17, 21, 25, 34, 42, 43, 45}: some column gets the same CT letter from two different PT letters or vice versa (e.g. pos 24 T->V and pos 66 L->V, 42 apart, which kills every divisor of 42, including 7 and 21). Allowed p<=30: 8, 11, 12, 13, 16, 18, 19, 20, 22, 23, 24, 26-30. So Bean's width-7 CT regularities CANNOT come from any direct period-7 cipher. Annealers must never find crib-clean direct solutions at forbidden periods (bug check).
- Half-free periodic Quagmire (novel/halffree.py): one alphabet keyed (395,948 dictionary/lore keyword alphabets, fwd+rev), the other completely FREE (union-find + injectivity), both roles, p 1-26. Hits equal random-permutation expectation at every p (only p=13,16,19,20,23,24 are weak tests, 13-96% random pass rate). p=8: 1 hit (MANATOID, keyed PT side), expected ~0.4: chance. Eliminated.
- Math-constant keystreams (novel/constants.py): pi, e, sqrt2, sqrt3, sqrt5, phi, ln2 as decimal digits, 2-digit numbers mod 26, base-26 and base-13 expansions, any offset, fwd/rev. Fixed AZ/KA variants k=a*K+b: best 8-10/24 (null). Unknown single mixed alphabet (clocksingle): zero hits. Eliminated.
- Block (in-row) transposition W2-9 (same column permutation applied to every row) + periodic p1-30, 12 variants (novel/blockperm.py): W<=8 nothing at m>=5; W9 2 distinct m=6 p=21 tuples, completed keys give gibberish (-7.25). Noise.
- Row-permutation ("strip") transposition + periodic substitution (novel/rowperm.py, DFS over placements of crib-bearing rows, validated on planted w=8/p=11 cipher): write PT in rows of width w, permute full rows, read rows (preserves residues mod w, so compatible with Bean's width-7/21 stats). w 6-30 x p 1-30 x 12 variants x 2 orders: max m=5 (w=6), same as shuffled-CT control (w=6 m=4: real 81 vs shuffled 191). Eliminated. (w<=5 not run: too many placements.)

### TEAM stego — S9 null LETTERS (masking by inserted letters) (DONE, negative)
- Delete all occurrences of letter set S (|S|<=3, S within {A,B,C,D,E,H,I,J,O,U,W,X} = letters absent from crib CT), then identity/routes W2-40/columnar W<=7 (fwd+inv) x periodic p1-24 x 12 variants x 2 orders on the shortened text. 8 survivors, all m=5 at p19-24 (noise, cf. E3). (stego/lettnull.py)

### TEAM stego — S10 Carter's book as running key (closes E4 gap) (DONE, negative)
- archive.org OCR: The Tomb of Tut.ankh.Amen vol 1 (1923, contains the K3 source passage at letter 139,284) and vol 2 (1927); letters only, fwd+rev, AZ/KA key index, 12 variants, any shift. Best 11/24 (vol2), 10/24, 9/24 = noise for ~600k offsets (needs 24). Note one 9/24 hit sits right after the K3 passage ("...PEERED IN LORD CARNARVON...") — not significant. (stego/carter.py; texts data/web/carter/)
- Inference (for team): Sanborn 2025: K5 (97 chars, same system) shares "some of the same coded words in the same position" as K4 -> identical CT words at identical positions => key depends on POSITION only (not on preceding PT/CT: argues against autokey/chaining) and against a whole-message transposition unless shared. Consistent with Bean + 1:1 statements.

### TEAM stego — S11 tableau-overlay keystream x keyed alphabets (DONE, negative)
- s_i = tableau letter level with each K4 cell (rows X,Y,Z,footer; also tableau shifted 1 row and top/bottom halves swapped; dx -2..2; mirror; with/without label col), indexed AZ or KA: 74 keystreams. Test posC - posP - s = const (and Beau/Var forms) over (AZ,KA,revs) x 395,948 dictionary-keyed alphabets both roles, and lore x lore. Best 11/24 (~2e8 tests) -> noise. (stego/overlay_alpha.py)

### TEAM stego — summary of the sculpture/stego track
- All simple sculpture-derived keys/structures are negative: overlay keys (S1, S11), 2-D running keys (S4), Carter book (S10), Hill (S2), spiral/diag/decimation transpositions (S3, S7), '?' as 98th char (S5), long period / 31-col chart keys (S6), double keyword layers (S8), null letters (S9).
- Physical facts worth keeping: Sanborn's working grid is 31 columns (K1/K2 charts, 14x31 panel-4 sheet); K3 perm = decimation x192 mod 337; YAR + extra L both on row 14; per-row constant (Caesar/monoalphabetic per copper row) impossible (E at 21 -> F, E at 30 -> G within row 25).

### Two stacked tableau layers (user idea) (DONE, negative)
- Model: layer 1 = keyword W (221,583 dict+lore words, len<=14) on tableau T1 in {AZ,KA}, rule vig/beau/var; layer 2 = unknown periodic key p2 1-22 on T2 in {AZ,KA}, any rule; both orders (L2∘L1, L1∘L2). Crib test: residual layer-2 key periodic, m>=6.
- Validation: planted SHADOW(KA) + CLOCK(AZ) recovered (p2=5).
- Result: zero hits (22 s). Two-tableau stacking with a dictionary keyword on one layer eliminated.

### Lead check of stego's K3-decimation insight (DONE, negative)
- stego: K3 transposition is exactly CT = (192i+191) mod 337 (decimation). Sanborn worksheets 31 columns; panel-4 sheet 14x31 = K3+?+K4.
- Lead test: all affine decimations mod 97 (9,312) and mod 98 with '?' slot dropped (4,116), fwd+inv, x p1-30 x 12 variants x 2 orders. Zero survivors m>=4. Compositions of decimations mod 97 are decimations, so double decimation covered too.
- K3_PT fixed (added OF, 336 letters) per stego; E4 rerun.
- Transposition + periodic substitution with ARBITRARY per-column alphabets (novel/anypoly.py, per-column injectivity, E1 perm set 138,546 x p1-30 x 2 orders): p=1,2 zero perms pass; p=3: 8 (order A only); p=4: 359; p=5: 657; p>=6 tens of thousands. Annealing the p independent substitutions (crib-pinned) on survivors p=3-5 (novel/lowp_anneal.py): REAL best -4.02 (p=5) / -4.28 (p=4) vs SHUFFLED-CT null -4.02 / -4.27 -> pure overfitting, fluent-looking false English. LESSON: with 97 letters, arbitrary per-column alphabets are unidentifiable by quadgrams already at p=4; any free-alphabet result needs a null at the same p.
- E1 extended to lore-keyword Quagmires (novel/lore_quag_trans.py, validated on planted BERLIN Quag-III + columnar): E1 perm set (138,778) x 765 alphabet variants (53 lore keywords: (A,A),(A,AZ),(AZ,A),(Arev,AZ),(AZ,Arev) x vig/beau/var) x p1-24 x 2 orders (~5e9 tuples): ZERO tuples at m>=5. Eliminated.
- Block-held key k_i = K[((i+o)//n) % p] (each key letter held for n letters), n 2-12, p 1-26, all o, lore alphabets both sides: zero hits (random exp 0). Eliminated.
- Wheatstone/Wadsworth cryptograph = literal "cipher clock" (novel/wheatstone.py, both modes validated on planted encryptions): outer ring AZ/KA/reversed with N_o = 27-39 cells (blanks at start/end/grouped), inner ring 26 letters COMPLETELY FREE, geared hands, clockwise moves (full turn on repeat). Mode PT-on-outer (two per-crib offsets) and CT-on-outer (one global offset): ZERO consistent configurations; 30 shuffled-CT controls also zero. Eliminated.
- Review (novel): clocksingle.consistent_beau, run_trifid, clocklib.scan_num checked, no bugs. novel tested Wheatstone/Wadsworth cipher clock (free inner alphabet) = zero consistent (novel/wheatstone.py). Note: periodic sub with ANY per-column alphabets impossible at p in {1-7,9,10,14,15,17,21,25}; face-keyed (24-periodic) models survive only for p=24 with free per-face alphabets, which cribs cannot test alone.
- CORRECTION (lead + anneal power test): face-keyed period-24 model is NOT closed. Annealing on 97 letters recovers plaintext only for p<=3-4, so P4's p=24 result means "untestable", not "negative". Status by sub-model:
  * CLOSED: fixed KA/AZ alphabets and keyword-keyed alphabets at p=24 (E1, alphapairs); the specific clock-derived 24-face shift vectors (face UTC, sizes, hours etc.) with fixed alphabets AND with one unknown single mixed alphabet (C2/C8/C9, cyclic per-city streams).
  * NOT TESTABLE: one unknown mixed alphabet with ARBITRARY 24 face shifts (Quagmire III p=24). At p=24 only 5 crib pairs share a residue (21/69 E,C->F,M; 22/70 A,L->L,Z; 23/71 S,O->R,F; 24/72 T,C->V,P; 25/73 N,K->Q,K), giving 5 four-term equations pos(C1)-pos(P1)=pos(C2)-pos(P2) on a free alphabet, which are trivially satisfiable. clocksingle does NOT cover this (it needs a known shift vector). Free per-face alphabets: even less constrained. Needs an external key source or much stronger language model.
- Dictionary-keyword columnar (all 396k-word list words of length >=9, distinct orders) + Myszkowski transposition (every word with repeated letters, distinct patterns): 574,098 perms (fwd+inv) x p1-24 x 12 variants x 2 orders (novel/dictcol.py): zero at m>=5 (13 at m=4, all p=24 = noise). Eliminated.
- Playfair (any square) impossible directly: CT doublets at even-aligned digraphs (18,32,42,46) and odd-aligned (25,67) -> both pairings contain a same-letter digraph, which Playfair never outputs. Also all 26 letters occur in CT, ruling out any single 5x5-square system (Playfair, Two-square, Bifid-25, Polybius-based) unless two squares omit different letters.

### Themed keywords x dictionary alphabets (DONE, negative)
- 256 themed alphabets (navigation/time/concealment/Berlin/Egypt/tradecraft words, fwd/rev) x 395,990 dict alphabets, both roles, 3 rules (~3e8 pair-rules).
- Best: PT=BECKONER, CT=DISCOVERY, key range 11/12 values, 60 pairs at range<=12.
- Null: 9M random alphabet pair-rules -> 18 at range 13, scaling to ~3e8 predicts dozens at 12 and a few at 11 => chance. Flagged key has no chain (Gromark-type, any base/lag/offset) or period <27 structure. NOISE.
- Carter & Mace "The Tomb of Tut.ankh.Amen" vol I (1923) = K3's actual source (contains "Slowly, desperately slowly..."): text fetched from archive.org (data/carter/carter_vol1_letters.txt, 282,392 letters). Running key, all offsets, fwd/rev, key letters AZ- and KA-indexed, 12 variants with k=a*K+b: best 10/24 (AZ), 11/24 (KA) vs shuffled-text null 12/24. Unknown single mixed alphabet (clocksingle, a=1): zero hits. Eliminated (closes E4's open item).

### 3A — key-fragment English-likeness (DONE, negative)
- For 110 lore/base x 395,948 dict alphabets (both roles) x 3 rules x key rendered in PA/CA/AZ: quadgram score of the two crib key fragments (13 + 11 letters).
- Real max -4.66 (MENGENLEHREUHR~rev/ABSURD) vs null (random CT alphabets, 1/8 size) max -4.62. No signal: running-key-from-English-phrase with word-keyed alphabets not supported.
- C16 (novel's idea a) Weltzeituhr-derived KEYED ALPHABETS + periodic key p1-30, direct: 750 alphabets (keyed from ring-order strings: name concat / initials / last letters starting at every face, both ring directions, 1997+1990a; each city name; all reversed) x pairs {(X,X),(AZ,X),(X,AZ),(KA,X),(X,KA)} + all ring-alphabet pairs (X,Y) x vig/beau/var | ZERO configs consistent with m>=4 (equal-size random-alphabet null also 0) | NEGATIVE. Idea b (plaintext-selected time-zone offset) = PT-autokey with clock table, covered in C14 within cribs.

## STATUS SUMMARY (2026-10-17, after team phase; anneal final pending)
- No candidate plaintext. Every survivor at random-control level; annealed "English" matches shuffled-CT control (overfit).
- Closed (validated, crib-only so independent of "masked English"): see entries above — transpositions (route/columnar/double/decimation/spiral/clock geometry) x periodic sub; 1-2 crib errors; autokey/chained/interrupted keys on KA/lore/dict alphabets; running keys (K1-K3, Carter 1923, Bible, Moby Dick, constants); Gromark/VIC single-alphabet all bases; Weltzeituhr/Mengenlehreuhr keys; tableau overlays; stacked layers; Hill 2-3; Chaocipher; Wheatstone; Trifid; nulls; '?' as 98th.
- Structural facts: direct periodic with ANY alphabets impossible at p 1-7,9,10,14,15,17,21,25 (novel). Bean's Gromark survivors = chance. Free-alphabet annealing on 97 letters only decisive for p<=3-4.
- Open / untestable by cribs: single unknown mixed alphabet + long arbitrary numeric key (Quagmire III p=24 face-keyed, OTP-like additive); free alphabets with p>=6; hand-made coding charts.
- What would move it: K5 ciphertext (shared words at shared positions expose key structure), auctioned coding charts, more plaintext.
- C16 scope caveat (novel): direct p=27-29 have no crib residue collisions (m=0 always) and p=26/30 have only 1, so "zero at m>=4" is uninformative there. C16 (and C4/C7 transposition runs reported as p1-30) are eliminated only for p<=~24-25.

### VIC-style keyword digit expansion (DONE, negative)
- 221,583 dict+lore words (len 3-20) -> digits by alphabetical rank mod 10 / A=1 / A=0 -> chain addition to 97 (d[i-L]+d[i-L+1] or d[i-L]+d[i-1]), base 10 or 26, +/- sign; single unknown mixed alphabet test.
- Validation: planted SHADOW rank-chain key under KA found. Null 200k random seeds: 0 hits.
- Result: zero hits. VIC/Gromark-style keyword-seeded additive on a single keyed alphabet eliminated.

### P4 verdict (from anneal's p4b + planner review)
- p1-30 x 3 shuffled nulls: no signal. p>=19 real and null both at -4.5..-4.7 overfit floor; gap <= 0.26.
- p=19 real crib-clean 8/8 vs null 0/8 = ARTIFACT: positions 27 & 65 share residue mod 19 and both are R->P (Bean's repeat), so real CT is trivially consistent; shuffled CT breaks it.
- Exhaustive q4exact: p=6,7 all keys, zero consistent.
- CLOSED: "no signal, limited power". Stop free-alphabet annealing. Better null would shuffle only the 73 non-crib letters.

### Key-randomness diagnostic (DONE)
- Fraction of 24 crib key values within ±3 of 0 (exp 6.5 if uniform): AZ/AZ Vig (=VarBeau mirror) 12/24, binomial p=0.013; all KA and Beaufort combos at chance (3-9/24). After ~6 independent variant look-elsewhere -> p≈0.08. Weak; consistent with novel's Bean-stat check. Only hint: CT letters sit near PT letters in plain AZ order (signed small shifts) — no family tested reproduces it.

### P6 — split-key (CKM-style) direct, run by planner in-memory (negative; re-log pending from novel)
- Two-key k=K1[i%a]+K2[i%b], a<b 2..13, a+b<=21, 12 variants AZ/KA: 720 tests, 0 consistent. Null 30 shuffled CTs: 0/21,600. Planted (7,11) found.
- Three-key a<b<c, a+b+c<=20: 960 tests, 0 consistent.
- Open sub-items assigned: novel (keyword component + E1 transpositions), stego (structured pad on digit-encoded plaintext).

### STANDING ITEM: obtain K5 ciphertext
- Sanborn 2025: K5 shares coded words in same positions as K4 => pad/key reuse => depth-2 attack (VENONA-style) is the only decisive test for the open OTP-like model. Sources to watch: Sanborn releases, RR Auction catalogue, Paradigm, press.

### TEAM stego — S12 cross-test with clock (DONE, negative)
- 178 sculpture-motivated transpositions (W31 panel layout: row-fill -> every row/col/snake/spiral/diagonal read; K3-analog decimation mod 98 with missing value 97; + inverses) x both orders x clock's keystreams (Weltzeituhr concat 1997/1990a AZ/KA, Mengenlehreuhr step-1 'lit', face-UTC city/letter) x fwd/rev x all offsets, unknown single mixed alphabet (clocksingle scan_single + scan_beau; null 0 in 2.4e7): ZERO hits. (stego/xclock.py, 1396 s)

### TEAM anneal — scorer + annealer power (2026-10-17)
- `wordscore.py`: unigram word Viterbi (12k words, MobyDick+KJV+Smith, count>=3, + lore). log10/char: K1 -1.47, K2 -0.85/-1.70, K3 -1.28/-0.96, modern README chunks mean -1.55 (min -2.18); random -5.7; old P4 overfits -1.8..-3.3. Used as an UNOPTIMISED discriminator (search uses quadgrams only).
- `anneal2.py`: generic free-alphabet SA, x=(CAinv[C]-K_i) mod 26, P=PA[x]; keystream modes periodic / fixed (Gromark) / PT-autokey (PA or CA index) / CT-autokey; crib-repair (PA forced to satisfy cribs after each move); reheating cycles; restart-convergence = pairwise non-crib agreement (chance ~0.07-0.12).
- Synthetic power (out-of-corpus PT with cribs, `synth.py`, 4M iters x4 restarts, best-of-4 accuracy): periodic Quag IV p1 99-100%, p2 93-100%, p3 79-90%, p4 58-73%, p6 37-47%, p8 36-49%, p12 18-27% (wrong text, q -4.6..-5.0 while truth -4.1..-4.25 => search failure, not identifiability). Temperature tuning / reheats / 10M iters give only marginal gains.
- Fixed keystream (Gromark, mode 1, `synth2.py`): power good — 2/3 texts recovered 100% with converging restarts (q=-4.08/-4.25), 1/3 stuck at 68%.

### TEAM anneal — P4 verdict: free-alphabet Quagmire IV + periodic key
- EXACT crib test (`run_q4exact.py` brute force p<=7, `run_q4dfs.py` DFS over residues w/ union-find pruning, validated vs brute force on synthetic): NO crib-consistent key for p=1..7, 9, 10, 11, 12 (any PT/CT alphabets whatsoever). p=8: 4,503,912 consistent keys of 26^7 (5.6e-4). => Quagmire IV (any alphabets) with period <=12 except 8 is ELIMINATED without scoring (assumes cribs exact, no transposition).
- P4b SA real vs 3 shuffled-CT nulls at p 8,10,13,16,19,20,23,24,26,29,30 (`run_p4b.py`, results/anneal/p4b.jsonl): crib-clean best q REAL -4.42..-5.05 vs NULL -4.51..-5.15, word score REAL -1.82..-2.77 vs NULL -1.82..-2.47, restart convergence REAL 0.05-0.15 vs NULL 0.04-0.15. Indistinguishable; no convergence anywhere. Combined with power failure at p>=6: P4 gives no evidence for any period; old p4.log "English" = overfit.
- C17 all clock stream windows (3,048,982: every offset/dir of 1500+ streams) through dual-alphabet union-find (gromark mode 0): 149 unique survivors (rate 4.9e-5 < random 4e-4; low-entropy streams) -> results/clock_dual_survivors.npy/.json, handed to anneal for free-dual-alphabet annealing vs crib-consistent null. Verdict pending anneal.

### P6 — split-key (CKM-style) (TEAM novel, DONE, negative)
- (0) Lore-alphabet set (AZ, KA, 53 lore words, fwd/rev, both roles, vig/beau/var; 33,708 key vectors), direct, novel/run_threekey.py:
  three free keys A[i%a]+B[i%b]+C[i%c], a<b<c, a+b+c-2<24, only models with >=3 checks per prime (286 models): 18 hits vs 21.4 expected by chance (each real hit is one alphabet pair repeated 6x by rev/rule symmetry). Strongest: (2,7,13) EGYPT/WELTZEITUHR beau, 4 checks. The key is fully determined and decrypts to gibberish (-7.61). Fixed lore keyword (KRYPTOS, PALIMPSEST, ABSCISSA, BERLIN, CLOCK, SHADOW, LAYERTWO; AZ/KA-indexed, +-, all phases) + one or two free periodic keys (120 informative models): 42 hits vs 60.9 expected. Chance.
- (1) Keyword + free periodic key, k_i = s*W[(i+o)%L] + B[i%b]: 221,583 lore + dictionary keywords (L<=14), AZ- or KA-indexed, s=+-1, all phases, b 2-13, 12 variants (novel/p6_kwfree.py, validated on planted SHADOW/KA + period 9). ZERO configurations; random-keyword null also 0.
- (2) Two-key A[x%a]+B[x%b] over the E1 transposition set (138,758 perms fwd+inv: identity, routes W2-49, columnar W<=8, lore columnar), a<b, a+b<=17, b%a!=0 (37 pairs), both orders, 12 variants, exact Gaussian elimination mod 2/13 (novel/p6_twokey_trans.py, validated on planted columnar + (5,7) key). ZERO consistent; shuffled-CT null also 0.

### Key-bias scan over alphabet pairs (planner, in-memory) (DONE, chance)
- 394,816 dict/lore alphabets x 92 lore alphabets, both roles, Vig/Beau: 145M tests, stat = crib key values within ±3. Best 20/24 (reversed lore alphabets vs PALESTRIN/ALPESTRIN/EGALIT/ALIMENT). Null 2M random pairs max 18/24 -> scaled max ~20. Chance. Bean small-shift bias not exploitable. CLOSED.

### Digit-encoded structured pad (stego digitpad.py) (DONE, negative)
- 776 letter->digit tables (A=01..26 variants, keyed 6x6, 10x10) x structured pads (periodic, chain addition, lore digit strings): 0 hits real, 0 null.

### P6 CLOSED: split-key eliminated in direct, three-key, keyword-component, E1-transposition variants.
### Remaining: Gromark dual-alphabet anneal w/ word-level discriminator (anneal, gated on power test). Then stop compute unless K5/charts/more PT appear.

### Alternative alphabet families (user question) (DONE, negative)
- `run_altalpha.py`: 562 alphabets (+rev): columnar-transposed keyword alphabets (plain + key-ordered columns, ACA/Gromark style) for lore words, Morse orders (length, tree, dot-dash), ITA2/Baudot code order, QWERTY/QWERTZ/column-QWERTY, ETAOIN frequency orders, decimations x3..25 of AZ/KA, first/last-appearance alphabets from K1-K3 PT/CT, Morse text, K4 CT, crib words; keyword+rest-reversed, keyword+rest-after-last-letter. Paired with each other, AZ, KA, lore-keyed, both roles, 3 rules (~2.1M pair-rules): zero flags (no digit key range<=12, no period<=22, no <=6 distinct).
- Columnar-transposed (key-ordered) alphabets for all 221k dictionary words vs AZ/KA: 24 weak flags, min range 13, none strong.

### TEAM anneal — Bean dual-alphabet Gromark survivors (b10 L5, 39 primers) annealed
- `run_gromark_anneal.py`: anneal2 mode 1 (keystream fixed, PT+CT alphabets free), 2M iters x4 restarts each. Null = 39 random uniform-digit 97-length keystreams that also pass the dual crib test.
- Result: BEAN best q max -4.875 (mean -5.156), word max -2.31; NULL q max -4.914 (mean -5.196), word max -2.42. Identical distributions. All gibberish. Restart convergence can be high for wrong keystreams too (5 Bean primers have a restart pair agreeing >=0.98 on gibberish at q~-5.1) => convergence alone is NOT sufficient for fixed-keystream models; require convergence AND q>=-4.6.
- Power at identical settings (`synth_gpower.py`, 9 synthetic Gromark encryptions): 7/9 recovered (acc>=0.99, q -4.08..-4.25); failures -4.56/-4.90. => if K4 were b10/L5 Gromark with dual free alphabets and English PT, P(miss) per primer ~0.2. Bean Gromark: NEGATIVE.
- Autokey with free alphabets (modes 2,4; L 3,8): annealer has NO power on synthetic (can't even satisfy cribs). Not run on K4; low priority given P2 negative and stego's K5 "same coded words in same positions" argument against text-dependent keys.

### Sexagesimal / "change the language base" (user request) (DONE, negative)
- `run_sexa.py`, single unknown mixed alphabet test (+ Beaufort sign), covers AZ/KA.
- S1 base-60 chain addition (Babylonian Gromark analogue), primer L=2-4, two lag rules, shift = digit mod 26: 26.4M primers, 0 hits. Planted (17,42,5) recovered uniquely.
- S2 clock-time keys: every start second of the day x 38 steps (1 s .. 24 h, incl. off-by-one) x 8 readings (H, M, S, H+M, H+M+S, H mod 12, M/5, minutes-since-midnight): 26.3M streams, 0 hits.
- S3 letters written in base b (2,3,4,5,6..12; A=0 encoding), digit-wise addition of chain-addition key digits mod b (primer L<=5): max 6/24 crib matches = noise.
- Verdict: base-60/time arithmetic and simple base-change additive layers eliminated (direct).

### Greek/Cyrillic look-alike readings (user idea) (DONE, negative)
- `run_lookalike.py`: carved letters re-read as Greek/Cyrillic phonetic values (P->R, H->N/I/E, B->V, Y->U, X->H/K/C, C->S; plus bijective look-alike swaps), applied to CT only or CT + crib PT. Each x E1 perm set (identity, routes, columnar W<=8, fwd+inv) x p1-24 x 12 variants x 2 orders.
- Result: only 2 weak survivors (same perm, p=23, m=4), best completed key -6.98 = gibberish. Note bijective relabellings are already absorbed by unknown-alphabet tests. NEGATIVE.

### TEAM anneal — clock dual-alphabet survivors annealed (C17 handoff)
- `screen_streams.py results/clock_dual_survivors.npy clock` (149 streams, 2M iters x4, null = 40 crib-consistent random streams with the clock value distribution) -> results/anneal/screen_clock.jsonl.
- CAND q max -4.895 (mean -5.23), word max -2.17; NULL q max -4.963 (mean -5.15). All gibberish; nothing near the -4.6 candidate threshold (synthetic truth -4.1..-4.25). One stream (idx 134) has perfect restart convergence on gibberish (q -4.94) — again showing convergence alone misleads for low-entropy fixed keystreams. Clock numeric streams + free dual alphabets: NEGATIVE.
- Real-vs-null crib-consistency (Quag IV, p>=13) left incomplete (DFS too slow on inconsistent shuffles under machine load); P4b SA nulls were consistent at p10 1/3, p13 1/3, p16 2/3, p20 2/3, p23-30 3/3 -> real K4's consistency at p 8,13,16,19,20 is not significant.
- C17 VERDICT (anneal, free dual alphabets, 2M iters x4 restarts): 149 clock survivors q max -4.895 (mean -5.23) vs 40 crib-consistent random nulls max -4.963 (max-of-149 vs max-of-40, gap within expected extreme-value spread); all gibberish, none near -4.6 threshold (synthetic truth -4.1..-4.25, power ~78%/stream) | NEGATIVE. Caveat: idx 134 converged across restarts on gibberish -> convergence alone unreliable for low-entropy streams.

### TEAM anneal — wrap-up (lead requests)
- P4 scope statement: free-alphabet SA can decide only p<=3 (partial p=4). For p>=6 treat periodic Quagmire IV with free alphabets as UNTESTABLE by this method, not eliminated. (Exact crib kills still stand: p 1-7, 9-12.)
- Power test using clock's REAL low-variety streams (`run_clock9.py`, planted PT, free PA/CA, 2M x4): stream0 (18 distinct values) recovered by 1/4 restarts (acc 0.99, q -4.22); stream60 (25 distinct) 3/4 restarts converge on truth (q -4.08); stream120 (10 distinct) partial only (acc 0.68, q -4.55). => power ~2/3 for clock-like streams, so the 149-window screen is informative (but not exhaustive).
- Clock's 9 canonical streams (results/clock_streams_for_anneal.json), fixed keystream with free dual alphabets: crib-INCONSISTENT for all 9 (pen 2-12 in every restart, real and null alike). Eliminated without needing a score. Best q REAL -4.96 vs NULL -5.04 (meaningless with pen>0).
- Best real-vs-null gaps: word score Bean vs null +0.12 (max -2.31 vs -2.42), clock 149 vs null +0.34 (max -2.17 vs -2.52), but no candidate reaches q>=-4.6 and no restart convergence on English => NO SIGNAL.
- 9 canonical offset-free clock streams (results/clock_streams_for_anneal.json: city UTC/letters/text from Berlin; Mengenlehreuhr lit & digits from 00:00, 18:53, 23:30): fail cribs even with FREE DUAL alphabets (crib penalty >=2 on every restart, real and shuffled alike) | ELIMINATED. anneal power test on these actual streams: 2/3 planted PTs recovered (10-value stream partial 0.68). C17 word-score gap: cand -2.17 vs null -2.52 (q -4.895 vs -4.963), gibberish.

### TEAM stego — S13 digit-encoded PT + structured mod-10 pad (lead task) (DONE, negative)
- Tables: 776 = 97 keyed alphabets (AZ, lore + stego keywords, fwd/rev) x {linear 00-25, linear 01-26 (= keyed 10x10, letters in first cells), 6x6 Polybius rows/cols 0-5 or 1-6}. Cipher digit = code +/- pad (mod 10); need 24 cribs exact + all 97 decrypted codes valid.
- Pads: general periodic digit pad q=1..60 (covers lore strings 385765/77844/19891109/19901103/1986 and keyword-rank digits at any phase); chain addition pad[n]=pad[n-L]+pad[n-L+k], L 2-20, all k, ANY primer (solved linearly mod 2 and mod 5; offset-invariant); clock digit streams (results/clock_streams_for_anneal.json, mod 10 and digit expansion) + lore strings, all cyclic offsets, fwd/rev.
- Result: real CT 0 periodic, 0 chain (no crib-consistent primer at all for any L<=20), 0 fixed. Null (2 shuffled CTs): also 0 -> as expected the test is very strict (48 crib digit equations; validity ~0.26^97 by chance). Self-tests: planted chain primer (L7) and periodic pad (q13) recovered. NEGATIVE. (stego/digitpad.py, logs stego/dp_*.log)

### Prior-art research (agent) -> data/prior_tests_research.md
- No public record of M-94/M-138, Ragbaby, Nicodemus vs K4. M-209 only restricted sub-spaces (Patrick repo, self-reported); turning grille partly; disrupted columnar W<=9.

### M-94 cylinder (US Army 1922-43) (DONE, negative)
- `run_m94.py`: 25 published disk alphabets (jproc.ca; B1 and R17=ARMYOFTHEUS cross-checked). Lines of L letters (L 12-25, using any subset of disks), all line-start offsets, independent generatrix per crib-bearing line (26^2-3), disk order solved by bipartite matching.
- Validation: planted M-94 message recovered (plus 3 spurious configs). Null: 5 shuffled CTs and 3 random disk sets -> 0.
- Result: 0 consistent configs for all L, offsets, generatrices. M-138-A not tested (100 strip alphabets not obtained).

### Ragbaby, 26-letter variant (DONE, negative)
- `run_ragbaby.py`: shift = word# + letter# (also word# - letter#, word# only), both signs; segmentations EAST|NORTHEAST, EASTNORTHEAST, EAST|NORTH|EAST x BERLIN|CLOCK, BERLINCLOCK; unknown word numbers (26^2); single unknown keyed alphabet (covers all keyword alphabets, AZ, KA). ACA 24-letter form impossible (CT has J, X).
- Validation: planted SHADOW Ragbaby recovered. Null 20 random: 0. Result: 0 hits.

### Nicodemus (DONE, negative)
- `run_nicodemus.py`: Vigenère period W + columnar by keyword order, read in blocks of B rows (B 3,4,5,6,full). All column orders W 2-9; dictionary/lore keyword orders W 10-14 (~100k orders). 12 substitution variants, both orders. Validation planted W=7 found. Result: 0 survivors.

### Historic rotor/disk systems (user request) (DONE, negative)
- `run_rotor_alberti.py`.
- T1 single stepping rotor / rotating cipher disk (Hebern, regular Kryha, Alberti turned per letter): C = ringC[R(ringP^-1(P)+a*floor(i/m)) - c*floor(i/m)], R unknown permutation, rings AZ/KA, a,c 0-25, m 1-6 (16,224 configs). Validation planted rotor recovered uniquely. Null 20 random: 0. REAL: 0.
- T2a Alberti indicator segments, single unknown alphabet, piecewise-constant shift with <=1 change point per crib run (all positions, all shifts): REAL 0, null 0; planted segment cipher recovered.
- T2b same with up to 2 changes per run over 110 lore x 396k dict alphabets, both roles, 3 rules: best = 7 changes in a run (real) vs 7 (random-alphabet null). No piecewise-constant structure.

### External info research (agent) -> data/external_info_2026.md
- Kobek: recovered PT exactly 97, cribs exactly in position. Sanborn SciAm Nov 2025: Egypt 1986 + Berlin Wall; "creativity"; "Who says it is even a math solution?"; K5 97 chars shares coded words in same positions; Paradigm plans K5 release later.
- 1990 dedication transcript (auction image): bottom text has "two separate systems" = "a major clue in itself". 1988 proof-of-concept plate: plain-AZ tableau rows (CDEFGHIJ/DEFGHIJK/EFGHIJKL).
- No charts/worksheets/K5 visible in published lot images; no pre-1997 Weltzeituhr list found.

### Direction-driven walks on the physical Kryptos tableau (DONE, negative)
- `run_tabwalk_dir.py`: actual 28x31 sculpture tableau grid (header/footer/side AZ incl.), start at every cell, periodic compass-step patterns length 1-4 over 8 directions (4,680, incl. E/NE zigzag for ENE), torus wrap skipping blank corners; key letter per position; 12 variants x key index AZ/KA. Validation planted (E,NE) walk recovered. REAL 0; 3 shuffled nulls 0.

### Initial-letter book keys (user idea) (DONE, negative)
- `run_initials.py`: keys = first letter of each word / sentence / paragraph / line, last letter of each word / line. Sources: Carter & Mace 1923 vol I (archive.org text, original 10,404 OCR line breaks), Smith Tutankhamen, KJV, Moby Dick, K3 with word breaks. Fwd/rev, all offsets; fixed alphabets (12 variants, AZ/KA key index, any shift) and single unknown mixed alphabet (both signs).
- Result: fixed-alphabet best 7-11/24 (random-stream null 10/24); unknown-alphabet hits 0 everywhere. Page-initial letters not tested (scan has no reliable page breaks; edition-specific).

### General running-key exclusion (any book) (DONE)
- If key = running text, the 24 crib key letters must read as text. Under all 12 standard variants x AZ/KA key-letter alphabets x 26 indicator shifts, best fragment quadgram -5.80 (e.g. JSMIHINNEIALM | OWNASEAPKTL); real English 11-13-letter fragments ~ -4.5..-5.2. None text-like (English, nor visibly German/Latin).
- => running key from ANY English book/speech/document (Reagan 1987, Kennedy 1963, Declaration, Book of the Dead, Poe, Kahn, etc.) is excluded with standard/KRYPTOS tableaus; with dictionary-keyed alphabets also chance (3A).

### Historic-methods survey (agent) -> data/historic_methods_survey.md (DONE)
- ACA list + Gaines/Kahn/FM 34-40-2 + German/Berlin + agent/aircrew systems classified vs K4 constraints. New structural kills: Slidefair (never self-encrypts; K4 has S->S@32, K->K@73), DRYAD (no Z), SARNEG (10 letters), Fractionated Morse (BERLINCLOCK -> ~15 CT letters), RS44/Ubchi/poem code alone (CT 2 E's < crib 3 E's).
- Periodic Gromark (ACA, validated on ACA ENIGMA example; novel/periodic_gromark.py): 221,583 words x 8 variants, best 8/24 vs null 8/24. NEGATIVE.
- 2x13/13x2 letter-matrix coordinate addition (= Vig/Beau over CRT alphabet; novel/crt_matrix.py): p1-24, 0 hits, null 0, planted found. NEGATIVE.
- Unknown 26-row SOE-silk table + dictionary keyword (novel/randtable_kw.py): real at chance -> untestable without a transcribed table.
- Source: CIA Studies in Intelligence 60(1) 2016 — aircrew learned classified memorized letter-encryption in advanced SERE (method not public).

### Shape paths over the tableau (user idea) (DONE, negative)
- `run_shapes.py`: 161,942 paths on the physical tableau: compass rose 8/16 rays (ray-by-ray and ring-by-ring, both rotations), cross, 24-point circle and star polygons {24/5,7,11} (vertices and full connecting lines), every centre cell, size 3-13; cyclic start, both directions. Fixed alphabets (12 variants x AZ/KA key idx) + single unknown alphabet.
- Validation planted star24/7 path recovered. REAL 0, shuffled null 0.

### Historic-methods survey (agent) -> data/historic_methods_survey.md
- New structural kills: pure transposition impossible (CT has 2 E, cribs need 3); Slidefair (no self-encryption; K4 has S->S, K->K); DRYAD, SARNEG, fractionated Morse, 5x5 systems, ADFGVX. DIANA OTP = Beaufort variant (covered except random pad).
- Agent tests: periodic Gromark (ACA-verified) 221k words best 8/24 = control; 2x13/13x2 coordinate-addition grids p1-24: 0; SOE random 26-alphabet table + keyword: untestable without real table.
- Shortlist: running keys from memorized texts with unknown alphabet; real printed SOE/OSS tables; 10x10 turning grille + periodic; RS44-style stencil; full M-209.

### Memorized/famous texts as running keys, incl. unknown alphabet (survey shortlist #1) (DONE, negative)
- `run_memtexts.py`: Declaration, Gettysburg, Constitution (Gutenberg), Reagan 1987 + JFK 1963 Berlin speeches, Star-Spangled Banner (1814 + songbook), Code of Conduct (EO 10631) (Wikisource), Pledge 1954, Leo Marks "The Life That I Have", CIA motto John 8:32. Full letters and word-initials, fwd/rev, all offsets.
- Fixed alphabets best 6-9/24 (noise); single unknown mixed alphabet: 0 hits for every text.

### Egyptian / US-crypto / CIA-founding texts as running keys (DONE, negative)
- `run_texts2.py` on data/texts2: Budge Book of the Dead (2 translations), Egyptian Literature, Budge Rosetta Stone, Herodotus (Account of Egypt + Histories vols 1-2), Poe Works vol 1 (incl. Gold-Bug), Friedman Military Cryptanalysis Part I (OCR), CIA Act 1949 + NSA 1947 pages (Wikisource stubs) + 1947 CIA memo. Letters + word initials, fwd/rev, all offsets.
- Fixed alphabets best 7-11/24 (noise); single unknown alphabet 0 hits everywhere. Not obtained: full statute texts of NSA 1947 / CIA Act 1949, Yardley's Black Chamber.
- Added: Parker Hitt "Manual for the Solution of Military Ciphers" (1916, first US Army crypto manual), Maspero Manual of Egyptian Archaeology, Budge Literature of the Ancient Egyptians: running keys best 9-11/24 fixed, 0 unknown-alphabet hits. All 33 complete 26-letter alphabets printed in Hitt (standard/reversed shifts, frequency-order alphabets etc.) as PT/CT alphabet pairs (+AZ, KA): 0 flags (no digit key, no period<=22).

### Per-line keys on copper layout (user idea) (DONE, negative)
- `run_perline.py`. Copper rows: row 25 holds 13 cribs (cols 17-29), row 26 3 (cols 28-30), row 27 8 (cols 0-7).
- A) different constant shift per line, single unknown alphabet (both signs): 0 hits (null 0).
- B) different keyword per line, 221k dict+lore words repeating from row col 0 or from K4-relative line start, 12 variants x AZ/KA idx x any indicator shift; rows 25 and 27 tested independently: 0 hits each (null 0).
- (Earlier: stego S6 row-restart periodic keys, no signal.)

### Is K4 PT a quotation? (user idea) (DONE, nothing found)
- Local corpora (37 files incl. Carter, Egyptian texts, speeches, Bible, Moby Dick, crypto manuals): no EASTNORTHEAST, no BERLINCLOCK, no exact spacing pattern EASTNORTHEAST.{29}BERLINCLOCK; ALEXANDERPLATZ only in Reagan speech.
- Web search: phrase pair appears only in Kryptos discussions. Side fact: the Weltzeituhr stands on a mosaic wind rose (compass rose) — thematic link between EAST NORTHEAST and the clock; also the Kryptos site has a compass rose/lodestone. Suggests PT gives a bearing relative to the clock, not a book quote.

### Kryptos compass needle bearing (research agent) -> data/compass_research.md
- No measured bearing published; reports conflict (rose north ~SSW 220°; needle south end 15-30° N of E; ENE vs WSW unknown). "Pulled off due north by a lodestone" quote is WSJ 2005 (not 1990 as I first said). ENE<->compass link = community speculation only. Great-circle CIA HQ -> Alexanderplatz = 44.4° (NE), not ENE (67.5°). Weltzeituhr wind rose orientation undocumented.
- Verdict: no usable clue without an on-site measurement.

### Literal K3 instruction "breach upper-left corner, widen the hole" (DONE, negative)
- `run_k3breach.py`: reading orders growing from a corner (square L-shells x4 traversals, anti-diagonals x3), all 4 corners, on copper layout (31 wide, K4 from col 27) and widths 2-49; 2,744 perms (fwd+inv) x periodic p1-24 x 12 variants x 2 orders. Validation planted copper-shell + SHADOW found. REAL 0, null 0.

### Layered Kryptos texts as key (user idea: K0 on K1 on K2...) (DONE, negative)
- `run_layers.py`: texts K0 Morse, K1/K2/K3 PT, K1/K2 CT, K3 CT (carved, 336), full carved left side before K4 (768), tableau right side (867); cyclic. Single running keys + all PAIRS summed/differenced (key = A[oA+i] ± B[oB+i]), every offset pair, AZ/KA indexing, 12 variants, any indicator shift.
- Validation planted K1PT+K3CT key found. REAL 0 hits; null 0. (Physical plate overlays = stego S1, best 8/24.)

### Per-row physical overlay with run-length scoring (user follow-up on S1 "8/24") (DONE, negative)
- Note: S1's 8/24 = chance (null P(>=8)=6e-4/stream over 15,840 streams); near-correct overlays do not give partial scores.
- `run_rowoverlay.py`: each K4 copper row independently aligned to ANY row of tableau (right) or cipher (left) grid, any column shift (torus), mirrored or not (view from behind), 12 variants x AZ/KA x indicator shift. Scores: longest consecutive matching run + count.
- Row 25 (EASTNORTHEAST 13): real best run 4 / count 6 vs random-grid null 4-5 / 6-7. Row 27 (LINCLOCK 8): real 4/6 vs null 4-5/5. At or below null. No partial alignment anywhere.

### K4 layered on itself / palimpsest (user idea) (DONE, negative)
- `run_selfoverlay.py`: maps f = all 9,311 affine i->(a i+b) mod 97 (incl. reversal, every cyclic shift, every decimation) + copper 4x31 grid row-flip / mirror / 180-rotation with all row/col shifts.
- (A) key_i = CT[f(i)]: 12 variants x AZ/KA x indicator shift, plus single unknown alphabet: 0 hits (3 shuffled nulls 0).
- (B) key_i = PT[f(i)] (true palimpsest; 5,969 maps testable with >=6 crib-crib links): 0 hits; planted PT[5i+11] KA-Vig recovered.

### Fable two-layer brainstorm (2nd round) — verified/tested
- Statistic: AZ-Vig crib shifts within ±3 mod 13 = 20/24 (exp 12.9); shuffled-CT null P=0.0021. But mod 11 (21 vs 15.3) and mod 12 (20 vs 14) also elevated -> general clustering near 0 and ±11; look-elsewhere p~0.01. Suggestive only.
- #1 small-shift + half-flip (C=P+s+13b, |s|<=3): IMPOSSIBLE at 24/24 — positions 29, 64, 68, 71 have shifts +6,-6,+6,-9 (outside ±3 of 0 and 13 mod 26); |s|<=5 still 3 outliers. Dead unless 3-4 crib errors.
- #2 half-free alphabet (free PT or free CT alphabet, other AZ/KA) + running key from K0-K3 PT/CT, left/right sculpture, K-keys concatenated, all corpora (Carter, KJV, Egyptian, speeches...), fwd/rev, both signs: 0 hits (null 0; planted found). `run_fable2.py`.
- #7 key = K3 PT/CT addressed by every affine map mod 336/337 (incl. K3's 192i+191): 0 hits.
- #6 mirrored / rotated / row-flipped copper reading + periodic p1-30: 0 survivors.
- #4 (concatenated K1-K3 keys as periodic key p=18/25): covered by periodic eliminations (p<=24 E1; p=25 impossible any alphabet per novel).
- Not run: #3 selector-switched two keywords and #8 proof-plate selector (need an arbitrary artifact-derived selector; fishing, low prior).

### SIGNAL: small-shift / letter-class structure (Fable deep dive + tests) — STRONGEST LEAD
- `run_signal.py` T1: family-corrected look-elsewhere MC (moduli 26/13/12/11 x windows ±2/±3 x 6 partitions x two offsets + 3-bin chi2): real min-p 0.0005, corrected p = 0.0029 (20k shuffles). Signal survives.
- T2 IC check: small-key-everywhere model gives IC<=0.0361 in 7% of English samples; observed mix 17% -> IC does NOT kill it (Fable's 2-sigma estimate too pessimistic).
- `run_twoparts.py` T2 (M1 letter-class): KRYPTOS-PT letters |k|<=w and each other PT letter's occurrences within a (2w+1) window (= fixed substitution sigma + small key): real failures 2 (w=2,3: E@64 F/G/Y, O@71 ->F), 1 (w=4); 20k shuffled-CT null mean 9.7-11, P<1e-4. Post-hoc class choice (Bean noticed it first) -> fair p ~1e-3.
- Implied structure: KRYPTOS letters ~unchanged, others substituted (sigma: A->K/L, B->N, C->N/O, E->F/G, H->N, I->T, L->X, N->R/S) then small aperiodic key ±3. Failures both in BERLINCLOCK (64, 71): carving errors or model imperfect.
- T3 two separate periodic ciphers (boundary 34-63, or per copper row; each part own period 1-12, alphabets AZ/KA/17 lore fwd/rev, 3 rules): no partition with both parts consistent; null 0.
- Open: sigma undetermined for 11 letters, key aperiodic -> cannot decode from cribs. Candidate generator for this structure is the next question.
- Constrained decode under M1 (`run_m1decode.py`, ±3, sigma implicit via window consistency, cribs fixed, 64/71 exempt): fully constraint-clean English-like texts found for real (best q -4.05) AND for fair nulls (non-crib 73 letters shuffled; -3.99..-4.16). Model too loose to decode: freedom manufactures English. Needs a generator for sigma/key.

### Fable generator search for the letter-class structure (DONE, no generator)
- No natural table reproduces sigma: affine AZ/KA maps max 13/24, keyword-mixed alphabets (6 conventions x 26 offsets) max 16/24, Polybius/2x13 grids max 15/24, KRYPTOS-fixed-slot permutations max 16/24 (model gets 22/24).
- KA-tableau misreading conventions: none tighter than plain AZ Vigenère; KA tableau apparently not involved.
- Zero-parameter view: shifts in two bands {-3..+3} and {+10..+14}; band bit b correlates with letter class AND position (b=0 in 21-33, b=1 in 63-72) — confounded. Residual small key s aperiodic; no match to coordinates/dates/pi/e digits (best 6/24).
- Candidate generators (none exact): ROT13-mask + small-key Vigenère (20/24, fails H29 E64 N68 O71 = ±6/-9); 2x13 homophonic slide (column shift by small key, row free = homophone); mod-12 clock slide (21/24 at ±3). Treat as descriptive; not decodable from cribs.

### Fable deep synthesis (round 3) + follow-ups
- Theory: direct, position-keyed two-pass hand system on PLAIN AZ tableau: (1) masking substitution from a hand-drawn chart (fixes ~E,K,O,R,S,T; moves A,B,C,I,L ~+10) — not a keyword/affine/columnar alphabet; (2) small aperiodic "nuance" key (0..4 or ±2). Explains signal, all negatives, K5 shared words. Not decodable from 24 cribs. Decisive future test: K5 depth (C4-C5 cancels key -> sigma-difference equations).
- Fable closed (inline): substitute-then-shift ("write keyed alphabet under A-Z, take letter beneath") for 796k keyword alphabets; error-tolerant periodic keys; rule-switching (Vig/Var/Beau by class) keys; affine/two-index sigma; 2x13 Playfair; row-initial ("ID BY ROWS") keys; UTC-offset reading (vacuous: 25/26 residues allowed; pos 72 +13 impossible).
- Lead follow-ups: #2 forward-map procedure over 13,312 structured alphabets (altalpha families + Hitt tables, all rotations/reversals), 4 orientations: 0 flags (random-permutation null 0/40k). #4 period-8 date keys (1989-11-09, 1990-11-03, 1986, 1969-10-07, coordinate digits; all formats, phases, signs, +0/+10/+13): 720 keys, 0 single-alphabet and 0 dual-alphabet hits.

### K5 availability check (2026-10-17)
- NOT released. Paradigm (paradigm.xyz/2026/06/kryptos): holds K5 CT (97 chars), "We plan to release K5 in the future" — no date/condition stated; other coverage says release follows K4 being solved. No public K5 CT or fragment found. K4 verifier at paradigm.xyz/kryptos/, $1 per submission, format unstated.

### K5 depth-attack tool READY (`k5_depth.py`)
- Model: C4 = sigma(P4)+k, C5 = sigma(P5)+k (shared chart sigma + position key k in 0..4); joint Viterbi over k (fixes both PT letters), quadgram on both texts, SA over sigma, soft crib penalty.
- Validation on synthetic K4/K5 pair (random sigma, random k 0..4): 92-93% of BOTH plaintexts recovered, best restarts converge (score -4.07). Usage when K5 released: `python k5_depth.py <K5CT>`; also try kset -2..2 and add any K5 cribs.
- Fable #3 chart-structured decode (`run_chartdecode.py`, bijective sigma + key 0..4 or ±2, Viterbi inner, 8 restarts): REAL q -4.06, word -1.62/-1.45, restart agreement 0.52/0.61 vs non-crib-shuffled nulls q -3.97..-4.08, word -1.25..-1.71, agreement 0.47..0.73. Pre-registered success (>=0.3 gap AND agreement >=0.8) NOT met: real == null. Single-text decode cannot identify sigma. Letter-class track: "real signal, not decodable without K5".

### New leads from rumkin.com K4/K5 pages (user screenshot, 2026-10-17)
- Dinner Q&A: buried bronze USGS marker (half buried, crosshairs) adjacent to Kryptos, "important", later removed. Geocaching forum thread on the missing benchmark.
- Sanborn: "something to be gained" from his NYT-released encryption charts; mystified nobody got more from his K1/K2 matrix; misspellings maybe not mistakes.
- Scheidt (via Elonka): Kryptos uses a system "unknown to anyone on the planet". K4 solvable without K1-K3; K5 not without K4. K4 "one-off?" -> "we don't answer it".
- Sanborn interview: "five or six" techniques; "matrix codes Ed gave me" + "I have also designed visual systems for encoding, which are much harder for cryptographers to crack because they're individualistic"; decoded text refers to an act and a location on agency grounds. => supports hand-made visual chart theory.
- Research agent dispatched: benchmark identity/stamping/coordinates + encryption sheets -> data/benchmark_and_sheets.md.

### Sanborn's NYT K1/K2 coding charts (user screenshot) — KEY FACTS
- Format: 31-column grid; per line three rows: PT / key (keyword written out repeatedly) / CT; lines numbered = copper panel line numbers (K2 rows 3-8). '?' copied into key and CT rows, consumes no key letter. K1 last letter on a 3rd short line (N/L/D). Keyword PALIMPCEST written above K1.
- IQLUSION explained: chart PT reads ILLUSION; key row switches to PALIMPCEST (C for S) at that cell; KA-Vig enc(L,C)=K = carved CT (= enc(Q,S)). => K1 "misspelling" = KEY-ROW alteration on the chart.
- UNDERGRUUND explained: chart PT reads UNDERGROUND and chart CT has E (= enc(O,S), correct) at K2 pos 114, but the COPPER has R (= enc(U,S)). => K2 "misspelling" = CT altered between chart and copper. (Also chart vs carved diff at K2 pos 118 O/D and K1 pos 30 Y/V — likely my photo misreads.)
- K3 DESPARATLY is transposition-only -> must be in PT itself. So the three misspellings arise at three different stages (key row, carving, plaintext) — deliberate "masking"?
- Implication for K4: carved K4 CT may differ from Sanborn's chart CT at a few positions; the two misfits of the letter-class model (E@64->Y, O@71->F) are candidates for such deliberate copper alterations. Crib tests should tolerate 1-2 altered CT letters (P1 did for periodic; letter-class model fits 24/24 if 64 & 71 are alterations).
- Confirmed from clean K2 chart scan (data/web/sheets/K2FromPdf.jpg): row 6 chart CT has E at K2 idx 114 (correct enc(O,S)); copper R. Chart/carved O-vs-D at idx 45, 118 = Sanborn's D handwriting resembling O. K4Clue.png is a solver's numbering sheet, not Sanborn's.
- Benchmark research (data/benchmark_and_sheets.md): marker not identified; candidates LOOMIS (HV4826, "LOOMIS PB AND PP 1930", destroyed 1984, ~100-127 m from K2 coords) and BOWEN (AJ3427, 1984); none matches Sanborn's description; no stamped key material found.

### Fable post-chart recommendation (2026-10-17)
- Chart forensics: PALIMPCEST is Sanborn's header spelling; key-row S cells overwritten (ink ~1.7x) = he corrected C->S but missed line 2 col 26 -> IQLUSION is a correction MISS (not designed). UNDERGRUUND and K2 dropped end-of-line S = post-chart changes. Expect 0-3 copper letters in K4 differing from his chart (fits 64/71). '?' passes through without consuming key; K4 is 97 letters. Ticks/arrows = proofreading marks. K4 key row must be non-keyword (hand-made "visual" small-number row + personal substitution).
- Fable inline test: 234k dictionary words + lore as key rows (continuous and per-copper-line restart), 26 alphabets, 3 rules, all phases: max 10/24 (need >=21 even with 3 alterations) -> keyword key rows dead even with many alterations.
- Plan: (1) extend k5_depth.py with 0-3 alteration slots + period-31 column-key option; (2) diagnostic: is 64/71 the unique alteration pair making letter-class fit 24/24?; (3) close dictionary-key-row x dictionary-tableau with t<=3 (EV <3%); (4) stop chart-lore/visual reconstructions; (5) external: Paradigm/Kobek-Byrne for K4 key-row type and any K5 fragment.

### Post-chart plan executed (2026-10-17)
- #2 Alteration diagnostic: letter-class model (w=±2 or ±3) reaches 24/24 with exactly ONE 2-position exemption set out of 276: (64, 71). No single exemption works; 22/23 working 3-sets contain 64&71. Shuffled-CT null: 0/2000 reach 24/24 with any 2 exemptions. => FIRM PREDICTION: Sanborn's K4 chart CT differs from the copper at positions 64 (carved Y; model expects C..J) and 71 (carved F; model expects L..R).
- #1 k5_depth.py extended: free-key mode robust to 3 altered CT letters per text (75-79% recovery); new period-31 copper-column key mode (anneal_col) 96-97% recovery on synthetic pair. Single-text column mode on K4 alone: weak (48% on synthetic) and real == null -> not decodable without K5.
- #3 `run_keyrow_t3.py`: 221k dictionary/lore keywords as key rows (continuous + per-copper-line restart) x 746 tableau alphabets (AZ, KA, lore/themed keyword alphabets, structured families, fwd/rev) x 3 rules, <=3 mismatches allowed: 0 hits. (Full 396k dictionary-tableau extension not run: ~3 h, EV low.)

### Visual positions of deliberate anomalies on the copper (user question) (no pattern)
- Copper (row, col), left side: K1 Q-slip (carved K) (1,24); K1 chart ticks K (0,17), Y (1,0); K2 UNDERGRUUND carved R (5,23); K3 DESPARATLY 'A' -> via K3 transposition (192i+191 mod 337) at (16,27) [carved A, mapping verified]; K4 predicted alterations 64 -> Y (26,29), 71 -> F (27,5).
- Columns 24, 23, 27, 29, 5; rows 1, 5, 16, 26, 27: no common column/diagonal/symmetry; carved letters K,R,A,Y,F; wrong PT letters Q,U,A + predicted E->?,O->? — no evident word or shape (EQUAL-type readings already tested as keys). Judged chance.

### Non-keyword numeric key rows (user idea) (DONE, negative)
- `run_nonword.py`: per-letter derivations of every text (K0, K1-K3, all corpora; fwd/rev, all offsets): Morse element count / dots / dashes / dots-dashes, phone-keypad digit, 5x5 Polybius row/col, index mod 5 / mod 10, vowel flag (x1,x2,x3 multipliers). Models: single unknown alphabet; half-free sigma(P)+k. Planted Morse-length key recovered. REAL 0 / 0 hits; null 0 / 0.

### Fable "artist" brief + ANTIPODES CHECK (2026-10-17) — prediction partly REFUTED
- Fable: Antipodes (Hirshhorn) carries K2 with the CHART letter E (not copper R; Bean) => Antipodes cut from chart-stage files => its K4 should show chart letters at 64/71. Light/shadow keys low-prior (K4 enciphered on paper 1988-89 before installation).
- Checked Elonka's Antipodes photos via Wayback (data/web/antipodes/; A5 inside view mirrored, A11 exterior close-up): reads "...WINFBN Y PVTTMZ F..." => position 64 = Y (clear, two photos), 71 = F (moderate; edge of frame). Also "?OBK..." present.
- => Chart letters at 64/71 match the copper. The 64/71 "carving alteration" prediction is NOT supported. Either chart-stage slips (like IQLUSION key-row slip) or the letter-class model is only approximate there. Statistical signal (p~0.003) stands; clean 24/24 story weakened. Caveat: Antipodes K4 could come from another file; 71 reading at frame edge.

### Artist sigma generators (Fable H1-H3) (DONE, partial = known signal only)
- `run_artist.py`: 708 sigmas: H1 alphabet-strip slides (AZ/KA/rev, offset d; also per-copper-row d), H2 KRYPTOS-pinned stencil (19 others written from start cell, +/-, wrap 26/31), H3 KRYPTOS-pinned dial rotation (others rotated in AZ/KA order; full-AZ rotation with KRYPTOS pinned). Small key 0..4 or ±2. Nulls: 40 shuffles.
- Best: H3full "KRYPTOS letters fixed, every other letter +12, then ±2 key" = 17/24 (null max 10); H2/H3 15/24; H1perrow 16/24. These reproduce the already-known two-band signal (two-offset model gave 17/24) but none fits E,H,N (+1..+6 band) -> no generator reaches 22-24/24. No new mechanism.

### Visual-artist framing: 2-D keyboard displacement mask (DONE, known signal only)
- QWERTY/QWERTZ/AZERTY 2-D key displacement (dr 0-2, dc -9..9, stagger approx), KRYPTOS pinned or not, small key: best 16/24 (QWERTY, KRYPTOS pinned, ±2 key) vs shuffled max 13 — same two-band signal, misses E/H/N; no better than "pin KRYPTOS, shift rest +12" (17/24).
- Next: research Sanborn's other SOLVED cipher artworks (Cyrillic Projector etc.) for his actual "individualistic visual" methods -> data/sanborn_other_ciphers.md.

### Sanborn's other solved cipher art (research) + signature-system closure
- data/sanborn_other_ciphers.md: Cyrillic Projector (solved 2003): single-layer keyed Vigenère: keyword alphabet ТЕНЬ ("SHADOW") + 6-letter key ЙБАСГТ from clue word MEDUSA (set in different font); inside-out cut for light projection; many typos (21/4/6). Sanborn: shares "some of the same code" as Kryptos, deliberate "common denominator". Other works: Caesar/Vigenère/transposition/binary, no details.
- `run_tableau_all.py`: Sanborn signature system for K4 = one keyword-mixed alphabet as tableau (PT, CT, key in T) x periodic key p1-24 x Vig/Beau/Var over ALL 395,948 dictionary/lore keyed alphabets (fwd/rev): 0 hits (m>=4); random-alphabet null 0/98,987; planted SHADOW tableau + MEDUSA key detected.

### Fable as Sanborn (5 visual designs) + predecessor test (DONE)
- Designs: Lodestone Rose (KRYPTOS fixed, rest -> antipode +13 ±), stencil-shadow per KA block (KRYPTOS / A-J / L-Z), cut-letter straight vs curved, two interleaved systems by parity/line, Weltzeituhr ring rulers. All cap at 17/24 (±4) — only via the KRYPTOS-pinning fact; KA/Beaufort rulers spread bands more (AZ is the tightest ruler).
- CORRECTION: the E/H/N "middle band" and A,B,C,I,L band are NOT distinguishable from chance (free monoalphabetic fit = null 99th pct). Only robust fact: PT letters of KRYPTOS have |AZ shift|<=2 in 9/10 (shuffled-CT null 0/5000; post-hoc caveat).
- Predecessor-driven key for non-KRYPTOS letters (g(P[i-1]), g(C[i-1]), g(C[i])): conflicts in every checkable case -> dead.

### Fable forensic/visual study of NYT charts (DONE, no key)
- PDF = same single scan; no hidden layer. No figure/shape in grid; keyword "stripes" = arithmetic of width 31 vs period; overwrite/slip/paste positions random; marks are proofreading. K2 chart col 0 = K2 idx 0 (copper line 3 starts with K1's trailing D) -> sheets NOT in register with copper; key stream continuous across lines; '?' takes a cell, consumes no key; block 6 CT is a re-pasted strip.
- Fable inline tests (null = shuffled CT): K4 key = K1/K2 chart cells at same (row,col) 4/24; vertical/interleaved chart column readings 7/24 (null max 8); header words <=5; Panel4Grid neighbours <=5; K4's own sheet cell-above (lags 1-40) 4/24. All chance.
- Lead follow-up: sheet-aligned row restarts (K4 from col 0, or '?' at col 0): dictionary keyword rows x 746 tableaus (<=3 mismatches) 0 hits; per-row periodic any-key p<=12 (12 variants) 0 hits. K2 coordinate digits as chain-addition primers (base 10/26, lag = primer length, both signs), single unknown alphabet: 0/32.

### Paradigm public images check (2026-10-17) — no K4 chart public
- paradigm.xyz/kryptos/history + 2026/06/kryptos images (data/web/paradigm/): handwritten notes captioned "K4 Coordinates, Howard Carter Passage, Layer Two" = K2/K3 plaintext notes (low-res, 90 KB; "K4 coordinates" = K2's coordinates); CIA contract, escort badge, dedication program, proof-of-concept plate (mirrored CDEFGHIJ/DEFGHIJK/EFGHIJKL), Dan Robinson with archive items (papers unreadable), mini Kryptos, Atomic Time catalog. Blurred printed letter grid behind contract (unreadable). No K4 coding chart or plaintext published; Paradigm states it keeps solution secret (items withheld).

### Light/shadow + Egypt (user push) (DONE, negative)
- `run_shadow_egypt.py`: (1) physical shadow projection of K4 cells onto the tableau grid with scale 0.6-1.6 (x,y), shear ±0.5 (x,y), all translations, mirrored or not; key = tableau letter under shadow; 12 variants x AZ/KA x shift: best 10/24 vs shuffled 9. (1b) same onto the cipher side (K0-K3 text): see results/shadow_egypt.log.
- (2) Egyptian uniliteral (hieroglyphic) alphabet order (A I Y W B P F M N R H S Q K G T D + rest, several placements of E/L/O, fwd/rev) as PT/CT alphabet with AZ/KA/each other, and as tableau x periodic p1-24: 0 flags, 0 hits.

### Crib dragging under the KRYPTOS fingerprint (user idea: probable words) (DONE, inconclusive)
- `run_wordfit.py`: 180 themed words; placement accepted if ALL its KRYPTOS letters (>=3) have |C-P|<=2. Real 20 all-fit placements vs non-crib-shuffle null 8.1±3.9 (z~3). Hits cluster at 35-40 (TOWARDS/SANBORN/TOWARD@37, STEPS@38, NORTH@40, SECONDS@35) — but CT 35-41 = "TWTQSJQ" is itself KRYPTOS-adjacent (T,S,Q near T/S/R), so most S/T/R-rich words fit there. Fingerprint has positive power only on KRYPTOS letters (non-K letters are not excluded: 2/14 cribs inside ±2 vs 2.7 expected) -> word identity not determinable. No phrase test attempted (overfitting).

### Fingerprint-constrained decode (DONE, no signal) + allowed-KRYPTOS-letter MAP
- `run_fingerprint_decode.py`: constraint "PT in KRYPTOS <=> |C-P|<=2" applied at all 97 positions (cribs fixed); ~16.6 allowed letters per free position; SA with quadgrams, word score, restart agreement; 5 non-crib-shuffled nulls.
- REAL q -3.77 word -1.20 agreement 0.19 vs NULL q -3.74..-3.76 word -1.09..-1.17 agreement 0.18-0.25: identical. Constraint too weak to decode (as expected: it only pins ~7 letters' placements).
- MAP of KRYPTOS letters allowed per unknown position (useful filter for any candidate PT): 0:OP 2:K 3:PRST 4:ST 5:OP 6:Y 7:OP 10:ST 11:K 13:RST 14:OP 15:K 16:K 20:Y | 34:OP 35:RST 36:Y 37:RST 38:OPRS 39:RST 40:K 41:OPRS 42:RST 43:RST 45:K 46-49:Y 50:RST 51-53:K 54:ST 56:K 57-58:Y 59:K 60:OP | 74:Y 77:K 78-79:Y 80:RST 81:K 84:K 86:K 87:ST 89:ST 90:Y 91:ST 93:K 95:Y 96:PRST; positions 1,8,9,12,17,18,19,44,55,61,62,75,76,82,83,85,88,92,94 allow NO KRYPTOS letter.

### KRYPTOS as mask + second WORD key on the other letters (user idea) (DONE, negative)
- Model: KRYPTOS-letter PTs pass through (±2); non-KRYPTOS PTs get Vigenère/Beaufort with a keyword (221k dict+lore words, key letters indexed AZ or KA). Mode A: key advances only on non-KRYPTOS letters (tested within each crib run, any phase); mode B: key advances every position (any phase). 0 hits both modes.
- Open: a non-word second key (numbers/drawn) on the non-KRYPTOS letters = the hand-chart case; not crib-testable.

### Chart-letter combinations as keys/alphabets (user idea) (DONE, negative)
- 1,125 key candidates: header words PALIMPCEST/PALIMPSEST/ABSCISSA/KRYPTOS and concatenations; marked letters (ticked K, Y; bold E), slip letters (C, Q, U, R), misspelling letters (Q, U, A), EQUAL, misspelled/correct words; all 2-4-letter permutations of KYE+CQUR. Tested as: plain periodic key (<=2 mismatches), KRYPTOS-mask + key on non-K letters (advancing every position, <=1 mismatch; or skipping K letters, exact), AZ and KA, Vig/Beau, all phases: 0 hits.
- Chart streams (K1/K2 key rows, PT, CT) as running keys on non-K positions, all offsets: 0. Combo-keyed alphabets (2,242) vs AZ/KA/each other: 0 flags.

### Reversals (user idea) (DONE, negative)
- Keys reversed (all 221k words + chart words, both directions), alphabets reversed (AZ/KA fwd+rev), plain periodic (<=2 mismatches) and KRYPTOS-mask + key (<=1): 0 hits on forward CT.
- K4 read BACKWARDS (cribs at mirrored positions): same key/alphabet families 0 hits; any periodic key p1-24 x 12 variants: 0 survivors. (Earlier: self-overlay affine maps incl. reversal as key, 0.)

### Group-1 leftovers (DONE, negative) + full tableau run launched
- Kryha-style irregular rotor stepping (patterns of advances 1-4, length 2-6; rings AZ/KA; ±a, c 0-25): 1.13M configs, 0 hits.
- Phrase-level small key: crib key letters under AZ/KA (shift 0/13) score -8.0..-9.2 (random ~-6.5): not English text.
- Two interleaved word keys (odd/even positions, 221k words, AZ/KA, Vig/Beau, <=1 mismatch per half): 0 hits.
- Proof-plate plain-AZ tableau x all word keys (<=2 mismatches): 0 hits.
- RUNNING: `run_keyrow_t3.py all` = 221k keyword key rows (continuous + per-line) x 396,572 tableau alphabets x 3 rules, <=3 altered letters -> results/keyrow_all.log.

### Candidate checker + themed generator (DONE; checker useful, generator degenerate)
- `candidate_check.py`: scores any 97-letter PT: cribs, KRYPTOS-fingerprint fit (K letters within ±2 of CT; non-K outside), q, word score, chance p. Lacy's published reconstruction: K-fit 6/33 (chance 0.63) -> contradicts the fingerprint.
- `run_generator.py`: beam search over themed+function vocab with fingerprint as hard (K letters) / soft (non-K) constraint. v1 exploited the rule by avoiding K letters (ONE WHO GO DUG...); v2 with K-density >=22% and quadgram scoring gives function-word salad (OVER THE AND THERE AND ALL ... IN I SAND THEM AN AND ...), K-fit 18/18 nonK 49/55, q -3.66, word -0.67. Verdict: the fingerprint is a FILTER (rejects ~50% of K letters per random text), not a generator; ~17 free letters/position leaves too much freedom. Meaningful candidates need semantic generation (external LLM prompt) + this checker.

### 3D ground-shadow overlap sweep (user request via model) (DONE, negative)
- `run_shadow_overlap.py`: 3D geometry of the model (two half-cylinders R 1.52 m, H 3.66 m, S-joined); both faces' letter cells projected along sun rays onto the ground; key for each K4 position = tableau letter whose shadow lands within half a cell of the K4 letter's shadow. Sweep az 0-358 x el 2-86 (7,740 sun positions; heading equivalent to az). 12 variants x AZ/KA key index x indicator shift.
- Only 166 sun positions put >=12 crib letters over tableau shadows (faces rarely overlap on the ground). Best crib agreement 6/13 at az 72 el 40; shuffled-CT nulls 5-6. NEGATIVE. Also: K4 was enciphered on paper before installation.

### Sanborn-habit tests (user: "be very creative") (DONE, all negative) — `run_habits.py`
- T1 slipped key row: 221,624 words+names as periodic key on AZ/KA tableau, 3 rules, all phases, with ONE phase slip of ±1..±3 before any crib position (or none): 0.
- T2 key written down the 31-wide worksheet (column-major, row snake, column snake, diagonal; sheet from K4 pos 0 or with '?' at col 0) and read by rows: 0.
- T3 neighbour mixing C = a*P_i + b*P_{i±1} + c (AZ/KA, all a units, b, c; 22 checks): 0.
- T4 key = next PT letter (lags 1-3, any indicator shift): 0.
- T5 proper names (CIA directors, Scheidt, Sanborn, Carter, Carnarvon, Erich John, Schabowski, Gorbachev, Reagan, Kennedy, Kohl, Honecker...) as keys (in T1) and as keyed tableaus x periodic p1-24: 0.
- T6 position-number keys (i mod m, (i+1) mod m, i div m for m 2-30; digit sums; i^2; triangular; ±, any shift): 0.
- Structural: shifts within EAST are +1,+11,-1,+2 -> key is not constant within words (kills word-length/first-letter/word-number keys).

### Sheet-derived visual tests (lead) (DONE, negative)
- (1) KRYPTOS mask + keyword restarting each row of the 31-col sheet (sheet / sheet-with-? / copper layouts), 221k words, AZ/KA, 3 rules, 15 non-K checks: 0.
- (2) key = distance to previous/next KRYPTOS letter in the plaintext (self-drawn), ±, any shift: 0.
- (3) column key (period 31) + per-row drift, sheet and copper: 0 consistent of 156 (chance 0.5).
- (4) diagonal/vertical sheet neighbours (lags 30/32/33, PT or CT) as key: 0.

### FULL dictionary-tableau run (DONE, negative)
- `run_keyrow_all_mp.py`: 221,583 keyword key rows (continuous + per-copper-line) x 396,572 tableau alphabets (dictionary/lore keyed fwd+rev + structured) x 3 rules, <=3 altered CT letters: 0 hits. Closes the Sanborn-signature family completely, even with carving alterations.

### Worksheet "move stuff" tests (DONE, negative)
- Visual notes: sheet layout stacks AST (31-33) over BER (63-65): shifts A+10/B+12, T-1/R-2, S0/E-6. 6 CT doubled letters (BB QQ SS SS ZZ TT) vs ~3.7 expected. Stubs OBKR (copper start) / KCAR (sheet end).
- (a) key = ciphertext slid by any lag -62..+62 (rows above or below, any sideways shift; forward autokey included), AZ/KA, 3 rules, any shift: 0.
- (b) key = PT or CT at mirrored (row-mirror, column-mirror, 180°) or row-swapped cells, sheet and copper layouts: 0.
- (c) all reorderings of the 4 rows (sheet/copper, fwd+inv = 92 perms) + periodic p1-24 x 12 variants: 0.

### "Build candidates with intent, then filter" (DONE; no readable candidate)
- Free-written themed phrases (25/2/14 per slot) score at chance on the fingerprint (best 7/24 K letters within ±2).
- Constraint-first fills (themed vocab, fingerprint-perfect, K-density >=22%/12%): slot1 e.g. OVER SECONDS VISIBLE DAY, ONE TWO INVISIBLE AGENCY; slot2 ONE TOWARDS DELIVERED HEADING ONE; slot3 DELIVERED INVISIBLE UNDER. Assembled: 15/15 K-fit, word score -0.61 (English-like by the metric) but not sentences. Recurring words (DELIVERED, INVISIBLE, TOWARDS, SECONDS) fit by letter composition (few/convenient K letters), not meaning.
- Verdict: fingerprint = filter only; composing a real message needs a writer with the allowed-letter map (worksheet) in front of them. Any candidate -> candidate_check.py -> Paradigm $1.
- Grammar-framed fills (verb/det/noun/prep/number frames, themed classes, fingerprint-perfect): slot1 e.g. WAIT BEYOND THIS OLD WALL / ON A STONE WATCH THE FLAME; slot2 DIG THE MESSAGE AND SEEK THE NEEDLE / UNDER THIS HEADING SEEK THE CANDLE; slot3 WALK BY THE INVISIBLE LIGHT. Assembled candidates: 17/17 K-fit, word -0.72..-0.75, q -4.17..-4.31 (English-quality) — readable but arbitrary: the constraint admits astronomically many such texts; each is a ~0 probability guess. Kept in results/intent3.log as seeds for the worksheet, not for $1 submissions.
