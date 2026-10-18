D# K4 Attack Plan (drafted by Fable planning agent, 2026-10-17)

Execution order: E0 tests -> E1 routes∘periodic -> E3 null masks -> E4 running/transposed keys -> E5 clock keystreams -> E2 double transposition -> E6 redo "eliminated" + Chaocipher.

Model: C = S∘T or T∘S; S in {Vig, Beau, VarBeau} x alphabet pairs {AZ,KA}^2; key index = pos mod p.
Crib filter: per (perm, p, S, order) derive key letter per crib, prune residue conflicts; survivors -> key completion by qscore hill-climb.
Key facts: cribs 21 and 63 differ by 42 -> widths 7,14,21,42 align. p=27-29 and p>=53 give zero crib collisions in direct case.
Success: Tier A qscore >= -5.0 + dict coverage >= 70% + readable. Tier B qscore >= -5.5 or m>=8 survivors.
Note: planner called EAST a community inference; actually Sanborn released EAST (Aug 2020). Using all 24 cribs, with 20-letter fallback.

## Revision 2 (Fable, with research)
Scheidt: "not mathematical, simple, can be remembered"; "change the language base"; "I masked the English language". Bean: positional stats argue no transposition; keyed alphabets with small/numeric keys favored.
New top experiment: alphabet-pair diagnosis — for PT alphabet (AZ/KA, rotations, rev) x CT alphabet (lore/dictionary keyword-keyed, rotations, rev) x Vig/Beau/Var, flag crib keystreams that are: all < base b (5..24), periodic <=30, few distinct values, or match running key (K1-K3 PT/CT, autokey). Then numeric-key expansions (Gromark bases 5-12, lore digit strings, Berlin-clock lamp counts, Weltzeituhr UTC offsets).

## Phase 2 (Fable, after phase-1 negatives)
P1 crib-error tolerance t=1,2 across E1/E2/alphapairs/Gromark-single (FP ≈ C(24,t)·26^-(m-t)).
P2 text-dependent keys on word-keyed alphabets: PT-autokey L1-13 (checks (13-L)+(11-L)), CT-autokey L1-40 (24 checks), linear chaining rules.
P3 interrupted-key (keyword restarts at word boundaries / trigger) — derive crib key letters, DP partition into keyword prefixes.
P4 annealing over free alphabets, narrowly: periodic p1-30, autokey L1-13, top Gromark survivors; null calibration with shuffled CT.
P5 Weltzeituhr city-ring running key, Berlin Clock lamp sequences.
Stop: more transposition families, more Gromark bases, unscored dual-alphabet filters.
Rule: calibrate every filter on random keystreams; report empirical pass rate.

## Phase 3-5 (Fable)
3A keystream pattern mining: crib key fragments (13 + 11 letters) under every alphabet pair -> English/German-likeness (calibrated vs random), exact substring in Kryptos corpus at independent offsets, repeats/palindromes.
3B Carter's real book as running key (DONE by stego: 11/24 noise).
3C annealing over text-dependent keys with free alphabets (+null).
3D monoalphabetic mask + interrupted/autokey.
3E '?' as leading 98th char for autokey/chaining.
Phase 4 verification protocol (re-encrypt, readability, Paradigm verifier, hash before disclosure).
Phase 5 long shots: Chaocipher annealing, Hill 3x3 w/ null, 6x6 Polybius fractionation, full Gromark-survivor annealing.
