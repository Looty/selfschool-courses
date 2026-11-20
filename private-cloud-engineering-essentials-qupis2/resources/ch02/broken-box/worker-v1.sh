#!/bin/bash
# worker-v1: an old queue worker that was told never to stop in the middle of a job.
# Installed as /opt/worker/worker-v1.sh and started by box-init.
trap '' TERM

while :; do
  echo "$(date '+%F %T') worker-v1 polling the queue"
  sleep 5
done
