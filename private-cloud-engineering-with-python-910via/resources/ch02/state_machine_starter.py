"""VM state machine with an Enum (drill, 5 to 8 minutes).

A virtual machine moves through a fixed set of states. Only some moves are
allowed; any other move is a bug in the caller and must raise.

States (the Enum is given below; its values are the strings an API sends)
    PENDING, PROVISIONING, RUNNING, STOPPED, ERROR, DELETED

Allowed transitions
    PENDING      -> PROVISIONING, DELETED
    PROVISIONING -> RUNNING, ERROR
    RUNNING      -> STOPPED, ERROR
    STOPPED      -> RUNNING, DELETED
    ERROR        -> DELETED
    DELETED      -> (nothing: final state)

IllegalTransition(current, target)
    An exception that stores both states as attributes `current` and
    `target`, and whose message is "illegal transition: running -> pending"
    (the two state values).

VM(name)
    Starts in PENDING. `vm.state` is the current VMState. `vm.history` is a
    list of every state the VM has been in, starting with [VMState.PENDING].

vm.can_transition(target) -> bool
vm.transition(target) -> None
    `target` is a VMState member or its string value ("running").
    An unknown string raises ValueError. A move not in the table raises
    IllegalTransition and leaves state and history unchanged.

Example
    vm = VM("web-1")
    vm.transition("provisioning")
    vm.transition(VMState.RUNNING)
    vm.state                     -> VMState.RUNNING
    vm.transition("pending")     -> raises IllegalTransition
"""
from enum import Enum


class VMState(Enum):
    PENDING = "pending"
    PROVISIONING = "provisioning"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    DELETED = "deleted"


class IllegalTransition(Exception):
    """Raised for a move that the transition table does not allow."""

    def __init__(self, current: VMState, target: VMState) -> None:
        """Store both states and build the message."""
        raise NotImplementedError


class VM:
    """A virtual machine and its lifecycle state."""

    def __init__(self, name: str) -> None:
        """Start in PENDING with history [PENDING]."""
        raise NotImplementedError

    def can_transition(self, target: "VMState | str") -> bool:
        """Return True if moving to target is allowed from the current state."""
        raise NotImplementedError

    def transition(self, target: "VMState | str") -> None:
        """Move to target or raise IllegalTransition."""
        raise NotImplementedError
