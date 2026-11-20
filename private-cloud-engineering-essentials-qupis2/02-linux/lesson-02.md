---
id: l05
title: "Files, permissions and disks"
quiz: quiz-05.yaml
sources: [114, 115, 122]
---
After this lesson you can read and set any permission mode in octal, predict what a user can do in a directory, and answer "the disk is full, walk me through it".

## Who gets which bits

The kernel uses exactly one bit group: owner if the process's user owns the file, else group if the file's group is one of the process's groups, else other. [122] Each group has read (4), write (2) and execute (1), which for a directory means search; a leading fourth digit holds setuid (4), setgid (2) and sticky (1). [122]

```text
0644  rw-r--r--   config file
0600  rw-------   private key, authorized_keys
0755  rwxr-xr-x   program, public directory
0750  rwxr-x---   directory for one team
2775  rwxrwsr-x   shared team directory (setgid)
1777  rwxrwxrwt   /tmp (sticky)
```

```bash
chmod 750 dir
chmod u=rwx,g=rx,o= dir     # same thing; + adds, - removes, = sets
```

[122]

Root skips these checks through `CAP_DAC_OVERRIDE`, but still needs at least one execute bit to run a file. [122] So even root gets exit status 126 running a `0644` script. Reproduce permission bugs as the service's user, not as root. [122]

## Directories

- To open `/srv/box/file` you need search (`x`) on `/`, `/srv` and `/srv/box`. [122]
- Removing a name needs write on the directory, not on the file. [122]

:::low-confidence
The course's test run on Debian 12 showed `r` on a directory lists names, `w` (with `x`) creates and deletes entries, and `x` alone lets you open a file whose name you know. The notes do not state this in one place; see the "Mode Structure" node of the GNU coreutils manual.
:::

## umask, setgid and sticky

The umask turns bits off at creation: `0666 & ~022` gives `0644`; the typical default is `022`. [122]

- **setuid** on a program: it runs with the file owner's user ID, which is how `passwd` updates root-owned files. Linux ignores it on `#!` scripts. [122]
- **setgid on a directory**: new files get the directory's group. [122]
- **sticky on a directory**: only a file's owner, the directory's owner or a privileged process can delete or rename it. [122]

## Inodes and links

An inode holds type, mode, owner, size, link count and timestamps, but not the name, which lives in the directory. [122]

```console
$ ln orig hard; ln -s orig soft; ls -li
341267 -rw-r--r-- 2 root root 5 hard
341267 -rw-r--r-- 2 root root 5 orig
341268 lrwxrwxrwx 1 root root 4 soft -> orig
$ rm orig; cat hard; cat soft
data
cat: soft: No such file or directory
```

A hard link is a second name for the same inode; a symlink stores a path and dangles once it is gone. [122] Data is freed only when the last name is gone and no process holds the file open. [122]

## "The disk is full": the walk-through

```bash
df -h                        # 1. free blocks per filesystem
df -i                        # 2. free inodes: many small files exhaust them
du -sh /var/*                # 3. who uses the blocks
du -s --inodes DIR/*         #    who uses the inodes
du -x                        #    stay on one filesystem
lsof +L1                     # 4. deleted files still held open
```

[114] [115]

A full inode table refuses new files even with free space:

```console
# touch /var/spool/vmjobs/incoming/job-0021.json
touch: cannot touch '...': No space left on device
# df -h /var/spool/vmjobs
tmpfs           4.0M   80K  4.0M   2% /var/spool/vmjobs
# df -i /var/spool/vmjobs
tmpfs            2048  2048     0  100% /var/spool/vmjobs
```

And a deleted log that a process still holds open frees nothing: after `rm /data/app.log`, `df` stayed at 40 MB used while `du` showed 0, and `lsof +L1` listed `/data/app.log (deleted)` held by PID 229. [115] Restart the holder.

Never "fix" permissions with `chmod 777`: every user can then replace the files; give the group what it needs (`750`, `640`). [122]

:::key-takeaways
- One bit group applies: owner, else group, else other. [122]
- Octal: 4 read, 2 write, 1 execute; leading 4 setuid, 2 setgid, 1 sticky. [122]
- Deleting needs write on the directory; reaching a path needs search on every directory. [122]
- Disk full: `df -h`, `df -i`, `du`, then `lsof +L1`. [114] [115]
:::

:::glossary
- **umask**: a per-process mask of bits removed from new files and directories.
- **Inode**: the on-disk record of a file's metadata, without its name.
:::
