---
id: l19
title: "Images, layers and Dockerfiles"
quiz: quiz-02.yaml
resources: [../resources/ch07/Dockerfile, ../resources/ch07/Dockerfile.bad, ../resources/ch07/.dockerignore, ../resources/ch07/requirements.txt, ../resources/ch07/app/service.py]
sources: [68, 69, 70, 71, 72, 73, 74, 79, 80, 105, 125]
---
After this lesson you can explain how image layers and copy-on-write work, order a Dockerfile so the cache helps, and review a Dockerfile line by line for size, secrets, signals and pinning.

## Shortcut

From the `ch07` resources folder (the service is a 70-line HTTP server with `/`, `/health` and `/metrics`):

```bash
docker build -t pce-ch07-good:1 --build-arg APP_VERSION=1.0.0 .
docker build -f Dockerfile.bad -t pce-ch07-bad:1 .
docker image ls --format '{{.Repository}}:{{.Tag}} {{.Size}}' | grep pce-ch07
docker run -d --name pce-ch07-good -p 18000:8000 pce-ch07-good:1
curl -s http://localhost:18000/
docker rm -f pce-ch07-good
```

In the course's test run (Docker Engine 29.9.1):

```text
pce-ch07-bad:1 1.68GB
pce-ch07-good:1 199MB
{"service": "pce-ch07-service", "host": "4ba1445956b1", "version": "1.0.0", "pid": 1}
```

Same service, same dependency, 8.4 times the size. `"pid": 1` matters later.

## Layers and copy-on-write

An image is a stack of read-only layers, one per instruction that changes the filesystem (`FROM`, `COPY`, `RUN`); `CMD`, `LABEL` and similar only change metadata [68]. Each layer stores differences from the one below, so deleting a file in a later layer does not shrink the image [68]. A container adds one thin writable layer on top; that layer is the only difference between a container and its image, and it is deleted with the container [68].

Copy-on-write: a read uses the file where it lies; the first write copies the whole file up into the writable layer and changes the copy [68]. With OverlayFS the image layers are the `lowerdir`, the container layer is the `upperdir`, and the combined view is `merged` [69]. Deleting a file from an image layer writes a whiteout file in `upperdir`, which hides the file without removing it; deleting a directory writes an opaque directory [69].

Docker Engine 29 uses the containerd image store by default on fresh installs, with an `overlayfs` snapshotter instead of the classic `overlay2` driver; the concepts hold, the paths differ [68] [70]. The test machine shows exactly that:

```bash
docker run --rm --entrypoint sh pce-ch07-good:1 -c 'grep "^overlay / " /proc/mounts'
```

```text
overlay / overlay rw,relatime,lowerdir=/var/lib/desktop-containerd/daemon/io.containerd.snapshotter.v1.overlayfs/snapshots/949/fs:...,upperdir=...,workdir=...
```

Deleting `/app/service.py` as root in one container left `/app` empty there, while a new container from the same image still listed `service.py`.

## Cache order

Each instruction is checked against the cache in order; once one layer changes, every later layer is rebuilt [74]. So copy dependency files first, install, then copy source [74]. The good Dockerfile does that. Editing only `service.py` in the test run:

```text
#13 [build 5/6] RUN pip install --no-cache-dir -r requirements.txt
#13 CACHED
#14 [build 6/6] COPY app/ ./app/
#14 DONE 0.0s
```

Changing `requirements.txt` re-ran `pip install` (1.3 s) and everything after it. A cold build took 6.7 s, a cached one 3.2 s.

## The instructions that matter

| Topic | Rule |
| --- | --- |
| `COPY` vs `ADD` | `COPY` copies from the context or a stage; `ADD` can also fetch URLs and Git repos and auto-extracts local tar files [71] [72]. Default to `COPY`. |
| `ARG` vs `ENV` | `ARG` exists only at build time and shows in `docker history`; `ENV` persists in the image and in `docker inspect` [71]. Neither is for secrets; use `RUN --mount=type=secret` [71]. |
| `USER` | Applies to later `RUN`, `CMD` and `ENTRYPOINT` [71]; create the user first with `groupadd -r` / `useradd -r` [72]. Files from `COPY` are owned by root unless you pass `--chown` [71]. |
| `HEALTHCHECK` | Defaults: interval 30s, timeout 30s, start period 0s, retries 3; status goes `starting`, `healthy`, `unhealthy` [71]. |
| Multi-stage | Each `FROM` starts a stage; `COPY --from=build` takes only the artefacts [73]. |
| `.dockerignore` | Keeps files out of the build context, like `.gitignore` [72] [74]. |
| Pinning | Tags move; a digest (`image@sha256:...`) does not, at the cost of applying updates yourself [72]. |
| apt | `apt-get update && apt-get install ...` in one `RUN`, then `rm -rf /var/lib/apt/lists/*` [72]. |

### CMD and ENTRYPOINT

What actually runs, per the Dockerfile reference [71].

