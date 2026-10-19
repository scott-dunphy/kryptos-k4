"""Build letter 4-gram models (interpolated, conditional log10 P(d|abc)) for Latin, Old English, German, Middle
Egyptian (TLA transliteration flattened to A-Z) and an English baseline built the same way (Moby Dick).
Output: data/lang/qg_<lang>.npy (26^4 float32) and data/lang/<lang>_letters.txt."""
import os, re, unicodedata, glob
import numpy as np

D = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(D, "raw")


def strip_acc(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def letters(s):
    return re.sub(r"[^A-Z]", "", strip_acc(s).upper())


def html_text(p):
    t = open(p, encoding="utf-8", errors="ignore").read()
    t = re.sub(r"(?s)<head.*?</head>|<script.*?</script>|<p class=\"internal_navigation\">.*?</p>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"&[a-z]+;|&#\d+;", " ", t)
    t = re.sub(r"(?i)the latin library|the classics page|christian latin", " ", t)
    return t


def gut(p, a=None, b=None):
    t = open(p, encoding="utf-8", errors="ignore").read()
    s = t.find("*** START"); e = t.find("*** END")
    t = t[s:e]
    if a:
        t = t[t.find(a):]
    if b and b in t:
        t = t[:t.find(b)]
    return t


def corpus(lang):
    if lang == "la":
        return letters(" ".join(html_text(p) for p in sorted(glob.glob(os.path.join(R, "la_*.html")))))
    if lang == "ang":
        lines = open(os.path.join(R, "ang_beowulf.txt"), encoding="utf-8", errors="ignore").read().split("\n")[:3844]
        t = "\n".join(l for l in lines if re.search(r"\S\s{4,}\S", l))   # verse lines (two half-lines)
        t = t.replace("þ", "th").replace("Þ", "Th").replace("ð", "th").replace("Ð", "Th").replace("æ", "ae").replace("Æ", "Ae").replace("ƿ", "w")
        t = re.sub(r"\[.*?\]|\d+", " ", t)
        return letters(t)
    if lang == "de":
        t = gut(os.path.join(R, "de_faust.txt"))
        for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("Ä", "Ae"), ("Ö", "Oe"), ("Ü", "Ue"), ("ß", "ss")):
            t = t.replace(a, b)
        return letters(t)
    if lang == "egy":
        t = open(os.path.join(R, "egy_tla_translit.txt"), encoding="utf-8").read()
        t = re.sub(r"\.(PL|DU|SG|t?)\b", lambda m: "t" if m.group(1) == "t" else "", t)
        for a, b in (("ꜣ", "a"), ("ꜥ", "a"), ("ꞽ", "i"), ("i̯", "i"), ("ḥ", "h"), ("ḫ", "kh"), ("ẖ", "kh"), ("š", "sh"),
                     ("ṯ", "tj"), ("ḏ", "dj"), ("ʾ", ""), ("u̯", "u")):
            t = t.replace(a, b)
        return letters(t)
    if lang == "en":
        return letters(open(os.path.join(D, "..", "mobydick.txt"), encoding="utf-8", errors="ignore").read())


def build(s):
    a = np.array([ord(c) - 65 for c in s], dtype=np.int64)
    c1 = np.bincount(a, minlength=26).astype(float) + 0.5
    c2 = np.bincount(a[:-1] * 26 + a[1:], minlength=26 ** 2).astype(float).reshape(26, 26)
    c3 = np.bincount((a[:-2] * 26 + a[1:-1]) * 26 + a[2:], minlength=26 ** 3).astype(float).reshape(26, 26, 26)
    c4 = np.bincount(((a[:-3] * 26 + a[1:-2]) * 26 + a[2:-1]) * 26 + a[3:], minlength=26 ** 4).astype(float).reshape(26, 26, 26, 26)
    p1 = c1 / c1.sum()
    p2 = c2 / np.maximum(c2.sum(1, keepdims=True), 1)
    p3 = c3 / np.maximum(c3.sum(2, keepdims=True), 1)
    p4 = c4 / np.maximum(c4.sum(3, keepdims=True), 1)
    P = (0.55 * p4 + 0.25 * p3[None] + 0.12 * p2[None, None] + 0.08 * p1[None, None, None])
    return np.log10(P).astype(np.float32).reshape(-1)


if __name__ == "__main__":
    for lang in ("la", "ang", "de", "egy", "en"):
        s = corpus(lang)
        open(os.path.join(D, f"{lang}_letters.txt"), "w").write(s)
        np.save(os.path.join(D, f"qg_{lang}.npy"), build(s))
        print(lang, len(s), s[:80])
