"""Sum pairs (a complete program: read standard input, write standard output).

Read several pairs of integers and print the sum of each pair.

Input
    Line 1: an integer N, the number of pairs (0 <= N <= 100000).
    Next N lines: two integers a and b separated by whitespace
    (-10**18 <= a, b <= 10**18). Lines may carry extra spaces.

Output
    N lines. Line i holds a + b for pair i. Nothing else: no prompt,
    no debug text, no trailing spaces. The grader compares strings exactly.

Example 1
    Input:
        3
        1 5
        3 10
        999 -34343
    Output:
        6
        13
        -33344

Example 2
    Input:
        1
        -7 7
    Output:
        0

Example 3
    Input:
        0
    Output:
        (nothing at all)

Write the logic in solve() so that it can be tested without a terminal.
main() is the thin wrapper a browser platform would run.
"""
import sys


def solve(text: str) -> str:
    """Return the output for the whole input text, lines joined by a newline."""
    raise NotImplementedError


def main() -> None:
    result = solve(sys.stdin.read())
    if result:
        print(result)


if __name__ == "__main__":
    main()
