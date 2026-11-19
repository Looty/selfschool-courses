import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "word_count_top_starter"
mod = importlib.import_module(TARGET)


class WordCountTopTest(unittest.TestCase):
    def test_example_1(self):
        self.assertEqual(mod.word_count_top("disk cpu disk net cpu disk", 2), ["disk", "cpu"])

    def test_tie_is_alphabetical_not_first_seen(self):
        self.assertEqual(mod.word_count_top("net cpu disk disk", 2), ["disk", "cpu"])

    def test_all_tied(self):
        self.assertEqual(mod.word_count_top("zeta beta alpha", 3), ["alpha", "beta", "zeta"])

    def test_empty_text(self):
        self.assertEqual(mod.word_count_top("", 3), [])

    def test_whitespace_only_text(self):
        self.assertEqual(mod.word_count_top("  \n\t ", 1), [])

    def test_case_is_ignored_and_output_is_lower_case(self):
        self.assertEqual(mod.word_count_top("Disk DISK", 5), ["disk"])

    def test_k_zero(self):
        self.assertEqual(mod.word_count_top("a b c", 0), [])

    def test_k_larger_than_distinct_words(self):
        self.assertEqual(mod.word_count_top("b a b", 10), ["b", "a"])

    def test_mixed_whitespace(self):
        self.assertEqual(mod.word_count_top("err\twarn\nerr  info\r\nwarn err", 2), ["err", "warn"])

    def test_digits_are_words(self):
        self.assertEqual(mod.word_count_top("404 200 404 500 200 404", 2), ["404", "200"])

    def test_returns_a_list_of_str(self):
        result = mod.word_count_top("a a b", 1)
        self.assertIsInstance(result, list)
        self.assertEqual(result, ["a"])

    def test_large_input(self):
        text = " ".join(["vm"] * 30000 + ["host"] * 20000 + ["disk"] * 20000)
        self.assertEqual(mod.word_count_top(text, 3), ["vm", "disk", "host"])


if __name__ == "__main__":
    unittest.main()
