---
id: l19
title: Overfitting and generalisation
quiz: quiz-05.yaml
resources: []
sources: [35]
---
After this lesson you can explain overfitting, say why we hold out validation text, and read a pair of loss curves.

## Memorising is not learning

A model that has memorised its training examples scores perfectly on them and fails on anything new. Google's crash course calls this **overfitting**: the model memorises the training set so closely that it predicts poorly on new data, "an invention that performs well in the lab but is worthless in the real world". The opposite goal is **generalisation**: good predictions on new data. [35]

For a language model the stakes are concrete. A model that has memorised its training text would simply recite it. What you want is a model that has absorbed the patterns and can continue text it has never seen.

## Hold some data back

To tell the two apart you split your text. The model trains on most of it (the **training set**) and you keep the rest aside (the **validation set**), never training on it. You then measure the loss on both. In the labs the last 10% of the text is held out this way.

## Reading loss curves

A **loss curve** plots loss against training steps. Training loss and validation loss usually track each other at first. Overfitting is suggested when training loss keeps falling or levels off while validation loss starts to rise. [35] The model keeps getting better at the training examples and worse at everything else.

## Causes

Overfitting results from one or both of two problems: the training data does not represent real-world data well, or the model is too complex. [35] For LLMs this has an important consequence that later chapters return to: bigger models need more training text to avoid simply memorising it (lesson 40).

:::key-takeaways
- Overfitting: the model memorises training data and predicts poorly on new data. [35]
- Generalisation is the goal: good predictions on data the model has not seen. [35]
- Watch validation loss. If it rises while training loss falls, the model is overfitting. [35]
- Causes: unrepresentative data, or a model that is too complex. [35]
:::

:::glossary
- **Overfitting**: learning the training data so closely that new data is predicted badly.
- **Generalisation**: doing well on data the model has not seen.
- **Training set**: the data the model learns from.
- **Validation set**: data held back and used only to measure progress.
- **Loss curve**: a plot of loss over training steps.
- **Representative**: similar enough to real-world data to be a fair sample of it.
- **Memorise**: store specific examples instead of learning the pattern behind them.
:::
