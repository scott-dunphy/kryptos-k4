# Semantic instructions in K0-K3 for attacking K4 (Fable, 2026-10-18)

Question: Sanborn (Wired 2005) "I have left instructions in the earlier text that refer to later text"; misspellings matter for "their orientation or positioning"; 2013 ACA dinner, "mystified" nobody got more from the K1/K2 matrix (see `data/fable_nyt_mystified.md`: that remark is about the coding charts). What could the instructions be, phrase by phrase, and which readings are still open after NOTES.md and `data/friends_prior_work.md`?

Method: each phrase is read as (a) the quote, (b) the concrete operation it could encode, (c) status against the log, (d) a testable spec or the external data that would decide it. Two quick tests were run today (section 5). Positions 0-indexed, cribs 21-33 and 63-73.

Prior, stated up front: the sentence "instructions in the earlier text" was said in 2005 about a piece whose K1-K3 texts were written in 1988-89 for a reader who would solve K1-K3 *first*. The cipher of K4 was fixed on paper in 1988 (RR lot: "original coding system", 1988 alternate chart = K5), before the copper existed. So instructions can be of three kinds: (i) a description of the cipher's *shape* (small shifts, layers, rows, positions), (ii) a key or alphabet *source*, (iii) a riddle instruction for what to do with the K4 plaintext (location, bearing, "deliver a message"). Nearly every reading of kind (ii) has been run to exhaustion by three teams. What survives is kind (i), which fits the one statistical signal we have, and kind (iii), which is not a cipher step at all. "Who says it is even a math solution?" (SciAm 2025) was said about the K4 -> K5 riddle, not demonstrably about the enciphering.

## 1. New forensic fact: "ID BY ROWS" was engineered, not an accident

- Checked today (`kryptos_texts.K2_CT`, key ABSCISSA): deleting the carved-omitted S (K2 CT index 361, the cell that encrypts the X of "WESTX") makes the KA-Vigenère decrypt of the tail read `...SECONDSWESTIDBYROWS` instead of `...WESTXLAYERTWO`. Any single deletion from index 310 on gives the same tail (key phase shifts by one).
- Under a phase slip the second reading is forced: P2[i] = P1[i] + k[i] - k[i-1] (KA arithmetic). For 8 consecutive letters to come out as an English phrase by chance is ~1e-5 or worse. So Sanborn chose "X LAYER TWO" and the ABSCISSA phases so that the *slipped* reading is "ID BY ROWS" (or vice versa). The 2006 "omitted for aesthetic reasons" statement is cover; this is "mistakes on purpose" (Wired 2005) in action, and a literal palimpsest: one ciphertext, two plaintexts, selected by a one-cell key slip.
- Consequences: (1) both "LAYER TWO" and "ID BY ROWS" are intended texts, so both count as instructions; (2) Sanborn demonstrably builds double readings by key-phase manipulation, which is the same habit seen in the K1 chart (PALIMPCEST key-row cell) and the K2 copper change (UNDERGRUUND); (3) for K4 the analogous construction would be K4/K5 as two readings sharing "coded words in the same positions" (Sanborn 2025), which is the depth attack already prepared in `k5_depth.py`. It cannot be exploited from K4 alone: a periodic word key is dead in every tableau family (E1, run_tableau_all, Barney 1.8M alphabets), so there is no second phase to try.

## 2. Phrase-by-phrase

Status codes: CLOSED (crib test with calibrated null, cite), DEAD (structural proof), OPEN-U (open but not testable with 24 cribs), OPEN-T (testable, spec given), THEME (plaintext-level riddle, not a cipher step).

### K0 Morse

