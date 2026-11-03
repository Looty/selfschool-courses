---
id: l13
title: "Memory, OOM, cgroups and file descriptors"
quiz: quiz-02.yaml
resources: [../resources/lab5/mem_leak.py, ../resources/lab5/fd_leak.py, ../resources/lab5/log_writer.py]
sources: [55, 57, 59, 60, 61, 62, 63, 64, 66, 67, 69, 79]
---
After this lesson you can prove a container was OOM-killed by its cgroup limit while the host looked fine, and diagnose "Too many open files" and a disk that `df` calls full while `du` finds nothing.

## What "used" memory means

`vmstat` splits memory into `swpd` (swap used), `free`, `buff` and `cache` (page cache). [67] The kernel uses idle memory to cache file data, so low `free` on a healthy host is normal. In cgroup v2 terms the split is `anon` (anonymous memory: heaps) and `file` (cached filesystem data). [57] A leak grows `anon`; file cache can be reclaimed.

Per process, `/proc/PID/status` gives `VmRSS` (resident set size, the sum of `RssAnon`, `RssFile` and `RssShmem`) and `VmPeak`; the man page calls them inaccurate, but fine for spotting growth. [59] When `RssAnon` is nearly all of `VmRSS`, as in the leaking "cache" (`mem_leak.py`) from the course's test run, the growth is heap.

## The OOM killer

Memory saturation shows first as swapping (`vmstat` `si`/`so`). The last resort is the OOM killer, which logs to the kernel ring buffer: Gregg's checklist uses `dmesg | grep killed`. [55] The kernel scores candidates with a badness heuristic from 0 (never kill) to 1000 (always kill), roughly the share of allowed memory a process uses. `oom_score_adj` (-1000 to +1000) is added, and -1000 exempts a task entirely. [69] Kubernetes sets `oom_score_adj` by QoS class: -997 for Guaranteed, 1000 for BestEffort, and a formula based on the memory request for Burstable. [79]

## cgroup v2: OOM inside a box

A cgroup's `memory.max` is a hard limit. If usage reaches it and cannot be reduced, "the OOM killer is invoked in the cgroup", even if the host has plenty of free memory. `memory.high` is softer: going over it throttles and forces reclaim, but never invokes the OOM killer. [57]

The files, under the cgroup's directory (`/sys/fs/cgroup` inside a container with its own cgroup namespace): [57]

| File | Tells you |
| --- | --- |
| `memory.current` | usage now, including descendants |
| `memory.max` | the hard limit |
| `memory.peak` | the highest usage recorded |
| `memory.events` | counters: `low`, `high`, `max` (about to cross max), `oom` (limit hit, allocation about to fail), `oom_kill` (processes killed) |
| `memory.stat` | the breakdown, including `anon` and `file` |

In the course's test run, the leak ran in a container started with `--memory=300m`; the incident playbook (chapter 07) walks through this incident. `free -m` reads system-wide figures, so it showed 5.5 GB free while `memory.current` sat at the 300 MiB `memory.max`. Seconds later `memory.events` showed `oom 1` and `oom_kill 1` [57], and `dmesg` showed `Memory cgroup out of memory: Killed process 15602 (python3)`. `Memory cgroup out of memory` and `oom_memcg=/docker/...` in the kernel log mark a cgroup-limit kill, not a host-wide one.

**Kubernetes has two mechanisms.** The kubelet **evicts** pods when node signals cross thresholds, such as `memory.available` below 100Mi by default. [79] If memory runs out first, the kernel OOM killer acts instead, and the container can be restarted in place by its `restartPolicy`, unlike an evicted pod. [79]

## "Too many open files": EMFILE vs ENFILE

`/proc/PID/fd/` holds one symlink per open descriptor, and `/proc/PID/limits` gives the soft and hard limit for each resource. [60] `ls /proc/PID/fd | wc -l` against the `Max open files` line is Gregg's utilization check for descriptors. [55]

Calls that create a descriptor fail with **EMFILE** when the per-process limit (`RLIMIT_NOFILE`) is reached, and with **ENFILE** when the system-wide limit is reached. [63] EMFILE means this process leaks descriptors or needs a higher limit; ENFILE means the whole host is out. In the course's test run, a "health check" (`fd_leak.py`) opens a TCP connection per call and never closes it, under `ulimit -n 256`:

```text
health check failed after 126: [Errno 24] Too many open files
$ ls /proc/4130/fd | wc -l
256
$ grep 'Max open files' /proc/4130/limits
Max open files            256                  256                  files
```

