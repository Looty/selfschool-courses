---
id: l23
title: "Release strategies: shadow, canary, A/B and rollback"
quiz: quiz-03.yaml
resources: []
sources: [1, 12, 14, 40]
---
After this lesson you can choose a release strategy for a new model, run a canary rollout with KServe, and roll back.

## Why not just replace the model

Offline metrics are only a proxy. A new model that wins on a test set can still behave differently on live traffic. Google's online model validation is exactly this: a canary deployment or an A/B test before the model serves everyone. [1] CD4ML lists the deployment capabilities a mature system supports: multiple models, **shadow models**, **competing models** (A/B tests or bandits) and online learning. [14]

| Strategy | What happens | What you learn |
| --- | --- | --- |
| Shadow | The new model receives live requests, but its answers are not used | How it behaves on live inputs, with no user impact |
| Canary | A small share of live traffic is served by the new model | Whether it is healthy and performs acceptably, with limited blast radius (few users hurt if it is bad) |
| A/B | Two models serve different groups at the same time | Which one is better on a business measure |
| Rollback | Traffic goes back to the previous model | Stops the damage while you investigate |

The strategy names come from CD4ML and Google's guide; the one-line descriptions are the usual meaning. [1][14]

## A canary in KServe

KServe's canary rollout sends a share of traffic to a new revision of an InferenceService. It works only in serverless deployment mode. The first revision gets 100% of traffic; when you add a new one, you set `canaryTrafficPercent` to the share the new revision should receive. Unhealthy revisions receive no traffic. [12]

The example updates the manifest from the first-service tutorial by adding the field and pointing `storageUri` at the new model: [40]

```yaml
spec:
  predictor:
    model:
      modelFormat:
        name: sklearn
      storageUri: "gs://kserve-examples/models/sklearn/1.0/model-2"
    canaryTrafficPercent: 10
```

`kubectl get isvc sklearn-iris` then shows the split: revision 1 at 90% and revision 2 at 10%, and two pods, one per revision. [40]

- **Promote:** remove the `canaryTrafficPercent` field and apply again. All traffic goes to revision 2, and revision 1's pods scale down to zero because they no longer receive traffic. [40]
- **Roll back and pin the previous model:** set `canaryTrafficPercent` to `0` on the current model and apply. Revision 1 then receives 100% of traffic and revision 2 none. [40]

## What to watch during a canary

A canary is only useful if you decide in advance what "healthy" means. Use the checks from the earlier lessons: error rate and latency of the service, the distribution of inputs and predictions compared with the old model (chapter 7), and, where labels arrive, the quality metric you validated offline. Set the rule before the rollout: the percentage steps, how long each step lasts and the condition that stops it.

:::low-confidence
The KServe pages read for this course describe the canary field and the example steps. They do not describe automated multi-step promotion beyond noting that the strategy supports configurable steps and can roll back if a step fails. Check the KServe documentation for the exact behaviour of your version. [12][40]
:::

:::key-takeaways
- Online validation is a canary or an A/B test before the model serves everyone. [1]
- In KServe, `canaryTrafficPercent` sets the new revision's share; removing it promotes; `0` rolls back. [40]
- Canary rollouts work in serverless mode only. [12]
- Decide the success and stop conditions before the rollout starts.
:::

:::glossary
- **Release strategy**: the plan for how a new version reaches users.
- **Offline metrics**: scores measured on saved data, not live users.
- **Proxy**: a stand-in measure that only approximates what you really care about.
- **Shadow model**: gets live requests, but its answers are only logged.
- **Canary**: a small share of real traffic goes to the new version.
- **A/B test**: two versions run at once for different groups and are compared.
- **Bandit**: an automatic A/B test that sends more traffic to the winner.
- **Online learning**: a model that keeps updating itself from live data.
- **Blast radius**: how many users a failure would affect.
- **Revision**: one deployed version of a KServe service.
- **`canaryTrafficPercent`**: the share of traffic the new revision gets.
- **Promote**: make the new version take all the traffic.
- **Rollback / pin**: send traffic back to the old version and keep it there.
- **Serverless mode**: the Knative-based KServe installation that supports canaries.
- **Latency / error rate**: how slow requests are and how many fail.
:::
