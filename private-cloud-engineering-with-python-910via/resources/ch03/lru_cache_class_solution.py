"""Reference solution for the LRU cache exercise (see lru_cache_class_starter.py)."""
from collections import OrderedDict
import time


class LRUCache:
    def __init__(self, capacity, ttl=None, clock=time.monotonic):
        """Create an empty cache."""
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self.ttl = ttl
        self.clock = clock
        self._data = OrderedDict()          # key -> (value, expires_at); oldest first

    def get(self, key, default=None):
        """Return the cached value or `default`."""
        entry = self._data.get(key)
        if entry is None:
            return default
        value, expires_at = entry
        if expires_at is not None and self.clock() >= expires_at:
            del self._data[key]
            return default
        self._data.move_to_end(key)         # now the most recently used
        return value

    def put(self, key, value):
        """Store a value, evicting the least recently used entry if over capacity."""
        expires_at = None if self.ttl is None else self.clock() + self.ttl
        self._data[key] = (value, expires_at)
        self._data.move_to_end(key)         # assignment alone keeps an existing key's place
        if len(self._data) > self.capacity:
            self._data.popitem(last=False)  # drop the least recently used

    def __len__(self):
        """Return the number of stored entries."""
        return len(self._data)


# Complexity: get and put are O(1) on average (a dict lookup plus O(1) reordering in the
# OrderedDict's linked list); space is O(capacity).
# Alternative: a plain dict also keeps insertion order, so `d[k] = d.pop(k)` moves a key to the
# end and `next(iter(d))` finds the oldest; or write the classic hash map plus doubly linked
# list by hand when the screen asks you not to use OrderedDict.
