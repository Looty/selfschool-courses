---
id: l07
title: "Lab: the broken box and Bash strict mode"
quiz: quiz-07.yaml
resources: [../resources/ch02/broken-box/Dockerfile, ../resources/ch02/broken-box/box-init.sh, ../resources/ch02/broken-box/check.sh, ../resources/ch02/broken-box/vmapi.py, ../resources/ch02/broken-box/vmapi.conf, ../resources/ch02/broken-box/vmapi-ctl.sh, ../resources/ch02/broken-box/worker-v1.sh, ../resources/ch02/broken-box/dispatcher.py, ../resources/ch02/broken-box/nightly.sh, ../resources/ch02/broken-box/SOLUTIONS.md]
sources: [105, 112, 114, 122, 124, 125]
---
After this lab you can diagnose seven classic faults on a Linux box from a root shell, out loud and in order, and write a Bash script in strict mode that fails loudly instead of quietly producing an empty result.

## Setup

Download the whole `broken-box` folder, then:

```bash
cd broken-box
docker build -t pce-ch02-broken-box .
docker run -d --name pce-ch02-box --tmpfs /var/spool/vmjobs:size=4m,nr_inodes=2048 pce-ch02-broken-box
docker exec -it pce-ch02-box bash
check
```

In Git Bash on Windows, prefix `docker run` and `docker exec` with `MSYS_NO_PATHCONV=1`, or `/var/spool/...` becomes a Windows path. `--tmpfs` gives the job spool its own in-memory filesystem with only 2048 inodes; without it, fault 5 cannot appear.

## The broken box (60 minutes)

The box has no systemd: `box-init` is process 1, and `vmapi-ctl start|stop|restart|status` stands in for `systemctl`.

1. Run `check`, pick one failing line.
2. Look before you change anything; say aloud what you check and why, as in an interview.
3. Change one thing, run `check` again.
4. Stuck ten minutes on a fault? Read its section in `SOLUTIONS.md`.
5. Then read all of `SOLUTIONS.md` and clean up: `docker rm -f pce-ch02-box; docker rmi pce-ch02-broken-box`.

| # | Symptom | Where to start |
| --- | --- | --- |
| 1 | `/var/log/vmapi/boot.log`: vmapi failed with exit status 126 | lesson 1 (exit statuses), lesson 2 (modes) |
| 2 | vmapi answers on the box but `check` cannot reach it on `eth0` | lesson 3, steps 2 to 4 |
| 3 | `kill` does not stop `worker-v1.sh` | `/proc/PID/status`, the script |
| 4 | `ps` shows `<defunct>` processes | their parent, and its code |
| 5 | new job files: "No space left on device" | `df -h`, then `df -i` |
| 6 | the nightly report, run as user `report`, is empty | run it as `report`, read the error |
| 7 | the nightly report exits 0 for a directory that does not exist | the script's first lines |

Rules: fix the cause, not only the running copy (the checker starts fresh copies for faults 3, 4 and 7); no `chmod 777`; keep the 20 queued jobs. Root skips permission checks; to act as another user, run `setpriv --reuid report --regid report --init-groups COMMAND` from `/`. [122]

**Hints.** (1) 126 is "found but not executable" [125]; check the program's mode, not `vmapi-ctl`'s. (2) `ss -ltn` [112], then `/etc/vmapi`. (3) `SigIgn` and the script's `trap`; ignored signals survive `fork` and `execve`. [105] `kill -9` fixes only this copy. (4) Only a zombie's parent can collect it: fix the code, then end the old parent. (5) `du -s --inodes /var/spool/vmjobs/*` [114]; delete stale `sessions/sess_*`, not the whole spool. (6) Which bits does group `report` have on the directory? [122] (7) Below.

## Bash strict mode

Faults 6 and 7 live in `nightly.sh`:

```bash
cd "$IN_DIR"
cat *.csv | grep ',running$' | cut -d, -f1 | sort | uniq -c > "$OUT"
```

Given `/nonexistent`, it printed the `cd` and `cat` errors, then `report written`, and exited 0. Bash keeps going after a failed command, and a pipeline's status is its last command's. [124] `set -euo pipefail` changes that:

- `-e`: exit when a command fails, except in an `if`/`while` condition, any part of `&&`/`||` but the last, a pipeline element but the last, or after `!`. [124]
- `-u`: an unset variable is an error; `${VAR:-default}` allows it. [124]
- `-o pipefail`: a pipeline returns the rightmost failing status, or 0. [124]

```console
$ false | true; echo $?
0
$ set -o pipefail; false | true; echo $?
1
$ (exit 3) | (exit 5) | true; echo $?
5
```

Traps: a function called as an `if` condition runs with `-e` off inside it. [124] Write `> file 2>&1`, not `2>&1 > file`: redirections apply left to right. [124]

:::key-takeaways
- Diagnose before you change: mode, listener, `/proc/PID/status`, parent, `df -i`, run as the right user. [112] [114] [122]
- 126 not executable, 127 not found, 128+N killed by signal N. [125]
- `set -euo pipefail` stops on failures, unset variables and failing pipelines; `-e` is ignored in conditions and `&&`/`||` lists. [124]
:::

:::glossary
- **Strict mode**: starting Bash scripts with `set -euo pipefail` so errors stop them.
- **Trap**: a Bash command that sets what the shell does when a signal arrives.
- **tmpfs**: a filesystem kept in memory, used here to make a small spool with few inodes.
:::
