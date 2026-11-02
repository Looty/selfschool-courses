#!/usr/bin/env bash
# Lab 5: four troubleshooting scenarios, diagnosed only with the chapter's tools.
# Run from the resources folder. The memory limit and the small /data tmpfs are part of the lab:
#   docker run --rm -it --privileged --memory=300m --memory-swap=300m --tmpfs /data:size=64m \
#     -v "$PWD/lab5":/lab5 -w /lab5 debian:bookworm bash lab5-run.sh all
# Or start a shell with the same flags, run `bash lab5-run.sh setup`, then `bash lab5-run.sh start N`
# and investigate yourself. Needs internet once (apt and py-spy from PyPI).
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
say() { printf '\n$ %s\n' "$*"; bash -c "$*"; }
hdr() { printf '\n==================== %s ====================\n' "$*"; }
pid_of() { pgrep -f "python3 .*$1" | head -n 1; }

setup() {
  apt-get update -qq >/dev/null
  apt-get install -y -qq python3 python3-venv procps sysstat lsof strace iproute2 linux-perf >/dev/null 2>&1 \
    || apt-get install -y -qq python3 python3-venv procps sysstat lsof strace iproute2 >/dev/null
  python3 -m venv /opt/py-spy && /opt/py-spy/bin/pip install -q py-spy
  ln -sf /opt/py-spy/bin/py-spy /usr/local/bin/py-spy
  echo "setup done"
}

start() {
  case $1 in
    1) nohup python3 /lab5/cpu_hog.py >/tmp/s1.log 2>&1 & ;;
    2) nohup python3 /lab5/mem_leak.py >/tmp/s2.log 2>&1 & ;;
    3) (ulimit -n 256; nohup python3 /lab5/fd_leak.py >/tmp/s3.log 2>&1 &) ;;
    4) nohup python3 /lab5/log_writer.py /data/app.log >/tmp/s4.log 2>&1 &
       sleep 2; rm -f /data/app.log ;;  # "someone cleaned up the log"
  esac
  sleep 1; echo "scenario $1 started"
}

investigate() {
  case $1 in
    1) sleep 3
       say "uptime"
       say "nproc"
       say "vmstat 1 3"
       say "pidstat -u 1 1 | sort -k8 -n -r | head -n 4"
       P=$(pid_of cpu_hog)
       say "grep -E '^(State|Threads|voluntary|nonvoluntary)' /proc/$P/status"
       say "py-spy dump --pid $P"
       say "timeout 5 perf record -q -g -p $P -o /tmp/perf.data -- sleep 3 >/dev/null 2>&1 && perf report -q --stdio -i /tmp/perf.data 2>/dev/null | grep -v '^$' | head -n 8 || echo 'perf not available on this kernel'"
       ;;
    2) sleep 4
       P=$(pid_of mem_leak)
       say "grep -E '^(VmPeak|VmRSS|RssAnon|RssFile)' /proc/$P/status"
       say "cat /sys/fs/cgroup/memory.max /sys/fs/cgroup/memory.current"
       say "free -m"
       sleep 12
       say "tail -n 2 /tmp/s2.log"
       say "pgrep -f '[m]em_leak.py' || echo 'no leaking process left'"
       say "cat /sys/fs/cgroup/memory.events"
       say "grep -E '^(anon|file) ' /sys/fs/cgroup/memory.stat"
       say "dmesg 2>/dev/null | grep -iE 'oom|killed process' | tail -n 3 || echo 'dmesg not readable here'"
       ;;
    3) sleep 8
       P=$(pid_of fd_leak)
       say "tail -n 2 /tmp/s3.log"
       say "ls /proc/$P/fd | wc -l"
       say "grep 'Max open files' /proc/$P/limits"
       say "ss -tanp | grep -c 'pid=$P,'"
       say "ss -tanp state established | head -n 3"
       say "lsof -p $P 2>/dev/null | awk '{print \$5}' | sort | uniq -c | sort -rn | head -n 4"
       say "timeout 3 strace -f -e trace=connect,socket,accept4 -p $P 2>&1 | grep -m 3 EMFILE"
       ;;
    4) sleep 6
       say "df -h /data"
       say "du -sh /data"
       say "ls -la /data"
       say "lsof +L1 2>/dev/null | head -n 3"
       P=$(pid_of log_writer)
       say "ls -l /proc/$P/fd | grep deleted"
       say "tail -n 1 /tmp/s4.log"
       ;;
  esac
}

fix() {
  case $1 in
    1) kill "$(pid_of cpu_hog)"; echo "killed the hog (the real fix: restore the loop's exit condition)";;
    2) pkill -f mem_leak.py; echo "the real fix: bound the cache (an LRU with a maximum size)";;
    3) pkill -f fd_leak.py; echo "the real fix: close connections (use 'with socket.create_connection(...)')";;
    4) P=$(pid_of log_writer)
       FD=$(ls -l /proc/$P/fd | awk '/deleted/ {print $9}' | head -n 1)
       say "truncate -s 0 /proc/$P/fd/$FD && df -h /data"
       kill "$P"; echo "the real fix: rotate logs with copytruncate or signal the service to reopen its log";;
  esac
}

case ${1:-} in
  setup) setup;;
  start) start "$2";;
  investigate) investigate "$2";;
  fix) fix "$2";;
  all)
    setup
    for n in 1 2 3 4; do
      hdr "Scenario $n"; start $n; investigate $n; hdr "Scenario $n: fix"; fix $n; sleep 1
    done;;
  *) echo "usage: $0 setup | start N | investigate N | fix N | all"; exit 2;;
esac
