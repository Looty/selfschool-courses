---
id: l39
title: "Azure Machine Learning: registry, environments and endpoints"
quiz: quiz-03.yaml
resources: []
sources: [54]
---
After this lesson you can list the MLOps capabilities Azure Machine Learning offers, describe how it registers and deploys a model, and read its vendor claims critically.

## The capability list

Azure Machine Learning is Microsoft's managed ML platform, the counterpart to SageMaker. Microsoft's article says it applies DevOps ideas to the ML lifecycle and lists seven capabilities. [54]

- Reproducible machine learning pipelines for data preparation, training and scoring.
- Reusable software environments for training and deployment.
- Register, package and deploy models from anywhere, with the metadata needed to use them.
- Lineage data for governance: who published models, why changes were made, when models were deployed or used.
- Notifications and alerts on lifecycle events such as experiment completion, model registration, deployment and data drift.
- Monitoring of operational and ML issues.
- End-to-end automation using pipelines and Azure Pipelines to test, update and roll out models.

Set against lesson 4's maturity ladders, this is a checklist of what a managed platform bundles.

## Environments and the registry

Environments track and reproduce the pip and conda dependencies of a project and can be used for training and deployment, so builds are reproducible without manual configuration. [54]

The registry stores and versions models in a workspace. A registered model is a logical container for one or more files. Models are identified by name and version, and registering under an existing name increments the version. Tags can be attached and used for search. You can also register models trained outside Azure Machine Learning. One safety rule: you cannot delete a registered model that is used in an active deployment. [54] Compare lesson 14: versions are immutable numbers, and the platform protects what production uses.

## Packaging and deployment

A model must be packaged into a Docker image to deploy; usually this happens automatically during deployment. The page advises deploying locally first to troubleshoot and debug. [54]

A deployment as an endpoint needs: the model, an entry (scoring) script that accepts requests, scores them and returns a response, an environment with the dependencies, and any other assets, plus the target configuration such as VM family, memory and cores. When you deploy an MLflow model you need neither an entry script nor an environment. [54] That is a practical payoff of the MLflow model format from lesson 15: the packaging contract is already inside the model.

Two endpoint types exist. **Batch endpoints** support batch scoring. **Online endpoints** serve real-time scoring and can run on a local environment, as managed online endpoints, or on Azure Kubernetes Service. [54] Lesson 21's batch versus online distinction appears here as two product types.

## Controlled rollout

For online endpoints the page describes creating multiple deployments, A/B testing by routing traffic between deployments of an endpoint, and switching deployments by updating traffic percentages in the endpoint configuration. [54] This is the same pattern as KServe's `canaryTrafficPercent` in lesson 23: the endpoint is the stable address, deployments are versions, and traffic weights move.

## Events and automation

Azure Machine Learning publishes key events to Azure Event Grid so you can notify and automate on model registration, deployment, data drift and training job events. A typical flow uses Git and Azure Pipelines so a change checked into the repository starts a training job, with a follow-on pipeline that can deploy the model as a web service. [54]

## Read vendor claims critically

The article says converting a model to ONNX "typically" can double performance. [54] No benchmark, model or hardware is given, so treat it as a reason to try the conversion and measure, not as an expectation. This is the habit lesson 24 taught for performance: load-test your own model.

:::low-confidence
The article is a conceptual overview. It does not describe pricing, limits, quota, or how its monitoring compares with open-source tools. [54]
:::

:::key-takeaways
- Azure ML bundles pipelines, environments, a versioned registry, endpoints, lineage metadata and events. [54]
- MLflow models can be deployed without an entry script or environment. [54]
- Online endpoints support multiple deployments and traffic percentages for A/B and safe rollout. [54]
- Measure vendor performance claims such as "ONNX can double performance" on your own model. [54]
:::

:::glossary
- **Azure Machine Learning (Azure ML)**: Microsoft's managed ML platform.
- **Workspace**: the top-level container in Azure ML holding your models, data and runs.
- **Environment (Azure ML)**: a saved list of software dependencies, so runs are reproducible.
- **pip / conda**: tools that install Python libraries.
- **Registered model**: a named, versioned model saved in the registry.
- **Lineage**: the record of who published what, when and why.
- **Docker image**: a packaged, ready-to-run bundle of an app and its dependencies.
- **Entry (scoring) script**: the code that receives a request, runs the model and returns the answer.
- **VM family**: the type of virtual machine, such as CPU-heavy or GPU.
- **Endpoint**: a stable address that serves a model; each endpoint can hold several deployments.
- **Batch endpoint / online endpoint**: for scoring many records on a schedule / answering live requests.
- **Managed online endpoint**: Azure runs and scales the servers for you.
- **AKS (Azure Kubernetes Service)**: Azure's managed Kubernetes.
- **Deployment (Azure ML)**: one version of a model running behind an endpoint.
- **Traffic percentage**: the share of requests each deployment receives.
- **Event Grid**: Azure's service for publishing and reacting to events.
- **Azure Pipelines**: Microsoft's CI/CD service.
- **ONNX**: a shared model file format that can run faster in some runtimes.
:::
