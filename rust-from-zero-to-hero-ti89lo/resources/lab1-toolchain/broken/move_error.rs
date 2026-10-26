// Does not compile on purpose. Try: rustc --edition 2024 broken/move_error.rs
fn main() {
    let greeting = String::from("hello");
    let moved = greeting; // ownership moves to `moved`
    println!("{moved}, {greeting}"); // error: `greeting` was moved
}
