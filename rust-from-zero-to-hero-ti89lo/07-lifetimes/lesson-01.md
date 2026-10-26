---
id: l17
title: Lifetime annotations and elision
quiz: quiz-17.yaml
sources: [9, 60]
---
After this lesson you can read and write lifetime annotations such as `'a`, explain what they do and do not change, and apply the three elision rules to tell when annotations are needed.

## Why lifetimes appear in signatures

Every reference has a lifetime: the part of the program in which it is valid. [9] Usually the compiler infers it, just as it infers most types. [9] Annotations are needed only when a function's signature does not tell the compiler how the lifetimes of its inputs and outputs relate. [9]

```rust
fn longest(x: &str, y: &str) -> &str {      // error[E0106]: missing lifetime specifier
    if x.len() > y.len() { x } else { y }
}
```

The returned reference points into either `x` or `y`, depending on run-time data, so neither you nor the compiler can say from the signature how long the result is valid. [9]

## Annotations describe, they do not change

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```

Lifetime parameters start with an apostrophe and are declared in angle brackets like type parameters. [9] This signature says: for some lifetime `'a`, both inputs live at least as long as `'a`, and so does the result. [9] In practice, the result is valid for the *shorter* of the two inputs' lifetimes. [9]

Lifetime annotations do not make any value live longer; they only tell the borrow checker which relationships to enforce, and calls that break them are rejected. [9]

```rust
let string1 = String::from("long string is long");
let result;
{
    let string2 = String::from("xyz");
    result = longest(string1.as_str(), string2.as_str());
}                                   // string2 dropped here
// println!("{result}");            // error[E0597]: `string2` does not live long enough
```

A human can see that `result` points into `string1`, but the signature promises only "the shorter of the two", and that ends with `string2`. [9] The annotations form a contract the compiler checks at each call without looking into the body. [9]

If the result never comes from `y`, say so, and `y` needs no relationship with it: `fn first<'a>(x: &'a str, y: &str) -> &'a str`. [9] What you can never do is return a reference to a local value: no annotation can stop it from being dropped, so return an owned value instead. [9]

## The three elision rules

Writing `'a` everywhere would be tedious. Before Rust 1.0 every reference in a signature needed one; the team then built the most common patterns into the compiler as the **elision rules**. [9] The compiler applies them to signatures without annotations: [9]

1. Each reference parameter gets its own lifetime parameter.
2. If there is exactly one input lifetime, it is assigned to all output references.
3. If there are several input lifetimes but one of them is `&self` or `&mut self`, the lifetime of `self` is assigned to all outputs.

If references in the output still have no lifetime after the three rules, compilation stops with an error and you must annotate. [9]

| Signature | After the rules | Result |
|---|---|---|
| `fn first_word(s: &str) -> &str` | rule 1 then 2: `fn first_word<'a>(s: &'a str) -> &'a str` | compiles |
| `fn longest(x: &str, y: &str) -> &str` | rule 1: two inputs, rules 2 and 3 do not apply | needs annotation |
| `fn part(&self, key: &str) -> &str` | rule 3: output gets `self`'s lifetime | compiles |

## Lifetime vs scope

RFC 2094, which introduced non-lexical lifetimes, makes a useful distinction: a value's *scope* runs until it is freed, while a reference's *lifetime* is the span of code where that reference may still be used. [60] A reference's lifetime must fit inside the scope of what it points to. [60] When you read `'a`, think "a region of code", not "a duration of the value".

:::key-takeaways
- Lifetime annotations relate the lifetimes of inputs and outputs; they never extend how long a value lives.
- `longest<'a>(x: &'a str, y: &'a str) -> &'a str` means the result is valid for the shorter input.
- Three elision rules cover most signatures; annotate when output references remain ambiguous.
:::

:::glossary
- **Lifetime**: the region of code during which a reference is valid.
- **Lifetime parameter**: a name such as `'a` used in a signature to relate reference lifetimes.
- **Elision**: leaving annotations out because the compiler can fill them in by fixed rules.
- **Input lifetime**: a lifetime on a parameter.
- **Output lifetime**: a lifetime on a return value.
- **Scope (of a value)**: the code from a value's creation until it is dropped.
- **Contract**: a promise in a signature that the compiler checks at every call.
:::
