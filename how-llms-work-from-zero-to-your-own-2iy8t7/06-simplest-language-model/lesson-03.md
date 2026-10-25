---
id: l26
title: "Measuring a language model: loss and perplexity"
quiz: quiz-03.yaml
resources: []
sources: [34, 35, 71]
---
After this lesson you can compute and read a language model's loss on unseen text, and say what perplexity means.

## One number to compare models

To say one model is better than another you need a score. For language models the natural one is: **how much probability did the model give to what actually came next?** If the real next character is `h` and the model gave `h` probability 0.34, that is a decent guess; if it gave 0.001, it was badly surprised.

The standard loss is cross-entropy, which Google's glossary describes as a generalization of log loss to multi-class classification, quantifying the difference between two probability distributions. [34] For next-token prediction it reduces to something simple: for each position take the model's probability of the true next token, take minus its logarithm, and average over positions. A probability of 1 costs 0; smaller probabilities cost more.

```
loss = average over positions of  -log( P(true next token) )
```

Lower is better, and it is measured on **validation text** the model did not train on (lesson 19). [35]

## Reference points

If a model knew nothing and guessed uniformly among V tokens, its loss would be log V. For the lab's 65 characters that is **4.174**. Any real model should beat that.

In the test run of the counting model (lab 6), the loss on held-out Shakespeare was **2.493**. The mini-GPT you train in chapter 8 reaches about **1.93** in a minute of training. Each gap is a measurable improvement: the model puts, on average, more probability on the character that really came next.

## Perplexity

**Perplexity** is the loss turned back into an intuitive count: exp(loss). The Hugging Face documentation defines it as "the exponentiated average negative log-likelihood of a sequence" and notes that it is equivalent to exponentiating the cross-entropy between the data and the model's predictions. Intuitively it measures the model's ability to predict uniformly among the specified tokens of a corpus. [71] A loss of 2.493 gives a perplexity of about 12.1: the model is, on average, as uncertain as if it were choosing uniformly among about 12 equally likely characters. The uniform guess has perplexity 65.

The same page makes two points worth keeping. First, "the tokenization procedure has a direct impact on a model's perplexity", so perplexities of models with different tokenizers must not be compared directly. Second, perplexity applies to autoregressive (left-to-right) models and is not well defined for masked models like BERT. [71]

## Measuring a model with a limited window

A real model sees only its context window, so evaluating a long text needs care. The Hugging Face page shows this with GPT-2 (1024-token window): cutting the text into disjoint 1024-token chunks gave a perplexity of 19.44 on WikiText-2, about the 19.93 reported in the GPT-2 paper, but sliding the window with a stride of 512 so each prediction had more context gave 16.44. The disjoint method is quick but, by giving most predictions less context, reports a worse (higher) number. [71] The lesson: a score depends on how it was measured, so say how.

:::low-confidence
Papers sometimes report the same quantity in bits (base-2 logs) or per word instead of nats per character, and the labs here use nats per character. Always check the unit and the tokenizer before comparing numbers across sources. [71]
:::

## Be careful comparing across tokenizers

A loss per *character* and a loss per *token* are not comparable, because a token carries more than one character. Compare models only when they use the same tokenizer and the same held-out text.

:::key-takeaways
- Loss for a language model is the average of −log P(true next token) on held-out text. [34][35]
- Guessing uniformly among V tokens gives loss log V (4.174 for 65 characters).
- Perplexity is exp(loss): roughly how many equally likely options the model is torn between.
:::

:::glossary
- **Cross-entropy loss**: the average of minus the log probability the model gave to the true next token. [34]
- **Log (logarithm)**: the inverse of exponentiation; makes products of probabilities into sums and small probabilities into big costs.
- **nat**: the unit of loss when natural logs are used (bits when base 2 is used).
- **Perplexity**: exp(loss); the effective number of equally likely options.
- **Uniform guess**: giving every token the same probability.
- **Held-out (validation) text**: text the model did not train on, used for honest scoring.
- **Surprise**: how unlikely the model thought the true next token was.
:::
