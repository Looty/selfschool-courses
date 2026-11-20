---
id: l02
title: "Timed problem: log aggregation"
quiz: quiz-02.yaml
resources: [../resources/ch01/log_stats_starter.py, ../resources/ch01/log_stats_solution.py, ../resources/ch01/log_stats_test.py]
sources: [9, 12, 18, 20, 35, 37]
---
After this lesson you can parse a stream of log lines in one pass, skip the broken ones, and report the busiest clients, the error rate per minute and the p95 latency per path, in about 25 minutes.

## The problem (25 minutes)

One line per request: `<timestamp> <level> <client_ip> <method> <path> <status> <latency_ms>`, for example:

```text
2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5
```

Write `log_stats(lines, top_n=3)` returning the top N client IPs by request count, the error rate per minute (status 500 or above divided by requests in that minute), the p95 latency per path, and a count of skipped malformed lines. The full statement is the docstring of `log_stats_starter.py`.

**Ask first** (two minutes, each answer removes a branch): is `lines` a list or a huge file? (Any iterable, read once.) What makes a line malformed? How are ties in the top N ordered? Which percentile definition? Are blank lines errors?

## The plain shape

Three pieces: a parser that returns a tuple or `None`, a percentile helper, and one loop over the input.

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
    if not 100 <= status <= 599 or not 0 <= latency < math.inf:
        return None
    return when.strftime("%Y-%m-%dT%H:%M"), ip, path, status, latency
```

`strptime` and `ip_address` both raise `ValueError` on bad input, so one `except` covers every conversion [35] [37].

```python
def percentile(values, pct):
    ordered = sorted(values)
    rank = -(-pct * len(ordered) // 100)     # integer ceil
    return ordered[max(rank, 1) - 1]
```

Nearest-rank: the value at 1-based rank `ceil(0.95 * n)`. Integer arithmetic avoids float surprises at exact boundaries.

```python
skipped = 0
requests = {}                    # ip -> count
minutes = {}                     # minute -> [requests, errors]
latencies = {}                   # path -> [ms, ...]
for line in lines:               # one pass, works on a file or a generator
    rec = parse_line(line)
    if rec is None:
        skipped += 1
        continue
    minute, ip, path, status, ms = rec
    requests[ip] = requests.get(ip, 0) + 1
    m = minutes.setdefault(minute, [0, 0])
    m[0] += 1
    m[1] += status >= 500
    latencies.setdefault(path, []).append(ms)

top = sorted(requests.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
```

Shortcuts: `Counter` for `requests`, `defaultdict(list)` for `latencies` [9]. Looping over a file object reads one line at a time [18], and a generator yields values lazily [20], so a 10 GB log never has to fit in memory. Sorting is stable and the key runs once per record [12].

**Complexity.** O(L) for the loop, O(U log U) to rank U distinct IPs, O(L log L) worst case for the percentile sorts.

## Gotchas that cost time

- **`most_common()` ties.** Equal counts come out in first-seen order; sort on `(-count, ip)` instead. [9]
- **`float("nan")` parses.** A `try` alone lets it through. `0 <= latency < math.inf` rejects it, because every comparison with `nan` is false; the tests include that line.
- **Loading everything.** `list(lines)` or `read().splitlines()` defeats the one-pass requirement. [18] [20]
- **Averaging ratios.** Divide errors by requests inside each minute, not across the whole log.
- **Blank last line.** A trailing newline yields an empty line. Decide the rule and test it. [18]

## Run it

1. Put the three `log_stats_*.py` files in one folder.
2. Edit `log_stats_starter.py`, then run `python log_stats_test.py`. The untouched starter fails only with `NotImplementedError`.
3. Stop at 25 minutes, then read the solution and run `python log_stats_test.py log_stats_solution` (12 tests, OK).

**Follow-up to discuss:** a p95 over the last five minutes, refreshed every second. Keep a `deque` of `(timestamp, latency)` per path and drop old entries, then talk about the cost of re-sorting on every refresh.

:::key-takeaways
- Read the input once; one parser returns `None` for bad lines. [18] [20]
- One `except ValueError` guards the timestamp, address and number conversions. [35] [37]
- Group first, rank at the end with a `(-count, name)` key. [12]
- Validate ranges, not only conversions: `nan` and negatives parse fine.
:::

:::glossary
- **Malformed line**: a log line that breaks the format rules and is counted, not processed.
- **Percentile (p95)**: the value below which 95 percent of the observations fall.
- **Nearest-rank**: a percentile rule that picks an actual observed value at rank ceil(p * n).
- **Error rate**: failed requests divided by all requests in the same period.
:::
