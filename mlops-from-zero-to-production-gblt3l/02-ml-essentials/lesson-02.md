---
id: l06
title: Data splits and leakage
quiz: quiz-02.yaml
resources: []
sources: [17, 18, 27]
---
After this lesson you can split a dataset correctly, say what each subset is for, and recognise the common ways information leaks from test data into training.

## Three sets, three jobs

Google's crash course splits the original data into three subsets. [18]

- The **training set** is what the model learns from.
- The **validation set** is used during development to check progress, tweak settings and pick the best version. Think of it as practice exams.
- The **test set** is used once at the end to double-check the chosen model on examples it has never seen. Think of it as the real exam: testing on different examples proves much more than testing on the ones the model studied.

The crash course's worked example partitions 70% training, 15% validation and 15% test, and notes there are no required percentages. [18] For the sets to represent the same thing, the data should be shuffled before partitioning. Sorting by time can make the sets less similar if the data is not stationary. [17] The same transformations used on the training set must be applied to validation, test and real-world data. [18]

## Pitfalls with the splits

The page lists several ways a split goes wrong. [18]

- **Overfitting to the test set.** Repeatedly tuning hyperparameters or features against the same test set lets the model implicitly fit its peculiarities. Use validation for iterative decisions and keep the test set for the final check. Validation and test sets also wear out with repeated use, so refresh them with new data.
- **Duplicates across sets.** Duplicate examples in training and test data can make loss look suspiciously low. Remove validation and test examples that duplicate training examples.
- **Unrepresentative splits.** A test set that differs from the training data or from the real world lets a model score well in testing and still perform poorly in production.
- **Nondeterminism.** Results vary between runs, so rerun an unusually good result before you trust it.

## Data leakage

Data leakage is cheating by accident: information that would not exist at prediction time sneaks into building the model, like seeing the exam answers while studying. Scores look great in testing (for example in cross-validation, which repeats the train/test split several ways), then drop on genuinely new data. [27]

The general rule from scikit-learn: never call `fit` on the test data. Anything a preprocessing step learns, such as a mean for normalisation, must come from the training subset only. [27] The page's recipe: [27]

1. Split into train and test subsets first, before any preprocessing.
2. Use `fit_transform` on the training subset and `transform` on the test subset.
3. Use a `Pipeline`, which makes sure each step is called on the right subset, which matters most with cross-validation and hyperparameter tuning.

The documentation shows how large the effect can be. With 200 samples, 10,000 random features and random binary targets, accuracy should be near chance (0.5). Selecting 25 features on all the data before splitting gave an accuracy of 0.76, an unfairly inflated score; selecting on the training data only gave 0.5. [27] The same risk applies to almost every transformation, including scalers, imputers and PCA. [27]

## The mirror image: inconsistent preprocessing

Anything done to the training data, such as scaling, imputing or feature selection, must also be applied to test and production data, otherwise the feature space changes and the model performs poorly. In scikit-learn's example the untransformed test set gave a mean squared error of about 62.8 against about 0.90 after applying the fitted scaler. [27] This is the seed of the training-serving skew problem that chapter 3 returns to.

:::key-takeaways
- Training learns, validation guides decisions, test confirms at the end; do not tune against the test set. [18]
- Remove duplicates across sets and make the test set representative of real-world data. [18]
- Split first, then fit every preprocessing step on the training data only. Pipelines help enforce it. [27]
- Leakage inflates offline scores and hides problems until production. [27]
:::

:::glossary
- **Training / validation / test set**: data to learn from, data to tune on, and data for the final check.
- **Shuffle**: randomly reorder examples so each subset looks alike.
- **Stationary data**: data whose patterns do not change over time.
- **Overfitting to the test set**: tuning against the final exam until the model only fits that exam.
- **Nondeterminism**: running the same thing twice and getting different results.
- **Data leakage**: information from outside the training data (often the test data) slipping into the model.
- **Preprocessing**: cleaning or rescaling data before the model sees it.
- **Normalisation / scaling**: rescaling numbers to a common range, for example subtracting the mean.
- **`fit` / `transform`**: scikit-learn's two steps: learn something from data (`fit`), then apply it (`transform`).
- **Pipeline (scikit-learn)**: an object that chains preprocessing and a model so each step runs on the right data.
- **Cross-validation**: testing a model several times on different train/test splits to get a steadier score.
- **Imputer**: fills in missing values.
- **PCA**: a method that squeezes many columns into a few that keep most of the information.
- **Training-serving skew**: data is prepared differently in training than in production.
:::
