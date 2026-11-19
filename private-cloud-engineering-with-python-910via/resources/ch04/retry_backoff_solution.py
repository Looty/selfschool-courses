"""Reference solution for the retry with backoff exercise (see retry_backoff_starter.py)."""
import functools
import logging
import random
import time

logger = logging.getLogger(__name__)


def full_jitter(delay):
    return random.uniform(0, delay)


def retry_call(func, *, attempts=5, base_delay=0.5, max_delay=8.0,
               retry_on=(Exception,), jitter=None, sleep=time.sleep):
    """Call func() until it succeeds or the attempts run out."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    jitter = jitter or full_jitter
    for n in range(attempts):
        try:
            return func()
        except retry_on as exc:
            if n == attempts - 1:
                raise                                  # last attempt: the original exception
            delay = min(max_delay, base_delay * 2 ** n)
            wait = jitter(delay)
            logger.warning("attempt %d/%d failed (%s); retrying in %.2fs", n + 1, attempts, exc, wait)
            sleep(wait)


def retrying(**options):
    """Return a decorator that applies retry_call with these options."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return retry_call(lambda: func(*args, **kwargs), **options)
        return wrapper
    return decorator


# Complexity: at most `attempts` calls and attempts - 1 sleeps; O(1) extra space. The total
# worst-case wait is the sum of the capped delays, which is what to tell a caller with a deadline.
# Alternative: pass a deadline instead of an attempt count and stop when the next sleep would
# cross it; with a monotonic clock injected, that is as easy to test as this version.
