---
id: l05
title: "Text and data: re, json, datetime, ipaddress"
quiz: quiz-05.yaml
resources: [../resources/ch02/parse_log_line_starter.py, ../resources/ch02/parse_log_line_solution.py, ../resources/ch02/parse_log_line_test.py, ../resources/ch02/json_flatten_starter.py, ../resources/ch02/json_flatten_solution.py, ../resources/ch02/json_flatten_test.py, ../resources/ch02/subnet_report_starter.py, ../resources/ch02/subnet_report_solution.py, ../resources/ch02/subnet_report_test.py]
sources: [23, 24, 25, 26, 35, 36, 37, 38]
---
After this lesson you can parse a log line with a regular expression, round-trip JSON, do date arithmetic without mixing naive and aware times, and answer subnet questions with `ipaddress`.

## Regular expressions

Write patterns as raw strings, `r"\d+"`, so Python does not treat the backslash as an escape. [24] [25]

```python
import re
re.search(r"\d+", "vm 42 up")       # first match anywhere, or None
re.match(r"\d+", "vm 42 up")        # only at the start -> None
re.fullmatch(r"\d+", "42")          # the whole string must match
```

`search` scans the string, `match` checks only the start, `fullmatch` needs the entire string; all return `None` on failure, so test the result before calling `.group()`. [24] [25] Since 3.15 the docs prefer the name `prefixmatch()` for `match()`, but it does not exist on older Pythons and the page says code that supports older versions should keep `match()`. [24] [23] This course uses `match` and `fullmatch`.

```python
m = re.search(r"(?P<host>[\w.-]+):(?P<port>\d+)", "to db-1.lab:5432 ok")
m.group("host"), m["port"]                  # ('db-1.lab', '5432')
m.groupdict()                               # {'host': 'db-1.lab', 'port': '5432'}
re.findall(r"(\w+)=(\d+)", "w=20 h=10")     # [('w', '20'), ('h', '10')]
[x.span() for x in re.finditer(r"\d+", "a1 b22")]   # [(1, 2), (4, 6)]
re.sub(r"\s+", " ", "a   b \n c")           # 'a b c'
pat = re.compile(r"\d+", re.IGNORECASE)     # reuse a compiled pattern
```

Group 0 is the whole match; named groups are `(?P<name>...)`, read with `m.group("name")`, `m["name"]` or `m.groupdict()`. [24] `findall` returns strings for no groups or one group, and tuples for several. [24] `finditer` yields match objects. [24] `sub` also accepts a function that receives the match. [24]

**Greedy versus lazy.** `*`, `+` and `?` take as much as possible; add `?` to take as little as possible. [24]

```python
re.search(r"<.*>", "<a> b <c>").group()    # '<a> b <c>'
re.search(r"<.*?>", "<a> b <c>").group()   # '<a>'
```

Flags: `re.I` ignore case, `re.M` makes `^` and `$` work per line, `re.S` lets `.` match newline, `re.X` allows whitespace and comments in the pattern; combine with `|`. [24] `\d`, `\w` and `\s` match Unicode characters for `str` patterns unless `re.ASCII` is given. [24] For fixed text prefer `str` methods, which are usually faster. [25]

## json

```python
import json
s = json.dumps({"b": 1, "a": [1, None, True]}, sort_keys=True, indent=2)
data = json.loads('{"x": 1.5}')
```

`dumps` returns a `str` and `dump` writes to a file object; `loads` takes a `str`, `bytes` or `bytearray`. [26] `indent` pretty-prints and `sort_keys` orders keys. [26] The mapping is object to `dict`, array to `list`, string to `str`, int and float numbers to `int` and `float`, `true` and `false` to `True` and `False`, `null` to `None`; tuples become arrays. [26] JSON keys are always strings, so `loads(dumps({1: "a"}))` gives `{'1': 'a'}`. [26] Invalid text raises `JSONDecodeError`, a subclass of `ValueError`. [26] A top-level value need not be an object. [26] Duplicate keys: the last one wins. [26]

## datetime and time

```python
from datetime import datetime, timedelta, timezone
t = datetime.fromisoformat("2026-11-19T08:00:00+00:00")     # aware
datetime.strptime("19/11/26 16:30", "%d/%m/%y %H:%M")        # naive
t.strftime("%Y-%m-%dT%H:%M:%S%z")                            # '2026-11-19T08:00:00+0000'
(t + timedelta(hours=25, minutes=30)).isoformat()
datetime.now(timezone.utc)                                   # aware "now"
```

