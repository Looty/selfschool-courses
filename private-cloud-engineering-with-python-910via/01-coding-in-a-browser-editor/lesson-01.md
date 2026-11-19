---
id: l01
title: "The editor, the limits and a routine"
quiz: quiz-01.yaml
resources: [../resources/ch01/sum_pairs_starter.py, ../resources/ch01/sum_pairs_solution.py, ../resources/ch01/sum_pairs_test.py, ../resources/ch01/word_count_top_starter.py, ../resources/ch01/word_count_top_solution.py, ../resources/ch01/word_count_top_test.py]
sources: [1, 2, 3, 4, 5, 6, 7, 9, 16, 17, 18, 22]
---
After this lesson you can say what a browser coding platform gives you and what it takes away, read standard input in the four usual ways, and follow a six-step routine that keeps you talking and testing under time pressure.

## What the platform gives you

The examples here come from HackerRank, because its documentation is public. Other platforms differ in detail, so treat this as one concrete case of a timed coding session.

| Item | What the documentation says |
| --- | --- |
| Python version | Python 3 is listed as "Python 3.14.2" for coding questions [1] |
| Time limit | 10 seconds for Python [1] |
| Memory limit | 512 MB [1] |
| Source size | 50 KB per submission [1] |
| Editor | Monaco Editor 0.50.0, with Normal, Emacs and Vim modes and 2, 4 or 8 space indents [3] |
| Libraries | A fixed list of extra packages; numpy and pandas appear only in the "ML Libraries" column, so assume the standard library [1] |

Check the real version at the start with `import sys; print(sys.version)`. The platform also shows an info icon next to the language dropdown with the environment details [3]. All code in this course runs on Python 3.11 and later; anything that needs 3.14 is marked.

Exceeding the time limit gives "Terminated due to timeout"; the listed causes include inefficient logic and infinite loops [3]. 10 seconds is generous for linear code and fatal for a nested loop over 10**5 items, which is why step 3 of the routine below is about cost.

## The two question shapes

**Function style.** The platform gives a read-only stub above and below your code. You complete the function and return a value. Anything you `print()` appears in a separate Debug Output panel and does not affect the score [3] [4].

**Complete program.** You read standard input yourself and print standard output. Debug output is not separated: it lands in "Your Output" and is compared with the expected output, which can turn a correct answer into Wrong Answer [4]. Scoring is exact string matching, so a stray space, a missing newline or a leftover debug print fails the case [2] [3].

Both shapes ship **sample test cases** (shown, with input and output) and **hidden test cases** that check edge cases, correctness and performance and show only your output [2] [3]. Running code does not change your score [2]. Custom input lets you try your own data when the test allows it, and then the question's own tests are not run [2] [4].

:::low-confidence
Everything above is documented for HackerRank Tests. The live Interview product has a Coding workspace with a Run icon, a Test Cases tab and an Input/Output tab [6]. Whether autocomplete exists in the new Interview editor is not stated on the pages read; the legacy editor has an on/off autocomplete setting [7]. Whether an AI assistant is present is set by the hiring company [6]. Check the platform's own pages for the session you are given.
:::

## Practise without autocomplete

The Test editor has IntelliSense-style suggestions for Python 3, opened manually with Ctrl+Space and switchable from the three-dots menu [2] [5]. Because it can be turned off, and its status in other formats is unknown, practise in a plain editor: type `import`, signatures and method names from memory. The rest of this course is built for that.

Two other formats exist in the live Interview product: a **DevOps** workspace, a sandboxed Linux environment in an in-browser terminal for installing packages and running command-line tools, and a **Whiteboard** workspace, a shared canvas with shapes, arrows and text [6].

## Reading standard input

`input()` reads one line and strips the trailing newline; at end of input it raises `EOFError`. A prompt string is written to standard output, so never pass one in a complete program [16]. `sys.stdin` is a text file object. [17] Its `readline()` keeps the newline, an empty string means end of file, and looping over the file is memory efficient. [18]

