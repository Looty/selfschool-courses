---
id: l10
title: "Containers: namespaces, cgroups, images and Dockerfiles"
quiz: quiz-10.yaml
resources: [../resources/ch04/inspect_container.sh, ../resources/ch04/Dockerfile, ../resources/ch04/Dockerfile.bad, ../resources/ch04/.dockerignore, ../resources/ch04/requirements.txt, ../resources/ch04/app/service.py]
sources: [60, 62, 65, 68, 71, 74, 78, 79, 102, 105, 125]
---
After this lesson you can say what a container is in kernel terms, explain exit 137, order a Dockerfile for the cache, and say why exec form stops fast (Docker Engine 29.9).

## Namespaces vs cgroups: what it sees, how much it gets

**Rule:** a container is an ordinary host process [102]; **namespaces** decide what it can *see*, **cgroups** (control groups) decide how much it can *use* [65]. Hook: namespaces are the walls, cgroups are the meter.

```console
$ docker run --rm --hostname demo python:3.13-slim-bookworm \
    sh -c 'hostname; ls /proc | grep -E "^[0-9]+$" | tr "\n" " "'
demo                       # uts namespace: its own hostname
1 10 8 9                   # pid namespace: the shell is PID 1; 4 PIDs in total
$ docker run --rm --network none python:3.13-slim-bookworm ls /sys/class/net
lo                         # net namespace with no network: loopback only
$ docker run --rm --memory 128m --cpus 0.5 --pids-limit 64 python:3.13-slim-bookworm \
    cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/cpu.max /sys/fs/cgroup/pids.max
134217728                  # 128 MiB in bytes
50000 100000               # 50 ms of CPU per 100 ms period
64
$ docker run --rm --memory 128m python:3.13-slim-bookworm grep MemTotal /proc/meminfo
MemTotal:        8132716 kB   # edge case: /proc/meminfo ignores the limit
```

The flags write those cgroup files [62] [78].

| | Namespace | cgroup |
| --- | --- | --- |
| Controls | what the process sees | how much it may use |
| Examples | `pid`, `net`, `mnt`, `uts`, `user` [60] | `memory.max`, `cpu.max`, `pids.max` [62] |

**P1.** With `--pids-limit 5` a shell starts 8 background `sleep`s. Namespace or cgroup, and what fails?

:::answer
A cgroup limit: past `pids.max`, `fork()` fails; the test run printed `Cannot fork`.
:::

## Memory limit: exit 137 means OOM-killed

**Rule:** at `memory.max` the kernel's OOM (out of memory) killer sends SIGKILL; a process killed by signal N exits 128+N, and SIGKILL is 9, so 137 [62] [125] [105].

```console
$ docker run --name t1 --memory 64m python:3.13-slim-bookworm python -c "x = bytearray(20*1024*1024); print('fits')"
fits                                            # 20 MiB in 64 MiB: exit=0 OOMKilled=false
$ docker run --name t2 --memory 64m python:3.13-slim-bookworm python -c "x = bytearray(200*1024*1024)"
$ docker inspect -f 'exit={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}' t2
exit=137 OOMKilled=true                         # killed, no traceback
$ docker run --name t3 python:3.13-slim-bookworm python -c "raise KeyError('DB_HOST')"
KeyError: 'DB_HOST'                             # exit=1 OOMKilled=false: an app bug
```

Edge case: `memory.high` only throttles; it never OOM-kills [62].

| Exit | Cause | Clue |
| --- | --- | --- |
| 1 | uncaught exception | traceback in logs |
| 137 | SIGKILL (128 + 9) | `OOMKilled=true` |

**P2.** A container exits 137 with `OOMKilled=false`. Was it the memory limit?

:::answer
No. 137 is any SIGKILL, for example `docker stop` after the grace period.
:::

## Layers and cache order

**Rule:** an image is a stack of read-only layers, one per `FROM`, `COPY` or `RUN` [68]; once one layer changes, every later layer is rebuilt [74].

