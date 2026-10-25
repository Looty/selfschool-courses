"""Lab 2 (chapter 2): a tiny ELIZA-style chatbot. No libraries, no learning, just keyword rules.

Run:  python lab02-mini-eliza.py          (type 'quit' to stop)
Try:  "I am sad", "my mother hates me", "I need a holiday", then something it has no rule for.
"""
import random
import re

# Each rule: a pattern to find in the user's sentence, and reply templates that reuse the matched fragment.
RULES = [
    (r"\bi am (.*)", ["Why do you say you are {0}?", "How long have you been {0}?"]),
    (r"\bi need (.*)", ["Why do you need {0}?", "Would getting {0} really help you?"]),
    (r"\bmy (mother|father|sister|brother)\b(.*)", ["Tell me more about your {0}.", "How do you feel about your {0}?"]),
    (r"\bbecause (.*)", ["Is that the real reason?", "What else could explain {0}?"]),
]
FALLBACKS = ["Please go on.", "I see.", "Can you say more about that?"]

# ELIZA also flipped pronouns so the echo reads naturally: "my job" becomes "your job".
SWAP = {"my": "your", "i": "you", "me": "you", "am": "are", "your": "my", "you": "I"}


def reflect(text: str) -> str:
    return " ".join(SWAP.get(w, w) for w in text.split())


def reply(sentence: str) -> str:
    s = sentence.lower().strip(" .!?")
    for pattern, templates in RULES:
        m = re.search(pattern, s)
        if m:
            fragments = [reflect(g.strip()) for g in m.groups()]
            return random.choice(templates).format(*fragments)
    return random.choice(FALLBACKS)


if __name__ == "__main__":
    print("Hello. What is on your mind?")
    while True:
        line = input("> ")
        if line.strip().lower() in {"quit", "exit"}:
            break
        print(reply(line))
