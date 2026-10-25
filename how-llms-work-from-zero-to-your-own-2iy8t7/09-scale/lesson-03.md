---
id: l40
title: "Chinchilla: models were undertrained (2022)"
quiz: quiz-03.yaml
resources: []
sources: [8, 2, 11, 3]
---
After this lesson you can state the Chinchilla result, and say how it changed the way models were sized.

## A correction to the recipe

Kaplan's recommendation (lesson 39) was to spend most of the budget on a bigger model and less on data. In March 2022 DeepMind's Hoffmann and colleagues trained more than 400 models, from 70 million to over 16 billion parameters, on 5 to 500 billion tokens, and reached a different conclusion: current large language models were **undertrained**, because the field had scaled model size while keeping the amount of training data roughly fixed. [8]

Their rule: for compute-optimal training, model size and the number of training tokens should be scaled **equally**. Each doubling of parameters should come with a doubling of training tokens. [8] Compare lesson 19: a model too big for its data tends to memorise.

## The test: Chinchilla

To check the claim, they built **Chinchilla**, with 70 billion parameters trained on about four times more data than Gopher (280 billion parameters), using the same compute budget. Chinchilla outperformed Gopher, GPT-3, Jurassic-1 and Megatron-Turing NLG on a wide range of downstream tasks, and reached 67.5% average accuracy on the MMLU benchmark, over 7 points better than Gopher. Because it is smaller, it also needs less compute for fine-tuning and inference. [8]

## The numbers behind "scale equally"

The paper fitted its results three different ways and found, for how the optimal number of parameters N and training tokens D grow with compute C, exponents of about 0.5 for both: roughly N_opt ∝ C^0.5 and D_opt ∝ C^0.5. By contrast Kaplan et al. (2020) had 0.73 for parameters and 0.27 for data. [8] So when compute grows 100 times, the 2022 rule says make the model 10 times bigger *and* train it on 10 times more tokens; the 2020 rule would have put nearly all of the increase into the model.

A table in the paper turns this into a rule of thumb. For a compute-optimal 1 billion parameter model it estimates about 20.2 billion tokens, and 400 million parameters pairs with 8 billion tokens: about **20 tokens per parameter**. [8] Chinchilla itself, with 70 billion parameters, was trained on 1.4 trillion tokens, again about 20 per parameter. [8] Compare GPT-3 (lesson 38): 175 billion parameters on 300 billion tokens, under 2 per parameter. That is the sense in which earlier models were "undertrained".

## Why smaller can be better

The key practical point is the last one. Training happens once; inference happens every time anyone uses the model. A smaller model trained on more data is cheaper to run forever.

## What changed afterwards

LLaMA (February 2023) took this lesson on board: models from 7 to 65 billion parameters trained on trillions of tokens of publicly available data. The authors report that LLaMA-13B outperforms GPT-3 (175B) on most benchmarks, and that LLaMA-65B is competitive with Chinchilla-70B and PaLM-540B. [11]

:::low-confidence
This course read only the first part of the Chinchilla paper (introduction, methods and Tables 2 and 3) and does not cover why the 2020 and 2022 recommendations differ in detail. Treat "about 20 tokens per parameter" as the 2022 paper's estimate under its assumptions, not as a final law. [8][2]
:::

:::key-takeaways
- Chinchilla (2022): for a given compute budget, scale parameters and training tokens together; many large models were undertrained. [8]
- A 70B model trained on 4x the data beat the 280B Gopher with the same compute. [8]
- Fitted exponents of about 0.5 for parameters and 0.5 for tokens (Kaplan: 0.73 and 0.27), or about 20 tokens per parameter; GPT-3 had under 2. [8][3]
- Smaller, better-trained models are cheaper to run, which is why later models used far more tokens. [11]
:::

:::glossary
- **Undertrained**: trained on too little data for its size.
- **Compute-optimal**: the best result for a fixed amount of training computation.
- **Chinchilla**: DeepMind's 70-billion-parameter model that tested the compute-optimal rule.
- **Gopher**: DeepMind's earlier 280-billion-parameter model.
- **MMLU**: a benchmark of multiple-choice questions across many subjects.
- **Inference cost**: the compute needed each time the model is used.
- **Open weights (LLaMA)**: models whose parameters are released for others to use.
:::
