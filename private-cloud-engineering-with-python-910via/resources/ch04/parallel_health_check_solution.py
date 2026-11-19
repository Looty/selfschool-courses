"""Reference solution for the parallel health check exercise (see the starter file)."""
from concurrent.futures import ThreadPoolExecutor, wait


def parallel_health_check(hosts, check, timeout=2.0, max_workers=None):
    """Return [(host, status, detail), ...] in input order; never raise."""
    if not hosts:
        return []
    workers = max_workers or min(32, len(hosts))
    pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="health")
    try:
        futures = [pool.submit(check, host) for host in hosts]   # list keeps input order
        done, _not_done = wait(futures, timeout=timeout)
        results = []
        for host, future in zip(hosts, futures):
            if future not in done:
                future.cancel()                  # only helps if it has not started yet
                results.append((host, "timeout", f"no answer within {timeout}s"))
                continue
            try:
                healthy = future.result()        # re-raises the check's own exception
            except Exception as exc:
                results.append((host, "error", f"{type(exc).__name__}: {exc}"))
            else:
                results.append((host, "up" if healthy else "down", ""))
        return results
    finally:
        # Do not block on checks that are still hanging; drop the ones not yet started.
        pool.shutdown(wait=False, cancel_futures=True)


# Complexity: N submissions and one pass over the futures, O(N) time and space in the caller;
# wall time is about max(check time, timeout) when max_workers >= N, and grows in rounds of
# max_workers when the pool is smaller.
# Alternative: as_completed(futures, timeout=...) handles results in finish order (good for a
# progress display) but you must map each future back to its host and catch TimeoutError; in
# asyncio, gather(..., return_exceptions=True) inside asyncio.timeout() is the same shape.
