---
id: l14
title: Model registry, versions and aliases
quiz: quiz-02.yaml
resources: []
sources: [1, 4, 14]
---
After this lesson you can register a model, load it by version or alias, and describe how an alias lets you promote or roll back without changing serving code.

## What a registry is for

Google's Level 2 components include a model registry as the place trained models are stored and handed to the deployment steps. [1] CD4ML asks for the same thing in other words: models must be versioned and managed because code, model and data all change. [14] A registry is a library catalogue for models: every trained model gets a name, a version number and an official place that deployment can point to, instead of "the file on someone's laptop".

## The MLflow registry model

MLflow's registry has these concepts. [4]

- **Model**: created by logging with a flavor's `log_model()`; a logged model can then be registered.
- **Registered model**: a named entry holding versions, aliases, tags and metadata.
- **Model version**: the first registration under a name is version 1, and each later registration under that name increments the number.
- **Model URI**: refers to a registered model as `models:/<name>/<version>`.
- **Alias**: a mutable, named pointer to a version. For example `champion` can point to version 1 of `MyModel`, referenced as `models:/MyModel@champion`.
- **Tags**: key-value labels on models or versions, such as `validation_status:approved`.
- **Lineage**: each version links to the run, logged model or notebook that produced it.

## Registering and loading

Register at log time, or register a model you already logged: [4]

```python
mlflow.<flavor>.log_model(..., registered_model_name="<NAME>")
mlflow.register_model(model_uri="<URI>", name="<NAME>")
```

Load by version or by alias with the same pattern: [4]

```python
mlflow.<flavor>.load_model("models:/<NAME>/<VERSION>")
mlflow.<flavor>.load_model("models:/<NAME>@<ALIAS>")
```

## Aliases as a deployment mechanism

The page presents aliases as the mechanism for deployment workflows: you can reassign an alias such as `champion` to a different version to change which model serves production traffic. [4] The consequence for operations is that serving code can load `models:/<NAME>@champion` and never change. Promotion is moving the alias, and rollback is moving it back, so neither requires a redeploy of the serving code.

That convenience carries a responsibility. An alias move is a production change. It should happen through the same reviewed path as a code deployment, after the checks in lesson 16, and it should be recorded.

:::low-confidence
The registry page does not describe the status of the older "stages" (Staging, Production) in detail, and its Open Source section still mentions transitioning models between stages. This course does not claim stages are deprecated. Check the MLflow release notes for the version you run. [4]
:::

:::key-takeaways
- A registry names and versions models; the first registration is version 1 and each later one increments. [4]
- Aliases are mutable pointers such as `champion`; load by `models:/<name>@<alias>`. [4]
- Moving an alias changes which model serves traffic, so treat it as a controlled deployment step. [4]
:::

:::glossary
- **Model registry**: a catalogue of trained models with names, versions and status.
- **Registered model**: one named entry in the registry that holds all its versions.
- **Model version**: a numbered snapshot of a registered model (v1, v2, ...).
- **Flavor**: the library a model was built with (scikit-learn, PyTorch, ...), which tells tools how to load it.
- **Model URI**: an address string for a model, like `models:/MyModel/3`.
- **Alias**: a movable nickname that points to one version, like `champion`; like a Git branch name pointing to a commit.
- **Champion**: the model currently trusted in production.
- **Tag (key-value)**: a label such as `validation_status: approved`.
- **Lineage**: the trail from a model back to the run, code and data that made it.
- **Promotion**: making a version the live one.
- **Rollback**: pointing back to the previous version.
- **Stages (Staging/Production)**: MLflow's older way of marking versions; aliases are the newer one.
- **CD4ML**: Continuous Delivery for Machine Learning, a ThoughtWorks approach.
- **Production traffic**: the real requests from real users.
:::
