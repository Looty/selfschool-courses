---
id: l04
title: "Processes, signals and systemd"
quiz: quiz-04.yaml
resources: [../resources/ch02/vmapi.service]
sources: [79, 105, 106, 117, 118, 119, 125]
---
After this lesson you can answer "the service is down, walk me through it": read a process's state from `/proc`, say what each stop signal does, and write and debug a systemd unit.

## The interview answer, in order

```bash
systemctl status vmapi                  # state, main PID, last 10 journal lines
journalctl -u vmapi -n 50 --no-pager    # what it said before it died
ss -ltnp                                # is anything listening? (lesson 3)
systemctl --failed                      # every failed unit
```

[117] [118]

## Process state from /proc

`/proc/PID/status` is the readable view; `ps` reads the one-line `/proc/PID/stat`. [106]

```console
# grep -E '^(Name|State|PPid|SigIgn)' /proc/2056/status
Name:	worker-v1.sh
State:	S (sleeping)
PPid:	1
SigIgn:	0000000000004006
```

States: R running, S interruptible sleep, D uninterruptible disk sleep, T stopped, Z zombie. [106] `SigBlk`, `SigIgn`, `SigCgt` are hex masks of blocked, ignored and caught signals. [106]

A zombie (`Z`, `<defunct>` in `ps`) has already exited; its parent never collected its exit status. When a child ends, SIGCHLD is sent, and its default action is to ignore it. [105] `kill -9` on a zombie changes nothing: fix or end the parent.

## Signals that matter

```text
SIGHUP   1  Term  terminal or controlling process went away
SIGINT   2  Term  keyboard interrupt
SIGKILL  9  Term  forced; cannot be caught, blocked or ignored
SIGTERM 15  Term  polite termination request
SIGCHLD 17  Ign   a child stopped or ended
SIGSTOP 19  Stop  stop; cannot be caught, blocked or ignored
```

[105] A forked child inherits its parent's dispositions, and `execve(2)` keeps ignored signals ignored. [105] So a script with `trap '' TERM` makes every program it starts ignore SIGTERM too.

Exit status tells you how a command ended. [125]

```console
$ sleep 30 & kill $!; wait $!; echo $?
143          # 128+15: killed by SIGTERM
$ sleep 30 & kill -9 $!; wait $!; echo $?
137          # 128+9: killed by SIGKILL
```

127 means command not found, 126 found but not executable. [125] `docker stop` sends SIGTERM, then SIGKILL after a grace period (10 s by default). [79]

## A systemd unit

A file in `/etc/systemd/system` (the administrator's) overrides one of the same name in `/usr/lib/systemd/system` (the packages'). [119] To change one line of a packaged unit, `systemctl edit NAME` creates a drop-in `NAME.service.d/override.conf`. [118] [119]

```ini
[Unit]
Description=vmapi VM inventory HTTP API
Wants=redis-server.service
After=redis-server.service

[Service]
Type=exec
User=vmapi
ExecStart=/usr/bin/python3 /opt/vmapi/vmapi.py
Restart=on-failure
RestartSec=2s
TimeoutStopSec=10s

[Install]
WantedBy=multi-user.target
```

- `Wants=` and `Requires=` say what to start; neither sets an order, so add `After=` or both start at once. [119]
- `Type=exec` fails the start if the binary cannot run; `Type=simple` reports success anyway. [119]
- `Restart=on-failure` is the recommended setting for long-running services; a unit stopped with `systemctl stop` is never restarted. [119]
- On stop, systemd runs `ExecStop=` if set, else sends SIGTERM, then SIGKILL after `TimeoutStopSec=`. [119]
- `[Install]` is read only by `systemctl enable`. [119]

Open `vmapi.service` in the resources: it is this unit with a comment on every line.

## Commands to type from memory

```bash
systemctl daemon-reload            # reread unit files after editing them
systemctl enable --now vmapi       # start at boot AND now; enable alone does not start
systemctl is-active vmapi          # exit 0 if active, 3 if not
systemctl cat vmapi                # unit file plus drop-ins
journalctl -u vmapi -f             # follow one unit's log
journalctl -u vmapi --since today  # time window
journalctl -p err -b               # errors since this boot
```

[117] [118]

The classic trap: `systemctl reload` asks the service to reload its own configuration; it does not reread the unit file. Only `daemon-reload` does. [118]

:::key-takeaways
- Service down: `systemctl status`, `journalctl -u`, then the exit status and the unit. [117] [118]
- SIGTERM (15) asks, SIGKILL (9) forces; SIGKILL and SIGSTOP cannot be caught. [105]
- 128+N means killed by signal N; 126 not executable, 127 not found. [125]
- `After=` sets order, `Wants=`/`Requires=` do not; use `Type=exec` and `Restart=on-failure`. [119]
- After editing a unit: `daemon-reload`, then restart. [118]
:::

:::glossary
- **Disposition**: what a process does when a given signal arrives: the default, ignore it, or run a handler.
- **Zombie**: a process that has exited but whose parent has not yet collected its exit status.
- **Unit**: anything systemd manages, described by a unit file such as `vmapi.service`.
- **Drop-in**: a small file in `NAME.service.d/` that overrides selected lines of a unit.
:::
