import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "top_k_frequent_starter"
mod = importlib.import_module(TARGET)


class TopKFrequentTest(unittest.TestCase):
    def test_example_1(self):
        items = ["kvm-02", "kvm-01", "kvm-02", "kvm-03", "kvm-02", "kvm-01"]
        self.assertEqual(mod.top_k_frequent(items, 2), [("kvm-02", 3), ("kvm-01", 2)])

    def test_tie_is_alphabetical(self):
        self.assertEqual(mod.top_k_frequent(["c", "a", "b"], 2), [("a", 1), ("b", 1)])

    def test_tie_inside_the_result(self):
        items = ["x", "y", "y", "x", "z"]
        self.assertEqual(mod.top_k_frequent(items, 3), [("x", 2), ("y", 2), ("z", 1)])

    def test_empty_input(self):
        self.assertEqual(mod.top_k_frequent([], 3), [])

    def test_k_zero(self):
        self.assertEqual(mod.top_k_frequent(["a", "a"], 0), [])

    def test_negative_k(self):
        self.assertEqual(mod.top_k_frequent(["a", "a"], -1), [])

    def test_k_larger_than_distinct_items(self):
        self.assertEqual(mod.top_k_frequent(["b", "a", "b"], 10), [("b", 2), ("a", 1)])

    def test_single_item(self):
        self.assertEqual(mod.top_k_frequent(["only"], 1), [("only", 1)])

    def test_result_is_a_list_of_tuples(self):
        result = mod.top_k_frequent(["a", "a", "b"], 1)
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], tuple)

    def test_large_input(self):
        items = []
        for i in range(2000):
            items.extend([f"host-{i:04d}"] * (i % 50 + 1))
        result = mod.top_k_frequent(items, 3)
        self.assertEqual(result, [("host-0049", 50), ("host-0099", 50), ("host-0149", 50)])


if __name__ == "__main__":
    unittest.main()
