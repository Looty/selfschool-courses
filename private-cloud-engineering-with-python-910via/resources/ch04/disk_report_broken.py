"""Fix the bug: a disk usage report (time box: 20 minutes).

This script runs `df -P -k <path>` for each path it is given and warns about
filesystems that are too full. It runs, and on a quiet day it even looks
right, but it has four bugs of the kind found in real ops scripts. Find and
fix them so that `python disk_report_test.py` passes.

The functions take the command runner as an argument (`runner`, by default
subprocess.run), so the tests can pass a fake runner and no real command runs.

Expected behaviour:

  run_df(path, runner)    runs df with the arguments as a LIST, never through a
                          shell, with a 10 second timeout; returns stdout as a
                          str; raises subprocess.CalledProcessError if df
                          exits with a non-zero code.
  parse_df(text)          parses `df -P -k` output: one header line, then one
                          line per filesystem with six fields
                              Filesystem 1024-blocks Used Available Capacity Mounted-on
                          and returns a list of dicts with keys "mount",
                          "size_gib", "used_gib" (1024-blocks / 1024 / 1024,
                          rounded to 1 decimal) and "use_percent" (int), one
                          per filesystem line, in input order.
  disk_report(paths, threshold, runner)
                          returns the dicts for every filesystem whose
                          use_percent is at least `threshold`, logging one
                          warning per full filesystem.

Sample `df -P -k /var` output:

    Filesystem     1024-blocks     Used Available Capacity Mounted on
    /dev/sda2        102687672 92418904  5009452      95% /var
"""
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


def run_df(path, runner=subprocess.run):
    """Return the stdout of `df -P -k path` as a str."""
    result = runner(f"df -P -k {path}", shell=True, capture_output=True, timeout=10)
    return result.stdout


def parse_df(text):
    """Return one dict per filesystem line of `df -P -k` output."""
    rows = []
    for line in text.splitlines()[2:]:
        fields = line.split()
        if len(fields) < 6:
            continue
        size_kib, used_kib = int(fields[1]), int(fields[2])
        rows.append({
            "mount": fields[5],
            "size_gib": round(size_kib / 1024 / 1024, 1),
            "used_gib": round(used_kib / 1024 / 1024, 1),
            "use_percent": int(fields[4].rstrip("%")),
        })
    return rows


def disk_report(paths, threshold=90, runner=subprocess.run):
    """Return the filesystems at or above `threshold` percent used."""
    full = []
    for path in paths:
        for row in parse_df(run_df(path, runner)):
            if row["use_percent"] >= threshold:
                logger.warning("%s is %d%% full (%.1f of %.1f GiB)",
                               row["mount"], row["use_percent"], row["used_gib"], row["size_gib"])
                full.append(row)
    return full


def main(argv):
    """Exit code 0: all below threshold, 1: something is full, 2: df failed."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    try:
        full = disk_report(argv or ["/"])
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as exc:
        logger.error("df failed: %s", exc)
        return 2
    return 1 if full else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
