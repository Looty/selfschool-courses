---
id: l16
title: Trait objects and dynamic dispatch
quiz: quiz-16.yaml
sources: [9, 17, 21, 26, 74]
---
After this lesson you can store values of different types behind one trait with `dyn Trait`, explain the cost of dynamic dispatch, recognize dyn-compatibility errors, and replace inheritance with Rust's tools.

## No inheritance

Rust has no way for a struct to inherit another struct's fields and methods. [17] For code reuse it offers default trait methods; for polymorphism it offers generics with bounds (resolved at compile time) and **trait objects** (resolved at run time). [17]

## dyn Trait

Generics need one concrete type per instance: a `Vec<T>` holds only `T`s. When a collection must hold different types that share behavior, use a trait object: [17]

```rust
pub trait Draw { fn draw(&self) -> String; }

pub struct Button { pub label: String }
pub struct Slider { pub value: u8 }

impl Draw for Button { fn draw(&self) -> String { format!("[{}]", self.label) } }
impl Draw for Slider { fn draw(&self) -> String { format!("<{}>", self.value) } }

pub struct Screen { pub components: Vec<Box<dyn Draw>> }

impl Screen {
    pub fn run(&self) {
        for c in &self.components { println!("{}", c.draw()); }
    }
}

let screen = Screen {
    components: vec![
        Box::new(Button { label: "OK".into() }),
        Box::new(Slider { value: 7 }),
    ],
};
screen.run();   // prints [OK] then <7>
```

A trait object is always behind a pointer (`&dyn Draw`, `Box<dyn Draw>`, `Rc<dyn Draw>`), because its size is not known at compile time. [26] The pointer is **wide**: it carries a pointer to the data and a pointer to a **vtable**, a table holding one function pointer per method of the trait for that concrete type. [26] The `dyn` keyword is required since the 2021 edition. [26]

If a library user adds a new type that implements `Draw`, `Screen` works with it unchanged, and putting a type that does not implement `Draw` in the vector is a compile error, not a runtime surprise. [17]

## Static vs dynamic dispatch

| | Generics (`T: Draw`) | Trait objects (`dyn Draw`) |
|---|---|---|
| Resolved | at compile time (static dispatch) | at run time through the vtable (dynamic dispatch) |
| Mixed types in one collection | no | yes |
| Code | one copy per type (monomorphized) | one shared copy |
| Cost | none; calls can be inlined | an indirect call; blocks inlining |

Dynamic dispatch adds a runtime lookup and prevents the compiler from inlining the call. [17] If your collections are always homogeneous, generics are preferable. [17]

## dyn compatibility

Not every trait can become a trait object. The Reference calls this *dyn compatibility* (it used to be called object safety). [26] The main rules: the trait must not require `Self: Sized`, has no associated constants, and every method that should be callable on a `dyn` value must take a receiver like `&self`, `&mut self` or `Box<Self>`, have no type parameters of its own, and not return `Self` or an opaque `impl Trait` (so no `async fn`). [26] A method can opt out with `where Self: Sized`; it then simply cannot be called through the trait object. [26]

`Clone` is the classic example: `fn clone(&self) -> Self` returns `Self`, so `Box<dyn Clone>` is not possible.

## Upcasting

Since Rust 1.86 a trait object can be converted to a trait object of one of its supertraits. [21] Checked on 1.99.1: [74]

```rust
trait Animal { fn name(&self) -> String; }
trait Pet: Animal { fn owner(&self) -> String; }   // Animal is a supertrait of Pet

fn as_animal(p: Box<dyn Pet>) -> Box<dyn Animal> {
    p   // upcast: allowed since 1.86
}
```

## Returning different types

Returning a trait object is how a function returns one of several types, which `-> impl Trait` cannot do. [9]

```rust
fn widget(kind: &str) -> Box<dyn Draw> {
    if kind == "button" { Box::new(Button { label: "go".into() }) }
    else { Box::new(Slider { value: 0 }) }
}
```

:::key-takeaways
- `Box<dyn Trait>` holds any type implementing the trait; calls go through a vtable.
- Prefer generics for homogeneous code (zero cost); use trait objects for open, mixed sets of types.
- A trait must be dyn compatible to be used as `dyn`: no `Self` returns, no generic methods, no `Self: Sized` requirement.
:::

:::glossary
- **Trait object**: a value of some type implementing a trait, used through a pointer, like `Box<dyn Draw>`.
- **dyn**: the keyword that marks a trait object type.
- **vtable**: a table of function pointers for one type's implementation of a trait.
- **Wide pointer**: a pointer that carries extra data, such as a length or a vtable pointer.
- **Static dispatch**: the method to call is fixed at compile time.
- **Dynamic dispatch**: the method to call is looked up at run time.
- **Inlining**: replacing a function call with the function's body, enabling further optimization.
- **Dyn compatibility**: the rules a trait must follow to be used as a trait object (formerly object safety).
- **Supertrait**: a trait that another trait requires, as `Animal` for `Pet`.
- **Upcasting**: converting a trait object to a trait object of a supertrait.
:::
