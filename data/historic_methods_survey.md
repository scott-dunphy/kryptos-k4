# Survey of historic hand and simple mechanical ciphers vs K4 (2026-10-17)

Scope: pre-1990 hand, field, agent, aircrew and simple-device systems from the standard catalogues. For each one: (a) is it compatible with K4, (b) has the project tested it (NOTES.md heading), (c) how plausible it is for Scheidt/Sanborn in 1990, (d) can the 24 crib letters test it.

## How to read this

**K4 hard constraints (all verified on `k4lib.CT`):**
- C1: 97 letters, no digits.
- C2: all 26 letters occur (J=3, W=5, Z=4).
- C3: positional alignment (EASTNORTHEAST at 21-33, BERLINCLOCK at 63-73).
- C4: TWO self-encryptions, S->S at pos 32 and K->K at pos 73.
- C5: IoC 0.036.
- C6: same-letter digraphs at both parities.
- C7: CT has only 2 E's, but the cribs need 3. So **no pure transposition of any kind** is possible unless a crib letter is wrong.
- C8: a single substitution with ANY alphabet is impossible. E->F at 21 but E->G at 30, and T->V at 24 but L->V at 66. This kills monoalphabetic, homophonic, key-phrase and per-row Caesar systems.
- C9 (novel): direct periodic substitution with arbitrary per-column alphabets is impossible at p in {1-7, 9, 10, 14, 15, 17, 21, 25}. Quagmire IV with any alphabets is impossible at p<=12 except 8.

**Prior scale:** H, M, L, VL.
- H: historic, by hand, memorable key words, US/CIA lineage.
- VL: machine, classified in 1990, or contradicts Scheidt's descriptions.

**Sources:** "Gen." means general catalogue knowledge from Gaines *Cryptanalysis* (1939/1956), Kahn *The Codebreakers* (1967/1996) and Friedman *Elementary Military Cryptography*. I did not re-read those books for this survey. Web sources are linked where they were actually read.

## 1. ACA cipher types (cryptogram.org list, read 2026-10-17)

Source: https://www.cryptogram.org/resource-area/cipher-types/

| ACA type | (a) Compatible? | (b) Project status | (c) Prior | (d) Crib-testable |
|---|---|---|---|---|
| Aristocrat, Patristocrat, Headlines, Key Phrase | No (C8, C5) | n/a, structural | - | - |
| AMSCO, Cadenus, Complete/Incomplete Columnar, Myszkowski, Nihilist Transposition, Railfence, Redefence, Route, Sequence Transposition, Swagman, Grille | Not alone (C7). Only possible as one layer combined with a substitution | Transposition + periodic sub: E1, E2, E3, S3, S5, S7, C4, C7, "Dictionary-keyword columnar + Myszkowski", Nicodemus | M (K3 used a transposition) | Yes, done |
| Baconian | No (5x expansion, C3) | n/a | - | - |
| Bazeries (ACA: 5x5 square + number-word transposition) | No (C2, 5x5) | n/a | - | - |
| Bifid, CM Bifid, Twin Bifid, Foursquare, Two-square, Tri-square, Phillips, Phillips-RC, Playfair, Seriated Playfair | No (C2: 5x5 drops a letter; C6 for Playfair) | "Playfair impossible" (novel batch 3) | - | - |
| Slidefair | **No**. It can never encrypt a letter to itself: the opposite-corner rule plus the "same column -> letters to the right" rule guarantees C!=P. K4 has S->S and K->K (C4). https://www.cryptogram.org/downloads/aca.info/ciphers/Slidefair.pdf | New structural kill (this survey) | - | - |
| Portax | Probably no (Porta-derived reciprocal; Porta is already impossible because of E->F). Not analysed in detail | not tested | L | - |
| Porta | No (E->F at 21) | novel batch 1 | - | - |
| Checkerboard, Grandpre, Homophonic, Monome-Dinome, Morbit, Nihilist Substitution, Numbered Key, Pollux, Syllabary, Tridigital | No (C1/C2: output is digits or a small coordinate alphabet) | digit-layer variants tested: S13, digitpad, VIC expansion | - | - |
| Fractionated Morse | No (C3). It outputs exactly 26 trigram letters, but its length is not preserved. BERLINCLOCK = 34 Morse symbols + 11 separators = 15 CT letters, not 11 | n/a | (M for "language base") | - |
| Trifid, Twin Trifid | Weakly compatible (27-cell cube; P(no filler in 97 outputs) about 0.026; not letter-aligned) | Trifid: T1 keyword cubes, periods 1-97, negative. Twin Trifid: untested | L | Yes (as T1) |
| Digrafid | Disfavoured (27-symbol; digraphic, but 97 is odd) | untested | VL | - |
| Vigenere, Variant, Beaufort, Gronsfeld, Quagmire I-IV | Yes | E1, alphapairs, P4/q4exact, lore/dict alphabets | H | Done |
| Autokey, Condi (PT-autokey in keyed alphabet) | Yes, but argued against: K5 "same coded words in same positions" points to a position-only key | P2, novel chained/self-keyed | M | Done |
| Progressive Key, Interrupted Key | Yes | E5, P3 | M | Done |
| Running Key | Yes | E4, S10, C10 (K1-K3, Carter, KJV, Moby Dick, Smith) | H | Partly. See shortlist #1 |
| Nicodemus, Ragbaby | Yes | run_nicodemus, run_ragbaby | M | Done |
| Gromark | Yes | E-G, VIC expansion, "Alternative alphabet families" (columnar-transposed keyword alphabets + digit key: 0 flags), Bean primers annealed | M | Done |
| **Periodic Gromark** | Yes | **Tested in this survey (negative)**: novel/periodic_gromark.py | L-M | Yes |
| Null | No (cover text) | n/a | - | - |
| Compressocrat | Not a K4-type system | n/a | - | - |

