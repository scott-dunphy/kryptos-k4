# Prior public tests of cipher methods against Kryptos K4

Compiled 2026-10-17 from web search/fetch. Only what sources said is reported. "No public record found" means my searches did not find one; it is not proof that nobody tried.

## Context
- Late 2025 and 2026 news (Scientific American, AFP, RR Auction): journalists Kobek and Byrne recovered the K4 plaintext from Sanborn's archive scraps. Sanborn reportedly confirmed it. The plaintext and the method are unpublished. RR Auction says the method is not known; Kobek says it is not a cryptographic solve. Paradigm now vets submissions. The method is still unknown, so K4 is still unsolved cryptographically.
  - https://www.scientificamerican.com/article/a-solution-to-the-cias-kryptos-code-is-found-after-35-years
  - https://content.rrauction.com/kryptos-k4-discovered-not-solved-heres-what-actually-happened/

## Table
| Method | Tested by | Where | Verdict | Thoroughness |
|---|---|---|---|---|
| 1a. M-94 / Jefferson wheel | No public record found | Searches of "Kryptos K4 M-94" returned only device-history pages. Not mentioned in the Bean paper, the Patrick repos, Adler, kryptosbot or kryptosfan. | None | n/a |
| 1b. M-138-A strip cipher (published strips) | No public record found | Same as above. | None | n/a |
| 2. Hagelin M-209 / C-38 | "Colin Patrick" (hobbyist, with Claude), self-reported | https://github.com/zeyeteam-debug/kryptos-k4-eliminations section 18 (`hagelin.py`, `hagelin2.py`, `hagelin3.py`) | 0 hits against the 24 cribs, and 0 on the null control, in three restricted sub-spaces. Sub-spaces: any two wheels (2-SAT); pins fixed by letter sets (910,464 configurations); wheels 25+21+17 (214,200 configurations). The author says the full M-209 "cannot be decided from 24 cribs". | Simplified model, restricted. Not a full-key-space exclusion. No independent verification. Other Hagelin C-series machines: no record found. |
| 3. Ragbaby | No public record found | The only "ragbaby" hit was a CWU "Kryptos 5" puzzle page, which is unrelated to K4: https://www.cwu.edu/academics/math/kryptos-challenges/kryptos-5-challenges | None | n/a. Bean's one-to-one and "minor differences" findings and Patrick's "keyword alphabets restarting per W" test (section 9, <=6/24) are only loosely related. |
| 4. Turning (Fleissner) grille | Patrick repos, self-reported | https://github.com/zeyeteam-debug/kryptos-k4-eliminations sections 31, 32 and 36 (`fleissner.py`, `fl_exact7.c`); https://github.com/jcolinpatrick/kryptos (`scripts/grille/`); https://kryptosbot.com/ | Annealing: best 20/24, but the planted control also reached 20/24, so inconclusive. Exact DFS: about 42% of one of eight variants covered, 0 survivors, the rest open. The jcolinpatrick README lists "route, grille" as eliminated, "scoped to the assumptions actually tested". Grille combined with Vigenère/substitution: not reported separately. | Partial, not exhaustive. Self-reported. Transposition alone is excluded by the letter-count argument (kryptosbot, cited below), so grille+substitution is the live form. |
| 5. Disrupted / interrupted columnar (+ substitution) | Patrick (same repo) | zeyeteam repo section 31 A.2 and section 36 | Myszkowski widths 3-9, VIC-disrupted widths 5-9 (width 10 sampled), irregular columnar widths 2-8: covered, 0 keyed hits. Myszkowski >=10 and disrupted >=10 (exhaustive): open. Section 36: 18.6M "tradecraft" transpositions gave 0 keyed hits. Section 5: any-alphabet periodic key plus transposition with width <=12: 0. Plain columnar and double columnar: listed as eliminated in the jcolinpatrick README. | Moderate within its bounds. Self-reported. |
| 6. Nicodemus | No public record found | Searches returned nothing. It only appears in the CryptoPrograms solver list, which is not K4-specific. | None | n/a. Nicodemus is Vigenère plus columnar, so the "periodic key + transposition (<=12)" and "columnar" families above cover it only partly. |

