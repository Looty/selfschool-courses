---
id: l47
title: What alignment does not fix
quiz: quiz-05.yaml
resources: []
sources: [4, 37, 21, 63, 51]
---
After this lesson you can name what alignment training improves, what it leaves unsolved, and what that means for how you use an assistant.

## What it improves

Tuning with human feedback made models more helpful and less toxic. In InstructGPT's evaluations, the aligned model gained in truthfulness and reduced toxic output, with minimal regressions on public benchmarks. [4] It also makes models far more pleasant to use: they answer the question asked, in a sensible format.

## What it leaves open

- **Simple mistakes.** The InstructGPT authors themselves say the model still makes simple mistakes. [4]
- **Hallucination.** The training objective after tuning is still about producing responses people rate well, and a confident wrong answer can rate well. Wikipedia lists hallucination, biased or inaccurate training data and black-box behaviour among the limits of LLMs. [21]
- **Imitated falsehoods.** TruthfulQA found models mimic common misconceptions; the authors argued that fine-tuning with objectives other than imitating web text is more promising than scale alone. [37] That is the direction RLHF took, but the benchmark's best model was still far from human truthfulness. [37]
- **Whose values?** Preference data reflects the labelers and their instructions, which are a small sample of people.

A survey of hallucination in natural language generation (Ji et al., 2022) states the starting point plainly: deep-learning-based generation "is prone to hallucinate unintended text", which degrades performance and raises concerns about safety in real-world applications. It reviews metrics, mitigation methods and task-by-task progress for summarisation, dialogue, question answering, data-to-text and translation. [63] And the GPT-4 report, which describes a model that accepts image and text inputs, claims that post-training alignment improves factuality and adherence to desired behaviour, but also says the model is "less capable than humans in many real-world scenarios". [51]

:::low-confidence
This course read the abstracts of the hallucination survey and the GPT-4 report, not their full texts, and did not find a source measuring how much alignment training changes hallucination rates in current models. Treat "helpful and less toxic, still not reliable" as the safe summary. [63][51][4][37]
:::

## What to do as a user or builder

1. **Ground answers in text you provide** when accuracy matters: paste or retrieve the source (chapter 11).
2. **Check claims that matter**, especially numbers, citations and names.
3. **Test your own cases** instead of trusting a general benchmark (chapter 13).
4. **Expect different failure modes** from different models, and from the same model after an update.

:::key-takeaways
- Alignment tuning improved truthfulness and reduced toxicity in InstructGPT, but simple mistakes remained. [4]
- Hallucination and bias are listed limits of LLMs. [21]
- The safe use pattern: ground in provided text, verify what matters, test your own cases.
:::

:::glossary
- **Alignment tax**: a worry that tuning for safety or helpfulness might cost performance elsewhere (not studied in these sources).
- **Grounding**: giving the model the source text it should answer from.
- **Imitative falsehood**: a false answer that copies a common misconception from the training data.
- **Robustness**: staying reliable when inputs are unusual.
- **Black-box behaviour**: outputs whose reasons are hard to inspect.
:::
