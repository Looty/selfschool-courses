---
id: l18
title: "What a container is: namespaces, cgroups and runtimes"
quiz: quiz-01.yaml
resources: [../resources/ch07/inspect_container.sh]
sources: [60, 61, 62, 63, 64, 65, 66, 78, 80, 83, 84, 85, 102, 103, 105, 125]
---
After this lesson you can show, on a running container, which namespaces isolate it and which cgroup files limit it, name the programs between `docker run` and the kernel, and compare a container with a VM in a few precise sentences.

## Run it first

`inspect_container.sh` starts a small container with limits, prints what the process sees from inside, then looks at the same process from the Docker host. It was tested in Git Bash on Windows; it is plain Bash and should also run on macOS and Linux (see the note at the end).

```bash
bash inspect_container.sh
```

It ran in 3.4 seconds in the course's test run (Docker Engine 29.9.1, Docker Desktop on a WSL2 6.6 kernel). The output is quoted section by section below.

## A container is a process

Docker's own definition: a container is an ordinary process that runs in isolation, with its own filesystem, its own view of processes, network interfaces and hostname, and optional limits on memory and CPU [102]. When you start a container, Docker creates a set of namespaces and control groups for it [65]. Namespaces decide what the process can see; control groups decide how much it can use.

```text
== inside: hostname, PIDs visible, and PID 1
demo
1 14 15 16 7
sleep 600
== outside: the same process is PID 12725 on the Docker host
-- host view of the container process:
sleep 600
```

Inside, `sleep` is PID 1 and only a handful of PIDs exist. On the host it is PID 12725, one process among hundreds.

## Namespaces: what the process can see

A namespace wraps a global resource so that the processes inside seem to have their own copy of it [60]. Linux has eight types [60].

| Namespace | Isolates |
| --- | --- |
| `cgroup` | the cgroup root directory |
| `ipc` | System V IPC and POSIX message queues |
| `mnt` | mount points |
| `net` | network devices, stacks, ports |
| `pid` | process IDs |
| `time` | boot and monotonic clocks |
| `user` | user and group IDs |
| `uts` | hostname and NIS domain name |

Every process has a `/proc/<pid>/ns/` directory with one symbolic link per type, whose target is the type plus an inode number; two processes are in the same namespace when those numbers match [60]. The script compares the container's process with host PID 1:

```text
-- its namespaces (left) against host PID 1 (right):
cgroup  cgroup:[4026532768]    cgroup:[4026531835]
ipc     ipc:[4026532766]       ipc:[4026532206]
mnt     mnt:[4026532764]       mnt:[4026532290]
net     net:[4026532769]       net:[4026532231]
pid     pid:[4026532767]       pid:[4026532291]
time    time:[4026532837]      time:[4026531834]
user    user:[4026531837]      user:[4026531837]
uts     uts:[4026532765]       uts:[4026532220]
```

Seven differ. The `user` namespace is shared with the host: Docker supports user namespaces, which map root in the container to an unprivileged host UID, but does not enable them by default [65]. Root in this container is still UID 0 on the host, held back by a reduced set of capabilities rather than by a different UID [65]. The kernel calls behind all this are `clone(2)`, `unshare(2)` and `setns(2)` [60].

## cgroups: how much it can use

A cgroup (control group) is a set of processes bound to limits; in cgroup v2 every process belongs to exactly one cgroup in a single hierarchy, and each limit is a file [61] [62]. The `docker run` flags `--memory`, `--cpus` and `--pids-limit` write those files [78] [80]. The script's container:

```bash
docker run -d --memory 128m --memory-swap 128m --cpus 0.5 --pids-limit 64 python:3.13-slim-bookworm sleep 600
```

```text
0::/
memory.max       134217728
memory.high      max
memory.swap.max  0
cpu.max          50000 100000
pids.max         64
```

| File | Meaning | Default |
| --- | --- | --- |
| `memory.max` | hard limit; at the limit the OOM killer runs inside the cgroup [62] | `max` |
| `memory.high` | throttle limit; going over it never invokes the OOM killer [62] | `max` |
| `cpu.max` | `$MAX $PERIOD` in microseconds [62] | `max 100000` |
| `pids.max` | process count; past it `fork()` fails with `EAGAIN` [62] | `max` |
| `memory.events` | counters: `max`, `oom`, `oom_kill` and others [62] | |

`--cpus 0.5` became `50000 100000`: 50 ms of CPU per 100 ms period, which is how Docker translates `--cpus` into a quota and period [78]. The `0::/` line from `/proc/self/cgroup` means the v2 hierarchy (ID 0) [61], and the path is `/` because the cgroup namespace gives the container its own cgroup root [60]. From the host the same cgroup is `/docker/47de3fc5...`; that prefix belongs to the `cgroupfs` cgroup driver, while hosts using the `systemd` driver place containers under `system.slice` [66].

