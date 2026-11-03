---
id: l12
title: "Method first, then CPU and disk"
quiz: quiz-01.yaml
resources: [../resources/lab5/cpu_hog.py]
sources: [54, 55, 56, 58, 59, 65, 67, 68, 71]
---
After this lesson you can work through a slow Linux host with the USE method, explain why load average can be high while the CPUs are idle, read process states including D, and use `vmstat`, `pidstat`, `py-spy` and `iostat -x` to go from "the box is slow" to the process and code line responsible.

## The USE method

Brendan Gregg's USE method fits in one sentence: "For every resource, check utilization, saturation, and errors." [54] A resource is any physical part of the server: CPUs, memory, disks, network interfaces, busses. Utilization is the average time it was busy; saturation is extra work it cannot service yet, often queued; errors is the count of error events. [54] Errors are quick to rule in or out, so checking them first is a small optimisation. [54]

The value is that it is a checklist: you stop when every resource has been checked, not at the first odd number. Gregg's Linux checklist maps each cell to commands: [55]

| Resource | Utilization | Saturation | Errors |
| --- | --- | --- | --- |
| CPU | `vmstat 1` us + sy + st; `top` per process | `vmstat 1` r greater than CPU count | perf hardware events, if available |
| Memory | `free -m`; `vmstat` free | `vmstat` si/so (swapping); OOM killer in `dmesg` | `dmesg` physical failures |
| Disk I/O | `iostat -xz 1` %util; `pidstat -d` | `iostat` queue size above 1, high await | device error counters |
| Network | `sar -n DEV 1`; `ip -s link` | drops, overruns, retransmits | `ip -s link` errors |
| File descriptors | `ls /proc/PID/fd \| wc -l` vs `ulimit -n` | (Gregg doubts it applies) | EMFILE in strace output |

This lesson covers CPU and disk; the next covers memory and descriptors.

## Load average is not CPU usage

On Linux, load averages count runnable tasks and also tasks in uninterruptible sleep. [56] A 1993 kernel patch made a slow swap disk count as load, so Linux reports **system** load, not CPU load. [56] The three numbers are exponentially damped moving sums of a five-second average, not plain 1-, 5- and 15-minute averages, so they lag. [56] A host with a hung NFS mount can show load 40 while `vmstat` reports the CPUs 90% idle.

For CPU saturation, Gregg suggests the `r` column of `vmstat 1` and per-process CPU from `pidstat 1` instead. [56] `r` is "the number of runnable processes (running or waiting for run time)"; `b` is processes blocked waiting for I/O. [67]

## Process states

The `State:` line of `/proc/PID/status` (the third field of `/proc/PID/stat`) is one letter: [58] [59]

| Letter | Meaning |
| --- | --- |
| R | Running (or runnable) |
| S | Sleeping in an interruptible wait |
| D | Waiting in uninterruptible disk sleep |
| Z | Zombie |
| T | Stopped (on a signal) |

D matters most on servers. A D process waits inside the kernel, usually on I/O, and does not react to signals until that wait ends. [58] List them with the kernel function they sleep in (`wchan`), which often names the subsystem:

```bash
ps -eo pid,stat,wchan:32,cmd | awk '$2 ~ /^D/'
```

## vmstat: the one-screen overview

Run `vmstat 1` and ignore the first line, an average since boot. The columns: [67]

| Group | Columns |
| --- | --- |
| procs | `r` runnable, `b` blocked waiting for I/O |
| swap | `si`, `so`: memory swapped in and out per second |
| io | `bi`, `bo`: KiB per second from and to block devices |
| cpu | `us` user, `sy` kernel, `id` idle, `wa` waiting for I/O, `st` stolen by the hypervisor |

From the CPU hog (`cpu_hog.py`) in the course's test run, on an 8-CPU machine:

```text
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  0      0 5794820 187816 1631560    0    0     0     0  624  537 12  1 87  0  0
 2  0      0 5794820 187816 1631560    0    0     0   100  519  487 13  0 87  0  0
```

