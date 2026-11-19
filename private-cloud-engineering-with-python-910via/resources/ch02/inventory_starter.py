"""Host inventory with capacity (drill, 5 to 8 minutes).

Write a small class that tracks hypervisor hosts and how many vCPUs are
allocated on each. Bad input must fail loudly with the right exception.

Exceptions (already defined below, use them as they are)
    InventoryError       base class for inventory problems
    UnknownHostError     the host name is not in the inventory
    CapacityError        not enough free vCPUs on the host

Inventory()
    Starts empty.

add_host(name, capacity)
    Register a host with `capacity` vCPUs, all free.
    - ValueError if name is empty or capacity < 1.
    - InventoryError if a host with that name already exists.

allocate(name, amount) -> int
    Allocate `amount` vCPUs on the host and return the free vCPUs left.
    - ValueError if amount < 1 (check this first).
    - UnknownHostError if the host does not exist.
    - CapacityError if amount is more than the free vCPUs; nothing changes.

release(name, amount) -> int
    Give back `amount` vCPUs and return the free vCPUs afterwards.
    - ValueError if amount < 1 or amount is more than what is allocated.
    - UnknownHostError if the host does not exist.

free(name) -> int
    Free vCPUs on the host. UnknownHostError if it does not exist.

len(inventory) is the number of hosts; `name in inventory` tests membership.
repr(inventory) is "Inventory(hosts=N, used=U/C)" where U is the total
allocated and C the total capacity, for example "Inventory(hosts=2, used=3/48)".

Example
    inv = Inventory()
    inv.add_host("kvm-01", 16)
    inv.allocate("kvm-01", 4)    -> 12
    inv.allocate("kvm-01", 20)   -> raises CapacityError
    inv.release("kvm-01", 4)     -> 16
    "kvm-01" in inv              -> True
"""


class InventoryError(Exception):
    """Base class for inventory errors."""


class UnknownHostError(InventoryError):
    """The host is not in the inventory."""


class CapacityError(InventoryError):
    """The host does not have enough free capacity."""


class Inventory:
    """Hosts and their allocated vCPUs."""

    def __init__(self) -> None:
        """Start with no hosts."""
        raise NotImplementedError

    def add_host(self, name: str, capacity: int) -> None:
        """Register a host with `capacity` free vCPUs."""
        raise NotImplementedError

    def allocate(self, name: str, amount: int) -> int:
        """Allocate vCPUs on a host; return the free vCPUs left."""
        raise NotImplementedError

    def release(self, name: str, amount: int) -> int:
        """Release vCPUs on a host; return the free vCPUs afterwards."""
        raise NotImplementedError

    def free(self, name: str) -> int:
        """Return the free vCPUs on a host."""
        raise NotImplementedError

    def __len__(self) -> int:
        """Return the number of hosts."""
        raise NotImplementedError

    def __contains__(self, name: object) -> bool:
        """Return True if a host with this name exists."""
        raise NotImplementedError

    def __repr__(self) -> str:
        """Return 'Inventory(hosts=N, used=U/C)'."""
        raise NotImplementedError
