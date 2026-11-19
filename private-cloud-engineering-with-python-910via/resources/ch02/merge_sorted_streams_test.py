import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "merge_sorted_streams_starter"
mod = importlib.import_module(TARGET)


class Opaque:
    """A message stand-in that refuses to be compared."""

    def __init__(self, label):
        self.label = label

    def __lt__(self, other):
        raise AssertionError("messages must not be compared")

    __gt__ = __le__ = __ge__ = __lt__


class MergeSortedStreamsTest(unittest.TestCase):
    def test_example_1(self):
        streams = [
            [(1, "a1"), (4, "a2")],
            [(2, "b1"), (3, "b2"), (9, "b3")],
        ]
        self.assertEqual(
            mod.merge_sorted_streams(streams),
            [(1, "a1"), (2, "b1"), (3, "b2"), (4, "a2"), (9, "b3")],
        )

    def test_equal_timestamps_lower_stream_first(self):
        self.assertEqual(mod.merge_sorted_streams([[(5, "x")], [(5, "w")]]), [(5, "x"), (5, "w")])

    def test_no_streams(self):
        self.assertEqual(mod.merge_sorted_streams([]), [])

    def test_all_streams_empty(self):
        self.assertEqual(mod.merge_sorted_streams([[], [], []]), [])

    def test_some_streams_empty(self):
        self.assertEqual(mod.merge_sorted_streams([[], [(1, "a")], []]), [(1, "a")])

    def test_single_stream_is_returned_as_is(self):
        stream = [(1, "a"), (1, "b"), (2, "c")]
        self.assertEqual(mod.merge_sorted_streams([stream]), stream)

    def test_equal_timestamps_inside_one_stream_keep_order(self):
        streams = [[(3, "first"), (3, "second")], [(3, "other")]]
        self.assertEqual(
            mod.merge_sorted_streams(streams),
            [(3, "first"), (3, "second"), (3, "other")],
        )

    def test_three_streams(self):
        streams = [[(1, "a"), (7, "b")], [(2, "c"), (8, "d")], [(0, "e"), (9, "f")]]
        self.assertEqual(
            mod.merge_sorted_streams(streams),
            [(0, "e"), (1, "a"), (2, "c"), (7, "b"), (8, "d"), (9, "f")],
        )

    def test_messages_are_never_compared(self):
        a, b, c = Opaque("a"), Opaque("b"), Opaque("c")
        result = mod.merge_sorted_streams([[(1, a), (2, c)], [(1, b)]])
        self.assertEqual([entry[1].label for entry in result], ["a", "b", "c"])

    def test_input_is_not_modified(self):
        streams = [[(1, "a")], [(0, "b")]]
        mod.merge_sorted_streams(streams)
        self.assertEqual(streams, [[(1, "a")], [(0, "b")]])

    def test_large_input(self):
        streams = [[(t, f"s{s}") for t in range(s, 30000, 3)] for s in range(3)]
        result = mod.merge_sorted_streams(streams)
        self.assertEqual(len(result), 30000)
        self.assertEqual([t for t, _ in result], list(range(30000)))


if __name__ == "__main__":
    unittest.main()
