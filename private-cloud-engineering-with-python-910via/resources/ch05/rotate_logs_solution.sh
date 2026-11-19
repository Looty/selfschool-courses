#!/bin/bash
# rotate_logs.sh LOG_DIR [KEEP]: reference solution.
# Rotates every LOG_DIR/*.log: NAME.log -> NAME.log.1 -> ... -> NAME.log.KEEP,
# by copy-then-truncate. Full specification: rotate_logs_starter.sh.
set -euo pipefail

usage() {
  echo "usage: rotate_logs.sh LOG_DIR [KEEP]" >&2
  exit 2
}

[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage
log_dir=$1
keep=${2:-3}

case $keep in
  '' | *[!0-9]* | 0*)
    echo "rotate_logs.sh: KEEP must be a positive integer, got '$keep'" >&2
    exit 2
    ;;
esac

if [ ! -d "$log_dir" ]; then
  echo "rotate_logs.sh: not a directory: $log_dir" >&2
  exit 1
fi

rotate_one() {
  local log=$1
  local i
  rm -f -- "$log.$keep"
  for ((i = keep - 1; i >= 1; i--)); do
    if [ -e "$log.$i" ]; then
      mv -- "$log.$i" "$log.$((i + 1))"
    fi
  done
  cp -p -- "$log" "$log.1"
  : >"$log"
}

shopt -s nullglob
count=0
for log in "$log_dir"/*.log; do
  [ -f "$log" ] || continue
  rotate_one "$log"
  count=$((count + 1))
done

echo "rotated $count file(s)"

# Cost: O(F * KEEP) renames for F log files; memory O(1) apart from the glob list.
# Alternative: logrotate(8) with "copytruncate" and "rotate KEEP" does the same job
# from a config file; a script like this one is for boxes where it is not installed.