```python
import sys

n = int(input())                       # one integer on a line
a, b = map(int, input().split())       # two integers on one line
rows = [input() for _ in range(n)]     # N more lines
lines = sys.stdin.read().splitlines()  # everything, split into lines
tokens = sys.stdin.read().split()      # everything, split on any whitespace
for line in sys.stdin:                 # streaming: line keeps its "\n"
    line = line.rstrip("\n")
```

The documented sample program reads N, then N pairs [2]:

```python
n = int(input())
for _ in range(n):
    a, b = map(int, input().split())
    print(a + b)
```

When you are unsure about extra spaces or blank lines, `sys.stdin.read().split()` and an index is the most forgiving pattern. For a clean test setup, put the logic in `solve(text) -> str` and call it from a thin `main()`; the exercise files below do this.

## The six-step routine

Say each step aloud, even alone. It is the habit that matters.

1. **Restate and ask.** Repeat the problem in one sentence. Ask about sizes, duplicates, empty input, negative numbers, case and output order.
2. **Two examples.** Write one normal case and one edge case (empty, single item, all equal, ties) as comments or a tiny test.
3. **Brute force and its cost.** Name the obvious solution and its big-O. "Nested loop, O(n**2), too slow for 10**5."
4. **Pick the data structure.** Dict or Counter for counting, set for membership, deque for a queue, heap for top-k, sorted list plus bisect for ranges.
5. **Code in small functions.** One function per idea, meaningful names, no clever one-liners you cannot explain.
6. **Test by hand and state complexity.** Trace your two examples through the code, then say time and space.

## Exercises

Both run with plain `unittest`. `python name_test.py` tests your starter file, and `python name_test.py name_solution` tests the reference. In the course's test run the reference solutions passed 12 of 12 tests each on Python 3.13 and 3.11, and the starters failed with `NotImplementedError`.

**`sum_pairs`** (10 minutes): a complete stdin/stdout program modelled on the documented sample [2]. Edit `sum_pairs_starter.py`, then run `python sum_pairs_test.py`. Hints: split the whole input into tokens; remember the output must have no extra text. Walkthrough: the reference reads all tokens, converts `2 * N` of them and joins the sums with newlines, O(N) time. Common mistakes: printing a prompt, printing a trailing blank line for N = 0, using `input()` in `solve`.

**`word_count_top`** (10 minutes): function style, return the k most frequent words, ties alphabetical. Run `python word_count_top_test.py`. Hints: `Counter`, then one `sorted` call with a tuple key. Walkthrough: key `(-count, word)` sorts by count descending and word ascending in one pass, O(n + m log m). `Counter.most_common` keeps ties in first-seen order [9], so it fails the tie example.

## Gotchas

- **Debug prints in a complete program.** They count as output and break exact matching. [4] Print to `sys.stderr` or remove them before submitting.
- **A prompt passed to `input()`.** The prompt goes to standard output, so it becomes part of your answer. [16]
- **`readline()` keeps the newline.** `int("5\n")` works but string comparisons and `split(",")` surprise you; strip it. [18]
- **Switching language resets the editor.** Copy your code first. [3]
- **Hidden tests show only your output.** A passing sample proves little; run your edge-case example by hand. [3]
- **Assuming a newer Python.** The platform lists 3.14.2 [1] while the current docs describe 3.15 [22]. Do not rely on features added in 3.15.

:::key-takeaways
- Python 3.14.2, 10 s, 512 MB and 50 KB are the documented HackerRank limits. [1]
- Function style: return a value, prints go to Debug Output. Complete program: prints are the answer. [3] [4]
- Output is compared exactly; remove debug prints and prompts. [2] [3]
- Practise without autocomplete; its availability varies by product. [5] [7]
- Six steps: restate, examples, brute force, structure, small functions, test and state complexity.
:::

:::glossary
- **Function style**: a question where you complete a given function and return a value.
- **Complete program**: a question where you read standard input and print standard output yourself.
- **Sample test cases**: the visible tests with shown input and expected output.
- **Hidden test cases**: tests whose input and expected output you never see.
- **Custom input**: your own input data used with Run Code instead of the official tests.
- **Autocomplete**: the editor suggesting names as you type.
- **Brute force**: the obvious solution that tries everything, usually slow.
- **Debug Output**: a separate panel for your prints in function-style questions.
:::
