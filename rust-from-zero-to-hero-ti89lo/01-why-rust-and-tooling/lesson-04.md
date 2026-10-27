---
id: l38
title: "Why Rust suits AI coding agents"
quiz: quiz-38.yaml
sources: [1, 3, 10, 15, 58, 67, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86]
---
After this lesson you can explain why a strict compiler helps an AI coding agent, compare what Rust, Python, TypeScript, Go and C++ check before a program runs, and say where the evidence for Rust is still thin.

## The agent loop: write, check, fix

An AI coding agent is a language model that writes code, runs tools such as a compiler or a test suite, reads the results and tries again. Anthropic's guide to building agents says an agent needs "ground truth" from its environment at each step, such as tool results or code execution, to judge its progress. [84] The same guide names automated tests as one reason coding suits agents: the agent can iterate using test results as feedback. [84]

So the useful question is not "which language does a model write best?" but "which language gives that loop the most useful signal, and how early?" A bug the compiler rejects costs the agent one more round. A bug that compiles and only shows up in production may never be traced back to the change that caused it.

## Rust rejects more mistakes before the code runs

Lab 1 showed three errors the compiler refused to build: a moved value, a conflicting borrow and a missing type. The ownership and borrowing rules reject use after move, dangling references and two simultaneous mutable borrows at compile time. [3] The `Send` and `Sync` traits stop a type that is not thread-safe, such as `Rc`, from being shared across threads, so whole classes of data race become compile errors. [15] Clippy then adds over 800 lints on top. [67]

There is indirect evidence that code which passes these checks is less often wrong. In Android, Google reported a rollback rate for Rust changes about 4 times lower than for C++. [58] Those changes were written by people, not agents, but they measure the same thing an agent cares about: how often code that builds still has to be undone.

## Rust reports errors in a form tools can read

`rustc --error-format json` prints each diagnostic as a JSON object on its own line, and `cargo build --message-format=json` (or `cargo check`) wraps them in messages whose `reason` is `compiler-message`. [77] [78] An agent can read the error code, the file, the line and the suggested fix without scraping text meant for people.

Each suggested fix carries an **applicability** level. `MachineApplicable` means the fix "can be applied mechanically"; `MaybeIncorrect`, `HasPlaceholders` and `Unspecified` mean it cannot. [77] Running the Lab 1 file `broken/move_error.rs` through `rustc --error-format json` on rustc 1.99.1 gave error `E0382` with one suggestion, trimmed here: [86]

```json
{"message": "borrow of moved value: `greeting`",
 "code": {"code": "E0382"},
 "children": [{"level": "help",
   "message": "consider cloning the value if the performance cost is acceptable",
   "spans": [{"line_start": 4, "suggested_replacement": ".clone()",
              "suggestion_applicability": "MachineApplicable"}]}]}
```

"Applicable" means the edit is mechanically valid, not that it is the best design: cloning compiles, but borrowing might be the better fix. The agent, or you, still has to judge.

The commands are also the same in every Cargo project: `cargo build`, `cargo test`, `cargo clippy` and `cargo fmt`. [1] [10] [67] An agent does not have to discover a project's own build system or test runner before it can start the loop.

Microsoft Research built RustAssistant on exactly this loop: prompting combined with repeated rounds between an LLM and the Rust compiler. [75] It reached a peak accuracy of roughly 74% on real-world compilation errors from popular open-source Rust repositories. [75]

## How the other languages compare

| Language | Checked before the program runs | Can reach run time by default |
|---|---|---|
| Rust | Types, ownership and borrowing, thread safety through `Send`/`Sync` [3] [15] | Logic errors, panics, deadlocks; anything inside `unsafe` |
| Python | Nothing by default; type hints are checked only by a separate, optional tool [81] | Wrong types, missing attributes, `None` where a value was expected |
| TypeScript | Types, through `tsc` [82] | Code with type errors still compiles to JavaScript unless `noEmitOnError` is set; null checks need `strict` [82] |
| Go | Types | Data races, found only by the race detector on paths that actually run [79] |
| C++ | Types | Undefined behavior, which compilers are not required to diagnose [80] |

- **Python**: PEP 484 says no type checking happens at run time and that Python "will remain a dynamically typed language". [81] An agent gets type errors only if the project runs a separate checker, and nothing stops the program from running anyway. [81]
- **TypeScript**: types are erased, so they "never change the runtime behavior" of the program, and `tsc` writes the JavaScript even when it reports errors. [82] The type checker is still a strong signal: a PLDI 2025 paper reports that LLMs "frequently generate code with typing errors", and using the type system to constrain generation cut compilation errors by more than half. [76]
- **Go**: the race detector is a run-time tool. It "only finds races that happen at runtime", and typically costs 5 to 10 times the memory and 2 to 20 times the run time. [79] Rust rejects the same kind of unsynchronized sharing at compile time. [15]
- **C++**: compilers are "not required to diagnose undefined behavior", and a program with undefined behavior "is not required to do anything meaningful". [80] A use after free that Rust refuses to compile can build cleanly in C++. [3] [80]

## The other side of the ledger

:::low-confidence
The strongest benchmark here does not favor Rust. MultiPL-E (2022, Codex) found that code generation performance "is correlated with language popularity" and that "static type-checking neither helps nor hinders" it; Python, a far more common language, scored higher than Rust. [83] That study is old and used one model. This course found no recent, peer-reviewed study comparing how well agents finish real tasks in each language, so treat the argument in this lesson as reasoning from how the tools work, not as a measured result.
:::

- **Every round is slower.** In the Rust Project's 2025 survey, build performance averaged 6 out of 10, 55% of respondents wait more than ten seconds for a rebuild, and about 45% of former Rust users named long compile times as one reason they stopped. [85] `cargo check`, which skips code generation, is the cheapest way to run the loop, and the survey found it is the command most people run after each change. [1] [85]
- **The compiler does not fix everything.** RustAssistant's peak of about 74% leaves roughly a quarter of real errors unfixed. [75] Its authors also note that Rust's features "pose a steep learning curve" for programmers. [75]
- **A passing build is not a correct program.** The compiler cannot see logic errors, so the agent still needs tests, in Rust as in any language. [84] [10]
- **Watch for fixes that silence the compiler.** An agent can make an error go away with `.clone()`, `Rc<RefCell<T>>` or `unsafe` when a borrow or a different design was the right answer. Review those changes the way you would review a junior colleague's.

:::key-takeaways
- An agent improves its code through a loop of writing, checking and fixing; the earlier and clearer the signal, the fewer bad rounds.
- Rust rejects memory and thread-safety mistakes at compile time that Python, TypeScript, Go and C++ let reach run time by default.
- rustc and Cargo emit JSON diagnostics, and each suggested fix says whether it can be applied mechanically.
- The evidence is mostly reasoning from the tools, not measured results: older benchmarks favor popular languages, and Rust's slower builds make each round cost more.
:::

:::glossary
- **AI coding agent**: a language model that writes code, runs tools on it and uses the results to try again.
- **Feedback loop**: the cycle of writing code, checking it and fixing what the check reports.
- **Diagnostic**: an error, warning or note the compiler reports.
- **Applicability**: rustc's label on a suggested fix saying whether a tool may apply it mechanically.
- **Type erasure**: removing type information when compiling, so types have no effect at run time.
- **Race detector**: Go's run-time tool that reports data races on the code paths a program actually runs.
- **Rollback**: undoing a change after it was merged, usually because it caused a problem.
:::
