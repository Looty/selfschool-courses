"""Reference solution for the log aggregation exercise (see log_stats_starter.py)."""
from collections import Counter, defaultdict
from datetime import datetime
import ipaddress
import math

LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR"}
TS_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def parse_line(line):
    """Return (minute, ip, path, status, latency_ms), or None if the line is malformed."""
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
    if not 0 <= latency < math.inf:      # also rejects nan: every comparison with nan is False
        return None
    return when.strftime("%Y-%m-%dT%H:%M"), ip, path, status, latency


def percentile(values, pct):
    """Return the nearest-rank percentile (pct is an int such as 95) of a non-empty list."""
    ordered = sorted(values)
    rank = -(-pct * len(ordered) // 100)     # ceil(pct * n / 100) in integer arithmetic
    return ordered[max(rank, 1) - 1]


def log_stats(lines, top_n=3):
    """Aggregate an iterable of log lines into the dict described in the starter file."""
    requests = Counter()                     # ip -> request count
    per_minute = defaultdict(lambda: [0, 0])  # minute -> [requests, errors]
    latencies = defaultdict(list)            # path -> [latency_ms, ...]
    skipped = 0

    for line in lines:                       # one pass; works for a file or a generator
        if not line.strip():
            continue
        record = parse_line(line)
        if record is None:
            skipped += 1
            continue
        minute, ip, path, status, latency = record
        requests[ip] += 1
        bucket = per_minute[minute]
        bucket[0] += 1
        if status >= 500:
            bucket[1] += 1
        latencies[path].append(latency)

    top = sorted(requests.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n]
    return {
        "top_ips": top,
        "error_rate_per_minute": {
            minute: errors / total for minute, (total, errors) in sorted(per_minute.items())
        },
        "p95_latency_ms": {path: percentile(vals, 95) for path, vals in sorted(latencies.items())},
        "skipped": skipped,
    }


# Complexity, for L lines, U distinct IPs, M minutes and P paths:
#   time   O(L) to parse and count, O(U log U) to rank the IPs, O(M log M) for the minutes,
#          and O(L log L) in the worst case to sort the latencies (all lines on one path).
#   space  O(U + M + L): the counters are small, but every latency is kept until the end.
# Alternative: heapq.nlargest(top_n, requests.items(), key=...) avoids sorting all U items, and
# a fixed set of latency buckets per path (a histogram) gives an approximate p95 in O(1) memory
# per path instead of storing every value.
