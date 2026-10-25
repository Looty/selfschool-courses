---
id: l45
title: Retrieval-augmented generation as a system
quiz: quiz-01.yaml
resources: []
sources: [26, 61]
---
After this lesson you can explain the idea behind retrieval-augmented generation, say what it adds as an operated system, and list what you must version and monitor.

## LLM basics in plain words

A **large language model (LLM)** is a model trained on huge amounts of text that predicts the next piece of text, which is enough to answer questions, summarise and write code. It reads and writes **tokens**, small chunks of text of roughly a word. Its **context window** is the most tokens it can see at once, so everything you want it to use must fit in the prompt. It does not look anything up: what it "knows" is frozen at training time. An **embedding** is a list of numbers capturing a text's meaning, so similar texts get similar numbers. **Fine-tuning** is extra training of an existing LLM on your own examples. An **LLM application** is ordinary code that builds a prompt, calls a model and handles the answer; this chapter is about operating that code.

## The idea in the original paper

The 2020 RAG paper starts from an observation: large language models absorb a lot of facts during training and store them in their parameters (the learned numbers inside the model), but they are clumsy at looking those facts up precisely. They also cannot easily show where an answer came from, or update what they know without retraining. [61]

Its answer combines two kinds of memory, like a student who has studied hard but also keeps a reference book open. **Parametric memory** is knowledge baked into the model's weights; in the paper, a pre-trained seq2seq model (one that turns an input text into an output text). **Non-parametric memory** is an external store the model reads from; in the paper, a dense vector index of Wikipedia (a searchable collection where each passage is represented by numbers capturing its meaning), searched by a pre-trained neural retriever (a model that finds the relevant passages). Retrieval-augmented generation (RAG) combines both in one model for writing text. [61] The authors compare two formulations: one uses the same retrieved passages for the whole answer, the other can use different passages for each word it writes. [61]

The abstract claims state-of-the-art results on three open-domain question-answering tasks (questions about anything, not one topic), beating models that rely on memory alone and models that only retrieve and extract, and more specific, varied and factual generated text than a memory-only baseline. [61]

## What changed since

Only the abstract was read for this course. The paper's system trains retriever and generator together; the RAG systems teams build today are often assembled from a hosted model and a separate vector store, as Microsoft's guide describes: an orchestration layer queries data sources and injects the most relevant results into the prompt, and a typical implementation splits source data into chunks and stores them with metadata in a vector store. [26][61] The shared idea is the one in the abstract: knowledge lives outside the weights, so it can be updated and its source shown.

## What RAG adds to what you operate

Treat the retrieval side as data and software, using the same habits as chapters 3 and 5. [26]

| Part | What to version and check | Why |
| --- | --- | --- |
| Source documents | Which documents, which version | Answers can only be as current and correct as the sources |
| Chunking and embedding | Chunk size, overlap, embedding model, index build | A change to any of them changes what is retrieved |
| Search configuration | Number of results, filters, ranking | Part of the behaviour, like a model hyperparameter |
| Prompt template | The instructions and how context is inserted | It is code for the model |
| Index freshness | How and when sources are re-indexed, including removal requests | Microsoft's guide names fresh and compliant indexes, for example right-to-be-forgotten requests |

The first four rows are the course's translation of the guide's DataOps and experimentation advice into a checklist. The guide itself lists chunking pipelines, vector stores, fresh and compliant search indexes, and tracking of prompt variants, chunking strategies, embedding model and search configuration. [26]

## Provenance is the operational payoff

Because retrieved passages are known, a RAG system can log which passages it used for an answer. That supports the "which data produced this output" question that lineage answers in classic ML (lesson 15) and makes failures diagnosable: wrong answer, right passages means a generation problem; wrong passages means a retrieval problem. This diagnostic split is course reasoning, not a claim from the sources.

:::low-confidence
Only the abstract of the RAG paper was read, and the Microsoft guide is written around Azure services. This lesson does not cover current retrieval techniques such as re-ranking or hybrid search. [26][61]
:::

:::key-takeaways
- RAG combines parametric memory (weights) with non-parametric memory (an external index) so knowledge can be updated and sourced. [61]
- In practice an orchestrator retrieves chunks from a vector store and injects them into the prompt. [26]
- Version source data, chunking, embeddings, search configuration and prompts, and plan index freshness. [26]
:::

:::glossary
- **RAG (retrieval-augmented generation)**: look up relevant text first, then let the model answer using it.
- **Language model**: a model that predicts and generates text.
- **Parameters / weights**: the learned numbers inside a model.
- **Parametric memory**: what the model "knows" from its weights.
- **Non-parametric memory**: an outside store the model reads from.
- **seq2seq**: a model type that turns one sequence of text into another.
- **Vector index**: a searchable store where each passage is a list of numbers, so similar meanings sit close together.
- **Retriever**: the component that finds relevant passages for a question.
- **Provenance**: where an answer's information came from.
- **Open-domain question answering**: answering questions on any subject.
- **Orchestrator / orchestration layer**: code that searches the data, builds the prompt and calls the model.
- **Prompt**: the text given to the model.
- **Chunk / chunking**: a small piece of a document / cutting documents into pieces for retrieval.
- **Overlap**: chunks sharing some text at the edges so nothing is cut mid-thought.
- **Embedding**: numbers representing a text's meaning; the **embedding model** produces them.
- **Vector store**: a database holding embeddings for similarity search.
- **Index freshness**: how up to date the searchable copy of the sources is.
- **Right to be forgotten**: a person's right to have their data removed.
- **Re-ranking / hybrid search**: re-sorting results with a better model / combining keyword and meaning-based search.
- **Lineage**: the trail showing what produced an output.
:::
