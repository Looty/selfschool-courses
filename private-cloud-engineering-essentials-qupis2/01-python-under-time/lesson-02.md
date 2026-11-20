---
id: l02
title: "Timed problem: log aggregation"
quiz: quiz-02.yaml
resources: [../resources/ch01/log_stats_starter.py, ../resources/ch01/log_stats_solution.py, ../resources/ch01/log_stats_test.py]
sources: [18, 20, 35, 37]
---
Three moves solve this problem: parse a line with `split`, take a percentile by index, compute a rate per group.

## The problem (25 minutes)

One line per request: `<timestamp> <level> <client_ip> <method> <path> <status> <latency_ms>`:

```text
2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5
```

Write `log_stats(lines, top_n=3)`: the top N client IPs by request count, the error rate per minute (status 500 or above), the p95 latency per path, and the count of skipped malformed lines. The full statement is in `log_stats_starter.py`.

**Ask first:** a list or a huge file? (Any iterable, read once.) What is malformed? Tie order? Which percentile?

## Parsing a line: split, count, convert

**Rule:** `line.split()` cuts on any run of spaces; a good line gives exactly 7 pieces, and every conversion that fails raises `ValueError`, so one `try` catches them all [35] [37].

```python
line = "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5"
len(line.split())             # 7: unpack into ts, level, ip, ...
"a  b c".split()              # ['a', 'b', 'c']: no empty pieces
"".split()                    # []: a blank line has 0 pieces
int("2OO")                    # ValueError (letter O)
ipaddress.ip_address("10.0.0.300")    # ValueError
float("nan")                  # nan: parses fine!
```

Trap: `nan` passes the `try`. Add a range check; every comparison with `nan` is false.

```python
0 <= 12.5 < math.inf          # True: keep
0 <= -1.0 < math.inf          # False: negative latency
0 <= float("nan") < math.inf  # False: nan
```

Return `None` for a bad line; the loop counts them.

**Contrast:** `"a  b".split()` gives `['a', 'b']`, but `"a,,b".split(",")` gives `['a', '', 'b']`: an explicit separator keeps empty pieces.

**P1.** A line has a path containing a space: `... GET /api/my vms 200 12.5`. How many pieces does `split()` give, and is the line kept?

## Percentile by index: nearest rank

**Rule:** sort the values; p95 is the value at place `ceil(95 * n / 100)`, counting places from 1.

Prerequisite, rounding up with integers: `//` rounds down. Flip the sign, round down, flip back:

```python
7 // 2           # 3
-7 // 2          # -4: down, away from zero
-(-7 // 2)       # 4: ceil(7 / 2)
-(-8 // 2)       # 4: exact division stays exact
0.07 * 100       # 7.000000000000001: float ceil would give 8
```

The ladder, with `ordered = [10, 20, 30, 40]` (n = 4):

| pct | `pct * n / 100` | place (round up) | value `ordered[place - 1]` |
| --- | --- | --- | --- |
| 25 | 1.0 | 1 | 10 |
| 50 | 2.0 | 2 | 20 |
| 95 | 3.8 | 4 | 40 |
| 0 | 0.0 | 0, raised to 1 | 10 (edge: `max(place, 1)`) |

Edge: with one value, `[7]`, every percentile is 7.

**Contrast:** places count from 1, list indexes from 0.

| Formula, numbers 1 to 20 | Index used | Result |
| --- | --- | --- |
| `ordered[place - 1]`, place 19 | 18 | 19 |
| `ordered[int(0.95 * 20)]` | 19 | 20: off by one |
| `ordered[int(1.0 * 20)]` (p100) | 20 | `IndexError` |

**P2.** What is the nearest-rank p50 of `[5, 1, 3]`?

## A rate per group: count both, divide last

**Rule:** keep a `[requests, errors]` pair per minute; divide only at the end, inside each minute.

```python
minutes = defaultdict(lambda: [0, 0])     # minute -> [requests, errors]
for minute, status in [("10:15", 200), ("10:15", 500),
                       ("10:16", 200), ("10:16", 200), ("10:16", 503)]:
    bucket = minutes[minute]
    bucket[0] += 1
    bucket[1] += status >= 500            # True adds 1, False adds 0
# 10:15 -> [1, 0] -> [2, 1]
# 10:16 -> [1, 0] -> [2, 0] -> [3, 1]
{m: errors / total for m, (total, errors) in minutes.items()}
# {'10:15': 0.5, '10:16': 0.3333333333333333}
```

Edge: a minute exists only once a request arrives, so `total` is never 0. Read `lines` once: looping over a file reads one line at a time [18], and a generator produces values lazily [20].

**Contrast:** one global ratio over the same lines, 2 / 5 = 0.4, hides the bad minute (0.5).

**P3.** Minute 10:20 has statuses 200, 404, 500, 502. What is its error rate?

## Run it

1. With the three `log_stats_*.py` files in one folder, edit the starter; run `python log_stats_test.py`.
2. Stop at 25 minutes, read the solution, run `python log_stats_test.py log_stats_solution` (12 tests, OK). The reference skips blank lines without counting them.

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| `line.split()` | cut on runs of spaces | `"a  b".split()` → `['a', 'b']` |
| `0 <= x < math.inf` | rejects negatives and `nan` | `nan` → `False` |
| `-(-a // b)` | integer round-up | `-(-7 // 2)` → `4` |
| nearest rank | `ordered[ceil(p*n/100) - 1]` | p95 of `[10, 20, 30, 40]` → `40` |

## Answers

**P1.** 8 pieces, so the line is skipped as malformed.

**P2.** 3. Sorted `[1, 3, 5]`; place `ceil(1.5) = 2`.

**P3.** 0.5: 500 and 502 count; 404 does not.

**R1.** `False`, so the line is rejected.

**R2.** 0 pieces, not 7.

**R3.** Place 4, value 40.

**R4.** 0.5; the global 1 / 10 hides it.

**R5.** One line at a time.

**R6.** 3: `-9 // 4` is -3, flipped to 3, the ceiling of 2.25.

## If you missed a quiz question

| If you thought... | Reread | Re-check |
| --- | --- | --- |
| A `try` around `float()` rejects `nan` | Parsing | **R1.** What is `0 <= float("nan") < math.inf`? |
| A blank line splits into 7 empty fields | Parsing | **R2.** How many pieces does `"".split()` give? |
| p95 is `ordered[int(0.95 * n)]` | Percentile | **R3.** Nearest-rank p95 of `[10, 20, 30, 40]`? |
| The minus signs in `-(-a // b)` cancel | Percentile, prerequisite | **R6.** `-(-9 // 4)`? |
| A global ratio gives the rate per minute | Rate per group | **R4.** Minute A: 1 error in 2; minute B: 0 in 8. Rate for A? |
| `for line in f` loads the whole file | Rate per group | **R5.** What does `for line in f` read per step? |

:::key-takeaways
- Split, check 7 pieces, convert in one `try`, then range-check. [35] [37]
- Nearest rank: sort, place `ceil(p * n / 100)`, index `place - 1`.
- Count per minute, divide at the end; read the input once. [18]
:::

:::glossary
- **Malformed line**: a line that breaks the format; it is counted, not processed.
- **nan**: "not a number", a float for which every comparison is false.
- **Percentile (p95)**: the value below which about 95 percent of the values fall.
- **Nearest rank**: a percentile rule that picks a real value at place ceil(p * n / 100).
- **Generator**: a function that hands out values one at a time.
:::
