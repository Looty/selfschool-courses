import importlib
import sys
import threading
import time
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "parallel_health_check_starter"
mod = importlib.import_module(TARGET)


class ParallelHealthCheckTest(unittest.TestCase):
    def setUp(self):
        # Hanging checks wait on this event; releasing it in cleanup lets their threads end.
        self.release = threading.Event()
        self.addCleanup(self.release.set)

    def test_docstring_example(self):
        def check(host):
            if host == "hv3":
                raise ConnectionRefusedError("port 22")
            return host != "hv2"

        self.assertEqual(
            mod.parallel_health_check(["hv1", "hv2", "hv3"], check),
            [("hv1", "up", ""), ("hv2", "down", ""), ("hv3", "error", "ConnectionRefusedError: port 22")],
        )

    def test_empty(self):
        self.assertEqual(mod.parallel_health_check([], lambda h: True), [])

    def test_results_in_input_order_not_finish_order(self):
        delays = {"slow": 0.15, "mid": 0.08, "fast": 0.0}

        def check(host):
            self.release.wait(delays[host])
            return True

        result = mod.parallel_health_check(["slow", "mid", "fast"], check, timeout=2)
        self.assertEqual([r[0] for r in result], ["slow", "mid", "fast"])
        self.assertTrue(all(r[1] == "up" for r in result))

    def test_checks_run_concurrently(self):
        def check(host):
            self.release.wait(0.1)
            return True

        start = time.monotonic()
        result = mod.parallel_health_check([f"hv{i}" for i in range(10)], check, timeout=2)
        elapsed = time.monotonic() - start
        self.assertEqual(len(result), 10)
        self.assertLess(elapsed, 0.6, "ten 0.1 s checks should overlap, not take 1 s")

    def test_hanging_check_times_out_without_blocking(self):
        def check(host):
            if host == "stuck":
                self.release.wait(30)
            return True

        start = time.monotonic()
        result = mod.parallel_health_check(["ok1", "stuck", "ok2"], check, timeout=0.2)
        elapsed = time.monotonic() - start
        self.assertEqual(
            result,
            [("ok1", "up", ""), ("stuck", "timeout", "no answer within 0.2s"), ("ok2", "up", "")],
        )
        self.assertLess(elapsed, 1.5, "must not wait for the hanging check")

    def test_never_raises_and_formats_errors(self):
        def check(host):
            if host == "boom":
                raise RuntimeError("libvirt connection lost")
            if host == "key":
                raise KeyError("hv9")
            return 0                                   # falsy counts as down

        self.assertEqual(
            mod.parallel_health_check(["boom", "key", "zero"], check),
            [
                ("boom", "error", "RuntimeError: libvirt connection lost"),
                ("key", "error", "KeyError: 'hv9'"),
                ("zero", "down", ""),
            ],
        )

    def test_duplicates_checked_separately(self):
        calls = []
        lock = threading.Lock()

        def check(host):
            with lock:
                calls.append(host)
            return True

        result = mod.parallel_health_check(["a", "a", "b"], check)
        self.assertEqual(result, [("a", "up", ""), ("a", "up", ""), ("b", "up", "")])
        self.assertEqual(sorted(calls), ["a", "a", "b"])

    def test_small_pool_still_returns_every_host(self):
        result = mod.parallel_health_check([f"h{i}" for i in range(7)], lambda h: True, max_workers=2)
        self.assertEqual([r[0] for r in result], [f"h{i}" for i in range(7)])
        self.assertTrue(all(r[1] == "up" for r in result))


if __name__ == "__main__":
    unittest.main()
