---
id: l14
title: "Incident playbook: from symptom to cause"
quiz: quiz-03.yaml
resources: [../resources/lab5/lab5-run.sh, ../resources/lab5/cpu_hog.py, ../resources/lab5/mem_leak.py, ../resources/lab5/fd_leak.py, ../resources/lab5/log_writer.py]
sources: [54, 55, 56, 57, 59, 60, 61, 62, 63, 64, 65, 66, 67, 71]
---
After this lesson you can take a vague report through a fixed playbook (symptom, first command, what the evidence means, cause, fix) and recognise the decisive output of four classic incidents: a CPU hog, a container OOM kill, a descriptor leak and a deleted-but-open log.

## The playbook

1. **Symptom**: what the user or monitor reports.
2. **First command**: the cheapest check that points at a resource. Errors are quick to rule in or out, so check them first [54]: an errno in the log is the best start.
3. **Evidence**: a USE cell (utilization, saturation or errors) for one resource, from Gregg's Linux checklist. [55]
4. **Cause**: a defect in code or configuration, not the resource that ran out.
5. **Fix**: something that removes the cause. Killing, restarting or raising a limit only moves the symptom.

Outputs below are from the course's test run, in a container on an 8-CPU host with cgroup v2.

| Incident | USE cell | Decisive evidence |
| --- | --- | --- |
| 1: job never finishes | CPU utilization, saturation | one PID at 100 %CPU |
| 2: service keeps restarting | memory saturation: OOM killer | `memory.events` `oom_kill 1` |
| 3: health checks fail | descriptor utilization, errors | EMFILE, fd count at the limit |
| 4: disk full, nothing using it | an error, then two tools disagree | `lsof +L1` shows `(deleted)` |

Optional: `../resources/lab5/lab5-run.sh` recreates each incident with `start N`, `investigate N` and `fix N` if you want to watch one live.

## Incident 1: the report job never finishes

**First command:** `vmstat 1`, whose `r` column counts "the number of runnable processes (running or waiting for run time)". [67] One sample, group-header line cut:

```text
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  0      0 5794820 187816 1631560    0    0     0     0  624  537 12  1 87  0  0
```

**Meaning:** `us` 12 on 8 CPUs is one CPU fully busy, and `r` 2 says the host is not saturated. [67] `uptime` would mislead: it printed `0.56` three seconds in, because load lags. [56] `pidstat -u 1` finds the process (header line cut) [71]:

```text
Average:        0      4084  100.00    0.00    0.00    0.00  100.00     -  python3
```

