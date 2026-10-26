---
id: l19
title: Vec, HashMap and choosing a collection
quiz: quiz-19.yaml
sources: [7, 38, 40, 63]
---
After this lesson you can use `Vec` and `HashMap` idiomatically (including the entry API), reason about their costs, and pick another standard collection when one of them does not fit.

## Vec<T>

```rust
let mut v: Vec<i32> = Vec::new();
v.push(1);
let w = vec![1, 2, 3];

let third: &i32 = &w[2];          // panics if out of range
let maybe: Option<&i32> = w.get(9); // None if out of range

for x in &w { println!("{x}"); }      // shared borrow of each element
for x in &mut v { *x += 50; }         // mutable borrow; * to reach the value
```

Use indexing when an out-of-range index is a bug that should crash, and `get` when it can legitimately happen, such as an index typed by a user. [7] A `Vec` holds one type; to store several kinds of values, put an enum in it (or a trait object, Chapter 6). [7] Dropping a vector drops every element. [7]

The standard library documents exactly what a `Vec` is: always a (pointer, capacity, length) triple, with elements stored contiguously on the heap. [40] It never stores elements inline on the stack ("small vector optimization"), and never shrinks by itself; `push` reallocates only when length equals capacity, which keeps it amortized O(1). [40] `Vec::new()` does not allocate at all, and `Vec::with_capacity(n)` requests exactly enough room for `n` elements. [40]

## HashMap<K, V>

```rust
use std::collections::HashMap;

let mut scores: HashMap<String, i32> = HashMap::new();
scores.insert(String::from("Blue"), 10);
let blue = scores.get("Blue").copied().unwrap_or(0);   // get returns Option<&V>

// count words with the entry API
let mut counts = HashMap::new();
for word in "hello world wonderful world".split_whitespace() {
    *counts.entry(word).or_insert(0) += 1;
}
// {"world": 2, "hello": 1, "wonderful": 1}, in some order
```

`HashMap` is not in the prelude, so it needs a `use`. [7] Inserting an owned value such as a `String` moves it into the map; `Copy` values are copied. [7] `entry(key)` returns an `Entry` that is either occupied or vacant, and `or_insert` returns a `&mut V` to the existing or newly inserted value; it does the lookup once and works well with the borrow checker. [7] Iteration order is arbitrary. [7]

The default hash function is SipHash, chosen to resist denial-of-service attacks rather than for raw speed; you can plug in another hasher if profiling shows hashing is the bottleneck. [7]

## Choosing a collection

The standard library's own advice: "you should probably just use Vec or HashMap". [38] When they do not fit: [38]

| Need | Collection |
|---|---|
| Queue, or fast push/pop at both ends | `VecDeque` |
| Map sorted by key, range queries, min/max key | `BTreeMap` |
| Just remember which keys were seen | `HashSet` / `BTreeSet` |
| Always process the largest item next (priority queue) | `BinaryHeap` |
| Split and join lists in O(1), no amortization tolerated | `LinkedList` (rarely) |

Typical costs: `Vec` get O(1), insert or remove at index `i` O(n-i); `HashMap` get and insert O(1) expected; `BTreeMap` O(log n). [38] Collections never shrink automatically, and `with_capacity` avoids repeated growth when you know the size up front. [38]

On linked lists, the community book *Learn Rust With Entirely Too Many Linked Lists* is blunt: "99% of the time you should just use a Vec", and most of the rest a `VecDeque`. [63]

:::key-takeaways
- `v[i]` panics on a bad index, `v.get(i)` returns `Option`; a held `&v[i]` blocks `push`.
- Use `entry(...).or_insert(...)` to update-or-insert in one lookup.
- Default to `Vec` and `HashMap`; reach for `VecDeque`, `BTreeMap`, sets or `BinaryHeap` for specific needs.
:::

:::glossary
- **Vec**: Rust's growable array stored on the heap.
- **HashMap**: a key-value map using hashing for fast lookup.
- **Entry API**: methods that find a map slot once and then read, insert or modify it.
- **Amortized O(1)**: constant time on average over many operations, though a single one may be slow.
- **Prelude**: the set of names Rust brings into every module automatically.
- **Hasher**: the algorithm that turns a key into a number for a hash table.
- **SipHash**: the default hash algorithm, resistant to attackers choosing colliding keys.
- **VecDeque**: a double-ended queue backed by a ring buffer.
- **BTreeMap**: a map kept sorted by key.
:::
