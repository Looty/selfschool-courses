# Git recovery lab: solutions

Recorded in the course's test run with Git 2.55.0.windows.3 in Git Bash on Windows, in the order below
(6A, 1, 2, 3, 4, 5, 6B). Hashes made by `make_lab_repo.sh` (for example `145402b`, `f601535`, `9c8a72e`,
`1cce4d2`) are fixed and will match yours. Hashes of commits you create yourself (the cherry-pick, the revert,
the rebased commits, the stash and the WIP commit) contain the current time and will differ.

```bash
bash make_lab_repo.sh ~/git-lab
cd ~/git-lab/repo
git log --oneline --graph --all     # look at the whole history before you touch anything
```

## Task 6, part A: shelve the work in progress

You are on `main` with a modified `NOTES.md` and an untracked `scratch-plan.txt`. Bisect and branch switching
need a clean tree, so stash both, including the untracked file.

```console
$ git stash push -u -m "wip: quota notes"
Saved working directory and index state On main: wip: quota notes
$ git stash list
stash@{0}: On main: wip: quota notes
$ git status --short
$
```

Without `-u` the untracked `scratch-plan.txt` would stay in the working tree.

## Task 1: a commit landed on the wrong branch

`Add JSON output for report` was committed on `docs`; it belongs on `feature/report`. Copy it across with
cherry-pick, then remove it from `docs` with a hard reset (safe here: `docs` was never pushed and the tree is clean).

```console
$ git switch docs
$ git log --oneline -3
a089371 Add JSON output for report
032b056 Fix typo in contributing guide
bd2c3be Add contributing guide
$ git switch feature/report
$ git cherry-pick docs
[feature/report 2ce1b54] Add JSON output for report
 Date: Mon Jan 5 16:00:00 2026 +0000
 1 file changed, 4 insertions(+)
 create mode 100644 lib/report_json.sh
$ git switch docs
$ git reset --hard HEAD~1
HEAD is now at 032b056 Fix typo in contributing guide
```

The `Date:` line shows that cherry-pick kept the original author date; the new hash (`2ce1b54` here) differs
because the committer date is now.

## Task 2: recover a commit lost by a hard reset

Someone ran `git reset --hard HEAD~1` on `experiment` and lost `Tune retry backoff`. The branch's reflog still has it.

```console
$ git reflog experiment
c900baa experiment@{0}: reset: moving to HEAD~1
f601535 experiment@{1}: commit: Tune retry backoff
c900baa experiment@{2}: commit: Add retry helper
bd2c3be experiment@{3}: branch: Created from bd2c3be1d541ca86916f90ffa894bcc090affaad
$ git switch experiment
$ git reset --hard experiment@{1}
HEAD is now at f601535 Tune retry backoff
```

`git reflog` with no argument shows the same commit as `HEAD@{N}`, but N depends on how many times you moved
HEAD before this task (it was `HEAD@{24}` in the test run). `experiment@{1}` does not depend on that.
`git branch -f experiment f601535` from another branch would work as well.

## Task 3: find the commit that broke `to_mib`

`tests/run.sh` exits 0 when the checks pass and 1 when they fail. `v1.0` is known good and `main` is bad.

```console
$ git switch main
$ sh tests/run.sh
FAIL: to_mib 2G gave 2000, expected 2048
$ git bisect start main v1.0
$ git bisect run sh tests/run.sh
Bisecting: 6 revisions left to test after this (roughly 3 steps)
[145402b947cb677494b45cdd06d7525f1a780283] Refactor unit parsing
running 'sh' 'tests/run.sh'
FAIL: to_mib 2G gave 2000, expected 2048
Bisecting: 3 revisions left to test after this (roughly 2 steps)
[ecae3210fcfd434bd1244fb1b5260f383626e2a8] Add usage section to README
running 'sh' 'tests/run.sh'
all checks passed
Bisecting: 1 revision left to test after this (roughly 1 step)
[061173555a32ddd5374118bb78cf96f13d25e0da] Add Makefile
running 'sh' 'tests/run.sh'
all checks passed
Bisecting: 0 revisions left to test after this (roughly 0 steps)
[be60327ca8c93ae93884d7ced09f0f35fdb5276a] Add changelog
running 'sh' 'tests/run.sh'
all checks passed
145402b947cb677494b45cdd06d7525f1a780283 is the first 'bad' commit
commit 145402b947cb677494b45cdd06d7525f1a780283
Author: Lab User <lab@example.com>
Date:   Tue Jan 6 02:00:00 2026 +0000

    Refactor unit parsing

 lib/size.sh | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)
bisect found first 'bad' commit
$ git tag found-bug refs/bisect/bad
$ git bisect reset
Switched to branch 'main'
```

