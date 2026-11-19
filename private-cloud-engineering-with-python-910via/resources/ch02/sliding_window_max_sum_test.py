import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "sliding_window_max_sum_starter"
mod = importlib.import_module(TARGET)


class SlidingWindowMaxSumTest(unittest.TestCase):
    def test_example_1(self):
        self.assertEqual(mod.sliding_window_max_sum([1, 4, 2, 10, 23, 3, 1, 0, 20], 4), 39)

    def test_all_negative(self):
        self.assertEqual(mod.sliding_window_max_sum([-5, -2, -8], 2), -7)

    def test_single_element(self):
        self.assertEqual(mod.sliding_window_max_sum([7], 1), 7)

    def test_window_is_whole_list(self):
        self.assertEqual(mod.sliding_window_max_sum([3, -1, 4], 3), 6)

    def test_window_of_one_is_the_maximum(self):
        self.assertEqual(mod.sliding_window_max_sum([2, 9, -3, 5], 1), 9)

    def test_best_window_is_first(self):
        self.assertEqual(mod.sliding_window_max_sum([9, 9, 1, 1, 1], 2), 18)

    def test_best_window_is_last(self):
        self.assertEqual(mod.sliding_window_max_sum([1, 1, 1, 9, 9], 2), 18)

    def test_k_zero_raises(self):
        with self.assertRaises(ValueError):
            mod.sliding_window_max_sum([1, 2, 3], 0)

    def test_k_too_large_raises(self):
        with self.assertRaises(ValueError):
            mod.sliding_window_max_sum([1, 2, 3], 4)

    def test_empty_list_raises(self):
        with self.assertRaises(ValueError):
            mod.sliding_window_max_sum([], 1)

    def test_input_list_is_not_modified(self):
        nums = [1, 2, 3, 4]
        mod.sliding_window_max_sum(nums, 2)
        self.assertEqual(nums, [1, 2, 3, 4])

    def test_large_input_runs_in_linear_time(self):
        nums = list(range(200000))
        k = 100000
        expected = sum(range(100000, 200000))
        self.assertEqual(mod.sliding_window_max_sum(nums, k), expected)


if __name__ == "__main__":
    unittest.main()
