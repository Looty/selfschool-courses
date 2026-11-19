import importlib
import logging
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "retry_backoff_starter"
mod = importlib.import_module(TARGET)
logging.disable(logging.CRITICAL)        # keep retry warnings out of the test output


def scripted(*outcomes):
    """Return a function that raises or returns the outcomes in order, and its call list."""
    calls = []
    items = iter(outcomes)

    def func(*args, **kwargs):
        calls.append((args, kwargs))
        value = next(items)
        if isinstance(value, BaseException):
            raise value
        return value

    return func, calls


def same(delay):
    return delay


class RetryCallTest(unittest.TestCase):
    def test_docstring_example(self):
        slept = []
        func, calls = scripted(ConnectionError("1"), ConnectionError("2"), "ok")
        self.assertEqual(mod.retry_call(func, base_delay=1, jitter=same, sleep=slept.append), "ok")
        self.assertEqual(slept, [1, 2])
        self.assertEqual(len(calls), 3)

    def test_success_first_time_never_sleeps(self):
        slept = []
        func, _ = scripted(42)
        self.assertEqual(mod.retry_call(func, sleep=slept.append), 42)
        self.assertEqual(slept, [])

    def test_exponential_delays_capped_and_last_exception_reraised(self):
        slept = []
        errors = [TimeoutError(f"try {i}") for i in range(6)]
        func, calls = scripted(*errors)
        with self.assertRaises(TimeoutError) as caught:
            mod.retry_call(func, attempts=6, base_delay=1, max_delay=10, jitter=same, sleep=slept.append)
        self.assertIs(caught.exception, errors[-1])
        self.assertEqual(slept, [1, 2, 4, 8, 10])          # no sleep after the 6th failure
        self.assertEqual(len(calls), 6)

    def test_jitter_receives_the_capped_delay(self):
        seen, slept = [], []

        def jitter(delay):
            seen.append(delay)
            return delay / 2

        func, _ = scripted(OSError(), OSError(), OSError(), "done")
        mod.retry_call(func, base_delay=3, max_delay=5, jitter=jitter, sleep=slept.append)
        self.assertEqual(seen, [3, 5, 5])
        self.assertEqual(slept, [1.5, 2.5, 2.5])

    def test_default_jitter_stays_within_the_delay(self):
        slept = []
        func, _ = scripted(*[OSError()] * 4, "done")
        mod.retry_call(func, base_delay=1, max_delay=100, sleep=slept.append)
        self.assertEqual(len(slept), 4)
        for delay, cap in zip(slept, [1, 2, 4, 8]):
            self.assertTrue(0 <= delay <= cap, f"{delay} not in [0, {cap}]")

    def test_non_retryable_error_propagates_at_once(self):
        slept = []
        func, calls = scripted(ValueError("bad request"), "never")
        with self.assertRaises(ValueError):
            mod.retry_call(func, retry_on=(ConnectionError,), sleep=slept.append)
        self.assertEqual((len(calls), slept), (1, []))

    def test_single_attempt(self):
        slept = []
        func, _ = scripted(ConnectionError("down"))
        with self.assertRaises(ConnectionError):
            mod.retry_call(func, attempts=1, sleep=slept.append)
        self.assertEqual(slept, [])

    def test_invalid_attempts(self):
        with self.assertRaises(ValueError):
            mod.retry_call(lambda: None, attempts=0, sleep=lambda s: None)


class RetryingDecoratorTest(unittest.TestCase):
    def test_passes_arguments_and_keeps_metadata(self):
        slept = []
        inner, calls = scripted(ConnectionError(), {"status": "ok"})

        @mod.retrying(attempts=3, base_delay=2, jitter=same, retry_on=(ConnectionError,), sleep=slept.append)
        def fetch(url, timeout=5):
            """Fetch a URL."""
            return inner(url, timeout=timeout)

        self.assertEqual(fetch("http://hv1:8080/health", timeout=1), {"status": "ok"})
        self.assertEqual(fetch.__name__, "fetch")
        self.assertEqual(fetch.__doc__, "Fetch a URL.")
        self.assertEqual(calls, [(("http://hv1:8080/health",), {"timeout": 1})] * 2)
        self.assertEqual(slept, [2])


if __name__ == "__main__":
    unittest.main()
