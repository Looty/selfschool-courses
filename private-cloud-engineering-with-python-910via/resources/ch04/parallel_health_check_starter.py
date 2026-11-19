"""Exercise: parallel health check (time box: 20 minutes).

Write parallel_health_check(hosts, check, timeout=2.0, max_workers=None).

    hosts        list of host names (duplicates are checked separately)
    check        a function check(host) -> bool: True if healthy. It may block
                 (it talks to the network in real use), return False, or raise.
                 Tests inject fake checks, so no real network is used.
    timeout      seconds, counted from the moment the checks are started
    max_workers  thread pool size; None means one worker per host, capped at 32

Run the checks concurrently in a concurrent.futures.ThreadPoolExecutor and
return a list with one tuple (host, status, detail) per input host, IN INPUT
ORDER, whatever order the checks finish in:

    status "up"       check returned a true value        detail ""
    status "down"     check returned a false value       detail ""
    status "error"    check raised an exception          detail "<ExceptionType>: <message>"
    status "timeout"  no answer within `timeout` s       detail "no answer within <timeout>s"

The function must never raise because of a check, and must return soon after
`timeout` even if some checks are still blocked: do not wait for them.
An empty host list returns [].

Example:

    def check(host):
        if host == "hv3":
            raise ConnectionRefusedError("port 22")
        return host != "hv2"

    parallel_health_check(["hv1", "hv2", "hv3"], check) == [
        ("hv1", "up", ""),
        ("hv2", "down", ""),
        ("hv3", "error", "ConnectionRefusedError: port 22"),
    ]

Check your work:  python parallel_health_check_test.py
"""


def parallel_health_check(hosts, check, timeout=2.0, max_workers=None):
    """Return [(host, status, detail), ...] in input order; never raise."""
    raise NotImplementedError
