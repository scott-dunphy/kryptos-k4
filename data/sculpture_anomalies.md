# Kryptos sculpture: physical anomalies and lore relevant to K4 (team stego, 2026-10-17)

Grids saved verbatim: `data/sculpture_left.txt` (cipher side, 28 lines, 869 chars = 865 letters + 4 '?'),
`data/sculpture_right.txt` (tableau, 28 lines, 867 letters). Source: Elonka Dunin transcript (Gwyn transcription,
hand-verified 2002, extra L added 2003) https://elonka.com/kryptos/transcript.html. Counts match Wikipedia (869 / 867).

## 1. Layout (row index 0-27, 0-indexed; four copper plates of 14 lines each)
Plate 1 = left rows 0-13 (K1 rows 0-1.., K2), plate 3 = left rows 14-27 (K3, K4); plate 2 = tableau header+A..M,
plate 4 = tableau N..Z+footer. Left line lengths:
`32 31 31 30 31 32 31 31 32 31 30 31 31 31 | 32 30 31 30 32 30 32 31 33 29 31 31 31 31`.
- K4 = row 24 cols 27-30 (`OBKR`, after `?` at col 26) + rows 25, 26, 27 (31 chars each) = 4+31+31+31 = 97.
  K4 index i -> row 25+(i-4)//31, col (i-4)%31 for i>=4. Cribs: EAST at row 25 cols 17-20, NORTHEAST row 25 col 21 ..
  row 25 col 29 (21..29), BERLIN = row 26 cols 28-30 + row 27 cols 0-2, CLOCK row 27 cols 3-7.
  So BERLIN straddles a line break exactly at BER|LIN.
- Rows 24-27 of the left side are level with tableau rows X, Y, Z and the footer (`  ABCD...ZABCD`).
- Line widths not justified in the transcript; actual physical alignment (left/right flush, spacing) uncertain.
- Lines 3,7,9 have the '?' of K2; line 24 col 26 has the '?' between K3 and K4 (K3 ends "...ANYTHING Q?").

## 2. Deliberate / acknowledged anomalies
| Item | Detail | Source |
|---|---|---|
| IQLUSION (K1) | ILLUSION, L->Q. Coding chart: PT spelled ILLUSION but key misspelled PALIMPCEST at chart line 7 col 26; L+C -> K (correct key would give W). | Wikipedia, NYT 2010 charts |
| UNDERGRUUND (K2) | O->U. Chart has correct UNDERGROUND, key ABSCISSA, CT E under O; sculpture has R instead (E->R in CT). | Wikipedia |
| DESPARATLY (K3) | E->A and a missing E. | kryptools |
| DIGETAL (Morse) | I->E; INTERPRETATI(T/U) truncated. | kryptools, Wikipedia |
| Misspelling letter sets | wrong letters Q,U,A,E (+ L of chart key C/S) -> "EQUAL" lore; correct letters L,O,E,I (+S). CT changes K<-W (K1), R<-E (K2). | derived |
| K2 omitted letter | an S omitted from CT "for aesthetic reasons" (end of line); PT X; ending is XLAYERTWO not IDBYROWS (Sanborn 2006-04-19). | Wired 2006 |
| YAR superscript | Y, A, R of `ENDYAHR` (left row 14, cols 3,4,6 — first line of plate 3 / K3) are the only superscript characters. | Wikipedia |
| Extra L (tableau) | Row N (right row 14) has 32 chars, ends `...GHIJL` + extra `L`; with it the right-most column reads H I L L downward (rows H..). Omitted on small replicas. | Wikipedia, Bauer-Link-Molle 2016 |
| Same row | Both YAR and the extra L sit on row 14 (first line of the bottom plates). | derived |
| Tableau header/footer | `ABCD...ZABCD` (30) offset one col; rows = letter + KA shifted (30 chars), alphabet KRYPTOSABCDEFGHIJLMNQUVWXZ. | transcript |
| Morse (K0) | E E VIRTUALLY E / E E E E E E INVISIBLE; DIGETAL E E E / INTERPRETATIT; E E SHADOW E E / FORCES E E E E E; LUCID E E E / MEMORY E; T IS YOUR / POSITION E; SOS; RQ (or YR upside down). Extra Es = 26 (by this count). | Wikipedia |
| Compass/lodestone | Compass rose engraved on granite, needle points at lodestone; direction ~ENE (the EASTNORTHEAST crib). | FAQ, rumkin |
| Coordinates | K2 38 57 6.5 N 77 8 44 W ~ 53 m SE of sculpture; USGS marker buried adjacent, later removed ("it is important"). | rumkin K5 page (dinner notes) |