## 2. Classic catalogue systems (Gaines, Kahn, Friedman, FM 34-40-2)

FM 34-40-2 chapter list (read): mono, multiliteral, polygraphic, periodic and aperiodic polyalphabetic, transposition, codes, syllabary. https://irp.fas.org/doddir/army/fm34-40-2/index.html

| Method | (a) | (b) | (c) | (d) |
|---|---|---|---|---|
| Alberti disk (1467) | Yes | "Historic rotor/disk systems" T1/T2 | M | Done |
| Trithemius tabula recta (progressive) | Yes | E5 | M | Done |
| Bellaso / della Porta reciprocal tables | No (fixed-point-free pairing; E->F) | structural | - | - |
| Cardano autokey | Yes | P2/P3 | L | Done |
| Vigenere (1586) autokey | Yes | P2 | M | Done |
| Rossignol Great Cipher, nomenclators, codebooks (one-part/two-part), trench codes | No (C1/C3) | n/a | - | - |
| Jefferson wheel (36 disks) | Yes | Original disk alphabets not preserved; M-94 tested instead | L | No |
| Bazeries cylinder (1891, 20 disks) | Probably no. Crypto Museum says 25 letters per disk, which would conflict with C2 (other sources say 26; not settled). https://www.cryptomuseum.com/crypto/usa/m94 , https://en.wikipedia.org/wiki/Jefferson_disk | untested | L | Only if the disk alphabets are obtained (Bazeries 1901) |
| M-94 (1922-43) | Yes | "M-94 cylinder", negative | M | Done |
| M-138-A strip | Yes | untested. The strip sets were classified and changed often, so they cannot be reconstructed | L | No |
| St-Cyr slide | Yes (= keyed Vigenere) | covered by E1/alphapairs | M | Done |
| Beaufort (1857) | Yes | E1 | M | Done |
| Wheatstone cryptograph | Yes | novel/wheatstone.py, negative | M | Done |
| Wheatstone Playfair, US Army Playfair (1917) | No (C6, C2) | structural | - | - |
| Nihilist (Russian, digits) | No (C1) | n/a | - | - |
| Chaocipher (1918) | Yes | novel chao.py (keyword alphabets) | L | Done |
| Hill (1929) | Yes | novel/stego hill: n=2,3 killed; n=4 underdetermined | L | Done |
| Kryha, Hebern (single rotor) | Yes | rotor T1 | L | Done |
| Enigma, Typex | No (no fixed points; C4) | structural | - | - |
| Hagelin C-36/C-38/M-209 | Yes (Beaufort with a long pin/lug key; self-encryption possible) | Only restricted sub-spaces, by an outside group (Patrick, in prior_tests_research.md) | L (machine; settings are not "remembered") | Weak: 24 key values vs about 131 pin bits + lug cage |
| SIGABA | Yes in principle | n/a | VL (still classified in 1990, which conflicts with "didn't compromise current methods") | No |
| Confederate Vigenere (MANCHESTERBLUFF, COMPLETEVICTORY, COMERETRIBUTION, period 15) | Yes | killed by E1 identity, p<=24 | M | Done |
| Union route (word) transposition | No (C7; word-level) | n/a | - | - |

## 3. WWI/WWII field and German/Berlin hand systems

