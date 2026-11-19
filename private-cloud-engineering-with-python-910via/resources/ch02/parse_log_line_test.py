import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "parse_log_line_starter"
mod = importlib.import_module(TARGET)

GOOD = "2026-11-19 08:15:02,123 ERROR [kvm-07] provision: disk full on /var"


class ParseLogLineTest(unittest.TestCase):
    def test_example_1(self):
        self.assertEqual(
            mod.parse_log_line(GOOD + "\n"),
            {
                "timestamp": "2026-11-19 08:15:02,123",
                "level": "ERROR",
                "host": "kvm-07",
                "component": "provision",
                "message": "disk full on /var",
            },
        )

    def test_without_trailing_newline(self):
        self.assertEqual(mod.parse_log_line(GOOD)["message"], "disk full on /var")

    def test_unknown_level(self):
        self.assertIsNone(mod.parse_log_line("2026-11-19 08:15:02,123 FATAL [kvm-07] provision: x"))

    def test_text_before_timestamp(self):
        self.assertIsNone(mod.parse_log_line("> " + GOOD))

    def test_message_with_colons_and_brackets(self):
        line = "2026-11-19 08:15:02,123 INFO [kvm-01.lab] api: GET /vms: 200 [12 ms]"
        self.assertEqual(mod.parse_log_line(line)["message"], "GET /vms: 200 [12 ms]")
        self.assertEqual(mod.parse_log_line(line)["host"], "kvm-01.lab")

    def test_empty_message(self):
        line = "2026-11-19 08:15:02,123 DEBUG [h1] sched: "
        self.assertEqual(mod.parse_log_line(line)["message"], "")

    def test_trailing_spaces_in_message_are_kept(self):
        line = "2026-11-19 08:15:02,123 INFO [h1] api: done  \n"
        self.assertEqual(mod.parse_log_line(line)["message"], "done  ")

    def test_missing_brackets(self):
        self.assertIsNone(mod.parse_log_line("2026-11-19 08:15:02,123 INFO kvm-07 api: ok"))

    def test_missing_milliseconds(self):
        self.assertIsNone(mod.parse_log_line("2026-11-19 08:15:02 INFO [kvm-07] api: ok"))

    def test_lower_case_level_is_rejected(self):
        self.assertIsNone(mod.parse_log_line("2026-11-19 08:15:02,123 info [kvm-07] api: ok"))

    def test_embedded_newline_is_rejected(self):
        self.assertIsNone(mod.parse_log_line("2026-11-19 08:15:02,123 INFO [h] api: a\nb"))

    def test_empty_line(self):
        self.assertIsNone(mod.parse_log_line(""))


if __name__ == "__main__":
    unittest.main()
