#!/bin/bash
# check: prints PASS or FAIL for each of the seven faults in the broken box.
# Installed as /usr/local/bin/check. Run it as root inside the container: check
# Each test runs as the user named in the symptom, because root skips most
# permission checks and would hide the fault.
set -u

passed=0
total=7

result() {
  # result NUMBER NAME OK HINT
  if [ "$3" = ok ]; then
    printf 'PASS  %s  %s\n' "$1" "$2"
    passed=$((passed + 1))
  else
    printf 'FAIL  %s  %s\n        %s\n' "$1" "$2" "$4"
  fi
}

as_user() {
  # as_user USER COMMAND...: run a command as another user, from /
  local user=$1
  shift
  (cd / && setpriv --reuid "$user" --regid "$user" --init-groups "$@")
}

http_get() {
  # http_get HOST PORT PATH: print the raw HTTP response, using bash's /dev/tcp
  (
    exec 3<>"/dev/tcp/$1/$2" || exit 1
    printf 'GET %s HTTP/1.0\r\nHost: %s\r\n\r\n' "$3" "$1" >&3
    timeout 3 cat <&3
  ) 2>/dev/null
}

# 1. vmapi starts and runs as its own user.
ok=no
pid=$(cat /run/vmapi.pid 2>/dev/null || true)
mode=$(stat -c %a /opt/vmapi/vmapi.py)
if [ -n "$pid" ] && [ -d "/proc/$pid" ] \
   && [ "$(ps -o user= -p "$pid" | tr -d ' ')" = vmapi ] \
   && [ $((8#$mode & 8#022)) -eq 0 ]; then
  ok=ok
fi
result 1 "vmapi is running as user vmapi" "$ok" \
  "vmapi-ctl start must succeed; the program must be executable and not writable by group or others"

# 2. vmapi is reachable on the container's own address, not only on loopback.
ok=no
addr=$(ip -4 -br addr show eth0 2>/dev/null | awk '{print $3}' | cut -d/ -f1)
if [ -n "$addr" ] && ss -ltn | awk '{print $4}' | grep -qx '0.0.0.0:8080' \
   && http_get "$addr" 8080 /healthz | head -n 1 | grep -q ' 200 '; then
  ok=ok
fi
result 2 "vmapi answers on ${addr:-eth0}:8080" "$ok" \
  "ss -ltnp shows where it listens; a request to the eth0 address must get HTTP 200 from /healthz"

# 3. The old worker is gone, and its script now stops on SIGTERM.
ok=no
if ! pgrep -f worker-v1.sh >/dev/null; then
  bash /opt/worker/worker-v1.sh >/dev/null 2>&1 &
  wpid=$!
  sleep 0.5
  kill -TERM "$wpid" 2>/dev/null
  for _ in $(seq 1 70); do
    kill -0 "$wpid" 2>/dev/null || break
    sleep 0.1
  done
  if kill -0 "$wpid" 2>/dev/null; then
    kill -KILL "$wpid" 2>/dev/null
  else
    ok=ok
  fi
  wait "$wpid" 2>/dev/null
fi
result 3 "worker-v1 is stopped and stops on SIGTERM" "$ok" \
  "no worker-v1.sh process may be left, and the script must exit within 7 s of SIGTERM"

# 4. No zombies, and the dispatcher now reaps its children.
ok=no
if [ "$(ps -eo stat= | grep -c '^Z')" -eq 0 ]; then
  python3 /opt/dispatcher/dispatcher.py >/dev/null 2>&1 &
  dpid=$!
  sleep 3.5
  zombies=$(ps -o stat= --ppid "$dpid" | grep -c '^Z')
  kill -KILL "$dpid" 2>/dev/null
  wait "$dpid" 2>/dev/null
  [ "$zombies" -eq 0 ] && ok=ok
fi
result 4 "no zombie processes, dispatcher reaps its children" "$ok" \
  "ps must show no Z processes, and a fresh dispatcher.py must leave no zombie children"

# 5. The job spool has free inodes and still holds the 20 queued jobs.
ok=no
spool=/var/spool/vmjobs
if ! mountpoint -q "$spool"; then
  hint="the spool is not a separate filesystem: start the container with the --tmpfs option from the lesson"
else
  hint="new files must be creatable in $spool/incoming, and the 20 queued jobs must still be there"
  iuse=$(df --output=ipcent "$spool" | tail -n 1 | tr -d ' %')
  jobs=$(find "$spool/incoming" -name 'job-*.json' | wc -l)
  probe="$spool/incoming/.check-$$"
  if [ "$iuse" -lt 50 ] && [ "$jobs" -eq 20 ] && : >"$probe" 2>/dev/null; then
    ok=ok
  fi
  rm -f "$probe"
fi
result 5 "the job spool can take new jobs" "$ok" "$hint"

# 6. The nightly report reads its input directory as user report.
ok=no
good_status=0
as_user report /opt/report/nightly.sh >/dev/null 2>&1 || good_status=$?
out=/srv/reports/out/running-vms.txt
inmode=$(stat -c %a /srv/reports/in)
if [ "$good_status" -eq 0 ] \
   && grep -Eq '^ *2 hv01$' "$out" && grep -Eq '^ *3 hv02$' "$out" \
   && [ $((8#$inmode & 8#002)) -eq 0 ]; then
  ok=ok
fi
result 6 "nightly report as user report counts 2 hv01 and 3 hv02" "$ok" \
  "as user report the script must read /srv/reports/in; the directory must not be writable by others"

# 7. The nightly report fails loudly on bad input (strict mode).
ok=no
missing_status=0
as_user report /opt/report/nightly.sh /nonexistent >/dev/null 2>&1 || missing_status=$?
empty=$(mktemp -d /tmp/check-empty.XXXX)
chmod 0755 "$empty"
empty_status=0
as_user report /opt/report/nightly.sh "$empty" >/dev/null 2>&1 || empty_status=$?
rmdir "$empty"
if [ "$missing_status" -ne 0 ] && [ "$empty_status" -ne 0 ]; then
  ok=ok
fi
result 7 "nightly report exits non-zero on a missing or empty input directory" "$ok" \
  "a run on /nonexistent (needs set -e) and a run on a directory without .csv files (needs pipefail) must both fail"

# Check 7 overwrote the report with an empty file; write the real one again.
as_user report /opt/report/nightly.sh >/dev/null 2>&1 || true

echo "$passed/$total passed"
[ "$passed" -eq "$total" ]