| Method | (a) | (b) | (c) | (d) |
|---|---|---|---|---|
| ADFGX / ADFGVX (1918) | No (output is 5 or 6 letters; C2) | n/a | - | - |
| UBCHI (double columnar) | Not alone (C7) | E2, double route | M | Done (with substitution) |
| Doppelkastenschlüssel (double Playfair) | No (two 5x5 squares; J present; C6) | structural; Bean 2021 | - | - |
| **Rasterschlüssel 44** (1944, 24x25 stencil, 10 white cells per row, read by numbered columns). Its Buchstabentauschtafel is only for place-name digraphs. https://en.wikipedia.org/wiki/Rasterschl%C3%BCssel_44 , https://ciphermachinesandcryptology.com/en/rasterschlussel44.htm | Not alone: it is a pure transposition (C7). Only RS44-style transposition + substitution would be compatible | untested as a stencil | L-M (German WWII, "matrix", Berlin theme) | Poor. The stencils were random daily keys; Wikipedia notes cryptanalysis needed a ~40-letter crib even with the stencil format known. Sampling only |
| Reservehandverfahren (Kriegsmarine): cage transposition + bigram tables. https://en.wikipedia.org/wiki/Reservehandverfahren , https://cryptomuseum.com/crypto/germany/rhv/index.htm | Marginal: digraphic needs an even length (97 is odd); the cage scatters the cribs | untested | L | No (676-entry table) |
| Slidex, BATCO, Griddle-type code cards | No (codes or digits; C1/C3) | n/a | - | - |
| Syko (RAF aircrew, 32 columns of A-Z + 0-9). https://en.wikipedia.org/wiki/Syko_Cipher_Device | Mostly no: the card alphabets include digits (C1); position-periodic (32) with arbitrary alphabets; p=32 is unconstrained | n/a | L (it is an aircrew system) | No (card unknown) |
| Abwehr / SD agent double transposition, book ciphers | No alone (C7) / digits | n/a | - | - |
| Rote Kapelle (Berlin) checkerboard + book | No (digits) | S13 covers digit layers | - | - |
| Stasi/KGB OTP + conversion card (digits). https://cryptomuseum.com/crypto/otp/ddr ; CIA-in-GDR digit OTP + matrix card: https://www.numbers-stations.com/articles/cia-agents-in-east-germany-use-of-numbers-station/ | No as a final layer (digits). A letter-to-digit-to-letter round trip is S13 | S13, digitpad | M (Berlin) | Done (structured pads); random OTP needs K5 |
| VIC (Soviet, 1950s) | No (digits) | VIC components tested (E-G, VIC expansion) | M | Done |

## 4. Agent, OTP and aircrew systems (Scheidt's "agents or pilots in case of capture")

What the record actually shows:

