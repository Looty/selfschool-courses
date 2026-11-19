---
id: l12
title: "Processes, signals and systemd"
quiz: quiz-01.yaml
resources: [../resources/ch05/vmapi.service]
sources: [79, 105, 106, 117, 118, 119, 125]
---
After this lesson you can read a process's state, parent and ignored signals straight from `/proc`, say which signal each stop action sends and what it does by default, and write, install and debug a systemd unit for a Python service.

## Process state, straight from /proc

Every process has a directory `/proc/PID`. The file `status` is the readable view; `stat` is the one-line form that `ps` reads. [106] The fields to know from `status`:

| Field | Meaning |
| --- | --- |
| `State` | a letter plus a word, see below |
| `PPid` | the parent's PID |
| `Uid`, `Gid` | four values each: real, effective, saved, filesystem |
| `Threads` | number of threads |
| `SigBlk`, `SigIgn`, `SigCgt` | hex masks of blocked, ignored and caught signals |
| `VmRSS` | resident memory (the page itself flags it as inaccurate) |

[106]

| Letter | Meaning |
| --- | --- |
| R | running or runnable |
| S | sleeping in an interruptible wait |
| D | waiting in uninterruptible disk sleep |
| T | stopped by a signal |
| t | stopped by a tracer |
| Z | zombie |
| I | idle (Linux 4.14 onward) |

[106]

In the course's test run, on the broken box from lesson 4 of this chapter:

```console
# grep -E '^(Name|State|PPid|Uid|Threads|SigIgn|SigCgt)' /proc/2056/status
Name:	worker-v1.sh
State:	S (sleeping)
PPid:	1
Uid:	0	0	0	0
Threads:	1
SigIgn:	0000000000004006
SigCgt:	0000000000010000
# tr '\0' ' ' < /proc/2056/cmdline
/bin/bash /opt/worker/worker-v1.sh
```

`cmdline` holds the arguments separated by null bytes, empty for a zombie. [106] `environ` holds the starting environment; later changes do not show there. [106]

## Parents, children and zombies

A process created by `fork(2)` is a copy of its parent and inherits the parent's signal dispositions. [105] When a child stops or ends, SIGCHLD is sent, and its default action is to ignore it. [105] The broken box's dispatcher forks one child per job and never collects their exit status; in the test run every finished child sat in the table in state Z, zombie [106]:

```console
# ps -eo pid,ppid,stat,cmd | grep -E 'dispatcher|defunct'
 2057     1 S    /usr/bin/python3 /opt/dispatcher/dispatcher.py
 2063  2057 Z    [python3] <defunct>
 2065  2057 Z    [python3] <defunct>
# kill -9 2063; ps -o pid,ppid,stat -p 2063
  PID  PPID STAT
 2063  2057 Z
```

`kill -9` changes nothing: a zombie has already exited. Fix or end the parent; in the test run, killing PID 2057 let process 1 collect all its zombies within a second.

:::low-confidence
The notes record the Z state and the empty `cmdline`, not the full rule: an orphan (a process whose parent died) is re-parented to PID 1 or to a "subreaper", which must call `wait(2)`. The demo shows the effect; for the rule, read wait(2) and `PR_SET_CHILD_SUBREAPER` in prctl(2).
:::

## Signals that matter

A signal's disposition decides what happens on delivery: the default action, ignore, or run a handler. [105] The default actions are Term, Core (terminate and dump core), Ign, Stop and Cont. [105] The numbers below hold on x86 and ARM; SIGCHLD, SIGSTOP, SIGCONT and SIGUSR1 differ on some other architectures, so scripts should use names. [105]

| Signal | No. | Default | Meaning |
| --- | --- | --- | --- |
| SIGHUP | 1 | Term | controlling terminal or process went away |
| SIGINT | 2 | Term | keyboard interrupt |
| SIGQUIT | 3 | Core | keyboard quit |
| SIGKILL | 9 | Term | forced termination |
| SIGSEGV | 11 | Core | invalid memory reference |
| SIGPIPE | 13 | Term | write to a pipe with no readers |
| SIGTERM | 15 | Term | termination request |
| SIGCHLD | 17 | Ign | a child stopped, ended or continued |
| SIGCONT | 18 | Cont | resume a stopped process |
| SIGSTOP | 19 | Stop | stop the process |
| SIGTSTP | 20 | Stop | stop typed at the terminal |

