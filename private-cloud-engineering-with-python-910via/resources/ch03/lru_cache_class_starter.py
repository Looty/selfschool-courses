"""Exercise: an LRU cache with an optional TTL (time box: 15 minutes).

Write a class LRUCache(capacity, ttl=None, clock=time.monotonic).

    capacity  maximum number of entries, an int of at least 1 (else ValueError)
    ttl       None for no expiry, or a number of seconds an entry stays valid
              after it was last PUT (a get does not extend it)
    clock     a function returning the current time in seconds; tests pass a
              fake clock so nothing ever really waits

Methods, each O(1):

    get(key, default=None)  return the value, or `default` if the key is
                            missing or expired. A hit makes the key the most
                            recently used. An expired entry is removed.
    put(key, value)         insert or replace the value, make the key the most
                            recently used and restart its TTL. If the cache now
                            holds more than `capacity` entries, remove the
                            least recently used one.
    __len__()               number of entries stored (an expired entry that has
                            not been touched yet may still be counted)

Example:

    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")        # 1, and "a" is now the most recently used
    cache.put("c", 3)     # evicts "b", the least recently used
    cache.get("b")        # None

    now = [0.0]
    cache = LRUCache(10, ttl=30, clock=lambda: now[0])
    cache.put("vm-17", "running")
    now[0] = 29.9
    cache.get("vm-17")    # "running"
    now[0] = 30.0
    cache.get("vm-17")    # None: an entry put at t expires at t + ttl

Check your work:  python lru_cache_class_test.py
"""
import time


class LRUCache:
    def __init__(self, capacity, ttl=None, clock=time.monotonic):
        """Create an empty cache."""
        raise NotImplementedError

    def get(self, key, default=None):
        """Return the cached value or `default`."""
        raise NotImplementedError

    def put(self, key, value):
        """Store a value, evicting the least recently used entry if over capacity."""
        raise NotImplementedError

    def __len__(self):
        """Return the number of stored entries."""
        raise NotImplementedError
