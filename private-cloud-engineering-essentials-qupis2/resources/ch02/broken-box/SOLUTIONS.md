# Broken box: solutions

Read this only after trying each fault yourself. Every command runs as root inside the box
(`docker exec -it pce-ch02-box bash`). Run `check` after each fix: exactly one more line turns to PASS.
The outputs below are from the course's test run (Docker 29.9.1, image built from `debian:bookworm-slim`,
Python 3.11.2 and bash 5.2 inside the box).

The fixes are given as one-line commands so that you can paste them. Making the same change with
`nano` or `vi` is just as good.

## Fault 1: vmapi does not start

Symptom and diagnosis:

```console
# cat /var/log/vmapi/boot.log
vmapi failed to start (exit status 126); see /var/log/vmapi/vmapi.log
# cat /var/log/vmapi/vmapi.log
setpriv: failed to execute /opt/vmapi/vmapi.py: Permission denied
# ls -l /opt/vmapi/vmapi.py
-rw-r--r-- 1 root root 2193 Nov 19 11:47 /opt/vmapi/vmapi.py
```

Exit status 126 means "found but not executable". The file has no `x` bit for anyone, so the
`vmapi` user cannot execute it. The owner (root) and the mode `644` keep it read-only for the service
user, which is right: a service must not be able to rewrite its own program.

Fix:

```console
# chmod 0755 /opt/vmapi/vmapi.py && vmapi-ctl start
vmapi started, pid 2165
# ps -o user,pid,cmd -p "$(cat /run/vmapi.pid)"
USER       PID CMD
vmapi     2165 /usr/bin/python3 /opt/vmapi/vmapi.py
```

Wrong fix: `chmod 777`. It starts, but now any user can replace the program that runs as `vmapi`,
and `check` fails on purpose.

## Fault 2: vmapi answers only on loopback

Diagnosis, layer by layer:

```console
# ss -ltn
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 0      5          127.0.0.1:8080      0.0.0.0:*
# ip -br addr
lo               UNKNOWN        127.0.0.1/8 ::1/128
eth0@if115       UP             172.17.0.2/16
```

The socket is bound to `127.0.0.1`, so only connections to loopback reach it. A request to the
`eth0` address (172.17.0.2 in the test run; use the one `ip -br addr` shows you) is refused:

```console
# (exec 3<>/dev/tcp/172.17.0.2/8080)
bash: connect: Connection refused
bash: line 1: /dev/tcp/172.17.0.2/8080: Connection refused
```

Fix: bind to all IPv4 addresses and restart.

```console
# sed -i 's/^bind = 127.0.0.1$/bind = 0.0.0.0/' /etc/vmapi/vmapi.conf
# vmapi-ctl restart
vmapi stopped
vmapi started, pid 2214
# ss -ltn
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 0      5            0.0.0.0:8080      0.0.0.0:*
```

`ss -ltnp` shows an empty Process column inside this container; the address column is what matters here.

## Fault 3: worker-v1 ignores SIGTERM

```console
# w=$(cat /run/worker-v1.pid); kill $w; sleep 2; ps -o pid,stat,cmd -p $w
  PID STAT CMD
 2056 S    /bin/bash /opt/worker/worker-v1.sh
# grep SigIgn /proc/$w/status
SigIgn:	0000000000004006
# grep -n trap /opt/worker/worker-v1.sh
4:trap '' TERM
```

`0x4006` has bits 1, 2 and 14 set: signals 2 (SIGINT), 3 (SIGQUIT) and 15 (SIGTERM) are ignored.
The script's `trap '' TERM` sets SIGTERM to "ignore". Bash ignores SIGINT and SIGQUIT in background
jobs it starts itself, which is why those two show up too.

Fix: stop the running copy with the signal it cannot ignore, then fix the script so the next copy
exits cleanly on SIGTERM.

```console
# kill -9 "$(cat /run/worker-v1.pid)"
# sed -i "s/^trap '' TERM\$/trap 'echo \"worker-v1 got SIGTERM, exiting\"; exit 0' TERM/" /opt/worker/worker-v1.sh
# sed -i 's/^  sleep 5$/  sleep 5 \& wait "$!"/' /opt/worker/worker-v1.sh
# cat /opt/worker/worker-v1.sh
#!/bin/bash
# worker-v1: an old queue worker that was told never to stop in the middle of a job.
# Installed as /opt/worker/worker-v1.sh and started by box-init.
trap 'echo "worker-v1 got SIGTERM, exiting"; exit 0' TERM

while :; do
  echo "$(date '+%F %T') worker-v1 polling the queue"
  sleep 5 & wait "$!"
done
```

Why the second `sed`: bash runs a trap only after the foreground command finishes. With a plain
`sleep 5`, SIGTERM waits up to five seconds (the test run measured 4.0 s). `wait` is interrupted by
the signal at once, so the trap runs immediately.

## Fault 4: zombies

```console
# ps -eo pid,ppid,stat,cmd | grep -E "dispatcher|defunct"
 2057     1 S    /usr/bin/python3 /opt/dispatcher/dispatcher.py
 2063  2057 Z    [python3] <defunct>
 2065  2057 Z    [python3] <defunct>
 2066  2057 Z    [python3] <defunct>
 2067  2057 Z    [python3] <defunct>
 2068  2057 Z    [python3] <defunct>
# kill -9 2063; ps -o pid,ppid,stat -p 2063
  PID  PPID STAT
 2063  2057 Z
```

