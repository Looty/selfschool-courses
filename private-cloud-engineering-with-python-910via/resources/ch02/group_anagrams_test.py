import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "group_anagrams_starter"
mod = importlib.import_module(TARGET)


class GroupAnagramsTest(unittest.TestCase):
    def test_example_1(self):
        self.assertEqual(
            mod.group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]),
            [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]],
        )

    def test_empty_input(self):
        self.assertEqual(mod.group_anagrams([]), [])

    def test_single_word(self):
        self.assertEqual(mod.group_anagrams(["kvm"]), [["kvm"]])

    def test_empty_strings_form_one_group(self):
        self.assertEqual(mod.group_anagrams(["", "b", ""]), [["", ""], ["b"]])

    def test_duplicates_are_kept(self):
        self.assertEqual(mod.group_anagrams(["ab", "ba", "ab"]), [["ab", "ba", "ab"]])

    def test_no_anagrams(self):
        self.assertEqual(mod.group_anagrams(["a", "b", "c"]), [["a"], ["b"], ["c"]])

    def test_same_letters_different_counts_are_not_anagrams(self):
        self.assertEqual(mod.group_anagrams(["aab", "abb", "baa"]), [["aab", "baa"], ["abb"]])

    def test_group_order_follows_first_appearance(self):
        self.assertEqual(
            mod.group_anagrams(["tan", "eat", "nat", "tea"]),
            [["tan", "nat"], ["eat", "tea"]],
        )

    def test_input_list_is_not_modified(self):
        words = ["eat", "tea"]
        mod.group_anagrams(words)
        self.assertEqual(words, ["eat", "tea"])

    def test_large_input(self):
        words = ["abc", "bca", "xyz"] * 3000
        result = mod.group_anagrams(words)
        self.assertEqual([len(group) for group in result], [6000, 3000])


if __name__ == "__main__":
    unittest.main()
