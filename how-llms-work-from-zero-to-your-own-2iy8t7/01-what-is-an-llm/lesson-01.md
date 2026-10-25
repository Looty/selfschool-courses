---
id: l01
title: The problem with words
quiz: quiz-01.yaml
resources: []
sources: [21, 72]
---
After this lesson you can say why handling language is hard for a computer, and what a language model is trying to do about it.

## Computers like numbers, people write words

A computer is excellent at arithmetic and at following exact rules. Language is neither. The same idea can be said many ways ("it's cold", "brr, freezing", "bring a coat"), and the same words can mean different things ("the bank of the river", "the bank approved the loan"). Meaning also depends on what came before: "it" in "the trophy did not fit in the suitcase because it was too big" refers to the trophy, but change "big" to "small" and it refers to the suitcase.

For decades, programmers tried to handle this by writing rules by hand. That works for narrow jobs and breaks quickly outside them. You will see this in chapter 2, where a famous 1960s chatbot used nothing but keyword rules.

## The change of approach

A language model replaces hand-written rules with a different question: given some text, **how likely is each possible next piece of text?** If you can answer that well, a lot of useful behaviour falls out. Complete a sentence, answer a question (the answer is the likely continuation of the question), translate (the likely continuation of "French:" after an English sentence), or write code.

The model does not look up meanings in a dictionary. Computers work with numbers, so text is first converted into integers, called **tokens**, usually with a method such as byte-pair encoding, and the model works on those numbers. [21] Chapter 5 shows how.

Google's Machine Learning Crash Course defines a language model the same way: it "estimates the probability of a token or sequence of tokens occurring within a longer sequence of tokens", and it adds that a token can be a word, a subword (a chunk with meaning, such as "un", "watch" or "ed") or a single character. [72]

## What "large" adds

An LLM is a **large language model**: the same idea, with a very large number of adjustable numbers inside it (parameters), trained on a very large amount of text. This course starts with tiny versions you can run on a laptop and works up, so you can see which parts are the idea and which parts are only scale.

## The plan for the course

1. Where the idea came from, and why it took until the 2010s to work (chapters 2 and 3).
2. The minimum learning theory you need (chapter 4).
3. Text to numbers, then the simplest possible language model, by counting (chapters 5 and 6).
4. Attention and the Transformer, the design behind GPT (chapters 7 and 8).
5. What scale changed, how a text predictor becomes an assistant, and how to use and adapt one (chapters 9 to 13).

:::key-takeaways
- Language is ambiguous and depends on context, which makes hand-written rules brittle.
- A language model predicts how likely each next piece of text is; many tasks can be phrased that way.
- Text is turned into integer tokens before a model can work on it. [21]
:::

:::glossary
- **Language model**: a program that estimates how likely each possible next piece of text is.
- **LLM (large language model)**: a language model with a very large number of adjustable numbers, trained on a huge amount of text.
- **Token**: a small chunk of text (a word, part of a word, a character) turned into an integer for the model.
- **Parameters**: the adjustable numbers inside a model; training changes them.
- **Rules-based system**: software whose behaviour is a list of instructions written by a person.
- **Ambiguity**: when the same words can mean more than one thing.
:::
