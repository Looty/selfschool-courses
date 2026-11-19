"""Fleet tasks for the hypervisor-management hosts, written with Fabric.

    fab --list
    fab status                               # every host in HOSTS, in parallel
    fab status --targets hvm01,hvm02
    fab rolling-restart                      # vmapi, one host at a time
    fab rolling-restart --service libvirtd --port 16509 --targets hvm03

Needs Fabric 2 or newer (pip install fabric) and SSH access to the hosts. The
host names must resolve through DNS or ~/.ssh/config.

rolling-restart calls sudo on the remote host. Either let the login user run
systemctl without a password, or start fab with --prompt-for-sudo-password.

The tasks build their own groups from --targets, so run them WITHOUT fab's -H
option: with -H, fab would call the task once per host and each call would walk
the whole group again.
"""
import time

from fabric import SerialGroup, ThreadingGroup, task
from fabric.exceptions import GroupException
from invoke import Exit

# Same names as inventory.ini, so both tools talk about the same fleet.
HOSTS = ("hvm01", "hvm02", "hvm03", "hvm04")

# LC_ALL=C keeps the number format the same on every host.
STATUS_COMMAND = "export LC_ALL=C; uptime && df -Pk /"
HEADERS = ("HOST", "UP", "LOAD1", "FREE /")


def host_list(targets):
    """Return the hosts named in a comma-separated string, or HOSTS if it is empty."""
    names = [name.strip() for name in targets.split(",") if name.strip()]
    return names or list(HOSTS)


def parse_status(stdout):
    """Turn the output of STATUS_COMMAND into (uptime, one-minute load, free GiB)."""
    lines = [line for line in stdout.splitlines() if line.strip()]
    uptime_line, df_line = lines[0], lines[-1]
    # " 13:52:01 up 12 days,  3:04,  2 users,  load average: 0.08, 0.03, 0.01"
    head, _, loads = uptime_line.partition("load average:")
    since_boot = head.split(" up ", 1)[1]
    parts = [part.strip() for part in since_boot.split(",")]
    up = ", ".join(part for part in parts if part and "user" not in part)
    load_1m = float(loads.split(",")[0])
    # "/dev/vda1  41151808  10616832  28413952  28% /"  (sizes in KiB)
    free_gib = int(df_line.split()[3]) / 1024 ** 2
    return up, load_1m, free_gib


def status_row(host, outcome):
    """Build one table row from a Result, or from the exception a host raised."""
    if isinstance(outcome, BaseException):
        return (host, f"ERROR {type(outcome).__name__}: {outcome}", "-", "-")
    if outcome is None or outcome.failed:
        code = "?" if outcome is None else outcome.exited
        return (host, f"ERROR command exited {code}", "-", "-")
    up, load_1m, free_gib = parse_status(outcome.stdout)
    return (host, up, f"{load_1m:.2f}", f"{free_gib:.1f}G")


def format_table(headers, rows):
    """Left-align every column to its widest cell."""
    table = [list(headers)] + [[str(cell) for cell in row] for row in rows]
    widths = [max(len(row[i]) for row in table) for i in range(len(headers))]
    return "\n".join(
        "  ".join(cell.ljust(width) for cell, width in zip(row, widths)).rstrip()
        for row in table
    )


def wait_healthy(conn, port, tries, delay):
    """Poll the health endpoint from the host itself; True as soon as it answers."""
    check = f"curl -fsS -o /dev/null http://127.0.0.1:{port}/healthz"
    for attempt in range(1, tries + 1):
        if conn.run(check, hide=True, warn=True).ok:
            return True
        if attempt < tries:
            time.sleep(delay)
    return False


@task(help={"targets": "comma-separated hosts (default: the HOSTS tuple)"})
def status(c, targets=""):
    """Print uptime, load and free disk for every host, gathered in parallel."""
    with ThreadingGroup(*host_list(targets), config=c.config, connect_timeout=10) as group:
        try:
            # warn=True: a non-zero exit comes back as a Result instead of raising.
            results = group.run(STATUS_COMMAND, hide=True, warn=True)
        except GroupException as exc:
            # At least one host raised (unreachable, authentication failed).
            # exc.result still maps every Connection to a Result or an exception.
            results = exc.result
        rows = [status_row(conn.host, results.get(conn)) for conn in group]
    print(format_table(HEADERS, rows))


@task(
    help={
        "service": "systemd unit to restart",
        "targets": "comma-separated hosts (default: the HOSTS tuple)",
        "port": "local port that serves /healthz",
        "tries": "health checks per host before giving up",
        "delay": "seconds between health checks",
    }
)
def rolling_restart(c, service="vmapi", targets="", port=8080, tries=10, delay=3):
    """Restart a service one host at a time; stop at the first unhealthy host."""
    done = []
    with SerialGroup(*host_list(targets), config=c.config, connect_timeout=10) as group:
        for conn in group:
            print(f"{conn.host}: restarting {service}")
            conn.sudo(f"systemctl restart {service}", hide=True)
            if not wait_healthy(conn, port, tries, delay):
                raise Exit(
                    f"{conn.host}: {service} is not healthy after the restart. "
                    f"Stopped. Hosts already restarted: {', '.join(done) or 'none'}",
                    code=1,
                )
            print(f"{conn.host}: healthy")
            done.append(conn.host)
    print(f"restarted {service} on {len(done)} host(s)")
