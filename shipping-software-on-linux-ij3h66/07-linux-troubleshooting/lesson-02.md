---
id: l26
title: "CPU and disk: vmstat, pidstat and iostat"
quiz: quiz-02.yaml
resources: [../resources/lab5/cpu_hog.py]
sources: [55, 59, 65, 67, 68, 70, 71]
---
After this lesson you can read `vmstat`, `pidstat` and `iostat -x` output column by column, go from "the box is slow" to the process and the code line responsible, and tell when `%util` is lying to you.

## vmstat: the one-screen overview

Run `vmstat 1` and ignore the first line, which is an average since boot. The columns, from the man page: [67]

| Group | Columns |
| --- | --- |
| procs | `r` runnable (running or waiting for run time), `b` blocked waiting for I/O |
| memory | `swpd`, `free`, `buff`, `cache` |
| swap | `si`, `so`: memory swapped in and out per second |
| io | `bi`, `bo`: KiB per second from and to block devices |
| system | `in` interrupts, `cs` context switches per second |
| cpu | `us` user, `sy` kernel, `id` idle, `wa` waiting for I/O, `st` stolen by the hypervisor |

From Lab 5's CPU hog on an 8-CPU machine:

```text
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  0      0 5794820 187816 1631560    0    0     0     0  624  537 12  1 87  0  0
 2  0      0 5794820 187816 1631560    0    0     0   100  519  487 13  0 87  0  0
```

`us` is about 12–13% on 8 CPUs, which is one CPU fully busy, so the host is not saturated (`r` is 2). That is the single-threaded-hog signature: the box looks fine overall, but one request path is stuck. `st` above zero on a VM means the hypervisor is taking CPU time from you. `wa` high with `b` high points at storage, not CPU.

## pidstat: which process

`pidstat -u 1` reports `%usr`, `%system`, `%wait` (time spent "waiting to run") and `%CPU` per task. [71] From the lab:

```text
Average:      UID       PID    %usr %system  %guest   %wait    %CPU   CPU  Command
Average:        0      4084  100.00    0.00    0.00    0.00  100.00     -  python3
```

`-t` adds per-thread lines, `-r` adds page faults and memory (VSZ, RSS), `-d` adds disk reads and writes per task, and `-w` adds context switches. [71] A high `%wait` with modest `%CPU` means the task wants more CPU than it gets, which is saturation for that task.

## From process to code line

`/proc/PID/status` confirms the state (`R (running)`) and shows the context switches. [59] For Python, `py-spy dump --pid` prints every thread's current stack without restarting or changing the program. [65]

```text
$ py-spy dump --pid 4084
Thread 4084 (active+gil)
    checksum_forever (cpu_hog.py:8)
    main (cpu_hog.py:12)
```

Line 8 is the `while True` loop. In a container, py-spy needs the `SYS_PTRACE` capability (`--cap-add SYS_PTRACE`); the same applies in Kubernetes. [65] For native code, `perf top` "generates and displays a performance counter profile in real time" and takes `-p PID` and `-g` for call graphs. [70]

:::low-confidence
`perf` did not run in this course's lab environment (Docker Desktop on a WSL2 kernel). The script fell back to "perf not available on this kernel". The perf-top man page does not cover kernel permission settings. On a normal Linux host, expect to need root or a relaxed `perf_event_paranoid` setting, and check your distribution's documentation.
:::

## iostat -x: disks

`iostat -xz 1` gives per-device extended statistics; `-z` hides idle devices. [55] The columns you read first: [68]

- `r/s`, `w/s`: completed read and write requests per second, after merges;
- `rkB/s`, `wkB/s`: throughput;
- `r_await`, `w_await`: average milliseconds per request, **including time in the queue**;
- `aqu-sz`: average queue length (older versions call it `avgqu-sz`);
- `%util`: the share of time the device had requests in flight.

The trap: `%util` near 100% means saturation only for a device that serves one request at a time. For devices that serve requests in parallel, such as RAID arrays and modern SSDs, it "does not reflect their performance limits". [68] On NVMe, trust `await` and `aqu-sz` over `%util`. Gregg's checklist uses `avgqu-sz > 1` or a high await as the saturation signal. [55]

## A five-minute CPU/disk pass

```bash
vmstat 1 5             # r vs nproc, us/sy/wa/st, si/so
pidstat -u 1 5         # who uses CPU, who waits for it
pidstat -d 1 5         # who does I/O
iostat -xz 1 5         # await, aqu-sz, then %util
```

Then go deeper on the one process that stands out: `/proc/PID/status`, `py-spy dump`, `strace` (lesson 28).

:::key-takeaways
- `vmstat 1`: compare `r` with the CPU count; read `us/sy/wa/st`; `si/so` non-zero means swapping. [67]
- `pidstat -u 1` finds the process; `%wait` is time spent waiting to run. [71]
- `py-spy dump --pid` shows a live Python stack without restarting it; containers need SYS_PTRACE. [65]
- In `iostat -x`, `await` includes queue time and `aqu-sz` is the queue; `%util` is misleading on parallel devices. [68]
:::

:::glossary
- **Context switch**: the CPU switching from one task to another.
- **Steal time (`st`)**: CPU time a hypervisor gave to other virtual machines while yours wanted to run.
- **I/O wait (`wa`)**: idle CPU time while some task waited for disk I/O.
- **py-spy**: a sampling profiler that reads a running Python process's stacks from outside.
- **`SYS_PTRACE`**: the Linux capability that allows inspecting another process's memory.
- **perf**: the Linux profiler built on kernel performance counters.
- **await**: average time a disk request took, queue time included.
- **Queue length (`aqu-sz`)**: average number of requests waiting at or in the device.
:::
