"""Reference solution for sum_pairs (see sum_pairs_starter.py for the statement)."""
import sys


def solve(text: str) -> str:
    """Return the output for the whole input text, lines joined by a newline."""
    tokens = text.split()
    n = int(tokens[0])
    sums = []
    for i in range(n):
        a = int(tokens[1 + 2 * i])
        b = int(tokens[2 + 2 * i])
        sums.append(str(a + b))
    return "\n".join(sums)


def main() -> None:
    result = solve(sys.stdin.read())
    if result:
        print(result)


if __name__ == "__main__":
    main()

# Complexity: O(N) time and O(N) extra space (all tokens and all output lines
# are held in memory; 100000 pairs is small against a 512 MB limit).
# Why tokens: splitting the whole input on whitespace ignores extra spaces,
# blank lines and Windows line endings in one step.
# Alternative: read line by line, which is what you type first in a session:
#     n = int(input())
#     for _ in range(n):
#         a, b = map(int, input().split())
#         print(a + b)
# It uses O(1) extra space but calls print() N times.
