---
id: l09
title: Slices, &str and String
quiz: quiz-09.yaml
sources: [3, 7, 19, 74]
---
After this lesson you can borrow part of a collection with a slice, choose between `&str` and `String` in signatures, and handle UTF-8 text without indexing bugs.

## Slices: a pointer plus a length

A **slice** is a reference to a contiguous run of elements in a collection; it does not own anything. [3]

```rust
let s = String::from("hello world");
let hello: &str = &s[0..5];   // bytes 0..5
let world: &str = &s[6..];    // byte 6 to the end
let all:   &str = &s[..];

let a = [1, 2, 3, 4, 5];
let middle: &[i32] = &a[1..3]; // [2, 3]
```

Internally a slice stores a pointer to its first element and a length. [3] That makes `&str` a two-word value: `std::mem::size_of::<&str>()` printed 16 on a 64-bit machine, while `String` (pointer, capacity, length) printed 24. [74] The `str` type itself has no fixed size, which is why you always see it behind a pointer such as `&str` or `Box<str>`. [19]

## Why slices beat indexes

Suppose `first_word` returned the index where the first word ends. Nothing ties that number to the string: if the string is cleared later, the index silently becomes wrong. [3] Returning a `&str` instead ties the result to the data, and the borrow checker then rejects code that clears the string while the slice is still used:

```rust
fn first_word(s: &str) -> &str {
    s.split(' ').next().unwrap_or("")
}

let mut s = String::from("hello world");
let word = first_word(&s);
s.clear();                 // error[E0502]: s is borrowed by `word`
println!("{word}");
```

## &str or String?

- `String` is an owned, growable, heap-allocated UTF-8 buffer; it wraps a `Vec<u8>`. [7]
- `&str` is a borrowed view into UTF-8 text owned by something else. String literals are `&'static str` pointing into the program binary. [3]

Take `&str` in parameters: a `&String` converts to `&str` automatically (a *deref coercion*, covered in Chapter 10), so one function accepts both. [3] Return or store a `String` when you need to own the text. [7]

## Building strings

```rust
let mut s = String::from("foo");
s.push_str("bar");          // append a &str
s.push('!');                // append one char
let s2 = String::from("tic") + "-" + "tac";   // + takes ownership of the left side
let s3 = format!("{s}-{s2}");                 // format! borrows everything
```

`+` calls `add(self, s: &str)`, so it consumes the left `String` and reuses its buffer; `format!` takes references and is easier to read for more than two pieces. [7]

## Why you cannot index a string

Rust strings are UTF-8, so one character may take several bytes: `"Hola".len()` is 4 but `"Здравствуйте".len()` is 24. [7] Indexing a byte would often return half a character, and indexing by characters cannot be constant time, so `s[0]` does not compile. [7] Be explicit about what you want: [7]

```rust
for c in "Зд".chars() { print!("{c} "); }   // З д
for b in "Зд".bytes() { print!("{b} "); }   // 208 151 208 180
```

Range slicing is allowed, but it is checked at run time: `&"Здравствуйте"[0..1]` panics because byte 1 is in the middle of a character. [7] [3] Grouping characters into user-visible letters (grapheme clusters) is not in the standard library; crates on crates.io provide it. [7]

:::key-takeaways
- A slice (`&[T]`, `&str`) is a borrowed pointer plus length; it owns nothing.
- Accept `&str` in parameters, own text with `String`.
- Strings are UTF-8 bytes: use `chars()` or `bytes()`, never integer indexing; slice only on character boundaries.
:::

:::glossary
- **Slice**: a borrowed view of a contiguous part of a collection.
- **&str / string slice**: a borrowed view of UTF-8 text.
- **String**: Rust's owned, growable text type.
- **UTF-8**: the text encoding where each character takes one to four bytes.
- **Unicode scalar value**: one Unicode code point, what Rust's `char` holds.
- **Grapheme cluster**: what a reader sees as one letter, possibly several scalar values.
- **Deref coercion**: Rust automatically turning `&String` into `&str` where needed.
- **'static**: a lifetime that lasts for the whole program, as string literals do.
:::
