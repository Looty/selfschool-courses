---
id: l10
title: "Containers: namespaces, cgroups, images and Dockerfiles"
quiz: quiz-10.yaml
resources: [../resources/ch04/inspect_container.sh, ../resources/ch04/Dockerfile, ../resources/ch04/Dockerfile.bad, ../resources/ch04/.dockerignore, ../resources/ch04/requirements.txt, ../resources/ch04/app/service.py]
sources: [60, 61, 62, 64, 65, 66, 68, 71, 72, 73, 74, 78, 79, 80, 83, 102, 105, 125]
---
After this lesson you can say what a container is in kernel terms, read its cgroup limits, explain exit 137, and review a Dockerfile for cache order, secrets, signals and pinning.

## A container is a process

A container is an ordinary process that runs in isolation, with optional limits on memory and CPU [102]. Docker creates a set of namespaces and control groups for it [65]: namespaces decide what it can see, cgroups how much it can use. Unlike a VM it shares the host kernel, so it starts in about a second, but its isolation boundary is that shared kernel, weaker than a hypervisor's [102].

**Namespaces** give processes their own copy of a global resource: `pid`, `net`, `mnt`, `uts` (hostname), `ipc`, `user`, `cgroup`, `time` [60]. Same inode in `/proc/<pid>/ns/<type>` means same namespace [60]. Docker does not enable user namespaces by default, so root in a container is UID 0 on the host with fewer capabilities [65].

**cgroups** (v2) bind processes to limits; each limit is a file [61] [62]. `docker run --memory 128m --cpus 0.5 --pids-limit 64` writes them [78]. At `memory.max` the OOM killer runs; `cpu.max` is quota and period in microseconds; past `pids.max`, `fork()` fails [62].

```text
memory.max   134217728
cpu.max      50000 100000    # 50 ms per 100 ms period
pids.max     64
```

`memory.high` only throttles, never OOM-kills; `memory.events` counts `oom_kill` [62]. A process killed by signal N exits 128+N [125], and SIGKILL is 9 [105]. So **exit 137 plus `oom_kill` means the memory limit, not a crash**.

The chain: `docker` CLI to `dockerd` to containerd to runc, which starts an OCI bundle [64] [66] [83].

## Images and layers

An image is a stack of read-only layers, one per `FROM`, `COPY` or `RUN` [68]. Deleting a file in a later layer does not shrink the image [68]. A container adds one writable layer; the first write to a file copies it up there (copy-on-write) [68].

Once one layer changes, every later layer is rebuilt [74]. From `Dockerfile`:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # cached until requirements.txt changes
COPY app/ ./app/                                     # editing source rebuilds only from here
```

## Dockerfile rules

- `COPY`, not `ADD` (which also fetches URLs and unpacks tars) [71] [72].
- `ARG` shows in `docker history`, `ENV` in `docker inspect`: no secrets. Use `RUN --mount=type=secret` [71].
- `USER app`, or it runs as root [72]. Multi-stage `COPY --from=build` takes only artefacts [73].
- Pin the base; tags move, a digest (`image@sha256:...`) does not [72].

**CMD and ENTRYPOINT.** `docker run` arguments replace `CMD` and are appended to an exec-form `ENTRYPOINT` (`["python","app.py"]`); a shell-form `ENTRYPOINT` ignores both [71].

**PID 1.** `docker stop` sends SIGTERM, then SIGKILL after a grace period [79]. In shell form PID 1 is `/bin/sh -c`, which does not pass signals on [71]. With `docker stop -t 10`, exec form stopped in 0.42 s (exit 0); shell form took 10.5 s (exit 137). `--init` (tini) was fast but exited 143 without running the app's shutdown code [80]. Exec form is the fix.

## Exercise (25 min)

From `resources/ch04`:

1. `bash inspect_container.sh`: compare namespaces and cgroup files inside and outside.
2. `docker build -t pce-ch07-good:1 --build-arg APP_VERSION=1.0.0 .` and `docker build -f Dockerfile.bad -t pce-ch07-bad:1 .`
3. `docker image ls | grep pce-ch07` (test run: 199 MB against 1.68 GB).
4. Find the faults in `Dockerfile.bad` (base, copy order, apt, secret, `rm`, `ENTRYPOINT`, user), then read `Dockerfile` as the answer.

:::low-confidence
`inspect_container.sh` was run only on Docker Desktop for Windows. Its host-side half runs a privileged helper; on a hardened host or a rootless daemon it may be refused.
:::

:::key-takeaways
- A container is a host process in new namespaces (what it sees) and a cgroup (what it may use). [65] [102]
- `--memory`, `--cpus`, `--pids-limit` become `memory.max`, `cpu.max`, `pids.max`; 137 with `oom_kill` is the memory limit. [62] [78] [125]
- Order layers from least to most often changed; a changed layer rebuilds everything after it. [74]
- Exec-form `ENTRYPOINT` makes the app PID 1 so `docker stop` stops it cleanly. [71] [79]
- `ARG` and `ENV` are not secret stores. [71]
:::

:::glossary
- **Namespace**: a kernel feature that gives a group of processes their own private copy of one system resource.
- **cgroup (control group)**: a kernel group of processes that shares limits for memory, CPU and process count.
- **Exec form**: an instruction written as a JSON list, run directly without a shell.
:::
