"""Running keys from memorized/famous texts, letters and word-initials, fixed alphabets + single unknown alphabet."""
import glob, re
from run_initials import test_stream, streams_from_text

EXTRA = {
    "pledge1954": "I pledge allegiance to the flag of the United States of America and to the republic for which it stands one nation under God indivisible with liberty and justice for all",
    "marks_poem": "The life that I have is all that I have and the life that I have is yours The love that I have of the life that I have is yours and yours and yours A sleep I shall have a rest I shall have yet death will be but a pause For the peace of my years in the long green grass will be yours and yours and yours",
    "ciamotto": "And ye shall know the truth and the truth shall make you free",
}
if __name__ == "__main__":
    texts = dict(EXTRA)
    for f in glob.glob("data/memtexts/*.txt"):
        t = open(f, errors="ignore").read()
        if "Wikimedia Error" in t:
            continue
        texts[f.split("/")[-1]] = t
    for name, t in texts.items():
        letters = re.sub("[^A-Za-z]", "", t).upper()
        test_stream(f"{name}:letters", letters)
        for sname, s in streams_from_text(t).items():
            if sname == "word_first" and len(s) >= 30:
                test_stream(f"{name}:{sname}", s)