126 checks used 252 descriptors, because both ends of each connection live in the same process. Errno 24 is EMFILE.

## ss, lsof and strace

| Tool | Use | Key options |
| --- | --- | --- |
| `ss` | sockets by state and owner | `-t` TCP, `-a` all, `-n` no name resolution, `-p` owning process, `-l` listeners, `state established` filter [62] |
| `lsof` | open files | `-p PID` one process; `+L1` "will select open files that have been unlinked" [66] |
| `strace` | syscalls as they happen | `-p PID` attach, `-f` follow threads and children, `-e trace=` filter, `-c` counts per syscall [61] |

On the leak, `ss -tanp | grep -c 'pid=4130,'` printed `253`, all ESTABLISHED to the same peer. [62] Many sockets in CLOSE-WAIT would be the same bug in another shape: the peer closed, the process never did. `lsof -p` summed up as `253 IPv4` against `11 REG`. [66] And strace showed the failing calls:

```text
$ strace -f -e trace=connect,socket,accept4 -p 4130
[pid  4132] accept4(3, ..., SOCK_CLOEXEC) = -1 EMFILE (Too many open files)
[pid  4130] socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_TCP) = -1 EMFILE (Too many open files)
```

The accept loop ran in thread 4132. [61]

## Disk full, but `du` finds nothing

A deleted file stays in existence until the last descriptor referring to it is closed. [64] The name is gone, so `du` cannot see it, but `df` still counts its blocks. In the course's test run, after `rm /data/app.log`, `df` showed the tmpfs 100% full and `du` showed `0`; `lsof +L1` listed fd `3w` of the writer, PID 4164, with `NLINK 0` and `/data/app.log (deleted)`, which is the proof. [66] Free the space now with `truncate -s 0 /proc/4164/fd/3`; in that run `df` went back to 0% without stopping the process. Fix the cause with log rotation that makes the process reopen its file. Also check `df -i`: running out of inodes fails file creation the same way.

## Gotchas

- **`free -m` looks fine, container still OOM-killed.** `free` is system-wide; the kill comes from the cgroup reaching `memory.max`. [57] Check `memory.events` for `oom_kill`.
- **Expecting `memory.high` to kill.** It throttles and forces reclaim, but never invokes the OOM killer. [57] Only `memory.max` does.
- **Evicted is not OOMKilled.** Eviction is the kubelet acting on node signals; an OOM kill is the kernel, and the container may restart in place. [79] Read the pod status before tuning limits.
- **Raising `ulimit -n` for an EMFILE leak.** Errno 24 is the per-process limit. [63] If `/proc/PID/fd` keeps growing toward it, a higher limit only delays the failure. Close the connections.
- **`strace -p` shows nothing.** Without `-f` you see only the main thread; in the course's test run the failing `accept4` ran in another thread. [61] Add `-f`.
:::key-takeaways
- Low `free` is normal; look at `anon` vs `file` and at swapping. [57] [67]
- Reaching `memory.max` invokes the OOM killer inside the cgroup even when the host has free memory; `memory.events` and "Memory cgroup out of memory" prove it. [57]
- The OOM killer picks by badness plus `oom_score_adj`; Kubernetes eviction is a separate mechanism. [69] [79]
- EMFILE is the per-process descriptor limit, ENFILE the system-wide one; `/proc/PID/fd`, `ss -tanp` and `strace -f` show the leak. [61] [62] [63]
- `df` full with `du` empty means deleted-but-open files: `lsof +L1`, then truncate via `/proc/PID/fd/N`. [64] [66]
:::

:::glossary
- **Anonymous memory**: memory not backed by a file, such as a program's heap.
- **Page cache**: file contents the kernel keeps in RAM; reclaimable.
- **OOM killer**: the kernel mechanism that kills a process when memory cannot be found.
- **cgroup (control group)**: a kernel grouping of processes with resource limits and counters.
- **`memory.max`**: the cgroup v2 hard memory limit.
- **Eviction**: the kubelet stopping a pod to free node resources.
- **QoS class**: Kubernetes' Guaranteed, Burstable or BestEffort rating of a pod, based on its requests and limits.
- **File descriptor (fd)**: a small number a process uses to refer to an open file, socket or pipe.
- **`RLIMIT_NOFILE`**: the per-process limit on open descriptors (`ulimit -n`).
- **Inode**: the filesystem record for one file; filesystems have a fixed number.
- **CLOSE-WAIT**: a TCP state where the peer has closed but the local program has not.
- **strace**: a tool that prints a process's system calls (requests to the kernel) as they happen.
:::
