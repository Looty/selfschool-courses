"""Reference solution for inventory (see inventory_starter.py)."""
from dataclasses import dataclass


class InventoryError(Exception):
    """Base class for inventory errors."""


class UnknownHostError(InventoryError):
    """The host is not in the inventory."""


class CapacityError(InventoryError):
    """The host does not have enough free capacity."""


@dataclass
class Host:
    name: str
    capacity: int
    used: int = 0


class Inventory:
    """Hosts and their allocated vCPUs."""

    def __init__(self) -> None:
        self._hosts: dict[str, Host] = {}

    def _get(self, name: str) -> Host:
        try:
            return self._hosts[name]
        except KeyError:
            raise UnknownHostError(name) from None

    def add_host(self, name: str, capacity: int) -> None:
        if not name:
            raise ValueError("host name must not be empty")
        if capacity < 1:
            raise ValueError(f"capacity must be at least 1, got {capacity}")
        if name in self._hosts:
            raise InventoryError(f"host {name} already exists")
        self._hosts[name] = Host(name, capacity)

    def allocate(self, name: str, amount: int) -> int:
        if amount < 1:
            raise ValueError(f"amount must be at least 1, got {amount}")
        host = self._get(name)
        free = host.capacity - host.used
        if amount > free:
            raise CapacityError(f"{name}: asked for {amount}, only {free} free")
        host.used += amount
        return host.capacity - host.used

    def release(self, name: str, amount: int) -> int:
        host = self._get(name)
        if amount < 1 or amount > host.used:
            raise ValueError(f"{name}: cannot release {amount}, {host.used} allocated")
        host.used -= amount
        return host.capacity - host.used

    def free(self, name: str) -> int:
        host = self._get(name)
        return host.capacity - host.used

    def __len__(self) -> int:
        return len(self._hosts)

    def __contains__(self, name: object) -> bool:
        return name in self._hosts

    def __repr__(self) -> str:
        used = sum(host.used for host in self._hosts.values())
        capacity = sum(host.capacity for host in self._hosts.values())
        return f"Inventory(hosts={len(self)}, used={used}/{capacity})"

# Complexity: every method is O(1) on average (one dict lookup), except
# __repr__, which is O(h) for h hosts.
# `raise UnknownHostError(name) from None` hides the internal KeyError from
# the traceback; `from err` would keep it as the cause.
# Order of checks matters for the tests: validate the cheap arguments first,
# then look up the host, and change state only after every check passed.
# Alternative: store two dicts (capacity and used) instead of a Host
# dataclass. Shorter to type, but easier to update one and forget the other.
