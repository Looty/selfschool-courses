---
id: l04
title: "Classes, dataclasses and exceptions"
quiz: quiz-04.yaml
resources: [../resources/ch02/inventory_starter.py, ../resources/ch02/inventory_solution.py, ../resources/ch02/inventory_test.py, ../resources/ch02/state_machine_starter.py, ../resources/ch02/state_machine_solution.py, ../resources/ch02/state_machine_test.py, ../resources/ch02/timer_context_starter.py, ../resources/ch02/timer_context_solution.py, ../resources/ch02/timer_context_test.py]
sources: [11, 12, 19, 20, 21, 22, 32, 33, 41]
---
After this lesson you can write a class with the special methods a timed problem usually needs, replace boilerplate with a `dataclass` or an `Enum`, and use `try`, `with` and custom exceptions correctly.

## Class basics

`__init__` runs when the class is called and must return `None`. [21] `x.f()` is the same as `Class.f(x)`; `self` is only a convention. [20] Instance variables belong to one object; a mutable class variable such as `tricks = []` is shared by all instances, so create such lists in `__init__`. [20]

```python
class Host:
    def __init__(self, name, cpus):
        self.name, self.cpus = name, cpus
    def __repr__(self):
        return f"Host({self.name!r}, {self.cpus})"
```

`__repr__` is the unambiguous debugging string, ideally valid Python; if `__str__` is missing, `__repr__` is used for `str()` and `print()` too. [21] Put the useful information there.

## Equality, hashing and ordering

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, major, minor): self.t = (major, minor)
    def __eq__(self, other):
        return self.t == other.t if isinstance(other, Version) else NotImplemented
    def __lt__(self, other):
        return self.t < other.t if isinstance(other, Version) else NotImplemented
    def __hash__(self): return hash(self.t)
```

A class that defines `__eq__` and not `__hash__` gets `__hash__ = None`, so its instances cannot go in a set or be dict keys. [21] Equal objects must have equal hashes; hash a tuple of the fields used in `__eq__`. [21] `total_ordering` derives the other comparisons from `__eq__` and one of `__lt__`, `__le__`, `__gt__`, `__ge__`, at some cost in speed. [11] Sorting itself only needs `__lt__`. [12]

## Iteration and context managers

A class with `__iter__` returning an iterator works in `for` loops; `__next__` raises `StopIteration` to end. [20] Often `__iter__` is simply a generator: `def __iter__(self): yield from self.items`. For `with`, define `__enter__` (its return value is bound by `as`) and `__exit__(exc_type, exc, tb)`; returning a true value suppresses the exception, so normally return `False` or `None`. [21]

```python
from contextlib import contextmanager

@contextmanager
def timed(record, key, clock):
    start = clock()
    try:
        yield
    finally:
        record[key] = clock() - start
```

`@contextmanager` turns a generator with exactly one `yield` into a context manager; an exception from the block is re-raised at the `yield`, so use `try`/`finally`, and re-raise anything you catch only to log. [41] Such managers are single use. [41]

## Dataclasses and Enum

```python
from dataclasses import dataclass, field

@dataclass(order=True, frozen=True)
class Job:
    priority: int
    name: str = field(compare=False)
    tags: tuple = ()
```

`@dataclass` generates `__init__`, `__repr__` and `__eq__`; `order=True` adds comparisons on the fields as a tuple; `frozen=True` makes assignment raise `FrozenInstanceError` and, with `eq=True`, generates `__hash__`. [32] With the default `eq=True, frozen=False`, `__hash__` is `None`. [32] A field without a default after one with a default raises `TypeError`, and a mutable default such as `[]` raises `ValueError`; write `field(default_factory=list)`. [32] `field(compare=False)` leaves a field out of equality and ordering. [32]

```python
from enum import Enum
class State(Enum):
    RUNNING = "running"
State("running"), State["RUNNING"], State.RUNNING.value
```

Call syntax looks a member up by value, index syntax by name. [33] In the course's test run `State("x")` raised `ValueError: 'x' is not a valid State`.

## Exceptions

```python
def divide(x, y):
    try:
        result = x / y
    except ZeroDivisionError:
        return None
    else:
        return result          # runs only if nothing was raised
    finally:
        print("always")        # runs before the return completes
