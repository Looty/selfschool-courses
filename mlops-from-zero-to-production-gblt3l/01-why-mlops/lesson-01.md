---
id: l01
title: How ML systems differ from software
quiz: quiz-01.yaml
resources: []
sources: [1, 14]
---
After this lesson you can name what changes when the thing you ship is a model, and explain what CI, CD and CT mean for ML.

## New to ML? The 60-second version

Chapter 1 uses ML words before chapter 2 teaches them properly, so here is the minimum. Normal software is rules a person wrote. In machine learning you instead show a program many **examples** (rows of data, each with the right answer, called a **label**) and let it work out the rules itself. Each example is described by **features**: the facts the program looks at, such as age or country. The process of working out the rules is **training**, and the result is the **model**: a file that takes new features and returns a **prediction**. Using the model on new data is **inference** or **serving**. A model is only as good as the data it was trained on, which is why so much of MLOps is about data. Chapter 2 covers how to measure whether a model is good.

## MLOps in one sentence

Google's guide defines MLOps as a way of working that joins building ML systems (Dev) with running them (Ops), using automation and monitoring at every step: combining code changes, testing, releasing, deploying and managing infrastructure. [1] Think of it as DevOps for machine learning. You already run services this way. The question is what is different when the thing you ship is a trained model, a program that learned its behaviour from data instead of being written line by line.

## Five differences from ordinary DevOps

Google lists these differences between ML systems and other software systems. [1]

- **Team skills.** The team usually includes data scientists or ML researchers who may not be experienced software engineers who can build production services.
- **Development.** ML is experimental. You try features, algorithms, modelling techniques and parameters, and the hard part is tracking what worked and keeping it reproducible and reusable.
- **Testing.** On top of the usual unit and integration tests you need to check the data itself, measure how good the trained model is, and decide whether it is good enough to ship.
- **Deployment.** You do not ship one model as a prediction service. You ship a multi-step pipeline (an automated assembly line) that retrains and deploys models by itself.
- **Production.** Models can go stale, because the real world's data changes over time. You track summary numbers about the incoming data, watch how the model performs live, and stay ready to roll back or step in.

## Three axes of change

Continuous Delivery for Machine Learning (CD4ML) adds a useful frame: an ML application changes along three axes, the code, the model and the data. [14] A normal release pipeline reacts to code changes. An ML pipeline also has to react to a new model and to new data, so all three need versioning and management in the delivery process. [14]

## CI, CD and CT, ML style

The same three letters get wider meanings. [1]

- **Continuous integration (CI)** is no longer only about testing and validating code and components. It also tests and validates data, data schemas and models.
- **Continuous delivery (CD)** is no longer about a single software package or service. It is about a system, the ML training pipeline, that should automatically deploy another service, the model prediction service.
- **Continuous training (CT)** is new and unique to ML systems. It is about automatically retraining models and serving them.

:::low-confidence
These definitions come from Google's MLOps guide. Other vendors draw the lines slightly differently, for example some treat CT as part of CD. Use the names as shorthand and agree on them with your team. [1]
:::

:::key-takeaways
- ML adds experiments, data and model testing, pipeline deployment and decay to the usual DevOps concerns. [1]
- Code, model and data are three separate axes of change to version and manage. [14]
- CI also validates data and models; CD deploys a pipeline that deploys a service; CT retrains and serves automatically. [1]
:::

:::glossary
- **MLOps**: DevOps habits (automation, testing, monitoring) applied to machine learning systems.
- **Model**: the result of training; a file that turns inputs into predictions, like a recipe the computer worked out from examples.
- **Training**: letting the computer study example data to adjust the model until its guesses are good.
- **Pipeline**: a chain of automated steps where each step's output feeds the next, like an assembly line.
- **Data scientist**: a person who explores data and builds models, usually without a software-engineering background.
- **Artifact**: any file your process produces and keeps, such as a trained model.
- **CI (continuous integration)**: automatically testing every change when it is merged.
- **CD (continuous delivery)**: automatically getting tested changes ready to release or released.
- **CT (continuous training)**: automatically retraining the model when there is new data or it gets worse.
- **Decay**: a model slowly getting worse because the real world drifted away from its training data.
- **Rollback**: switching back to the previous working version.
- **Data schema**: the agreed shape of the data: which columns exist and what type each one is.
:::
