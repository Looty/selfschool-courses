---
id: l29
title: "The bottleneck: squeezing a sentence into one vector"
quiz: quiz-01.yaml
resources: []
sources: [5, 27, 43]
---
After this lesson you can describe the encoder-decoder design for translation, and the problem that made researchers invent attention.

## Translation as two networks

Machine translation is a clean test of sequence modelling: read a sentence in one language, write it in another. Before 2014 the standard neural design was an **encoder-decoder**. An encoder network (often an LSTM, lesson 12) reads the source sentence and produces a summary; a decoder network then writes the target sentence from that summary, one word at a time. [5][27]

## The result that made it famous

The design was shown at scale in "Sequence to Sequence Learning with Neural Networks" (Sutskever, Vinyals and Le, 2014): a multilayered LSTM encodes the input into a fixed-dimensional vector and a second deep LSTM decodes it. On WMT'14 English-to-French translation it reached a BLEU score of 34.8, against 33.3 for a phrase-based statistical baseline. A trick that helped a lot was reversing the order of the words in the source sentence (but not the target): the authors say this introduces many short-term dependencies between source and target, which eases optimisation. [43] It was a landmark, and it also made the weakness easy to see.

## The fixed-length vector

In that design the summary is a single vector of a fixed size, no matter how long the sentence is. The authors of the 2014 paper that introduced attention argued that compressing a whole source sentence into a fixed-length vector limits translation performance. [5] Think of being asked to translate a 60-word sentence after someone reads it to you once and then wipes your notes: you keep a vague gist, and detail from the beginning is the first to go.

There are two reasons the limit bites.

- A fixed-size vector holds the same amount of information for a 5-word and a 60-word sentence, so long inputs lose detail.
- The decoder has to use that one vector for every word it writes, though different output words depend on different parts of the input (the first French word may depend on the first English word, the last on the last).

## What would be better

The fix is to stop compressing. Keep a vector for **every** input word and let the decoder look back at whichever ones matter for the word it is writing right now. The next lesson shows how the 2014 paper did it.

:::key-takeaways
- Encoder-decoder translation compresses the source sentence into one fixed-length vector. [5]
- That fixed vector limits translation quality, especially for long sentences. [5]
- The remedy is to keep a vector per input word and look back selectively.
:::

:::glossary
- **Encoder**: the network that reads the input and produces a representation of it.
- **Decoder**: the network that writes the output from that representation.
- **Encoder-decoder**: the translation design built from those two parts.
- **Fixed-length vector**: a vector whose size does not change with the length of the input.
- **Bottleneck**: a narrow point everything must pass through, limiting what gets through.
- **Source / target language**: the language translated from / into.
:::
