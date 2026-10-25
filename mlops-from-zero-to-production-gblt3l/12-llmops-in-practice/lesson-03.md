---
id: l47
title: Automated evals and graders
quiz: quiz-03.yaml
resources: []
sources: [62, 63]
---
After this lesson you can choose between code-based and model-based graders, design an eval set that includes edge cases, and run an evaluation with a dataset, a predict function and scorers.

## Design principles

The Anthropic page gives three principles for eval design. [62]

- **Be task-specific.** Mirror the real task distribution and include edge cases: irrelevant or overly long input, harmful or irrelevant user input, and ambiguous cases where humans also disagree.
- **Automate when possible.** Use formats that can be graded automatically: multiple choice, string match, code-based checks or LLM-based grading.
- **Prioritise volume over quality.** The page prefers many automatically graded questions with somewhat lower signal to fewer high-quality, hand-graded ones.

The third principle is a trade-off, not a law. It fits regression-style evals that run on every change; for a final release decision you may still want a small set graded by experts.

## Five grading methods in the page's examples

Each is tied to a criterion from the previous lesson. [62]

| Method | Criterion | Example on the page |
| --- | --- | --- |
| Exact match (code) | Task fidelity | Sentiment over 1,000 labelled tweets, normalised string comparison; edge cases include sarcasm and mixed sentiment |
| Cosine similarity (code) | Consistency | Embed answers to paraphrased FAQ questions with Sentence-BERT (`all-MiniLM-L6-v2`) and average pairwise similarity over 50 question groups |
| ROUGE-L F1 (code) | Relevance and coherence | Score summaries of 200 articles against reference summaries by longest common subsequence |
| LLM Likert scale | Tone and style | A grader model rates each customer-service reply from 1 to 5 for a target tone |
| LLM binary classification | Privacy | A grader answers yes or no on whether a medical chatbot reply contains PHI, over 500 queries |

Two cautions from the page: the ROUGE-L implementation shown is simplified and may score differently from the Python `rouge` library, and for LLM-based grading it recommends using a different model as the grader than the one that generated the output. [62] The binary PHI check is presented as able to catch implicit PHI that rule-based systems miss. [62]

## Running it: dataset, predict function, scorers

MLflow's GenAI evaluation follows the same shape. An evaluation combines a dataset of test cases, one or more scorers, and a predict function that generates outputs. Scorers include built-in LLM-as-a-judge scorers and tools to build custom judges. [63]

```python
results = mlflow.genai.evaluate(
    data=dataset,
    predict_fn=predict_fn,
    scorers=[
        Correctness(),
        Guidelines(name="is_english", guidelines="The answer must be in English"),
    ],
)
```

Results appear as a run, which ties evaluation to the experiment tracking of lesson 13: the prompt version, the model and the scores belong in one record. [63] The page's example calls an OpenAI model and needs an API key, so it costs money to run; budget for eval cost like any test suite. [63]

## Judges need checking too

An LLM judge is just another model asked to grade the first one's answers, so its judgement depends on which model and prompt you use for it. The MLflow page does not discuss how reliable judges are. [63] A practical safeguard, the course's advice and not the page's, is to hand-grade a small sample, compare the judge with your grades, and re-check when you change the judge.

:::low-confidence
Only the first two thirds of the Anthropic page were read. The MLflow page is an overview and does not discuss judge reliability, scaling or cost. [62][63]
:::

:::key-takeaways
- Evals should mirror the task and include edge cases; automate grading where possible. [62]
- Match the method to the criterion: exact match, similarity, ROUGE, LLM scale or LLM yes/no. [62]
- Use a different model as grader than the one that produced the output, and check the judge against human grades. [62][63]
- An evaluation is a dataset, a predict function and scorers; log it with your experiment. [63]
:::

:::glossary
- **Eval set**: the collection of test cases an application is scored on.
- **Grader / scorer**: whatever assigns a score: code, a person, or another model.
- **Code-based grader**: a program checks the answer by fixed rules.
- **Model-based (LLM) grader / LLM-as-a-judge**: another model reads the answer and scores it.
- **Edge case**: an unusual input that tends to break things.
- **Regression eval**: a test run on every change to catch things that got worse.
- **Exact match**: the answer must equal the expected text (after tidying).
- **Cosine similarity**: a score of how alike two embeddings are (1 = identical direction).
- **Embedding / Sentence-BERT**: numbers representing a text's meaning / a model that makes them.
- **ROUGE-L**: a score comparing a summary with a reference by their longest shared sequence of words.
- **Longest common subsequence**: the longest run of words appearing in both texts, in order.
- **Likert scale**: a rating scale such as 1 to 5.
- **Binary classification**: a yes/no judgement.
- **PHI (protected health information)**: private medical details about a person.
- **Implicit PHI**: details that reveal health information without stating it outright.
- **MLflow GenAI evaluation**: MLflow's tooling for running evals and logging results.
- **Predict function**: your code that takes an input and returns the application's answer.
- **Dataset (of test cases)**: inputs, and optionally expected outputs.
:::