1. **US aircrew were taught classified covert-letter encryption in advanced SERE training.** CIA *Studies in Intelligence* 60(1), 2016, Peterson & Taylor, "A Shield and a Sword" (https://www.cia.gov/resources/csi/static/Intel-Support-to-Communications.pdf):
   - "a small number of POWs had, in fact, learned more advanced, classified encryption methods during advanced SERE training".
   - "Stockdale and his small group memorized the code".
   - Messages were "translated into encryption code and then written down to be sent in a series of sequenced letters", even when letters were limited to six lines.
   - Basic SERE taught "doubletalk".

   This is the closest documented match to Scheidt's wording: memorized, executed years later, keyed, hand-only, and English plaintext disguised inside innocent text (compare "I masked the English language" and "a bit of stego"). The method itself is not public.
2. **WWII precedent, MIS-X "Code Users" (CUs).** Aircrew were trained before capture to embed coded messages in POW letters, and censors flagged CU names (https://www.nationalmuseum.af.mil/Visit/Museum-Exhibits/Fact-Sheets/Display/Article/197474/mis-x-the-us-escape-and-evasion-experts/ , https://conscript-heroes.com/Art41-MIS-X-960.html). The British equivalent was MI9 letter codes: an indicator plus hidden words "alternated every fourth and fifth word", with trigger words starting "an intricate alphabetical sequence" (https://www.plymouth.ac.uk/news/researchers-crack-mi9-codes-to-discover-pows-wartime-requests). These are stego word-selection codes. The ciphertext they produce is an innocent letter, not a random-looking string, so K4's CT cannot be such a carrier. **Implication:** if Scheidt modelled K4 on these systems, the analogue is a memorable keyword cipher stage plus a "masking" stage, and the masking may sit in the plaintext (a hidden second message), which can only be tested after decryption.
3. **Tap code** (SERE, 5x5, C=K): no (C2). https://en.wikipedia.org/wiki/Tap_code
4. **SARNEG** (SAR Numerical Encryption Grid): a 10-letter word with no repeated letters encodes digits 0-9 for downed aircrew (position, time, heading). https://www.militarydictionary.org/term/search-and-rescue-numerical-encryption-grid. Output is only 10 letters, so no (C2) as a full system. It is still the canonical "simple, remembered, with the correct key word" pilot method. Lesson: aircrew keys are isogram words (no repeated letters), which favours isogram keywords in any search.
5. **DRYAD** (KTC 1400 D, authentication and numeral cipher): 25 rows of A-Y permutations. https://en.wikipedia.org/wiki/DRYAD. No: no Z, and K4 has 4 Z (C2).
6. **ISOPREP / blood chit / AFM 64-5 / FM 21-76-1:** authentication by personal questions and visual signals; no letter cipher found. (FM 21-76-1 index: https://www.globalsecurity.org/military/library/policy/army/fm/21-76-1/index.html; the PDF did not download. AFM 64-5 was not consulted.)
7. **DIANA** (US Special Forces, Vietnam): letter OTP with a reciprocal trigraph table (https://en.wikipedia.org/wiki/Beaufort_cipher , https://sfrvn.net/c1/diana.asp). Algebraically C = 25 - P - K (mod 26, A=0), which is a Beaufort variant. Self-encryption is possible when K is odd, so it is compatible. Crib key values (= 25 - P - C): QOQLWVTPFPPPO / LXTTYTLPGIF, not readable. Periodic and running-text DIANA keys are covered by the E1/E4/C10 variants (multiplier -1). A random pad is untestable without K5 (standing item).
8. **SOE/OSS letter OTP + silk conversion squares (LOP), and "26 mixed alphabets + keyword" silk tables.** Duke collection, item A: keyword PHOENIX selects rows; the example has a->a in row E, so self-encryption occurs. https://people.duke.edu/~ng46/collections/crypto-silks.htm. Fairbrother says the squares were "mostly all the same": https://www.metzdowd.com/pipermail/cryptography/2026-January/039332.html.
   - Compatible. It is the plainest reading of "matrix codes Ed gave me".
   - With an unknown table it is NOT testable. **Tested in this survey:** unknown 26-row table + periodic dictionary keyword, rows shared by repeated key letters. 34,781 / 221,583 words pass vs 21k-60k on 5 shuffled-CT nulls. No power.
   - Testable only if a real printed table is transcribed (shortlist #2).
9. **SOE poem code / WOK** (double transposition keyed from a memorized poem). https://en.wikipedia.org/wiki/Poem_code. No alone (C7). The memorized-poem idea transfers to running keys (shortlist #1).

## 5. Experiments run during this survey (all negative)

| Test | Model | Space | Result |
|---|---|---|---|
| Periodic Gromark (novel/periodic_gromark.py) | ACA procedure, validated exactly on the ACA ENIGMA example. CTA = keyword transposition-block alphabet; primer = column ranks; chain d[i]=d[i-n]+d[i-n+1] mod 10; C = CTA[(±off_g + P + ±d_i) mod 26], off_g = CTA position of header[(i//n) mod n]; PT index in AZ or CTA | 221,583 dictionary + lore words x 8 variants | Best 8/24 (real) vs 8/24 (shuffled-CT null). 24/24 is needed. NEGATIVE |
| Nihilist-style coordinate addition in a 26-cell letter matrix (novel/crt_matrix.py) | 2x13 / 13x2 keyword grid, coordinates added mod (2,13). By CRT this equals Vig/Beau over alphabet X[n]=grid[n mod R][n mod C], which is not a keyword alphabet, so earlier tests missed it | 221,583 words x 2 shapes x fwd/rev x Vig/Beau x periodic p1-24 (>=4 collisions) | 0 hits; null 0; planted p=9 recovered. NEGATIVE |
| Unknown SOE-style 26-row table + dictionary keyword (novel/randtable_kw.py) | rows chosen by keyword letter, table free | 221,583 words | Real at chance: 34,781 passes vs 21k-60k on nulls. UNTESTABLE |

Also noted: a non-square Bifid (e.g. 2x13) is ill-defined, because row and column coordinates have different ranges. So the only 26-letter Delastelle fractionation is Trifid with one spare cell (already tested).

## 6. Ranked shortlist: UNTESTED, K4-compatible, crib-testable

1. **Running key from memorized texts** (the poem-code idea in additive form).
   - Why: "simple, can be remembered, executed years later"; SOE agents memorized poems; aircrew memorized codes.
   - Corpus: national anthems (US, German Deutschlandlied/DDR anthem, UK, Marseillaise in English), Pledge of Allegiance, Gettysburg Address, Declaration (preamble + full), US Constitution preamble, JFK "Ich bin ein Berliner" and Reagan "Tear down this wall" speeches, Leo Marks' poem "The Life That I Have", popular poems (Poe "The Raven", Kipling "If", Frost, Shakespeare soliloquies/sonnets, "Jabberwocky", "Twas the night before Christmas", Gray's Elegy), Boy Scout oath, Army Code of Conduct (aircrew-relevant), CIA/OSS creeds, nursery rhymes. (Lord's Prayer, Psalm 23 and John 8:32 are already covered by KJV.)
   - Get exact texts from Gutenberg/Wikisource, keep them verbatim, and try with and without the title.
   - Model: k_i = a*K[o+i]+b (clocklib.scan_num, 12 variants) plus unknown single mixed alphabet (clocksingle Vig/Var/Beau). All offsets, forward and reversed. Also a start at word w of the text (the "key word/s" as an indicator).
   - Size: about 1e5-1e6 offsets.
   - False positives: fixed variants need 24/24 (P~26^-24); unknown-alphabet null is 0 in 2.4e7. Effectively zero.
2. **Real printed conversion tables** (SOE silk "26 mixed alphabets", the Duke item; Marks' LOP square in *Between Silk and Cyanide* ch. 30; OSS/CIA letter-OTP tables; DIANA, which is Beaufort and already covered).
   - Transcribe the table images.
   - Test with a periodic dictionary keyword (221k), the texts in #1 as running key, and K1-K3 PT.
   - Test: row[key letter](P)=C at all 24 cribs. Random pass about 26^-24 per key.
   - Blocker: getting a legible table.
3. **Turning (Fleissner) grille 10x10 (97 + 3 nulls/"?") + periodic or keyword substitution.**
   - Why: "matrix"; RS44/Cysquare-like stencils; historic.
   - Only grille-transposition alone has been tried (by others), and it is impossible by C7.
   - Model: perm from a grille (4^25 ≈ 1.1e15), then substitution periodic p<=24 (cribfilter kernel, m>=5).
   - Not exhaustive: run DFS over grille quadrant choices with residue-consistency pruning on crib cells, or anneal grille + key with the E1 kernel as fitness.
   - False positives: as E1 (m>=5 at p<=20, about 0 per 1e8). Calibrate with shuffled CT.
4. **RS44-style random stencil transposition + keyword Vigenere** (Berlin/Wehrmacht lineage).
   - Model: a 24x25 stencil with 10 white cells per row is out of reach. Restrict to Sanborn's 31-column sheet geometry: white-cell masks generated from a keyword (e.g. letters of the keyword row marked), with column read order from a keyword.
   - Size: dictionary keywords^2 x p1-24, about 1e9 with E1 kernel. False positives: as E1.
   - Low prior. Only worth it if 1-3 fail.
5. **Hagelin M-209 with full keying constraints** (historic US Army, Beaufort-type, compatible).
   - Model: C = (25 - P + k_i) mod 26, where k_i = number of bars with a lug on an active pin. The 6 wheels (26, 25, 23, 21, 19, 17) are indexed at i + offset.
   - Approach: SAT/ILP over pins (131 bits) + lug cage (choose 27 bars from the 2-lug patterns) using the 24 k values.
   - Expect many solutions (underdetermined). Use only together with a language score on the decrypted non-crib letters vs a shuffled-CT null.
   - Low prior (a machine; settings are not "remembered").

Shortlist items already run in this survey and now closed: Periodic Gromark; 26-cell-matrix coordinate addition. Families that look historic but are structurally impossible: Slidefair, Portax (probably), DRYAD, SARNEG, Doppelkasten, RS44 alone, ADFGVX, tap code, Fractionated Morse, all 5x5 systems.

## 7. Gaps and honesty notes
- The mechanics of the SERE advanced encryption (Vietnam) and the MIS-X CU codes are not public. Nothing here reconstructs them.
- The Bazeries disk letter count is unsettled (25 vs 26).
- AFM 64-5, CREST searches for aircrew codes, NSA Cryptologic Quarterly pieces, Gaines/Kahn/Friedman: not re-read for this survey.
- Scheidt/Sanborn quotes are as supplied by the user; their sources were not re-verified here.
- The survey assumes the cribs are exact. C7 (no pure transposition) depends on all three crib E's being correct.
