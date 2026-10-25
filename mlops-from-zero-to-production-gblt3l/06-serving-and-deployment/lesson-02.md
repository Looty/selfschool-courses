---
id: l22
title: Serving on Kubernetes with KServe
quiz: quiz-02.yaml
resources: []
sources: [11, 39, 42]
---
After this lesson you can read an InferenceService manifest, deploy a model with it, and say which KServe features depend on the serverless installation.

## What KServe is

KServe describes itself as a standard platform for running AI models on Kubernetes (software that runs containers across machines), for both classic prediction and generative AI ("inference" means using a trained model). It is an incubating project of the CNCF, the foundation behind Kubernetes. Its features include autoscaling based on request load, scale to zero (shutting down when idle), canary rollouts, explanations of why the model answered as it did, logging of requests with detection of odd inputs and drift, and support for frameworks such as TensorFlow, PyTorch, scikit-learn, XGBoost and ONNX (an interchange format for models). [11]

Two caveats matter for planning. Scale to zero requires the Knative serverless installation rather than a standard Kubernetes deployment, and canary rollouts are not supported on a standard Kubernetes deployment either. [11]

## The InferenceService

The core resource is the `InferenceService`. The first-service tutorial deploys a scikit-learn model with this manifest: [39]

```yaml
apiVersion: "serving.kserve.io/v1beta1"
kind: "InferenceService"
metadata:
  name: "sklearn-iris"
  namespace: kserve-test
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://kfserving-examples/models/sklearn/1.0/model"
      resources:
        requests:
          cpu: "100m"
          memory: "512Mi"
        limits:
          cpu: "1"
          memory: "1Gi"
```

Reading it: `modelFormat` says what kind of model it is, `storageUri` says where the model files are, and `resources` sets how much CPU and memory to reserve (`requests`) and the most it may use (`limits`), like any workload. You supply the model location and format; KServe selects a runtime and creates the serving resources. [39] The tutorial warns not to deploy InferenceServices into namespaces labelled `control-plane`, because doing so skips storage-initializer injection. [39]

## Deploy and call it

```bash
kubectl apply -n kserve-test -f inferenceservice.yaml
kubectl get inferenceservices sklearn-iris -n kserve-test   # READY should be True
```

The `READY` column should show `True`, and the output includes the service URL. [39] The tutorial then sends a v1 prediction request, with a JSON body containing an `instances` array, to `/v1/models/sklearn-iris:predict`, adding a `Host` header when going through the ingress gateway: [39]

```bash
curl -v -H "Host: ${SERVICE_HOSTNAME}" -H "Content-Type: application/json" \
  "http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/sklearn-iris:predict" -d @./iris-input.json
```

The expected response for the two sample rows is `{"predictions": [1, 1]}`. [39] From inside the cluster you can use the service hostname directly. [39]

## From a registry to a service

Lesson 14 left you with `models:/<name>@<alias>` in a registry. KServe reads model files from a `storageUri` such as a cloud storage path. A deployment pipeline therefore needs one step that resolves the alias to the stored model location and writes it into the manifest, and applies the manifest. That step is what makes "move the alias" into "the service changes". Keeping the manifest in Git makes the change reviewable.

## Autoscaling basics

Kubernetes' HorizontalPodAutoscaler (HPA) changes the replica count of a workload to match demand, for example on CPU utilisation. It is a resource plus a controller that, by default, runs about every 15 seconds. Its core formula is `desiredReplicas = ceil(currentReplicas × currentMetricValue / desiredMetricValue)`. [42] KServe's own request-based autoscaling is described in its documentation; the pages read for this course do not describe its configuration. [11]

:::low-confidence
The tutorial examples use a Knative-style hostname and an Istio ingress. Install options change between KServe releases, so confirm the installation guide for the version you deploy. The v2 inference protocol was not covered by the pages read. [11][39]
:::

:::key-takeaways
- An `InferenceService` names a model format and a `storageUri`; KServe creates the serving resources. [39]
- Scale to zero and canary rollouts need the Knative serverless installation. [11]
- A pipeline step must translate a registry alias into the model location in the manifest.
:::

:::glossary
- **Inference**: using a trained model to make predictions.
- **Kubernetes**: software that runs and manages containers across a cluster of machines.
- **KServe**: a tool for serving ML models on Kubernetes.
- **CNCF**: the Cloud Native Computing Foundation, home of Kubernetes and related projects.
- **Knative / serverless**: a layer that starts services on demand and shuts them down when idle.
- **Scale to zero**: running no copies at all when there is no traffic.
- **Canary rollout**: sending a small share of traffic to a new version first.
- **Explainability**: showing why a model gave a particular answer.
- **Drift / outlier detection**: spotting data that has changed or looks unusual.
- **ONNX**: a shared file format for models from different frameworks.
- **InferenceService**: KServe's Kubernetes resource describing a served model.
- **Manifest**: a YAML file that declares what you want Kubernetes to run.
- **Namespace**: a named partition inside a cluster.
- **Predictor**: the part of the service that runs the model.
- **`storageUri`**: where the model files are stored.
- **Ingress gateway**: the entry point that routes outside requests into the cluster.
- **HPA (HorizontalPodAutoscaler)**: Kubernetes' automatic "add or remove copies" controller.
- **Replica / Pod**: a running copy of a service; a Pod is Kubernetes' smallest unit.
- **`kubectl`**: the command-line tool for Kubernetes.
:::
