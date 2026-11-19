---
id: l11
title: "Threads, pools, asyncio and the GIL"
quiz: quiz-02.yaml
resources: [../resources/ch04/parallel_health_check_starter.py, ../resources/ch04/parallel_health_check_solution.py, ../resources/ch04/parallel_health_check_test.py, ../resources/ch04/retry_backoff_starter.py, ../resources/ch04/retry_backoff_solution.py, ../resources/ch04/retry_backoff_test.py]
sources: [22, 23, 28, 29, 30, 31, 38, 44]
---
After this lesson you can choose between threads, processes and asyncio for a given job, explain what the GIL does, run checks in a `ThreadPoolExecutor` with timeouts and error handling, and write a retry helper with exponential backoff that tests can run instantly.

## Shortcut

Download the six files into one folder:

```bash
python parallel_health_check_test.py                          # your starter
python parallel_health_check_test.py parallel_health_check_solution
python retry_backoff_test.py
python retry_backoff_test.py retry_backoff_solution
```

In the course's test run both references passed on Python 3.13 and 3.11: `Ran 8 tests` in about 0.5 s for the health check (its tests use short real waits, 0.1 to 0.2 s) and `Ran 9 tests` in a few milliseconds for the retry helper, which never really sleeps. The untouched starters failed only with `NotImplementedError`. The health check was run five times in a row without a flaky failure.

## Which tool for which job

| Job | Use | Why |
| --- | --- | --- |
| Many blocking I/O calls (HTTP, SSH, DNS, files) | Threads (`ThreadPoolExecutor`) | Threads are "particularly useful when tasks are I/O bound" [29] |
| CPU-heavy Python work (parsing, hashing, number crunching) | Processes (`ProcessPoolExecutor`) | It side-steps the GIL [28] |
| Thousands of sockets, one thread of control | `asyncio` | Tasks switch at `await` points [31] |

## The GIL

In CPython, because of the Global Interpreter Lock (GIL), "only one thread can execute Python code at once" [29]. So threads do not speed up CPU-bound Python code, but while a thread waits on I/O another can run. As of Python 3.13 a separate free-threaded build can disable the GIL, but it is not available by default [29]. The free-threaded build is officially supported and no longer experimental since 3.14, still optional, and whether it becomes the default is undecided [22]. Details from the free-threading HOWTO: you detect it with `python -VV` or `sys._is_gil_enabled()`, a C extension that is not marked as supporting it can turn the GIL back on, and built-in types use internal locks, but the page recommends your own `threading.Lock` for shared data [44]. For this course's code, assume the GIL is on. The interview platform in chapter 1 lists Python 3.14.2, while the current docs are 3.15 [23].

## ThreadPoolExecutor

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(check, host): host for host in hosts}
    for fut in as_completed(futures):
        host = futures[fut]
        try:
            print(host, fut.result())
        except Exception as exc:
            print(host, "failed:", exc)
```

`submit(fn, *args)` returns a `Future`. `result(timeout=None)` returns the value, raises `TimeoutError` if not done in time, and, if the call raised, re-raises the same exception [28]. So exceptions surface at `result()`, not at `submit()`. `as_completed(fs)` yields futures as they finish; `map(fn, *iterables)` is like the built-in `map` but runs calls concurrently, and its example pairs inputs with results using `zip`, relying on input order [28]. If a call raises, the exception appears when you reach its value in the iterator [28]. Using the executor in a `with` block calls `shutdown(wait=True)` on exit [28]. The default `max_workers` is `min(32, (os.process_cpu_count() or 1) + 4)` since 3.13 [28].

**Lock and Queue.** A `threading.Lock` has two states and is created unlocked; `acquire()` blocks until it is free and `release()` unlocks it, and `with lock:` does both safely [29]. Use it around any read-modify-write on shared data. A `queue.Queue` is the safer default for passing work between threads: it implements all the locking, `put` and `get` can block or take a timeout (raising `Full` or `Empty`), and `task_done()` plus `join()` let you wait until all items are processed [30].

## asyncio in one screen

`async def` defines a coroutine function; calling it only creates a coroutine object, which does not run until awaited or scheduled [31]. `asyncio.run(main())` is the entry point [31].

```python
import asyncio

async def check(host):
    await asyncio.sleep(0.1)          # stands in for a network call
    return host, True

async def main(hosts):
    async with asyncio.timeout(2):
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(check(h)) for h in hosts]
    return [t.result() for t in tasks]

print(asyncio.run(main(["hv1", "hv2"])))
```

`gather(*aws, return_exceptions=False)` returns results in the same order as its arguments; with the default, the first exception propagates and the other awaitables keep running, while `return_exceptions=True` puts exceptions in the result list [31]. `asyncio.TaskGroup` (added in 3.11) cancels the remaining tasks when one fails and raises an `ExceptionGroup` [31]. `asyncio.timeout(delay)` is an async context manager that turns a cancellation into `TimeoutError`, catchable only outside the `async with` [31]. `asyncio.to_thread(func, ...)` runs a blocking function in a thread so it does not block the event loop; because of the GIL it mainly helps I/O-bound functions [31]. Keep a reference to a task you create: the loop holds only weak references, so an unreferenced task may be garbage collected before it finishes [31].

:::low-confidence
`TaskGroup.cancel()` is new in Python 3.15 [31] [23], so it is unavailable on the 3.14.2 platform and the course's code avoids it. The asyncio code above was not run by the course's test files; only the thread-pool and retry exercises were tested.
:::

## Exercise A: parallel_health_check (20 minutes)

Write `parallel_health_check(hosts, check, timeout=2.0, max_workers=None)`. Run `check(host)` for every host in a thread pool and return `[(host, status, detail), ...]` in input order, with status `up`, `down`, `error` or `timeout`. It must never raise, and must return soon after `timeout` even if some checks are still blocked. Ask: what does a falsy return mean (down)? Is the timeout per host or overall (here: from when the checks start)? What format for error detail?

**Hints.** Keep the futures in a list parallel to `hosts`, so order is free. `concurrent.futures.wait(futures, timeout=...)` returns `(done, not_done)` [28]. Check `future in done`, then call `result()` inside `try/except Exception`.

### Walkthrough

```python
pool = ThreadPoolExecutor(max_workers=workers)
try:
    futures = [pool.submit(check, host) for host in hosts]
    done, _ = wait(futures, timeout=timeout)
    results = []
    for host, fut in zip(hosts, futures):
        if fut not in done:
            fut.cancel()
            results.append((host, "timeout", f"no answer within {timeout}s"))
            continue
        try:
            healthy = fut.result()
        except Exception as exc:
            results.append((host, "error", f"{type(exc).__name__}: {exc}"))
        else:
            results.append((host, "up" if healthy else "down", ""))
    return results
