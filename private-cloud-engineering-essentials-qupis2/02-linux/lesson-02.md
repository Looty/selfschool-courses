---
id: l05
title: "Files, permissions and disks"
quiz: quiz-05.yaml
sources: [114, 115, 122]
---
After this lesson you can read a permission mode as a number, predict what a user can do in a directory, and answer "the disk is full".

## Permission bits as numbers

**Rule:** each digit is a sum of three switches, read 4, write 2, execute 1; the three digits are owner, group, other. [122]

One digit first:

```text
7 = 4+2+1   rwx
6 = 4+2     rw-
5 = 4  +1   r-x
4 = 4       r--
0           ---   edge: nothing at all
```

Three digits (Ubuntu; `stat` prints both forms):

```console
$ chmod 640 f; stat -c '%a %A' f
640 -rw-r-----        # owner rw, group r, other nothing
$ chmod 755 f; stat -c '%a %A' f
755 -rwxr-xr-x        # program, public directory
$ chmod 0 f; stat -c '%a %A' f
0 ----------          # edge: even the owner is locked out
```

Which digit applies? Exactly one: owner if you own the file, else group if you are in its group, else other. [122] Edge: the owner of a `0077` file cannot read it, though everyone else can. [122] Edge: root skips read and write checks but still needs one `x` bit to run a file, so root gets 126 on a `0644` script. [122]

**Contrast:** `640` (team can read, others nothing) versus `777` (anyone can replace your files): give the group what it needs, never 777. [122]

**P1.** File `app.conf` is `0640`, owner `alice`, group `ops`. Can `bob`, who is in `ops`, edit it?

:::answer
No. `bob` is not the owner, so the group digit 4 (`r--`) applies: read only.
:::

## Permission bits on a directory

**Rule:** a directory is a list of names; `r` reads the list, `w` changes it (create, delete, rename), `x` lets you pass through. [122]

Test run: `bob` (group `ops`), directory owned by `alice:ops`, holding a `0640` file:

| Directory mode (group digit) | `ls dir` | `cat dir/file` | create a file |
| --- | --- | --- | --- |
| `750` (r-x) | ok | ok | denied |
| `740` (r--) | ok, but `-?????????` per entry | denied | denied |
| `710` (--x) | denied | ok, if he knows the name | denied |
| `770` (rwx) | ok | ok | ok |

Edge: with `770`, `bob` deleted `alice`'s `0400` file: deleting needs `w` on the directory, not the file. [122] Opening `/srv/box/file` needs `x` on `/`, `/srv` and `/srv/box`. [122]

:::low-confidence
The sources state the `x` and delete rules; the `r` and create columns are what the Debian 12 test run showed. See "Mode Structure" in the GNU coreutils manual.
:::

**P2.** `/srv/exports` is `750 root:export`. A job running as user `export` (group `export`) creates `/srv/exports/out.txt`. What happens? Smallest fix?

:::answer
Permission denied: group digit 5 (`r-x`) has no `w`, and creating a name changes the directory. Fix: `chmod 770`, not `777`.
:::

## df, du and the deleted-but-open file

**Prerequisite:** a file's record (owner, mode, size, link count) is its inode; its name lives in the directory. [122] The data is freed only when the last name is gone *and* no process holds the file open. [122]

**Rule:** `df` asks the filesystem how much is free; `du` walks the directory tree and adds up the files it finds by name. [114]

Ladder from the course's test runs:

```console
$ df -h /data                       # 1. 40 MB log, held open by tail
tmpfs  100M   40M   60M  40% /data
$ rm /data/app.log; df -h /data     # 2. name gone, data still held
tmpfs  100M   40M   60M  40% /data
$ du -sh /data                      # 3. du finds no name, counts 0
0	/data
$ lsof +L1                          # 4. open files with link count 0
tail  229 root  3r  REG ... /data/app.log (deleted)
```

[114] [115] Restart the holder (here PID 229) and `df` drops. Edge, the other "full": a filesystem out of inodes refuses new files while `df -h` shows space:

```console
# touch /var/spool/vmjobs/incoming/job-0021.json
touch: cannot touch '...': No space left on device
# df -h /var/spool/vmjobs     → 4.0M size, 2% used
# df -i /var/spool/vmjobs     → 2048 inodes, 2048 used, 100%
```

[114]

**Contrast:**

| Command | Counts | Blind to |
| --- | --- | --- |
| `df -h` | blocks on the filesystem | which files |
| `df -i` | inodes | blocks |
| `du -sh DIR` | files reachable by name | deleted-but-open files |
| `lsof +L1` | open files with no name | named files |

[114] [115]

**P3.** `df -h` says `/var` is 100% full, `du -sh /var` says 3 GB of a 20 GB disk. What do you run next?

:::answer
`lsof +L1`: a deleted but open file uses blocks `df` counts and `du` cannot see.
:::

## "The disk is full": the walk-through

1. `df -h`: which filesystem is full? [114]
2. `df -i`: or out of inodes? [114]
3. `du -sh /var/*` (`-x`: one filesystem); `du -s --inodes DIR/*`. [114]
4. `df` and `du` disagree? `lsof +L1`, restart the holder. [115]
5. Delete or rotate the culprit.

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| octal digit | r 4 + w 2 + x 1 | `6` → `rw-` |
| `chmod 640 f` | owner, group, other | `-rw-r-----` |
| dir `x` / `w` | pass through / change names | `w` deletes others' files |
| `df -h` / `df -i` | free blocks / inodes | 2% vs 100% |
| `du`, `lsof +L1` | sum by name; open, nameless | deleted log → 0, `(deleted)` |

## If you missed a quiz question

**If you thought** 5 means `rw-`: reread "Bits as numbers". **R1.** What is digit 5?

:::answer
`r-x`.
:::

**If you thought** deleting needs `w` on the file: reread "Directory bits". **R2.** What does deleting a file need?

:::answer
Write on the directory.
:::

**If you thought** "No space left" always means no blocks: reread "df, du". **R3.** `df -h` says 2%; what next?

:::answer
`df -i`.
:::

**If you thought** `rm` frees space at once: reread "df, du". **R4.** Does `rm` on an open 2 GB log free 2 GB?

:::answer
No: removing the name frees nothing while a process holds the file.
:::

**If you thought** a user gets every digit that matches: reread "Bits as numbers". **R5.** Do the "other" bits add to a group member's rights?

:::answer
No: a non-owner group member gets only the group digit.
:::

:::key-takeaways
- 4 read, 2 write, 1 execute; one digit applies: owner, else group, else other. [122]
- Directory `x` passes through; `w` creates and deletes names. [122]
- `df -h`, `df -i`, `du`, then `lsof +L1`. [114] [115]
:::

:::glossary
- **Octal**: base-8 numbers; one digit holds three permission bits.
- **Inode**: the on-disk record of a file (owner, mode, size), without its name.
- **Link count**: how many names point to one inode.
:::
