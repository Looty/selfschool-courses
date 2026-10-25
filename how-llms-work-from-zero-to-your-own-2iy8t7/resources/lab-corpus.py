"""Gets the practice text used by labs 6 to 13 and saves it as input.txt in the current folder.

Run:  python lab-corpus.py
It downloads about 1 MB of Shakespeare (public-domain plays, the same text the nanoGPT README uses).
If the download fails it writes a small synthetic text instead, so every lab still runs offline.
"""
import random
import urllib.request

URL = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"

try:
    text = urllib.request.urlopen(URL, timeout=20).read().decode("utf-8")
    source = "tiny Shakespeare (downloaded)"
except Exception as e:  # no network, blocked, moved
    print("download failed:", e)
    random.seed(0)
    subjects = ["the king", "a stranger", "my lord", "the queen", "an old man"]
    verbs = ["speaks of", "dreams of", "fears", "loves", "forgets"]
    objects = ["the sea", "his crown", "the night", "a distant war", "the morning"]
    text = "\n".join(f"{random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)}." for _ in range(20000))
    source = "synthetic fallback (repetitive: models learn it very quickly)"

with open("input.txt", "w", encoding="utf-8") as f:
    f.write(text)
print(f"wrote input.txt: {len(text):,} characters, {len(set(text))} distinct characters; source: {source}")
