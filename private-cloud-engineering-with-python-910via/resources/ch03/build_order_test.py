import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "build_order_starter"
mod = importlib.import_module(TARGET)

EXAMPLE = {
    "app": ["libnet", "libjson"],
    "libnet": ["libc"],
    "libjson": ["libc"],
    "tests": ["app"],
}


def implementations():
    funcs = [mod.build_order]
    if hasattr(mod, "build_order_graphlib"):
        funcs.append(mod.build_order_graphlib)
    return funcs


class BuildOrderTest(unittest.TestCase):
    def assert_valid_order(self, deps, order):
        position = {name: i for i, name in enumerate(order)}
        for target, needs in deps.items():
            for name in needs:
                self.assertLess(position[name], position[target], f"{name} must build before {target}")

    def assert_reported_cycle(self, deps, message):
        prefix = "dependency cycle: "
        self.assertTrue(message.startswith(prefix), message)
        names = message[len(prefix):].split(" -> ")
        self.assertGreaterEqual(len(names), 2)
        self.assertEqual(names[0], names[-1])
        for a, b in zip(names, names[1:]):
            self.assertIn(b, deps.get(a, []), f"{a} does not depend on {b}")

    def test_example(self):
        for func in implementations():
            with self.subTest(func=func.__name__):
                order, levels = func(EXAMPLE)
                self.assertEqual(levels, [["libc"], ["libjson", "libnet"], ["app"], ["tests"]])
                self.assertEqual(order, ["libc", "libjson", "libnet", "app", "tests"])

    def test_empty(self):
        for func in implementations():
            with self.subTest(func=func.__name__):
                self.assertEqual(func({}), ([], []))

    def test_independent_targets_share_one_level(self):
        deps = {"b": [], "c": [], "a": []}
        for func in implementations():
            with self.subTest(func=func.__name__):
                self.assertEqual(func(deps), (["a", "b", "c"], [["a", "b", "c"]]))

    def test_level_is_the_longest_path_not_the_first_seen(self):
        # d depends on a (level 0) and on c (level 2), so d is in level 3.
        deps = {"b": ["a"], "c": ["b"], "d": ["a", "c"]}
        for func in implementations():
            with self.subTest(func=func.__name__):
                order, levels = func(deps)
                self.assertEqual(levels, [["a"], ["b"], ["c"], ["d"]])
                self.assert_valid_order(deps, order)

    def test_duplicate_dependencies_count_once(self):
        deps = {"app": ["lib", "lib", "lib"], "lib": []}
        for func in implementations():
            with self.subTest(func=func.__name__):
                self.assertEqual(func(deps), (["lib", "app"], [["lib"], ["app"]]))

    def test_larger_graph_is_valid(self):
        deps = {f"t{i}": [f"t{j}" for j in range(i) if i % (j + 1) == 0] for i in range(60)}
        for func in implementations():
            with self.subTest(func=func.__name__):
                order, levels = func(deps)
                self.assertEqual(sorted(order), sorted(deps))
                self.assert_valid_order(deps, order)

    def test_cycle_is_named(self):
        deps = {"a": ["b"], "b": ["c"], "c": ["a"], "d": ["a"], "e": []}
        for func in implementations():
            with self.subTest(func=func.__name__):
                with self.assertRaises(ValueError) as caught:
                    func(deps)
                self.assert_reported_cycle(deps, str(caught.exception))

    def test_self_dependency_is_a_cycle(self):
        deps = {"a": ["a"], "b": []}
        for func in implementations():
            with self.subTest(func=func.__name__):
                with self.assertRaises(ValueError) as caught:
                    func(deps)
                self.assertEqual(str(caught.exception), "dependency cycle: a -> a")

    def test_cycle_behind_a_valid_part(self):
        deps = {"base": [], "x": ["base", "y"], "y": ["z"], "z": ["x"]}
        for func in implementations():
            with self.subTest(func=func.__name__):
                with self.assertRaises(ValueError) as caught:
                    func(deps)
                self.assert_reported_cycle(deps, str(caught.exception))


if __name__ == "__main__":
    unittest.main()
