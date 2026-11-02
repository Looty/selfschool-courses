---
id: l27
title: "Memory, the OOM killer and cgroup v2 limits"
quiz: quiz-03.yaml
resources: [../resources/lab5/mem_leak.py]
sources: [55, 57, 59, 67, 69, 79]
---
After this lesson you can tell real memory pressure from page cache, find out which OOM killer struck and why, and explain how a container can be OOM-killed while `free -m` on the host looks fine.

## What "used" means

`vmstat` splits memory into `swpd` (swap used), `free` (idle), `buff` (buffers) and `cache` (page cache). [67] The kernel uses idle memory to cache file data, so low `free` on a healthy host is normal. In cgroup v2 terms the split is `anon` (anonymous memory: heaps, `mmap(MAP_ANONYMOUS)`) and `file` (cached filesystem data, including tmpfs and shared memory). [57] Anonymous memory is what a leak grows; file cache can be reclaimed.

Per process, `/proc/PID/status` gives `VmRSS` (resident set size, which is the sum of `RssAnon`, `RssFile` and `RssShmem`), `VmPeak` and `VmSwap`. The man page warns these values are inaccurate and points to `/proc/PID/statm`. [59] They are fine for spotting growth. Lab 5's leaking "cache", four seconds in:

```text
VmPeak:   177808 kB
VmRSS:    171828 kB
RssAnon:  166604 kB
RssFile:    5224 kB
```

`RssAnon` is nearly all of `VmRSS`, so the growth is heap.

## Saturation and the OOM killer

Memory saturation shows up first as swapping (`vmstat` `si`/`so`) and page scanning. The last resort is the OOM killer, which logs to the kernel ring buffer: Gregg's checklist uses `dmesg | grep killed`. [55] The kernel scores candidates with a badness heuristic from 0 (never kill) to 1000 (always kill), roughly the share of allowed memory a process uses. `oom_score_adj` (-1000 to +1000) is added to that score, and -1000 exempts a task entirely. [69] Kubernetes sets `oom_score_adj` by QoS class: -997 for Guaranteed, 1000 for BestEffort, and a formula based on the memory request for Burstable. [79]

## cgroup v2: OOM inside a box

A cgroup's `memory.max` is a hard limit. If usage reaches it and cannot be reduced, "the OOM killer is invoked in the cgroup". [57] That kill happens even if the host has plenty of free memory. `memory.high` is softer: going over it throttles the cgroup and forces reclaim, but it never invokes the OOM killer. [57]

The files that tell the story, all under the cgroup's directory (inside a container with its own cgroup namespace, that is `/sys/fs/cgroup`): [57]

- `memory.current`: usage now, including descendants;
- `memory.max`: the hard limit;
- `memory.peak`: the highest usage recorded;
- `memory.events`: counters for `low`, `high`, `max` (usage was about to cross max), `oom` (the limit was hit and an allocation was about to fail) and `oom_kill` (processes in this cgroup killed by an OOM killer);
- `memory.stat`: the breakdown, including `anon` and `file`.

Lab 5 ran the leak in a container started with `--memory=300m`:

```text
$ cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.current
314572800
313917440
$ free -m
               total        used        free      shared  buff/cache   available
Mem:            7942         886        5593          26        1679        7055
```

`free -m` reads system-wide figures, so it showed 5.5 GB free while the container sat at its 300 MiB limit. Seconds later:

```text
$ cat /sys/fs/cgroup/memory.events
low 0
high 0
max 3204
oom 1
oom_kill 1
$ dmesg | grep -i 'killed process'
Memory cgroup out of memory: Killed process 15602 (python3) total-vm:300748kB, anon-rss:289024kB, ...
```

`Memory cgroup out of memory` and `oom_memcg=/docker/...` in the kernel log mark a cgroup-limit kill, not a host-wide one. The PID in `dmesg` (15602) differs from the PID inside the container, because the kernel logs the host's PID-namespace view. Reading `dmesg` from a container needed `--privileged` in the lab. On a normal host, run it on the node.

## Kubernetes: two different mechanisms

The kubelet evicts pods when node-level signals cross thresholds: `memory.available` below 100Mi by default on Linux, computed from cgroupfs rather than `free -m`, and excluding inactive file cache. [79] That is **eviction**: the pod is stopped and rescheduled. If memory runs out before the kubelet can reclaim, the kernel's OOM killer acts instead. An OOM-killed container can be restarted in place according to its `restartPolicy`, unlike an evicted pod. [79] "OOMKilled" on a container with a memory limit is usually the cgroup case from this lesson.

:::key-takeaways
- Low `free` is normal; look at `anon` vs `file` and at swapping (`si`/`so`). [57] [67]
- The OOM killer picks by badness (0–1000) plus `oom_score_adj` (-1000 exempts). [69]
- Reaching `memory.max` invokes the OOM killer inside the cgroup, even when the host has free memory. [57]
- `memory.events` (`oom`, `oom_kill`) and "Memory cgroup out of memory" in `dmesg` prove a cgroup-limit kill. [57]
- Kubernetes eviction (kubelet, node signals) and OOM kills (kernel, cgroup) are different mechanisms. [79]
:::

:::glossary
- **Anonymous memory**: memory not backed by a file, such as a program's heap.
- **Page cache**: file contents the kernel keeps in RAM; reclaimable.
- **RSS**: resident set size, the part of a process's memory currently in RAM.
- **OOM killer**: the kernel mechanism that kills a process when memory cannot be found.
- **cgroup (control group)**: a kernel grouping of processes with resource limits and counters.
- **`memory.max`**: the cgroup v2 hard memory limit.
- **Eviction**: the kubelet stopping a pod to free node resources.
- **QoS class**: Kubernetes' Guaranteed, Burstable or BestEffort rating of a pod, based on its requests and limits.
:::
