---
id: l58
title: Open weights, closed APIs, and who can build one
quiz: quiz-02.yaml
resources: []
sources: [11, 28, 21, 18, 29, 51, 52, 66]
---
After this lesson you can explain the difference between open-weight and API-only models, and say why the LLaMA release in 2023 changed who could experiment.

## Three ways models have been shared

The history in chapter 9 already shows three patterns.

| Pattern | Example | What you get |
| --- | --- | --- |
| **API only** | GPT-3 (2020) | You send text to a service; you never see the weights [21] |
| **Staged release** | GPT-2 (2019) | Smaller models first, the full model later, after monitoring for misuse [28] |
| **Open weights** | LLaMA (2023) | Downloadable parameters you can run and adapt [11] |

## LLaMA

In February 2023 Meta's Touvron and colleagues released LLaMA, a family of models from 7 to 65 billion parameters trained on trillions of tokens. The authors state that state-of-the-art models can be trained using publicly available datasets exclusively, that LLaMA-13B outperforms GPT-3 (175B) on most benchmarks, and that LLaMA-65B is competitive with Chinchilla-70B and PaLM-540B. They released all the models to the research community. [11]

The practical effect, together with the Chinchilla insight (lesson 40), was that a model small enough to run on one machine could match a far bigger API model on many benchmarks. People could study, fine-tune (lesson 50) and run models locally. Wikipedia's overview lists open-source models such as BLOOM and LLaMA gaining popularity in 2022 and 2023. [21]

## What came after LLaMA

- **Llama 2 (July 2023)**: pretrained and fine-tuned models from 7 billion to 70 billion parameters. The fine-tuned versions, Llama 2-Chat, are optimised for dialogue; the authors say they outperform open-source chat models on most tested benchmarks and, judged by human ratings of helpfulness and safety, "may be a suitable substitute for closed-source models". They describe their fine-tuning and safety work in detail so the community can build on it. [52]
- **Mistral 7B (October 2023)**: a 7-billion-parameter model that its authors say outperforms Llama 2 13B on all evaluated benchmarks and Llama 1 34B in reasoning, mathematics and code generation. It uses grouped-query attention for faster inference and sliding-window attention to handle long sequences at lower cost, and is released under the Apache 2.0 licence. [66]
- **GPT-4 (March 2023)**, by contrast, is described in a technical report that gives capabilities, such as exam performance around the top 10% of test takers on a simulated bar exam, but whose abstract says nothing about parameter count, architecture, training data or compute. The authors do say they built infrastructure that scales predictably, so that models trained with at most 1/1,000th of GPT-4's compute could forecast some aspects of its performance. [51]

This is a real difference in what you can learn. With an open-weight model you can read how it was built and run it yourself; with a closed one you get behaviour and a report. 

:::low-confidence
Only the abstracts of the Llama 2, Mistral 7B and GPT-4 papers were read. "Open weights" does not always mean "open source": a model's licence may restrict use, and the training data is often not released (GPT-2's WebText was not publicly released, for example). The sources read here do not cover licence terms, so check each model's licence before using it. [28][29]
:::

## Trade-offs

- **Open weights:** you can run it privately, adapt it, inspect it, and rely on it not changing underneath you. You pay for hardware and take on operating it, and safety measures are in your hands.
- **API:** no hardware to run and often the strongest models, but your data leaves your machine, behaviour can change when the provider updates, and you pay per token.
- **Release strategy matters:** staged releases like GPT-2's were an attempt to look for misuse before full release; by November 2019 OpenAI said it had "seen no strong evidence of misuse so far". [28]

## You can build a small one

The nanochat project describes itself as the simplest experimental harness for training LLMs, aimed at end-to-end training of GPT-2-class models on budgets under $1000, and reports about 2 hours on one 8-GPU node for about $48 at on-demand prices. [18] That is a long way from your laptop mini-GPT but the same pipeline: tokenizer, pretraining, fine-tuning, evaluation, inference. You have now built every stage in miniature.

:::key-takeaways
- Models are shared as API-only, staged releases, or open weights. [21][28][11]
- LLaMA (2023) released 7B to 65B models trained on public data; LLaMA-13B beat GPT-3 on most benchmarks. [11]
- Open weights give control and privacy; APIs give convenience and often capability. 
:::

:::glossary
- **Open weights**: trained parameters published so anyone can download and run them.
- **Open source**: the code (and sometimes data) is published under a licence allowing broad use; not the same as open weights.
- **API-only**: the model is only reachable through a hosted service.
- **Licence**: the legal terms for using a model or code.
- **LLaMA**: Meta's 2023 family of open-weight models.
- **Local inference**: running a model on your own machine.
- **nanochat**: a small open project for training chat-style models end to end. [18]
:::
