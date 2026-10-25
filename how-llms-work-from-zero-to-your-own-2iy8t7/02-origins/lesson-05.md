---
id: l09
title: "Lab 2: build a mini ELIZA"
quiz: quiz-05.yaml
resources: [../resources/lab02-mini-eliza.py]
sources: [22]
---
After this lab you will have run a keyword-rule chatbot, changed its rules, and found where it breaks.

## Shortcut: the ready-made script

Download `lab02-mini-eliza.py` from this lesson's Resources. It uses only Python's standard library, so there is nothing to install:

```bash
python lab02-mini-eliza.py
```

Type sentences; type `quit` to stop. It was run while writing this course.

## What the script does

It has the same parts ELIZA had. [22]

1. **Keyword rules.** A list of patterns, each with several reply templates: `I am ...`, `I need ...`, `my mother/father/...`, `because ...`.
2. **Decomposition.** A regular expression finds the pattern and captures the fragment after it (for "I am sad", the fragment is "sad").
3. **Reflection.** A small table swaps pronouns ("my" becomes "your", "I" becomes "you") so the echo reads naturally.
4. **Reassembly.** The captured fragment is dropped into a template.
5. **Fallback.** With no matching rule, it says something noncommittal like "Please go on."

In a test run, "I am sad" gave "Why do you say you are sad?", "my mother hates me" gave "Tell me more about your mother.", "I need a holiday" gave "Would getting a holiday really help you?", and a sentence with no matching rule ("what is the weather") got the fallback "Can you say more about that?".

## Try this

- Add a rule for `i feel (.*)` with two templates.
- Type "I am happy that I am sad". What does it echo, and does the result make sense?
- Type a sentence that is clearly a question about facts ("who wrote Hamlet"). The program cannot answer. That gap is the one language models were built to close.

## Check yourself

- How many rules would you need to cover ordinary conversation? Why does that approach not scale?
- Which of the five parts above would a language model replace?

:::key-takeaways
- A keyword-and-template chatbot needs no learning, only rules. [22]
- It fails outside its rules, and writing more rules does not scale.
:::

:::glossary
- **Regular expression (regex)**: a compact pattern language for finding text.
- **Capture group**: the part of a match you keep, such as the words after "I am".
- **Template**: a reply with blanks to fill.
- **Reflection (pronoun swap)**: changing "my" to "your" and so on so an echoed phrase reads correctly.
- **Fallback**: the default reply when no rule matches.
- **Standard library**: the libraries that come with Python, needing no installation.
:::
