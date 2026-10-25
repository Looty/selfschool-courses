---
id: l24
title: "Performance: batching, concurrency and load testing"
quiz: quiz-04.yaml
resources: []
sources: [1, 25, 41, 42]
---
After this lesson you can explain how dynamic batching trades latency for throughput, how concurrency is configured, and how to load-test a model before release.

## The questions performance work answers

Google's CD checks include load-testing the prediction service for queries per second (QPS) and latency. [1] Two numbers describe a service: how many requests it handles per second, and how long one takes. They are in tension, and batching makes the tension visible.

## Dynamic batching

Triton Inference Server (NVIDIA's model server) has a dynamic batcher that groups incoming requests into batches, like a bus waiting a few seconds to fill up instead of leaving with one passenger. This usually raises throughput, because hardware such as GPUs is far more efficient on many inputs at once. It is meant for stateless models (ones that do not remember earlier requests), and each batch goes to the configured model instances. You enable and tune it per model in the model configuration. [41]

- `max_queue_delay_microseconds` lets the batcher hold requests briefly so more can join when it cannot form a maximum or preferred batch. A batch that fills up is sent immediately; if the delay expires, the partial batch is sent anyway, and no request waits longer than the configured value. [41]
- `preferred_batch_size` lists batch sizes the batcher should try to build. The documentation says most models should not set it; it mainly helps TensorRT models with several optimisation profiles. [41]

```
dynamic_batching {
  max_queue_delay_microseconds: 100
}
```

The trade-off is stated plainly. The default sends batches without delay, so latency stays low. More throughput comes from a larger maximum batch size or a nonzero delay, both costing some latency. The recommended approach is to increase the delay until latency reaches your budget, then stop. [41]

Triton applies dynamic batching when `max_batch_size` is above 1 and no scheduler is specified, and the batch dimension must be the first dimension of all inputs and outputs. [25]

## Concurrency: instance groups

The `instance_group` setting controls how many execution instances of a model exist, so that requests can run in parallel. By default Triton creates one instance per available GPU. `count` sets instances per group, `kind` selects GPU or CPU, and `gpus` pins a group to specific devices. [25]

Two knobs, then: how many copies of the model run (instance groups), and how requests are grouped into batches for each (the batcher).

## Scaling out

At the cluster level the HorizontalPodAutoscaler adds Pods when a metric rises above target. Its formula is `desiredReplicas = ceil(currentReplicas × currentMetricValue / desiredMetricValue)`: with 4 replicas at 80% average CPU against a 50% target it asks for ceil(4 × 80/50) = 7. [42] It reads resource metrics from the metrics API, which is usually provided by Metrics Server, installed separately. [42]

:::low-confidence
The HPA page was read only in part (about 100,000 of 132,000 characters), so its stabilisation windows and scaling policies are not covered. Also not covered: how autoscaling behaves for slow-starting or GPU-bound model servers. Test those yourself. [42]
:::

## A load test plan

1. Pick a latency budget from the product need, not from what the service happens to do.
2. Replay realistic inputs at increasing request rates and record latency percentiles and errors.
3. Change one knob at a time: batch delay, instance count, replicas. Keep the results with the model version in your tracker (lesson 13).
4. Re-run when the model, the hardware or the batching settings change.

:::key-takeaways
- Load-test for QPS and latency before release. [1]
- Dynamic batching raises throughput; `max_queue_delay_microseconds` caps the wait, and delay costs latency. [41]
- `instance_group` sets how many model instances run in parallel. [25]
- HPA scales replicas by the ratio of current to desired metric value. [42]
:::

:::glossary
- **QPS (queries per second)**: how many requests a service handles per second.
- **Latency**: how long one request takes.
- **Latency budget**: the longest wait you will accept.
- **Latency percentile (p95, p99)**: the time that 95% (or 99%) of requests beat; shows the slow tail that averages hide.
- **Throughput**: total work done per second.
- **Dynamic batching**: grouping requests into batches on the fly.
- **Triton Inference Server**: NVIDIA's server for running models fast.
- **Stateless model**: a model whose answer depends only on the current input.
- **Queue delay**: how long a request may wait for others to join a batch.
- **TensorRT**: NVIDIA's tool for optimising models to run quickly.
- **Instance group**: how many copies of a model run, and on which devices.
- **GPU / CPU**: graphics processor (fast at parallel maths) and the general processor.
- **HPA**: Kubernetes' controller that adds or removes copies by load.
- **Metrics Server**: an add-on that gives Kubernetes CPU and memory numbers.
- **Load test**: sending realistic traffic to find limits before release.
:::
