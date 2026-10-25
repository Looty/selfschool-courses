---
id: l52
title: Giving the model facts it does not have (RAG)
quiz: quiz-05.yaml
resources: []
sources: [38, 21]
---
After this lesson you can explain retrieval-augmented generation in one paragraph, and when to prefer it to fine-tuning.

This is a short version. The MLOps course in this app covers operating a RAG system in detail; here you only need the idea.

## The problem

A model's knowledge is frozen at training time, is stored implicitly in its weights, and cannot be cited. The RAG paper (Lewis et al., May 2020) says large pretrained models store factual knowledge in their parameters but have limited ability to access and precisely manipulate it, so they lag behind task-specific architectures on knowledge-intensive tasks. [38] Updating a fact would mean retraining.

## The idea

Combine two kinds of memory. **Parametric memory** is what is in the model's weights. **Non-parametric memory** is an outside store the model can read from; in the paper, a dense vector index of Wikipedia reached through a neural retriever. [38] At question time:

1. **Retrieve**: turn the question into a vector (an embedding, lesson 23) and find the stored passages whose vectors are closest.
2. **Augment**: paste those passages into the prompt.
3. **Generate**: have the model answer from the pasted text.

The paper reports state-of-the-art results on three open-domain question-answering tasks, and more specific, diverse and factual generated text than a model using parametric memory alone. [38]

## Why it is popular

- **Updatable.** Change the documents, not the model.
- **Citable.** You know which passages were used and can show them.
- **Cheaper than training** for changing facts. Compare fine-tuning (lesson 50), which is better for style and behaviour than for facts.

## Limits

RAG answers can only be as good as the retrieval: if the right passage is not found, the model may fall back on its memory and hallucinate (lesson 3). Also, everything retrieved must fit in the context window (lesson 2). [21]

:::key-takeaways
- RAG combines parametric memory (weights) with non-parametric memory (a retrievable store). [38]
- Retrieve relevant passages, put them in the prompt, and let the model answer from them. [38]
- It makes knowledge updatable and citable, but quality depends on retrieval.
:::

:::glossary
- **RAG (retrieval-augmented generation)**: retrieving relevant text and giving it to the model to answer from.
- **Parametric memory**: knowledge stored in the model's weights.
- **Non-parametric memory**: knowledge in an outside store the model reads.
- **Retriever**: the component that finds relevant passages.
- **Vector index**: a store where each passage is a vector, searched by similarity.
- **Knowledge-intensive task**: a task that needs facts rather than only language skill.
- **Open-domain QA**: answering questions about anything.
:::
