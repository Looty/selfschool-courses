---
id: l07
title: "Exercise: reservations and VM placement"
quiz: quiz-02.yaml
resources: [../resources/ch03/merge_reservations_starter.py, ../resources/ch03/merge_reservations_solution.py, ../resources/ch03/merge_reservations_test.py, ../resources/ch03/place_vms_starter.py, ../resources/ch03/place_vms_solution.py, ../resources/ch03/place_vms_test.py]
sources: [8, 12, 14, 155]
---
After this lesson you can merge overlapping reservations, compute peak concurrency with a sweep or a heap, and place VM requests on hypervisors with first-fit and best-fit, while explaining why the order of the requests changes the result.

## Shortcut

Download the six files for this lesson into one folder, then:

```bash
python merge_reservations_test.py                       # your starter
python merge_reservations_test.py merge_reservations_solution
python place_vms_test.py
python place_vms_test.py place_vms_solution
```

In the course's test run the reference solutions printed `Ran 8 tests` and `OK` (merge) and `Ran 12 tests` and `OK` (placement) on Python 3.13 and 3.11. The untouched starters failed only with `NotImplementedError`.

## Problem A: merge reservations and find the peak (12 minutes)

A reservation is `(start, end)` with `start < end`, half-open: it includes `start` and stops just before `end`. Write `merge_reservations(reservations)`, returning the busy periods with overlapping or touching ones merged, and `peak_concurrency(reservations)`, the most VMs running at one moment. Invalid ranges raise `ValueError`; the input list must not be modified.

**Questions worth asking:** are endpoints inclusive? (Decides whether `(1, 5)` and `(5, 8)` overlap.) Can the input be unsorted? Can it be empty? Are duplicates separate VMs?

**Hints.** Sort by start, then keep the last merged period and either extend its end with `max(...)` or open a new one. For the peak, turn each reservation into two events, `(start, +1)` and `(end, -1)`, sort them and keep a running sum.

### Walkthrough

```python
def merge_reservations(reservations):
    _check(reservations)
    merged = []
    for start, end in sorted(reservations):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
```

`sorted()` returns a new list, so the input is untouched [12]. The `max` matters: for `[(1, 10), (2, 3)]` the second range lies inside the first, and assigning `end` would shrink the busy period to `(1, 3)`.

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

Tuples compare element by element [12], so at the same time `(5, -1)` sorts before `(5, 1)`: an ending VM is counted out before a starting one is counted in, which is exactly the half-open rule. The heap version sorts by start and keeps a min-heap of end times: pop every end time at or before the new start, push the new end, and the heap size is the number running now [8]. `heappush` and `heappop` keep the smallest item at `heap[0]` [8].

**Complexity.** Both are O(n log n) time (the sort dominates; `list.sort()` is O(n log n) [14]) and O(n) space. With small integer times, a difference array gives O(n + T) without sorting.

## Problem B: place VMs on hypervisors (18 minutes)

`hosts` maps a name to `(free_cpu, free_ram_gb)`; `vms` is a list of `(name, cpu, ram_gb)`. A VM fits when both resources fit. Write `place_vms(hosts, vms, strategy="first_fit", largest_first=False)` returning `(assignment, unplaced)`. First-fit takes the first host that fits. Best-fit takes the host that is left with the least CPU after placement (ties: least RAM, then earlier host). `largest_first=True` processes the biggest VMs first (most CPU, then most RAM, then arrival order).

**Questions worth asking:** Do both resources have to fit at once? How are ties between hosts broken? Should the input hosts be changed? What is returned for a VM that fits nowhere?

**Hints.** Copy the free capacities into your own mutable dict. Build the list of hosts that fit, then choose with the strategy. Compute `unplaced` at the end from the input order.

### Walkthrough

```python
free = {name: list(cap) for name, cap in hosts.items()}
queue = vms
if largest_first:
    queue = sorted(vms, key=lambda vm: (vm[1], vm[2]), reverse=True)
for name, cpu, ram in queue:
    fits = [h for h, (c, r) in free.items() if c >= cpu and r >= ram]
    if not fits:
        continue
    host = fits[0] if strategy == "first_fit" else \
        min(fits, key=lambda h: (free[h][0] - cpu, free[h][1] - ram))
    free[host][0] -= cpu
    free[host][1] -= ram
    assignment[name] = host
```

`sorted(..., reverse=True)` keeps equal items in their original order, because `reverse` preserves stability [12]. `min()` returns the first of several equal minimums, which gives the "earlier host" tie-break for free.

**Why largest-first helps.** Take two hosts with 10 CPUs each and requests of 4, 4, 6, 6 CPUs. In arrival order first-fit puts 4 and 4 on the first host, one 6 on the second, and the last 6 fits nowhere. Largest-first places each 6 on its own host, then each 4 beside one: all four fit. Big items are the hardest to place; putting them in while the hosts are empty leaves small items to fill the gaps.

:::low-confidence
That finding the best possible packing is a hard problem (bin packing is known to be NP-hard) comes from general computer science knowledge, not from this course's sources. Treat first-fit, best-fit and largest-first as heuristics: fast, usually good, not guaranteed optimal. Check an algorithms textbook for the formal statement.
:::

**Complexity.** V requests, H hosts: O(V * H) for the placement loop plus O(V log V) for the sort. A real scheduler works in two phases, filter the hosts that can take the VM, then weigh the survivors; OpenStack Nova's scheduler documents exactly that order [155]. `first_fit` and `best_fit` here are a tiny version of filter then choose.

## Gotchas

- **Inclusive end times.** Treating `end` as occupied makes touching reservations overlap and inflates the peak. Agree the interval convention first.
- **Shrinking a merged period.** Assigning `end` instead of `max(prev_end, end)` breaks nested reservations.
- **Ordering events wrongly at equal times.** If starts sort before ends at the same instant, `(1, 5)` and `(5, 8)` count as two concurrent VMs.
- **Mutating the caller's data.** `reservations.sort()` or decrementing the `hosts` dict in place changes the caller's input. `sorted()` and a copied dict avoid it. [12]
- **Checking only one resource.** A VM that fits CPU-wise on a host with no RAM must not be placed there.
- **Expecting optimal answers.** Greedy placement can miss a perfect packing; say so out loud and offer the heuristic's limits.

## Follow-up variation

Reservations now carry a CPU count, and the question is the peak CPU in use. The sweep becomes `(start, +cpu)` and `(end, -cpu)`; the heap approach changes more, because the heap size no longer equals the load, so you keep a running total beside it. Discuss which version you would rather type under time pressure (the sweep) and why.

:::key-takeaways
- Sort by start, extend the last period with `max(end)`; sort events so ends come before starts at equal times.
- `sorted()` copies, so the caller's list is untouched; `reverse=True` keeps stability. [12]
- A min-heap of end times gives the running count too. [8]
- First-fit and best-fit are heuristics; largest-first usually packs better because big items are placed while space is plentiful.
- Real schedulers filter hosts, then weigh the remaining ones. [155]
:::

:::glossary
- **Half-open interval**: a range that includes its start and excludes its end.
- **Sweep line**: processing sorted start and end events in order while keeping a running count.
- **Peak concurrency**: the largest number of reservations active at the same moment.
- **Hypervisor**: a host that runs virtual machines and has a fixed amount of CPU and RAM to give them.
- **First-fit**: placing each item on the first bin where it fits.
- **Best-fit**: placing each item on the bin that will be left with the least free space.
- **Bin packing**: the problem of fitting items into as few fixed-size bins as possible.
:::
