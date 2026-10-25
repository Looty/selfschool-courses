---
id: l31
title: "LLMOps: what changes with generative AI"
quiz: quiz-03.yaml
resources: []
sources: [15, 26]
---
After this lesson you can say which MLOps investments carry over to generative AI, what is new (prompts, retrieval, safety, tokens), and how to assess GenAIOps maturity.

## LLM basics in plain words

This lesson assumes a few ideas the course does not teach elsewhere. A **large language model (LLM)** is a model trained on huge amounts of text that predicts the next piece of text, which is enough to answer questions, summarise and write code. It reads and writes **tokens**, small chunks of text of roughly a word, and its **context window** is the most tokens it can see at once, so everything you want it to use must fit in the prompt. It does not look anything up: what it "knows" is frozen at training time, which is why **RAG** (below) pastes fresh documents into the prompt. An **embedding** is a list of numbers capturing a text's meaning; texts with similar meaning get similar numbers, which is how a vector store finds relevant passages. **Fine-tuning** means giving an existing LLM extra training on your own examples. The same box is repeated in chapter 12.

## Extend, do not restart

Generative AI means models, like the ones behind chatbots, that produce text, images or code. Microsoft's architecture guide on operating them (GenAIOps, also called LLMOps; LLM = large language model) says that if you have MLOps investments you do not need to start over. You can reuse them for several generative AI patterns, and extend them for others. [26] The maturity-model page agrees that GenAIOps adds capabilities that complement the MLOps levels, such as prompt lifecycle, retrieval augmentation, output safety and token cost governance. [15]

## What is different

The guide names how generative AI workloads differ. Traditional ML trains new models for specific tasks, and the trained, deployed model is the key asset. Generative AI workloads consume, and sometimes fine-tune, models that address a broad range of use cases, and a key asset is the **prompt**, made of instructions and often context data. The orchestration logic that builds prompts and calls the model and other back ends is part of the system you govern. [26]

It describes three technical patterns: [26]

- **Fine-tuning**: giving an existing model extra training on your own examples. It follows the same steps as training a traditional model (prepare data, train, evaluate, deploy), so existing MLOps investments apply directly.
- **Prompting**: steering a model with text. A system prompt sets its persona or rules, user prompts carry the conversation, and an orchestrator (code that assembles the prompt and calls the model, often exposed as an API) builds them.
- **Retrieval-augmented generation (RAG)**: look up relevant information first, then paste it into the prompt so the model can answer from it. An orchestration layer searches your data sources and injects the best matches. Typically the source data is cut into chunks and stored with metadata in a vector store (a database that finds items by meaning, not exact words).

## The same loops, new content

The guide maps the familiar loops onto the new patterns. [26]

| Area | Carries over | New work |
| --- | --- | --- |
| DataOps | Reproducibility and data versioning | Chunking pipelines, vector stores, keeping search indexes fresh and compliant, for example right-to-be-forgotten requests |
| Experimentation | Tracking inputs next to outputs | Prompt variants, chunking strategies, embedding model choice, search configuration |
| Evaluation | Metrics per task | Metrics by use case: BLEU for translation, ROUGE and others for summarisation, groundedness, relevance, coherence and fluency for RAG |
| Deployment | Tests, canary and blue-green rollouts | Deploying orchestrators and data stores, often behind a gateway in front of the model |
| Monitoring | Operational monitoring, drift | Latency, token usage and 429 errors, content safety, user feedback such as thumbs up or down |

The gateway deserves a note: a common practice is a gateway in front of the model for load balancing, authentication and monitoring, which also supports progressive rollout of new models and rollback. [26]

## Resource management is different

For models consumed as a service, infrastructure is not your concern; the focus moves to throughput, quota and throttling, and tokens are used for billing, throttling and quotas. The guide advises monitoring quota usage for cost management and performance efficiency. [26]

## Assess maturity separately

Use the MLOps maturity model for your existing practices. Because GenAIOps needs other capabilities that can mature independently, the guide suggests defining workload-specific maturity levels for them: data and prompt versioning, experimentation and evaluation, deployment automation, monitoring, content safety and resource management, each with measurable entry and exit criteria. [26]

:::low-confidence
The guide is written around Azure services and its examples use them. The patterns are general, but the product names are not. This course did not read a vendor-neutral source on LLM operations. [26]
:::

:::key-takeaways
- Reuse MLOps for fine-tuning; extend it for prompting and RAG. [26]
- The prompt, the orchestrator and the retrieval data store become part of what you version, test and monitor. [26]
- New concerns: content safety, token cost and quotas, index freshness. [15][26]
:::

:::glossary
- **Generative AI**: models that create new text, images, code or audio.
- **LLM (large language model)**: a generative model trained on huge amounts of text.
- **GenAIOps / LLMOps**: MLOps adapted to generative AI.
- **Prompt**: the text instructions (and context) you give a model.
- **System prompt / user prompt**: the standing rules for the model, and the person's actual request.
- **Orchestrator**: code that builds prompts, calls the model and other services, and combines the results.
- **Fine-tuning**: extra training of an existing model on your own data.
- **RAG (retrieval-augmented generation)**: fetch relevant documents and give them to the model along with the question.
- **Chunk**: a small piece of a document stored for retrieval.
- **Embedding**: a list of numbers that captures the meaning of a text, so similar texts are close together.
- **Vector store**: a database that finds items by similarity of meaning.
- **Search index**: the structure that makes searching fast; must be kept up to date.
- **Right to be forgotten**: a person's legal right to have their data deleted.
- **BLEU / ROUGE**: scores comparing generated text with a reference text (translation, summaries).
- **Groundedness**: the answer sticks to the provided sources.
- **Coherence / fluency**: the text hangs together and reads naturally.
- **Blue-green rollout**: run old and new side by side, then switch traffic over.
- **Gateway**: a front door in front of the model handling authentication, load balancing and monitoring.
- **Token**: a small chunk of text (about a word or part of one) that models read and bill by.
- **429 error**: "too many requests", the service is throttling you.
- **Quota / throttling**: a cap on usage, and slowing you down when you hit it.
:::
