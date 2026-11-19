---
id: l15
title: "Lab: the broken box and Bash strict mode"
quiz: quiz-04.yaml
resources: [../resources/ch05/broken-box/Dockerfile, ../resources/ch05/broken-box/box-init.sh, ../resources/ch05/broken-box/check.sh, ../resources/ch05/broken-box/vmapi.py, ../resources/ch05/broken-box/vmapi.conf, ../resources/ch05/broken-box/vmapi-ctl.sh, ../resources/ch05/broken-box/worker-v1.sh, ../resources/ch05/broken-box/dispatcher.py, ../resources/ch05/broken-box/nightly.sh, ../resources/ch05/broken-box/SOLUTIONS.md, ../resources/ch05/rotate_logs_starter.sh, ../resources/ch05/rotate_logs_solution.sh, ../resources/ch05/rotate_logs_test.sh]
sources: [105, 112, 114, 122, 124, 125]
---
After this lab you can diagnose seven classic faults on a Linux box from a root shell, and write a Bash script in strict mode that fails loudly instead of quietly producing an empty result.

## Shortcut

Download the `broken-box` folder and the three `rotate_logs_*.sh` files. Build and start the box, open a shell in it and run the checker:

```bash
cd broken-box
docker build -t pce-ch05-broken-box .
docker run -d --name pce-ch05-box --tmpfs /var/spool/vmjobs:size=4m,nr_inodes=2048 pce-ch05-broken-box
docker exec -it pce-ch05-box bash
check
```

In Git Bash on Windows, prefix `docker run` and `docker exec` with `MSYS_NO_PATHCONV=1`, or `/var/spool/...` becomes a Windows path. `--tmpfs` gives the job spool its own in-memory filesystem (a tmpfs) with only 2048 inodes; without it, fault 5 cannot appear.

For the strict-mode exercise, on any machine with bash:

```bash
bash rotate_logs_test.sh                          # tests your rotate_logs_starter.sh
bash rotate_logs_test.sh rotate_logs_solution.sh  # tests the reference
```

The course's test run used Docker 29.9.1 and `debian:bookworm-slim` (Python 3.11.2, bash 5.2.15). A fresh box printed `0/7 passed`; each fix from `SOLUTIONS.md` added one PASS, ending at `7/7 passed`. The reference script printed `Ran 11 tests: 11 passed, 0 failed` in Git Bash (bash 5.3) and in Debian; the untouched starter, `1 passed, 10 failed`.

## The broken box (45 to 60 minutes)

The box has no systemd: `box-init` is process 1, and `vmapi-ctl start|stop|restart|status` stands in for `systemctl`. The table gives symptoms only. Look before you change anything, change one thing, run `check`.

| # | Symptom | Where to start |
| --- | --- | --- |
| 1 | `/var/log/vmapi/boot.log` says vmapi failed with exit status 126 | lesson 1 (exit statuses), lesson 2 (modes) |
| 2 | vmapi answers on the box but `check` cannot reach it on `eth0` | lesson 3, steps 2 to 4 |
| 3 | `kill` does not stop `worker-v1.sh` | `/proc/PID/status`, the script |
| 4 | `ps` shows `<defunct>` processes | their parent, and its code |
| 5 | new job files cannot be created: "No space left on device" | `df -h`, then `df -i` |
| 6 | the nightly report, run as user `report`, is empty | run it as `report`, read the error |
| 7 | the nightly report exits 0 even when given a directory that does not exist | the script's first lines |

Rules: fix the cause, not only the running copy (the checker starts fresh copies for faults 3, 4 and 7); no `chmod 777`; keep the 20 queued jobs. To act as another user, run `setpriv --reuid report --regid report --init-groups COMMAND` from `/`, because root skips permission checks. [122]

### Hints

1. 126 means "found but not executable". [125] Look at the mode of the program, not of `vmapi-ctl`.
2. `ss -ltn` [112], then the configuration file in `/etc/vmapi`.
3. `SigIgn` in `/proc/PID/status`, and `trap` in the script. Ignored signals survive `fork` and `execve`. [105] In the test run, bash ran a new trap only after the foreground `sleep 5` finished, so stopping took up to five seconds.
4. A zombie has already exited; only its parent can collect it. Fix the code, then end the old parent.
5. Blocks and inodes are counted separately. [114] `du -s --inodes /var/spool/vmjobs/*` shows who uses them. [114]
6. The directory's group is `report`. Which bits does the group have? [122]
7. See the next section.

Stuck for ten minutes on one fault? Read its section in `SOLUTIONS.md`. Clean up with `docker rm -f pce-ch05-box` and `docker rmi pce-ch05-broken-box`.

