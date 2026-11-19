---
id: l06
title: "Exercise: log aggregation"
quiz: quiz-01.yaml
resources: [../resources/ch03/log_stats_starter.py, ../resources/ch03/log_stats_solution.py, ../resources/ch03/log_stats_test.py]
sources: [8, 9, 12, 13, 14, 18, 20, 35, 37]
---
After this lesson you can parse a stream of log lines in one pass, skip the broken ones, and report the busiest clients, the error rate per minute and the 95th percentile latency per path, in about 25 minutes.

## Shortcut

Download the three `log_stats_*.py` files into one folder and run the tests against your own starter, then against the reference:

```bash
python log_stats_test.py                    # tests your log_stats_starter.py
python log_stats_test.py log_stats_solution # tests the reference solution
```

In the course's test run the reference printed `Ran 12 tests` and `OK` on Python 3.13 and 3.11, and the untouched starter printed `FAILED (errors=24)`, every error a `NotImplementedError`, so the file imports cleanly and fails only where you have not written code yet.

## The problem (25 to 30 minutes)

A service writes one line per request: `<timestamp> <level> <client_ip> <method> <path> <status> <latency_ms>`, for example `2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5`. Write `log_stats(lines, top_n=3)` returning the top N client IPs by request count, the error rate per minute (status 500 or above, divided by requests in that minute) and the p95 latency per path, plus a count of skipped malformed lines. The full statement is the docstring of `log_stats_starter.py`.

**Clarifying questions worth asking** before typing: Is `lines` a list or a file too large for memory? (Here: any iterable, read once.) What makes a line malformed? How are ties in the top N ordered? Which percentile definition? Are blank lines errors? Spending two minutes on these is part of the exercise, because each answer removes a branch from the code.

## Hints

1. Split a line with `str.split()` and check there are exactly seven fields. Do all validation in one `parse_line` function that returns a tuple or `None`.
2. `datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ")` raises `ValueError` on a bad timestamp [37]. `ipaddress.ip_address()` raises `ValueError` on an invalid address [35]. One `try/except ValueError` covers the timestamp, address, status and latency conversions.
3. Count with a `Counter`; group with a `defaultdict` [9]. `Counter.most_common()` keeps first-seen order among equal counts, which is not the tie-break the problem asks for, so sort `(-count, ip)` yourself.
4. Nearest-rank percentile: sort the values and take the one at 1-based rank `ceil(0.95 * n)`.

## Walkthrough

The reference solution has three pieces: a validating parser, a percentile helper and a single loop.

```python
def parse_line(line):
    parts = line.split()
    if len(parts) != 7:
        return None
    ts, level, ip, _method, path, status, latency = parts
    try:
        when = datetime.strptime(ts, TS_FORMAT)
        ipaddress.ip_address(ip)
        status = int(status)
        latency = float(latency)
    except ValueError:
        return None
    if level not in LEVELS or not path.startswith("/"):
        return None
    if not 100 <= status <= 599:
        return None
    if not 0 <= latency < math.inf:
        return None
    return when.strftime("%Y-%m-%dT%H:%M"), ip, path, status, latency
```

The last check does two jobs: it rejects negative latencies and also `nan`, because every comparison with `nan` is false. `float("nan")` parses without error, so a try/except alone lets it through; the test file includes that line.

```python
def percentile(values, pct):
    ordered = sorted(values)
    rank = -(-pct * len(ordered) // 100)     # ceil in integer arithmetic
    return ordered[max(rank, 1) - 1]
```

Integer ceiling avoids floating point surprises at exact boundaries: for 20 values, `0.95 * 20` can land just above or below 19.0 as a float, but `95 * 20 // 100` is exact.

The main loop reads the input once, so it works on a list, an open file or a generator. Iterating a file object line by line is memory efficient [18], and a generator function produces values lazily [20], so a 10 GB log never has to fit in memory. Per line it updates a `Counter` of IPs, a `[requests, errors]` pair per minute and a list of latencies per path. Only the latency lists grow with the input.

At the end, rank the IPs with `sorted(requests.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]`. Sorting is stable and the key function runs once per record [12].

**Complexity.** With L lines the loop is O(L). Ranking U distinct IPs costs O(U log U), because `list.sort()` is O(n log n) [14]. The percentile sorts cost O(L log L) in the worst case. Space is O(U + M + L) for IPs, minutes and stored latencies. Alternative: `heapq.nlargest(n, ...)` is the better tool when U is huge and N small, though the docs say it performs best for small n [8]. A fixed-bucket histogram per path gives an approximate p95 in constant memory.

## Gotchas

- **Counting blank lines as malformed.** A trailing newline at end of file yields an empty line. Decide the rule up front and test it. [18]
- **`most_common()` ties.** Equal counts come out in first-seen order, so the result changes with input order. Sort on `(-count, ip)` for a deterministic answer. [9]
- **Percentile of an empty list.** A path with no valid lines never enters the dict, so `percentile` is never called on `[]`. Group first, compute after.
- **Keeping every line.** `lines = list(lines)` or `read().splitlines()` defeats the generator requirement and fails on large input. [18] [20]
- **Averaging per-minute rates.** Compute errors divided by requests inside each minute; averaging ratios across minutes weights quiet minutes as much as busy ones.
- **`float("nan")` and negative numbers parse fine.** Validate the range, not only the conversion.

## Follow-up variation

Suppose the log arrives continuously and the dashboard wants the p95 of the last five minutes, refreshed every second. Storing all latencies no longer works. Discuss keeping a deque of `(timestamp, latency)` per path and dropping entries older than five minutes, then the cost of re-sorting on every refresh, and why a sorted list kept with `bisect.insort` (O(n) insertion, per the docs [13]) or an approximate histogram trades exactness for speed.

:::key-takeaways
- Read the input once, line by line; validate every field in one parser that returns `None` for bad lines. [18] [20]
- `strptime` and `ip_address` raise `ValueError`, so one `except ValueError` guards the conversions. [35] [37]
- Group first, sort at the end; sort keys like `(-count, name)` make ties deterministic. [12]
- Nearest-rank p95 is the value at rank `ceil(0.95 * n)` of the sorted list.
:::

:::glossary
- **Malformed line**: a log line that breaks the format rules and is counted, not processed.
- **Percentile (p95)**: the value below which 95 percent of the observations fall.
- **Nearest-rank**: a percentile rule that picks an actual observed value at rank ceil(p * n).
- **Generator**: a function that yields values one at a time instead of building a whole list.
- **Error rate**: failed requests divided by all requests in the same period.
:::
