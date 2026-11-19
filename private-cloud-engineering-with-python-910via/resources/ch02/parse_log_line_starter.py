"""Parse a log line with a regular expression (drill, 5 to 8 minutes).

A provisioning service writes lines like this:

    2026-11-19 08:15:02,123 ERROR [kvm-07] provision: disk full on /var

Turn one line into a dict, or return None if the line is not in this format.

Format, left to right, single spaces between the parts
    timestamp  YYYY-MM-DD HH:MM:SS,mmm   (digits; exactly this shape)
    level      one of DEBUG, INFO, WARNING, ERROR, CRITICAL
    host       inside square brackets: letters, digits, '_', '.', '-'
    component  letters, digits or '_', followed by a colon and one space
    message    everything after that, possibly empty, may contain colons

Output
    {"timestamp": ..., "level": ..., "host": ..., "component": ..., "message": ...}
    All values are strings. A single trailing newline on the input is
    ignored. Anything before the timestamp makes the line invalid.

Example 1
    parse_log_line("2026-11-19 08:15:02,123 ERROR [kvm-07] provision: disk full on /var\\n")
    -> {"timestamp": "2026-11-19 08:15:02,123", "level": "ERROR",
        "host": "kvm-07", "component": "provision",
        "message": "disk full on /var"}

Example 2 (unknown level)
    parse_log_line("2026-11-19 08:15:02,123 FATAL [kvm-07] provision: x")  ->  None

Example 3 (text before the timestamp)
    parse_log_line("> 2026-11-19 08:15:02,123 INFO [kvm-07] api: ok")  ->  None
"""


def parse_log_line(line: str) -> "dict[str, str] | None":
    """Return the fields of one log line as a dict, or None if it does not match."""
    raise NotImplementedError