## Bash strict mode

Faults 6 and 7 live in one script, `nightly.sh`, whose work is one pipeline:

```bash
cd "$IN_DIR"
cat *.csv | grep ',running$' | cut -d, -f1 | sort | uniq -c > "$OUT"
```

Before the fix, a bad run looked like a good one:

```console
# (cd / && setpriv --reuid report --regid report --init-groups /opt/report/nightly.sh /nonexistent; echo "exit=$?")
/opt/report/nightly.sh: line 11: cd: /nonexistent: No such file or directory
cat: '*.csv': No such file or directory
report written: /srv/reports/out/running-vms.txt
exit=0
```

Bash keeps going after a failed command, and a pipeline's status is that of its last command. [124] `set -euo pipefail` changes three things:

- `-e`: exit as soon as a pipeline, list or compound command fails. Not when the failing command is the condition of `if`, `elif`, `while` or `until`, any part of `&&`/`||` except the last, a pipeline element except the last, or inverted with `!`. [124]
- `-u`: using an unset variable is an error, and a non-interactive shell exits. [124] `${VAR:-default}` says "unset is fine here"; in the test run it printed the default under `-u`.
- `-o pipefail`: the pipeline returns the status of the rightmost command that failed, or 0 if all succeeded. [124]

From the test run, in bash 5.2:

```console
$ false | true; echo $?
0
$ set -o pipefail
$ false | true; echo $?
1
$ (exit 3) | (exit 5) | true; echo $?
5
```

Traps remain: a function called as an `if` condition runs with `-e` off inside it. [124] In the test run, `local v=$(false)` did not stop the script, and `((n++))` with `n=0` did.

Also: quote `"$@"` to keep arguments as separate words [125], and write `> file 2>&1`, not `2>&1 > file`, because redirections apply left to right. [124]

## Exercise: rotate_logs (20 minutes)

Write `rotate_logs.sh LOG_DIR [KEEP]` in strict mode: for each `*.log` file, shift `NAME.log.1` up to `NAME.log.KEEP`, copy the log to `.1`, then truncate the log. Bad arguments exit 2, a missing directory exits 1. The full statement is the header of `rotate_logs_starter.sh`.

**Hints.** Validate `KEEP` with a `case` pattern before touching any file. `shopt -s nullglob` makes an empty directory loop zero times, not once over a literal `*.log`. Quote every path; the tests use a space. Copy-then-truncate (`cp -p` then `: > "$log"`) keeps the inode, so a program that holds the log open keeps writing to the same file; the last test checks the inode number.

**Walkthrough.** The reference checks the arguments with `[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage` (inside an `||` list, so `-e` does not fire on the test [124]) and `KEEP` with `case $keep in '' | *[!0-9]* | 0*)`. `rotate_one` deletes `.KEEP`, renames the others counting down from `KEEP-1`, then copies and truncates; a failing `mv` or `cp` stops the script before `rotated N file(s)`. Cost: O(F × KEEP) renames for F logs. Common mistakes: an unquoted `$log`, counting up (which overwrites `.2` before it moves), and `mv` instead of copy-then-truncate.

## Gotchas
- **`kill -9` as the fix for fault 3.** The next worker ignores SIGTERM again; fix the `trap`. [105]
- **Deleting the whole spool.** It frees inodes and loses the 20 queued jobs; delete only `sessions/sess_*`. [114]
- **`set -e` inside `if f; then`.** The function runs with `-e` ignored, so its failures pass silently. [124]
- **Redirect before failure.** `> "$OUT"` empties the file before the pipeline runs, so a failed run leaves an empty report; write a temporary file and `mv` it.

:::key-takeaways
- Diagnose before you change: mode, listener, `/proc/PID/status`, parent, `df -i`, run as the right user. [112] [114] [122]
- Exit 126 is "not executable", 127 "not found", 128+N "killed by signal N". [125]
- `set -euo pipefail` makes a script stop on the first failure, on unset variables and on failures inside pipelines. [124]
- `-e` is ignored in conditions, in `&&`/`||` lists and in functions called from them. [124]
:::

:::glossary
- **Strict mode**: the habit of starting Bash scripts with `set -euo pipefail` so errors stop them.
- **Pipeline**: commands joined by `|`, each reading the previous one's output.
- **Exit status**: the number from 0 to 255 a command returns; 0 means success.
- **Trap**: a Bash command that sets what the shell does when a signal arrives.
- **tmpfs**: a filesystem kept in memory, used here to make a small spool with few inodes.
- **Copy-then-truncate**: rotating a log by copying it and emptying the original, so its inode stays the same.
:::
