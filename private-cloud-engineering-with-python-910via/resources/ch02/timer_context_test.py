import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "timer_context_starter"
mod = importlib.import_module(TARGET)


def fake_clock(*readings):
    """Return a clock function that yields the given readings in order."""
    it = iter(readings)
    return lambda: next(it)


class TimerClassTest(unittest.TestCase):
    def test_elapsed_from_fake_clock(self):
        with mod.Timer(clock=fake_clock(10.0, 12.5)) as t:
            pass
        self.assertEqual(t.elapsed, 2.5)

    def test_enter_returns_the_timer(self):
        timer = mod.Timer(clock=fake_clock(0.0, 1.0))
        with timer as t:
            self.assertIs(t, timer)

    def test_elapsed_is_none_inside_the_block(self):
        with mod.Timer(clock=fake_clock(1.0, 4.0)) as t:
            self.assertIsNone(t.elapsed)
        self.assertEqual(t.elapsed, 3.0)

    def test_exception_propagates_and_elapsed_is_stored(self):
        t = mod.Timer(clock=fake_clock(5.0, 5.75))
        with self.assertRaises(RuntimeError):
            with t:
                raise RuntimeError("boom")
        self.assertEqual(t.elapsed, 0.75)

    def test_clock_read_exactly_twice(self):
        calls = []

        def clock():
            calls.append(1)
            return float(len(calls))

        with mod.Timer(clock=clock):
            pass
        self.assertEqual(len(calls), 2)

    def test_default_clock_works(self):
        with mod.Timer() as t:
            sum(range(1000))
        self.assertIsInstance(t.elapsed, float)
        self.assertGreaterEqual(t.elapsed, 0.0)


class TimedFunctionTest(unittest.TestCase):
    def test_records_elapsed(self):
        stats = {}
        with mod.timed(stats, "provision", clock=fake_clock(100.0, 103.0)):
            pass
        self.assertEqual(stats, {"provision": 3.0})

    def test_records_even_when_block_raises(self):
        stats = {}
        with self.assertRaises(KeyError):
            with mod.timed(stats, "lookup", clock=fake_clock(1.0, 1.5)):
                raise KeyError("missing")
        self.assertEqual(stats, {"lookup": 0.5})

    def test_two_keys(self):
        stats = {}
        with mod.timed(stats, "a", clock=fake_clock(0.0, 1.0)):
            pass
        with mod.timed(stats, "b", clock=fake_clock(0.0, 2.0)):
            pass
        self.assertEqual(stats, {"a": 1.0, "b": 2.0})

    def test_nothing_recorded_before_exit(self):
        stats = {}
        with mod.timed(stats, "x", clock=fake_clock(0.0, 1.0)):
            self.assertNotIn("x", stats)

    def test_default_clock_works(self):
        stats = {}
        with mod.timed(stats, "real"):
            sum(range(1000))
        self.assertGreaterEqual(stats["real"], 0.0)


if __name__ == "__main__":
    unittest.main()
