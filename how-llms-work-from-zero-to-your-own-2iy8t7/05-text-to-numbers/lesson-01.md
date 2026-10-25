---
id: l20
title: "Tokens: why not just words?"
quiz: quiz-01.yaml
resources: []
sources: [6, 21, 30]
---
After this lesson you can explain why models use tokens instead of words or characters, and what a vocabulary is.

## Three choices

A model works on numbers, so text must be cut into pieces and each piece given an integer. There are three obvious ways to cut.

| Unit | Example for "unhappiness" | Problem |
| --- | --- | --- |
| Whole words | `unhappiness` | New words, names, typos and rare forms are not in the list |
| Single characters | `u n h a p p i n e s s` | Sequences become very long, and a character alone carries little meaning |
| **Subwords** | `un` `happi` `ness` | A middle path |

**Words** need a fixed vocabulary, and any word outside it is unknown. The subword paper calls translation an "open-vocabulary problem" and argues many word classes, such as names, compounds and loanwords, can be handled by smaller units. [6] **Characters** never fail on a new word, but every sentence turns into many steps, and the model's context window (lesson 2) fills quickly.

## Subwords in practice

Modern LLMs use subword tokens, usually learned with a compression-style method called byte-pair encoding (next lesson). [21][6] Common words become a single token; rare words split into a few pieces; anything unknown can still be spelled out from smaller pieces.

You saw this in lab 1: GPT-2's tokenizer turned "The capital of France is" into five tokens, `The`, `Ġcapital`, `Ġof`, `ĠFrance`, `Ġis`, where `Ġ` marks a leading space. The same word with and without a space before it is a different token.

## What this explains about LLMs

- A model's **context window** is counted in tokens, not words, so "how much fits" depends on the tokenizer. [21]
- Prices and speed limits for hosted models are usually counted in tokens.
- Tokenization can cause odd behaviour: a model that sees `ĠFrance` as one unit does not "see" its letters, which is one reason models can stumble on tasks like counting letters in a word. (Reasonable consequence of the design, but not a claim from the sources.)
- The default of `generate()` is measured in new *tokens* (lesson 4). [30]

:::key-takeaways
- Models work on integer tokens; text is cut into words, characters or subwords.
- Subwords avoid the unknown-word problem of whole words and the length of characters. [6]
- Context windows and costs are counted in tokens. [21]
:::

:::glossary
- **Token**: one piece of text (word, subword or character) turned into an integer.
- **Vocabulary**: the fixed list of all tokens a model knows.
- **Subword**: a piece smaller than a word, such as a prefix, a suffix or a common stem.
- **Open-vocabulary problem**: the fact that new words keep appearing, so a fixed word list will always miss some.
- **Out-of-vocabulary**: not in the model's word list.
- **Tokenizer**: the code that cuts text into tokens and back.
- **Loanword / compound**: a word borrowed from another language / one made of two words joined.
:::
