#!/bin/bash
# vmapi-ctl: start, stop, restart or show the vmapi service.
# The box has no systemd, so this small script stands in for systemctl.
# Installed as /usr/local/bin/vmapi-ctl. Run it as root.
set -euo pipefail

BIN=/opt/vmapi/vmapi.py
PIDFILE=/run/vmapi.pid
LOG=/var/log/vmapi/vmapi.log

running() {
  [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null
}

start() {
  if running; then
    echo "vmapi is already running, pid $(cat "$PIDFILE")"
    return 0
  fi
  # setpriv drops from root to the vmapi user and then executes the program.
  setpriv --reuid vmapi --regid vmapi --init-groups "$BIN" >>"$LOG" 2>&1 &
  local pid=$!
  sleep 1
  if kill -0 "$pid" 2>/dev/null; then
    echo "$pid" >"$PIDFILE"
    echo "vmapi started, pid $pid"
  else
    local status=0
    wait "$pid" || status=$?
    echo "vmapi failed to start (exit status $status); see $LOG" >&2
    return 1
  fi
}

stop() {
  if ! running; then
    echo "vmapi is not running"
    rm -f "$PIDFILE"
    return 0
  fi
  local pid
  pid=$(cat "$PIDFILE")
  kill -TERM "$pid"
  local tries=0
  while kill -0 "$pid" 2>/dev/null; do
    tries=$((tries + 1))
    if [ "$tries" -gt 50 ]; then
      echo "vmapi did not stop after SIGTERM, sending SIGKILL" >&2
      kill -KILL "$pid"
      break
    fi
    sleep 0.1
  done
  rm -f "$PIDFILE"
  echo "vmapi stopped"
}

status() {
  if running; then
    echo "vmapi is running, pid $(cat "$PIDFILE")"
  else
    echo "vmapi is not running"
    return 3
  fi
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  restart) stop; start ;;
  status) status ;;
  *)
    echo "usage: vmapi-ctl {start|stop|restart|status}" >&2
    exit 2
    ;;
esac
