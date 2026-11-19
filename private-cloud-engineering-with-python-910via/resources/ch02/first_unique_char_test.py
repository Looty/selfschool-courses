import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "first_unique_char_starter"
mod = importlib.import_module(TARGET)


class FirstUniqueCharTest(unittest.TestCase):
    def test_example_1(self):
        self.assertEqual(mod.first_unique_char("swiss"), 1)

    def test_all_repeat(self):
        self.assertEqual(mod.first_unique_char("aabb"), -1)

    def test_empty_string(self):
        self.assertEqual(mod.first_unique_char(""), -1)

    def test_single_character(self):
        self.assertEqual(mod.first_unique_char("z"), 0)

    def test_first_character_is_unique(self):
        self.assertEqual(mod.first_unique_char("abcb"), 0)

    def test_last_character_is_unique(self):
        self.assertEqual(mod.first_unique_char("aabbc"), 4)

    def test_case_matters(self):
        self.assertEqual(mod.first_unique_char("aA"), 0)

    def test_not_fooled_by_a_later_repeat(self):
        self.assertEqual(mod.first_unique_char("abacb"), 3)

    def test_non_letter_characters(self):
        self.assertEqual(mod.first_unique_char("  -- x"), 5)

    def test_large_input_runs_in_linear_time(self):
        s = "ab" * 50000 + "c"
        self.assertEqual(mod.first_unique_char(s), 100000)


if __name__ == "__main__":
    unittest.main()
