# External info on Kryptos K4 (research date 2026-10-17)

Method: WebSearch/WebFetch (summarizing fetcher, so quotes are as relayed) plus direct download and visual inspection of RR Auction lot images (saved in scratchpad rr/). Confidence tags: [H] primary/seen directly, [M] reputable secondary, [L] unverified/third-party.

## 1. RR Auction lot 2001 (sold $962,500)
URL: https://www.rrauction.com/auctions/lot-detail/350761607302001-the-complete-secrets-of-kryptos-jim-sanborns-private-archive/ [H]
Sale recap: https://content.rrauction.com/jim-sanborns-complete-kryptos-archive-sells-for-962500-at-auction/ [M]

Lot text (summarized): archive of working documents; K1-K4 materials, original coding charts for K1-K3, "original coding system for K4", unpublished 1988 alternate K1 plaintext+chart, unpublished 1988 alternate K4 plaintext+chart = K5. 17 numbered items; items 1-7 are WITHHELD from photos "for secrecy". RR says it never saw the archive and relied on Sanborn's representations. Private afternoon with Sanborn included.

Public images (cdn.rrauction.com/auction/730/3507616_N.jpg, N = 291,2,3,8,9,30,16,25,23,24,27,31; I viewed all). NONE show K4/K5 charts, worksheets or ciphertext. What is visible:
- _2.jpg, _3.jpg, _30 composite: curved copper "proof of concept" plate, stamped "J.S. 1988" (_9.jpg edge). Cut-out letters in 3 rows of 8, each row is the alphabet shifted by one: CDEFGHIJ / DEFGHIJK / EFGHIJKL (a Vigenere/Caesar tableau fragment, normal alphabet, no keyed alphabet visible).
- A second plate (_3.jpg) shows rows "EECHIJKL / DEECHIJK / CDEECHIJ" with mirrored/reversed glyphs (letters like G, J, L reversed; some letter substitutions look like E for F). Reading is hard; probably a mirrored-back-side view of the same kind of plate (Sanborn's Vigenere table viewed from the other side). Not legible as K4 material.
- _291 and composite (_30? the black-background shot): Escort Required badge No. 13764 dated 15 May 1991; GSA contract SF-33 GS11P88EGC0237 ($250,000, 29 Jul 1988); SF-30 modification (+$5,000, 186-day extension); CIA dedication program 5 Nov 1990; remarks transcript; photos (Sanborn at studio, shaking hands at CIA podium, cutting copper); yellow legal-pad handwritten sheets (see below).
- Background of _291: faded printed grid/table of letters, out of focus, unreadable (grid layout only; cannot give dimensions).
- Yellow legal-pad sheets (composite) show handwritten K2-style text ("Between subtle shading and the absence of light lies the nuance of illusion X ... it was totally invisible. Hows that possible? They used the earths magnetic field X the information was gathered and transmitted undergrund to an unknown location X does Langley know about this? they should it's buried out there somewhere"), with small line-number marks (100, 200 etc.) in margin. This is K2 working text, not K4.
- _16.jpg: typed transcript of Sanborn's 1990 dedication remarks. Relevant statements: plates inside are "four separate copper sheets"; "two plates ... that is Vigenere's table ... I used that table to encipher the top plate"; "I haven't given anybody the key words"; "The bottom plate is enciphered in a much more difficult fashion"; "There are two systems of enciphering the bottom text ... two separate systems and that is a major clue in itself." (Known quote, 1990; confirms two-system bottom half.)

Gap: no image of any K4/K5 coding chart, worksheet, grid, or table is public. NYT/WaPo/AP/Smithsonian press images not retrievable (WaPo 403); no archived-site checks done.

## 2. Kobek and Byrne
Sources: https://zonamotel.substack.com/p/interview-kryptos-k4-uncovered-jarett [M]; https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/ [M, seller-biased]; https://www.scientificamerican.com/article/how-the-cias-kryptos-sculpture-gave-up-its-final-secret/ [M]; NYT 2025-10-16 (cited by Wikipedia, not fetched).
- Found Sept 2025 at Smithsonian Archives of American Art, ~5 pages of scrambled text; images ~33rd/34th of Byrne's photos. Pages = 1990 copies Sanborn made for CIA's historical-intelligence reviewers to show text was inoffensive: sentences cut into strips, taped out of order.
- Kobek: text "makes semantic sense"; known plaintexts (BERLIN CLOCK, EAST NORTHEAST) "exactly in the right position"; "exactly the right length" (97); initially thought half was there. "No way on earth that this is a cryptographic solve."
- Emailed Sanborn 3 Sep 2025; Sanborn confirmed accuracy; files sealed 50 yrs (to 2075). They refuse to publish plaintext; claim RR lawyers threatened them.
- They say they lack: method, cipher system, coding charts, how K4 relates to K5. Byrne: lay person without artist clues would struggle with the strips.
- Nothing published on themes/words/structure beyond the above. No books/podcasts with content found. Gap.

## 3. Sanborn statements 2025-2026
- Open letter Aug 2025: https://www.elonka.com/kryptos/OpenLetterAug2025.html [H]. Auction 20 Nov 2025; "Power resides with a secret, not without it"; K4 solved still leaves a riddle "K5"; AI verifier planned. No method hints.
- SciAm 12 Nov 2025 "final clues": https://www.scientificamerican.com/article/cia-kryptos-puzzle-creator-releases-final-clues/ [M]. Solution involves his late-1986 Egypt trip and the fall of the Berlin Wall (1989); BERLINCLOCK = World Clock Berlin (not Mengenlehreuhr); theme "delivering a message"; advises "creativity"; "Who says it is even a math solution?"; K5 released when K4 solved, in a "public space", 97 characters, incorporates elements of the other puzzles, and K4 and K5 "share some coded words in the same positions."
- WaPo 1 Nov 2025 (403, not read; title says auction includes K5 solution): https://www.washingtonpost.com/entertainment/art/2025/11/01/kryptos-code-jim-sanborn-k5-auction/
- "They did not solve K4 and they certainly did not find the key." "K4 has been discovered and it points in the direction of K5." (relayed via RR post.)
- Not found: any use of the terms "masking", "matrix" by Sanborn in 2025-26 sources I could reach. (Prior-knowledge 2020s hints not re-verified.)
- Wikipedia: Kobek says Sanborn at a March 2019 dinner "did not care" what method solvers used.

## 4. Paradigm (June 2026)
https://www.paradigm.xyz/writing/kryptos [H]; site https://www.paradigm.xyz/kryptos/ [H]; Wikipedia cites NYT 2026-06-12 and WIRED (Levy) 2026-06-12 (not read).
- Paradigm revealed as buyer June 2026. Verifier: plaintext -> SHA256 -> HMAC via Google Cloud KMS; secret key lives in KMS; Jim Gillogly's answer loaded on a device so Paradigm never saw it (note: wording says "Jim Gillogly's answer entered"; relayed by fetcher, treat carefully). $1 per submission. Page does NOT state normalization (case/spaces), length rules. Site shows K4 ciphertext 97-char grid, "Decrypt K4", "Show Hint" (text not retrieved), CTF of 10 Kryptos-style puzzles, $10,000 total, $1,000 first solver each.
- Archive images on Paradigm post: captions only (mini Kryptos item, proof-of-concept curved copper plate, Sanborn with Dan Robinson at studio). No charts.
- K5: 97-char ciphertext made same time as K4; "plan to release K5 in the future." Not yet released as of my search.
- Gap: verifier input format unknown; check the site's About/History pages and the CTF entry page.

## 5. Public K5 ciphertext
None found. (rumkin.com/reference/kryptos/k5/ has only description: 97 chars, riddle leading elsewhere, needs K4 first.) [M]

## 6. Original Weltzeituhr city list (pre-1997)
https://de.wikipedia.org/wiki/Weltzeituhr_(Alexanderplatz) [M]. Only: 1997 restoration (Oct-Dec 1997, ~350,000 DM, Hans-Joachim Kunsch) renamed Leningrad->St. Petersburg, Alma Ata->Almaty, Bratislava->Pressburg; added 20 cities (Jerusalem, Tel Aviv named; politically unwanted in GDR); some cities reassigned to other zones (Kiew example, no zones given); now 146 names + date-line entry (other sites say 148). Cited 1997 sources: Berliner Zeitung, taz, Maerkische Allgemeine. No full 1969 list found. Gap: need Berliner Zeitung/taz Nov-Dec 1997 articles, DDR postcards/photos (Bundesarchiv, Deutsche Fotothek), designer Erich John material.
Implication: BERLINCLOCK may be a plaintext reference to the 1969-era clock; the pre-1997 list is unknown online here.

## 7. Cryptanalysis claims since 2025
- No credible public method derivation. https://lkn-law.com/2026/09/06/kryptos/ states sources do not establish a verified reconstruction of the K4 encipherment. [M]
- https://github.com/keithadler/kryptos : constraint search with the 24 known letters; rules out K1-K3 running keys, Tut/Bible running keys, Hill, 5x5 square ciphers, double K1/K2 cipher, any cipher where letter maps to itself (pos 74 K->K, so not Enigma-like/self-exclusion). Open: two unknown alphabets, long keys, stacked layers. [L, self-reported]
- https://github.com/nitsuah/kryptos : all null, 2.6M candidates (masking/transposition). [L]
- https://solvekryptos.com/ and /verify [L, explicitly unofficial]: proposes Quagmire-III-like variant, keyword KRYPTOS, shift split into base r (from four "helper cards") + 1-bit gate; admits cards are "back-solved from plaintext", plaintext is its own guess ("THECOMPASSROSEISHEREXEASTNORTHEAST..."), 45 positions depend on unavailable worksheet values; 97/97 match is unvalidated. Treat as unvalidated hypothesis, plaintext guess shouldn't be trusted.
- https://gist.github.com/atoponce/1cd01f40786ab21af011f0d6257fba0c : "No, ChatGPT didn't solve Kryptos 4."
- No leaks found.

## Bottom line on concrete constraints
Hard: K4 plaintext is 97 chars; known strips match known positions; two separate enciphering systems for bottom text (Sanborn 1990); proof-of-concept plate uses plain shifted-alphabet Vigenere rows (A..-style tableau, normal alphabet); K4/K5 share coded words at same positions (K5 97 chars); Sanborn hints "maybe not a math solution", needs creativity; letter->itself allowed (74 K->K). No chart images, grid sizes or key material are public.
