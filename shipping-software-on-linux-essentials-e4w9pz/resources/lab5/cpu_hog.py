"""Scenario 1: a CPU hog. A 'report' worker that never finishes its checksum loop."""
import hashlib


def checksum_forever(seed: bytes) -> None:
    digest = seed
    while True:  # the bug: the exit condition was lost in a refactor
        digest = hashlib.sha256(digest).digest()


def main() -> None:
    checksum_forever(b"nightly-report")


if __name__ == "__main__":
    main()
