---
id: l17
title: "Lab: undo, recover and find the bad commit"
quiz: quiz-02.yaml
resources: [../resources/ch06/make_lab_repo.sh, ../resources/ch06/check_lab.sh, ../resources/ch06/LAB_SOLUTIONS.md]
sources: [153, 154]
---
After this lab you can pick the right undo command for a mistake (reset, revert, reflog, cherry-pick, stash), find a regression with `git bisect run`, and force-push without clobbering a colleague's work.

## Shortcut

Needs only Git and Bash. Build the lab, solve the six tasks inside `repo`, then check:

```bash
bash make_lab_repo.sh ~/git-lab      # creates ~/git-lab/repo and ~/git-lab/remote.git
cd ~/git-lab/repo
git log --oneline --graph --all      # read the history first
# ... solve tasks 6A, 1, 2, 3, 4, 5, 6B ...
bash /path/to/check_lab.sh ~/git-lab
```

In the course's test run (Git 2.55.0.windows.3 in Git Bash) a fresh lab printed six `FAIL` lines and exit status 1; after the solutions in `LAB_SOLUTIONS.md` it printed six `PASS` lines and `All tasks pass.` with exit status 0. Two builds produced identical commit hashes, so the hashes in the solutions match yours for every commit the script makes.

## The undo toolbox

### reset: three modes

`git reset <commit>` can do three things in order: move the branch HEAD points to; make the index match that commit; make the working directory match the index [153]. The mode decides where it stops [153]:

| Mode | Branch moves | Index reset | Working directory reset |
|---|---|---|---|
| `--soft` | yes | no | no |
| `--mixed` (default) | yes | yes | no |
| `--hard` | yes | yes | yes |

The course's test run tried each mode separately, each time starting from a repo with commits `one` and `two`, where `f.txt` contains `two` (the comments are added):

```console
$ git reset --soft HEAD~1
$ git status --short
M  f.txt                 # change still staged
$ git reset --mixed HEAD~1
Unstaged changes after reset:
M	f.txt                 # change kept, unstaged
$ git reset --hard HEAD~1
HEAD is now at b54453a one   # f.txt now contains "one"
```

`--hard` is one of the few Git commands that destroys data: a dropped commit can come back through the reflog, but uncommitted work it overwrites cannot [153]. `git reset --soft HEAD~2` followed by `git commit` squashes the last two commits into one [153]. With a path, `git reset file.txt` only unstages that file [153].

### revert: undo by adding a commit

`git revert <commit>` records a new commit that reverses the changes of an existing one [154]. Nothing is rewritten, so it is the safe undo for commits others already have. It needs a clean working tree [154]. Reverting a merge needs `-m 1` to say which parent is the mainline [154].

### reflog: the safety net

Reflogs record every time a branch tip or HEAD moved in your local repository [154]. `HEAD@{2}` is where HEAD was two moves ago; `main@{one.week.ago}` is where main pointed a week ago [154]. Unreachable entries expire after 30 days by default and others after 90, so recovery has a time limit [154].

### cherry-pick: copy a commit

`git cherry-pick <commit>` applies the change that commit introduced and records it as a new commit on the current branch [154]. On a conflict, fix the files, `git add`, then `git cherry-pick --continue`, or `--abort` [154]. `-x` adds a "(cherry picked from commit …)" line, useful for backports [154].

### stash: shelve work in progress

`git stash push` saves working-directory and index changes and resets the tree to HEAD; `-u` also takes untracked files, `-m` labels the entry [154]. `pop` applies and drops the newest entry, `apply` keeps it, and `git stash branch <name>` creates a branch from the commit where the stash was made, applies it there and drops it [154]. If `pop` hits a conflict the entry is kept; resolve, then `git stash drop` [154].

### bisect: binary search for the bad commit

`git bisect start <bad> <good>` then `git bisect run <cmd>` tests commits automatically: exit 0 means good, 1 to 127 (except 125) means bad, 125 means skip this commit [153] [154]. Finish with `git bisect reset`, which returns to where you started [153].

### push --force-with-lease

After a rebase or amend, a normal push is refused as a non-fast-forward [154]. `--force` overrides every safety check and can delete commits on the remote; `--force-with-lease` refuses unless the remote branch still matches your remote-tracking branch [154]. In the course's test run a second clone pushed to `topic` after the first clone's last fetch, and the first clone then amended and force-pushed:

