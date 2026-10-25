---
id: l11
title: Feature stores and point-in-time joins
quiz: quiz-03.yaml
resources: []
sources: [1, 8, 9, 31, 32]
---
After this lesson you can explain what a feature store is for, name its parts, and say why a point-in-time join prevents leakage.

## What problem it solves

Google lists a feature store as an optional component of an automated pipeline. Think of it as a shared pantry of ready-made model inputs (features): one central place that defines, stores and hands out features for both training and serving, so every team cooks from the same ingredients. It offers an API for high-throughput batch serving and for low-latency real-time serving, which reduces duplicated features and helps avoid training-serving skew. [1]

Feast is an open-source feature store. Its documentation describes the pieces. [8][32]

- **Entity**: the thing features describe, with a join key (the quickstart uses a `driver` with join key `driver_id`). [31]
- **Feature view**: a group of features, usually related to one or more entities, with a data source. The source is used to build training datasets and to materialise values into the online store. [8]
- **Registry**: where feature definitions are stored; features are defined as code in version-controlled repositories. [8][32]
- **Offline store**: persists batch data used to produce training datasets. Feast does not manage it directly but runs queries against it. [32]
- **Online store**: a database holding only the latest feature values for each entity, filled by materialisation or stream ingestion. [32]
- **Feature server**: a REST API server that serves feature values for an entity key and feature reference, designed to scale horizontally. [32]

## The workflow

The quickstart has this order. [31]

```bash
feast apply                                # register definitions, create infrastructure
# training:  store.get_historical_features(entity_df=..., features=[...])
feast materialize-incremental $CURRENT_TIME # load latest values into the online store
# serving:   store.get_online_features(features=[...], entity_rows=[...])
```

`feast apply` scans the repository for definitions, registers them and creates the infrastructure. `get_historical_features` builds training data from the offline store. `materialize-incremental` writes feature values up to a timestamp into the online store. `get_online_features` returns the latest values for given entities for real-time inference. [31] The two retrieval calls read the same definitions, which is how a feature store reduces skew between training and serving. [1][8]

## Point-in-time correctness

Suppose each training row is an event with a timestamp and a label (the known outcome). If you attach features by taking their latest value, a row can receive values recorded after its event, a peek into the future. The model then learns from information it would not have had at prediction time, and offline scores look better than real-world performance. That is data leakage. [9]

Feast prevents it with a point-in-time join: for each entity row it looks backwards from that row's timestamp, never forward, and takes the matching feature values. The look-back is limited by the feature view's TTL, measured from each row's timestamp. In the documentation's example with a 2-hour TTL, a row 11 hours after its feature row gets no feature value, because the match is outside the TTL. [9]

There is a refinement for backfills. By default only the event timestamp is constrained, so a value corrected or backfilled after the row's timestamp can still be returned. Passing `filter_by_created_timestamp=True` also requires the feature's created timestamp to be at or before the row's timestamp. That keeps backfilled values out of training data and better matches what the online store would have served. Some offline stores do not support it yet. [9]

:::low-confidence
A feature store adds a system to run. Google calls it optional, and Feast's offline and online stores are separate backends you provision. Whether it pays off depends on how many models share features. This course did not read a cost comparison. [1][32]
:::

:::key-takeaways
- A feature store standardises feature definitions and serves them in batch for training and with low latency for inference. [1]
- Offline store for training data, online store for the latest values, registry for definitions. [32]
- A point-in-time join looks backwards from each row's timestamp so no future values leak into training data. [9]
:::

:::glossary
- **Feature store**: a shared system that defines, stores and serves model inputs for training and live use.
- **Feast**: a popular open-source feature store.
- **Entity**: the thing the features describe, such as a driver or a customer.
- **Join key**: the column used to match rows between tables, like `driver_id`.
- **Feature view**: a named group of related features plus where their data comes from.
- **Registry**: the catalogue where feature definitions are kept.
- **Offline store**: the big historical data used to build training sets.
- **Online store**: a fast database holding only the latest feature values for live predictions.
- **Materialisation**: copying fresh values from the offline store into the online store.
- **Feature server**: a small web service that returns feature values on request.
- **Batch vs real-time serving**: computing for many records at once versus answering one request in milliseconds.
- **Latency**: how long one request takes to answer.
- **Inference**: using a trained model to make a prediction.
- **Point-in-time join**: attaching to each row only the values that were known at that row's moment.
- **TTL (time to live)**: how old a value may be and still be used.
- **Backfill**: adding or correcting historical data after the fact.
- **Horizontal scaling**: handling more load by adding more copies of a service.
:::
