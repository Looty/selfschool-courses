import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "place_vms_starter"
mod = importlib.import_module(TARGET)


class PlaceVmsTest(unittest.TestCase):
    def test_first_fit_example(self):
        hosts = {"hv1": (8, 32), "hv2": (4, 16)}
        vms = [("a", 4, 16), ("b", 8, 32)]
        self.assertEqual(mod.place_vms(hosts, vms, "first_fit"), ({"a": "hv1"}, ["b"]))

    def test_best_fit_example(self):
        hosts = {"hv1": (8, 32), "hv2": (4, 16)}
        vms = [("a", 4, 16), ("b", 8, 32)]
        self.assertEqual(mod.place_vms(hosts, vms, "best_fit"), ({"a": "hv2", "b": "hv1"}, []))

    def test_default_is_first_fit_in_arrival_order(self):
        hosts = {"hv1": (10, 64), "hv2": (10, 64)}
        vms = [("s1", 4, 8), ("s2", 4, 8), ("b1", 6, 8), ("b2", 6, 8)]
        self.assertEqual(
            mod.place_vms(hosts, vms),
            ({"s1": "hv1", "s2": "hv1", "b1": "hv2"}, ["b2"]),
        )

    def test_largest_first_places_everything(self):
        hosts = {"hv1": (10, 64), "hv2": (10, 64)}
        vms = [("s1", 4, 8), ("s2", 4, 8), ("b1", 6, 8), ("b2", 6, 8)]
        self.assertEqual(
            mod.place_vms(hosts, vms, largest_first=True),
            ({"b1": "hv1", "b2": "hv2", "s1": "hv1", "s2": "hv2"}, []),
        )

    def test_both_resources_must_fit(self):
        hosts = {"cpu-rich": (64, 4), "ram-rich": (2, 512), "balanced": (8, 32)}
        vms = [("db", 8, 32)]
        for strategy in ("first_fit", "best_fit"):
            with self.subTest(strategy=strategy):
                self.assertEqual(mod.place_vms(hosts, vms, strategy), ({"db": "balanced"}, []))

    def test_best_fit_tie_breaks(self):
        # Same CPU left on b and c (0); c leaves less RAM. a leaves more CPU.
        hosts = {"a": (6, 8), "b": (4, 32), "c": (4, 16)}
        self.assertEqual(mod.place_vms(hosts, [("vm", 4, 8)], "best_fit"), ({"vm": "c"}, []))
        # Full tie on CPU and RAM left: the earlier host wins.
        hosts = {"x": (4, 16), "y": (4, 16)}
        self.assertEqual(mod.place_vms(hosts, [("vm", 2, 8)], "best_fit"), ({"vm": "x"}, []))

    def test_unplaced_keeps_arrival_order_with_largest_first(self):
        hosts = {"hv1": (4, 16)}
        vms = [("tiny", 1, 1), ("huge", 64, 256), ("mid", 4, 16), ("big", 32, 64)]
        assignment, unplaced = mod.place_vms(hosts, vms, largest_first=True)
        self.assertEqual(assignment, {"mid": "hv1"})
        self.assertEqual(unplaced, ["tiny", "huge", "big"])

    def test_largest_first_orders_by_cpu_then_ram_then_arrival(self):
        hosts = {"hv1": (4, 100), "hv2": (4, 100), "hv3": (4, 100)}
        vms = [("a", 4, 8), ("b", 4, 16), ("c", 4, 8)]
        assignment, unplaced = mod.place_vms(hosts, vms, largest_first=True)
        self.assertEqual(assignment, {"b": "hv1", "a": "hv2", "c": "hv3"})
        self.assertEqual(unplaced, [])

    def test_inputs_are_not_modified(self):
        hosts = {"hv1": (8, 32)}
        vms = [("b", 2, 4), ("a", 4, 8)]
        mod.place_vms(hosts, vms, "best_fit", largest_first=True)
        self.assertEqual(hosts, {"hv1": (8, 32)})
        self.assertEqual(vms, [("b", 2, 4), ("a", 4, 8)])

    def test_empty_inputs(self):
        self.assertEqual(mod.place_vms({}, [("a", 1, 1)]), ({}, ["a"]))
        self.assertEqual(mod.place_vms({"hv1": (1, 1)}, []), ({}, []))

    def test_exact_fit_and_zero_sized_request(self):
        hosts = {"hv1": (2, 4)}
        vms = [("exact", 2, 4), ("zero", 0, 0), ("one", 1, 1)]
        self.assertEqual(mod.place_vms(hosts, vms), ({"exact": "hv1", "zero": "hv1"}, ["one"]))

    def test_unknown_strategy_raises(self):
        with self.assertRaises(ValueError):
            mod.place_vms({"hv1": (1, 1)}, [("a", 1, 1)], strategy="worst_fit")


if __name__ == "__main__":
    unittest.main()
