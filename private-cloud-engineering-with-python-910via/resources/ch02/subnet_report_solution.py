"""Reference solution for subnet_report (see subnet_report_starter.py)."""
import ipaddress
from itertools import islice


def subnet_report(cidr: str, used: list[str], n: int) -> dict:
    """Return usage figures and the first n free host addresses of cidr."""
    net = ipaddress.IPv4Network(cidr, strict=False)
    if net.prefixlen < net.max_prefixlen - 1:
        total = net.num_addresses - 2
        reserved = {net.network_address, net.broadcast_address}
    else:
        total = net.num_addresses
        reserved = set()

    taken = set()
    for text in used:
        addr = ipaddress.IPv4Address(text)
        if addr not in net:
            raise ValueError(f"{addr} is outside {net}")
        if addr in reserved:
            raise ValueError(f"{addr} is not a usable host of {net}")
        taken.add(addr)

    free_hosts = (host for host in net.hosts() if host not in taken)
    return {
        "network": str(net),
        "total": total,
        "used": len(taken),
        "free": total - len(taken),
        "first_free": [str(host) for host in islice(free_hosts, n)],
    }

# Complexity: O(u) to check u used addresses, plus O(n + u) to find the
# first n free ones, because hosts() is a lazy iterator and islice stops
# early. Space O(u). Nothing builds the full host list, which for a /16
# would be 65534 objects.
# IPv4Network and IPv4Address raise AddressValueError or NetmaskValueError,
# both subclasses of ValueError, so invalid input needs no extra code.
# strict=False masks the host bits off "10.20.0.5/29"; the default
# strict=True would raise ValueError instead.
# Alternative: compute total as len(list(net.hosts())). Simpler to type but
# O(2**(32 - prefix)) time and memory.
