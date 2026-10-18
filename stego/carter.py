"""S10: Carter's 'The Tomb of Tut.ankh.Amen' (1923 vol 1 = K3 source; vol 2) as running key (E4 gap).
2025 open letter: Sanborn's 1986 Egypt trip figures in the solution. OCR from archive.org; letters only."""
import re, sys
from common import *
from run_e4 import scan

def letters(path):
    t = open(path, errors="ignore").read()
    t = re.sub(r"[¬-]\s*\n\s*", "", t)
    return re.sub("[^A-Z]", "", t.upper())

if __name__ == "__main__":
    res = []
    for f in sys.argv[1:]:
        s = letters(f)
        i = s.find("WIDENINGTHEHOLEALITTLE"); print(f, len(s), "K3 source found at", i)
        for tag, s2 in (("", s), ("~rev", s[::-1])):
            for kname, kal in (("AZ", AZ), ("KA", KA)):
                S = np.array([kal.index(c) for c in s2], dtype=np.int64)
                for v in range(cf.NV):
                    best = np.zeros(len(S) - 97, dtype=np.int64)
                    scan(S, REQ[v], cf.CRIB_I, best)
                    o = int(best.argmax())
                    res.append((int(best.max()), f.split("/")[-1] + tag, kname, cf.VARIANTS[v][:3], o, s2[o:o+97][:30]))
    res.sort(key=lambda x: -x[0])
    for r in res[:10]: print(r)