```console
$ git push --force-with-lease origin topic
 ! [rejected]        topic -> topic (stale info)
error: failed to push some refs to '.../server.git'
```

A background `git fetch` (for example in an IDE) updates the tracking ref and silently defeats this protection [154].

## The tasks

`LAB_SOLUTIONS.md` has every command and its output. Try each task before reading it.

**6A. Shelve work in progress.** `main` has a modified `NOTES.md` and an untracked `scratch-plan.txt`. Stash both so the tree is clean. Hint: plain `git stash` leaves untracked files behind.

**1. Commit on the wrong branch.** `Add JSON output for report` sits on `docs`; move it to `feature/report` and remove it from `docs`. Hint: copy, then move `docs` back one commit.

**2. Lost commit.** A hard reset dropped `Tune retry backoff` from `experiment`. Hint: `git reflog experiment`.

**3. Find the bug.** `sh tests/run.sh` fails on `main` and passes on tag `v1.0`. Find the first bad commit with `git bisect run` and tag it `found-bug`. In the test run, four test runs covered 13 commits:

```console
$ git bisect start main v1.0
$ git bisect run sh tests/run.sh
Bisecting: 6 revisions left to test after this (roughly 3 steps)
...
145402b947cb677494b45cdd06d7525f1a780283 is the first 'bad' commit
```

**4. Undo a pushed commit.** `Switch default region to dc-test` is on `origin/release`. Undo it without rewriting history, then push.

**5. Rebase with a conflict.** Rebase `feature/quota` onto `main`. `README.md` conflicts; keep both command lines.

**6B. Restore the work.** Turn the stash into a branch `wip/notes` and commit it there.

## Which undo when

| Situation | Command |
|---|---|
| Last commit not pushed, want to redo it | `git reset --soft HEAD~1` or `git commit --amend` [153] |
| Commit already pushed | `git revert <commit>` [154] |
| Branch moved and a commit vanished | `git reflog <branch>`, then reset or branch to it [154] |
| Commit on the wrong branch | `git cherry-pick`, then reset the wrong branch [154] |
| Must switch branches mid-edit | `git stash push -u` [154] |
| Rewrote a branch you already pushed alone | `git push --force-with-lease` [154] |

## Gotchas

- **`reset --hard` with uncommitted work.** The reflog brings back commits, not edits you never committed. Run `git status` first, or stash. [153]
- **Resetting a pushed branch.** Others still have the old commits; use `revert` on shared branches. [153] [154]
- **Bisect test exit codes.** A script that exits 125 marks the commit as skipped, and a code above 127 aborts the bisect, so make the script exit 0 or 1. [154]
- **Forgetting `git bisect reset`.** HEAD is left wherever the search ended, which Pro Git calls a weird state. At the end `refs/bisect/bad` names the culprit, so tag it, then reset. [153] [154]
- **`stash` without `-u`.** Untracked files stay in the working tree and can block a branch switch. [154]
- **`--force-with-lease` after a background fetch.** The lease checks against a tracking ref that was refreshed behind your back; name the expected value with `--force-with-lease=<ref>:<expect>` when in doubt. [154]

:::key-takeaways
- `reset` moves the branch; `--soft` stops there, `--mixed` also resets the index, `--hard` also the working directory. [153]
- `revert` adds an inverse commit and is the undo for shared history. [154]
- The reflog keeps old branch positions locally for 30 to 90 days. [154]
- `git bisect run` turns a test script's exit status into a binary search. [154]
- Force-push with `--force-with-lease`, never plain `--force`. [154]
:::

:::glossary
- **Reflog**: a local log of where each branch and HEAD pointed over time.
- **Revert**: a new commit that applies the reverse of an earlier commit.
- **Cherry-pick**: copying one commit's change onto another branch as a new commit.
- **Stash**: a saved, shelved set of uncommitted changes.
- **Bisect**: a binary search through history for the commit that introduced a bug.
- **Remote-tracking branch**: your local copy of where a branch on the remote pointed at the last fetch.
- **Non-fast-forward**: a push that would drop commits on the remote, refused by default.
:::
