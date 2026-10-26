---
id: l22
title: "Lab 2: a word-frequency counter"
quiz: quiz-22.yaml
resources: [../resources/lab2-wordfreq/Cargo.toml, ../resources/lab2-wordfreq/src/lib.rs, ../resources/lab2-wordfreq/src/main.rs, ../resources/lab2-wordfreq/sample.txt]
sources: [5, 6, 7, 8, 10, 11, 12]
---
After this lab you will have built a small command-line tool that counts words with an iterator chain and a HashMap, run its unit tests, and handled bad input without panicking.

This is a hands-on lab. It uses only the standard library, so it needs no internet access. It was built and tested with rustc 1.99.1 while writing this course.

## Shortcut: the ready-made files

Download the four files from Resources into a folder `wordfreq/`, keeping `src/` as a subfolder. Then:

```bash
cargo test                       # 5 unit tests
cargo run -- sample.txt 5        # the 5 most frequent words
cargo run -- sample.txt x        # bad argument: an error, not a panic
```

What you should see from the second command:

```text
80 words, 53 distinct
   11  the
    4  to
    3  a
    3  compiler
    3  value
```

`cargo test` reports `5 passed; 0 failed`. The third command prints `top-n must be a whole number, got "x"` and exits with status 2.

## Step 1: library and binary

The package has `src/lib.rs` with all the logic and a thin `src/main.rs` that parses arguments and prints; the binary calls the library as `wordfreq::count_words`, like an outside user would. [6] That split also lets the logic be tested directly. [10]

## Step 2: splitting words with an iterator chain

```rust
pub fn words(text: &str) -> impl Iterator<Item = String> + '_ {
    text.split(|c: char| !(c.is_alphanumeric() || c == '\''))
        .map(|w| w.trim_matches('\''))
        .filter(|w| !w.is_empty())
        .map(str::to_lowercase)
}
```

Every step is a lazy adapter; nothing runs until the caller loops over the result. [12] The return type is `impl Iterator`, because the real type contains closures and cannot be written out. [12] The `+ '_` says the iterator borrows from `text`, so it cannot outlive it. `str::to_lowercase` is passed as a function instead of a closure, which works because functions implement the closure traits. [12] Splitting on `char` values is UTF-8 safe; you never index bytes. [7]

## Step 3: counting with the entry API

```rust
let mut counts = HashMap::new();
for word in words(text) {
    *counts.entry(word).or_insert(0) += 1;
}
```

This is the Book's word-count pattern: one lookup per word, and `or_insert` returns a `&mut usize` to increment. [7]

## Step 4: a deterministic top-n

`HashMap` iteration order is arbitrary, so `top_n` copies the pairs into a `Vec`, sorts by count descending and then by word, and truncates. [7] Without the tie-break, two runs could print equally frequent words in a different order, and the test `top_n_breaks_ties_alphabetically` would be flaky.

## Step 5: errors without panics

`main` uses `let ... else` to print a usage message when the file argument is missing, and `unwrap_or_else` to report a bad number or unreadable file, printing to stderr with `eprintln!` and calling `process::exit` with a nonzero code. [5] [8] [11]

## Check yourself

- Add a test that `count_words("Rust rust RUST")` gives `{"rust": 3}`. Which function makes that pass?
- Change `top_n` to break ties by word in reverse order and run the tests. Which one fails, and why?
- Run `cargo run -- missing.txt`. Which line of `main.rs` printed the message?

:::key-takeaways
- Keep logic in `lib.rs`; make `main.rs` a thin, error-reporting shell.
- Lazy iterator chains plus `entry().or_insert()` give concise, fast counting.
- Sort HashMap output before printing or testing it, because iteration order is arbitrary.
:::

:::glossary
- **Unit test**: a small test of one function, kept next to the code.
- **Tie-break**: a second sort key used when the first one is equal.
- **Flaky test**: a test that passes or fails depending on chance.
- **Exit status**: the number a program returns to the shell; nonzero means failure.
- **stderr**: the output stream for error messages, separate from normal output.
:::
