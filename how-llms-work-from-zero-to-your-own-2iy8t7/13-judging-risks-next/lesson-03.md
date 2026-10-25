---
id: l59
title: Risks, limits and where to go next
quiz: quiz-03.yaml
resources: []
sources: [21, 37, 29, 4, 19, 3, 18, 75, 64]
---
After this lesson you can list the main risks of LLMs in plain terms and choose what to study next.

## The risks you now understand

Every item below traces back to something you built or read in this course.

| Risk | Where it comes from | Seen in |
| --- | --- | --- |
| **Hallucination** | The objective rewards likely text, not true text [21] | Lessons 3, 47 |
| **Falsehoods imitated from data** | Larger models were generally less truthful on TruthfulQA [37] | Lesson 3 |
| **Bias** | Models reflect biases in their training data; GPT-2's card shows stereotyped completions [29] | Lessons 3, 41 |
| **Toxic or unhelpful output** | Scaling alone does not make a model follow user intent [4] | Lesson 43 |
| **Overtrust (the ELIZA effect)** | Fluent output reads as understanding | Lesson 8 |
| **Contamination of scores** | Benchmarks may leak into training data [3] | Lesson 57 |
| **Cost and concentration** | Training the largest models needs large infrastructure [21] | Lesson 41 |
| **Tool and injection risks** | Models that act on text they read can be misled | Lesson 53 |

None of these has a single fix. They are managed with testing, grounding answers in sources, limiting what tools can do, keeping a human in the loop for important decisions, and measuring on your own cases.

## A checklist from security practice

If you build an application on a model, the OWASP GenAI Security Project's Top 10 for LLM applications (2025 edition) is a practical list of what goes wrong. The ten entries are: prompt injection, sensitive information disclosure, supply chain, data and model poisoning, improper output handling, excessive agency, system prompt leakage, vector and embedding weaknesses, misinformation, and unbounded consumption. [75] Several map directly to this course: *excessive agency* is the tool-calling loop of lesson 53 with too many privileges; *improper output handling* is trusting the model's text without validating it; *vector and embedding weaknesses* concerns the retrieval systems of lesson 52; *unbounded consumption* is the cost side of tokens and long contexts. [75]

## A system-level view

The Stanford report "On the Opportunities and Risks of Foundation Models" gives the field a name for this class of model: systems trained on broad data at scale that can be adapted to a wide range of downstream tasks. Two of its points matter for risk. First, **emergence**: scale produces new capabilities that were not explicitly designed in, so it is unclear when these models fail and what they can do. Second, **homogenisation**: when many applications are built on the same base model, its flaws are inherited by all of them. [64]

## What the course did not cover

Be honest about the gaps. Lesson 64 introduces serving efficiency (caching, quantisation, mixture of experts) but only at the level of the papers' abstracts. These sources did not cover multimodal models that handle images or audio in any depth, long-context techniques beyond position encodings, interpretability research, or regulation and law. Each is a field of its own.

## Where to go next

Choose by goal.

- **Build more from scratch.** Andrej Karpathy's *Neural Networks: Zero to Hero* series builds from backpropagation (micrograd) through a character-level bigram model and an MLP language model to a GPT and its tokenizer, in code. It assumes solid Python and introductory maths. [19] You have already met each idea here, so the series should now go faster.
- **Train a bigger model.** Study the nanochat project's tokenizer, pretraining, fine-tuning and evaluation scripts end to end. [18]
- **Use models in applications.** The MLOps course in this app covers running LLM applications: retrieval, evaluation, tracing and security.
- **Read the papers.** Start with the ones in this course's source list: *Attention Is All You Need*, the GPT-3 paper, the scaling-law and Chinchilla papers, and InstructGPT. Their abstracts are short; the full texts repay a second read now.

:::key-takeaways
- Most LLM risks follow from how the models are trained: likely text, web data, and fluent output.
- Manage them with testing, grounding, limited tools and human oversight; none has a single fix.
- Next steps: build more from scratch (Zero to Hero), train a bigger model (nanochat), or apply models in products.
:::

:::glossary
- **Hallucination**: a confident statement the training data does not justify.
- **Overtrust**: relying on a system more than its reliability deserves.
- **Human in the loop**: a person reviews or approves important decisions.
- **Quantisation**: storing a model's numbers with fewer bits to save memory.
- **Multimodal**: handling more than text, such as images or audio.
- **Mixture of experts**: a model design where only part of the network runs for each token.
- **Interpretability**: research into what a model's parts do.
:::
