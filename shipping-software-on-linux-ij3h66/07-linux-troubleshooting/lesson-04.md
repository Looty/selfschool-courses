---
id: l28
title: "Files, descriptors and syscalls: /proc, lsof, strace and ss"
quiz: quiz-04.yaml
resources: [../resources/lab5/fd_leak.py, ../resources/lab5/log_writer.py]
sources: [55, 59, 60, 61, 62, 63, 64, 66]
---
After this lesson you can diagnose "Too many open files" and "No space left on device" when `du` disagrees with `df`, read a process's limits and open files straight from `/proc`, and use `strace` and `ss` to watch what a process is actually doing.

## `/proc/PID`: the process's own account

Before any tool, look at the kernel's view of the process:

- `/proc/PID/status`: state, memory, threads, context switches, and `FDSize`, the number of descriptor slots allocated. [59]
- `/proc/PID/limits`: the soft limit, hard limit and units for each resource limit. [60]
- `/proc/PID/fd/`: one symlink per open descriptor, pointing at the file, socket or pipe.

`ls /proc/PID/fd | wc -l` against `ulimit -n` (or the `Max open files` line) is Gregg's utilization check for file descriptors. [55]

## "Too many open files": EMFILE vs ENFILE

`open()` and every other call that creates a descriptor fail with **EMFILE** when the per-process limit (`RLIMIT_NOFILE`) is reached, and with **ENFILE** when the system-wide limit on open files is reached. [63] They need different fixes. EMFILE means this process leaks descriptors or needs a higher `LimitNOFILE`. ENFILE means the whole host is out.

Lab 5's leaky "health check" opens a TCP connection per call and never closes it, under `ulimit -n 256`:

```text
health check failed after 126: [Errno 24] Too many open files
$ ls /proc/4130/fd | wc -l
256
$ grep 'Max open files' /proc/4130/limits
Max open files            256                  256                  files
```

126 checks used 252 descriptors because both ends of each connection live in the same process. Errno 24 is EMFILE. Raising the limit would only delay the failure.

## ss: sockets by state and owner

`ss -t` shows TCP sockets, `-a` both listening and non-listening, `-n` skips name resolution, `-p` shows the owning process and `-l` only listeners. State filters such as `state established` narrow the list. [62]

```text
$ ss -tanp | grep -c 'pid=4130,'
253
$ ss -tanp state established | head -n 3
Recv-Q Send-Q Local Address:Port  Peer Address:Port Process
0      0          127.0.0.1:9099     127.0.0.1:50984 users:(("python3",pid=4130,fd=236))
```

Hundreds of ESTABLISHED sockets owned by one PID, all to the same peer, is a connection leak. Many sockets in CLOSE-WAIT would point at the same bug in a different shape: the peer closed, but the process never did.

## lsof: what is open

`lsof -p PID` lists a process's open files. [66] Summarising by type showed the leak's shape: `253 IPv4` against `11 REG`. The option that earns its keep on full disks is `+L1`, which "will select open files that have been unlinked". [66]

## Disk full, but `du` finds nothing

A file that is deleted while a process holds it open stays in existence until the last descriptor referring to it is closed. [64] The name is gone, so `du` and `ls` cannot see it, but the blocks are still allocated, so `df` counts them. Lab 5's log writer, after someone ran `rm /data/app.log`:

```text
$ df -h /data
tmpfs            64M   64M     0 100% /data
$ du -sh /data
0	/data
$ lsof +L1
COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NLINK NODE NAME
python3 4164 root    3w   REG  0,102 67108864     0    2 /data/app.log (deleted)
```

`NLINK 0` and `(deleted)` are the proof. Two fixes:

- **Release the space now:** truncate the file through the process's descriptor, `truncate -s 0 /proc/4164/fd/3`. In the lab, `df` went back to 0% used without stopping the process.
- **Fix the cause:** restart the process or signal it to reopen its log, and rotate logs in a way that works with the program (copy-and-truncate, or reopen on signal).

Check `df -i` as well. A filesystem can also run out of inodes while it still has free space, and then file creation fails the same way.

## strace: the syscalls themselves

`strace -p PID` attaches to a running process; `-f` follows child processes and threads; `-e trace=` limits the output to a set, with classes such as `%file` and `%network`; `-c` counts time, calls and errors per syscall; `-T` shows time spent in each call; `-tt` adds microsecond timestamps; `-y` prints paths for descriptor arguments; `-o` writes to a file; `-s` raises the default 32-character string limit. [61] On the fd leak:

```text
$ strace -f -e trace=connect,socket,accept4 -p 4130
[pid  4132] accept4(3, ..., SOCK_CLOEXEC) = -1 EMFILE (Too many open files)
[pid  4130] socket(AF_INET, SOCK_STREAM|SOCK_CLOEXEC, IPPROTO_TCP) = -1 EMFILE (Too many open files)
```

Without `-f` you would only see the main thread. The accept loop ran in thread 4132. Gregg lists exactly this, EMFILE on calls that return descriptors, as the error signal for file descriptors. [55] Like py-spy, strace needs ptrace permission on the target, which in containers means `SYS_PTRACE` or a privileged container.

:::key-takeaways
- `/proc/PID/fd` count vs `/proc/PID/limits` "Max open files" shows descriptor utilization. [55] [60]
- EMFILE is the per-process limit; ENFILE is the system-wide one. [63]
- `ss -tanp` shows sockets per process and state; a pile of ESTABLISHED or CLOSE-WAIT sockets for one PID is a leak. [62]
- Deleted-but-open files keep their space; `lsof +L1` finds them, and truncating via `/proc/PID/fd/N` frees it. [64] [66]
- `strace -f -p PID -e trace=...` shows failing syscalls with their errno, across threads. [61]
:::

:::glossary
- **File descriptor (fd)**: a small number a process uses to refer to an open file, socket or pipe.
- **`RLIMIT_NOFILE`**: the per-process limit on open descriptors (`ulimit -n`).
- **errno**: the error code a failed system call returns, such as EMFILE.
- **Unlinked file**: a file whose name was removed while it is still open.
- **Inode**: the filesystem record for one file; filesystems have a fixed number.
- **System call (syscall)**: a request from a program to the kernel, such as `open` or `connect`.
- **CLOSE-WAIT**: a TCP state where the peer has closed but the local program has not.
- **strace**: a tool that prints a process's system calls as they happen.
:::