`kill -9` changes nothing: a zombie has already exited. All five have the same parent, PID 2057,
which forks a child per job and never collects its exit status.

Fix the code first, then end the old parent. Its zombies pass to PID 1 (`box-init`), which collects them.

```console
# sed -i '/print("dispatched job/a\        os.waitpid(pid, 0)' /opt/dispatcher/dispatcher.py
# grep -n -A1 'dispatched job' /opt/dispatcher/dispatcher.py
25:        print("dispatched job %d to pid %d" % (number, pid), flush=True)
26-        os.waitpid(pid, 0)
# kill "$(pgrep -xf '/usr/bin/python3 /opt/dispatcher/dispatcher.py')"
# sleep 1; ps -eo stat | grep -c '^Z'
0
```

`os.waitpid(pid, 0)` blocks until that child exits and collects its status. Here each job takes
0.2 s, so waiting in line is fine. A dispatcher with long jobs would instead collect finished
children with `os.waitpid(-1, os.WNOHANG)` in its main loop, or use `subprocess` or
`concurrent.futures`, which collect for you.

## Fault 5: "No space left on device" with free space

```console
# touch /var/spool/vmjobs/incoming/job-0021.json
touch: cannot touch '/var/spool/vmjobs/incoming/job-0021.json': No space left on device
# df -h /var/spool/vmjobs
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           4.0M   80K  4.0M   2% /var/spool/vmjobs
# df -i /var/spool/vmjobs
Filesystem     Inodes IUsed IFree IUse% Mounted on
tmpfs            2048  2048     0  100% /var/spool/vmjobs
# du -s --inodes /var/spool/vmjobs/*
21	/var/spool/vmjobs/incoming
2026	/var/spool/vmjobs/sessions
```

Blocks are free; inodes are not. 2026 empty session files use them all. Delete the stale sessions,
not the queued jobs:

```console
# find /var/spool/vmjobs/sessions -type f -name 'sess_*' -delete
# df -i /var/spool/vmjobs
Filesystem     Inodes IUsed IFree IUse% Mounted on
tmpfs            2048    23  2025    2% /var/spool/vmjobs
# ls /var/spool/vmjobs/incoming | wc -l
20
```

## Fault 6: the nightly report is empty

Run it as the user that runs it every night, not as root (root skips the permission check):

```console
# (cd / && setpriv --reuid report --regid report --init-groups /opt/report/nightly.sh; echo "exit=$?")
/opt/report/nightly.sh: line 11: cd: /srv/reports/in: Permission denied
cat: '*.csv': No such file or directory
report written: /srv/reports/out/running-vms.txt
exit=0
# ls -ld /srv/reports/in
drwx------ 2 root report 4096 Nov 19 12:19 /srv/reports/in
# id report
uid=1000(report) gid=1000(report) groups=1000(report)
```

The directory belongs to group `report`, but the group bits are `---`: no `r` to list it, no `x` to
enter it. Give the group read and search, nothing to others:

```console
# chmod 0750 /srv/reports/in
# (cd / && setpriv --reuid report --regid report --init-groups /opt/report/nightly.sh; echo "exit=$?")
report written: /srv/reports/out/running-vms.txt
exit=0
# cat /srv/reports/out/running-vms.txt
      2 hv01
      3 hv02
```

Wrong fix: `chmod 777 /srv/reports/in`. It works, and lets every user add or delete input files.

## Fault 7: the nightly report "succeeds" on bad input

Before the fix, both bad runs print "report written" and exit 0:

```console
# (cd / && setpriv --reuid report --regid report --init-groups /opt/report/nightly.sh /nonexistent; echo "exit=$?")
/opt/report/nightly.sh: line 11: cd: /nonexistent: No such file or directory
cat: '*.csv': No such file or directory
report written: /srv/reports/out/running-vms.txt
exit=0
```

Two problems: the failed `cd` does not stop the script, and the pipeline's status is that of
`uniq`, the last command, which succeeds on empty input. Turn on strict mode:

```console
# sed -i 's/^IN_DIR=/set -euo pipefail\n\nIN_DIR=/' /opt/report/nightly.sh
# mkdir -p /tmp/empty && chmod 755 /tmp/empty
# (cd / && setpriv --reuid report --regid report --init-groups /opt/report/nightly.sh /nonexistent; echo "exit=$?")
/opt/report/nightly.sh: line 13: cd: /nonexistent: No such file or directory
exit=1
# (cd / && setpriv --reuid report --regid report --init-groups /opt/report/nightly.sh /tmp/empty; echo "exit=$?")
cat: '*.csv': No such file or directory
exit=1
```

`set -e` stops at the failed `cd`; `pipefail` makes the pipeline fail when `cat` fails, even though
`uniq` succeeded.

One problem remains, and `check` does not test it: the shell opens `> "$OUT"` before the pipeline
runs, so a failed run still leaves an empty report behind. A sturdier script writes to
`"$OUT.tmp"` and renames it with `mv` only after the pipeline succeeded.

## Final check

```console
# check
PASS  1  vmapi is running as user vmapi
PASS  2  vmapi answers on 172.17.0.2:8080
PASS  3  worker-v1 is stopped and stops on SIGTERM
PASS  4  no zombie processes, dispatcher reaps its children
PASS  5  the job spool can take new jobs
PASS  6  nightly report as user report counts 2 hv01 and 3 hv02
PASS  7  nightly report exits non-zero on a missing or empty input directory
7/7 passed
```

Clean up on the host:

```bash
docker rm -f pce-ch02-box
docker rmi pce-ch02-broken-box
```
