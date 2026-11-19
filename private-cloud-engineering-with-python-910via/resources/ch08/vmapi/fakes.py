"""In-memory stand-ins for Redis and an RQ queue, for unit tests only.

FakeRedis implements just the commands app.py, app_fastapi.py and tasks.py
use, with decode_responses=True behaviour (values come back as str).
FakeQueue records what would have been enqueued instead of talking to Redis.
"""


class FakeRedis:
    def __init__(self):
        self.data = {}   # key -> str (strings) or dict (hashes)
        self.ttls = {}   # key -> seconds, as last set

    def ping(self):
        return True

    def set(self, key, value, nx=False, ex=None):
        if nx and key in self.data:
            return None
        self.data[key] = str(value)
        self.ttls.pop(key, None)
        if ex is not None:
            self.ttls[key] = ex
        return True

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        self.ttls.pop(key, None)
        return 1 if self.data.pop(key, None) is not None else 0

    def hset(self, key, mapping):
        self.data.setdefault(key, {}).update({k: str(v) for k, v in mapping.items()})
        return len(mapping)

    def hget(self, key, field):
        return self.data.get(key, {}).get(field)

    def hgetall(self, key):
        return dict(self.data.get(key, {}))

    def hincrby(self, key, field, amount=1):
        record = self.data.setdefault(key, {})
        record[field] = str(int(record.get(field, "0")) + amount)
        return int(record[field])

    def expire(self, key, seconds):
        if key not in self.data:
            return False
        self.ttls[key] = seconds
        return True

    def ttl(self, key):
        if key not in self.data:
            return -2
        return self.ttls.get(key, -1)

    def eval(self, script, numkeys, key, token):
        # Only the compare-and-delete unlock script is used in this project.
        if self.data.get(key) == token:
            return self.delete(key)
        return 0


class FakeQueue:
    def __init__(self):
        self.jobs = []   # (func, args, options) for every enqueue call

    def enqueue(self, func, *args, **options):
        self.jobs.append((func, args, options))
        return options.get("job_id")
