---
id: l21
title: Byte-pair encoding
quiz: quiz-02.yaml
resources: []
sources: [6, 21, 42, 60, 73]
---
After this lesson you can explain how byte-pair encoding builds a vocabulary by repeatedly merging the most frequent pair.

## An idea borrowed from compression

Byte-pair encoding (BPE) started as a compression technique. The subword paper evaluates several segmentation methods for translation, including character n-gram models and BPE, "a compression-based segmentation technique", and found that subword models beat a back-off dictionary baseline by 1.1 BLEU for English-German and 1.3 BLEU for English-Russian on WMT 15. [6] The same idea became the usual way to build the token vocabulary of language models. [21]

## The algorithm

1. Start with the text as individual characters. The vocabulary is just those characters.
2. Count every pair of adjacent tokens.
3. Take the most frequent pair and merge it into one new token. Add that token to the vocabulary and remember the rule.
4. Replace every occurrence of the pair in the text with the new token.
5. Repeat from step 2 until you have the vocabulary size you want.

Frequent pieces get merged early and so become single tokens; rare sequences stay split into smaller pieces.

## A worked example

Take the text `low lower lowest newer newest`. The pair `l` + `o` occurs in `low`, `lower` and `lowest`, so it is merged into `lo`. Next ` lo` (space, then `lo`) may be merged, then `we` + `r` into `wer`, and so on. In the lab you will watch this happen on a small sentence: starting at 62 single-character tokens, ten merges bring it to 25.

## Using the rules on new text

To tokenize new text, apply the recorded merges in the order they were learned. A word the tokenizer has never seen, such as "slowly", does not fail: it gets split into whatever known pieces fit, down to single characters if needed. This is how BPE copes with the open-vocabulary problem from lesson 20. [6]

## A second worked example, with word counts

The Hugging Face LLM course uses a tiny word list with counts: *hug* (10 times), *pug* (5), *pun* (12), *bun* (4) and *hugs* (5). The starting vocabulary is the characters `b, g, h, n, p, s, u`. The pair `u`+`g` appears 20 times (in hug, pug and hugs), the most of any pair, so the first merge is `ug`. Next `u`+`n` appears 16 times, giving `un`; then `h`+`ug` appears 15 times, giving `hug`. To tokenize a new word you split it into characters and apply the merges in the order they were learned: `bug` becomes `[b, ug]`, while `mug` becomes `[<unk>, ug]` because `m` was never in the starting alphabet. [73]

## Byte-level BPE: no unknown characters

That last example shows a weakness: any character absent from training becomes an unknown token. GPT-2 solved it by running BPE on **bytes** instead of Unicode characters. A byte-level base vocabulary needs only 256 entries and can represent any text. The GPT-2 paper notes that running BPE over Unicode code points would require a base vocabulary of over 130,000 before any merges, which is "prohibitively large" next to the 32,000 to 64,000 token vocabularies usually used. [42] It also notes that applying BPE directly to bytes gives sub-optimal merges, because BPE is a greedy frequency-based heuristic: it spent vocabulary slots on many versions of common words such as "dog", "dog.", "dog!" and "dog?". To avoid that, the authors prevent BPE from merging across character categories (letters with punctuation, say), with an exception for spaces that improves compression while adding only minimal fragmentation of words. [42] The result was a vocabulary of 50,257 tokens. [42]

SentencePiece, a 2018 tokenizer library, takes another step: it trains subword models directly from raw sentences, with no separate "split into words" stage, which makes it language-independent. [60]

## One simplification in the lab

Real tokenizers usually first split text into words or punctuation groups and merge only *within* those chunks. The lab's tokenizer merges across spaces too (you will see a merge such as `w` + ` lo`), which real tokenizers avoid. The method, count pairs and merge the most frequent, is the same.

:::key-takeaways
- BPE builds a vocabulary by repeatedly merging the most frequent adjacent pair of tokens.
- Frequent strings become single tokens; rare ones stay in smaller pieces. [6]
- New text is tokenized by replaying the merges in order; unseen words fall back to smaller pieces. [6]
:::

:::glossary
- **BPE (byte-pair encoding)**: a method that builds a token vocabulary by merging the most frequent adjacent pair, again and again.
- **Merge rule**: one recorded step, such as "join `l` and `o` into `lo`".
- **Vocabulary size**: how many distinct tokens the tokenizer has; a design choice.
- **BLEU**: a score comparing machine translations with human ones; higher is better.
- **Back-off dictionary**: a lookup table used when a rare word cannot be translated normally.
- **Segmentation**: cutting text into pieces.
:::
