---
id: l13
title: "Files, permissions and the filesystem"
quiz: quiz-02.yaml
sources: [106, 114, 115, 122]
---
After this lesson you can read and set any permission mode in octal, predict what a user can do in a directory, explain inodes, hard links and symlinks, and tell a full disk from a disk out of inodes.

## Who gets which bits

Every file has an owner, a group and a mode. The kernel uses exactly one of three bit groups: the owner bits if the process's user owns the file, else the group bits if the file's group is one of the process's groups, otherwise the "other" bits. [122] So an owner of a `0077` file cannot read it, though everyone else can.

Each group has three bits: read, write, and execute, which for a directory means search. [122] In octal each digit is the sum of 4 (r), 2 (w) and 1 (x); a fourth, leading digit holds setuid (4), setgid (2) and sticky (1). [122]

| Octal | Symbolic | Typical use |
| --- | --- | --- |
| `0644` | `rw-r--r--` | config file, readable by all |
| `0600` | `rw-------` | private key, `authorized_keys` |
| `0755` | `rwxr-xr-x` | program or public directory |
| `0750` | `rwxr-x---` | directory for one team |
| `2775` | `rwxrwsr-x` | shared team directory (setgid) |
| `1777` | `rwxrwxrwt` | `/tmp` (sticky) |

`chmod` takes both forms: `chmod 750 dir` or `chmod u=rwx,g=rx,o= dir`; `u`, `g`, `o`, `a` choose who, and `+`, `-`, `=` add, remove or set. [122] `chmod` never changes a symlink's own mode; it changes the target. [122]

Root traditionally skips these checks. On Linux that is the capability `CAP_DAC_OVERRIDE`, which still grants execute only if at least one execute bit is set. [122] In the test run, even root got `Permission denied` and exit status 126 running a `0644` script.

## Directories: r, w and x mean different things

To open `/srv/box/file`, a process needs search (`x`) permission on `/`, `/srv` and `/srv/box`; a missing one gives `EACCES`. [122] Removing a name needs write permission on the directory, not on the file. [122] In the course's test run, user `bob` (in group `ops`) tried a directory owned by `alice:ops`, holding a `0640` file:

| Directory mode | `ls dir` | `cat dir/file` | create a file |
| --- | --- | --- | --- |
| `750` (r-x) | ok | ok | denied |
| `740` (r--) | ok (`ls -l` shows `-?????????` per entry) | denied | denied |
| `710` (--x) | denied | ok (if he knows the name) | denied |
| `770` (rwx) | ok | ok | ok |

With `770`, `bob` also deleted a `0400` file owned by `alice`: the file's own mode did not matter.

:::low-confidence
The notes verify that `x` on a directory is search and that removing a name needs `w` on the directory. They do not state in one place that `r` lists names and `w` creates, removes and renames entries; the table above is what the test run showed on Debian 12. The usual reference is the "Mode Structure" node of the GNU coreutils manual.
:::

## umask, setuid, setgid and sticky

The umask turns bits off when a file or directory is created: mode `0666 & ~022` gives `0644`. [122] The typical default is `022`. [122] It is inherited across `fork` and kept by `execve`, and `/proc/PID/status` shows it in the `Umask` field. [122] [106] In the course's test run, as user `alice`:

```console
$ umask
0022
$ touch f; mkdir d; ls -ld f d
drwxr-xr-x 2 alice alice 4096 Nov 19 12:23 d
-rw-r--r-- 1 alice alice    0 Nov 19 12:23 f
$ umask 077; touch g; ls -l g
-rw------- 1 alice alice 0 Nov 19 12:23 g
```

- **setuid** on a program: the process runs with the file owner's user ID as its effective ID, which is how `passwd` (`-rwsr-xr-x root`) can update root-owned files. **setgid** does the same for the group. [122] Linux ignores both bits on `#!` scripts. [122]
- **setgid on a directory**: new files get the directory's group, and new subdirectories get the setgid bit too. [122] In the test run, `alice` created `x` and `sub` in a `2775 root:ops` directory and both came out in group `ops`.
- **Sticky bit on a directory**: a file can be renamed or deleted only by its owner, the directory's owner or a privileged process, which is why `/tmp` is `1777`. [122] In the test run, `bob` got `Operation not permitted` deleting `alice`'s file there.

## Inodes and links

An inode stores the file's metadata: type and mode, owner, group, size, link count and timestamps (`atime` read, `mtime` content changed, `ctime` metadata changed). [122] The name lives in the directory, not in the inode, and inode numbers are unique only within one filesystem. [122] From the course's test run:

