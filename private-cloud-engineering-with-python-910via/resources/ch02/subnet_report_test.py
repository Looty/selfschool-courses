import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "subnet_report_starter"
mod = importlib.import_module(TARGET)


class SubnetReportTest(unittest.TestCase):
    def test_example_1(self):
        self.assertEqual(
            mod.subnet_report("10.20.0.0/29", ["10.20.0.1", "10.20.0.3"], 3),
            {"network": "10.20.0.0/29", "total": 6, "used": 2, "free": 4,
             "first_free": ["10.20.0.2", "10.20.0.4", "10.20.0.5"]},
        )

    def test_host_bits_set_are_masked(self):
        self.assertEqual(
            mod.subnet_report("192.168.1.77/30", [], 5),
            {"network": "192.168.1.76/30", "total": 2, "used": 0, "free": 2,
             "first_free": ["192.168.1.77", "192.168.1.78"]},
        )

    def test_used_outside_network_raises(self):
        with self.assertRaises(ValueError):
            mod.subnet_report("10.0.0.0/29", ["10.0.1.1"], 1)

    def test_network_and_broadcast_are_not_usable(self):
        with self.assertRaises(ValueError):
            mod.subnet_report("10.0.0.0/29", ["10.0.0.0"], 1)
        with self.assertRaises(ValueError):
            mod.subnet_report("10.0.0.0/29", ["10.0.0.7"], 1)

    def test_invalid_inputs_raise_value_error(self):
        with self.assertRaises(ValueError):
            mod.subnet_report("10.0.0.0/33", [], 1)
        with self.assertRaises(ValueError):
            mod.subnet_report("10.0.0.0/24", ["10.0.0.256"], 1)

    def test_duplicates_count_once(self):
        report = mod.subnet_report("10.0.0.0/29", ["10.0.0.1", "10.0.0.1"], 1)
        self.assertEqual((report["used"], report["free"]), (1, 5))
        self.assertEqual(report["first_free"], ["10.0.0.2"])

    def test_n_zero(self):
        self.assertEqual(mod.subnet_report("10.0.0.0/29", [], 0)["first_free"], [])

    def test_full_network(self):
        used = [f"10.0.0.{i}" for i in range(1, 7)]
        report = mod.subnet_report("10.0.0.0/29", used, 3)
        self.assertEqual((report["free"], report["first_free"]), (0, []))

    def test_slash_31_has_two_hosts(self):
        report = mod.subnet_report("10.0.0.0/31", ["10.0.0.0"], 5)
        self.assertEqual(report["total"], 2)
        self.assertEqual(report["first_free"], ["10.0.0.1"])

    def test_slash_32_has_one_host(self):
        report = mod.subnet_report("10.9.9.9/32", [], 5)
        self.assertEqual((report["total"], report["first_free"]), (1, ["10.9.9.9"]))

    def test_large_network_is_fast_and_sorted(self):
        used = [f"10.1.0.{i}" for i in range(1, 255)]
        report = mod.subnet_report("10.1.0.0/16", used, 2)
        self.assertEqual(report["total"], 65534)
        self.assertEqual(report["free"], 65534 - 254)
        self.assertEqual(report["first_free"], ["10.1.0.255", "10.1.1.0"])


if __name__ == "__main__":
    unittest.main()
