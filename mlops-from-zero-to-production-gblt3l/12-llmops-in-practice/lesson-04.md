---
id: l48
title: Tracing, monitoring and security for LLM apps
quiz: quiz-04.yaml
resources: []
sources: [26, 63, 67, 68]
---
After this lesson you can say what to record about each LLM call, which production signals to watch, and how the OWASP list frames security for LLM applications.

## Trace every call

A trace is a step-by-step record of one request as it moves through your application, like a receipt listing every stop. MLflow Tracing records metrics such as latency (how long a step took) and token usage (a token is a small chunk of text the model reads or writes, and what you are billed by) at each step of an LLM application, plus quality metrics, so you can find bottlenecks. Human feedback from end users or domain experts can be attached to traces, with metadata such as user and timestamp. [63] A trace is the LLM equivalent of the request log in lesson 25, with steps inside it: retrieval, prompt construction, model call and post-processing.

For a RAG application the useful fields per request are the question, the retrieved passages, the final prompt (or its version id), the model and its version, the response, token counts, latency and any user feedback. That list is the course's suggestion, assembled from what the sources say to monitor. [26][63] Log an identifier you can join to later feedback, as lesson 27 argued for delayed labels.

## Production signals

Microsoft's guide lists the monitoring additions for generative AI: latency, token usage and 429 errors (throttling), content safety, and user feedback such as thumbs up or down, alongside the operational monitoring and drift checks that carry over from MLOps. [26] When models are consumed as a service, infrastructure is not your concern; throughput, quota and throttling become the focus, and tokens are used for billing, throttling and quotas, so the guide advises monitoring quota usage for cost and performance. [26]

Two consequences for alerts. First, a rise in 429 errors is a capacity symptom that users feel, so it deserves a symptom-based alert (lesson 25). Second, a drop in thumbs-up share or a rise in flagged content is a quality signal that may arrive before any labelled evaluation; combine it with the offline eval set to see whether a prompt, model or source change caused it. [26]

## Quality in production

MLflow lists production monitoring as part of its evaluation story: the same quality scorers used before release can be applied to production traces. [63] The overview does not say how often, at what sampling rate or at what cost, so decide those yourself; LLM-judge calls on every request double your model spend.

## Security: what the OWASP list adds

OWASP maintains a Top 10 for LLM applications; the 2025 edition is published on the OWASP GenAI Security Project site. [67] The official page fetched for this course did not contain the list itself, so the ten names below come from a security vendor's page that maps the 2025 list to its tests. [68]

1. LLM01 Prompt Injection
2. LLM02 Sensitive Information Disclosure
3. LLM03 Supply Chain Vulnerabilities
4. LLM04 Data and Model Poisoning
5. LLM05 Improper Output Handling
6. LLM06 Excessive Agency
7. LLM07 System Prompt Leakage
8. LLM08 Vector and Embedding Weaknesses
9. LLM09 Misinformation
10. LLM10 Unbounded Consumption

[68] Only the names were taken from that page; this lesson does not describe what each risk means. Read the official document before building a threat model. [67]

Lesson 30 covered the OWASP Machine Learning Security Top Ten, which concerns classical models; the LLM list is a separate document aimed at applications that include a language model. Two practical points follow from the other sources in this chapter. Retrieved text and user text both enter the prompt, so anything that can write to your index or your inputs is part of the attack surface. And logs that contain prompts and responses contain whatever users typed, so they need the same data-protection controls as the application.

:::low-confidence
The OWASP 2025 list could not be read from the official page; the item names come from a vendor's restatement and no descriptions were read. The logging and attack-surface advice is the course's own reasoning. [67][68]
:::

:::key-takeaways
- Trace each step of an LLM request and attach feedback to the trace. [63]
- Monitor latency, token usage, 429s, content safety and user feedback in addition to MLOps signals. [26]
- Apply your pre-release scorers to production traces, and choose a sampling rate to control cost. [63]
- Use the OWASP LLM Top 10 for threat modelling; read the official document, which this course could not retrieve in full. [67][68]
:::

:::glossary
- **Trace**: a recorded path of one request through every step of an application.
- **Tracing**: automatically collecting those records.
- **Token**: a small chunk of text (roughly a word or less) that models read and are billed by.
- **Latency**: how long something takes.
- **Bottleneck**: the slowest step that limits everything else.
- **Human feedback**: ratings or comments from users or experts attached to a trace.
- **RAG**: giving the model retrieved documents along with the question.
- **Prompt template / version id**: the reusable prompt text with blanks to fill, and its version label.
- **Throttling / 429 error**: the service slowing or refusing requests because you hit a usage limit.
- **Quota**: your allowed amount of usage.
- **Content safety**: filtering harmful or inappropriate output.
- **Thumbs up/down**: simple user feedback.
- **LLM judge**: a model that scores another model's outputs.
- **Sampling rate**: the share of requests you check, to save cost.
- **OWASP**: a nonprofit that publishes lists of common security risks.
- **Prompt injection**: hidden instructions in input that trick the model into misbehaving.
- **Excessive agency**: giving the model too much power to act.
- **Unbounded consumption**: runaway use of compute or tokens, often meaning surprise bills or denial of service.
- **Attack surface**: all the places an attacker could get in.
- **Threat model**: a written list of what could go wrong and who might cause it.
- **Supply chain vulnerability**: risk from third-party models, libraries or data you depend on.
:::
