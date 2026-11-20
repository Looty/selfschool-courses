---
id: l04
title: "Processes, signals and systemd"
quiz: quiz-04.yaml
resources: [../resources/ch02/vmapi.service]
sources: [79, 105, 106, 117, 118, 119, 125]
---
After this lesson you can say what `kill`, `kill -9` and `kill -HUP` do, decode an exit status such as 137, and answer "the service is down, walk me through it".

## Signals: asking versus forcing

**Prerequisite.** A signal is a short numbered message the kernel delivers to a process. Per signal, a process has a disposition: default action, ignore, or its own handler. [105]

**Rule:** SIGTERM is a knock on the door (the process may clean up, or ignore it); SIGKILL removes it without asking. [105]

Each rung starts `sleep 30` in the background (`$!` is its PID); `wait` collects its status, 128+N for signal N. [125]

```console
$ sleep 30 & kill $!; wait $!; echo $?         # plain kill sends TERM (15)
143                                             # 128 + 15
$ sleep 30 & kill -9 $!; wait $!; echo $?      # KILL (9)
137                                             # 128 + 9
$ sleep 30 & kill -HUP $!; wait $!; echo $?    # HUP (1); sleep has no handler
129                                             # 128 + 1: HUP's default is Term
$ bash -c 'trap "" TERM; sleep 30' & sleep 1; kill $!   # edge: TERM ignored
$ ps -o stat= -p $!                             # S: still alive, sleeping
$ kill -9 $!; wait $!; echo $?                 # KILL cannot be ignored
137
```

Ignored signals are inherited by children and survive `execve`, so `trap '' TERM` in a script spreads to every program it starts. [105] `SigIgn` in `/proc/PID/status` shows them. [106] Edge: `kill -9` on a zombie (`<defunct>`, state Z) changes nothing; it has already exited. Fix or end its parent. [106]

**Contrast:**

| Signal | No. | Default | Catchable? | Sent by |
| --- | --- | --- | --- | --- |
| SIGTERM | 15 | Term | yes | `kill`, `systemctl stop`, `docker stop` |
| SIGKILL | 9 | Term | no | `kill -9`; systemd and `docker stop` after a timeout (Docker: 10 s) |
| SIGHUP | 1 | Term | yes | the terminal or controlling process went away |

[105] [119] [79] Memory hook: TERM "please leave", KILL "security drags you out", HUP "the phone line hung up".

**P1.** A script with `trap '' TERM` starts `worker`. What do `kill WORKER_PID` and then `kill -9 WORKER_PID` do?

:::answer
`kill` does nothing: the worker inherited the ignored TERM. `kill -9` ends it; `wait` reports 137.
:::

## Exit statuses: how a command ended

**Rule:** 127 is not found, 126 is found but not executable, above 128 is killed by signal (status minus 128). [125]

```console
$ nosuchcmd; echo $?                           # 127: not found
127
$ chmod 644 job.sh; ./job.sh; echo $?          # 126: found, no execute bit
126
$ sleep 30 & kill -INT $!; wait $!; echo $?    # 130 = 128 + 2, SIGINT (Ctrl-C)
130
```

[125] [105]

**P2.** A job log says `exit status 143`. Crash, bad path, or stop request?

:::answer
A stop request: 143 − 128 = 15, SIGTERM.
:::

## systemctl: which command rereads what

**Rule:** systemd keeps its own copy of each unit file; `daemon-reload` refreshes that copy, `restart` restarts the process, `reload` asks the service to reread its *own* config. [118]

`vmapi.service` in the resources is a unit with `Restart=on-failure` and a comment per line. Test-run ladder:

```console
# systemctl enable --now vmapi                   # link for boot AND start now
Created symlink /etc/systemd/system/multi-user.target.wants/vmapi.service → ...
# kill -9 $(systemctl show -p MainPID --value vmapi)
# journalctl -u vmapi -n 8 --no-pager            # back 2 s later (RestartSec=2s)
... Main process exited, code=killed, status=9/KILL
... Scheduled restart job, restart counter is at 1.
# systemctl stop vmapi; systemctl is-active vmapi; echo $?
inactive                                         # edge: a stop is never restarted
3
```

[118] [119]

**Contrast:**

| Command | Rereads the unit file? | Touches the process? |
| --- | --- | --- |
| `systemctl daemon-reload` | yes | no |
| `systemctl reload vmapi` | no | asks it to reread its own config |
| `systemctl restart vmapi` | no | stops and starts it |
| `systemctl enable vmapi` | no | no: boot links only; add `--now` |

[118] On stop, systemd runs `ExecStop=` if set, else sends SIGTERM, then SIGKILL after `TimeoutStopSec=`. [119]

**P3.** You change `ExecStart=`, run `systemctl reload vmapi`, and the old command still runs. Why? What fixes it?

:::answer
`reload` does not reread unit files. Run `systemctl daemon-reload`, then `systemctl restart vmapi`.
:::

## "The service is down": the walk-through

1. `systemctl status vmapi`: state, main PID, last 10 log lines. [118]
2. `journalctl -u vmapi -n 50 --no-pager`: its last words. [117]
3. Decode the end: `status=9/KILL`, 143, 126, 127.
4. `systemctl cat vmapi`: unit file plus drop-ins. [118]
5. Fix; `daemon-reload` if you edited the unit; `restart`. [118]
6. Running but unreachable? `ss -ltnp` (lesson 3).

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| `kill PID` | sends TERM, can be ignored | `sleep` → 143 |
| `kill -9 PID` | KILL, cannot be ignored | `sleep` → 137 |
| exit status | 126 no x, 127 not found, 128+N signal N | 130 → SIGINT |
| `daemon-reload` | reread unit files | then `restart` |
| `enable --now` | boot link and start | `enable` alone: not started |

## If you missed a quiz question

**If you thought** `kill` means "force": reread "Signals". **R1.** Does `kill PID` send signal 9?

:::answer
No. Plain `kill` sends 15, TERM.
:::

**If you thought** status 137 means "exited with 137" or "not found": reread "Exit statuses". **R2.** Decode 137.

:::answer
128 + 9 = 137: killed by SIGKILL.
:::

**If you thought** `kill -9` clears a zombie: reread "Signals". **R3.** Can `kill -9` remove a `<defunct>` process?

:::answer
No: it already exited. Fix or end its parent.
:::

**If you thought** `enable` starts the service: reread "systemctl". **R4.** Is a service running right after `systemctl enable`?

:::answer
No: `enable` only creates the boot link.
:::

**If you thought** `Restart=on-failure` undoes `systemctl stop`: reread "systemctl". **R5.** Does systemd restart a unit you stopped?

:::answer
No: a unit stopped with `systemctl stop` is never restarted.
:::

:::key-takeaways
- TERM (15) asks, KILL (9) forces; ignored signals are inherited. [105]
- 128+N: killed by signal N; 126 not executable; 127 not found. [125]
- Edited a unit: `daemon-reload`, then `restart`. [118]
:::

:::glossary
- **Signal**: a short numbered message the kernel delivers to a process, such as "please stop".
- **Disposition**: what a process does when a given signal arrives: the default, ignore it, or run a handler.
- **Zombie**: a process that has exited but whose parent has not yet collected its exit status.
- **Exit status**: the number a command returns; 0 means success.
- **Unit**: anything systemd manages, described by a unit file such as `vmapi.service`.
- **Journal**: systemd's log store, read with `journalctl`.
:::
