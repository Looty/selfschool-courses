"""Exercise: log aggregation (time box: 30 minutes).

A service writes one access-log line per request, with seven fields separated
by single spaces:

    <timestamp> <level> <client_ip> <method> <path> <status> <latency_ms>

    2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5

Field rules (a line that breaks any rule is malformed):
  * timestamp   UTC, exactly the format %Y-%m-%dT%H:%M:%SZ
  * level       one of DEBUG, INFO, WARNING, ERROR
  * client_ip   a valid IPv4 or IPv6 address
  * method      any token without spaces
  * path        starts with "/"
  * status      an integer from 100 to 599
  * latency_ms  a finite number that is not negative

Write log_stats(lines, top_n=3). `lines` is ANY iterable of strings (a list,
an open file, a generator) and may be far larger than memory would allow as a
list, so read it once, line by line. Lines may end with a newline.

Return a dict with exactly these keys:

  "top_ips"                list of (ip, request_count), highest count first,
                           ties broken by the ip string in ascending order,
                           at most top_n entries
  "error_rate_per_minute"  dict: minute "YYYY-MM-DDTHH:MM" -> errors / requests
                           in that minute (a float). An error is a status of
                           500 or above. Keys in ascending order.
  "p95_latency_ms"         dict: path -> 95th percentile of latency_ms for
                           that path, by the nearest-rank rule: sort the n
                           values, take the one at 1-based rank ceil(0.95 * n).
                           Keys in ascending order.
  "skipped"                number of malformed lines

Blank lines (empty or only whitespace) are ignored and are not counted as
malformed. Malformed lines are counted in "skipped" and otherwise ignored.

Example:

    lines = [
        "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5",
        "2026-11-19T10:15:40Z ERROR 10.0.0.7 POST /api/vms 503 950.0",
        "this line is not a log line",
        "2026-11-19T10:16:01Z INFO 10.0.0.5 GET /health 200 1.0",
    ]
    log_stats(lines, top_n=1) == {
        "top_ips": [("10.0.0.5", 2)],
        "error_rate_per_minute": {"2026-11-19T10:15": 0.5, "2026-11-19T10:16": 0.0},
        "p95_latency_ms": {"/api/vms": 950.0, "/health": 1.0},
        "skipped": 1,
    }

Check your work:  python log_stats_test.py
"""


def parse_line(line):
    """Return (minute, ip, path, status, latency_ms), or None if the line is malformed."""
    raise NotImplementedError


def percentile(values, pct):
    """Return the nearest-rank percentile (pct is an int such as 95) of a non-empty list."""
    raise NotImplementedError


def log_stats(lines, top_n=3):
    """Aggregate an iterable of log lines into the dict described in the module docstring."""
    raise NotImplementedError
