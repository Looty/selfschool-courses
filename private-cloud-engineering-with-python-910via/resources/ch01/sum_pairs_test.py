import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "sum_pairs_starter"
mod = importlib.import_module(TARGET)

import contextlib
import io
from unittest import mock


class SolveTest(unittest.TestCase):
    def test_documented_sample(self):
        self.assertEqual(mod.solve("3\n1 5\n3 10\n999 -34343\n"), "6\n13\n-33344")

    def test_single_pair(self):
        self.assertEqual(mod.solve("1\n-7 7\n"), "0")

    def test_zero_pairs_gives_empty_output(self):
        self.assertEqual(mod.solve("0\n"), "")

    def test_no_trailing_newline_in_input(self):
        self.assertEqual(mod.solve("2\n1 2\n3 4"), "3\n7")

    def test_extra_spaces_and_tabs(self):
        self.assertEqual(mod.solve("  2 \n  10    20  \n\t-1\t-2\n"), "30\n-3")

    def test_windows_line_endings(self):
        self.assertEqual(mod.solve("2\r\n1 1\r\n2 2\r\n"), "2\n4")

    def test_big_integers(self):
        big = 10 ** 18
        self.assertEqual(mod.solve(f"1\n{big} {big}\n"), str(2 * big))

    def test_lines_after_the_first_n_pairs_are_ignored(self):
        self.assertEqual(mod.solve("1\n4 5\n100 200\n"), "9")

    def test_output_has_no_stray_whitespace(self):
        out = mod.solve("3\n0 0\n1 1\n2 2\n")
        self.assertEqual(out.split("\n"), ["0", "2", "4"])

    def test_many_pairs(self):
        n = 50000
        text = f"{n}\n" + "".join(f"{i} {i}\n" for i in range(n))
        lines = mod.solve(text).split("\n")
        self.assertEqual(len(lines), n)
        self.assertEqual(lines[-1], str(2 * (n - 1)))


class MainTest(unittest.TestCase):
    def run_main(self, stdin_text):
        out = io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(stdin_text)), contextlib.redirect_stdout(out):
            mod.main()
        return out.getvalue()

    def test_main_prints_exactly_the_expected_text(self):
        self.assertEqual(self.run_main("3\n1 5\n3 10\n999 -34343\n"), "6\n13\n-33344\n")

    def test_main_prints_nothing_for_zero_pairs(self):
        self.assertEqual(self.run_main("0\n"), "")


if __name__ == "__main__":
    unittest.main()
