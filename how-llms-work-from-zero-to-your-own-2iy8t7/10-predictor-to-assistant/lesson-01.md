---
id: l43
title: Why a text predictor is not yet an assistant
quiz: quiz-01.yaml
resources: []
sources: [4, 21, 37, 30, 65]
---
After this lesson you can explain why a pretrained model does not follow instructions well, and what instruction tuning is.

## The gap

A pretrained model (chapters 8 and 9) is trained to continue text. Ask it "Write a poem about spring" and a good continuation might be a list of other poem requests, because such lists exist on the web. It is not trying to help you; it is trying to continue.

The InstructGPT paper opens on exactly this: scaling a language model up does not by itself make it better at following the user's intent, and large models can still produce untruthful, toxic or unhelpful output. [4] TruthfulQA showed a related effect: the largest models were generally the least truthful, because they had learned popular falsehoods from the training text. [37]

The InstructGPT authors give the cause in one sentence: the usual objective, "predicting the next token on a webpage from the internet", is different from the objective "follow the user's instructions helpfully and safely", so the language modelling objective is **misaligned**. [4]

## Instruction tuning before InstructGPT: FLAN

Google's FLAN paper (Wei et al., September 2021) showed the idea at scale. Instruction tuning, finetuning a language model on tasks described through natural-language instructions, substantially improves zero-shot performance on unseen tasks. They tuned a 137-billion-parameter pretrained model on over 60 NLP tasks phrased as instructions; the resulting FLAN model beat zero-shot GPT-3 (175B) on 20 of 25 evaluated tasks. Ablations showed that the number of finetuning datasets, the model scale and the use of natural-language instructions all mattered. [65]

OpenAI's InstructGPT work found, though, that public NLP datasets are "not reflective of how our language models are used": they compared GPT-3 fine-tuned on human-preference data against GPT-3 fine-tuned on the FLAN and T0 collections, and the preference-trained models did better on the prompts people actually submit. [4] That motivates the next lessons.

## Instruction tuning

The first fix is plain **supervised fine-tuning** (lesson 2). Collect examples of prompts paired with the response a good assistant would give, and continue training the pretrained model on those pairs, using the same next-token loss. Wikipedia describes this as instruction tuning: supervised fine-tuning that teaches a model to follow user instructions. [21]

In the InstructGPT recipe this is the first of three steps: labelers write demonstrations of the desired behaviour, and GPT-3 is fine-tuned on them with supervised learning. [4] Steps two and three, which use human rankings and reinforcement learning, are the next lessons.

## What changes in practice

- The model learns the *format* of helpful conversation: answer the question, stay on topic, stop at the end.
- It does not learn many new facts; those came from pretraining. The fine-tuning set is tiny by comparison with pretraining.
- Chat models are given text in a special template with roles ("system", "user", "assistant") that mirrors the fine-tuning data. If you pass a chat model plain text without its template, the Hugging Face documentation warns, it may return worse output. [30]

:::key-takeaways
- Scaling up alone does not make a model follow instructions or tell the truth. [4][37]
- Instruction tuning continues training on (prompt, ideal response) pairs. [21][4]
- It teaches the format of helpfulness more than it teaches new knowledge.
:::

:::glossary
- **Instruction tuning**: supervised fine-tuning on prompts paired with good responses. [21]
- **Supervised fine-tuning (SFT)**: continuing training with the next-token loss on a curated dataset.
- **Demonstration**: a human-written example of the desired response.
- **Labeler**: a person who writes or rates examples for training.
- **Chat template**: the fixed text layout with roles that a chat model expects.
- **Alignment**: making a model's behaviour match what people want.
:::
