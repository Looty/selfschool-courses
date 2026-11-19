"""Exercise: retry with exponential backoff (time box: 15 minutes).

1. retry_call(func, *, attempts=5, base_delay=0.5, max_delay=8.0,
              retry_on=(Exception,), jitter=None, sleep=time.sleep)

   Call func() with no arguments. If it returns, return its value. If it
   raises an exception that is an instance of one of `retry_on`, wait and try
   again, up to `attempts` calls in total. After the last failed call,
   re-raise that call's exception unchanged. An exception that is not in
   `retry_on` propagates at once, with no wait.

   The wait before retry number n (n = 0 for the wait after the first
   failure) is

       delay = min(max_delay, base_delay * 2 ** n)
       sleep(jitter(delay))

   `jitter` is a function from a delay to the delay actually slept. When it
   is None use "full jitter": random.uniform(0, delay). `sleep` is injected
   so tests run instantly. Never sleep after the last attempt.

   Raise ValueError if attempts < 1.

2. retrying(**options) -> decorator
   The same behaviour as a decorator that accepts the same keyword options.
   The wrapped function keeps its __name__ and docstring and passes its
   arguments through:

       @retrying(attempts=3, retry_on=(ConnectionError,), sleep=fake_sleep)
       def fetch(url, timeout=5):
           ...

Example (sleep records the delays instead of waiting):

    slept = []
    calls = iter([ConnectionError("1"), ConnectionError("2"), "ok"])
    def flaky():
        value = next(calls)
        if isinstance(value, Exception):
            raise value
        return value
    retry_call(flaky, base_delay=1, jitter=lambda d: d, sleep=slept.append)  # -> "ok"
    slept == [1, 2]

Check your work:  python retry_backoff_test.py
"""
import time


def retry_call(func, *, attempts=5, base_delay=0.5, max_delay=8.0,
               retry_on=(Exception,), jitter=None, sleep=time.sleep):
    """Call func() until it succeeds or the attempts run out."""
    raise NotImplementedError


def retrying(**options):
    """Return a decorator that applies retry_call with these options."""
    raise NotImplementedError
