---
id: l25
title: "What to monitor: system, data and model"
quiz: quiz-01.yaml
resources: []
sources: [1, 2, 14, 43, 45]
---
After this lesson you can describe the three layers of ML monitoring, apply the golden signals to a model service, and write alerts that are worth waking someone for.

## Three layers

A model in production can fail in three different places, and one layer's dashboard will not show another's failure.

1. **The service.** Is it up, fast and not failing? This is ordinary monitoring, and you already know it.
2. **The data.** Are the inputs what the model expects? Google's guide asks to track summary statistics of the data and to monitor online performance, because data profiles change. [1]
3. **The model.** Is it still predicting well? Google lists monitoring the model's predictive performance as the last step of the lifecycle, and it is what triggers a new iteration. [1]

## The service layer: golden signals

The SRE book's four golden signals apply to a prediction service without change. [43]

- **Latency**: time to serve a request. Track successful and failed requests separately, since a fast error can mask a problem.
- **Traffic**: demand on the system, for example requests per second.
- **Errors**: the rate of failed requests. Failures can be explicit, implicit (a 200 response with wrong content) or defined by policy (slower than a committed threshold).
- **Saturation**: how full the service is, focused on its most constrained resource, which for a model service may be a GPU.

Implicit errors deserve special attention for ML. A model can return a well-formed 200 response with a bad prediction, which is why the other two layers exist.

Prometheus is a common way to collect this layer. It stores metrics as time series (a number measured over and over, like requests per second), each named and tagged with key-value labels; it asks your services for their numbers over HTTP ("scraping"), lets you query them with its language PromQL, and evaluates alerting rules. [45]

## The data layer

The technical-debt paper asks for live monitoring because tests cannot cover a changing world. Its suggestions include: [2]

- **Prediction bias**: the mix of answers the model gives should match the mix of real outcomes (if 5% of cases are fraud, it should not flag 40%). This is necessary but not sufficient, since a useless model that always guesses the average can pass it. Check it per group (slice) and alert on it.
- **Action limits**: sensible caps on real-world actions the model can trigger (for example, the most refunds per hour), loose enough to avoid false alarms, with an alert when hit.
- **Upstream producers**: the systems that feed you data. Monitor them, hold them to service-level objectives (promises about quality) that take your needs into account, and pass their alerts along.

Lesson 26 covers detecting distribution changes in the inputs.

## The model layer, and logging

Quality metrics need labels, and labels often arrive late (lesson 27). In the meantime, CD4ML recommends logging a model's inputs, outputs and decisions, so you can detect skew between training and serving and close the feedback loop when labels arrive. [14]

## Alerts worth having

The SRE chapter's guidance carries over. Pages should be urgent, actionable and tied to user-visible symptoms. It suggests asking whether an alert catches a condition that is otherwise undetected, whether you could safely ignore it, and whether you can act on it. Causes are mainly debugging aids; symptoms are what to page on. [43] Apply it by layer: page on user-visible symptoms (errors, latency, a prediction distribution that has collapsed), and send data and model drift to a ticket queue unless they reach a limit you decided in advance.

:::key-takeaways
- Monitor three layers: the service, the data and the model. [1]
- The golden signals (latency, traffic, errors, saturation) apply to model services; implicit errors are the ML risk. [43]
- Prediction bias, action limits and upstream producers are monitoring suggestions from the technical-debt paper. [2]
- Page on symptoms; use dashboards and tickets for causes. [43]
:::

:::glossary
- **Monitoring**: continuously measuring a running system and alerting when something looks wrong.
- **Golden signals**: the four basics to watch: latency, traffic, errors, saturation.
- **Latency / traffic / errors / saturation**: how slow, how busy, how often it fails, how close to full.
- **Implicit error**: a "successful" response that is actually wrong.
- **SRE (site reliability engineering)**: Google's discipline of running services reliably.
- **Prometheus / PromQL**: a popular metrics system and its query language.
- **Time series**: a measurement tracked over time.
- **Label (in Prometheus)**: a key-value tag on a metric, such as `model="v3"`.
- **Prediction bias**: the model's answers are skewed compared with reality.
- **Null model**: a trivial model that ignores the input, such as "always predict the average".
- **Slice**: a subgroup of data.
- **Action limit**: a cap on what an automated decision may do.
- **Upstream producer**: a system that supplies your input data.
- **SLO (service-level objective)**: a target level of service quality.
- **Page / paging**: alert a person immediately, even at night.
- **Ground truth / labels**: the real outcomes.
:::
