#!/bin/bash
# rotate_logs.sh: rotate the *.log files in one directory, in strict mode.
#
# Usage: rotate_logs.sh LOG_DIR [KEEP]
#
# Input
#   LOG_DIR  a directory. Required.
#   KEEP     how many old copies to keep per log: a positive integer with no
#            leading zero. Optional, default 3.
#
# What it does, for every regular file LOG_DIR/NAME.log (names may contain spaces):
#   1. delete NAME.log.KEEP if it exists;
#   2. rename NAME.log.(KEEP-1) to NAME.log.KEEP, ..., NAME.log.1 to NAME.log.2,
#      skipping numbers that do not exist;
#   3. copy NAME.log to NAME.log.1, then truncate NAME.log to zero bytes.
#      (Copy-then-truncate keeps the same file, so a program that holds
#      NAME.log open keeps writing to it.)
#   Files that do not end in .log are not touched.
#
# Output and exit status
#   stdout: "rotated N file(s)" as the last line, N = number of logs rotated.
#   No arguments, or more than two, or a bad KEEP: a line starting with "usage:"
#   or an error message on stderr, exit status 2, nothing rotated.
#   LOG_DIR is not a directory: an error message on stderr, exit status 1.
#   Any command that fails during rotation stops the script with a non-zero
#   status, and "rotated" is not printed.
#
# Constraints
#   Bash only, plus rm, mv, cp. The script must turn on strict mode with the
#   exact line: set -euo pipefail
#
# Examples
#   $ ls logs/
#   api.log  notes.txt
#   $ rotate_logs.sh logs
#   rotated 1 file(s)
#   $ ls logs/
#   api.log  api.log.1  notes.txt          (api.log is now empty)
#
#   $ rotate_logs.sh logs 0
#   rotate_logs.sh: KEEP must be a positive integer, got '0'     (exit status 2)
#
#   $ rotate_logs.sh /no/such/dir
#   rotate_logs.sh: not a directory: /no/such/dir                (exit status 1)
#
# Test it:  bash rotate_logs_test.sh            (tests this starter file)

echo "rotate_logs.sh: not implemented yet" >&2
exit 1