| Phrase | Operation it could encode | Status |
|---|---|---|
| "VIRTUALLY INVISIBLE" / K2 "TOTALLY INVISIBLE" | the key is not written anywhere on the sculpture (a hand-made chart) | OPEN-U; consistent with H3 in `fable_nyt_mystified.md` and with every negative sculpture-derived key (S1, S4, S11, run_layers, Barney "physical layout") |
| "DIGETAL INTERPRETATIT" (digital; E for I, extra T) | letters as numbers; dot/dash = binary; E (dot) and T (dash) as the error letters = a binary hint | CLOSED: digit codes (run_digitcode, S13, groups.py 5-bit XOR/ITA2 Vernam, Z3^3, Barney Z27/Z9xZ3), Morse element counts of every text as key (run_nonword), Morse text as running key (E4, C10, run_layers), carry/borrow +0/+1 keys (carry.py); binary {0,s} key with fixed alphabet DEAD (E->F,G,Y) |
| "SHADOW FORCES" | SHADOW = the Cyrillic Projector keyword (ТЕНЬ); Sanborn: Projector shares "some of the same code" with Kryptos | CLOSED: SHADOW as key/tableau in every lore run (run_tableau_all planted SHADOW/MEDUSA, S8, P6, two-tableau); Projector = single-layer keyed Vigenère, and that whole family is dead for K4 |
| "LUCID MEMORY" | memorised key (Scheidt's memorisable systems); "lucid" = light | CLOSED as running keys from memorised texts (run_memtexts, run_texts2, general running-key exclusion: crib key letters not text-like under any standard tableau) |
| "T IS YOUR POSITION" | start cell = T (KA index 4; AZ 19); or the single dash marks the reader's position on the slab | DEAD as a constant/start offset (absorbed by indicator shift in every test); THEME otherwise (the Morse slabs face the entrance; "position" = where you stand) |
| SOS, RQ | keys/alphabets | CLOSED (stego words as keys/alphabets; chart-letter combinations) |
| 26 extra E's / E-run counts 2,1,6,3,2,2,5,3,1,1 | numeric key of length ~10-13 | DEAD: periodic p<=24 with fixed alphabets (E1); with a free mask p 1-12,14,15 inconsistent (Barney mask.py); p=13 would need a 13-value reading of the E runs (none natural) |

### K1 "Between subtle shading and the absence of light lies the nuance of iqlusion"

| Phrase | Operation | Status |
|---|---|---|
| "subtle shading" | the Vigenère rows are shades of one alphabet (Caesar shifts); shading = small shift | see "nuance" |
| "the absence of light" | zero shift / no key; or letters removed (nulls); or the holes themselves (the carved letters are absences) | nulls CLOSED (E3, S9 letter nulls, S5 '?'); zero-key cells: 2 self-encryptions (S@32, K@73) are chance-level (mystified diag, P=0.27) |
| "the nuance" | *nuance* literally = a shade of difference (French, from "cloud"): a small shift lying between a row shift and no shift | OPEN-U and the strongest lead: KRYPTOS-letter shifts within +-2 in 9/10 cribs, family-corrected p~0.003 (run_signal, run_twoparts); not decodable from 24 cribs (run_chartdecode, run_m1decode: real = null). Reading: K1 *describes* the K4 system (mask + small aperiodic key) rather than supplying its key |
| "iqlusion" (Q for L) | illusion = mirror; Q/L slip = key-row cell alteration | mirror/reversal CLOSED (reversed alphabets everywhere, run_reflection, rowoverlay mirror, self-overlay); the slip is a KEY-ROW cell change on the chart (chartdiff) = the hand-alteration habit, which the pinned-table tests allow (<=3 alterations, 0 hits) |
| "BETWEEN ... lies" | the key lies *between* two things: average of two keys / two tableaux | CLOSED: two summed keys (P6, Barney two-key, keysplit, keysplit_long), two stacked tableaux, two-stage |
| PALIMPSEST (K1 key) | overwriting: a second text under/over the first; a two-layer CT (section 1 shows he does exactly this in K2) | OPEN-U: for K4 the second layer would be K5 (depth attack); single-CT two-layer families CLOSED (S8, two-tableau, Barney two-stage 1.26e10) |

### K2

| Phrase | Operation | Status |
|---|---|---|
| "totally invisible" | as K0; also invisible = no written key | OPEN-U (hand chart) |
| "they used the earth's magnetic field" | compass: 32-point rose (ENE is point 6), declination at Langley ~10 W as a constant; lodestone pulls the needle off north = a fixed deviation | **CLOSED today** (section 5, test A): periodic additive on a ring of m cells, m in 24,27-40,48,60,64,100, AZ/KA 0/1-based fwd/rev, p 1-31, +-, validity at all 97 cells: real = null. Constant deviation = Caesar, absorbed everywhere. Wheatstone rings 27-39 (novel/wheatstone.py, Barney) also 0. THEME residue: a bearing in the plaintext may need declination correction (riddle) |
| "the information was gathered and transmitted underground to an unknown location" | gathered = text collected from the tableau, transmitted = Morse (the Morse slabs sit at ground level, half buried) -> Morse text as key; "unknown location" = the buried marker / coordinates | CLOSED: Morse as running key (E4, C10, run_layers), Morse-derived numbers (run_nonword), coordinates as digit keys/primers (Barney, S13, chart-sheet tests). THEME: this is a dead-drop story (buried message, "his last message"); K4 "delivering a message" continues it |
| "does Langley know about this" | CIA seal = 16-point compass rose; Langley as key | DEAD/CLOSED: any 16-periodic fixed-alphabet key (E1); LANGLEY in lore lists |
| "buried out there somewhere" | K5 is "buried" (Sanborn 2025 links K5 to this line) | THEME: the K4 plaintext points to a place; not a cipher operation |
| coordinates 38 57 6.5 N 77 8 44 W | digit keys, primers, periods | CLOSED (Barney digit streams, S13, VIC/Gromark primers, period-8 date/coordinate keys) |
| "ONLY WW" | William Webster; W = "double U" (cf. UNDERGRUUND's UU) | CLOSED: names as keys/tableaus (habits T5); UU/WW letter play gives no operation |
| "X LAYER TWO" | K4 has two layers (Sanborn 1990: "two separate systems ... a major clue") | OPEN-U after section 1: the two layers are mask + position key (both unidentifiable from cribs); every keyword-on-one-layer combination CLOSED (S8, two-tableau, run_pinned_table, run_mask_trans L<=5, Barney two-stage) |
| "ID BY ROWS" (engineered second reading) | identify/decode by rows: per-row keys, row restarts, row IDs (chart line numbers) as key, row permutation | CLOSED: per-line constants/keywords (run_perline), row-restart periodic (S6), row-initial keys (Fable inline), row permutations (rowperm, worksheet row reorderings), per-row overlay. Per-row Caesar DEAD (E@21->F, E@30->G in one row) |
| ABSCISSA (K2 key) = x-coordinate | the key depends on the horizontal coordinate = sheet column (period 31 on his 31-column chart); "orientation or positioning" of misspellings points the same way | fixed alphabets at p=31 CLOSED (S6 p25-48, digitcode p=31); mask + column key OPEN-U (only 2 cross-row checks: cols 28, 29). `k5_depth.py anneal_col` is the test once K5 exists |

### K3 (Carter, 26 Nov 1922)

| Phrase | Operation | Status |
|---|---|---|
| "a tiny breach in the upper left hand corner" | start reading at the upper-left corner of a grid; grille/stencil window | CLOSED: corner-growing and spiral/diagonal reads x periodic (run_k3breach, S3), all E1 routes; a grille over K4 = transposition/selection, DEAD by crib positions (Kobek: PT exactly in position) and the E-count proof (Reggie) |
| "widening the hole a little, I inserted the candle and peered in" | look *through* the cut letters: tableau letter seen through each K4 hole; light projection (shadow) | CLOSED in transcript geometry: S1 (15,840 overlays), S11 (x 396k alphabets), rowoverlay (per-row free alignment), shadow_egypt, 3D shadow sweep. Caveat: the 3D sweep used wrong geometry; the Sun Study (web/kryptos_sun_study.html) is the live re-do and its photo check failed. Low prior anyway: K4 was enciphered on paper in 1988 |
| "the hot air escaping caused the flame to flicker" | irregular (aperiodic) key | OPEN-U: matches the nuance-key reading |
| "details of the room within emerged from the mist" | gradual emergence = solve by partial reads | THEME |
| "Can you see anything q?" (the famous answer "Yes, wonderful things" is withheld) | the unspoken answer is the key | **CLOSED today** (test B): WONDERFULTHINGS, YESWONDERFULTHINGS, THEGLINTOFGOLD, STRANGEANIMALS..., CARNARVON, TUTANKHAMEN and ~80 other implied Carter/Berlin/Egypt phrases as periodic keys on AZ/KA tableaus (3 rules, all phases) and as pinned keystreams with an arbitrary mask: real 18 mismatches / 9 mask faults vs null 17 / 7-9; planted 0/0 |
| Carter breach as the Berlin Wall breach | K3 (Egypt 1986) and K4 (Berlin 1989) are the "two events"; K3's breach-and-peer scene prefigures looking through the Wall / through the copper screen from one side to the other ("delivering a message" across) | THEME, strong literary fit, no cipher operation beyond the overlay family above |
| DESPARATLY (A for E, missing E) | PT-level alteration (K3 is transposition only) | the "three stages" habit (chartdiff); no key content |

### Physical instrument

| Element | Operation | Status |
|---|---|---|
| tableau seen from behind (mirrored; obkr.jpg) | reversed alphabet / reversed rows | CLOSED (absorbed by fwd/rev alphabet pairs; reflection test) |
| K4 rows level with tableau rows X, Y, Z, footer | key = letter level with each K4 cell | CLOSED (S1, S11; dx +-4, dy +-27) |
| light through the cut letters onto the tableau / ground / pools | shadow key | CLOSED in model geometry; Sun Study pending real apertures |
| petrified tree, bubbling pool, calm pool | reflection (vertical flip) | CLOSED (run_reflection) |
| lodestone + compass rose | bearing; ring alphabet | ring CLOSED today; bearing THEME (compass_research.md: no measured bearing) |
| copper "scroll" | the Qumran Copper Scroll is a list of buried-treasure locations | THEME only (fits "buried out there") |
| 1988 proof-of-concept plate: plain AZ Caesar rows | the K4 tableau may be plain AZ, not KRYPTOS-keyed | consistent with the fingerprint (AZ is the tightest ruler); plain-AZ keyword runs CLOSED |

## 3. Reading the clues as a whole

Taken together the earlier texts describe a system rather than hand over a key: *palimpsest* (layers), *abscissa* (horizontal position), *layer two* / *ID by rows* (two layers, row-and-column bookkeeping on a sheet), *nuance between shading and absence of light* (a small shift between a row shift and none), *invisible* (nothing written on the sculpture), *flickering flame* (irregular). That is a one-sentence description of the working theory: a hand-drawn substitution chart plus a small aperiodic position key written on the 31-column sheet, position-keyed (so K5 shares coded words), with deliberate slips. Every reading that would instead *supply* the key (Morse, coordinates, WW, SHADOW, the unspoken Carter reply, compass/clock rings, overlays, light) is closed with calibrated nulls. "Who says it is even a math solution" and "delivering a message" belong to the plaintext riddle (a place and an act on the grounds), not to the cipher.

## 4. Ranked open semantic readings (prior x testability)

1. **"Nuance" = small aperiodic shift over a mask (K1 as description of the K4 system).** Only reading with a measured signal (p~0.003). Not decodable from K4 alone; decided by K5 depth (`k5_depth.py`, free-key mode robust to 3 alterations). External data: K5 ciphertext.
2. **"Layer two" / "ID by rows" / palimpsest as an engineered two-reading construction** (section 1). For K4 the second reading is K5 (shared coded words at shared positions). Same decisive data: K5. Zero-cost side effect: treat "ID BY ROWS" as intended text when weighing row-based mechanics (all crib-testable versions already 0).
3. **ABSCISSA + "orientation or positioning" = column-indexed (period-31 sheet) key behind a mask.** Untestable with cribs (two cross-row checks). Decided by K5 in `anneal_col` mode. If the Paradigm archive ever shows a K4 sheet with numbers under the PT row, this is confirmed by inspection.
4. **K3 "peer through the hole" = physical light/overlay reading with the real aperture geometry.** Transcript-geometry versions all closed; the only residual is whether justified vs fixed-pitch letter spacing shifts the level-cell mapping by one cell mid-row. Spec: once 30+ aperture centres are measured on the LoC TIF (Sun Study plan), recompute key_i = tableau letter nearest in physical x,y to K4 cell i (and its mirror), 12 variants x AZ/KA x indicator shift; pass = 24/24; FP per stream ~6e-4 at 8/24 (S1 null), ~1e-10 at 24/24; a few hundred streams. Prior low (K4 enciphered on paper).
5. **Compass/lodestone/declination as a plaintext bearing instruction** (ENE from the clock or from the lodestone, corrected for magnetic variation). THEME: not a cipher step; needs the plaintext. Ring-alphabet and clock-ring cipher versions are closed (today's test A, Wheatstone, clock C1-C17).

Below the fold (closed today or earlier, listed so nobody re-proposes them): unspoken Carter answers as keys; 32-point / 24-hour / 60-minute ring arithmetic; Morse E-run counts as a key; SHADOW/MEDUSA Projector keys; WW/Webster; coordinates; "upper-left corner" reads; grilles; reflections; row restarts and per-row keys.

## 5. Tests run today

Script: `/private/tmp/claude-501/-Users-scottdunphy-PycharmProjects-K4/08cd910e-1aec-4adf-a5c5-a6d027bec969/scratchpad/semantic_tests.py` (12 s).

- **Test A, ring-modulus periodic additive ("magnetic field" / compass rose / clock).** C = (P +- k[i mod p]) mod m on a ring of m cells, letters numbered AZ or KA, forward or reversed, 0- or 1-based (8 numberings), m in {24, 27-40, 48, 60, 64, 100}, p 1-31; key per residue forced by the first crib in the class, remaining cribs checked, and every one of the 97 decrypted cells must be a letter. Planted m=32, p=11 recovered (plus its p=22 multiples). Real: 24 hits, all at p=27-29 with m=24 (vacuous: no two cribs share a residue there); 10 shuffled CTs: 24-37 hits of the same vacuous kind. NEGATIVE.
- **Test B, implied/unspoken Carter and Berlin phrases as keys.** 80 phrases (WONDERFULTHINGS, YESWONDERFULTHINGS, EVERYWHERETHEGLINTOFGOLD, STRANGEANIMALSSTATUESANDGOLD, CARNARVON, TUTANKHAMEN, VALLEYOFTHEKINGS, DELIVERINGAMESSAGE, WORLDCLOCK, TISYOURPOSITION, SUBTLESHADING, ABSENCEOFLIGHT, IDBYROWS, XLAYERTWO ...), all phases, key letters indexed AZ/KA, PT/CT alphabets AZ/KA, Vig/Beau/Var (fixed test, count mismatches) and pinned keystream + arbitrary PT-side mask (count repeat/injectivity faults). Planted KA-Vig WONDERFULTHINGS: 0 mismatches; planted random mask + the same key: 0 mask faults. Real: best 18 mismatches (YESWONDERFULTHINGS) and 9 mask faults; 80 random 15-letter keys: 17 / 9; three shuffled CTs: 17-18 / 7-9. NEGATIVE.
- **IDBYROWS verification** (section 1): deterministic recomputation from `kryptos_texts`, no statistics needed beyond the 26^-8 chance argument.

## 6. What would decide the rest

- K5 ciphertext (readings 1-3): depth attack ready.
- A photo or scan of any K4 sheet from the RR/Paradigm archive (reading 3): a numeric row under the plaintext would confirm the column-key form by inspection.
- Measured aperture positions from the LoC Highsmith TIF (reading 4): feeds the Sun Study; then one recomputation of the level-cell overlay.
- Nothing in K0-K3 that we can read supplies a key that the cribs would accept; further mining of the earlier texts for key material has an expected value near zero.
