---
id: l29
title: "Risk and governance: the NIST AI RMF"
quiz: quiz-01.yaml
resources: []
sources: [23, 24, 46]
---
After this lesson you can name the AI RMF's four functions and seven trustworthiness characteristics, and map them to things your pipeline already does.

## What the framework is

NIST (the US National Institute of Standards and Technology) developed the AI Risk Management Framework (AI RMF), with input from the public and private sectors. It is a set of guidelines for spotting and managing the ways AI can harm people, organisations and society. It is voluntary and meant to help build trustworthiness into how AI is designed, built, used and evaluated. AI RMF 1.0 was released on 26 January 2023, and a Generative AI Profile (NIST-AI-600-1) followed on 26 July 2024. The page says AI RMF 1.0 is being revised as part of the White House AI Action Plan. [23]

## The four functions

The AI RMF Core has four functions. [24]

- **Govern** is about who is responsible and how decisions get made: a culture of managing risk, with clear processes, documentation and accountability, tied to the organisation's values. It runs through everything and supports the other three.
- **Map** is about understanding the situation before you build: what the system is for, where it will be used, what could go wrong and what its limits are. It supports an early decision about whether to proceed at all.
- **Measure** is about checking how risky it really is, using numbers, expert judgement or both, and tracking it over time. Systems should be tested before deployment and regularly during operation.
- **Manage** is about acting on what you found: putting resources on the biggest risks, planning responses, recovering from incidents and communicating about them.

The functions are not a strict checklist. After Govern is in place, organisations can apply them in a flexible order, and the process should be iterative. [24]

## Seven characteristics of trustworthy AI

The framework lists characteristics a system should balance. [46]

1. Valid and reliable
2. Safe
3. Secure and resilient
4. Accountable and transparent
5. Explainable and interpretable
6. Privacy-enhanced
7. Fair, with harmful bias managed

"Valid and reliable" is described as a necessary condition of trustworthiness and sits at the base. Accountable and transparent spans the others, since accountability presupposes transparency. The characteristics influence and sometimes conflict with each other: the page gives tradeoffs between interpretability and privacy and between accuracy and interpretability, and says trustworthiness is only as strong as the weakest characteristic. [46]

## Mapping it to what you already do

This is the course's own mapping, not NIST's.

| AI RMF function | MLOps practice from this course |
| --- | --- |
| Govern | Roles for model ownership, approval stages in the release pipeline, documentation (lessons 19, 30) |
| Map | Intended use and limits written down in the model card (lesson 15) |
| Measure | Validation before release, evaluation across slices, monitoring in production (lessons 16, 25 to 27) |
| Manage | Rollback, incident response, retraining decisions (lessons 23, 28) |

The practical point: most of the framework's content is process around the same artifacts you already version, test and monitor. A pipeline that keeps those records produces most of what an audit asks for.

:::low-confidence
The framework is under revision, and the pages read do not cover regulation. Laws that apply to AI systems vary by country and sector and were not researched for this course; check with your legal and compliance people. [23]
:::

:::key-takeaways
- AI RMF is voluntary and has four functions: Govern (cross-cutting), Map, Measure, Manage. [24]
- Seven trustworthiness characteristics are balanced against each other; valid and reliable is the base. [46]
- Much of the RMF's evidence is a by-product of a well-run MLOps pipeline.
:::

:::glossary
- **Governance**: the rules, roles and approvals that decide how something is built and used.
- **NIST**: the US standards agency that wrote the framework.
- **AI RMF (AI Risk Management Framework)**: NIST's voluntary guide to managing AI risk.
- **Trustworthiness**: how much people can reasonably rely on an AI system.
- **Govern / Map / Measure / Manage**: the four activities of the framework: set the rules, understand the context, assess the risk, act on it.
- **Accountable**: someone is answerable for what the system does.
- **Transparent**: it is clear how and why it works as it does.
- **Explainable / interpretable**: a human can understand its answers.
- **Resilient**: keeps working, or recovers, when attacked or stressed.
- **Privacy-enhanced**: protects people's personal data.
- **Harmful bias**: unfair, systematic skew against certain groups.
- **Generative AI Profile**: an add-on to the framework for generative AI.
- **Tradeoff**: gaining one quality (such as accuracy) can cost another (such as interpretability).
- **Audit**: an independent check that records and practice meet the rules.
- **Model card**: a short document saying what a model is for and where it fails.
:::
