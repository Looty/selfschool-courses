---
id: l15
title: "Packaging, lineage and model cards"
quiz: quiz-03.yaml
resources: []
sources: [1, 16, 33]
---
After this lesson you can say what a packaged model contains, which metadata a pipeline should record about every run, and what a model card is for.

## A model is more than weights

A file of weights (the learned numbers) is not enough for someone else to run a model; they also need to know how to load it and what to feed it. MLflow's model format packages a trained model as a folder holding the model file plus an `MLmodel` file, a description of how to read it. Tools such as a web server, a batch job or a deployment target then all use the same package. [33]

The `MLmodel` file is YAML. Its required `flavors` section lists every flavor the model supports, and optional fields record metadata: when it was created, the `run_id` of the tracking run that produced it, the input and output `signature`, an `input_example` and the MLflow version used. [33]

- A **flavor** is a convention that tells a tool how to interpret the model's files. One model can have several flavors. The generic `python_function` (pyfunc) flavor lets tools that only need predictions work with models from any library. [33]
- The **signature** describes expected inputs, outputs and optional inference parameters, and lets MLflow check incoming data against the schema. [33]
- MLflow also logs environment files (`conda.yaml`, `python_env.yaml`, `requirements.txt`) so the environment can be recreated. [33]

Two operational features stand out. `mlflow models serve -m <model_uri>` starts a REST server with an `/invocations` endpoint, and `mlflow.models.predict(...)` runs the model in an isolated environment to check that the logged dependencies and the input are sufficient before deployment. [33]

## Metadata every run should leave behind

Google's Level 1 description of ML metadata management lists what a pipeline run records: [1]

- the versions of the pipeline and its components;
- start and end times and how long each step took;
- the executor and the parameter arguments passed;
- pointers to the artifacts each step produced, such as prepared data, anomalies, statistics and vocabularies;
- a pointer to the previous trained model, which allows a rollback;
- the evaluation metrics for the training and test sets.

This is what makes a deployed model auditable: from a version in the registry, to the run, to the data and the code. The registry's lineage link and the `run_id` in `MLmodel` are the two ends of that chain. [33]

## Model cards

Model cards are short documents that accompany a trained model. They report benchmarked performance across different conditions, including demographic, cultural and intersectional groups, describe the intended use contexts, and describe the evaluation procedures used. [16] The paper recommends that released models be accompanied by documentation of their performance characteristics. [16]

You do not need a standard template to benefit. A card is where "what is this model for, what is it not for, how was it evaluated and where does it perform worse" is written down, next to the model version, rather than in someone's head.

:::low-confidence
Only the abstract page of the Model Cards paper was read, so this lesson does not give the card's section layout. Check the paper for the template before adopting one. [16]
:::

:::key-takeaways
- A packaged MLflow model has flavors, a signature, environment files and metadata such as the producing run. [33]
- Record versions, timings, parameters, artifacts, the previous model and metrics for every run. [1]
- A model card documents performance across conditions, intended use and evaluation procedure. [16]
:::

:::glossary
- **Packaging**: bundling the model with everything needed to run it.
- **`MLmodel` file**: a small YAML file in the package describing how the model can be used.
- **YAML**: a simple human-readable text format for settings.
- **Flavor**: a recipe that tells tools how to load the model; one model can offer several.
- **`pyfunc` (python_function)**: MLflow's generic flavor; "give me inputs, I give you predictions", whatever library was used.
- **Signature**: the declared shape of the model's inputs and outputs, used to catch bad data.
- **Input example**: a sample input saved with the model to test it.
- **`/invocations` endpoint**: the URL of the served model where you send data and get predictions.
- **Lineage**: the chain from a deployed model back to its run, data and code.
- **Metadata**: data about data, such as who ran what, when, with which settings.
- **Executor**: the machine or process that ran a step.
- **Vocabulary**: the list of known words or categories a model was built with.
- **Model card**: a short document saying what a model is for, how it was tested and where it does badly.
- **Intersectional groups**: people in several groups at once, such as older women.
- **Conda / `requirements.txt`**: files that list the software libraries to install.
:::
