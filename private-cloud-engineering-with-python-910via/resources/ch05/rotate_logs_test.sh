#!/bin/bash
# Tests for rotate_logs.sh.
# Usage: bash rotate_logs_test.sh [SCRIPT]
#   SCRIPT defaults to rotate_logs_starter.sh (your file);
#   bash rotate_logs_test.sh rotate_logs_solution.sh tests the reference.
set -u

TARGET=${1:-rotate_logs_starter.sh}
if [ ! -f "$TARGET" ]; then
  echo "no such file: $TARGET" >&2
  exit 2
fi
TARGET=$(cd "$(dirname "$TARGET")" && pwd)/$(basename "$TARGET")

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
passed=0
failed=0

# run ARGS...: runs the target; sets $status, $out (stdout) and $err (stderr).
run() {
  status=0
  out=$(bash "$TARGET" "$@" 2>"$WORK/stderr") || status=$?
  err=$(cat "$WORK/stderr")
}

# fresh: prints the path of a new, empty log directory.
fresh() {
  local dir
  dir=$(mktemp -d "$WORK/logs.XXXX")
  echo "$dir"
}

check() {
  local name=$1
  shift
  if "$@"; then
    echo "ok    $name"
    passed=$((passed + 1))
  else
    echo "FAIL  $name   (status=$status, stdout='$out', stderr='$err')"
    failed=$((failed + 1))
  fi
}

t_strict_mode_line() {
  status=- out=- err=-
  grep -Eq '^[[:space:]]*set -euo pipefail([[:space:]]|$)' "$TARGET"
}

t_no_args() {
  run
  [ "$status" -eq 2 ] && [[ $err == usage:* ]] && [[ $out != *rotated* ]]
}

t_too_many_args() {
  local d
  d=$(fresh)
  echo x >"$d/a.log"
  run "$d" 3 extra
  [ "$status" -eq 2 ] && [ "$(cat "$d/a.log")" = x ] && [ ! -e "$d/a.log.1" ]
}

t_bad_keep() {
  local d k
  d=$(fresh)
  echo x >"$d/a.log"
  for k in 0 abc -1 07; do
    run "$d" "$k"
    [ "$status" -eq 2 ] || return 1
  done
  [ ! -e "$d/a.log.1" ]
}

t_missing_dir() {
  run "$WORK/no such dir"
  [ "$status" -eq 1 ] && [ -n "$err" ] && [[ $out != *rotated* ]]
}

t_empty_dir() {
  local d
  d=$(fresh)
  run "$d"
  [ "$status" -eq 0 ] && [ "$(printf '%s\n' "$out" | tail -n 1)" = "rotated 0 file(s)" ]
}

t_one_log() {
  local d
  d=$(fresh)
  printf 'line one\nline two\n' >"$d/api.log"
  echo keep >"$d/notes.txt"
  run "$d"
  [ "$status" -eq 0 ] \
    && [ "$(printf '%s\n' "$out" | tail -n 1)" = "rotated 1 file(s)" ] \
    && [ -f "$d/api.log" ] && [ ! -s "$d/api.log" ] \
    && [ "$(cat "$d/api.log.1")" = "$(printf 'line one\nline two')" ] \
    && [ "$(cat "$d/notes.txt")" = keep ] && [ ! -e "$d/notes.txt.1" ]
}

t_keep_limit() {
  local d n
  d=$(fresh)
  for n in 1 2 3 4; do
    echo "gen $n" >"$d/api.log"
    run "$d" 2
    [ "$status" -eq 0 ] || return 1
  done
  [ "$(cat "$d/api.log.1")" = "gen 4" ] && [ "$(cat "$d/api.log.2")" = "gen 3" ] \
    && [ ! -e "$d/api.log.3" ]
}

t_default_keep_is_3() {
  local d n
  d=$(fresh)
  for n in 1 2 3 4 5; do
    echo "gen $n" >"$d/api.log"
    run "$d"
  done
  [ "$status" -eq 0 ] && [ "$(cat "$d/api.log.3")" = "gen 3" ] && [ ! -e "$d/api.log.4" ]
}

t_spaces_and_count() {
  local d
  d=$(fresh)
  echo a >"$d/my app.log"
  echo b >"$d/worker.log"
  run "$d"
  [ "$status" -eq 0 ] && [ "$(printf '%s\n' "$out" | tail -n 1)" = "rotated 2 file(s)" ] \
    && [ "$(cat "$d/my app.log.1")" = a ] && [ "$(cat "$d/worker.log.1")" = b ]
}

t_same_inode() {
  local d before after
  d=$(fresh)
  echo a >"$d/api.log"
  before=$(stat -c %i "$d/api.log")
  run "$d"
  after=$(stat -c %i "$d/api.log")
  [ "$status" -eq 0 ] && [ "$before" = "$after" ]
}

check "script contains: set -euo pipefail" t_strict_mode_line
check "no arguments: usage on stderr, exit 2" t_no_args
check "three arguments: exit 2, nothing rotated" t_too_many_args
check "KEEP 0, abc, -1 or 07: exit 2" t_bad_keep
check "missing directory: exit 1, no 'rotated'" t_missing_dir
check "directory without logs: rotated 0 file(s)" t_empty_dir
check "one log rotated, other files untouched" t_one_log
check "KEEP=2 keeps exactly two old copies" t_keep_limit
check "default KEEP is 3" t_default_keep_is_3
check "names with spaces, count of 2" t_spaces_and_count
check "copy-then-truncate keeps the inode" t_same_inode

echo "Ran $((passed + failed)) tests: $passed passed, $failed failed"
[ "$failed" -eq 0 ]