The last section of the script runs a child process that asks for 200 MiB in a 64 MiB cgroup:

```text
python exit status: 137
Killed
max 20
oom 1
oom_kill 1
oom_group_kill 0
```

`oom_kill 1` counts the killed process [62]. Status 137 is 128 + 9: a process ended by signal N gets 128+N [125], and SIGKILL is 9 [105]. Exit 137 with `oom_kill` above zero means "hit the memory limit", not "crashed".

## From `docker` to the kernel

Docker Engine is a daemon, `dockerd`, an API, and the `docker` CLI that calls it [63]. The CLI talks to the daemon over a Unix socket, by default `/var/run/docker.sock` [66]. `dockerd` uses containerd to manage container lifecycles, and containerd uses runc as its runtime by default [64] [66]. runc is a low-level tool that starts a container from an OCI bundle: a `rootfs` directory plus a `config.json` [83]. The OCI (Open Container Initiative) writes the runtime specification that makes runc replaceable [84]. containerd also handles image transfer and storage, and can serve as a Kubernetes runtime through its CRI plugin [85].

```bash
docker info --format '{{.Driver}} {{.CgroupVersion}} {{.CgroupDriver}} {{.DefaultRuntime}}'
```

```text
overlayfs 2 cgroupfs runc
```

Other runtimes, such as gVisor or Kata Containers, can be chosen per container with `--runtime` [64].

## Containers versus VMs

| | Container | Virtual machine |
| --- | --- | --- |
| Kernel | shares the host kernel [102] | boots its own [102] |
| Start-up | about a second, no OS to boot [102] | an OS boot |
| Isolation boundary | the shared kernel [102] | the hypervisor's hardware boundary, stronger [102] |
| Contents | app plus dependencies, no guest OS [103] | full OS, virtual CPU, memory, disk [103] |

They are combined in practice: cloud servers are usually VMs running many containers, and Docker Desktop on Windows or macOS runs Linux containers inside a small Linux VM [102]. The test run above shows it: the kernel was a WSL2 kernel, not Windows.

## Gotchas

- **"Root in the container is safe."** Without user namespaces it is UID 0 on the host with fewer capabilities, and anyone who can reach the daemon can mount the host's `/` into a container. [65]
- **Reading `/proc/meminfo` for the limit.** In the course's test run a container started with `--memory 128m` still showed `MemTotal: 8132708 kB`, the whole Docker Desktop VM. Read `/sys/fs/cgroup/memory.max`, the hard limit. [62]
- **`memory.high` as a safety net.** It throttles and never OOM-kills; only `memory.max` triggers the OOM killer. [62]
- **Treating 137 as a crash.** Check `docker inspect -f '{{.State.OOMKilled}}'` and `memory.events` before reading code.
- **Expecting cgroups to isolate data.** They limit resources; they do not stop one container reading another's data. [65]

:::low-confidence
`inspect_container.sh` was run only on Docker Desktop for Windows (Git Bash, WSL2 kernel). The host-side half runs a privileged helper with `--pid=host` and `--cgroupns=host`. It worked on Docker Desktop in the test run; on a hardened host or a rootless daemon it may be refused. The `--cgroupns` flag is not covered by this course's sources; check `docker run --help` on your version.
:::

:::key-takeaways
- A container is a host process placed in new namespaces (what it sees) and a cgroup (what it may use). [65] [102]
- Same inode in `/proc/<pid>/ns/<type>` means same namespace. [60]
- `--memory`, `--cpus`, `--pids-limit` become `memory.max`, `cpu.max`, `pids.max`; `memory.events` records OOM kills. [62] [78]
- `docker` CLI to `dockerd` to containerd to runc; runc runs an OCI bundle. [64] [66] [83]
- VMs boot their own kernel behind a hypervisor; containers share one kernel. [102]
:::

:::glossary
- **Namespace**: a kernel feature that gives a group of processes their own private copy of one system resource, such as hostnames or process IDs.
- **cgroup (control group)**: a kernel group of processes that shares limits and usage accounting for memory, CPU and process count.
- **OOM killer**: the kernel routine that kills a process when memory runs out, or when a cgroup reaches its memory limit.
- **dockerd**: the long-running Docker daemon that the `docker` command sends requests to.
- **containerd**: a daemon that pulls images and supervises containers on behalf of higher-level tools.
- **runc**: the small program that actually creates the namespaces and cgroup and starts the container's first process.
- **OCI bundle**: a directory holding a root filesystem and a `config.json` that tells a runtime how to start a container.
- **Capabilities**: slices of root's power that the kernel can grant or remove one by one.
:::
