---
id: l07
title: "Lab: the broken box and Bash strict mode"
quiz: quiz-07.yaml
resources: [../resources/ch02/broken-box/Dockerfile, ../resources/ch02/broken-box/box-init.sh, ../resources/ch02/broken-box/check.sh, ../resources/ch02/broken-box/vmapi.py, ../resources/ch02/broken-box/vmapi.conf, ../resources/ch02/broken-box/vmapi-ctl.sh, ../resources/ch02/broken-box/worker-v1.sh, ../resources/ch02/broken-box/dispatcher.py, ../resources/ch02/broken-box/nightly.sh, ../resources/ch02/broken-box/SOLUTIONS.md]
sources: [105, 112, 114, 122, 124, 125]
---
After this lab you can make a Bash script fail loudly with strict mode, and diagnose seven classic Linux faults out loud, in order.

## Why strict mode: the silent failure

Faults 6 and 7 of the lab live in `nightly.sh`:

```bash
cd "$IN_DIR"
cat *.csv | grep ',running$' | cut -d, -f1 | sort | uniq -c > "$OUT"
```

Given `/nonexistent`, it printed the `cd` and `cat` errors, then `report written`, and exited 0. Bash continues after a failure, and a pipeline's status is its last command's. [124] `set -euo pipefail` fixes that (rungs below: bash on Ubuntu).

## set -e: stop at the first failure

**Rule:** with `-e`, the script exits as soon as a command fails, unless that failure is being tested. [124]

```console
$ bash -c 'false; echo after'                    # 1. no -e: keeps going
after
$ bash -c 'set -e; false; echo after'; echo $?   # 2. stops, status 1
1
$ bash -c 'set -e; false || echo fallback'       # 3. edge: inside || it is tested
fallback
$ bash -c 'set -e; if false; then :; fi; echo end'   # 4. edge: if condition
end
$ bash -c 'set -e; false | true; echo end'      # 5. edge: not the last in a pipe
end
```

Exempt: `if`/`while` conditions, all of `&&`/`||` but the last, all of a pipe but the last, and after `!`. [124] Trap: a function called as an `if` condition runs with `-e` off inside it. [124]

**P1.** Under `set -e`, does `grep -q x missing.txt && echo found` stop the script?

## set -u: an unset variable is an error

**Rule:** with `-u`, using a never-set variable stops the script instead of becoming empty. [124]

```console
$ bash -c 'echo "[$REGION]"; echo end'           # 1. no -u: empty
[]
end
$ bash -c 'set -u; echo "[$REGION]"; echo end'   # 2. stops, "end" never prints
bash: line 1: REGION: unbound variable
$ bash -c 'set -u; echo "[${REGION:-eu}]"'       # 3. default: unset is fine here
[eu]
$ bash -c 'set -u; REGION=""; echo "[$REGION]"'  # 4. edge: empty is not unset
[]
```

**P2.** Under `set -u`, what does `echo "${PORT:-8080}"` print when `PORT` was never set?

## set -o pipefail: a pipe fails if any part fails

**Rule:** with `pipefail`, a pipeline returns the rightmost failing status, or 0 if all succeeded. [124]

```console
$ bash -c 'false | true; echo $?'                                  # 1. last wins: 0
0
$ bash -c 'set -o pipefail; false | true; echo $?'                 # 2. 1, from false
1
$ bash -c 'set -o pipefail; (exit 3) | (exit 5) | true; echo $?'   # 3. rightmost: 5
5
$ bash -c 'set -o pipefail; true | true; echo $?'                  # 4. all fine: 0
0
```

**Contrast:** `cd /nonexistent; echo "report written"`:

| Flags | Prints `report written`? | Exit status |
| --- | --- | --- |
| none | yes | 0 |
| `set -euo pipefail` | no, stops at `cd` | 1 |

Memory hook: **e** = error stops, **u** = unset stops, **pipefail** = the pipe tells the truth.