`py-spy dump` prints the live stack without restarting the program (the caller's frame line cut) [65]:

```text
$ py-spy dump --pid 4084
Thread 4084 (active+gil)
    checksum_forever (cpu_hog.py:8)
```

In a container, py-spy needs the `SYS_PTRACE` capability (`--cap-add SYS_PTRACE`), in Docker and in Kubernetes. [65]

**Cause:** a `while True` loop lost its exit condition. **Fix:** restore it.

## Incident 2: the service restarts every few minutes

**First command:** `/proc/PID/status`. Four seconds in, `RssAnon` was 166604 kB of a `VmRSS` of 171828 kB: the growth is heap. [59] Then compare the cgroup with the host [57]:

```text
$ cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.current
314572800
313917440
$ free -m
               total        used        free      shared  buff/cache   available
Mem:            7942         886        5593          26        1679        7055
```

**Meaning:** the container sits at its 300 MiB `memory.max` while the system-wide `free -m` shows 5593 MB free. Reaching `memory.max` invokes the OOM killer inside the cgroup anyway. [57] Seconds later (the `low 0` and `high 0` lines cut):

```text
$ cat /sys/fs/cgroup/memory.events
max 3204
oom 1
oom_kill 1
$ dmesg | grep -i 'killed process'
Memory cgroup out of memory: Killed process 15602 (python3) total-vm:300748kB, anon-rss:289024kB, ...
```

The OOM killer in `dmesg` is the memory-saturation signal in Gregg's checklist. [55]

**Cause:** an unbounded cache, 8 MiB per request, never evicted. **Fix:** bound it, for example an LRU with a maximum size.

## Incident 3: health checks start failing

**First command:** the service log, an error first. [54]

```text
health check failed after 126: [Errno 24] Too many open files
$ ls /proc/4130/fd | wc -l
256
$ grep 'Max open files' /proc/4130/limits
Max open files            256                  256                  files
```

**Meaning:** errno 24 is EMFILE, the per-process limit; ENFILE would mean the whole host is out. [63] The descriptor count against `Max open files` is the utilization check, here at 100%. [55] [60] `ss -tanp` showed 253 sockets owned by the PID, all ESTABLISHED to 127.0.0.1:9099 [62]: both ends of each connection live in the same process. `strace -f` follows threads [61]; one line, the other cut:

```text
$ strace -f -e trace=connect,socket,accept4 -p 4130
[pid  4132] accept4(3, ..., SOCK_CLOEXEC) = -1 EMFILE (Too many open files)
```

The failing accept loop ran in thread 4132, which plain `strace -p` would miss.

**Cause:** connections opened, kept in a list, never closed. **Fix:** close them (`with socket.create_connection(...) as s:`).

## Incident 4: disk full, but nothing is using it

**First command:** the log said `[Errno 28] No space left on device`, so check the filesystem both ways:

```text
$ df -h /data
tmpfs            64M   64M     0 100% /data
$ du -sh /data
0	/data
$ lsof +L1
COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NLINK NODE NAME
python3 4164 root    3w   REG  0,102 67108864     0    2 /data/app.log (deleted)
```

**Meaning:** a deleted file stays in existence until the last descriptor referring to it is closed [64], so `du` cannot see its name but `df` still counts its blocks. `lsof +L1` selects open files that have been unlinked [66]; `NLINK 0` and `(deleted)` are the proof.

**Cause:** the log was removed while the service held it open. **Stop-gap:** `truncate -s 0 /proc/4164/fd/3`; `df` went back to 0% used. **Fix:** log rotation that makes the service reopen its file.

## Stop-gap or fix?

| Incident | Stop-gap | Lasting fix |
| --- | --- | --- |
| 1 | kill the process | restore the loop's exit condition |
| 2 | raise `--memory` | bound the cache |
| 3 | raise `ulimit -n` | close each connection |
| 4 | truncate via `/proc/PID/fd/N` | rotation that reopens the log |

## Gotchas

- **Raising the memory limit.** The cache never evicts, so any `memory.max` is reached again and the OOM kill repeats. [57] Bound the cache.
- **Raising `ulimit -n` for EMFILE.** If `/proc/PID/fd` keeps growing toward the limit, a higher limit only delays the failure. [63] Close the connections.
- **Stopping at `truncate`.** The service still writes to the deleted file through its descriptor, so the space fills up again until it reopens its log. [64] Fix the rotation.
- **`strace -p` shows nothing.** Without `-f` you see only the main thread. [61] Add `-f`.

:::key-takeaways
- Start with errors, then work the USE cells of one resource. [54] [55]
- Low `us` with one PID at 100% in `pidstat` is a single-threaded hog; `py-spy dump` names the line. [65] [67] [71]
- A container OOM kill shows in `memory.events` and `dmesg` while `free -m` looks healthy. [57]
- EMFILE with `/proc/PID/fd` at `Max open files` is a descriptor leak. [60] [63]
- `df` full with `du` empty means a deleted-but-open file: `lsof +L1`. [64] [66]
:::

:::glossary
- **Playbook**: a fixed sequence of steps, from symptom to fix, applied to every incident.
- **Root cause**: the underlying defect, as opposed to the symptom you saw first.
- **Stop-gap**: an action that relieves the symptom for now without removing the cause.
- **LRU cache**: a cache that evicts the least recently used entries when it reaches its size limit.
- **EMFILE**: the error when a process reaches its own open-descriptor limit.
- **Unlinked file**: a file whose name was removed while it is still open.
- **`SYS_PTRACE`**: the Linux capability that allows inspecting another process's memory.
:::