## 3. Statements (exact where possible)
- Sanborn (Wired 2005-01-20): "I will say that I have left instructions in the earlier text that refer to later text."
  Also "most of my things are rife with mistakes on purpose"; "five or six" techniques; "matrix codes Ed gave me";
  "visual systems for encoding ... individualistic".
- Sanborn: misspellings matter not for what they are but for "their orientation or positioning" (Elonka FAQ).
- Scheidt (Wired 2005): "four different processes. Two of them are similar and the other two are different";
  "the last process, I masked the English language"; "the masking technique may not be known".
  Scheidt (NPR 2005): masked the frequency advantage. No public Scheidt quote with the word "stego" found.
- Sanborn 1989 letter: right side "partly deciphered by using the table and partly by using a potentially challenging encoding system".
- 1:1 mapping NYPVTT->BERLIN (Zola dinners 2011/2013); 2019: Sanborn only commits to 97 chars and BERLIN starting at char 64.
- "What do you have in letter-position 27?" used to check claimed solutions (NYT 2010).
- 2025 open letter (Spy Museum, 2025-11-12): two events in the solution — 1986 Egypt trip and 1989 fall of Berlin Wall;
  BERLINCLOCK = World Clock (Weltzeituhr); codes are about "delivering a message"; K5 linked to "its buried out there somewhere";
  "Who says it is even a math solution?"; K5 97 chars sharing "some of the same coded words in the same position".
- RR Auction lot 2001 (sold $962,500, buyer Paradigm, disclosed 2026-06): "original coding system for K4";
  "handwritten signed Kryptos plain texts used for screen cutting K4 (2 pieces)"; "original scrambled texts shown to the
  Department of Historical Intelligence" (= the strip-cut PT pages Kobek/Byrne found; scrambling was for review, not crypto);
  1988 alternate K4 plaintext+coding chart = K5. K5 CT held by Paradigm, unreleased.
- Kobek/Byrne (2025-09) have the PT; not public. Public "reconstructions" (e.g. solvekryptos.com) are speculation.

## 4. Sources
- https://elonka.com/kryptos/transcript.html , https://elonka.com/kryptos/faq.html
- https://en.wikipedia.org/wiki/Kryptos (fetched 2026-10-17)
- https://www.kryptools.com.about.ag/hints.htm (quote collection), https://rumkin.com/reference/kryptos/k4/ , /k5/
- https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/ (2025-11)
- https://www.rrauction.com/jim-sanborn-kryptos-k4-solution-auction/ ; https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/
- https://www.paradigm.xyz/writing/kryptos

## 5. Sanborn's worksheets (kryptools Sheets page: https://www.kryptools.com.about.ag/Sheets/sheets.htm)
- K1 chart (NYT 2010-11-20): key PALIMPCEST written at top; rows of 31 cells: PT / key / CT; K1 = 31+31+1 (last N/L/D on a third row). Ticks under CT K (row 1 col 17) and Y.
- K2 chart: key ABSCISSA; rows numbered 3..8 (= panel line numbers); 31 cells; '?' copied into PT and key rows and does not consume a key letter; overflow letters written in a margin column.
- K3 step 1: 8 rows x 42; step 2: 14 x 24 grid (rotation). Equivalent to CT_idx = (192*PT_idx + 191) mod 337.
- Panel-4 worksheet (NOVA 2007): 14 lines x 31 = K3 (336) + '?' + K4 (97) exactly; sculpture deviates only in K3 rows (displaced letters A, T, T, IT for the S-curve).
- K4 clue sheet (2010): '?' shown unnumbered before OBKR (1-4); K4 numbered 1..97.
