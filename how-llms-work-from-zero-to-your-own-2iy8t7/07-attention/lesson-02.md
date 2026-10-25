---
id: l30
title: "Attention: learning where to look (2014)"
quiz: quiz-02.yaml
resources: []
sources: [5, 1]
---
After this lesson you can describe in plain words what attention does, and why it improved translation.

## The idea

The 2014 paper "Neural Machine Translation by Jointly Learning to Align and Translate" proposed letting the model "automatically (soft-)search for parts of a source sentence" that are relevant to predicting each target word, without cutting the source into hard units. [5] That mechanism is **attention**.

Concretely, in the paper's design, the encoder is a bidirectional RNN (one reading the sentence forwards and one backwards, 1000 hidden units each), so every source word gets an "annotation" vector that summarises the words around it, not a single summary for the whole sentence. When the decoder is about to write a target word, an **alignment model** scores each annotation for how relevant it is right now, the scores become weights that add up to 1, and the decoder takes the weighted sum of the annotations. That sum is a summary built fresh for this one output word. The alignment model is itself a small feed-forward network, trained jointly with everything else. [5]

Crucially, the paper stresses that, unlike in traditional machine translation, the alignment is not treated as a hidden variable to be inferred. The model directly computes a **soft alignment**, which allows the gradient of the cost to be backpropagated through it, so the alignment model and the translation model are trained together. [5]

"Soft" means the model does not pick one source word. It spreads its attention: maybe 70% on one word, 20% on another and the rest on the others. Because the weights are smooth numbers, the whole thing can be trained with gradient descent.

## What it bought

On English-to-French translation, the authors report results comparable to the existing state-of-the-art phrase-based system. They also report that a qualitative look at the learned "soft alignments" agrees well with human intuition: when writing a French word, the model attends to the English words a person would have matched with it. [5] Alignment, which words correspond to which, had been a separate engineering task; here it is learned as a by-product.

## An analogy

Translating a long sentence the old way is reading it once and writing from memory. With attention you can keep the source text in front of you and glance at the relevant bit before writing each word. The glance is cheap, and what you attend to changes at every word.

## Where this leads

Notice the cost: the decoder's glance goes back to the encoder's vectors, which were still produced by an LSTM that reads one word at a time. In 2017 the Transformer authors asked whether you need the LSTM at all if attention does the heavy lifting; their answer, "Attention Is All You Need", is chapter 8. [1]

:::low-confidence
About a third of the paper was read (the model description and the training setup); its exact equations and the full results tables were not. The paper trained its models for about five days each and used beam search to find translations, and compared the new "RNNsearch" with a plain encoder-decoder "RNNencdec" on sentences up to 30 and 50 words. [5]
:::

:::key-takeaways
- Attention lets the decoder softly search the source for the parts relevant to each output word. [5]
- It reached results comparable to the state-of-the-art phrase-based system, and its learned alignments looked sensible to humans. [5]
- "Soft" means weights spread across inputs and everything stays trainable by gradient descent.
:::

:::glossary
- **Attention**: a mechanism that scores the inputs for relevance and uses the scores to take a weighted mix of them.
- **Alignment**: which source words correspond to which target words.
- **Soft vs hard**: spreading weight across several choices vs picking exactly one.
- **Weighted average**: a mix where each part counts according to its weight.
- **Phrase-based system**: the earlier, non-neural statistical translation approach.
- **Qualitative analysis**: judging by examining examples rather than by a score.
:::
