"""Egyptian / US-crypto / CIA-founding texts as running keys (letters + word initials), fixed + unknown alphabet."""
import glob, re
from run_initials import test_stream, streams_from_text
if __name__ == "__main__":
    for f in sorted(glob.glob("data/texts2/*.txt")):
        t = open(f, errors="ignore").read()
        name = f.split("/")[-1]
        test_stream(f"{name}:letters", re.sub("[^A-Za-z]", "", t).upper())
        s = streams_from_text(t)["word_first"]
        if len(s) >= 30:
            test_stream(f"{name}:word_first", s)
