"""Alternative alphabet families a 1990 hand cipherer might use, tested against cribs.

Families: columnar-transposed keyword alphabets (plain + keyed column order), Morse-ordered, ITA2/Baudot order,
QWERTY/QWERTZ, frequency order, decimations of AZ/KA, first-appearance alphabets from Kryptos texts,
keyword variants (rest reversed / rest continuing after last keyword letter).
Tests (direct): periodic key p<=22 consistency (run_alphapairs.diag), single-alphabet chain keys skipped;
plus autokey (run_p2.scan). Paired with themselves, AZ, KA, and lore/dict keyed alphabets.
"""
import numpy as np
from k4lib import AZ, KA, keyed_alphabet
import kryptos_texts as kt
from run_alphapairs import load_words, pos_table, diag, PL, CL, CI


def dedupe(s):
    out = []
    for c in s:
        if c.isalpha() and c.upper() not in out:
            out.append(c.upper())
    return "".join(out)


def complete(s, base=AZ):
    return dedupe(s + base)


def columnar_alpha(key, ordered):
    """Write keyed sequence (key + rest) in rows of len(dedupe(key)); read columns (in key order if ordered)."""
    k = dedupe(key)
    seq = complete(k)
    W = len(k)
    cols = list(range(W))
    if ordered:
        cols = sorted(cols, key=lambda i: k[i])
    return "".join(seq[r * W + c] for c in cols for r in range((len(seq) + W - 1) // W) if r * W + c < len(seq))


def families(words):
    fam = {}
    morse = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....",
             "I": "..", "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.",
             "Q": "--.-", "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
             "Y": "-.--", "Z": "--.."}
    fam["morse_len"] = "".join(sorted(AZ, key=lambda c: (len(morse[c]), morse[c])))
    fam["morse_tree"] = "ETIANMSURWDKGOHVFLPJBXCYZQ"
    fam["morse_dotdash"] = "".join(sorted(AZ, key=lambda c: morse[c].replace(".", "0").replace("-", "1")))
    fam["ita2"] = "ETAOINSHRDLUCMFWYPVBGKJQXZ"  # placeholder overwritten below
    # ITA2 code values (letters shift), order by 5-bit code
    ita2 = {"E": 1, "A": 3, "S": 5, "I": 6, "U": 7, "D": 9, "R": 10, "J": 11, "N": 12, "F": 13, "C": 14, "K": 15,
            "T": 16, "Z": 17, "L": 18, "W": 19, "H": 20, "Y": 21, "P": 22, "Q": 23, "O": 24, "B": 25, "G": 26,
            "M": 28, "X": 29, "V": 30}
    fam["ita2"] = "".join(sorted(AZ, key=lambda c: ita2[c]))
    fam["qwerty"] = "QWERTYUIOPASDFGHJKLZXCVBNM"
    fam["qwertz"] = "QWERTZUIOPASDFGHJKLYXCVBNM"
    fam["qwerty_col"] = "QAZWSXEDCRFVTGBYHNUJMIKOLP"
    fam["etaoin"] = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
    fam["etaoin2"] = "ETAONRISHDLFCMUGYPWBVKXJQZ"
    for d in (3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        fam[f"AZdec{d}"] = "".join(AZ[(i * d) % 26] for i in range(26))
        fam[f"KAdec{d}"] = "".join(KA[(i * d) % 26] for i in range(26))
    texts = {"K1PT": kt.K1_PT, "K2PT": kt.K2_PT, "K3PT": kt.K3_PT, "K1CT": kt.K1_CT, "K2CT": kt.K2_CT,
             "MORSE": kt.MORSE, "BERLINCLOCK": "BERLINCLOCK", "EASTNORTHEAST": "EASTNORTHEAST",
             "EASTNORTHEASTBERLINCLOCK": "EASTNORTHEASTBERLINCLOCK", "K4CT": "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"}
    for n, t in texts.items():
        fam[f"first_{n}"] = complete(t)
        fam[f"firstKA_{n}"] = complete(t, KA)
        fam[f"last_{n}"] = complete(t[::-1])
    for w in words:
        k = dedupe(w)
        rest = [c for c in AZ if c not in k]
        fam[f"col_{w}"] = columnar_alpha(w, False)
        fam[f"colord_{w}"] = columnar_alpha(w, True)
        fam[f"restrev_{w}"] = k + "".join(rest[::-1])
        last = k[-1]
        after = [c for c in AZ[AZ.index(last) + 1:] + AZ[:AZ.index(last)] if c not in k]
        fam[f"after_{w}"] = k + "".join(after)
    return fam


if __name__ == "__main__":
    lore, dictw = load_words()
    lore_ext = sorted(set(lore + ["KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "BERLINCLOCK",
                                   "SHADOW", "LUCID", "MEMORY", "LAYERTWO", "EQUAL", "SANBORN", "SCHEIDT"]))
    fam = families(lore_ext)
    # add reversed versions
    for n, a in list(fam.items()):
        assert sorted(a) == list(AZ), (n, a)
        fam[n + "~rev"] = a[::-1]
    names = list(fam)
    print("alt alphabets", len(names))
    A = np.array([pos_table(fam[n]) for n in names])
    # partner set: alt alphabets + AZ + KA + lore keyed + dict keyed (columnar-transposed dict too)
    partners = {"AZ": AZ, "KA": KA, "AZ~rev": AZ[::-1], "KA~rev": KA[::-1]}
    partners.update(fam)
    for w in lore_ext:
        partners["kw_" + w] = keyed_alphabet(w)
    pn = list(partners)
    B = np.array([pos_table(partners[n]) for n in pn])
    out = np.zeros((2_000_000, 6), dtype=np.int64)
    rules = ["vig", "beau", "var"]
    for lab, X, Y, NX, NY in (("PT=alt", A, B, names, pn), ("CT=alt", B, A, pn, names)):
        n = diag(X, Y, PL, CL, CI, out)
        r = out[:n]
        strong = r[(r[:, 3] <= 12) | ((r[:, 5] > 0) & (r[:, 5] <= 22)) | (r[:, 4] <= 6)]
        print(lab, "pairs", X.shape[0] * Y.shape[0] * 3, "flagged", n, "strong", len(strong),
              "min range", int(r[:, 3].min()) if n else None)
        for x in strong[:15]:
            print("   PT", NX[x[0]], "CT", NY[x[1]], rules[x[2]], "range", x[3], "distinct", x[4], "period", x[5])
    # columnar-transposed alphabets for ALL dictionary words vs AZ/KA/alt (both roles)
    dictcol = {}
    for w in dictw:
        a = columnar_alpha(w, True)
        dictcol.setdefault(a, w)
    D = np.array([pos_table(a) for a in dictcol]); DN = list(dictcol.values())
    C2 = np.array([pos_table(a) for a in [AZ, KA, AZ[::-1], KA[::-1]]]); C2N = ["AZ", "KA", "AZ~rev", "KA~rev"]
    for lab, X, Y, NX, NY in (("PT=dictcol", D, C2, DN, C2N), ("CT=dictcol", C2, D, C2N, DN),
                              ("PT=dictcol,CT=dictcol-self", None, None, None, None)):
        if X is None:
            continue
        n = diag(X, Y, PL, CL, CI, out)
        r = out[:n]
        strong = r[(r[:, 3] <= 12) | ((r[:, 5] > 0) & (r[:, 5] <= 22)) | (r[:, 4] <= 6)]
        print(lab, "pairs", X.shape[0] * Y.shape[0] * 3, "flagged", n, "strong", len(strong),
              "min range", int(r[:, 3].min()) if n else None)
        for x in strong[:15]:
            print("   PT", NX[x[0]], "CT", NY[x[1]], rules[x[2]], "range", x[3], "distinct", x[4], "period", x[5])
