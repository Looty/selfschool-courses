"""Scenario 2: a memory leak. A 'cache' that only ever grows."""
import time

CACHE = []


def handle_request(i: int) -> None:
    CACHE.append(bytearray(8 * 1024 * 1024))  # 8 MiB per request, never evicted
    if i % 5 == 0:
        print(f"handled {i} requests, cache entries: {len(CACHE)}", flush=True)


def main() -> None:
    i = 0
    while True:
        i += 1
        handle_request(i)
        time.sleep(0.25)


if __name__ == "__main__":
    main()
