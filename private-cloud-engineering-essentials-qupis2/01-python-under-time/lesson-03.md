---
id: l03
title: "Timed problem: reservations and VM placement"
quiz: quiz-03.yaml
resources: [../resources/ch01/merge_reservations_starter.py, ../resources/ch01/merge_reservations_solution.py, ../resources/ch01/merge_reservations_test.py, ../resources/ch01/place_vms_starter.py, ../resources/ch01/place_vms_solution.py, ../resources/ch01/place_vms_test.py]
sources: [12, 155]
---
Three moves: merge sorted intervals, sweep events for the peak, place VMs greedily.

## The problems (30 minutes)

**A (12 minutes).** A reservation `(start, end)` is half-open: it includes `start` and stops just before `end`. Write `merge_reservations`, joining overlapping or touching periods, and `peak_concurrency`, the most VMs running at once. Do not modify the input.

**B (18 minutes).** `hosts` maps a name to `(free_cpu, free_ram_gb)`; `vms` lists `(name, cpu, ram_gb)`. Write `place_vms(hosts, vms, strategy="first_fit", largest_first=False)` returning `(assignment, unplaced)`. Full statements: the starters.

**Ask first:** inclusive ends? Empty input? Tie-breaks?

## Merging intervals: sort, then extend the last one

**Rule:** sort by start; if the next interval starts at or before the last merged end, stretch that end with `max`, otherwise start a new one.

```python
merged = []
for start, end in sorted(reservations):    # sorted() copies; input untouched [12]
    if merged and start <= merged[-1][1]:
        merged[-1] = (merged[-1][0], max(merged[-1][1], end))
    else:
        merged.append((start, end))
```

| Input | `merged` step by step | Result |
| --- | --- | --- |
| `[]` | | `[]` |
| `[(1, 3), (2, 4)]` | `(1, 3)` → `(1, 4)` | `[(1, 4)]` |
| `[(1, 5), (5, 8)]` | `(1, 5)` → `(1, 8)`: touching joins | `[(1, 8)]` |
| `[(1, 10), (2, 3)]` | `max(10, 3)` keeps 10; `end` alone gives `(1, 3)` | `[(1, 10)]` |
| `[(6, 8), (1, 4)]` | sorted first: `(1, 4)`, then `(6, 8)` | `[(1, 4), (6, 8)]` |

**P1.** What does merging `[(3, 4), (1, 2), (2, 3)]` give?

## Peak overlap: a sweep over events

**Rule:** turn each interval into two events, `(start, +1)` and `(end, -1)`, sort them, and keep a running count; the peak is the largest running count.

Prerequisite: tuples compare left to right, so at the same time `(5, -1)` sorts before `(5, 1)` [12]. `[(1, 5), (2, 6)]` becomes `[(1, 1), (2, 1), (5, -1), (6, -1)]`:

| Reservations | Running count | Peak |
| --- | --- | --- |
| `[]` | | 0 |
| `[(1, 5), (2, 6)]` | 1, 2, 1, 0 | 2 |
| `[(1, 4), (2, 5), (3, 6)]` | 1, 2, 3, 2, 1, 0 | 3 |
| `[(1, 5), (5, 8)]` | 1, 0, 1, 0: the end at 5 goes first | 1 |

**Contrast:** merge and peak on the same `[(1, 5), (5, 8)]`.

| Question | Rule at time 5 | Answer |
| --- | --- | --- |
| merge | `5 <= 5`: touching joins | `[(1, 8)]` |
| peak with plain `sort()` | end before start | 1 |
| peak sorted by `(t, -delta)` | start before end | 2: wrong for half-open |

**P2.** What is the peak for `[(1, 3), (2, 4), (3, 5)]`?

## Placing VMs: greedy, largest first

**Rule:** for each VM, list the hosts with enough free CPU and RAM; first-fit takes the first, best-fit the one left with the least CPU; largest-first sorts the VMs biggest first before the loop.

