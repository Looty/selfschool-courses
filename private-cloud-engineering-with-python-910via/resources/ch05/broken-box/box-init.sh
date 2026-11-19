#!/bin/bash
# box-init: process 1 of the broken box. Installed as /usr/local/sbin/box-init.
# It creates the faults that only exist at run time, starts the box's
# "services", then sleeps. As process 1 it also collects the exit status of
# any process whose parent has gone away.
trap 'exit 0' TERM INT

SPOOL=/var/spool/vmjobs

# The job spool: 20 queued jobs that matter, plus stale session files.
mkdir -p "$SPOOL/incoming" "$SPOOL/sessions"
for n in $(seq 1 20); do
  printf '{"job": "create-vm", "id": %d}\n' "$n" >"$SPOOL/incoming/job-$(printf '%04d' "$n").json"
done

# Fault 5: a session cleaner that never ran. Only when the spool is its own
# small filesystem (see the docker run command in the lesson); otherwise
# this loop would fill the container's root filesystem.
if mountpoint -q "$SPOOL"; then
  n=0
  while { : >"$SPOOL/sessions/sess_$(printf '%06d' "$n")"; } 2>/dev/null; do
    n=$((n + 1))
  done
fi

# Fault 3: the old worker.
/opt/worker/worker-v1.sh >/var/log/worker-v1.log 2>&1 &
echo "$!" >/run/worker-v1.pid

# Fault 4: the dispatcher.
/usr/bin/python3 /opt/dispatcher/dispatcher.py >/var/log/dispatcher.log 2>&1 &

# Fault 1 shows up here; fault 2 is behind it.
/usr/local/bin/vmapi-ctl start >/var/log/vmapi/boot.log 2>&1

while :; do
  sleep 3600 &
  wait "$!"
done