**P3.** With `pipefail`, what is the status of `grep x /nonexistent | sort`? (grep returns 2 when it cannot open a file.)

## Setup

Download the `broken-box` folder:

```bash
cd broken-box
docker build -t pce-ch02-broken-box .
docker run -d --name pce-ch02-box --tmpfs /var/spool/vmjobs:size=4m,nr_inodes=2048 pce-ch02-broken-box
docker exec -it pce-ch02-box bash
check
```

In Git Bash on Windows, prefix `docker run` and `docker exec` with `MSYS_NO_PATHCONV=1`. `--tmpfs` gives the spool 2048 inodes; without it, fault 5 cannot appear.

## The broken box (60 minutes)

No systemd here: `vmapi-ctl start|stop|restart|status` stands in for `systemctl`.

1. Run `check`, pick one failing line.
2. Look first; say aloud what you check and why.
3. Change one thing, run `check` again.
4. Stuck ten minutes? Read `SOLUTIONS.md`.
5. Clean up: `docker rm -f pce-ch02-box; docker rmi pce-ch02-broken-box`.

| # | Symptom | Where to start |
| --- | --- | --- |
| 1 | `boot.log`: vmapi exit status 126 | lesson 1 (exit statuses), lesson 2 (modes): the program's mode [125] |
| 2 | vmapi answers on the box, not on `eth0` | lesson 3, steps 2 to 4; then `/etc/vmapi` [112] |
| 3 | `kill` does not stop `worker-v1.sh` | `SigIgn` in `/proc/PID/status`, the script's `trap` [105] |
| 4 | `ps` shows `<defunct>` processes | their parent, and its code |
| 5 | "No space left on device" | `df -i`, `du -s --inodes`; delete only stale `sessions/sess_*` [114] |
| 6 | report, run as `report`, is empty | run it as `report`; group bits [122] |
| 7 | report exits 0 for a missing directory | strict mode, above |

Rules: fix the cause, not the running copy; no `chmod 777`; keep the 20 queued jobs. Root skips permission checks; act as a user with `setpriv --reuid report --regid report --init-groups COMMAND` from `/`. [122]

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| `set -e` | exit on an untested failure | `false; echo x` → stops |
| `set -u` | unset variable is an error; `${V:-d}` allows it | `${REGION:-eu}` → `eu` |
| `pipefail` | rightmost failure wins | `(exit 3) \| (exit 5) \| true` → 5 |

## Answers

**P1.** No: `grep` is not the last command of the `&&` list, so `-e` ignores it.

**P2.** `8080`: `:-` supplies the default; `-u` stays quiet.

**P3.** 2: `grep` is the rightmost failure, though `sort` succeeded.

**R1.** No: it is tested by `if`.

**R2.** No: empty is still set.

**R3.** 0: the last command decides.

**R4.** 4: the rightmost failure; the last command's 0 does not hide it.

## If you missed a quiz question

| If you thought... | Reread | Re-check |
| --- | --- | --- |
| `-e` stops on every failure | set -e | **R1.** Does `if grep -q x f; then` stop on a miss? |
| `-u` stops on empty values | set -u | **R2.** Does `X=""; echo $X` stop under `-u`? |
| a pipe fails if any part fails, by default | pipefail | **R3.** `false \| true` without pipefail? |
| pipefail returns the first failure, or the last command's | pipefail | **R4.** `true \| (exit 4) \| (exit 0)` with pipefail? |

:::key-takeaways
- `set -euo pipefail`: stop on failures, unset variables, failing pipes. [124]
- `-e` is off in conditions and `&&`/`||` lists. [124]
- Diagnose before you change. [112] [114] [122]
:::

:::glossary
- **Strict mode**: starting Bash scripts with `set -euo pipefail` so errors stop them.
- **Pipeline**: commands joined by `|`, each reading the previous one's output.
- **Trap**: a Bash command that sets what the shell does when a signal arrives.
- **tmpfs**: a filesystem kept in memory.
:::
