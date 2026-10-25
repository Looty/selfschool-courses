---
id: l08
title: "ELIZA: the chatbot with no understanding (1966)"
quiz: quiz-04.yaml
resources: []
sources: [22, 40]
---
After this lesson you can describe how the first famous chatbot worked, and what the "ELIZA effect" warns you about today.

## What ELIZA was

ELIZA was written by Joseph Weizenbaum at MIT between 1964 and 1967 and published in 1966, for an IBM 7094 computer. It is considered one of the first chatbots and one of the first programs to attempt the Turing test (lesson 5). [22]

## How it worked

ELIZA did not understand language. It scanned the user's sentence for **keywords**, each ranked by its script. When it found one, it applied a **decomposition rule** to split the sentence into fragments and a **reassembly rule** to build a reply from them, often turning the user's own statement back into a question. [22] Its behaviour lived in editable scripts, and the best known, DOCTOR, imitated a psychotherapist who mostly reflects what the patient says. Wikipedia summarises the setting as chosen partly to sidestep giving the program a database of real-world knowledge. [22]

Weizenbaum's 1966 paper explains the choice in his own words. The scripts that existed at the time made ELIZA respond roughly as a Rogerian psychotherapist would, because the psychiatric interview is one of the few examples of a categorised conversation between two people in which one of them is free to assume "the pose of knowing almost nothing of the real world". If you tell a psychiatrist "I went for a long boat ride" and he answers "Tell me about boats", you do not conclude that he knows nothing about boats; you assume he had some purpose. [40] The program's apparent competence depended on the setting, not on knowledge.

The paper also stresses that ELIZA is a framework: the keywords and transformation rules live in a script that can start small and be "grown and molded as experience with it builds up". [40]

A typical exchange, in the spirit of the original:

```
> I am sad
Why do you say you are sad?
> my mother hates me
Tell me more about your mother.
```

Nothing in the program knows what sadness or a mother is. It matches a pattern and fills in a template. In the next lesson you will build one in about thirty lines.

## The ELIZA effect

Many users attributed human feelings to the program. This became known as the **ELIZA effect**. One report says Weizenbaum's own secretary asked him to leave the room so she could talk with it privately, and that Weizenbaum was troubled that brief exposure could produce "powerful delusional thinking in quite normal people". The experience shaped his later critique of AI. [22]

## Why it matters now

Today's models are far more capable, but the human side of the effect is unchanged: fluent replies make people assume understanding. A language model is a far better pattern-matcher than ELIZA, and it can state falsehoods fluently (lesson 3). Judging what a system *does* is safer than judging how human it *sounds*.

:::key-takeaways
- ELIZA (Weizenbaum, MIT, published 1966) used keyword rules, decomposition and reassembly, with no understanding. [22]
- The DOCTOR script mimicked a therapist who reflects statements back. [22]
- The ELIZA effect: people attribute understanding and feelings to fluent programs. [22]
- Weizenbaum chose the therapist role because it lets one side pose as knowing little about the world. [40]
:::

:::glossary
- **Chatbot**: a program that holds a text conversation.
- **Keyword**: a word the program is set to look for.
- **Decomposition rule**: a pattern that splits the user's sentence into parts.
- **Reassembly rule**: a template that builds a reply from those parts.
- **Script**: ELIZA's editable file of rules; DOCTOR was one script.
- **Rogerian therapist**: a counsellor who mostly reflects the client's own words back.
- **ELIZA effect**: the tendency to treat a fluent program as if it understood you.
:::
