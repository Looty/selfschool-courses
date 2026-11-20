"""Reference solution for the VM placement exercise (see place_vms_starter.py)."""

STRATEGIES = ("first_fit", "best_fit")


def place_vms(hosts, vms, strategy="first_fit", largest_first=False):
    """Return (assignment, unplaced) for the given placement strategy."""
    if strategy not in STRATEGIES:
        raise ValueError(f"unknown strategy {strategy!r}; expected one of {STRATEGIES}")

    free = {name: list(capacity) for name, capacity in hosts.items()}   # our own mutable copy
    queue = vms
    if largest_first:
        # sorted() is stable, also with reverse=True, so equal sizes keep arrival order.
        queue = sorted(vms, key=lambda vm: (vm[1], vm[2]), reverse=True)

    assignment = {}
    for name, cpu, ram in queue:
        fits = [host for host, (free_cpu, free_ram) in free.items()
                if free_cpu >= cpu and free_ram >= ram]
        if not fits:
            continue
        if strategy == "first_fit":
            host = fits[0]
        else:
            # min() returns the first of several equal minimums, which is the earlier host.
            host = min(fits, key=lambda h: (free[h][0] - cpu, free[h][1] - ram))
        free[host][0] -= cpu
        free[host][1] -= ram
        assignment[name] = host

    unplaced = [name for name, _cpu, _ram in vms if name not in assignment]
    return assignment, unplaced


# Complexity for V requests and H hosts: O(V * H) time for the placement loop, plus
# O(V log V) when largest_first sorts the requests; O(V + H) extra space.
# Alternative: when only one resource matters, keep the hosts' free capacity in a sorted
# list and use bisect to find the tightest fit in O(log H) per request instead of O(H).
