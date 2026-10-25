---
id: l05
title: Training, loss and metrics
quiz: quiz-01.yaml
resources: []
sources: [17, 28, 29]
---
After this lesson you can read a loss curve, explain what accuracy, precision and recall measure, and spot when a metric is misleading.

## Loss: how wrong is the model?

Loss is a score for how wrong the model is: how far its predictions are from the true answers (the labels). Only the size of the miss matters, not whether it was too high or too low, so each loss removes the sign by taking an absolute value or squaring the difference. [28] For regression (predicting a number, like a price) the common ones are: [28]

- **L1 loss**: the sum of absolute differences; **MAE** is its average over the examples.
- **L2 loss**: the sum of squared differences; **MSE** is its average, and **RMSE** is the square root of MSE.

Squaring makes large errors count for much more, and MAE and RMSE are often easier to interpret because they are in the same units as the prediction. [28] The goal of training is to minimise loss. [28] From an operator's point of view, training is a process that turns data into a model by driving a loss number down, and the loss over time is one of the first things to log.

## Generalisation and overfitting

A model that has memorised the training set so closely that it fails on new data is overfit, like a student who memorised last year's exam answers. Underfitting is the opposite: the model is too simple and does poorly even on the training data. The goal is generalisation, good predictions on new data. [17]

You find this with **loss curves**, which plot loss against training iterations. A generalisation curve shows two of them, for the training set and for the validation set. In an overfit model the two curves start out together and then diverge: training loss keeps falling or levels off, while validation loss starts to rise. [17] Google names two causes of overfitting: the training data does not represent real-world data well enough, or the model is too complex. [17]

## Classification metrics

For classifiers, four counts matter: true positives (TP), true negatives (TN), false positives (FP) and false negatives (FN). [29]

| Metric | Formula | Question it answers |
| --- | --- | --- |
| Accuracy | (TP + TN) / (TP + TN + FP + FN) | How many predictions were right? |
| Recall (true positive rate) | TP / (TP + FN) | Of the real positives, how many were found? |
| Precision | TP / (TP + FP) | Of the predicted positives, how many were real? |
| False positive rate | FP / (FP + TN) | Of the real negatives, how many raised a false alarm? |

[29]

**Accuracy can mislead.** It works reasonably well only on balanced data. If 1% of examples are positive, a model that always predicts negative scores 99% accuracy and never finds a positive. [29] For imbalanced data look at recall, precision or the false positive rate.

**Precision and recall trade off through the threshold.** Raising the classification threshold makes the model more conservative: fewer false positives (higher precision) but more false negatives (lower recall). Lowering it does the opposite. Each metric is computed at one threshold, so the right choice depends on which error costs more. [29]

:::key-takeaways
- Loss measures how wrong predictions are; training minimises it. MAE, MSE and RMSE are the common regression losses. [28]
- Overfitting shows as validation loss rising while training loss keeps falling. [17]
- Accuracy is misleading on imbalanced data; use precision, recall or false positive rate. [29]
- The classification threshold trades precision against recall. [29]
:::

:::glossary
- **Label**: the correct answer attached to a training example.
- **Loss**: a score of how wrong the model's predictions are; lower is better.
- **Regression**: predicting a number (a price, a temperature).
- **Classification / classifier**: predicting a category (spam or not spam).
- **MAE / MSE / RMSE**: three ways to average the model's errors: plain size, squared size, and square root of the squared average.
- **Overfitting**: learning the training data too exactly, noise included, so new data goes badly.
- **Underfitting**: the model is too simple to capture the pattern at all.
- **Generalisation**: doing well on data the model has never seen.
- **Loss curve**: a line chart of loss as training goes on.
- **True/false positive/negative (TP, FP, TN, FN)**: right "yes", wrong "yes", right "no", wrong "no".
- **Precision**: when the model says "yes", how often it is right.
- **Recall**: of all the real "yes" cases, how many the model found.
- **Imbalanced data**: one category is far rarer than the other, like fraud among normal payments.
- **Threshold**: the score above which the model answers "yes"; moving it trades precision against recall.
:::
