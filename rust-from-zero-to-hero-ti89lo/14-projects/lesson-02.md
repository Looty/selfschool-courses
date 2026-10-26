---
id: l36
title: "Lab 5: an async HTTP key-value service"
quiz: quiz-36.yaml
resources: [../resources/lab5-kv/Cargo.toml, ../resources/lab5-kv/Cargo.lock, ../resources/lab5-kv/src/lib.rs, ../resources/lab5-kv/src/main.rs, ../resources/lab5-kv/tests/api.rs]
sources: [41, 47, 48, 49, 55]
---
After this lab you will have an HTTP service built with axum and Tokio that stores key-value pairs in shared memory, shuts down cleanly on Ctrl+C, and is covered by in-process tests that need no open port.

This is a hands-on lab. The first build downloads crates, so it needs internet access once. Built, tested and run with rustc 1.99.1, axum 0.8.9, tokio 1.54.1, tower 0.5.3 and http-body-util 0.1.5.

## Shortcut: the ready-made files

Download the five files into `kv/`, keeping `src/` and `tests/`. Then:

```bash
cargo test                          # 3 tests, no network needed
cargo run                           # listening on http://127.0.0.1:3000
```

In a second terminal:

```bash
curl -X PUT -d rust localhost:3000/kv/lang     # 201 Created (empty body)
curl localhost:3000/kv/lang                     # rust
curl localhost:3000/kv                          # {"keys":["lang"]}
curl -i localhost:3000/kv/nope                  # 404 Not Found
```

Those were the responses in our test run, with status codes 201, 200, 200 and 404. Stop the server with Ctrl+C; the shutdown handler then prints `shutting down`.

:::low-confidence
The Ctrl+C path was not exercised in testing: the test server was stopped by ending the process. The tests and the four requests above were run.
:::

## Step 1: the router (src/lib.rs)

```rust
pub type Db = Arc<RwLock<HashMap<String, String>>>;

pub fn app(db: Db) -> Router {
    Router::new()
        .route("/kv", get(list_keys))
        .route("/kv/{key}", get(get_value).put(put_value).delete(delete_value))
        .with_state(db)
}
```

A `Router` maps paths and methods to **handlers**: async functions whose arguments are **extractors** and whose return value can be turned into a response. [55] `Path(key)` pulls the `{key}` segment out of the URL, `State(db)` hands in the shared state, and a `String` argument receives the request body. [55] Returning `Json(...)` sets `content-type: application/json`; a `StatusCode` or `Result<String, StatusCode>` works directly as a response. [55]

## Step 2: shared state

axum clones the state for every request, so the docs recommend wrapping it in an `Arc`, which makes each clone a reference-count increment. [55] [41] Inside, a `std::sync::RwLock` lets many readers or one writer at a time. Following the Tokio tutorial's advice, a synchronous lock is fine here because every handler takes the lock, does a quick map operation and drops the guard before returning: no guard is ever held across an `.await`. [49] Handlers are spawned as tasks on a multi-threaded runtime, so this state must be `Send + Sync`, which `Arc<RwLock<...>>` is. [48]

## Step 3: main and graceful shutdown

Shortened from `src/main.rs`:

```rust
#[tokio::main]
async fn main() {
    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000").await.expect("port 3000 should be free");
    axum::serve(listener, app(Db::default()))
        .with_graceful_shutdown(async { tokio::signal::ctrl_c().await.expect("Ctrl+C handler"); })
        .await
        .unwrap();
}
```

`#[tokio::main]` needs Tokio's `macros` and `rt-multi-thread` features; the lab enables those plus `net` and `signal` instead of `full`. [55] [47] `with_graceful_shutdown` stops accepting connections when the future completes, here when Ctrl+C is pressed.

## Step 4: testing without a network

`tests/api.rs` builds the `Router`, sends it a request with `tower::ServiceExt::oneshot`, and reads the body with `http-body-util`. Because axum handlers are tower services, no socket is opened. [55] The `many_concurrent_writers` test spawns 100 tasks that each PUT a different key and then checks that the map holds 100 entries.

## Check yourself

- Add `GET /kv/{key}/len` returning the value's length. Which extractor and which return type do you use?
- Put a `tokio::time::sleep(...).await` inside `put_value` *while holding* the write guard. What does the compiler say, and why? [49]
- Change the state to `Arc<tokio::sync::RwLock<...>>`. What changes in the handlers?

:::key-takeaways
- axum handlers are async functions taking extractors (`Path`, `State`, body) and returning anything that converts into a response.
- Share state as `Arc<...>`; a std lock is fine when the guard never crosses an `.await`.
- Test routers in-process with `oneshot`: fast, deterministic, no ports.
:::

:::glossary
- **HTTP**: the protocol web browsers and APIs use to send requests and responses.
- **Router**: maps request paths and methods to handler functions.
- **Handler**: the async function that serves one route.
- **Extractor**: a handler argument that pulls data out of the request, such as the path or body.
- **Status code**: the number in an HTTP response saying how the request went, such as 404.
- **RwLock**: a lock that allows many readers or one writer.
- **Graceful shutdown**: stopping a server after it stops accepting new work, instead of killing it.
- **tower Service**: the trait axum handlers and routers implement, which lets them be called directly in tests.
- **curl**: a command-line tool for sending HTTP requests.
:::
