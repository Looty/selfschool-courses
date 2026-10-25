---
id: l05
title: "Turing's question (1950)"
quiz: quiz-01.yaml
resources: []
sources: [16]
---
After this lesson you can explain what the imitation game is, and why it makes language the test of machine intelligence.

## "Can machines think?"

In 1950 the mathematician Alan Turing published "Computing Machinery and Intelligence" in the journal *Mind*. It opens with the question "Can machines think?" and immediately says the question is a bad one: to answer it you would have to define "machine" and "think" by how people use the words, and that, he argues, is dangerous. So he replaces it with a related question that is less ambiguous. [16]

## The imitation game

Turing's replacement is a game with three players. An interrogator sits in a separate room and puts questions to two hidden players, one man and one woman, labelled only X and Y. The interrogator must work out which is which. The man tries to make the interrogator guess wrongly, and the woman tries to help. Answers are written or typed, so tone of voice gives nothing away. [16]

Then comes the twist: what happens if a machine takes the man's place? Would the interrogator be wrong as often as when a man plays? These questions, Turing proposes, replace "Can machines think?" [16]

## Why this matters for language models

Two things about the design are worth noticing, and both still shape the field.

1. **The test is conducted entirely in text.** Behaviour in conversation is the evidence. Nothing is asked about what is going on inside.
2. **It turns an argument about definitions into an experiment.** You can run the game and count how often the interrogator guesses wrongly.

That is the same move modern evaluation makes. Instead of asking whether a model "understands", researchers write test questions and score the answers (chapter 13). It is also the reason a fluent chatbot is so persuasive and so easy to over-trust, which lesson 8 shows with a 1960s program.

:::low-confidence
Only the opening page of the paper was available when this course was written, so this lesson covers the question and the structure of the game, not Turing's later objections and replies. Read the full paper before quoting more. [16]
:::

:::key-takeaways
- Turing replaced "Can machines think?" with the imitation game. [16]
- In the game, a machine takes one hidden player's place and an interrogator judges from typed answers. [16]
- Judging a system by its conversational behaviour is still how language models are tested.
:::

:::glossary
- **Imitation game**: Turing's test in which an interrogator tries to tell hidden players apart from typed answers.
- **Interrogator**: the person asking questions in the game.
- **Turing test**: the common name for the imitation game applied to machines.
- **Behaviour vs understanding**: judging what a system does rather than what happens inside it.
:::
