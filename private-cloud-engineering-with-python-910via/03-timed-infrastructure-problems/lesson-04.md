---
id: l09
title: "Exercise: caches and rate limiters"
quiz: quiz-04.yaml
resources: [../resources/ch03/lru_cache_class_starter.py, ../resources/ch03/lru_cache_class_solution.py, ../resources/ch03/lru_cache_class_test.py, ../resources/ch03/rate_limiter_starter.py, ../resources/ch03/rate_limiter_solution.py, ../resources/ch03/rate_limiter_test.py]
sources: [9, 11, 14, 38, 51, 53]
---
After this lesson you can write an LRU cache with O(1) operations and an optional expiry time, and token-bucket and sliding-window rate limiters, all with an injectable clock so the tests never wait.

## Shortcut

Download the six files into one folder:

```bash
python lru_cache_class_test.py                    # your starter
python lru_cache_class_test.py lru_cache_class_solution
python rate_limiter_test.py
python rate_limiter_test.py rate_limiter_solution
```

In the course's test run the references printed `Ran 10 tests` and `OK` for both files on Python 3.13 and 3.11 in a few milliseconds, and the untouched starters failed only with `NotImplementedError`.

## Why the clock is injected

Both problems depend on time. Code that calls `time.sleep(30)` in a test makes the test take 30 seconds and flaky. Instead, the class takes `clock`, a function returning seconds, defaulting to `time.monotonic`. `time.monotonic()` is a clock that cannot go backwards and is not affected by system clock updates, so it suits timeouts and elapsed time; `time.time()` can return a lower value if the system clock is set back [38]. A test passes a fake clock object and moves its `now` attribute forward by hand.

## Problem A: LRU cache with optional TTL (15 minutes)

Write `LRUCache(capacity, ttl=None, clock=time.monotonic)` with `get(key, default=None)`, `put(key, value)` and `__len__`, each O(1). An LRU (least recently used) cache evicts the entry unused for longest. `get` hit makes the key most recent. `put` restarts the TTL (time to live: seconds before an entry expires); `get` does not extend it. An entry put at time t expires at t + ttl.

**Questions worth asking:** What happens at exactly t + ttl? Does a read refresh the TTL? Does replacing a value count as use? What if `capacity < 1`? Must a stored `None` be distinguishable from a miss?

**Hints.** An `OrderedDict` remembers insertion order and has `move_to_end(key)` and `popitem(last=False)`; the docs say it suits LRU caches [9]. Store `(value, expires_at)` as the value.

### Walkthrough

```python
class LRUCache:
    def __init__(self, capacity, ttl=None, clock=time.monotonic):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity, self.ttl, self.clock = capacity, ttl, clock
        self._data = OrderedDict()

    def get(self, key, default=None):
        entry = self._data.get(key)
        if entry is None:
            return default
        value, expires_at = entry
        if expires_at is not None and self.clock() >= expires_at:
            del self._data[key]
            return default
        self._data.move_to_end(key)
        return value

    def put(self, key, value):
        expires_at = None if self.ttl is None else self.clock() + self.ttl
        self._data[key] = (value, expires_at)
        self._data.move_to_end(key)
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)
```

Because the stored value is a tuple, a cached `None` is `(None, ...)` and never confused with a miss. Expired entries are removed lazily on access, so `len()` may still count one that nobody has touched; the starter docstring says so. The `move_to_end` after assignment is needed because assigning to an existing key keeps its old position.

**Complexity.** O(1) average per operation; O(capacity) space. Alternative: a plain `dict` also keeps insertion order, so `d[k] = d.pop(k)` moves a key to the end and `next(iter(d))` is the oldest; the docs describe these emulations [9]. If you may not use `OrderedDict`, write a dict plus a doubly linked list by hand.

**The built-in.** `functools.lru_cache` memoises a function's results: `@lru_cache(maxsize=128)` keeps the most recent calls, arguments must be hashable, `cache_info()` reports hits and misses, and `maxsize=None` disables eviction [11]. Do not cache impure functions such as `time()` or `random()` [11]. It has no TTL, which is why this exercise exists.

## Problem B: per-client rate limiters (15 minutes)

