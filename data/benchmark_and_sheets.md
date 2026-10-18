# Kryptos: buried benchmark + Sanborn coding sheets (web research, 2026-10-17)

## LEAD 1 - benchmark
Source: https://forums.geocaching.com/GC/index.php?/topic/328615-missing-benchmark-that-may-relate-to-the-kryptos-mystery/ (whole thread is on one page; started by skintigh 2014-12-23, last post 2015-10-26). Also rumkin.com/reference/kryptos/k2/ repeats it as hearsay. interred2.rssing.com not checked in detail (no benchmark text found by grep); Elonka site returns 403; no datasheet for the benchmark is in the online NGS DB.

Sanborn quotes (as relayed in thread, from a Kryptos-group dinner Q&A): "there is something buried adjacent to Kryptos. Jae and I went back to visit a couple of years ago, and they had removed it, but it is important." "The thing that was buried is a bronze USGS marker. It was half buried. It had little cross hairs on the top of it." (Sept 2015 notes of another attendee: "USGA marker... how he paced off the location of the coordinates"; Oct 2015 dinner: benchmark "had been up against the front of the new building (NE of the slabs)", he thought such things were permanent. Pointed spot ~ N38 57 7.5, W77 8 47.8 = 38.952104, -77.146586 (skintigh's guess, not exact); roughly 4th corner of rectangle Kryptos / K3 coords / unmarked "Triangle" slab; ~10 m from LOOMIS.)

Candidate marks (NGS):
- LOOMIS, PID HV4826: "LOOMIS PB AND PP 1930" (Public Buildings and Public Parks, not USGS; Bill93 guessed disk design circle, unknown). Good recovery 1956. NAD27 38 57 05.82000N 077 08 49.22200W. Recovery 1984 (CLN): "STATION BOWEN WAS ESTABLISHED TO REPLACE THIS STATION. THIS STATION WAS DESTROYED UPON COMPLETION OF POSITIONING OF STATION BOWEN." (found via NGS datasheet search, "Destroyed Marks"). Stamping text not given in thread.
- BOWEN, PID AJ3427: NGS disk (agency NGS/ex-C&GS, not USGS), stamped "BOWEN 1984", set in top of 32 cm round concrete monument flush with ground; underground mark also "BOWEN 1984" 1.1 m down. Ref marks "BOWEN NO 1 1984", "BOWEN NO 2 1984" ~50 ft away. Scaled-from-map position NAD83(1986) 38 57 18. N, 077 08 55. W (+/-6"), SPC VA N 2,143,870 / 3,617,130 m, Falls Church quad 1994. No elevation. Description: near east end of the administration building; 9.0 m SE of 18" pine, 17.7 m SSE of SE end of rock wall, 23.5 m S of south corner of building, 18.5 m ESE of parking-lot roll curb, 28.7 m E of fire hydrant. Computed (DaveD from NGS obs): 38-57-19.0546, 77-08-55.7080; Bill93 Google Earth fit 38 57 19.05 N 77 08 55.65 W. Described as "on property of US Dept of Transportation" (sic, CIA compound). Orphan/not in online DB. 2 CIA TANK marks ~0.5 km away.
- Neither matches the sculpture. K2 coords 38 57 06.5N 77 08 44W = (Bill93 NAD27->NAD83) 38 57 06.9 N, 077 08 42.9 W. LOOMIS (NAD27) is ~100 m (thread: ~127 m after datum shift) from them; BOWEN is ~ 0.35 km NW. I did not compute bearings myself. I found NO stamped text of the specific marker Sanborn saw; no source identifies it. Nothing in the sources says the stamping or coordinates are a key; the thread theories: coordinates paced off from marker (skintigh), coordinates a cipher index/ scaled map values (Bill93), USGS witness post, misremembered agency.
- Datasheet direct URLs (geodesy.noaa.gov) returned 404 for me.

## LEAD 2 - sheets
kryptools.com does not resolve; mirror https://www.kryptools.com.about.ag/Sheets/sheets.htm worked. Source: NYT 2010-11-21 http://www.nytimes.com/2010/11/21/us/21codecharts.html (not fetched); PDF k1k2.pdf (8x10 in, 110 dpi, created 2010-11-20). Saved in /Users/scottdunphy/PycharmProjects/K4/data/web/sheets/: K1FromPdf.jpg, K2FromPdf.jpg, k1k2.pdf, K4Clue.png, K3-sheet-partial.jpg, Panel4Grid.png (kryptostable2.pdf is an HTML 404 stub).

Format: handwritten on graph paper with taped pieces; 31 columns; each block = 3 rows PT / KEY / CT, Vigenere tableau. Block numbers in left margin: K1 blocks 1,2 (+ partial 3rd block with single column N / L / D); K2 blocks 3-8 (only 6 of 12 lines shown; last "LAYERTWO / IDBYROWS" line absent).

K1 (my reading of image; header over top: PALIMPCEST, misspelled with C):
1 PT BETWEENSUBTLESHADINGANDTHEABSEN
  KEY PALIMPSESTPALIMPSESTPALIMPSESTP
  CT EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIV  (arrow at left; tick under K, small mark under it)
2 PT CEOFLIGHTLIESTHENUANCEOFILLUSIO  (sheet writes ILLUSIO(N) with two L's)
  KEY ALIMPSESTPALIMPSESTPALIMPCESTPA  (key has a C where S expected, col 26)
  CT JYQTQUXQBQVYUVLLTREVJYQTMKYROMF  (the page notes ticks under K and Y; arrow/loop at left)
3 (partial) PT N, KEY L, CT D -> matches sculpture K1 ending ...RDMFD.
Page notes: arrows under 1 and 2, darker letters (S's in key row).
My derived finding (check): in KA alphabet (KRYPTOSABCDEFGHIJLMNQUVWXZ) L + key C = K, and Q + key S = K. So the sheet's CT K (identical to the sculpture's) came from PT L with mistyped key C; with the true key S it decrypts to Q = the "IQLUSION" misspelling. i.e. the sculpture error is traceable to a key slip (PALIMPCEST) on the sheet.

K2 (header ABSCISSA; key period 8: ABSCISSA; my reading, possible OCR slips):
3 PT ITWASTOTALLYINVISIBLEHOWSTHATPO / KEY ABSCISSAABSCISSAABSCISSAABSCISS / CT VFPJUDEEHZWETZYVGWHKKQETGFQJNCE
4 PT SSIBLE?THEYUSEDTHEEARTHSMAGNETI / KEY AABSCI?SSAABSCISSAABSCISSAABSCI / CT GGWHKK?DQMCPFQZDQMMIAGPFXHQRLGT
5 PT CFIELDXTHEINFORMATIONWASGATHERED / KEY SSAABSCISSAABSCISSAABSCISSAABSCI / CT IMVMZJANQLVKQEDAGDVFRPJUNGEUNAQZ (first column boxed/bracketed)
6 PT ANDTRANSMITTEDUNDERGROUNDTOANUN / KEY SSAABSCISSAABSCISSAABSCISSAABSC / CT GZLECGYUXUEENJTBJLBQCETBJDFHRRY
7 PT KNOWNLOCATIONXDOESLANGLEYKNOWAB / KEY ISSAABSCISSAABSCISSAABSCISSAABS / CT IZETKZEMVDUFKSJHKFWHKUWQLSZFTIH
8 PT OUTTHIS?THEYSHOULDITSBURIEDOUT / KEY CISSAAB?SCISSAABSCISSAABSCISSAA / CT HDDDUVH?DWKBFUFPWNTDFIYCUQZEREE
Notable: the "?" is carried through PT, key and CT rows (key row skips a letter there? key reads "AABSCI?SS" so "?" occupies a key slot - key advances). Sheet PT reads UNDERGROUND (sculpture has UNDERGRUUND). "BURIed" has lowercase "ed" (page note); mark under the 8 and stray mark above an I; some lowercase m in rows. Sheet is evidently a worksheet of the final text laid out 31/row.
Check needed: I did not verify the cell-by-cell CT against the sculpture K2 text.

K4 sheet (K4Clue.png, NYT PDF created 2010-11-17): K4 CT numbered 1-97 in rows (first row shows "? O B K R" at 1-4... with "?" as an unnumbered extra at far left), with N Y P / V T T written above the BERLIN positions 64-69 (NYPVTT above BERLIN letters); i.e. 5-position start shifted: row 1 "OBKR" 1-4, then UOXOG... at 5. Confirms 97 letters. Image shows the "?" separate from numbered positions.
K3 sheets: 8x42 grid (336 chars) from Nova video 2007-07-01 4:17, "SLOWLYDESPARATLY" first row; 14x24 transposition grid with END top right; Panel4Grid.png: K3+K4 in 14 lines x 31 chars with "Top #4" on sheet holder (differs slightly from final sculpture per kryptools).
Community analysis found: only the kryptools notes above; no further analysis located.