```python
fits = [h for h, (c, r) in free.items() if c >= cpu and r >= ram]   # free: a copy
host = fits[0]                                                          # first-fit
host = min(fits, key=lambda h: (free[h][0] - cpu, free[h][1] - ram))   # best-fit
```

`min` picks the first of equal minimums, the earlier host. `reverse=True` stays stable [12].

Two hosts with 10 CPUs, RAM plentiful:

| Order of CPU requests | hv1 | hv2 | Unplaced |
| --- | --- | --- | --- |
| arrival: 4, 4, 6, 6 | 4 + 4 | 6 | one 6 |
| largest first: 6, 6, 4, 4 | 6 + 4 | 6 + 4 | none |

Edge: a VM whose CPU or RAM fits nowhere is unplaced.

**Contrast:** hosts hv1 with 8 free CPUs, hv2 with 5; one VM of 4 CPUs.

| Strategy | Host | Left over |
| --- | --- | --- |
| first-fit | hv1 | 4 |
| best-fit | hv2 | 1: the tightest fit |

These are heuristics, not guarantees. Real schedulers filter hosts, then weigh the survivors, as OpenStack Nova does [155].

**P3.** Hosts hv1 (6 CPUs), hv2 (4 CPUs). VMs x (3), y (3), z (4) arrive in that order. First-fit, largest first: which VM is unplaced? In arrival order?

## Run it

1. With the six files in one folder, edit each starter; run `python merge_reservations_test.py` and `python place_vms_test.py`.
2. At the time box, read the solutions; run `python merge_reservations_test.py merge_reservations_solution` (8 tests) and `python place_vms_test.py place_vms_solution` (12 tests).

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| merge | sort, `start <= last_end` joins, `max` the end | `[(1, 5), (5, 8)]` → `[(1, 8)]` |
| sweep | `(t, +1)`, `(t, -1)`, sort, running max | `[(1, 5), (2, 6)]` → 2 |
| first-fit / best-fit | first host / tightest host | 8 and 5 free, VM 4 → hv1 / hv2 |

## Answers

**P1.** `[(1, 4)]`: sorted, each touches the last.

**P2.** 2. At time 3 the end of `(1, 3)` goes before the start of `(3, 5)`.

**P3.** Largest-first: y. z takes hv1 (2 left), x takes hv2 (1 left), y fits nowhere. Arrival order places all three: x and y on hv1, z on hv2.

**R1.** `(1, 10)`.

**R2.** 1.

**R3.** Yes: both CPU and RAM must fit, so it is unplaced.

**R4.** One 6-CPU VM.

**R5.** No; `sorted()` returns a new list.

**R6.** hv2: 1 left beats 4.

## If you missed a quiz question

| If you thought... | Reread | Re-check |
| --- | --- | --- |
| Assigning `end` is enough when merging | Merging | **R1.** Merge `[(1, 10), (2, 3)]`? |
| Touching intervals run at the same time | Peak | **R2.** Peak of `[(1, 5), (5, 8)]`? |
| Only CPU needs to fit | Placing | **R3.** 2 CPUs, 16 GB on a host with 8 CPUs, 4 GB: unplaced? |
| Best-fit means the most room | Placing | **R6.** 8 and 5 free, VM 4: best-fit host? |
| Arrival order never matters | Placing | **R4.** 10 + 10 CPUs, requests 4, 4, 6, 6, first-fit: what is left out? |
| `sorted(reservations)` changes the caller's list | Merging | **R5.** Does `sorted(xs)` change `xs`? |

:::key-takeaways
- Merge: sort, join when `start <= last_end`, keep `max(end)`. [12]
- Peak: sweep `(t, +1)`, `(t, -1)`; plain sort applies ends first. [12]
- Placement: both resources must fit; order changes the result.
:::

:::glossary
- **Half-open**: includes its start, excludes its end.
- **Sweep**: walking sorted start and end events with a running count.
- **First-fit**: each VM goes on the first host with room.
- **Best-fit**: each VM goes on the host left with the least room.
- **Heuristics**: quick rules of thumb, usually good, never guaranteed best.
:::
