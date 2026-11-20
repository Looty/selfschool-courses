import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "merge_reservations_starter"
mod = importlib.import_module(TARGET)


class MergeReservationsTest(unittest.TestCase):
    def test_examples(self):
        self.assertEqual(mod.merge_reservations([(1, 5), (2, 6), (8, 10)]), [(1, 6), (8, 10)])
        self.assertEqual(mod.merge_reservations([(5, 8), (1, 5)]), [(1, 8)])

    def test_empty_and_single(self):
        self.assertEqual(mod.merge_reservations([]), [])
        self.assertEqual(mod.merge_reservations([(3, 4)]), [(3, 4)])

    def test_nested_reservation_does_not_shorten_the_period(self):
        # (2, 3) lies inside (1, 10); the merged end must stay 10, not become 3.
        self.assertEqual(mod.merge_reservations([(1, 10), (2, 3), (9, 12)]), [(1, 12)])

    def test_unsorted_input_and_chain(self):
        data = [(20, 25), (1, 3), (6, 9), (2, 7), (30, 31), (24, 26)]
        self.assertEqual(mod.merge_reservations(data), [(1, 9), (20, 26), (30, 31)])

    def test_input_is_not_modified(self):
        data = [(5, 8), (1, 5)]
        mod.merge_reservations(data)
        mod.peak_concurrency(data)
        self.assertEqual(data, [(5, 8), (1, 5)])

    def test_invalid_reservation_raises(self):
        for bad in [(5, 5), (7, 2)]:
            with self.subTest(reservation=bad):
                with self.assertRaises(ValueError):
                    mod.merge_reservations([(1, 2), bad])
                with self.assertRaises(ValueError):
                    mod.peak_concurrency([(1, 2), bad])


class PeakConcurrencyTest(unittest.TestCase):
    CASES = [
        ([], 0),
        ([(1, 5)], 1),
        ([(1, 5), (2, 6), (8, 10)], 2),
        ([(1, 5), (5, 8)], 1),                       # touching is not overlapping
        ([(1, 10), (2, 3), (3, 4), (4, 5)], 2),      # short ones run one after another
        ([(1, 4), (2, 5), (3, 6), (4, 7)], 3),       # (1, 4) ends as (4, 7) starts
        ([(0, 100)] * 4, 4),                         # duplicates count separately
        ([(9, 12), (1, 10), (2, 11), (10, 11)], 3),
    ]

    def test_peak(self):
        for reservations, expected in self.CASES:
            with self.subTest(reservations=reservations):
                self.assertEqual(mod.peak_concurrency(list(reservations)), expected)

    @unittest.skipUnless(hasattr(mod, "peak_concurrency_heap"), "optional heap variant not defined")
    def test_heap_variant_agrees(self):
        for reservations, expected in self.CASES:
            with self.subTest(reservations=reservations):
                self.assertEqual(mod.peak_concurrency_heap(list(reservations)), expected)


if __name__ == "__main__":
    unittest.main()
