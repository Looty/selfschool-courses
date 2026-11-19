"""Exercise: per-client rate limiters (time box: 15 minutes).

Both classes decide, for one request at a time, whether a client may proceed.
Each takes a `clock` function returning the current time in seconds; tests
pass a fake clock, so nothing ever really waits. Clients are independent: one
client using up its allowance never affects another.

1. TokenBucketLimiter(rate, burst, clock=time.monotonic)
   Each client has a bucket that holds at most `burst` tokens and starts full.
   Tokens are added continuously at `rate` tokens per second, never above
   `burst`. allow(client) returns True and removes one token if the client
   has at least one token at that moment; otherwise it returns False and
   removes nothing.
   Raise ValueError if rate <= 0 or burst < 1.

2. SlidingWindowLimiter(limit, window, clock=time.monotonic)
   allow(client) returns True if the client had fewer than `limit` ALLOWED
   requests in the last `window` seconds, that is with a time t where
   now - window < t <= now, and then records this request. Rejected requests
   are not recorded.
   Raise ValueError if limit < 1 or window <= 0.

Examples (clock is a fake that the test moves forward):

    tb = TokenBucketLimiter(rate=1, burst=2, clock=clock)    # time 0
    tb.allow("a"), tb.allow("a"), tb.allow("a")   -> True, True, False
    # time 1.0: one token has been added
    tb.allow("a"), tb.allow("a")                  -> True, False

    sw = SlidingWindowLimiter(limit=2, window=10, clock=clock)
    # times 0 and 1: allowed; time 5: rejected (two in the last 10 s)
    # time 10: allowed again, because the request at 0 is no longer inside (0, 10]

Check your work:  python rate_limiter_test.py
"""
import time


class TokenBucketLimiter:
    def __init__(self, rate, burst, clock=time.monotonic):
        """Create a limiter with `rate` tokens per second and `burst` maximum tokens."""
        raise NotImplementedError

    def allow(self, client):
        """Return True and spend a token if the client has one, else False."""
        raise NotImplementedError


class SlidingWindowLimiter:
    def __init__(self, limit, window, clock=time.monotonic):
        """Create a limiter allowing `limit` requests per `window` seconds per client."""
        raise NotImplementedError

    def allow(self, client):
        """Return True and record the request if the client is under its limit, else False."""
        raise NotImplementedError
