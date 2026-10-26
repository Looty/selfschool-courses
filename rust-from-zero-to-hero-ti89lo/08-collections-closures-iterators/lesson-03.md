---
id: l21
title: Iterators and zero-cost abstractions
quiz: quiz-21.yaml
sources: [9, 12, 19]
---
After this lesson you can chain iterator adapters, know which calls actually do the work, choose between `iter`, `iter_mut` and `into_iter`, and implement `Iterator` for your own type.

## The Iterator trait

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
    // ...dozens of provided methods built on next
}
```

An iterator only has to implement `next`, which returns `Some(item)` until the sequence ends and then `None`. [12] `Item` is an associated type: each iterator says once what it yields. [12] [19] Calling `next` changes the iterator's position, so you need a `mut` iterator to call it directly; a `for` loop takes ownership of the iterator and handles that for you. [12]

## Three ways to iterate a collection

| Call | Yields | The collection afterwards |
|---|---|---|
| `v.iter()` | `&T` | still usable |
| `v.iter_mut()` | `&mut T` | still usable, possibly changed |
| `v.into_iter()` | `T` (owned) | consumed |

[12] `for x in &v` is shorthand for `v.iter()`, `for x in &mut v` for `iter_mut()`, and `for x in v` for `into_iter()`.

## Lazy adapters, eager consumers

Iterators are **lazy**: building one does nothing until something consumes it. [12]

```rust
let v = vec![1, 2, 3];
v.iter().map(|x| x + 1);    // warning: unused `Map` that must be used; nothing runs

let plus_one: Vec<i32> = v.iter().map(|x| x + 1).collect();   // [2, 3, 4]
let total: i32 = v.iter().sum();                               // 6
```

Methods like `map`, `filter`, `enumerate`, `zip`, `take` and `skip` are **iterator adapters**: they return a new iterator and run nothing. Methods like `sum`, `collect`, `count` and `for_each` are **consuming adapters**: they call `next` until the end. [12] Because laziness defers the work, a chain processes each element through every step before moving to the next one, without building intermediate vectors.

Closures passed to adapters often capture their environment: [12]

```rust
#[derive(Debug, PartialEq)]
struct Shoe { size: u32, style: String }

fn shoes_in_size(shoes: Vec<Shoe>, shoe_size: u32) -> Vec<Shoe> {
    shoes.into_iter().filter(|s| s.size == shoe_size).collect()
}
```

`collect` needs to know the target type, from an annotation or from the function's return type. [12]

## Returning iterators

Iterator types get long (`Filter<Map<Iter<'_, i32>, ...>, ...>`) or unnameable because they contain closures, so return them as `impl Iterator`: [9]

```rust
fn evens(limit: u32) -> impl Iterator<Item = u32> {
    (0..limit).filter(|n| n % 2 == 0)
}
```

The Book suggests the same for its search function: returning `impl Iterator<Item = &'a str>` instead of a `Vec` lets the caller print matches as they are found instead of waiting for all of them. [12]

## Your own iterator

```rust
struct Countdown(u32);

impl Iterator for Countdown {
    type Item = u32;
    fn next(&mut self) -> Option<u32> {
        if self.0 == 0 { None } else { self.0 -= 1; Some(self.0 + 1) }
    }
}

let v: Vec<u32> = Countdown(3).collect();   // [3, 2, 1]
let s: u32 = Countdown(3).zip(Countdown(3).skip(1)).map(|(a, b)| a * b).sum();  // 3*2 + 2*1 = 8
```

Implement `next`, and every provided method (`map`, `zip`, `sum`, ...) works on your type. [12]

## Zero-cost

Are iterators slower than hand-written loops? The Book benchmarked a search over the full text of *The Adventures of Sherlock Holmes*: the `for` loop version took 19,620,300 ns per iteration, the iterator version 19,234,900 ns. [12] Iterators are one of Rust's **zero-cost abstractions**: they compile to roughly the code you would write by hand, including loop unrolling and removed bounds checks. [12] The Book quotes Bjarne Stroustrup's zero-overhead principle for C++: "What you don't use, you don't pay for." [12]

:::key-takeaways
- `iter` borrows, `iter_mut` borrows mutably, `into_iter` consumes.
- Adapters (`map`, `filter`) are lazy; consumers (`collect`, `sum`) run the chain.
- Implement `next` to get the whole iterator toolbox; iterator chains cost the same as loops.
:::

:::glossary
- **Iterator**: a value that produces a sequence of items, one per call to `next`.
- **Lazy**: doing no work until the result is needed.
- **Iterator adapter**: a method that wraps an iterator in a new one, such as `map`.
- **Consuming adapter**: a method that runs the iterator to the end, such as `sum` or `collect`.
- **collect**: the consumer that builds a collection, such as a Vec, from an iterator.
- **Zero-cost abstraction**: a high-level feature that compiles to code as fast as the low-level version.
- **Loop unrolling**: an optimization that repeats a loop body to reduce loop overhead.
:::