[105]

SIGKILL and SIGSTOP cannot be caught, blocked or ignored. [105] A forked child inherits its parent's dispositions, and `execve(2)` resets handled signals to the default but keeps ignored ones ignored. [105] So a script that ignores SIGTERM passes that on to every program it starts.

A command killed by signal N has exit status 128+N in the shell. [125] From the test run:

```console
$ sleep 30 & kill $!; wait $!; echo $?
143
$ sleep 30 & kill -9 $!; wait $!; echo $?
137
```

143 is 128+15, so plain `kill` sent SIGTERM; 137 is 128+9. Two other statuses to know: 127 means command not found, 126 found but not executable. [125] `docker stop` sends SIGTERM, then SIGKILL after a grace period (10 s by default for Linux containers). [79]

:::low-confidence
Reading `SigIgn`: bit N-1 stands for signal N, so `0x4006` (bits 1, 2, 14) means signals 2, 3 and 15 are ignored. That matched the test run (the script had `trap '' TERM`; bash ignores SIGINT and SIGQUIT in its background jobs), but neither rule is in the notes; see proc_pid_status(5) and bash(1).
:::

## systemd units

systemd manages units: services, sockets, targets, timers, mounts and others. [119] It searches unit directories in order, and a file earlier in the list overrides a file of the same name later: [119]

| Directory | Who writes it |
| --- | --- |
| `/etc/systemd/system` | the administrator |
| `/run/systemd/system` | runtime units |
| `/usr/local/lib/systemd/system` | software the administrator installed |
| `/usr/lib/systemd/system` | the distribution's packages |

To change one setting of a packaged unit, create a drop-in, `/etc/systemd/system/NAME.service.d/override.conf`, holding only the changed lines. [119] `systemctl edit NAME` creates it and reloads the manager. [118] After editing a unit file by hand, run `systemctl daemon-reload`; `systemctl reload` is different, it asks the service to reload its own configuration. [118]

The unit for the course's small API, `vmapi.service`:

```ini
[Unit]
Description=vmapi VM inventory HTTP API
Wants=redis-server.service
After=redis-server.service

[Service]
Type=exec
User=vmapi
Group=vmapi
ExecStart=/usr/bin/python3 /opt/vmapi/vmapi.py
Restart=on-failure
RestartSec=2s
TimeoutStopSec=10s

[Install]
WantedBy=multi-user.target
```

- **[Unit]**: `Wants=` starts Redis too, but vmapi starts even if Redis is missing or fails. [119] With `Requires=`, stopping or restarting Redis stops or restarts vmapi too. [119] Neither sets an order: without `After=` both start at once, so `Wants=` and `After=` usually go together. [119]
- **[Service]**: `Type=exec` counts the service as started once the binary has actually been executed, so a wrong path fails the start. [119] With `Type=simple` (the default when `ExecStart=` is set) the start succeeds even if the binary cannot run. [119] `Restart=on-failure` is the page's recommendation for long-running services. [119] A unit stopped with `systemctl stop` is never restarted. [119] On stop, systemd runs `ExecStop=` if set, otherwise sends SIGTERM, and sends SIGKILL if the service is still running after `TimeoutStopSec=`. [119]
- **[Install]** is read only by `systemctl enable`: `WantedBy=multi-user.target` makes it create a link in `multi-user.target.wants/`. [119]

In the test run (Debian 12, systemd 252, privileged container) the Redis unit did not exist and vmapi started anyway; after `kill -9`, `Restart=on-failure` brought it back 2 s later:

