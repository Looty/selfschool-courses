import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "json_flatten_starter"
mod = importlib.import_module(TARGET)


class JsonFlattenTest(unittest.TestCase):
    def test_example_1(self):
        text = '{"vm": {"name": "web-1", "disks": [{"size": 20}, {"size": 100}]}}'
        self.assertEqual(
            mod.json_flatten(text),
            {"vm.name": "web-1", "vm.disks.0.size": 20, "vm.disks.1.size": 100},
        )

    def test_custom_separator_and_scalars(self):
        self.assertEqual(mod.json_flatten('{"a": {"b": null}, "c": true}', sep="/"), {"a/b": None, "c": True})

    def test_top_level_list_raises(self):
        with self.assertRaises(ValueError):
            mod.json_flatten("[1, 2]")

    def test_top_level_scalar_raises(self):
        with self.assertRaises(ValueError):
            mod.json_flatten("42")

    def test_invalid_json_raises_value_error(self):
        with self.assertRaises(ValueError):
            mod.json_flatten("{'single': 'quotes'}")

    def test_empty_object(self):
        self.assertEqual(mod.json_flatten("{}"), {})

    def test_empty_containers_are_leaves(self):
        self.assertEqual(mod.json_flatten('{"a": {}, "b": [], "c": {"d": []}}'), {"a": {}, "b": [], "c.d": []})

    def test_flat_object_is_unchanged(self):
        self.assertEqual(mod.json_flatten('{"x": 1, "y": "z"}'), {"x": 1, "y": "z"})

    def test_nested_lists(self):
        self.assertEqual(mod.json_flatten('{"m": [[1, 2], [3]]}'), {"m.0.0": 1, "m.0.1": 2, "m.1.0": 3})

    def test_number_types_survive(self):
        result = mod.json_flatten('{"cpu": 2, "load": 0.5}')
        self.assertIsInstance(result["cpu"], int)
        self.assertIsInstance(result["load"], float)

    def test_document_order_is_kept(self):
        result = mod.json_flatten('{"z": 1, "a": {"y": 2, "b": 3}}')
        self.assertEqual(list(result), ["z", "a.y", "a.b"])


if __name__ == "__main__":
    unittest.main()
