import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "inventory_starter"
mod = importlib.import_module(TARGET)


class InventoryTest(unittest.TestCase):
    def setUp(self):
        self.inv = mod.Inventory()
        self.inv.add_host("kvm-01", 16)
        self.inv.add_host("kvm-02", 32)

    def test_allocate_returns_free_left(self):
        self.assertEqual(self.inv.allocate("kvm-01", 4), 12)
        self.assertEqual(self.inv.free("kvm-01"), 12)

    def test_release_returns_free_after(self):
        self.inv.allocate("kvm-01", 10)
        self.assertEqual(self.inv.release("kvm-01", 4), 10)

    def test_allocate_exactly_to_capacity(self):
        self.assertEqual(self.inv.allocate("kvm-01", 16), 0)

    def test_over_capacity_raises_and_changes_nothing(self):
        self.inv.allocate("kvm-01", 10)
        with self.assertRaises(mod.CapacityError):
            self.inv.allocate("kvm-01", 7)
        self.assertEqual(self.inv.free("kvm-01"), 6)

    def test_capacity_error_is_an_inventory_error(self):
        with self.assertRaises(mod.InventoryError):
            self.inv.allocate("kvm-01", 17)

    def test_unknown_host(self):
        with self.assertRaises(mod.UnknownHostError):
            self.inv.allocate("kvm-99", 1)
        with self.assertRaises(mod.UnknownHostError):
            self.inv.release("kvm-99", 1)
        with self.assertRaises(mod.UnknownHostError):
            self.inv.free("kvm-99")

    def test_bad_amounts_raise_value_error(self):
        with self.assertRaises(ValueError):
            self.inv.allocate("kvm-01", 0)
        with self.assertRaises(ValueError):
            self.inv.allocate("kvm-99", -1)
        with self.assertRaises(ValueError):
            self.inv.release("kvm-01", 1)

    def test_add_host_validation(self):
        with self.assertRaises(ValueError):
            self.inv.add_host("", 8)
        with self.assertRaises(ValueError):
            self.inv.add_host("kvm-03", 0)
        with self.assertRaises(mod.InventoryError):
            self.inv.add_host("kvm-01", 8)

    def test_duplicate_host_error_is_not_value_error(self):
        try:
            self.inv.add_host("kvm-01", 8)
        except ValueError:
            self.fail("a duplicate host is an InventoryError, not a ValueError")
        except mod.InventoryError:
            pass

    def test_len_and_contains(self):
        self.assertEqual(len(self.inv), 2)
        self.assertIn("kvm-02", self.inv)
        self.assertNotIn("kvm-03", self.inv)

    def test_repr(self):
        self.inv.allocate("kvm-01", 3)
        self.assertEqual(repr(self.inv), "Inventory(hosts=2, used=3/48)")
        self.assertEqual(repr(mod.Inventory()), "Inventory(hosts=0, used=0/0)")

    def test_instances_do_not_share_state(self):
        other = mod.Inventory()
        self.assertEqual(len(other), 0)
        self.assertNotIn("kvm-01", other)


if __name__ == "__main__":
    unittest.main()
