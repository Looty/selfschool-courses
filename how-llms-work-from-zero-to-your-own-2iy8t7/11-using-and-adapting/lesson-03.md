---
id: l50
title: "Fine-tuning and LoRA (2021)"
quiz: quiz-03.yaml
resources: []
sources: [10, 67]
---
After this lesson you can say when you would fine-tune instead of prompt, and how LoRA lets you do it by training a tiny fraction of the weights.

## Prompt or fine-tune?

Prompting (lesson 48) changes what the model sees. **Fine-tuning** changes the model: it continues training on your own examples (lesson 43). Rules of thumb:

- **Prompting first.** It is instant, free of training, and reversible.
- **Fine-tune** when you need a consistent style or format that prompts cannot hold, a narrow task done cheaply at scale with a smaller model, or behaviour you cannot fit in a prompt.
- **Neither** for adding lots of changing facts: provide those in the prompt (lesson 52).

## The cost problem

Full fine-tuning updates every parameter, so you need memory for the weights, their gradients and the optimiser's bookkeeping. For a 175-billion-parameter model that means a separate full copy per task.

## LoRA

In June 2021 Hu and colleagues proposed **LoRA: Low-Rank Adaptation**. The idea: freeze the pretrained weights and inject small trainable low-rank matrices into each Transformer layer. [10] "Low-rank" means that instead of learning a full change ΔW to a big weight matrix W, you learn two thin matrices B and A whose product has the same shape: W + B·A. If W is 1000 × 1000, A might be 4 × 1000 and B 1000 × 4: 8,000 numbers instead of a million.

The paper's claims, compared with fine-tuning GPT-3 175B with Adam: [10]

- Up to 10,000 times fewer trainable parameters.
- About 3 times less GPU memory.
- Model quality on par with or better than full fine-tuning on RoBERTa, DeBERTa, GPT-2 and GPT-3.
- **No additional inference latency**, unlike adapter layers, because the product B·A can be merged into W after training.

The authors also give an empirical study of rank deficiency in language-model adaptation to explain why it works: the useful change to the weights seems to live in a small number of dimensions. [10]

## What the full paper adds

The LoRA paper's introduction frames the goal as making adaptation more parameter- and compute-efficient, and it names the two earlier strategies and their weaknesses: adding **adapter layers**, which introduce inference latency because they add computation that must run in sequence; or optimising the **input-layer activations** (prompt-tuning style), which have their own limits at large scale. [10] With GPT-3 175B as the base, the number of trainable parameters can be as small as 0.01% of the base model's. [10]

## Going further: QLoRA

QLoRA (Dettmers et al., May 2023) combines LoRA with quantisation: it backpropagates gradients through a frozen, 4-bit quantised pretrained model into low-rank adapters, which cuts memory enough to fine-tune a 65-billion-parameter model on a single 48 GB GPU while aiming to preserve full 16-bit fine-tuning quality. Its innovations include a 4-bit NormalFloat data type, "double quantization" and paged optimisers. [67] The authors also report that their Guanaco model family reached 99.3% of ChatGPT's performance on the Vicuna benchmark after 24 hours of fine-tuning on one GPU, though they also say current chatbot benchmarks are not fully trustworthy. [67]

## Practical consequences

- You can keep **one base model and many small LoRA files**, one per task or customer.
- You can fine-tune a large model on modest hardware.
- The same trick is used for adapting open-weight models (lesson 58). In the next lab you will implement LoRA yourself.

:::key-takeaways
- Fine-tune when prompts cannot give a consistent behaviour; keep facts in the prompt.
- LoRA freezes the base weights and trains small low-rank matrices: up to 10,000x fewer trainable parameters and about 3x less GPU memory on GPT-3 175B. [10]
- LoRA adds no inference latency because the learned change can be merged into the weights. [10]
:::

:::glossary
- **Fine-tuning**: continuing training of a pretrained model on your own examples.
- **LoRA (low-rank adaptation)**: freezing the weights and training two thin matrices whose product is the weight change. [10]
- **Low-rank**: expressible using a small number of dimensions.
- **Adapter**: a small extra layer inserted into a frozen model (the older approach LoRA improves on).
- **Frozen**: not updated during training.
- **Optimiser state**: the extra numbers (such as running averages) Adam keeps for each parameter.
- **Merge**: adding the learned change into the base weights so no extra computation is needed.
:::
