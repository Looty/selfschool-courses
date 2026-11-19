import importlib
import sys
import unittest

TARGET = sys.argv.pop(1) if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "lru_cache_class_starter"
mod = importlib.import_module(TARGET)


class FakeClock:
    def __init__(self, now=0.0):
        self.now = now

    def __call__(self):
        return self.now


class LRUCacheTest(unittest.TestCase):
    def test_docstring_example(self):
        cache = mod.LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        self.assertEqual(cache.get("a"), 1)
        cache.put("c", 3)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(cache.get("a"), 1)
        self.assertEqual(cache.get("c"), 3)
        self.assertEqual(len(cache), 2)

    def test_default_for_missing_key(self):
        cache = mod.LRUCache(1)
        self.assertEqual(cache.get("nope", "fallback"), "fallback")
        self.assertIsNone(cache.get("nope"))

    def test_falsy_values_are_cached(self):
        cache = mod.LRUCache(3)
        cache.put("zero", 0)
        cache.put("none", None)
        self.assertEqual(cache.get("zero", "miss"), 0)
        self.assertIsNone(cache.get("none", "miss"))

    def test_put_existing_key_updates_and_refreshes(self):
        cache = mod.LRUCache(2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("a", 10)          # "a" becomes most recent, so "b" is evicted next
        cache.put("c", 3)
        self.assertEqual(cache.get("a"), 10)
        self.assertIsNone(cache.get("b"))
        self.assertEqual(len(cache), 2)

    def test_capacity_one(self):
        cache = mod.LRUCache(1)
        cache.put("a", 1)
        cache.put("b", 2)
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 2)

    def test_invalid_capacity(self):
        for bad in (0, -3):
            with self.subTest(capacity=bad):
                with self.assertRaises(ValueError):
                    mod.LRUCache(bad)

    def test_eviction_order_follows_gets(self):
        cache = mod.LRUCache(3)
        for key in "abc":
            cache.put(key, key.upper())
        cache.get("a")
        cache.get("b")
        cache.put("d", "D")         # "c" is now the least recently used
        self.assertIsNone(cache.get("c"))
        self.assertEqual([cache.get(k) for k in "abd"], ["A", "B", "D"])

    def test_ttl_expiry_uses_injected_clock(self):
        clock = FakeClock()
        cache = mod.LRUCache(10, ttl=30, clock=clock)
        cache.put("vm-17", "running")
        clock.now = 29.9
        self.assertEqual(cache.get("vm-17"), "running")
        clock.now = 30.0
        self.assertIsNone(cache.get("vm-17"))
        self.assertEqual(len(cache), 0)     # the expired entry was removed on access

    def test_get_does_not_extend_ttl_but_put_does(self):
        clock = FakeClock()
        cache = mod.LRUCache(10, ttl=5, clock=clock)
        cache.put("k", 1)
        clock.now = 4
        self.assertEqual(cache.get("k"), 1)
        clock.now = 6
        self.assertIsNone(cache.get("k"))   # expired at 5 even though it was read at 4
        cache.put("k", 2)                   # put at 6 -> valid until 11
        clock.now = 10.5
        self.assertEqual(cache.get("k"), 2)

    def test_no_ttl_never_expires(self):
        clock = FakeClock()
        cache = mod.LRUCache(2, clock=clock)
        cache.put("k", "v")
        clock.now = 10 ** 9
        self.assertEqual(cache.get("k"), "v")


if __name__ == "__main__":
    unittest.main()