## Bean, "Cryptodiagnosis of Kryptos K4" (HistoCrypt 2021)
Full text read: https://ecp.ep.liu.se/index.php/histocrypt/article/view/153 (PDF at /download/153/109). Code: https://github.com/RichardBean/k4testing.
- It does NOT test M-94, M-138, M-209, ragbaby, grille, disrupted columnar or Nicodemus.
- Eliminated: seriated Playfair, double Playfair and standard Playfair. The IC is 0.036 against about 0.048, there are 26 letters, there is a KK doublet, and CLOCK's K to K plus BERLIN force impossible digraph mappings. The Hill cipher is argued against (97 is prime).
- Main claim: Monte Carlo tests of the crib letters show "minor differences" (a one-in-5,520 chance, and a one-in-240 chance for mean 3.6). He concludes this "strongly suggest[s] one-to-one" substitution with NO transposition. This conflicts with items 4, 5 and 6 (all involve transposition).
- It favours Gromark or a variant (a Gillogly suggestion since 1999). A key-space search over bases and primer lengths was done. It is explicitly not a proof ("it is of course possible that a new encryption algorithm ... is in use").
- It notes that Gillogly and an NSA analyst (2007) suggested substitution plus transposition because of width-7 doublets.

## Other "ruled out" lists
- https://github.com/keithadler/kryptos (README): rules out running keys from K1-K3, the sculpture, Carter's book and the Bible; Hill; anything built on a 5x5 square (Playfair, Bifid, four-square); K1/K2 ciphers applied twice; ciphers that cannot map a letter to itself. Left open: "two unknown alphabets at once, long keys, stacked layers, or a hand method with no clean mathematical form". It has a family-by-key-length grid that is an image, which I could not read. SEARCH.md was not read.
- https://kryptosbot.com/ (Patrick and Claude): 597 eliminations, 721.7B configurations. Categories are Bespoke, Fractionation, Key Models, Multi Layer, Substitution, Transposition and others. Textbook periodic Vigenère-type ciphers on standard and KRYPTOS alphabets, rearrangements, and bounded two- and three-step combinations are reported as failing. Keyword-mixed alphabet variants are not fully closed. Its transposition page was not fetchable (404 on the browse link), but a search snippet said pure rearrangement is impossible because the ciphertext has 2 E's and the cribs need 3. I did not verify this directly.
- https://kryptosfan.wordpress.com/2014/01/01/no-transposition-in-k4/ was not read (title only). The kryptosfan Methods page has plans only (transposition fed to Playfair, Bifid and four-square) and no verdicts.
- https://github.com/jcolinpatrick/kryptos: a "What's been eliminated" section. Fractionation (Bifid, Trifid, ADFGVX, Playfair, four-square) and transposition (columnar, double columnar, AMSCO, Myszkowski, rail fence, route, grille) are listed as eliminated. Open: "non-English or generated keys, keyword-ordered or repeated rearrangements, and null letters." It claims no solution.
- Elonka Dunin's https://elonka.com/kryptos/ has no tried-lists. It points to groups.io and the Kryptos wiki.

## Not yet ruled out, per these lists
- Any stack with a transposition layer (Bean's argument is statistical, not a proof).
- Gromark and other running-key or primer-based ciphers (Bean's candidate). Patrick tested only LFSR and some numeric keys.
- Strip and wheel ciphers (M-94, M-138): no record found.
- Ragbaby and Nicodemus: no record found.
- Full M-209 and other Hagelin machines: only restricted sub-spaces tested.
- Grille: only partly covered (annealing inconclusive; one of eight variants about 42% covered exactly).
- Disrupted and Myszkowski columnar at widths >=10.
- Keyword-mixed alphabets, two unknown alphabets at once, long keys, and hand methods.

## Not checked (inaccessible or not reached)
groups.io archive, Reddit, ACA discussions, Schmeh posts (nothing found for these methods), Bauer's "Unsolved!", NSA K1-K3 documents, Gillogly statements (only via Bean), Dunin's wiki. The repo results are self-reported, partly AI-assisted, and not independently verified.
