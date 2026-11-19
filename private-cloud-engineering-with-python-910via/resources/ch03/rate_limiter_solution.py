"""Reference solution for the rate limiter exercise (see rate_limiter_starter.py)."""
from collections import defaultdict, deque
import time


class TokenBucketLimiter:
    def __init__(self, rate, burst, clock=time.monotonic):
        """Create a limiter with `rate` tokens per second and `burst` maximum tokens."""
        if rate <= 0 or burst < 1:
            raise ValueError("rate must be > 0 and burst >= 1")
        self.rate = rate
        self.burst = burst
        self.clock = clock
        self._buckets = {}                      # client -> [tokens, last_refill_time]

    def allow(self, client):
        """Return True and spend a token if the client has one, else False."""
        now = self.clock()
        bucket = self._buckets.get(client)
        if bucket is None:
            bucket = self._buckets[client] = [float(self.burst), now]   # new clients start full
        tokens, last = bucket
        tokens = min(self.burst, tokens + (now - last) * self.rate)     # lazy refill
        bucket[1] = now
        if tokens >= 1:
            bucket[0] = tokens - 1
            return True
        bucket[0] = tokens
        return False


class SlidingWindowLimiter:
    def __init__(self, limit, window, clock=time.monotonic):
        """Create a limiter allowing `limit` requests per `window` seconds per client."""
        if limit < 1 or window <= 0:
            raise ValueError("limit must be >= 1 and window > 0")
        self.limit = limit
        self.window = window
        self.clock = clock
        self._log = defaultdict(deque)          # client -> times of allowed requests, oldest first

    def allow(self, client):
        """Return True and record the request if the client is under its limit, else False."""
        now = self.clock()
        times = self._log[client]
        while times and times[0] <= now - self.window:   # left the window (now - window, now]
            times.popleft()
        if len(times) < self.limit:
            times.append(now)
            return True
        return False


# Complexity: TokenBucketLimiter.allow is O(1) time and O(1) space per client.
# SlidingWindowLimiter.allow is O(1) amortised (each time is appended and popped once) and keeps
# up to `limit` timestamps per client, so O(clients * limit) space.
# Alternative: a fixed-window counter (one count per client per window number, now // window)
# needs O(1) space per client but lets up to 2 * limit requests through around a window edge.
# Neither class here ever forgets an idle client; a real service would expire idle entries.
