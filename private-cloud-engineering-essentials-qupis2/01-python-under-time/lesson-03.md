---
id: l03
title: "Timed problem: reservations and VM placement"
quiz: quiz-03.yaml
resources: [../resources/ch01/merge_reservations_starter.py, ../resources/ch01/merge_reservations_solution.py, ../resources/ch01/merge_reservations_test.py, ../resources/ch01/place_vms_starter.py, ../resources/ch01/place_vms_solution.py, ../resources/ch01/place_vms_test.py]
sources: [8, 12, 14, 155]
---
After this lesson you can merge overlapping reservations, compute peak concurrency with a sweep, and place VMs on hypervisors with first-fit and best-fit, while explaining why request order changes the result.

## Problem A: merge reservations and find the peak (12 minutes)

A reservation is `(start, end)` with `start < end`, half-open: it includes `start` and stops just before `end`. Write `merge_reservations(reservations)`, merging overlapping or touching periods, and `peak_concurrency(reservations)`, the most VMs running at once. Invalid ranges raise `ValueError`; do not modify the input.

**Ask first:** inclusive endpoints? (Decides whether `(1, 5)` and `(5, 8)` overlap.) Unsorted or empty input?

```python
def merge_reservations(reservations):
    _check(reservations)                  # raise ValueError on start >= end
    merged = []
    for start, end in sorted(reservations):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
```

`sorted()` returns a new list, so the caller's input is untouched [12]. The `max` matters: for `[(1, 10), (2, 3)]`, assigning `end` would shrink the period to `(1, 3)`.

```python
def peak_concurrency(reservations):
    events = []
    for start, end in reservations:
        events.append((start, 1))
        events.append((end, -1))
    events.sort()
    running = peak = 0
    for _time, delta in events:
        running += delta
        peak = max(peak, running)
    return peak
```

Tuples compare element by element [12], so `(5, -1)` sorts before `(5, 1)`: an ending VM leaves before a starting one arrives, the half-open rule. Heap version: sort by start, pop every end time at or before the new start, push the new end; the heap size is the number running [8]. Both are O(n log n) [14].

## Problem B: place VMs on hypervisors (18 minutes)

`hosts` maps a name to `(free_cpu, free_ram_gb)`; `vms` is a list of `(name, cpu, ram_gb)`. A VM fits when both resources fit. Write `place_vms(hosts, vms, strategy="first_fit", largest_first=False)` returning `(assignment, unplaced)`. First-fit takes the first host that fits; best-fit the host left with the least CPU (ties: least RAM, then earlier host). `largest_first=True` handles the biggest VMs first.

```python
free = {name: list(cap) for name, cap in hosts.items()}   # own copy
queue = vms
if largest_first:
    queue = sorted(vms, key=lambda vm: (vm[1], vm[2]), reverse=True)
for name, cpu, ram in queue:
    fits = [h for h, (c, r) in free.items() if c >= cpu and r >= ram]
    if not fits:
        continue
    if strategy == "first_fit":
        host = fits[0]
    else:
        host = min(fits, key=lambda h: (free[h][0] - cpu, free[h][1] - ram))
    free[host][0] -= cpu
    free[host][1] -= ram
    assignment[name] = host
```

`reverse=True` keeps the sort stable, so equal VMs stay in arrival order [12]. `min()` returns the first of equal minimums: the "earlier host" tie-break for free.

**Why largest-first helps.** Two hosts with 10 CPUs, requests 4, 4, 6, 6. In arrival order first-fit puts 4 and 4 on host one, a 6 on host two, and the last 6 fits nowhere. Largest-first puts a 6 on each host, then a 4 beside each: all fit.

:::low-confidence
That finding the best possible packing is a hard problem (bin packing is known to be NP-hard) comes from general computer science knowledge, not from this course's sources. Treat first-fit, best-fit and largest-first as heuristics: fast, usually good, not guaranteed optimal. Check an algorithms textbook for the formal statement.
:::

**Complexity.** O(V * H) plus O(V log V) for the sort. Real schedulers also filter hosts, then weigh the survivors, as OpenStack Nova documents [155].

## Gotchas that cost time

- **Inclusive ends, or starts sorted before ends.** Either makes `(1, 5)` and `(5, 8)` concurrent.
- **Mutating the caller's data.** `reservations.sort()` or decrementing `hosts` in place. Use `sorted()` and a copy. [12]
- **Checking only CPU.** RAM must fit too.

## Run it

1. Put the six files in one folder.
2. Edit each starter; run `python merge_reservations_test.py` and `python place_vms_test.py`.
3. At the time box, read the solutions; run `python merge_reservations_test.py merge_reservations_solution` (8 tests) and `python place_vms_test.py place_vms_solution` (12 tests).

:::key-takeaways
- Sort by start, extend the last period with `max(end)`. [12]
- Sweep events `(t, +1)` and `(t, -1)`; plain tuple sort puts ends first at equal times. [12]
- Copy inputs before changing them; `sorted()` already copies. [12]
- First-fit and best-fit are greedy heuristics; largest-first usually packs better. [155]
:::

:::glossary
- **Half-open interval**: a range that includes its start and excludes its end.
- **Sweep line**: processing sorted start and end events in order while keeping a running count.
- **Best-fit**: placing each item on the bin that will be left with the least free space.
:::
