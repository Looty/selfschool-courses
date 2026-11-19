import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "rate_limiter_starter"
mod = importlib.import_module(TARGET)


class FakeClock:
    def __init__(self, now=0.0):
        self.now = now

    def __call__(self):
        return self.now


class TokenBucketTest(unittest.TestCase):
    def test_burst_then_refill(self):
        clock = FakeClock()
        tb = mod.TokenBucketLimiter(rate=1, burst=2, clock=clock)
        self.assertEqual([tb.allow("a") for _ in range(3)], [True, True, False])
        clock.now = 1.0
        self.assertEqual([tb.allow("a"), tb.allow("a")], [True, False])

    def test_tokens_never_exceed_burst(self):
        clock = FakeClock()
        tb = mod.TokenBucketLimiter(rate=10, burst=3, clock=clock)
        tb.allow("a")
        clock.now = 3600.0                      # an hour idle still gives only 3 tokens
        self.assertEqual([tb.allow("a") for _ in range(4)], [True, True, True, False])

    def test_fractional_refill(self):
        clock = FakeClock()
        tb = mod.TokenBucketLimiter(rate=2, burst=1, clock=clock)
        self.assertTrue(tb.allow("a"))
        clock.now = 0.25                        # half a token
        self.assertFalse(tb.allow("a"))
        clock.now = 0.5                         # the half token is kept, now one in total
        self.assertTrue(tb.allow("a"))

    def test_clients_are_independent(self):
        clock = FakeClock()
        tb = mod.TokenBucketLimiter(rate=1, burst=1, clock=clock)
        self.assertTrue(tb.allow("a"))
        self.assertFalse(tb.allow("a"))
        self.assertTrue(tb.allow("b"))

    def test_invalid_arguments(self):
        for kwargs in ({"rate": 0, "burst": 1}, {"rate": 1, "burst": 0}, {"rate": -1, "burst": 5}):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    mod.TokenBucketLimiter(clock=FakeClock(), **kwargs)


class SlidingWindowTest(unittest.TestCase):
    def test_docstring_example(self):
        clock = FakeClock()
        sw = mod.SlidingWindowLimiter(limit=2, window=10, clock=clock)
        results = []
        for t in (0, 1, 5, 10, 10.5, 11):
            clock.now = t
            results.append(sw.allow("a"))
        # 0 ok, 1 ok, 5 full, 10 ok (0 left), 10.5 full (1 and 10 inside), 11 ok (1 left)
        self.assertEqual(results, [True, True, False, True, False, True])

    def test_rejected_requests_are_not_recorded(self):
        clock = FakeClock()
        sw = mod.SlidingWindowLimiter(limit=1, window=5, clock=clock)
        self.assertTrue(sw.allow("a"))
        for t in (1, 2, 3, 4):
            clock.now = t
            self.assertFalse(sw.allow("a"))
        clock.now = 5                           # only the request at 0 counted, and it has left
        self.assertTrue(sw.allow("a"))

    def test_burst_at_one_instant(self):
        clock = FakeClock(100.0)
        sw = mod.SlidingWindowLimiter(limit=3, window=1, clock=clock)
        self.assertEqual([sw.allow("a") for _ in range(5)], [True, True, True, False, False])

    def test_clients_are_independent(self):
        clock = FakeClock()
        sw = mod.SlidingWindowLimiter(limit=1, window=60, clock=clock)
        self.assertTrue(sw.allow("10.0.0.1"))
        self.assertFalse(sw.allow("10.0.0.1"))
        self.assertTrue(sw.allow("10.0.0.2"))

    def test_invalid_arguments(self):
        for kwargs in ({"limit": 0, "window": 1}, {"limit": 1, "window": 0}):
            with self.subTest(**kwargs):
                with self.assertRaises(ValueError):
                    mod.SlidingWindowLimiter(clock=FakeClock(), **kwargs)


if __name__ == "__main__":
    unittest.main()