```

At most one handler runs and the first matching `except` wins, so put subclasses before their base classes. [19] `else` holds code that should not be protected by the `try`. [19] `finally` runs whether or not an exception occurred, and a `return` inside `finally` overrides the earlier result and discards the exception; Python 3.14 warns about it. [19] [22] A bare `raise` in an `except` block re-raises the current exception; `raise New(...) from err` records a cause and `from None` hides the context. [19] Custom exceptions derive from `Exception` and end in `Error`. [19] Catch several types with a tuple: `except (KeyError, ValueError) as err:`.

:::low-confidence
The tutorial page read prints `except A, B:` without brackets, which is valid from Python 3.14 only. [19] [22] This course writes the bracketed tuple form, which the pages read do not show; the course's code ran on Python 3.11 and 3.13. Check the language reference before relying on the unbracketed form, and avoid it on 3.11.
:::

## Drills

Edit the starter, run `python name_test.py`, and add `name_solution` to test the reference. In the course's test run every solution passed on Python 3.13 and 3.11 and every starter failed with `NotImplementedError`.

1. **`inventory`** (8 minutes, 12 tests). A host inventory with `add_host`, `allocate`, `release`, `free`, `len`, `in` and a `repr`, with `UnknownHostError` and `CapacityError` under `InventoryError`. Hint: validate arguments first, then look up the host, then change state. Walkthrough: a dict of small `Host` dataclasses; `raise UnknownHostError(name) from None` hides the internal `KeyError`. Mistake: changing `used` before the capacity check.
2. **`state_machine`** (8 minutes, 12 tests). An `Enum` of VM states with a table of allowed moves and an `IllegalTransition` exception. Hint: store the table as data, `dict[state, frozenset[state]]`. Walkthrough: `VMState(target)` converts both members and strings and raises `ValueError` for unknown strings; check membership; append to `history` only after success. Mistake: an `if`/`elif` chain per state.
3. **`timer_context`** (7 minutes, 11 tests). A `Timer` class and a `@contextmanager` function sharing an injectable clock. Hint: the default is `time.monotonic`, not `time.monotonic()`. Walkthrough: `__exit__` stores the elapsed time and returns `False`; the generator uses `try`/`finally`. Mistake: returning `True` from `__exit__`, which swallows errors.

## Gotchas

- **Mutable default argument.** `def add_tag(tag, tags=[])` shares one list across calls: in the course's test run `add_tag("a")` then `add_tag("b")` printed `['a', 'b']` for both. Use `tags=None` and create the list inside.
- **`__eq__` without `__hash__`.** The class becomes unhashable. [21]
- **Mutable dataclass default.** `x: list = []` raises `ValueError`. [32]
- **Shared class variable.** A list defined in the class body is shared by every instance. [20]
- **`__exit__` returning a truthy value.** It suppresses the exception. [21]
- **`except Exception` too early.** The first matching handler wins, so specific ones must come first. [19]

:::low-confidence
The explanation that a default argument is evaluated once, at function definition, is standard Python behaviour but is not in the documentation pages read for this course. The behaviour itself was observed in the course's test run.
:::

:::key-takeaways
- Define `__repr__` always; define `__hash__` whenever you define `__eq__` and want set or dict use. [21]
- `dataclass` removes boilerplate; use `default_factory` for lists and dicts. [32]
- `Enum(value)` looks up by value and raises `ValueError` if unknown. [33]
- `try`/`except`/`else`/`finally`: `else` only on success, `finally` always. [19]
- A context manager's `__exit__` should return a falsy value unless it means to swallow the error. [21]
:::

:::glossary
- **Special method**: a method with double underscores, such as `__repr__`, that Python calls for built-in syntax.
- **Dataclass**: a class whose boilerplate methods are generated from its annotated fields.
- **Enum**: a fixed set of named constants.
- **Context manager**: an object that sets something up and cleans it up around a `with` block.
- **Custom exception**: your own error class, usually a subclass of `Exception`.
- **Frozen**: not allowed to change after creation.
- **Injectable clock**: a time function passed in as an argument so tests can replace it.
:::