`TokenBucketLimiter(rate, burst, clock)`: each client has a bucket of at most `burst` tokens that starts full and refills at `rate` per second; `allow(client)` spends one token or returns `False`. `SlidingWindowLimiter(limit, window, clock)`: `allow(client)` is true if the client had fewer than `limit` allowed requests with timestamps in `(now - window, now]`, and then records this one. Rejected requests are not recorded.

A service answers a rejected request with HTTP 429 Too Many Requests, which may carry a `Retry-After` header [53].

**Hints.** Token bucket: do not run a timer. On each call compute `tokens = min(burst, tokens + elapsed * rate)`, a lazy refill. Sliding window: a `deque` of timestamps per client; pop from the left while the oldest is outside the window.

### Walkthrough

```python
def allow(self, client):                      # TokenBucketLimiter
    now = self.clock()
    bucket = self._buckets.get(client)
    if bucket is None:
        bucket = self._buckets[client] = [float(self.burst), now]
    tokens, last = bucket
    tokens = min(self.burst, tokens + (now - last) * self.rate)
    bucket[1] = now
    if tokens >= 1:
        bucket[0] = tokens - 1
        return True
    bucket[0] = tokens
    return False
```

Rejections must still store the refilled `tokens` and `now`, or the elapsed time would be counted twice on the next call.

```python
def allow(self, client):                      # SlidingWindowLimiter
    now = self.clock()
    times = self._log[client]
    while times and times[0] <= now - self.window:
        times.popleft()
    if len(times) < self.limit:
        times.append(now)
        return True
    return False
```

The boundary is half-open: with a window of 10, a request at time 0 stops counting at exactly time 10, matching `(now - window, now]`.

**Complexity.** Token bucket O(1) time and space per client. Sliding window O(1) amortised, since each timestamp is appended and removed once, with up to `limit` stored per client. Alternative: a fixed-window counter needs one number per client but can let through almost twice the limit around a window edge. In Redis, the data types page names a sorted set as the structure for a sliding-window rate limiter, with most operations O(log n) [51]. Both classes here also keep idle clients forever; a real service would expire them. Dict lookups are O(1) on average [14].

## Gotchas

- **Real sleeps in tests.** Inject the clock; never `time.sleep` in a test.
- **Wall clock for durations.** `time.time()` can jump backwards when the system clock is set back; use `time.monotonic()`. [38]
- **Forgetting `move_to_end` on update.** Assigning an existing key leaves it in its old place, so a just-updated entry can be evicted first. [9]
- **Recording rejected requests in a sliding window.** A client who keeps retrying then never recovers.
- **One global bucket.** Limiters are per client; keep state in a dict keyed by client.
- **`lru_cache` on methods with mutable state.** `functools.lru_cache` needs hashable arguments and is for pure functions. [11]

## Follow-up variation

The service now runs on several processes behind a load balancer. An in-memory limiter allows each process its own quota, so the real limit is multiplied. Discuss moving the state to a shared store: a Redis key with an expiry for a fixed window, or a sorted set for a sliding one [51], and what changes when two requests from one client race on the same counter (the check and the increment must be one atomic step).

:::key-takeaways
- Inject the clock so tests control time; `time.monotonic` is the right default clock. [38]
- `OrderedDict` with `move_to_end` and `popitem(last=False)` gives an O(1) LRU cache. [9]
- `functools.lru_cache` is the built-in for pure functions; it has no TTL. [11]
- Token bucket: lazy refill, `min(burst, tokens + elapsed * rate)`. Sliding window: a deque of timestamps trimmed on each call.
- A limited client gets HTTP 429, optionally with `Retry-After`. [53]
:::

:::glossary
- **LRU (least recently used)**: an eviction rule that discards the entry that has gone unused the longest.
- **TTL (time to live)**: how many seconds a cache entry stays valid.
- **Token bucket**: a limiter that spends one token per request and refills tokens at a steady rate up to a maximum.
- **Sliding window**: a limiter that counts requests in the most recent period of fixed length.
- **Injectable clock**: a time source passed in as an argument so tests can control it.
- **Monotonic clock**: a clock that never goes backwards, used for measuring elapsed time.
- **HTTP 429**: the status code a server sends when a client has made too many requests.
:::