Codes: `%Y` year, `%m` month, `%d` day, `%H` 24-hour, `%M` minute, `%S` second, `%f` microseconds, `%z` offset; `strptime` parses, `strftime` formats. [37] An **aware** datetime knows its offset; a **naive** one does not, and subtracting one from the other raises `TypeError`; they are also never equal. [37] `timedelta` keeps days, seconds and microseconds, so use `total_seconds()` for the whole duration rather than `.seconds`. [37] Always give a year when parsing month and day, because the default year 1900 is not a leap year; since 3.15 `%d` without a year is an error. [37] `datetime.utcnow()` is deprecated; use `datetime.now(timezone.utc)`. [37]

To time a block, use `time.monotonic()`, a clock that cannot go backwards and is not affected by system clock updates; only the difference between two calls is meaningful. [38] `time.time()` can jump if the system clock is set back. [38]

## ipaddress

```python
import ipaddress
net = ipaddress.ip_network("10.0.0.5/24", strict=False)   # 10.0.0.0/24
ipaddress.ip_address("10.0.0.9") in net                   # True
next(net.hosts()), net.num_addresses                      # 10.0.0.1, 256
list(net.subnets(new_prefix=26))                          # four /26 networks
ipaddress.ip_network("10.0.0.5/24")    # ValueError: 10.0.0.5/24 has host bits set
```

`ip_network` raises `ValueError` when host bits are set unless `strict=False`. [35] [36] `hosts()` is an iterator of the usable addresses, all except the network and broadcast address; for a /31 both are returned and for a /32 the single address. [35] A network works as a container: `addr in net`, `net[0]`, `net.num_addresses`. [35] [36] Addresses compare and sort, and comparing versions or types raises `TypeError`. [36] Convert with `str(addr)` or `int(addr)` for other modules. [36]

## Drills

Edit the starter, run `python name_test.py`, and add `name_solution` to test the reference. In the course's test run every solution passed on Python 3.13 and 3.11 and every starter failed with `NotImplementedError`.

1. **`parse_log_line`** (8 minutes, 12 tests). Named groups into a dict. Hint: `fullmatch` with `.*` for the message. Walkthrough: one compiled pattern, strip exactly one trailing newline, return `match.groupdict()`; O(L). Mistake: `search` lets text before the timestamp through; `strip()` eats the message's trailing spaces.
2. **`json_flatten`** (7 minutes, 11 tests). Dotted keys for nested objects and lists. Hint: a recursive helper with a prefix. Walkthrough: `json.loads`, check the top level is a dict, walk dicts and lists, treat empty containers as leaves; O(N). Mistake: dropping `{}` and `[]` silently.
3. **`subnet_report`** (8 minutes, 11 tests). Free address count and the first N free hosts. Hint: `islice` over `hosts()`. Walkthrough: `IPv4Network(cidr, strict=False)`, validate used addresses against the network and the reserved addresses, then take N from a lazy generator, so a /16 never builds a 65534-item list. Mistake: `len(list(net.hosts()))`.

## Gotchas

- **`re.match` is not `re.search`.** It only checks the start. [24]
- **Unanchored patterns.** Use `fullmatch` when the whole string must fit. [24]
- **Greedy `.*`.** It runs to the last possible match. [24]
- **Naive minus aware.** It raises `TypeError`; make both aware with `timezone.utc`. [37]
- **`.seconds` on a `timedelta`.** It is only the seconds part, 0 to 86399; use `total_seconds()`. [37]
- **`ip_network` with host bits.** `ValueError` unless `strict=False`. [35]

:::low-confidence
3.15 renames `re.match` to `re.prefixmatch` and changes `strptime` for `%d` without a year. [23] [37] The course's code works on 3.11 and 3.13 and avoids both. If your platform runs 3.15, `re.match` still works because it is kept for compatibility. [24]
:::

:::key-takeaways
- Raw strings for patterns; `fullmatch` to validate, `search` to find, `groupdict()` for named groups. [24]
- JSON keys become strings; `JSONDecodeError` is a `ValueError`. [26]
- Never mix naive and aware datetimes; time durations with `time.monotonic()`. [37] [38]
- `ip_network(..., strict=False)` and `hosts()` cover most subnet questions. [35]
:::

:::glossary
- **Regular expression**: a compact pattern language for matching text.
- **Raw string**: a string literal written `r"..."` where backslashes are kept as typed.
- **Named group**: a part of a pattern, written `(?P<name>...)`, whose match can be read by name.
- **Greedy**: matching as much text as possible.
- **Naive datetime**: a date and time without any time zone information.
- **Aware datetime**: a date and time that carries its offset from UTC.
- **CIDR**: the address/prefix notation for a network, for example `10.0.0.0/24`.
- **Host bits**: the part of an address after the network prefix.
:::
