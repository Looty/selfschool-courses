import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "count_in_range_starter"
mod = importlib.import_module(TARGET)


class NoIteration(list):
    """A sorted list that fails the test if the solution loops over it."""

    def __iter__(self):
        raise AssertionError("do not scan the list; use bisect")


class CountInRangeTest(unittest.TestCase):
    VALUES = [1, 3, 3, 5, 8, 13]

    def test_example_1(self):
        self.assertEqual(mod.count_in_range(self.VALUES, 3, 8), 4)

    def test_gap_between_values(self):
        self.assertEqual(mod.count_in_range(self.VALUES, 4, 4), 0)

    def test_empty_list(self):
        self.assertEqual(mod.count_in_range([], 0, 10), 0)

    def test_lo_greater_than_hi(self):
        self.assertEqual(mod.count_in_range([5], 10, 1), 0)

    def test_whole_list(self):
        self.assertEqual(mod.count_in_range(self.VALUES, -100, 100), 6)

    def test_both_limits_are_inclusive(self):
        self.assertEqual(mod.count_in_range(self.VALUES, 1, 13), 6)
        self.assertEqual(mod.count_in_range(self.VALUES, 3, 3), 2)

    def test_range_below_all_values(self):
        self.assertEqual(mod.count_in_range(self.VALUES, -5, 0), 0)

    def test_range_above_all_values(self):
        self.assertEqual(mod.count_in_range(self.VALUES, 14, 99), 0)

    def test_all_duplicates(self):
        self.assertEqual(mod.count_in_range([7, 7, 7, 7], 7, 7), 4)

    def test_negative_values(self):
        self.assertEqual(mod.count_in_range([-9, -4, -4, 0, 2], -4, 0), 3)

    def test_does_not_scan_the_list(self):
        values = NoIteration(range(0, 1000000, 2))
        self.assertEqual(mod.count_in_range(values, 10, 20), 6)
        self.assertEqual(mod.count_in_range(values, 11, 11), 0)


if __name__ == "__main__":
    unittest.main()
