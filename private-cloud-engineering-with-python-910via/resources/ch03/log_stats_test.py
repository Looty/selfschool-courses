import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "log_stats_starter"
mod = importlib.import_module(TARGET)

SAMPLE = [
    "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5",
    "2026-11-19T10:15:40Z ERROR 10.0.0.7 POST /api/vms 503 950.0",
    "this line is not a log line",
    "2026-11-19T10:16:01Z INFO 10.0.0.5 GET /health 200 1.0",
]


def line(second=0, ip="10.0.0.1", path="/api/vms", status=200, latency=10.0, minute=15):
    level = "ERROR" if status >= 500 else "INFO"
    return f"2026-11-19T10:{minute:02d}:{second:02d}Z {level} {ip} GET {path} {status} {latency}"


class ParseLineTest(unittest.TestCase):
    def test_valid_line(self):
        self.assertEqual(
            mod.parse_line("2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5\n"),
            ("2026-11-19T10:15", "10.0.0.5", "/api/vms", 200, 12.5),
        )

    def test_ipv6_client(self):
        record = mod.parse_line("2026-11-19T23:59:59Z WARNING 2001:db8::1 GET / 404 3")
        self.assertEqual(record, ("2026-11-19T23:59", "2001:db8::1", "/", 404, 3.0))

    def test_malformed_lines_return_none(self):
        bad = [
            "",
            "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200",            # six fields
            "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5 extra",  # eight fields
            "2026-11-19 10:15:02 INFO 10.0.0.5 GET /api/vms 200 12.5",         # space in timestamp
            "2026-13-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 12.5",        # month 13
            "2026-11-19T10:15:02Z NOTICE 10.0.0.5 GET /api/vms 200 12.5",      # unknown level
            "2026-11-19T10:15:02Z INFO 10.0.0.999 GET /api/vms 200 12.5",      # bad address
            "2026-11-19T10:15:02Z INFO 10.0.0.5 GET api/vms 200 12.5",         # path without /
            "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms OK 12.5",         # status not a number
            "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 99 12.5",         # status out of range
            "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 fast",        # latency not a number
            "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 -1",          # negative latency
            "2026-11-19T10:15:02Z INFO 10.0.0.5 GET /api/vms 200 nan",         # float() accepts it
        ]
        for text in bad:
            with self.subTest(line=text):
                self.assertIsNone(mod.parse_line(text))


class PercentileTest(unittest.TestCase):
    def test_nearest_rank(self):
        self.assertEqual(mod.percentile([7.0], 95), 7.0)
        self.assertEqual(mod.percentile(list(range(1, 21)), 95), 19)      # ceil(19.0) = 19
        self.assertEqual(mod.percentile(list(range(1, 101)), 95), 95)
        self.assertEqual(mod.percentile([30, 10, 20], 95), 30)            # ceil(2.85) = 3
        self.assertEqual(mod.percentile([4, 1, 3, 2], 50), 2)

    def test_does_not_reorder_the_input(self):
        values = [3.0, 1.0, 2.0]
        mod.percentile(values, 95)
        self.assertEqual(values, [3.0, 1.0, 2.0])


class LogStatsTest(unittest.TestCase):
    def test_docstring_example(self):
        self.assertEqual(
            mod.log_stats(SAMPLE, top_n=1),
            {
                "top_ips": [("10.0.0.5", 2)],
                "error_rate_per_minute": {"2026-11-19T10:15": 0.5, "2026-11-19T10:16": 0.0},
                "p95_latency_ms": {"/api/vms": 950.0, "/health": 1.0},
                "skipped": 1,
            },
        )

    def test_empty_input(self):
        self.assertEqual(
            mod.log_stats([]),
            {"top_ips": [], "error_rate_per_minute": {}, "p95_latency_ms": {}, "skipped": 0},
        )

    def test_top_ips_order_and_tie_break(self):
        lines = (
            [line(ip="10.0.0.9")] * 2
            + [line(ip="10.0.0.10")] * 2
            + [line(ip="10.0.0.3")] * 5
            + [line(ip="10.0.0.4")]
        )
        result = mod.log_stats(lines, top_n=3)
        # 10.0.0.10 and 10.0.0.9 tie on 2; "10.0.0.10" < "10.0.0.9" as strings.
        self.assertEqual(result["top_ips"], [("10.0.0.3", 5), ("10.0.0.10", 2), ("10.0.0.9", 2)])
        # top_n larger than the number of distinct addresses returns them all.
        self.assertEqual(len(mod.log_stats(lines, top_n=10)["top_ips"]), 4)

    def test_error_rate_counts_only_5xx_and_sorts_minutes(self):
        lines = [
            line(minute=17, status=500),
            line(minute=15, status=404),
            line(minute=15, status=200),
            line(minute=16, status=502),
            line(minute=16, status=200),
            line(minute=16, status=200),
            line(minute=16, status=599),
        ]
        rates = mod.log_stats(lines)["error_rate_per_minute"]
        self.assertEqual(list(rates), ["2026-11-19T10:15", "2026-11-19T10:16", "2026-11-19T10:17"])
        self.assertEqual(rates["2026-11-19T10:15"], 0.0)
        self.assertEqual(rates["2026-11-19T10:16"], 0.5)
        self.assertEqual(rates["2026-11-19T10:17"], 1.0)

    def test_p95_per_path(self):
        lines = [line(path="/slow", latency=float(ms)) for ms in range(100, 0, -1)]
        lines += [line(path="/fast", latency=2.0), line(path="/fast", latency=1.0)]
        self.assertEqual(mod.log_stats(lines)["p95_latency_ms"], {"/fast": 2.0, "/slow": 95.0})

    def test_blank_lines_ignored_and_malformed_counted(self):
        lines = ["\n", "   \n", "garbage\n", line() + "\n", "2026-11-19T10:15:02Z INFO x GET / 200 1\n"]
        result = mod.log_stats(lines)
        self.assertEqual(result["skipped"], 2)
        self.assertEqual(result["top_ips"], [("10.0.0.1", 1)])

    def test_accepts_a_one_shot_generator(self):
        def produce():
            for i in range(20000):
                yield line(second=i % 60, ip=f"10.0.{i % 7}.1", latency=float(i % 50)) + "\n"

        result = mod.log_stats(produce(), top_n=2)
        self.assertEqual(result["top_ips"], [("10.0.0.1", 2858), ("10.0.1.1", 2857)])
        self.assertEqual(result["p95_latency_ms"], {"/api/vms": 47.0})
        self.assertEqual(result["skipped"], 0)


if __name__ == "__main__":
    unittest.main()
