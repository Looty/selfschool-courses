"""The provisioning job and the Redis helpers it shares with the API.

A VM record is a Redis hash at vm:<id>. Its "status" field moves:

    requested -> building -> active
                          -> error    (after MAX_ATTEMPTS failed attempts)
    any of these -> deleted           (DELETE /vms/<id>; the hash then expires)

The job is idempotent: running provision(vm_id) again for an active VM,
a deleted VM or a VM that no longer exists changes nothing, and a run that
finds the VM still "building" (an earlier run died) simply builds again.
"""
import os
import secrets
import time
from contextlib import contextmanager

from redis import Redis
from rq import Retry

QUEUE_NAME = "vms"
RETRY = Retry(max=2, interval=[2, 4])   # 2 retries, so at most 3 attempts
MAX_ATTEMPTS = RETRY.max + 1
JOB_TIMEOUT = 60                         # seconds; RQ's default is 180
LOCK_SECONDS = 10

UNLOCK_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


class LockTimeout(Exception):
    """Another process held the VM's lock for too long."""


def redis_from_env():
    """Connect to the Redis named by REDIS_URL, returning str instead of bytes."""
    return Redis.from_url(os.environ.get("REDIS_URL", "redis://localhost:6379/0"),
                          decode_responses=True)


def vm_key(vm_id):
    return f"vm:{vm_id}"


@contextmanager
def vm_lock(r, vm_id, wait_seconds=5.0):
    """Hold lock:vm:<id> with SET NX EX; release it only if it is still ours."""
    key = f"lock:{vm_key(vm_id)}"
    token = secrets.token_hex(16)
    deadline = time.monotonic() + wait_seconds
    while not r.set(key, token, nx=True, ex=LOCK_SECONDS):
        if time.monotonic() > deadline:
            raise LockTimeout(key)
        time.sleep(0.05)
    try:
        yield
    finally:
        r.eval(UNLOCK_SCRIPT, 1, key, token)


def transition(r, vm_id, allowed_from, to, **fields):
    """Set status to `to` if the current status is in allowed_from.

    Returns the status after the call (None if the VM does not exist).
    The lock makes the read and the write one step for every process that
    also takes the lock (the API's DELETE and every worker).
    """
    with vm_lock(r, vm_id):
        status = r.hget(vm_key(vm_id), "status")
        if status not in allowed_from:
            return status
        r.hset(vm_key(vm_id), mapping={"status": to, **fields})
        return to


def simulate_build(r, vm_id, build_seconds):
    """Stand-in for the hypervisor call: wait, then fail if the request asked to."""
    time.sleep(build_seconds)
    if r.hget(vm_key(vm_id), "fail") == "1":
        raise RuntimeError("simulated hypervisor error")


def record_failure(r, vm_id, exc):
    """Count a failed attempt; the last allowed attempt moves the VM to error."""
    with vm_lock(r, vm_id):
        if r.hget(vm_key(vm_id), "status") != "building":
            return
        attempts = r.hincrby(vm_key(vm_id), "attempts", 1)
        fields = {"error": str(exc)}
        if attempts >= MAX_ATTEMPTS:
            fields["status"] = "error"
        r.hset(vm_key(vm_id), mapping=fields)


def run_provision(r, vm_id, build_seconds):
    """The job's logic, with the Redis connection passed in so tests can use a fake."""
    status = transition(r, vm_id, ("requested", "building"), "building")
    if status != "building":
        return status            # active, error, deleted or gone: nothing to do
    try:
        simulate_build(r, vm_id, build_seconds)
    except Exception as exc:
        record_failure(r, vm_id, exc)
        raise                    # RQ sees the failure and schedules a retry
    return transition(r, vm_id, ("building",), "active")


def provision(vm_id):
    """The function RQ runs. Its only argument is a string, so any serializer works."""
    build_seconds = float(os.environ.get("BUILD_SECONDS", "2"))
    return run_provision(redis_from_env(), vm_id, build_seconds)
