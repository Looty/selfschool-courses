"""Reference solution for timer_context (see timer_context_starter.py)."""
import time
from contextlib import contextmanager


class Timer:
    """Context manager that records the elapsed time of its block."""

    def __init__(self, clock=time.monotonic) -> None:
        self._clock = clock
        self._start = None
        self.elapsed = None

    def __enter__(self) -> "Timer":
        self._start = self._clock()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        self.elapsed = self._clock() - self._start
        return False


@contextmanager
def timed(record: dict, key: str, clock=time.monotonic):
    """Store the elapsed time of the block in record[key], even on error."""
    start = clock()
    try:
        yield
    finally:
        record[key] = clock() - start

# Complexity: O(1) time and space for both.
# The default argument is the function time.monotonic itself, not a call to
# it: `clock=time.monotonic()` would freeze one number at import time.
# __exit__ returns False so an exception from the block keeps propagating;
# returning True would silently swallow it.
# In timed(), try/finally is what makes the time land in the record when the
# block raises: the exception is re-raised inside the generator at `yield`.
# Alternative: time.perf_counter as the default clock; it is also monotonic
# and has the highest available resolution for short durations.
