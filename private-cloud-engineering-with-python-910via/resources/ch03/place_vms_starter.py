"""Exercise: VM placement (time box: 18 minutes).

A scheduler must place VM requests on hypervisors.

    hosts  dict: host name -> (free_cpu, free_ram_gb). The dict's order is the
           host order.
    vms    list of (vm_name, cpu, ram_gb) in the order the requests arrived.
           VM names are unique. All numbers are non-negative integers.

A VM fits on a host when the host has at least that much free CPU AND at least
that much free RAM. Placing a VM reduces the host's free CPU and RAM.

Write place_vms(hosts, vms, strategy="first_fit", largest_first=False) that
returns a pair (assignment, unplaced):

    assignment  dict: vm_name -> host name, for every VM that was placed
    unplaced    list of vm_names that fit on no host, in the order they
                appear in `vms`

Strategies, applied to one VM at a time:

    "first_fit"  the first host, in host order, on which the VM fits
    "best_fit"   among the hosts on which the VM fits, the one left with the
                 least free CPU after the placement; ties go to the least free
                 RAM after the placement, then to the earlier host

With largest_first=True, process the VMs from largest to smallest: most CPU
first, ties by most RAM, remaining ties in arrival order. Otherwise process
them in arrival order.

Raise ValueError for an unknown strategy. Do not modify `hosts` or `vms`.

Examples:

    hosts = {"hv1": (8, 32), "hv2": (4, 16)}
    vms = [("a", 4, 16), ("b", 8, 32)]
    place_vms(hosts, vms, "first_fit") == ({"a": "hv1"}, ["b"])
    place_vms(hosts, vms, "best_fit")  == ({"a": "hv2", "b": "hv1"}, [])

    hosts = {"hv1": (10, 64), "hv2": (10, 64)}
    vms = [("s1", 4, 8), ("s2", 4, 8), ("b1", 6, 8), ("b2", 6, 8)]
    place_vms(hosts, vms) == ({"s1": "hv1", "s2": "hv1", "b1": "hv2"}, ["b2"])
    place_vms(hosts, vms, largest_first=True) == (
        {"b1": "hv1", "b2": "hv2", "s1": "hv1", "s2": "hv2"}, [])

Check your work:  python place_vms_test.py
"""


def place_vms(hosts, vms, strategy="first_fit", largest_first=False):
    """Return (assignment, unplaced) for the given placement strategy."""
    raise NotImplementedError
