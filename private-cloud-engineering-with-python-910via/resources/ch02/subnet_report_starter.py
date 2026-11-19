"""Subnet usage report with ipaddress (drill, 5 to 8 minutes).

A VM network has a CIDR block and a list of addresses already handed out.
Report how many host addresses are free and which ones to hand out next.

Input
    cidr: an IPv4 network such as "10.20.0.0/29". Host bits may be set
          ("10.20.0.5/29" means the network 10.20.0.0/29).
    used: a list of IPv4 address strings already in use. Duplicates may occur
          and count once.
    n:    how many free addresses to list (n >= 0).

Usable hosts are the addresses that ipaddress's hosts() returns: for a
prefix of /30 or shorter, every address except the network and broadcast
address; for /31 both addresses; for /32 the single address.

Output, a dict
    "network":    the network in prefix form, e.g. "10.20.0.0/29"
    "total":      number of usable hosts
    "used":       number of distinct used addresses
    "free":       total - used
    "first_free": the n lowest free usable addresses, as strings, ascending

Errors
    Raise ValueError for an invalid CIDR or address, for a used address that
    is outside the network, and for a used address that is not a usable host
    (the network or broadcast address of a /30 or larger network).

Constraints
    Prefix length between /16 and /32.

Example 1
    subnet_report("10.20.0.0/29", ["10.20.0.1", "10.20.0.3"], 3)
    -> {"network": "10.20.0.0/29", "total": 6, "used": 2, "free": 4,
        "first_free": ["10.20.0.2", "10.20.0.4", "10.20.0.5"]}

Example 2 (host bits set, nothing used)
    subnet_report("192.168.1.77/30", [], 5)
    -> {"network": "192.168.1.76/30", "total": 2, "used": 0, "free": 2,
        "first_free": ["192.168.1.77", "192.168.1.78"]}

Example 3
    subnet_report("10.0.0.0/29", ["10.0.1.1"], 1)  -> raises ValueError
"""


def subnet_report(cidr: str, used: list[str], n: int) -> dict:
    """Return usage figures and the first n free host addresses of cidr."""
    raise NotImplementedError