`us` at 12–13% on 8 CPUs is one CPU fully busy, and `r` is 2, so the host is not saturated. That is the single-threaded-hog signature. `st` above zero on a VM means the hypervisor takes CPU from you. `wa` high with `b` high points at storage, not CPU.

## pidstat and py-spy: from process to code line

`pidstat -u 1` reports `%usr`, `%system`, `%wait` (time spent "waiting to run") and `%CPU` per task; `-t` adds threads and `-d` disk I/O per task. [71] From the same run:

```text
Average:      UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
Average:        0      4084  100.00    0.00    0.00    0.00  100.00     -  python3
```

`/proc/4084/status` confirmed `R (running)`. [59] For Python, `py-spy dump --pid` prints every thread's current stack without restarting the program: [65]

```text
$ py-spy dump --pid 4084
Thread 4084 (active+gil)
    checksum_forever (cpu_hog.py:8)
    main (cpu_hog.py:12)
```

Line 8 is the `while True` loop.

## iostat -x: disks

`iostat -xz 1` gives per-device extended statistics; `-z` hides idle devices. [55] Read `r/s` and `w/s` (requests per second), `r_await` and `w_await` (average ms per request, **including time in the queue**), `aqu-sz` (average queue length, `avgqu-sz` in older versions) and `%util` (share of time with requests in flight). [68] Gregg uses a queue above 1 or a high await as the saturation signal. [55]

A five-minute CPU/disk pass:

```bash
vmstat 1 5             # r vs nproc, us/sy/wa/st, si/so
pidstat -u 1 5         # who uses CPU, who waits for it
pidstat -d 1 5         # who does I/O
iostat -xz 1 5         # await, aqu-sz, then %util
```

## Gotchas

- **`%util` 100 on NVMe.** For devices that serve requests in parallel, such as RAID arrays and modern SSDs, `%util` "does not reflect their performance limits". [68] Judge by await and `aqu-sz`: low await and a short queue mean the device keeps up.
- **High load, idle CPUs.** Load counts uninterruptible tasks. [56] Find D processes with the `ps ... wchan` command and chase the disk or mount they wait on.
- **`kill -9` does nothing.** A D process ignores signals until its kernel wait ends. [58] Fix the disk, NFS server or storage path instead.
- **Load lags.** In the course's test run a full-CPU process had run three seconds when `uptime` still printed `load average: 0.56, 0.26, 0.16`. [56] Use `vmstat 1` and `pidstat 1` for "now".
- **12% CPU looks healthy.** On 8 CPUs, `us` 12 is one core pinned. [67] `pidstat -u 1` (`-t` for threads) finds the 100% task. [71]
- **`py-spy dump` permission error in a container.** It needs the `SYS_PTRACE` capability, in Docker and Kubernetes. [65] Add `--cap-add SYS_PTRACE`.

:::key-takeaways
- USE: for every resource, check utilization, saturation and errors; work the checklist to the end. [54] [55]
- Load average includes D tasks; use `vmstat 1` r against the CPU count, and `pidstat 1`, for CPU saturation. [56] [67] [71]
- D state means waiting in the kernel; signals do not help until the wait ends. [58]
- `py-spy dump --pid` shows a live Python stack; containers need SYS_PTRACE. [65]
- In `iostat -x`, `await` includes queue time; `%util` misleads on parallel devices. [68]
:::

:::glossary
- **USE method**: checking utilization, saturation and errors for every resource.
- **Saturation**: work queued because the resource is fully busy.
- **Load average**: Linux's damped count of runnable plus uninterruptible tasks.
- **Uninterruptible sleep (D state)**: a process waiting inside the kernel that cannot be woken by signals.
- **`wchan`**: the kernel function a sleeping process is waiting in.
- **Zombie**: a finished process whose parent has not yet collected its exit status.
- **Steal time (`st`)**: CPU time a hypervisor gave to other virtual machines while yours wanted to run.
- **I/O wait (`wa`)**: idle CPU time while some task waited for disk I/O.
- **py-spy**: a sampling profiler that reads a running Python process's stacks from outside.
- **`SYS_PTRACE`**: the Linux capability that allows inspecting another process's memory.
:::
