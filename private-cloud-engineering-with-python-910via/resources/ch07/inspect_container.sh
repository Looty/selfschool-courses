#!/usr/bin/env bash
# Show that a container is a process with namespaces and cgroup limits.
# Runs on Linux, macOS or Windows (Git Bash) with Docker. Usage: bash inspect_container.sh
set -euo pipefail
export MSYS_NO_PATHCONV=1          # stop Git Bash rewriting /proc and /sys paths

NAME=pce-ch07-demo
IMAGE=python:3.13-slim-bookworm
HELPER=debian:bookworm-slim

docker rm -f "$NAME" >/dev/null 2>&1 || true
docker run -d --name "$NAME" --hostname demo \
  --memory 128m --memory-swap 128m --cpus 0.5 --pids-limit 64 \
  "$IMAGE" sleep 600 >/dev/null

echo "== inside: hostname, PIDs visible, and PID 1"
docker exec "$NAME" sh -c 'hostname; ls /proc | grep -E "^[0-9]+$" | tr "\n" " "; echo; cat /proc/1/cmdline | tr "\0" " "; echo'

echo "== inside: namespaces of PID 1"
docker exec "$NAME" ls -l /proc/1/ns

echo "== inside: cgroup membership and limit files"
docker exec "$NAME" sh -c 'cat /proc/self/cgroup
for f in memory.max memory.high memory.swap.max cpu.max pids.max; do printf "%-16s %s\n" "$f" "$(cat /sys/fs/cgroup/$f)"; done
echo "memory.events:"; cat /sys/fs/cgroup/memory.events'

PID=$(docker inspect -f '{{.State.Pid}}' "$NAME")
echo "== outside: the same process is PID $PID on the Docker host"

# A helper container that shares the host PID and cgroup namespaces.
docker run --rm --pid=host --cgroupns=host --privileged "$HELPER" sh -c "
  echo '-- host view of the container process:'; cat /proc/$PID/cmdline | tr '\0' ' '; echo
  echo '-- its namespaces (left) against host PID 1 (right):'
  for ns in cgroup ipc mnt net pid time user uts; do
    printf '%-7s %-22s %s\n' \$ns \$(readlink /proc/$PID/ns/\$ns) \$(readlink /proc/1/ns/\$ns)
  done
  CG=\$(cut -d: -f3 /proc/$PID/cgroup)
  echo \"-- its cgroup on the host: \$CG\"
  for f in memory.max cpu.max pids.max; do printf '%-12s %s\n' \$f \"\$(cat /sys/fs/cgroup\$CG/\$f)\"; done
"

docker rm -f "$NAME" >/dev/null
echo "== removed $NAME"

echo "== OOM inside a 64 MiB cgroup: a child process asks for 200 MiB"
# sh stays PID 1, so the container survives the kill and can print the counters.
docker run --rm --name "$NAME-oom" --memory 64m --memory-swap 64m "$IMAGE" sh -c '
  python -c "b = bytearray(b\"x\") * (200 * 1024 * 1024)"
  echo "python exit status: $?"
  cat /sys/fs/cgroup/memory.events' || true
