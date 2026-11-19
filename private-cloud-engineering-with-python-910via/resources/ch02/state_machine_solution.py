"""Reference solution for state_machine (see state_machine_starter.py)."""
from enum import Enum


class VMState(Enum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DELETED = "deleted"


ALLOWED: dict[VMState, frozenset[VMState]] = {
    VMState.PENDING: frozenset({VMState.PROVISIONING, VMState.DELETED}),
    VMState.PROVISIONING: frozenset({VMState.RUNNING, VMState.ERROR}),
    VMState.RUNNING: frozenset({VMState.STOPPED, VMState.ERROR}),
    VMState.STOPPED: frozenset({VMState.RUNNING, VMState.DELETED}),
    VMState.ERROR: frozenset({VMState.DELETED}),
    VMState.DELETED: frozenset(),
}


class IllegalTransition(Exception):
    """Raised for a move that the transition table does not allow."""

    def __init__(self, current: VMState, target: VMState) -> None:
        super().__init__(f"illegal transition: {current.value} -> {target.value}")
        self.current = current
        self.target = target


class VM:
    """A virtual machine and its lifecycle state."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.state = VMState.PENDING
        self.history = [VMState.PENDING]

    def can_transition(self, target: "VMState | str") -> bool:
        return VMState(target) in ALLOWED[self.state]

    def transition(self, target: "VMState | str") -> None:
        target = VMState(target)
        if target not in ALLOWED[self.state]:
            raise IllegalTransition(self.state, target)
        self.state = target
        self.history.append(target)

    def __repr__(self) -> str:
        return f"VM({self.name!r}, state={self.state.value})"

# Complexity: O(1) per transition (a dict lookup and a set membership test).
# VMState(x) does both conversions: given a member it returns that member,
# given a value string it looks the member up, and an unknown value raises
# ValueError. That is why no isinstance check is needed.
# The table is data, not a chain of if/elif: adding a state is one line, and
# the table can be printed or tested on its own.
# Alternative: put the allowed set on each member (a method on VMState that
# returns ALLOWED[self]), so callers can ask VMState.RUNNING.can_go(...).
