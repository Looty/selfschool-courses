---
id: l61
title: "Pretrain, then fine-tune: ELMo and ULMFiT (2018)"
quiz: quiz-05.yaml
resources: []
sources: [68, 69, 9, 41, 3]
---
After this lesson you can explain transfer learning for language, and name the three 2018 results that made "pretrain on text, then adapt" the standard recipe.

## The recipe before 2018

Word vectors (lessons 14 and 23) were already pretrained on big text and reused. But everything above the vectors, the network that actually did the task, was built from scratch for each task, with labelled data. Labels are expensive; raw text is free. The question of 2018 was how much more of the network could be pretrained.

## ELMo: vectors that depend on the sentence

A word vector from word2vec is the same for "bank" in "river bank" and "bank account". ELMo ("Deep contextualized word representations", Peters et al., February 2018) derives word representations from the internal states of a deep **bidirectional language model** pretrained on a large corpus. Each word gets a vector that depends on its whole sentence, so it can capture both syntax and semantics and how a word's meaning changes with context (polysemy). The representations can be added to existing models and significantly improved the state of the art on six NLP tasks, including question answering, textual entailment and sentiment analysis. The authors stress that using the network's deep internal layers, not only the top one, is crucial. [69]

## ULMFiT: fine-tune the whole language model

ULMFiT ("Universal Language Model Fine-tuning for Text Classification", Howard and Ruder, January 2018) goes further: pretrain a language model, then **fine-tune the language model itself** for the task, rather than only feeding its outputs to a new network. It is described as an effective transfer learning method that can be applied to any NLP task. It reduced error by 18 to 24% on most of the datasets tested, and with only 100 labelled examples it matched the performance of training from scratch on 100 times more data. [68]

## GPT-1 and BERT

OpenAI's GPT (June 2018) combined pretraining a decoder-only Transformer on unlabelled text with fine-tuning on each task, and beat task-specific architectures on 9 of 12 tasks. [41] Google's BERT (October 2018) pretrained a deep bidirectional Transformer and, with one added output layer, set new state-of-the-art results on eleven tasks. [9] Both used the Transformer (lesson 34) as the pretrained network.

## What it changed

By the end of 2018 the pattern was set: **pretrain** a language model on a huge unlabelled corpus (a general skill), then **adapt** it (a specific one). The GPT-3 paper (2020) pushed the idea to its limit: for a model large enough, the adaptation step can be a few examples written in the prompt, with no weight updates at all (lesson 48). [3]

:::key-takeaways
- ELMo (2018): contextual word vectors from a pretrained bidirectional language model; big gains on six tasks. [69]
- ULMFiT (2018): fine-tune the whole pretrained language model; with 100 labelled examples it matched training from scratch on 100 times more data. [68]
- GPT-1 and BERT (2018) did the same with Transformers; GPT-3 later removed the fine-tuning step with in-context learning. [41][9][3]
:::

:::glossary
- **Transfer learning**: reusing what was learned on one task or dataset for another.
- **Pretraining / fine-tuning**: a general first training stage on unlabelled text, then a short task-specific stage.
- **Contextual representation**: a word vector that depends on the sentence around the word.
- **Polysemy**: a word having several meanings, like "bank".
- **Bidirectional language model**: a model that reads text in both directions to build its representations.
- **Labelled data**: examples with known right answers, expensive to collect.
- **Text classification**: assigning a category (positive or negative review, topic) to a text.
:::
