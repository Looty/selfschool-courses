---
id: l40
title: Managed platform or self-hosted stack?
quiz: quiz-04.yaml
resources: []
sources: [20, 52, 53, 54]
---
After this lesson you can compare a managed ML platform with the open-source stack you built in chapters 3 to 6, and write down the decision criteria for your own team.

## Same jobs, different owners

Every system in this course does the same jobs: version data, track experiments, register models, run pipelines, serve models, watch them. The choice is who builds and operates each part. This lesson lines up the two managed platforms you read about against the open-source tools of earlier chapters. The mapping comes from the pages cited; the judgement at the end is the course's own.

| Job | Open-source tool in this course | SageMaker | Azure ML |
| --- | --- | --- | --- |
| Pipeline as a DAG | DVC stages, Kubeflow Pipelines [20] | Pipelines, steps linked by data dependencies [52] | Machine learning pipelines [54] |
| Skip unchanged work | DVC hashes (lesson 17) | Opt-in step caching with a timeout [53] | Not covered by the page read |
| Model registry | MLflow Model Registry (lesson 14) | RegisterModel into a model package group [52] | Versioned registered models, tags [54] |
| Gate before release | Validation step in CI (lesson 16) | Condition step [52] | Not described as a single feature in the page read |
| Serve and roll out | KServe canary (lesson 23) | Create model and batch Transform step [52] | Online and batch endpoints, traffic percentages [54] |
| Lifecycle events | Your CI triggers (lesson 20) | EventBridge scheduling listed as a topic [52] | Event Grid events [54] |

Blank or "not covered" cells do not mean the feature is missing; they mean the pages used for this course do not say.

## What you give up and gain

A managed platform trades integration for dependence: everything fits together, but you rely on the vendor (this reliance is called lock-in). Reading the pages, the gains are concrete: pipeline, registry, environments, endpoints and lineage live behind one set of APIs and permissions, and events connect them. [52][54] Kubeflow Pipelines, by contrast, is described as a platform for portable, scalable workflows that run in containers on Kubernetes-based systems and can be submitted to any conformant backend, including a cloud's managed one. [20] That portability is what you keep when you write pipelines against the open interface.

The costs are not in these pages: none of the three gives prices, limits or an exit plan. Treat the following as questions to ask, not findings.

## Decision criteria

1. **Where is the data?** Moving data between clouds costs time and money, and jobs run best next to it. If the data already lives in one cloud, that platform has a head start.
2. **Who runs it?** A platform team that already runs Kubernetes can operate KServe, MLflow and a pipeline engine. A small team without that capacity benefits from a managed service.
3. **How regulated is it?** The audit trail of lesson 29 and 30 (who approved, which data, which code) is easier when the platform records lineage for you, and harder when you must assemble it from five tools.
4. **How portable must it be?** If you must run in two clouds or on premises, keep the pipeline definition and the model format (for example MLflow models, lesson 15) portable.
5. **What is the exit cost?** Count what would need rewriting: pipeline definitions, registry metadata and deployment configs.

A common outcome is a mix: managed compute and storage, open formats on top. Whether that works for you depends on your answers, and none of the pages used here supply data to settle it.

:::low-confidence
Google's managed platform is not covered here: the pages fetched for it returned only navigation text, so no claims about it are made. No source compares costs, performance or lock-in across platforms. [52][54]
:::

:::key-takeaways
- Managed and self-hosted stacks do the same jobs; the question is who builds and operates each part. [20][52][54]
- SageMaker and Azure ML each bundle pipelines, a versioned registry, deployment and events. [52][54]
- Decide on data location, operating capacity, regulation, portability and exit cost; no source here settles it for you. [20][52][54]
:::

:::glossary
- **Managed platform**: a cloud service where the vendor runs the infrastructure.
- **Self-hosted stack**: tools you install and operate yourself.
- **Open-source**: software whose code is public and free to use.
- **Lock-in**: being so tied to one vendor that leaving is costly.
- **Portability**: the ability to move your work to another system without rewriting it.
- **Exit cost**: what it would cost to leave a platform.
- **DAG / pipeline**: connected steps run in dependency order.
- **Kubeflow Pipelines**: an open-source pipeline system on Kubernetes.
- **Conformant backend**: any system that follows the same open interface.
- **Model registry**: a versioned catalogue of models.
- **Condition step**: SageMaker's pass/fail gate.
- **Online / batch endpoints**: Azure's live and scheduled prediction services.
- **Lineage**: the trail of which data and code produced a model.
- **Audit trail**: records showing who did what and why.
- **On premises**: running on your own hardware instead of the cloud.
- **Platform team**: the group that runs shared infrastructure for other engineers.
:::