| | no `ENTRYPOINT` | `ENTRYPOINT e p` (shell) | `ENTRYPOINT ["e","p"]` (exec) |
| --- | --- | --- | --- |
| `CMD ["c","p"]` | `c p` | `/bin/sh -c e p` | `e p c p` |
| `CMD c p` (shell) | `/bin/sh -c c p` | `/bin/sh -c e p` | `e p /bin/sh -c c p` |

Arguments to `docker run` replace `CMD` and are appended to an exec-form `ENTRYPOINT` [71]. A shell-form `ENTRYPOINT` ignores both [71]. The test run proved it the hard way: `docker run pce-ch07-bad:1 python --version` started the web server and never printed a version.

## PID 1 and `docker stop`

`docker stop` sends SIGTERM to the container's main process, then SIGKILL after a grace period [79]. With a shell-form `ENTRYPOINT` the main process is `/bin/sh -c`, which does not pass signals on, so the app never sees SIGTERM [71]. The fixes are exec form, or `exec` in a wrapper script (`exec "$@"`) [71] [72]. `docker run --init` puts a small init (tini) at PID 1 that forwards signals and reaps zombies [80]. Measured with `docker stop -t 10`:

| Image | Stop time | Exit | Log |
| --- | --- | --- | --- |
| good (exec form, Python is PID 1) | 0.42 s | 0 | `SIGTERM received, shutting down` |
| bad (shell form) | 10.5 s | 137 | nothing |
| bad with `--init` | 0.47 s | 143 | nothing |

137 is SIGKILL (9) and 143 is SIGTERM (15), each plus 128 [105] [125]. `--init` stopped it fast, but the exit was 143 and the app's `SIGTERM received` line never appeared, so its own shutdown code did not run. Exec form is the real fix.

## Reviewing `Dockerfile.bad`

| Line | Problem | Good version |
| --- | --- | --- |
| 1 `FROM python:latest` | unpinned; resolved to Python 3.15.2 in the test run, full Debian | `python:3.13-slim-bookworm`, plus a digest for repeatability [72] |
| 2 `ADD . /app` | copies the whole context first, so every edit busts the cache [74] | `COPY requirements.txt` then `COPY app/` |
| 4-5 | separate `apt-get update`, unneeded compilers, no list cleanup [72] | none needed in the runtime stage |
| 7 `ENV API_TOKEN=...` | secret baked into the image; `docker inspect` printed it [71] | pass at run time |
| 8 `RUN rm -rf /root/.cache` | cannot shrink the 12.2 MB pip layer below it [68] | `pip install --no-cache-dir` |
| 10 shell-form `ENTRYPOINT` | ignores SIGTERM and arguments [71] | exec form |
| (missing) `USER` | runs as root | `USER app` [72] |

BuildKit flagged line 10 itself: `JSONArgsRecommended: JSON arguments recommended for ENTRYPOINT to prevent unintended behavior related to OS signals`.

## Gotchas

- **`rm` in a later layer.** The bytes stay in the earlier layer; clean up in the same `RUN` that created them. [68]
- **Secrets in `ARG` or `ENV`.** Both are readable from the image (`docker history`, `docker inspect`). [71]
- **`latest` in `FROM`.** Your next build may get a new major Python with no change in your repo. [72]
- **`COPY . .` before installing.** One changed source file reinstalls every dependency. [74]
- **`EXPOSE` publishes nothing.** It is documentation; `-p` publishes. [71]
- **Shell-form `ENTRYPOINT`.** Slow stops ending in 137, and `docker run IMAGE args` silently ignored. [71] [79]

:::low-confidence
Without `-t`, `docker stop` on the shell-form image ended with SIGKILL after about 3.4 seconds on the test machine, while the docs give a 10 second default for Linux containers [79]. The container's `StopTimeout` was unset, so the shorter wait came from this Docker Desktop install. Use `docker stop -t 10` when you want to reproduce the table above.
:::

:::key-takeaways
- Layers are read-only diffs; a container adds one writable layer; writes copy up, deletes write whiteouts. [68] [69]
- Order instructions from least to most frequently changed; a changed layer rebuilds everything after it. [74]
- Multi-stage plus a slim pinned base and no build tools: 199 MB against 1.68 GB here. [72] [73]
- Exec-form `ENTRYPOINT`/`CMD` makes the app PID 1 so `docker stop` can stop it cleanly. [71] [79]
- `ARG` and `ENV` are not secret stores. [71]
:::

:::glossary
- **Layer**: one read-only set of file changes in an image, produced by one build instruction.
- **Copy-on-write**: a file is shared until something writes to it, and only then copied for the writer.
- **Whiteout**: a marker file in the upper layer that hides a file from a lower layer.
- **Build context**: the set of files sent to the builder, normally the folder named at the end of `docker build`.
- **Multi-stage**: a Dockerfile with several `FROM` lines where the final image copies only what it needs from earlier stages.
- **Exec form**: an instruction written as a JSON list, run directly without a shell.
- **Shell form**: an instruction written as plain text, run through `/bin/sh -c`.
- **Digest**: a content hash that names one exact image, unlike a tag, which can be moved.
- **tini**: a tiny init program used by `--init` to forward signals and reap finished child processes.
:::