```console
$ echo data > orig; ln orig hard; ln -s orig soft; ls -li orig hard soft
341267 -rw-r--r-- 2 root root 5 Nov 19 12:23 hard
341267 -rw-r--r-- 2 root root 5 Nov 19 12:23 orig
341268 lrwxrwxrwx 1 root root 4 Nov 19 12:23 soft -> orig
$ rm orig; cat hard; cat soft
data
cat: soft: No such file or directory
```

A **hard link** is a second name for the same inode (same number, link count 2). A **symlink** is its own small file storing a path; it dangles once the path is gone. Path resolution follows at most 40 symlinks before failing with `ELOOP`. [122]

`unlink` removes a name; the data is freed only when the last name is gone and no process holds the file open. [122] So deleting a log that a process still holds open frees nothing, as the test run showed on a 100 MB tmpfs:

```console
$ df -h /data            # 40 MB app.log, held open by a process
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           100M   40M   60M  40% /data
$ rm /data/app.log; df -h /data; du -sh /data
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           100M   40M   60M  40% /data
0	/data
$ lsof +L1
COMMAND PID USER   FD   TYPE DEVICE SIZE/OFF NLINK NODE NAME
tail    229 root    3r   REG  0,146 41943040     0    2 /data/app.log (deleted)
```

`lsof +L1` lists open files with a link count below 1. [115] Chapter 7 of the companion course covers this incident in full.

## Space versus inodes

| Command | Answers |
| --- | --- |
| `df -h` | free blocks per filesystem, in powers of 1024 [114] |
| `df -i` | free inodes per filesystem [114] |
| `df -hT` | the same with the filesystem type [114] |
| `du -sh DIR` | blocks used under DIR [114] |
| `du -s --inodes DIR/*` | inodes used per subdirectory [114] |
| `du -x` | stay on one filesystem [114] |

A filesystem with free blocks but no free inodes still refuses new files. From the lab's job spool:

```console
# touch /var/spool/vmjobs/incoming/job-0021.json
touch: cannot touch '/var/spool/vmjobs/incoming/job-0021.json': No space left on device
# df -h /var/spool/vmjobs
Filesystem      Size  Used Avail Use% Mounted on
tmpfs           4.0M   80K  4.0M   2% /var/spool/vmjobs
# df -i /var/spool/vmjobs
Filesystem     Inodes IUsed IFree IUse% Mounted on
tmpfs            2048  2048     0  100% /var/spool/vmjobs
```

In scripts, `df --output=FIELDS` picks columns [114], but not together with `-i` (the test run printed `options -i and --output are mutually exclusive`); use `df --output=ipcent`.

## Where things live

| Path | Holds |
| --- | --- |
| `/etc` | configuration local to this machine [122] |
| `/var/log`, `/var/lib`, `/var/spool` | logs, program state, queued work [122] |
| `/run` | runtime data since boot; replaces `/var/run` [122] |
| `/tmp` | temporary files, may be deleted without notice [122] |
| `/opt` | add-on packages [122] |
| `/srv` | data this machine serves [122] |
| `/usr/bin`, `/usr/local` | programs; locally installed software [122] |
| `/proc`, `/sys` | running processes and kernel information [122] |

## Gotchas

- **`chmod 777` as a fix.** It works and lets every user replace the program or files; give the group what it needs (`750`, `640`). [122]
- **Testing permissions as root.** Root skips the read and write checks, so reproduce the problem as the service's user. [122]
- **A directory without `x`.** Without search permission you cannot reach anything inside, whatever the files' modes say. [122]
- **Deleting a file still held open.** `df` does not move; find the holder with `lsof +L1` and restart it. [115]
- **"No space left" with free space.** Check `df -i`; many small files use up inodes. [114]
- **Setuid on a script.** Linux ignores the bit on `#!` files, so the script runs as the caller. [122]

:::key-takeaways
- One bit group applies: owner, else group, else other. [122]
- Octal digits: 4 read, 2 write, 1 execute or search; leading digit 4 setuid, 2 setgid, 1 sticky. [122]
- Deleting a name needs write on the directory; reaching a path needs search on every directory. [122]
- Hard links share an inode; a symlink stores a path. [122]
- `df -h` for blocks, `df -i` for inodes, `du` to find who uses them. [114]
:::

:::glossary
- **Mode**: the permission bits and type stored with a file.
- **Octal**: base-8 notation, one digit per three permission bits.
- **umask**: a per-process mask of bits removed from new files and directories.
- **setuid**: a bit that makes a program run with its owner's user ID.
- **setgid**: the same for the group; on a directory it makes new files inherit the group.
- **Sticky bit**: on a directory, only a file's owner may delete or rename it.
- **Inode**: the on-disk record of a file's metadata, without its name.
- **Hard link**: an extra directory entry pointing at the same inode.
- **Symlink**: a small file that stores a path to another file.
:::
