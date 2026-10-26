---
id: l37
title: "Capstone: combine the labs into one project"
quiz: quiz-37.yaml
resources: [../resources/lab4-tasks/tests/store.rs, ../resources/lab5-kv/src/lib.rs, ../resources/lab5-kv/tests/api.rs]
sources: [10, 13, 46, 49, 50, 55, 56, 57, 66, 67]
---
After this capstone you will have designed and built, on your own, a task-tracker web service that reuses the Lab 4 library behind the Lab 5 HTTP layer, organized as a Cargo workspace with tests, docs and lints, and reviewed it against a checklist.

This lesson gives a specification and a review checklist rather than finished code. Budget several hours. The starting points are the Lab 4 project (all files are in that lab's lesson; its tests are attached here), and the Lab 5 router and tests from Resources; nothing in this lesson's target design was run while writing the course.

## The goal

Expose the task store from Lab 4 over HTTP:

| Method and path | Effect | Success | Errors |
|---|---|---|---|
| `GET /tasks?all=true` | list tasks (open ones unless `all`) | 200, JSON array | |
| `POST /tasks` with JSON `{"title": "..."}` | add a task | 201, the new task | 400 if the title is empty |
| `POST /tasks/{id}/done` | mark done | 200, the task | 404 if missing |
| `DELETE /tasks/{id}` | remove | 204 | 404 if missing |

Tasks persist to the JSON file after every change.

## Suggested structure

```text
taskhub/
├── Cargo.toml              # [workspace] members = ["crates/*"], resolver = "3"
└── crates/
    ├── tasks/              # the Lab 4 library, unchanged at first
    ├── tasks-cli/          # the Lab 4 binary, now depending on tasks by path
    └── tasks-web/          # new: axum service depending on tasks
```

A workspace shares one `Cargo.lock` and one `target/` directory, so the CLI and the web service always use the same versions of the library and its dependencies; a virtual manifest must set `resolver`. [46] [13] Members depend on each other with path dependencies, for example `tasks = { path = "../tasks" }`. [13]

## Design decisions to make (and write down)

1. **State.** The `Store` must be shared by all handlers: `Arc<Mutex<Store>>` with a std `Mutex` works if no guard is held across `.await`. [49] Saving to disk is blocking I/O; either keep it short inside the lock or hand it to a single **manager task** that owns the store and receives commands over `mpsc` with `oneshot` replies. [50] Write down which you chose and why.
2. **Errors to responses.** Map `StoreError::NotFound` to 404, `EmptyTitle` to 400 and I/O or JSON errors to 500. A clean way is to implement axum's `IntoResponse` for a small error type of the web crate, so handlers can return `Result<Json<Task>, ApiError>`. [55] Keep `StoreError` as the library's typed error. [56] Use anyhow only in `main`. [57]
3. **JSON.** Use axum's `Json` extractor for request bodies and `Json` responses; it works with any type implementing serde's traits. [55]

## Testing

- Keep and run the library's integration tests unchanged. [10]
- Test every route in-process with `oneshot`, like Lab 5, including each error status. Give every test its own temporary JSON file so tests can run in parallel. [10]
- Add one end-to-end check by hand with `curl`.

## Review checklist

Before calling it done, check each item:

- [ ] `cargo test --workspace` passes; every route and every error status has a test.
- [ ] `cargo clippy --workspace` is clean; you did not enable `clippy::restriction` wholesale. [67]
- [ ] `cargo fmt` leaves no diff.
- [ ] Public items in `tasks` have doc comments with an example; `cargo test` runs the doc tests. [13]
- [ ] Errors follow C-GOOD-ERR: meaningful messages, `Error` implemented, causes available through `source()`. [66]
- [ ] Structs keep their fields private (C-STRUCT-PRIVATE) and arguments use types, not bools (C-CUSTOM-TYPE). [66]
- [ ] No lock guard lives across an `.await`; blocking work is short or moved off the async threads. [49]
- [ ] `Cargo.lock` is committed. [13]
- [ ] There is no `unwrap()` on user input or I/O outside tests.

## Going further

- Add `PATCH /tasks/{id}` to rename a task, reusing the Lab 4 `edit` exercise.
- Replace the JSON file with a database crate, behind the same `Store` API.
- Add request logging as tower middleware, which axum supports through tower and tower-http. [55]

:::key-takeaways
- Reuse code across binaries with a workspace: one library, several front ends, one lockfile.
- Keep typed errors in the library and convert them to HTTP statuses at the edge.
- Finish with tests for every route and error, clean lints and docs, and a written design note.
:::

:::glossary
- **Capstone**: a final project that combines what a course taught.
- **Workspace**: several Cargo packages built together with one lockfile.
- **Path dependency**: a dependency on a crate in a local folder instead of crates.io.
- **IntoResponse**: the axum trait for types that can become an HTTP response.
- **Manager task**: a task that owns a resource and serves requests sent to it over a channel.
- **End-to-end test**: a test that exercises the whole running system, as a user would.
- **Middleware**: code that wraps every request, for logging, timeouts or authentication.
:::