```dockerfile
FROM python:3.13-slim-bookworm
WORKDIR /app
COPY requirements.txt .
RUN cat requirements.txt > deps.txt && sleep 2   # stands in for pip install
COPY app/ ./app/
```

| Edit, then rebuild | first `COPY` | `RUN` (2 s) | `COPY app/` |
| --- | --- | --- | --- |
| `app/main.py` | CACHED | CACHED | rebuilt |
| `requirements.txt` | rebuilt | rebuilt, 2.3 s | rebuilt |
| `app/main.py`, with `COPY . .` as the first `COPY` | rebuilt | rebuilt, 2.2 s | (none) |

Edge case: deleting a file in a later layer does not shrink the image [68]. A 50 MB file created in one `RUN` and removed in the next grew a 183 MB base image to 231 MB.

**P3.** Why does `COPY . .` before `RUN pip install` reinstall everything on every code edit?

:::answer
Any source edit changes the `COPY . .` layer, so the install after it is rebuilt.
:::

## Exec form vs shell form: who is PID 1

**Rule:** `docker stop` sends SIGTERM to PID 1, then SIGKILL after a grace period [79]; in shell form PID 1 is `/bin/sh -c`, which does not pass the signal on [71].

```dockerfile
ENTRYPOINT ["python", "app.py"]    # exec form: python is PID 1
ENTRYPOINT python app.py           # shell form: /bin/sh -c is PID 1
```

Course test run, `docker stop -t 10`:

| Image | Stop time | Exit |
| --- | --- | --- |
| exec form | 0.42 s | 0 |
| shell form | 10.5 s | 137 |

Edge case: shell form also ignores `docker run` arguments [71].

**P4.** A container always takes the full grace period to stop and exits 137. What do you check first in its Dockerfile?

:::answer
Shell-form `ENTRYPOINT`: `/bin/sh` is PID 1 and never forwards SIGTERM.
:::

## Exercise (25 min)

From `resources/ch04`:

1. `bash inspect_container.sh`: compare namespaces and cgroup files inside and outside.
2. `docker build -t pce-ch07-good:1 --build-arg APP_VERSION=1.0.0 .` and `docker build -f Dockerfile.bad -t pce-ch07-bad:1 .`
3. `docker image ls | grep pce-ch07` (test run: 199 MB against 1.68 GB).
4. Find the faults in `Dockerfile.bad` (base, copy order, apt, secret, `rm`, `ENTRYPOINT`, user), then read `Dockerfile` as the answer.

:::low-confidence
`inspect_container.sh` was tested only on Docker Desktop for Windows; its privileged host-side half may be refused elsewhere.
:::

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| namespace / cgroup | sees / uses | `--cpus 0.5` → `50000 100000` |
| exit 137 | 128 + SIGKILL | with `OOMKilled=true`: memory limit |
| layer cache | change busts all later layers | edit source → only last `COPY` |
| exec form | app is PID 1, gets SIGTERM | stop 0.42 s, exit 0 |

## If you missed a quiz question

**If you thought** namespaces limit memory: reread "Namespaces vs cgroups". **R1.** Which one holds `memory.max`?

:::answer
cgroup.
:::

**If you thought** `rm` in a later layer shrinks the image: reread "Layers". **R2.** Does it?

:::answer
No; the bytes stay in the earlier layer.
:::

**If you thought** 137 means an app crash: reread "Exit 137". **R3.** What does an uncaught exception exit with?

:::answer
1, with a traceback.
:::

:::key-takeaways
- A container is a host process: namespaces set what it sees, cgroups what it uses. [65] [102]
- Exit 137 with `OOMKilled=true` is the memory limit, not a crash. [62] [125]
- Install dependencies before copying source; use exec-form `ENTRYPOINT`. [71] [74]
:::

:::glossary
- **Namespace**: a kernel feature that gives a group of processes their own private copy of one system resource.
- **cgroup (control group)**: a kernel group of processes that shares limits for memory, CPU and process count.
- **OOM (out of memory) killer**: the kernel routine that kills a process when a memory limit is reached.
- **Exec form**: an instruction written as a JSON list, run directly without a shell.
:::
