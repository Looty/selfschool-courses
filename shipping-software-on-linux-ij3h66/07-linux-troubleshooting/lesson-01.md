---
id: l25
title: "A method first: USE, load average and process states"
quiz: quiz-01.yaml
resources: []
sources: [54, 55, 56, 58, 59, 67]
---
After this lesson you can work through a slow Linux host with the USE method instead of random tools, explain why load average can be high while the CPUs are idle, and read process states, including D, from `/proc`.

## The USE method

Brendan Gregg's USE method fits in one sentence: "For every resource, check utilization, saturation, and errors." [54]

- **Resource**: any physical functional part of the server: CPUs, memory, disks, network interfaces, busses. [54]
- **Utilization**: the average time the resource was busy doing work. [54]
- **Saturation**: how much extra work the resource has that it cannot service yet, often queued. [54]
- **Errors**: the count of error events. [54]

Gregg notes that errors can be checked first as a small optimisation, because they are quick to rule in or out. [54] The method's value is that it is a checklist. You stop when every resource has been checked, not when you find the first odd number. His Linux checklist maps each cell to commands. [55]

| Resource | Utilization | Saturation | Errors |
| --- | --- | --- | --- |
| CPU | `vmstat 1` us + sy + st; `top` per process | `vmstat 1` r greater than CPU count | perf hardware events, if available |
| Memory | `free -m`; `vmstat` free | `vmstat` si/so (swapping); OOM killer in `dmesg` | `dmesg` physical failures |
| Disk I/O | `iostat -xz 1` %util; `pidstat -d` | `iostat` queue size above 1, high await | device error counters (see the checklist) |
| Network | `sar -n DEV 1`; `ip -s link` | drops, overruns, retransmits | `ip -s link` errors |
| File descriptors | `ls /proc/PID/fd \| wc -l` vs `ulimit -n` | (Gregg doubts it applies) | EMFILE in strace output |

The cells come from Gregg's checklist [55]; lessons 26 to 28 show each command in action.

## Load average is not CPU usage

On Linux, load averages count not only runnable tasks but also tasks in uninterruptible sleep. [56] Gregg traces this to a 1993 kernel patch that made a slow swap disk count as load, so Linux reports **system** load, not CPU load. [56] The three numbers are not plain 1-, 5- and 15-minute averages either: they are exponentially damped moving sums of a five-second average. [56] Two consequences:

- A host with a hung NFS mount or a saturated disk can show a load of 40 while `vmstat` reports the CPUs 90% idle. The load is made of processes stuck in D state.
- Load lags. In Lab 5 a process using a full CPU had been running for three seconds when `uptime` still printed `load average: 0.56, 0.26, 0.16`.

For CPU saturation specifically, Gregg suggests per-thread run queue latency, the `r` column of `vmstat 1`, and per-process CPU from `pidstat 1`. [56] The `r` column is "the number of runnable processes (running or waiting for run time)"; `b` is processes blocked waiting for I/O. [67]

## Process states

The third field of `/proc/PID/stat`, also the `State:` line of `/proc/PID/status`, is a single letter: [58] [59]

| Letter | Meaning |
| --- | --- |
| R | Running (or runnable) |
| S | Sleeping in an interruptible wait |
| D | Waiting in uninterruptible disk sleep |
| Z | Zombie |
| T | Stopped (on a signal) |
| t | Tracing stop |
| I | Idle (kernel threads, Linux 4.14+) |

D is the one that matters on servers. A process in D is waiting inside the kernel, usually on I/O, and does not react to signals until that wait ends. `kill -9` on a D process seems to do nothing. The fix is whatever the kernel is waiting for: the disk, the NFS server, the storage path. Find D processes with:

```bash
ps -eo pid,stat,wchan:32,cmd | awk '$2 ~ /^D/'
```

`wchan` shows the kernel function the process sleeps in, which often names the subsystem (for example an NFS or block-layer function).

:::key-takeaways
- USE: for every resource, check utilization, saturation and errors; work the checklist to the end. [54] [55]
- Linux load average includes uninterruptible (D) tasks, so it measures system load, not CPU load. [56]
- Use `vmstat 1` r against the CPU count, and `pidstat 1`, for CPU saturation instead of load average. [55] [56] [67]
- D state means waiting in the kernel (usually I/O); signals do not help until the wait ends. [58]
:::

:::glossary
- **USE method**: checking utilization, saturation and errors for every resource.
- **Utilization**: how busy a resource was over a time window.
- **Saturation**: work queued because the resource is fully busy.
- **Load average**: Linux's damped count of runnable plus uninterruptible tasks.
- **Uninterruptible sleep (D state)**: a process waiting inside the kernel that cannot be woken by signals.
- **Run queue**: the tasks waiting for a CPU.
- **`wchan`**: the kernel function a sleeping process is waiting in.
- **Zombie**: a finished process whose parent has not yet collected its exit status.
:::
