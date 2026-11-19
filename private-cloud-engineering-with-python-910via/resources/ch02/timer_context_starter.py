"""Timer context manager with an injectable clock (drill, 5 to 8 minutes).

Measure how long a block of code takes, in two styles. Both take the clock
as a parameter (a function with no arguments that returns seconds as a
float). Real code passes time.monotonic; tests pass a fake clock that
returns fixed numbers, so the result is exact and the test never sleeps.

Part 1: the class Timer(clock=time.monotonic)
    with Timer() as t:
        do_work()
    t.elapsed  -> seconds the block took (float)
    - __enter__ reads the clock once and returns the Timer itself.
    - __exit__ reads the clock once and stores elapsed = end - start.
    - t.elapsed is None before the block has finished.
    - Exceptions from the block are NOT swallowed: they propagate after
      elapsed has been stored.

Part 2: the generator function timed(record, key, clock=time.monotonic)
    Decorate it with contextlib.contextmanager.
    with timed(stats, "provision"):
        do_work()
    stats["provision"]  -> seconds the block took
    - The clock is read once on entry and once on exit.
    - The time is stored even when the block raises, and the exception
      still propagates.
    - It yields nothing useful (None).

Example with a fake clock
    ticks = iter([10.0, 12.5])
    with Timer(clock=lambda: next(ticks)) as t:
        pass
    t.elapsed  -> 2.5
"""
import time
from contextlib import contextmanager


class Timer:
    """Context manager that records the elapsed time of its block."""

    def __init__(self, clock=time.monotonic) -> None:
        """Store the clock; elapsed starts as None."""
        raise NotImplementedError

    def __enter__(self) -> "Timer":
        """Read the clock and return self."""
        raise NotImplementedError

    def __exit__(self, exc_type, exc_value, traceback) -> bool:
        """Read the clock, store elapsed, do not suppress exceptions."""
        raise NotImplementedError


@contextmanager
def timed(record: dict, key: str, clock=time.monotonic):
    """Store the elapsed time of the block in record[key], even on error."""
    raise NotImplementedError
    yield
