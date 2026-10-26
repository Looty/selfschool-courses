---
id: l33
title: Declarative and procedural macros
quiz: quiz-33.yaml
sources: [19, 53, 56]
---
After this lesson you can read and write a `macro_rules!` macro, explain how macros differ from functions, and describe the three kinds of procedural macros and how they are built.

## Why macros

Macros write code that writes code. They can do two things functions cannot: take a variable number of arguments (`println!("{}", x)` or `println!("hi")`), and expand *before* type checking, so a macro can, for example, implement a trait for a type. [19] The price is that macro definitions are harder to read and maintain, and a macro must be defined or imported before it is used in a file. [19]

There are two families: **declarative** macros (`macro_rules!`, "macros by example") and **procedural** macros, which come in three kinds: custom `#[derive]`, attribute-like and function-like. [19]

## macro_rules!

A declarative macro looks like a `match` over the *syntax* you pass in. This is a simplified `vec!`: [19]

```rust
#[macro_export]
macro_rules! my_vec {
    ( $( $x:expr ),* ) => {
        {
            let mut temp_vec = Vec::new();
            $(
                temp_vec.push($x);
            )*
            temp_vec
        }
    };
}

let v: Vec<u32> = my_vec![1, 2, 3];
```

- `$x:expr` matches any Rust expression and names it `$x`. [19]
- `$( ... ),*` means "zero or more, separated by commas", and the `$( ... )*` in the body repeats once per match. [19]
- `my_vec![1, 2, 3]` therefore expands to three `push` calls. [19]
- `#[macro_export]` makes the macro available to crates that depend on this one. [19]

Each arm is a pattern; more complex macros have several arms, tried in order. Macro patterns match code structure, so their syntax differs from value patterns. [19] The Book points to *The Little Book of Rust Macros* for the full art. [19]

## Procedural macros

A procedural macro is a Rust function that receives a `TokenStream` (the source code it is applied to) and returns a new `TokenStream`. [19] Procedural macros must live in their own crate, declared with the `proc-macro` crate type. [19] They usually rely on two crates: `syn` parses the token stream into a syntax tree, and `quote!` turns Rust-like templates back into tokens, with `#name` interpolating a variable. [19]

```rust
// in the hello_macro_derive crate (crate-type = proc-macro)
use proc_macro::TokenStream;
use quote::quote;

#[proc_macro_derive(HelloMacro)]
pub fn hello_macro_derive(input: TokenStream) -> TokenStream {
    let ast: syn::DeriveInput = syn::parse(input).unwrap();
    let name = &ast.ident;
    let generated = quote! {
        impl HelloMacro for #name {
            fn hello_macro() {
                println!("Hello, Macro! My name is {}!", stringify!(#name));
            }
        }
    };
    generated.into()
}
```

With that, `#[derive(HelloMacro)] struct Pancakes;` gets an implementation that prints `Hello, Macro! My name is Pancakes!`; Rust has no runtime reflection, so this name lookup has to happen at compile time. [19] A derive macro's function returns a `TokenStream`, not a `Result`, so it reports errors by panicking; production macros should give precise messages. [19] The convention is to name the derive crate after the trait's crate, such as `foo` and `foo_derive`. [19]

The other two kinds: [19]

- **Attribute-like**: `#[route(GET, "/")] fn index() {}`, defined with `#[proc_macro_attribute]`; it receives the attribute's tokens and the item's tokens, and can apply to functions, not just structs and enums.
- **Function-like**: `sql!(SELECT * FROM posts)`, defined with `#[proc_macro]`; it can parse arbitrary syntax, which `macro_rules!` cannot.

## Macros you already use

Every `#[derive(Serialize, Deserialize)]` from Serde and `#[derive(Error)]` from thiserror is a custom derive macro generating trait implementations at compile time. [53] [56] Serde's design note is that this avoids runtime reflection entirely, so the generated code can be as fast as a hand-written serializer. [53]

:::key-takeaways
- Macros expand before type checking and can take any number of arguments; prefer functions when a function works.
- `macro_rules!` matches syntax patterns like `$( $x:expr ),*` and repeats the body per match.
- Procedural macros are functions from `TokenStream` to `TokenStream` in a `proc-macro` crate, typically using `syn` and `quote`.
:::

:::glossary
- **Macro**: code that generates other code at compile time.
- **Declarative macro**: a `macro_rules!` macro defined by matching syntax patterns.
- **Procedural macro**: a function that transforms source tokens into new tokens.
- **TokenStream**: a sequence of source-code tokens, the input and output of procedural macros.
- **Fragment specifier**: the kind of syntax a macro variable matches, such as `expr` or `ident`.
- **syn**: a crate that parses Rust tokens into a syntax tree.
- **quote**: a crate that turns code templates back into tokens.
- **Reflection**: a program inspecting its own types at run time, which Rust does not offer.
- **Custom derive**: a procedural macro used through `#[derive(...)]`.
:::
