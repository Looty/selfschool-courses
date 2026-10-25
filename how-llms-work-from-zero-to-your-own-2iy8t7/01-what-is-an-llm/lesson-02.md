---
id: l02
title: An LLM on one page
quiz: quiz-02.yaml
resources: []
sources: [21, 3, 8]
---
After this lesson you can explain in plain words what an LLM is, how it is made, and the handful of terms the rest of the course builds on.

## New to ML? The 60-second version

Normal software is rules a person wrote. In machine learning you instead show a program many **examples** and let it work out the rules itself. An example is a row of data, often with the right answer attached (a **label**). Each example is described by **features**, the facts the program looks at. The process of working out the rules is **training**, and the result is the **model**: a file of numbers that turns new features into a **prediction**. Using a trained model on new data is **inference**. The numbers a model adjusts while learning are its **parameters** (or **weights**). A model is only as good as the examples it learned from.

## What an LLM is

Put that together and an LLM is a model whose examples are huge amounts of text, whose job is to predict the next token, and whose parameters number in the billions. Wikipedia's overview describes the training in two stages: **pretraining**, where a model is trained to predict the next word on a large body of text, and later adjustment (fine-tuning) to make it follow instructions or behave well. [21] Chapter 10 covers the second stage.

Three ideas carry most of the rest of the course.

- **Context window.** The model can only consider a limited span of tokens at once, called its context window. Everything it can "remember" in a conversation has to fit in it. [21]
- **Scale.** The GPT-3 paper trained a model with 175 billion parameters, 10 times more than any previous non-sparse language model, and showed that scaling up improved performance on tasks given only a few examples in the prompt. [3]
- **Training data matters as much as size.** A later study found that large models of the time were undertrained: for the best result, the number of parameters and the number of training tokens should grow together. [8]

## How the pieces fit

```
text  ->  tokens  ->  [ model: parameters ]  ->  probabilities for the next token  ->  pick one  ->  add it to the text  ->  repeat
```

That loop is all that text generation is. Each pass produces one token, appends it to the text, and runs again. A chat reply of 200 words is a few hundred passes of that loop.

## What it is not

An LLM is not a database and not a search engine. It does not look things up. Everything it "knows" is stored implicitly in its parameters from training, so it can state wrong things in a fluent voice. Lesson 3 covers this.

:::key-takeaways
- Training turns examples into a model; inference uses the model on new inputs.
- An LLM is a model trained to predict the next token on a very large amount of text, then often tuned further. [21]
- It generates text by repeating one step: predict the next token, add it, repeat.
- Scale (parameters and tokens) is a main reason the approach works. [3][8]
:::

:::glossary
- **Example / label / feature**: one row of data / its known right answer / the facts the program looks at in it.
- **Training**: adjusting a model's parameters so its predictions fit the examples.
- **Model**: the result of training; numbers that turn inputs into predictions.
- **Inference**: using a trained model to make a prediction.
- **Parameters (weights)**: the adjustable numbers inside a model.
- **Pretraining**: the first, large training stage: predict the next token on lots of text.
- **Fine-tuning**: extra training on a smaller, specific set of examples.
- **Context window**: the most tokens a model can consider at once.
- **Few-shot**: giving the model a few examples inside the prompt, with no extra training.
- **Prompt**: the text you give the model to continue.
- **Undertrained**: trained on too little data for its size.
:::
