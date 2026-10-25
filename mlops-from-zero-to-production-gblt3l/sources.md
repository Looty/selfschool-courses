# Sources

Numbers are stable: lessons and questions cite them as `[n]`. Never renumber; append new sources at the end.
Only list sources that were actually read during research. Never invent a URL.

1. [MLOps: Continuous delivery and automation pipelines in machine learning](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning) · Google Cloud Architecture Center · accessed 2026-10-22 · reliability: high
   - Notes: definitions of MLOps, CI, CD, CT; maturity levels 0, 1, 2; pipeline components, triggers, CI/CD stages. The "MLOps for generative AI" section was not covered by the fetched text.
2. [Hidden Technical Debt in Machine Learning Systems](https://proceedings.neurips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf) · Sculley et al., NIPS 2015 · accessed 2026-10-22 · reliability: high
   - Notes: the PDF could not be parsed, so the body was read from a plain-text copy of the same paper (object.cloud.sdsc.edu, NeurIPS/2015). Only the abstract was verified against the NeurIPS PDF itself.
3. [The ML Test Score: A Rubric for ML Production Readiness and Technical Debt Reduction](https://research.google/pubs/pub46555/) · Nielsen, Salib, Sculley; IEEE Big Data 2017 · accessed 2026-10-22 · reliability: high
   - Notes: only the abstract page was read (28 tests and monitoring needs). The test categories and scoring method were not read.
4. [MLflow Model Registry](https://mlflow.org/docs/latest/ml/model-registry) · MLflow project · accessed 2026-10-22 · reliability: high
   - Notes: registered models, versions, aliases, tags, lineage, registering and loading models. Status of stages not stated on the page.
5. [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking) · MLflow project · accessed 2026-10-22 · reliability: high
   - Notes: runs, experiments, logging, autologging, backend and artifact stores, tracking server, UI.
6. [Defining DVC Pipelines](https://doc.dvc.org/user-guide/pipelines/defining-pipelines) · DVC (Iterative) · accessed 2026-10-22 · reliability: high
   - Notes: dvc.yaml stages, deps, params, outs, metrics, DAG, what invalidates a stage. dvc.lock and dvc repro covered only briefly.
7. [Data Versioning (DVC Get Started)](https://doc.dvc.org/start/data-management/data-versioning) · DVC (Iterative) · accessed 2026-10-22 · reliability: high
   - Notes: dvc add, .dvc files, remotes, push/pull, checkout.
8. [Feast concepts overview](https://docs.feast.dev/getting-started/concepts/overview) · Feast project · accessed 2026-10-22 · reliability: high
   - Notes: project, feature view, entity, materialization, registry, feature server, retrieval APIs. Offline/online store definitions are not on this page.
9. [Feast: point-in-time joins](https://docs.feast.dev/getting-started/concepts/point-in-time-joins) · Feast project · accessed 2026-10-22 · reliability: high
   - Notes: data leakage, TTL, created-timestamp filter.
10. [Feast architecture overview](https://docs.feast.dev/getting-started/architecture/overview) · Feast project · accessed 2026-10-22 · reliability: medium
    - Notes: only a partial overview came back (push model, transformations, RBAC); the page text contained a line telling the reader to send a query request, which was ignored.
11. [KServe README](https://raw.githubusercontent.com/kserve/kserve/master/README.md) · KServe project (CNCF) · accessed 2026-10-22 · reliability: high
    - Notes: what KServe is, features, serverless-only caveats for scale to zero and canary. No YAML example on the page.
12. [KServe canary rollout](https://kserve.github.io/website/docs/model-serving/predictive-inference/rollout-strategies/canary) · KServe project · accessed 2026-10-22 · reliability: high
    - Notes: canaryTrafficPercent, serverless mode only, promotion and rollback. No YAML example on the fetched page.
13. [Rules of Machine Learning: Best Practices for ML Engineering](https://developers.google.com/machine-learning/guides/rules-of-ml) · Martin Zinkevich, Google · accessed 2026-10-22 · reliability: high
    - Notes: rules 1, 4, 8-11, 29-37 as returned by the fetch.
14. [Continuous Delivery for Machine Learning](https://martinfowler.com/articles/cd4ml.html) · Sato, Wider, Windheuser; martinfowler.com · accessed 2026-10-22 · reliability: high
    - Notes: code, model and data as the three axes of change; technical components of CD4ML.
15. [MLOps maturity model](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/mlops-maturity-model) · Microsoft Azure Architecture Center · accessed 2026-10-22 · reliability: high
    - Notes: five levels (0-4). Written around Azure Machine Learning; the levels themselves are tool-neutral.
16. [Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993) · Mitchell et al., 2018 · accessed 2026-10-22 · reliability: high
    - Notes: abstract page only; the card template was not read.
17. [Overfitting (Machine Learning Crash Course)](https://developers.google.com/machine-learning/crash-course/overfitting/overfitting) · Google for Developers · accessed 2026-10-22 · reliability: high
    - Notes: overfitting, generalization, loss curves, 70/15/15 split example.
18. [Dividing the original dataset (Machine Learning Crash Course)](https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets) · Google for Developers · accessed 2026-10-22 · reliability: high
    - Notes: training, validation and test sets; pitfalls. Time-based splits are not covered.
19. [TensorFlow Data Validation](https://www.tensorflow.org/tfx/guide/tfdv) · TensorFlow / TFX · accessed 2026-10-22 · reliability: high
    - Notes: statistics, schema inference, anomalies, skew, drift (L-infinity and Jensen-Shannon).
20. [Kubeflow Pipelines overview](https://www.kubeflow.org/docs/components/pipelines/overview/) · Kubeflow project · accessed 2026-10-22 · reliability: high
    - Notes: pipelines, components, IR YAML, backends. SDK decorators are not on this page.
21. [Evidently introduction](https://docs.evidentlyai.com/introduction) · Evidently AI · accessed 2026-10-22 · reliability: high
    - Notes: what Evidently is, library and platform.
22. [Evidently: data drift detection](https://docs.evidentlyai.com/metrics/explainer_drift) · Evidently AI · accessed 2026-10-22 · reliability: high
    - Notes: default statistical tests and thresholds by column type and reference size; dataset-level drift.
23. [AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) · NIST · accessed 2026-10-22 · reliability: high
    - Notes: AI RMF 1.0 released 2023-01-26; generative AI profile 2024-07-26; framework under revision.
24. [AI RMF Core](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) · NIST AIRC · accessed 2026-10-22 · reliability: high
    - Notes: the Govern, Map, Measure and Manage functions.
25. [Triton model configuration](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/model_configuration.html) · NVIDIA · accessed 2026-10-22 · reliability: high
    - Notes: dynamic batching and instance groups, model repository. Batcher tuning parameters are not on this page.
26. [Generative AI operations for organizations with MLOps investments](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/genaiops-for-mlops) · Microsoft Azure Architecture Center · accessed 2026-10-22 · reliability: high
    - Notes: GenAIOps versus MLOps: fine-tuning, prompting, RAG; inner and outer loop; monitoring, gateway. Examples use Azure services.
27. [Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html) · scikit-learn · accessed 2026-10-22 · reliability: high
    - Notes: inconsistent preprocessing, data leakage, pipelines, controlling randomness with random_state.
28. [Linear regression: Loss (Machine Learning Crash Course)](https://developers.google.com/machine-learning/crash-course/linear-regression/loss) · Google for Developers · accessed 2026-10-22 · reliability: high
    - Notes: loss, L1, L2, MAE, MSE, RMSE. The page does not explain how training lowers loss.
29. [Classification: Accuracy, recall, precision and related metrics (Machine Learning Crash Course)](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall) · Google for Developers · accessed 2026-10-22 · reliability: high
    - Notes: definitions and formulas, class imbalance, the threshold trade-off.
30. [Reproducibility (PyTorch notes, 2.14)](https://docs.pytorch.org/docs/2.14/notes/randomness.html) · PyTorch · accessed 2026-10-22 · reliability: high
    - Notes: no guarantee across releases, commits or platforms; seeding; deterministic algorithms; cuDNN; DataLoader. The stable URL redirects to the 2.14 page. CUBLAS_WORKSPACE_CONFIG is not mentioned on the page.
31. [Feast quickstart](https://docs.feast.dev/getting-started/quickstart) · Feast project · accessed 2026-10-22 · reliability: high
    - Notes: feature_store.yaml, entities, feature views, feast apply, get_historical_features, materialize, get_online_features, feature services.
32. [Feast components overview](https://docs.feast.dev/getting-started/components/overview) · Feast project · accessed 2026-10-22 · reliability: high
    - Notes: registry, offline store, online store, feature server, compute engine. "Provider" is not described on this page.
33. [MLflow Models](https://mlflow.org/docs/latest/ml/model) · MLflow project · accessed 2026-10-22 · reliability: high
    - Notes: the MLmodel file, flavors, python_function, signature, input example, environment files, serving with `mlflow models serve`, validating with `mlflow.models.predict`.
34. [Create components (Kubeflow Pipelines)](https://www.kubeflow.org/docs/components/pipelines/user-guides/components/) · Kubeflow project · accessed 2026-10-22 · reliability: high
    - Notes: index page: component = remote function definition; Python, container and importer components.
35. [Lightweight Python components (Kubeflow Pipelines)](https://www.kubeflow.org/docs/components/pipelines/user-guides/components/lightweight-python-components/) · Kubeflow project · accessed 2026-10-22 · reliability: high
    - Notes: @dsl.component, type annotations, packages_to_install, the hermetic restriction and the default base image.
36. [Compose components into pipelines (Kubeflow Pipelines)](https://www.kubeflow.org/docs/components/pipelines/user-guides/components/compose-components-into-pipelines/) · Kubeflow project · accessed 2026-10-22 · reliability: high
    - Notes: @dsl.pipeline example, task outputs, parallel tasks, .after(). Compiling and running a pipeline are on other pages that were not read.
37. [dvc repro](https://doc.dvc.org/command-reference/repro) · DVC (Iterative) · accessed 2026-10-22 · reliability: high
    - Notes: what repro does, options --force, --single-item, --pull, run cache. The detailed dvc.lock comparison is not explained on the page.
38. [CML with GitHub Actions](https://cml.dev/doc/start/github) · CML (Iterative) · accessed 2026-10-22 · reliability: high
    - Notes: example workflow that trains a model and posts a report to a pull request with `cml comment create`; setup-cml action and `cml runner`.
39. [First InferenceService (KServe)](https://kserve.github.io/website/docs/getting-started/predictive-first-isvc) · KServe project · accessed 2026-10-22 · reliability: high
    - Notes: the sklearn-iris InferenceService YAML, kubectl commands, status, v1 REST request. v2 protocol not shown on the page.
40. [Canary rollout example (KServe)](https://kserve.github.io/website/docs/model-serving/predictive-inference/rollout-strategies/canary-example) · KServe project · accessed 2026-10-22 · reliability: high
    - Notes: canaryTrafficPercent, traffic split, promotion by removing the field, rollback by setting it to 0.
41. [Dynamic batcher (Triton Inference Server)](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/batcher.html) · NVIDIA · accessed 2026-10-22 · reliability: high
    - Notes: dynamic batching, preferred_batch_size, max_queue_delay_microseconds, latency versus throughput.
42. [Horizontal Pod Autoscaling](https://kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/) · Kubernetes · accessed 2026-10-22 · reliability: high
    - Notes: HPA behaviour, control loop, metric types, the replica formula. The last part of the page (about 32,000 characters, including stabilization windows and scaling policies) was not read.
43. [Monitoring Distributed Systems (Site Reliability Engineering book)](https://sre.google/sre-book/monitoring-distributed-systems/) · Google SRE · accessed 2026-10-22 · reliability: high
    - Notes: the four golden signals, symptoms versus causes, what makes a good alert, white-box versus black-box monitoring. General service monitoring, not ML-specific.
44. [What is concept drift in ML, and how to detect and address it](https://evidentlyai.com/ml-in-production/concept-drift) · Evidently AI (ML in Production guide, updated 2025-01-15) · accessed 2026-10-22 · reliability: medium
    - Notes: vendor guide. Concept drift versus data drift, gradual, sudden and recurring drift, proxy signals when labels are delayed, actions to take. The page does not discuss incremental drift.
45. [Prometheus overview](https://prometheus.io/docs/introduction/overview/) · Prometheus (CNCF) · accessed 2026-10-22 · reliability: high
    - Notes: metrics as time series with labels, PromQL, pull model, alerting, components.
46. [AI RMF: characteristics of trustworthy AI systems](https://airc.nist.gov/airmf-resources/airmf/3-sec-characteristics/) · NIST AIRC · accessed 2026-10-22 · reliability: high
    - Notes: seven characteristics and how they relate and trade off.
47. [OWASP Machine Learning Security Top Ten](https://owasp.org/www-project-machine-learning-security-top-ten/) · OWASP · accessed 2026-10-22 · reliability: medium
    - Notes: the project page says the work is in draft and changes frequently. It did not list the ten items; the names ML01 Input Manipulation Attack and ML02 Data Poisoning Attack come from a search result for this page. Secondary descriptions of the two were not used.
48. [Architecture overview (Apache Airflow 3.3.2)](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html) · Apache Airflow · accessed 2026-10-22 · reliability: high
    - Notes: components (scheduler, Dag processor, API server, metadata database, workers, triggerer), DAG run flow, deployment patterns, recommendations. No sizing numbers or executor tuning.
49. [Dags (Apache Airflow 3.3.2)](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html) · Apache Airflow · accessed 2026-10-22 · reliability: high
    - Notes: declaring a Dag, `>>` dependencies, schedule, Dag runs and logical date, trigger rules, branching. The page has no idempotency section and does not explain `catchup`.
50. [XComs (Apache Airflow)](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html) · Apache Airflow · accessed 2026-10-22 · reliability: high
    - Notes: XCom purpose, size caution, push and pull, the Airflow 3 change to `xcom_pull`, object-storage and custom backends.
51. [Tasks (Apache Airflow)](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html) · Apache Airflow · accessed 2026-10-22 · reliability: high
    - Notes: operators, sensors and `@task`, task states, retries, timeouts, special exceptions, heartbeat timeouts. Deferrable and poke sensors are not explained on the page.
52. [Pipelines overview (Amazon SageMaker AI)](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-overview.html) · AWS · accessed 2026-10-22 · reliability: high
    - Notes: a pipeline is a DAG defined by data dependencies; example with Processing, Training, Condition, RegisterModel, CreateModel and Transform steps; list of topics (caching, retries, ClarifyCheck/QualityCheck, scheduling).
53. [Caching pipeline steps (Amazon SageMaker AI)](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines-caching.html) · AWS · accessed 2026-10-22 · reliability: high
    - Notes: opt-in step caching with a timeout, successful runs only, scoped to one pipeline, supported step types. The per-step cache key list is on a page that was not read.
54. [MLOps model management (Azure Machine Learning)](https://learn.microsoft.com/en-us/azure/machine-learning/concept-model-management-and-deployment) · Microsoft · accessed 2026-10-22 · reliability: high
    - Notes: capabilities, environments, model registry, endpoints (batch and online), controlled rollout, lineage metadata, Event Grid events, Azure Pipelines. Contains a vendor claim that ONNX conversion "typically" doubles performance, with no measurement shown.
55. [Schedule GPUs (Kubernetes)](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/) · Kubernetes · accessed 2026-10-22 · reliability: high
    - Notes: device plugins, `nvidia.com/gpu` style resources, limits-only rule, node labels, Node Feature Discovery, administrator responsibilities.
56. [Jobs (Kubernetes)](https://kubernetes.io/docs/concepts/workloads/controllers/job/) · Kubernetes · accessed 2026-10-22 · reliability: high
    - Notes: run-to-completion Jobs, completions and parallelism, Indexed mode, backoffLimit default and back-off delay, suspend. The sections on `ttlSecondsAfterFinished`, `activeDeadlineSeconds` and pod failure policy were not read.
57. [Kueue overview](https://kueue.sigs.k8s.io/docs/overview/) · Kubernetes SIGs · accessed 2026-10-22 · reliability: high
    - Notes: job queueing and quota system, what it leaves to other components, supported job types. High-level; mechanics are on other pages.
58. [ClusterQueue (Kueue)](https://kueue.sigs.k8s.io/docs/concepts/cluster_queue/) · Kubernetes SIGs · accessed 2026-10-22 · reliability: high
    - Notes: resource groups and flavors, nominalQuota, borrowingLimit, lendingLimit, cohorts, queueing strategies, preemption fields, caveats.
59. [Ray on Kubernetes (KubeRay)](https://docs.ray.io/en/latest/cluster/kubernetes/index.html) · Ray project · accessed 2026-10-22 · reliability: high
    - Notes: KubeRay operator, head and worker Pods, the three custom resources (named but not explained), optional autoscaling. The page also promotes a commercial service.
60. [RayJob quickstart (KubeRay)](https://docs.ray.io/en/latest/cluster/kubernetes/getting-started/rayjob-quick-start.html) · Ray project · accessed 2026-10-22 · reliability: high
    - Notes: RayJob creates a cluster and submits a job, submitter modes, `shutdownAfterJobFinishes` and TTL, Kueue and `suspend`. Manifests are not shown in full; some options are alpha or deprecated.
61. [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) · Lewis et al., NeurIPS 2020 (arXiv v4) · accessed 2026-10-22 · reliability: high
    - Notes: abstract only: parametric versus non-parametric memory, what RAG combines, claimed results on open-domain QA. The paper body was not read.
62. [Define success criteria and build evaluations (Claude documentation)](https://platform.claude.com/docs/en/docs/test-and-evaluate/develop-tests) · Anthropic · accessed 2026-10-22 · reliability: high
    - Notes: criteria should be specific, measurable, achievable, relevant; eval design principles; code-based, similarity, and LLM-based grading examples. Vendor documentation; the last third of the page was not read.
63. [GenAI evaluation and monitoring (MLflow)](https://mlflow.org/docs/latest/genai/eval-monitor/) · MLflow project · accessed 2026-10-22 · reliability: high
    - Notes: evaluation datasets, scorers, `mlflow.genai.evaluate`, tracing and production monitoring at overview level. Does not discuss how reliable LLM judges are.
64. [MLflow Tracking quickstart](https://mlflow.org/docs/latest/ml/tracking/quickstart/) · MLflow project · accessed 2026-10-22 · reliability: high
    - Notes: autologging, `mlflow server --port 5000`, manual `start_run` logging, loading with `pyfunc`.
65. [Get started with DVC](https://doc.dvc.org/start) · DVC (Iterative) · accessed 2026-10-22 · reliability: high
    - Notes: install, `dvc init`, `dvc add`, remotes, `dvc push` and `dvc pull`, switching versions with `git checkout` and `dvc checkout`.
66. [Evidently quickstart (ML)](https://docs.evidentlyai.com/quickstart_ml) · Evidently AI · accessed 2026-10-22 · reliability: high
    - Notes: `Report` with `DataDriftPreset` and `DataSummaryPreset`, reference versus current data, JSON and HTML export. API as of the fetched page; it differs from older Evidently versions.
67. [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/) · OWASP GenAI Security Project · accessed 2026-10-22 · reliability: medium
    - Notes: the official page fetched did not contain the list of ten risks; the names LLM01 Prompt Injection and LLM02 Sensitive Information Disclosure come from a web search whose results restated the list. Descriptions of the risks were not read from the official text. See source 68 for the list.
68. [OWASP LLM Top 10 (red teaming guide)](https://promptfoo.dev/docs/red-team/owasp-llm-top-10/) · Promptfoo (security testing vendor) · accessed 2026-10-22 · reliability: medium
    - Notes: third-party page that maps the OWASP Top 10 for LLM Applications 2025 to its own testing tool; used only for the ten item IDs and names (LLM01 Prompt Injection to LLM10 Unbounded Consumption). Descriptions of the risks were not taken from it.
