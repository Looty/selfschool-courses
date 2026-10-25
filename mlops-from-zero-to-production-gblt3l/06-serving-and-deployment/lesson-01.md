---
id: l21
title: "Serving patterns: batch, online and embedded"
quiz: quiz-01.yaml
resources: []
sources: [1, 14, 33]
---
After this lesson you can choose between batch, online and embedded serving for a use case, and name what each costs operationally.

## Three ways to put a model to work

"Serving" just means making the trained model available so it can answer questions. Google's guide lists three forms: a small standalone service (a microservice) with a REST API that answers one request at a time ("online"), a model embedded in a phone or other edge device, and a batch prediction system that scores lots of records at once. [1] CD4ML frames the same choice for a web application as embedding the model in the application, deploying it as a separate service, or publishing its output as data. [14]

| Pattern | How predictions are produced | Typical fit |
| --- | --- | --- |
| Online | One request in, one answer back from a running service | Interactive features where the answer is needed now |
| Batch | A scheduled job scores a whole dataset and stores the results | Predictions that can be computed ahead of time and read later |
| Embedded | The model ships inside the application on a device | Edge or mobile cases |

The "typical fit" column is guidance, not a quotation. Pick by asking when the answer is needed, how many predictions, and where the input lives.

## What each costs

**Online** makes the model a service you operate: it has an API, availability, latency and scaling needs, and must be validated and rolled out like any service (lessons 22 to 24). Google's CD checks apply: verify the model is compatible with the target infrastructure, test the API with expected inputs and load-test for queries per second and latency. [1]

**Batch** moves the work into a scheduled pipeline. The operational concerns are data validation before the run and the freshness of the stored predictions. Google's CD list includes validating the data used for retraining or batch prediction. [1]

**Embedded** distributes the model with the application, so updating it means releasing the application, and the model must fit the device. The sources read for this course do not cover embedded deployment in depth.

## Packaging that works for more than one pattern

A model packaged in a standard format can be used by several patterns. An MLflow model is a directory with the artifact plus an `MLmodel` file, so that tools such as a REST server, a Spark batch job or a deployment target can all use it. [33] Concretely, `mlflow models serve -m <model_uri>` starts a REST server, and `mlflow.pyfunc.spark_udf(spark, model_uri)` turns the model into a Spark UDF for distributed scoring. [33]

A useful design habit: keep the feature computation shared between the batch and online paths (lesson 12), otherwise a model used in both places gives different answers in each.

:::low-confidence
The latency, cost and freshness trade-offs in the table are general engineering guidance rather than claims from the sources. The sources establish the three forms and the checks that apply to them. [1][14]
:::

:::key-takeaways
- Three serving forms: online REST service, embedded model, batch prediction. [1]
- Online makes the model a service to operate; batch needs data validation and a schedule. [1]
- A standard model package lets one model serve more than one pattern. [33]
:::

:::glossary
- **Serving**: running a trained model so it can answer prediction requests.
- **Online (real-time) serving**: one request in, one answer back, right now.
- **Batch serving**: a scheduled job scores a big set of records and saves the results.
- **Embedded model**: the model lives inside an app on a device.
- **Edge device**: a phone, sensor or gadget at the "edge" rather than in a data centre.
- **Microservice**: a small, separately running service that does one job.
- **REST API**: a standard way for programs to call a service over HTTP.
- **Latency**: how long one request takes.
- **Throughput / QPS**: how many requests per second are handled.
- **Scaling**: adding capacity to cope with more load.
- **Freshness**: how up to date stored predictions are.
- **Spark**: a tool for processing huge datasets across many machines.
- **UDF (user-defined function)**: your own function plugged into a data tool, here the model.
- **Distributed scoring**: spreading predictions over many machines.
- **Package format**: a standard way of bundling a model so tools can run it.
:::
