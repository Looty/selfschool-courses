---
id: l29
title: "Lab 5: four incidents, diagnosed with the chapter's tools"
quiz: quiz-05.yaml
resources: [../resources/lab5/lab5-run.sh, ../resources/lab5/cpu_hog.py, ../resources/lab5/mem_leak.py, ../resources/lab5/fd_leak.py, ../resources/lab5/log_writer.py]
sources: [55, 56, 57, 59, 61, 62, 63, 64, 65, 66, 67, 71]
---
After this lab you will have diagnosed a CPU hog, a memory leak that hits a container limit, a socket leak and a disk filled by a deleted log, each from symptom to root cause, using only `vmstat`, `pidstat`, `/proc`, `py-spy`, cgroup files, `dmesg`, `ss`, `lsof` and `strace`.

This is a hands-on lab. `lab5-run.sh all` was run end to end while writing this course, in a `debian:bookworm` container with the flags below, on Docker Desktop with a WSL2 6.6 kernel and cgroup v2. Outputs are from that run; PIDs and numbers on your machine will differ. `perf` did not work on that kernel, and the script reports it as unavailable.

## Shortcut

From the resources folder (the scripts are in `lab5/`):

```bash
docker run --rm -it --privileged --memory=300m --memory-swap=300m --tmpfs /data:size=64m \
  -v "$PWD/lab5":/lab5 -w /lab5 debian:bookworm bash
bash lab5-run.sh setup
bash lab5-run.sh start 1        # investigate yourself, then compare with:
bash lab5-run.sh investigate 1
bash lab5-run.sh fix 1
```

Each flag has a job. `--privileged` lets `py-spy`, `strace` and `dmesg` work [65], `--memory` creates the cgroup limit for scenario 2, and `--tmpfs /data:size=64m` gives scenario 4 a small disk to fill without touching yours. Try each scenario with only the symptom before you run `investigate`.

## Incident 1: "the report job never finishes"

| Step | Command | What it showed |
| --- | --- | --- |
| Overview | `vmstat 1 3` | `us` 12–13 on 8 CPUs, `r` 2: one CPU busy, host not saturated [67] |
| Load | `uptime` | `0.56` three seconds in: load lags [56] |
| Who | `pidstat -u 1 1` | PID 4084 at `100.00` %CPU [71] |
| State | `/proc/4084/status` | `State: R (running)` [59] |
| Where | `py-spy dump --pid 4084` | `checksum_forever (cpu_hog.py:8)` [65] |

Root cause: a `while True` loop lost its exit condition. Fix: restore it. Killing the process only stops the symptom.

## Incident 2: "the service restarts every few minutes"

| Step | Command | What it showed |
| --- | --- | --- |
| Growth | `/proc/PID/status` | `RssAnon` 166604 kB of `VmRSS` 171828 kB after 4 s: heap [59] |
| Limit | `memory.max`, `memory.current` | 314572800 and 313917440: at the limit [57] |
| Host | `free -m` | 5593 MB free: the host looks fine |
| Proof | `memory.events` | `oom 1`, `oom_kill 1` [57] |
| Kernel | `dmesg` | `Memory cgroup out of memory: Killed process ... (python3)` [55] |

Root cause: an unbounded cache (8 MiB per request, never evicted). Fix: bound it, for example an LRU with a maximum size. Raising the limit only moves the crash.

## Incident 3: "health checks start failing after a while"

| Step | Command | What it showed |
| --- | --- | --- |
| Symptom | service log | `[Errno 24] Too many open files` (EMFILE) [63] |
| Count | `ls /proc/PID/fd \| wc -l` | 256 [55] |
| Limit | `/proc/PID/limits` | `Max open files 256 256` |
| Sockets | `ss -tanp` | 253 sockets owned by the PID, all ESTABLISHED to 127.0.0.1:9099 [62] |
| Types | `lsof -p PID` | `253 IPv4`, `11 REG` [66] |
| Syscalls | `strace -f -e trace=connect,socket,accept4 -p PID` | `accept4(...) = -1 EMFILE` in thread 4132 [61] |

Root cause: connections opened and kept in a list, never closed. Fix: close them (`with socket.create_connection(...) as s:`).

## Incident 4: "disk full, but nothing is using it"

| Step | Command | What it showed |
| --- | --- | --- |
| Symptom | `df -h /data` | `64M 64M 0 100%` |
| Contradiction | `du -sh /data` and `ls -la /data` | `0`, empty directory |
| Holder | `lsof +L1` | `python3 4164 ... 3w ... NLINK 0 ... /data/app.log (deleted)` [66] |
| Confirm | `ls -l /proc/4164/fd` | `3 -> /data/app.log (deleted)` |
| Impact | service log | `[Errno 28] No space left on device` |

Root cause: the log was deleted while the service still held it open, so its blocks stayed allocated. [64] Immediate fix: `truncate -s 0 /proc/4164/fd/3`, after which `df` showed `0%` used. Lasting fix: log rotation that makes the service reopen its file.

## Check yourself

- In incident 2, rerun with `--memory=600m`. How long until the kill, and does `memory.events` show `max` events before `oom`?
- In incident 3, run `ss -s` before and after the fix. Which counters change?

:::key-takeaways
- One busy CPU on a big host shows as low `us` with one process at 100% in `pidstat`; `py-spy dump` names the line. [65] [67] [71]
- A container OOM kill shows in `memory.events` and `dmesg` while `free -m` looks healthy. [57]
- EMFILE plus a high `/proc/PID/fd` count and many sockets in `ss` means a descriptor leak. [62] [63]
- `df` full with `du` empty means deleted-but-open files: `lsof +L1`. [64] [66]
:::

:::glossary
- **Privileged container**: a container started with most kernel restrictions lifted; for labs, not production.
- **tmpfs**: a filesystem that lives in memory, used here as a small disk to fill safely.
- **LRU cache**: a cache that evicts the least recently used entries when it reaches its size limit.
- **Root cause**: the underlying defect, as opposed to the symptom you saw first.
:::