Tag `refs/bisect/bad` before `git bisect reset`, while the bisect refs are still there. The bug: the refactor uses `factor=1000`
for G instead of 1024. Four test runs covered 13 commits.

## Task 4: undo a pushed commit on `release`

`Switch default region to dc-test` is already on `origin/release`. Others may have fetched it, so do not
rewrite: record a new commit that reverses it, then push normally (a fast-forward).

```console
$ git switch release
$ git revert --no-edit HEAD
[release b366644] Revert "Switch default region to dc-test"
 Date: Thu Nov 19 14:15:43 2026 +0200
 1 file changed, 1 insertion(+), 1 deletion(-)
$ cat config/defaults.env
REGION=dc1
DEFAULT_FLAVOUR=medium
$ git push origin release
To .../remote.git
   9c8a72e..b366644  release -> release
$ git log --oneline -3
b366644 Revert "Switch default region to dc-test"
9c8a72e Switch default region to dc-test
c2466bb Prepare release 1.1
```

## Task 5: rebase `feature/quota` onto `main`, with one conflict

Both `main` and `feature/quota` appended a line at the end of README's command list.

```console
$ git switch feature/quota
$ git rebase main
Rebasing (1/2)
Auto-merging README.md
CONFLICT (content): Merge conflict in README.md
error: could not apply 3dd92e5... Add quota command
hint: Resolve all conflicts manually, mark them as resolved with
hint: "git add/rm <conflicted_files>", then run "git rebase --continue".
...
$ tail -6 README.md
- `to_mib`: convert a size such as 2G to MiB
<<<<<<< HEAD
- `to_gib`: convert a size to whole GiB
=======
- `quota`: show how many VMs a team may run
>>>>>>> 3dd92e5 (Add quota command)
```

During a rebase the `HEAD` side is `main` plus the commits replayed so far, and the other side is your
commit. Keep both lines, delete the three marker lines, then:

```console
$ git add README.md
$ git rebase --continue
```

Git opens your editor with the commit message; save and close it unchanged. (The test run used
`GIT_EDITOR=true git rebase --continue` to skip the editor.)

```console
[detached HEAD 586c1ba] Add quota command
 2 files changed, 5 insertions(+)
 create mode 100644 lib/quota.sh
Rebasing (2/2)
Successfully rebased and updated refs/heads/feature/quota.
$ git log --oneline --graph -4
* 1a12032 Document quota limits
* 586c1ba Add quota command
* 1cce4d2 Tidy size.sh comments
* 3fdca25 Update notes
```

If `feature/quota` had already been pushed, the rebase replaced its commits, so a plain push would be refused
as a non-fast-forward. Use `git push --force-with-lease origin feature/quota`, which refuses if someone else
pushed to that branch since your last fetch.

## Task 6, part B: turn the stash into a branch

```console
$ git switch main
$ git stash list
stash@{0}: On main: wip: quota notes
$ git stash branch wip/notes
Switched to a new branch 'wip/notes'
On branch wip/notes
Changes not staged for commit:
	modified:   NOTES.md
Untracked files:
	scratch-plan.txt
Dropped refs/stash@{0} (dde5e9526b936e077b91ba763a6980aa5ae361f4)
$ git add -A
$ git commit -m "WIP: quota notes"
$ git stash list
$
```

## Check

```console
$ git switch main
$ bash check_lab.sh ~/git-lab
PASS  task 1: JSON commit moved from docs to feature/report
PASS  task 2: experiment tip is 'Tune retry backoff' again
PASS  task 3: tag found-bug points at the first bad commit
PASS  task 4: region change reverted on release, old commit still in history, pushed to origin
PASS  task 5: feature/quota sits on top of main, README keeps both command lines
PASS  task 6: stash turned into branch wip/notes with NOTES.md and scratch-plan.txt; stash list empty
All tasks pass.
```

To start again: delete the lab directory and run `make_lab_repo.sh` once more.
