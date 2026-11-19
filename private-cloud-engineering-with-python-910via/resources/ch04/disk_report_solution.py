"""Reference solution for the disk report fix-the-bug exercise (see disk_report_broken.py).

The four bugs and their fixes:
  1. run_df built a shell command with an f-string and shell=True, so a path such as
     "/tmp; rm -rf ~" would run a second command. Fix: pass a list, no shell.
  2. run_df ignored the exit code, so a failed df looked like "no filesystems".
     Fix: check=True, which raises CalledProcessError on a non-zero exit.
  3. Captured output is bytes unless text mode is on; parse_df then failed on
     bytes.rstrip("%"). Fix: text=True.
  4. parse_df skipped two lines ([2:]) instead of the one header line, so the
     first filesystem, usually the only one for a single path, was never checked.
     Fix: [1:].
"""
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)


def run_df(path, runner=subprocess.run):
    """Return the stdout of `df -P -k path` as a str."""
    result = runner(["df", "-P", "-k", path],                  # fix 1: a list, no shell
                    capture_output=True, text=True,              # fix 3: str, not bytes
                    check=True, timeout=10)                      # fix 2: raise on failure
    return result.stdout


def parse_df(text):
    """Return one dict per filesystem line of `df -P -k` output."""
    rows = []
    for line in text.splitlines()[1:]:                           # fix 4: skip ONE header line
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


# Complexity: parse_df is O(L) for L lines of output; disk_report runs one df per path.
# Alternative: os.statvfs() or shutil.disk_usage() reads the same numbers without starting a
# process or parsing text, which removes bugs 1 to 4 at once (not covered by this course's notes).
