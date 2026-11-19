"""Reference solution for parse_log_line (see parse_log_line_starter.py)."""
import re

LINE_RE = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) "
    r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL) "
    r"\[(?P<host>[\w.-]+)\] "
    r"(?P<component>\w+): "
    r"(?P<message>.*)",
    re.ASCII,
)


def parse_log_line(line: str) -> "dict[str, str] | None":
    """Return the fields of one log line as a dict, or None if it does not match."""
    if line.endswith("\n"):
        line = line[:-1]
    match = LINE_RE.fullmatch(line)
    if match is None:
        return None
    return match.groupdict()

# Complexity: O(L) for a line of length L.
# fullmatch anchors both ends, so text before the timestamp fails (search
# would skip it) and nothing can follow the message. `.*` does not cross a
# newline, so a line with an embedded newline does not match.
# re.ASCII makes \d mean [0-9] and \w mean [a-zA-Z0-9_]; without it \d also
# accepts other Unicode digits.
# Strip only the one newline: line.strip() would also eat trailing spaces
# that belong to the message.
# Alternative: line.split(" ", 5) plus checks on each part. Faster to run,
# but every rule (level list, brackets, colon) becomes a separate if.