```console
# systemctl enable --now vmapi
Created symlink /etc/systemd/system/multi-user.target.wants/vmapi.service → /etc/systemd/system/vmapi.service.
# kill -9 $(systemctl show -p MainPID --value vmapi)
# journalctl -u vmapi -n 8 --no-pager
Nov 19 12:23:20 643b0f37fb62 python3[119]: vmapi listening on 127.0.0.1:8080
Nov 19 12:23:21 643b0f37fb62 systemd[1]: vmapi.service: Main process exited, code=killed, status=9/KILL
Nov 19 12:23:21 643b0f37fb62 systemd[1]: vmapi.service: Failed with result 'signal'.
Nov 19 12:23:23 643b0f37fb62 systemd[1]: vmapi.service: Scheduled restart job, restart counter is at 1.
Nov 19 12:23:23 643b0f37fb62 systemd[1]: Stopped vmapi.service - vmapi VM inventory HTTP API.
Nov 19 12:23:23 643b0f37fb62 systemd[1]: Starting vmapi.service - vmapi VM inventory HTTP API...
Nov 19 12:23:23 643b0f37fb62 systemd[1]: Started vmapi.service - vmapi VM inventory HTTP API.
Nov 19 12:23:23 643b0f37fb62 python3[126]: vmapi listening on 127.0.0.1:8080
# systemctl stop vmapi; systemctl is-active vmapi; echo $?
inactive
3
```

A drop-in with a wrong `ExecStart=` path made `systemctl start` exit 1 (`status=203/EXEC`) under `Type=exec`, and 0 under `Type=simple`. Before `daemon-reload`, systemctl only warned that the file had changed and started the old version.

## systemctl and journalctl

| Command | Does |
| --- | --- |
| `systemctl status vmapi` | state, main PID and the last 10 journal lines [118] |
| `systemctl enable --now vmapi` | link it for boot and start it now [118] |
| `systemctl is-active vmapi` | exit 0 if active, 3 if not [118] |
| `systemctl --failed` | every failed unit [118] |
| `systemctl cat vmapi` | unit file plus drop-ins [118] |
| `systemctl kill -s SIGUSR1 vmapi` | send a signal, default SIGTERM [118] |
| `systemctl mask vmapi` | link it to /dev/null so nothing can start it [118] |
| `journalctl -u vmapi -f` | follow one unit's log [117] |
| `journalctl -u vmapi -n 50 --no-pager` | last 50 lines, no pager [117] |
| `journalctl -u vmapi --since today` | a time window; also `--until`, dates, `yesterday` [117] |
| `journalctl -p err -b` | errors and worse since this boot [117] |
| `journalctl -k -b -1` | kernel messages from the previous boot [117] |

## Gotchas

- **Editing a unit and nothing changes.** systemd keeps the old version until `systemctl daemon-reload`; `systemctl reload` does not do it. [118]
- **`Requires=` without `After=`.** Both units start at once and your service races its dependency. [119]
- **`Type=simple` hides a bad path.** The start reports success even if the binary cannot run; use `Type=exec`. [119]
- **`enable` does not start.** It only creates the `[Install]` links; add `--now`. [118]
- **A script that ignores SIGTERM makes its children ignore it.** Ignored dispositions survive `fork` and `execve`, so only SIGKILL works, after the stop timeout. [105] [119]

:::key-takeaways
- `/proc/PID/status` gives State, PPid, Uid and the signal masks; `ps` reads `/proc/PID/stat`. [106]
- SIGTERM (15) asks, SIGKILL (9) forces; SIGKILL and SIGSTOP cannot be caught or ignored. [105]
- Exit status 128+N means "killed by signal N": 143 for SIGTERM, 137 for SIGKILL. [125]
- `Wants=`/`Requires=` say what to start, `After=` says in which order. [119]
- Use `Type=exec` and `Restart=on-failure` for long-running services. [119]
- After editing a unit: `systemctl daemon-reload`, then restart. [118]
:::

:::glossary
- **Disposition**: what a process does when a given signal arrives: the default, ignore it, or run a handler.
- **Zombie**: a process that has exited but whose parent has not yet collected its exit status.
- **Orphan**: a process whose parent has exited.
- **Unit**: anything systemd manages, described by a unit file such as `vmapi.service`.
- **Drop-in**: a small file in `NAME.service.d/` that overrides selected lines of a unit.
- **Target**: a unit that groups other units, such as `multi-user.target`.
- **Journal**: systemd's log store, read with `journalctl`.
:::
