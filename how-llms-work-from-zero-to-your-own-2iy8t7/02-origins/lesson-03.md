---
id: l07
title: "Shannon's guessing game: the first language models"
quiz: quiz-03.yaml
resources: []
sources: [31]
---
After this lesson you can explain how Claude Shannon approximated English with statistics, read his six samples, and see why that is the ancestor of every language model.

## Text as probability

Language models are older than the computers that could run them. In 1948 Claude Shannon, one of the four Dartmouth organisers (lesson 6), published "A Mathematical Theory of Communication" in the *Bell System Technical Journal*. A short section of it, "The series of approximations to English", shows what you get when you generate text from nothing but statistics about real text. [31]

## The ladder, with Shannon's own samples

Shannon assumed a 27-symbol alphabet: the 26 letters and a space. These are the samples he printed. [31]

1. **Zero-order** (symbols independent and equally likely): `XFOML RXKHRJFFJUJ ZLPWCFWKCYJ FFJEYVKCQSGHYD QPAAMKBZAACIBZLHJQD.`
2. **First-order** (independent, but with the letter frequencies of English): `OCRO HLI RGWR NMIELWIS EU LL NBNESEBY A TH EEI ALHENHTTPA OOBTTV A NAH BRL.`
3. **Second-order** (digram structure: each letter depends on the one before): `ON IE ANTSOUTINYS ARE T INCTORE ST BE S DEAMY ACHIN D ILONASIVE TUCOOWE AT TEASONARE FUSO TIZIN ANDY TOBE SEACE CTISBE.`
4. **Third-order** (trigram: each letter depends on the previous two): `IN NO IST LAT WHEY CRATICT FROURE BIRS GROCID PONDENOME OF DEMONSTURES OF THE REPTAGIN IS REGOACTIONA OF CRE.`
5. **First-order word approximation** (words chosen independently with their English frequencies): `REPRESENTING AND SPEEDILY IS AN GOOD APT OR COME CAN DIFFERENT NATURAL HERE HE THE A IN CAME THE TO OF TO EXPERT GRAY COME TO FURNISHES THE LINE MESSAGE HAD BE THESE.`
6. **Second-order word approximation** (the probability of each word depends on the word before): `THE HEAD AND IN FRONTAL ATTACK ON AN ENGLISH WRITER THAT THE CHARACTER OF THIS POINT IS THEREFORE ANOTHER METHOD FOR THE LETTERS THAT THE TIME OF WHO EVER TOLD THE PROBLEM FOR AN UNEXPECTED.`

Shannon points out that "the resemblance to ordinary English text increases quite noticeably at each of the above steps", and that the samples have reasonably good structure out to about twice the range used to build them: a sequence of four or more words from sample 6 "can easily be placed in sentences without unusual or strained constructions". His conclusion: a sufficiently complex stochastic process will give a satisfactory representation of a discrete source. [31]

## How he generated them, by hand

The first two samples used a book of random numbers and a table of letter frequencies. For the rest Shannon used a trick: open a book at a random page, pick a letter, record it; open another page, read until that letter appears and record the letter that follows it; turn to another page, find that second letter, record the one after it, and so on. [31] The book itself was the table of statistics. He adds that further approximations would be interesting but "the labor involved becomes enormous at the next stage". [31]

## Why this is the ancestor

Every rung conditions on a little more context than the last, and each is a model of *what comes next given what came before*. That is the definition of a language model. The rest of the course is the climb: in chapter 6 you build rung 3 yourself in a few lines of Python, and by chapter 8 the context is hundreds of characters, handled by attention instead of a table.

## A number worth remembering

Shannon also estimated that the redundancy of ordinary English, ignoring structure beyond about eight letters, is roughly 50%: when we write English, half of what we write is determined by the structure of the language and half is chosen freely. He found that figure by several methods, including deleting letters from text and asking someone to restore them. [31] Redundancy is exactly what a language model exploits: if half the text is predictable from context, a model can guess it.

:::key-takeaways
- Shannon built six approximations to English from statistics alone: random letters, letter frequencies, digrams, trigrams, and word-level frequencies and transitions. [31]
- Each step adds more context and looks more like English. [31]
- He generated them by hand by opening books at random pages; the next stage was too laborious. [31]
- English is about 50% redundant, which is what makes next-token prediction possible. [31]
:::

:::glossary
- **Alphabet (here)**: the 27 symbols: 26 letters and a space.
- **Zero-order / first-order / second-order / third-order approximation**: using no, single-letter, previous-letter, or previous-two-letter statistics.
- **Digram / trigram**: two / three letters in a row.
- **Word approximation**: the same idea with whole words as the units.
- **Stochastic process**: a process driven by probabilities.
- **Redundancy**: the share of a text that is determined by the structure of the language rather than chosen freely.
- **Entropy**: Shannon's measure of how much information, or surprise, a source carries per symbol.
- **Markov process**: a process where the next step depends only on a limited recent past; Shannon spelled it "Markoff".
:::