finally:
    pool.shutdown(wait=False, cancel_futures=True)
```

The pool is not used in a `with` block on purpose: `with` calls `shutdown(wait=True)` and would wait for the hanging check, defeating the timeout [28]. `cancel_futures=True` cancels pending futures that have not started; running ones are never cancelled [28]. A thread already blocked in `check` cannot be killed, so it keeps running in the background. Note the docs: whatever `wait` is, the whole Python program will not exit until all pending futures are done [28]. A real check should therefore also have its own socket timeout. **Complexity:** O(N) in the caller; wall time is about the longest check, capped by `timeout`, when there are at least N workers.

## Exercise B: retry_backoff (15 minutes)

Write `retry_call(func, *, attempts=5, base_delay=0.5, max_delay=8.0, retry_on=(Exception,), jitter=None, sleep=time.sleep)` and a `retrying(**options)` decorator. The wait before retry n (0-based) is `min(max_delay, base_delay * 2 ** n)`, passed through `jitter` (default: full jitter, `random.uniform(0, delay)`). Never sleep after the last attempt; re-raise that attempt's exception unchanged; an exception not in `retry_on` propagates at once. Jitter is a random spread added to each wait so many clients that failed together do not all retry together.

### Walkthrough

```python
def retry_call(func, *, attempts=5, base_delay=0.5, max_delay=8.0,
               retry_on=(Exception,), jitter=None, sleep=time.sleep):
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    jitter = jitter or full_jitter
    for n in range(attempts):
        try:
            return func()
        except retry_on:
            if n == attempts - 1:
                raise
            sleep(jitter(min(max_delay, base_delay * 2 ** n)))
```

Injecting `sleep` and `jitter` is what makes it testable: a test passes `slept.append` and `lambda d: d` and asserts `slept == [1, 2, 4, 8, 10]`. The decorator wraps the function with `functools.wraps` so `__name__` and `__doc__` survive. If you need a deadline rather than an attempt count, measure elapsed time with `time.monotonic()` [38]. **Complexity:** at most `attempts` calls and `attempts - 1` sleeps, O(1) space.

## Gotchas

- **Exceptions vanish until `result()`.** A failed `submit` shows nothing until you call `result()` or `exception()`; a fire-and-forget future hides the error. [28]
- **`with ThreadPoolExecutor` and a hung task.** The `with` exit waits for everything; use `shutdown(wait=False, cancel_futures=True)` when you must return on time. [28]
- **Threads for CPU-bound work.** Under the GIL one thread runs Python code at a time, so no speed-up. Use processes. [29]
- **Process pools and the 3.14 start method.** On Unix other than macOS the default start method is now `forkserver`, not `fork`, so code that relied on inherited state can break. [22]
- **Calling a coroutine without `await`.** It creates a coroutine object that never runs; Python warns. [31]
- **Unreferenced tasks.** Keep a reference to anything from `create_task`. [31]
- **Retrying everything.** Retrying on a bad request (a `ValueError`) only repeats the failure; list the transient errors in `retry_on`.
- **Using 3.15 features.** `TaskGroup.cancel()` is 3.15 only. [23]

## Follow-up variation

The health check must be capped at 50 checks in flight across a fleet of 5,000 hosts, and report results as they arrive. Discuss `max_workers=50` with `as_completed`, a `Semaphore` in asyncio, and why `wait(timeout=...)` for the whole batch is no longer the right model: each host needs its own deadline, which means a per-check socket timeout or `asyncio.timeout` inside each task.

:::key-takeaways
- Threads for blocking I/O, processes for CPU, asyncio for many sockets. [29] [28] [31]
- The default CPython build has the GIL; the free-threaded build is optional. [29] [44] [22]
- Exceptions in pool tasks re-raise from `Future.result()`. [28]
- `with ThreadPoolExecutor` waits at exit; use `shutdown(wait=False, cancel_futures=True)` to stop waiting. [28]
- Inject `sleep`, `jitter` and clocks so retry and timeout code tests instantly.
:::

:::glossary
- **GIL (Global Interpreter Lock)**: the lock that lets only one thread run Python code at a time in standard CPython.
- **ThreadPoolExecutor**: a pool of worker threads that runs submitted functions.
- **Future**: an object representing a result that may not be ready yet.
- **asyncio**: Python's library for running many tasks on one thread by switching at `await`.
- **Coroutine**: a function defined with `async def` that can pause at `await`.
- **TaskGroup**: an asyncio context manager that runs a group of tasks and cancels the rest if one fails.
- **Exponential backoff**: waiting longer after each failure, doubling the delay up to a maximum.
- **Jitter**: a random amount added to or taken from a wait time.
- **Free-threaded build**: a CPython build with the GIL disabled.
:::
