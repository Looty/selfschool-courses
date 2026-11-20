---
id: l09
title: "Lab: undo, recover and find the bad commit"
quiz: quiz-09.yaml
resources: [../resources/ch03/make_lab_repo.sh, ../resources/ch03/check_lab.sh, ../resources/ch03/LAB_SOLUTIONS.md]
sources: [153, 154]
---
After this lab you can pick the right undo command for a mistake (reset, revert, reflog, cherry-pick, stash), find a regression with `git bisect run`, and force-push without clobbering a colleague's work.

## The undo toolbox

### reset: three modes

`git reset <commit>` moves the branch HEAD points to, then optionally resets the index, then the working directory [153].

| Mode | Branch | Index | Working dir |
|---|---|---|---|
| `--soft` | moves | kept | kept |
| `--mixed` (default) | moves | reset | kept |
| `--hard` | moves | reset | reset |

`--hard` destroys data: a dropped commit comes back through the reflog, uncommitted work does not [153]. `git reset file.txt` only unstages that file [153].

### revert, reflog, cherry-pick, stash

All from the Git reference [154].

```bash
git revert <commit>          # new commit with the inverse change; needs a clean tree
git revert -m 1 <merge>      # reverting a merge: -m names the mainline parent
git reflog experiment        # every position the branch had, as experiment@{N}
git cherry-pick <commit>     # copy that change as a new commit here
git stash push -u -m "wip"   # shelve changes, -u includes untracked files
git stash pop                # apply and drop (kept if it conflicts)
git stash branch <name>      # new branch from the stash's commit, apply, drop
```

Revert rewrites nothing, so it is the undo for commits others already have [154]. Reflog entries expire (30 days for unreachable ones, 90 for others) [154].

### bisect: binary search

`git bisect run` reads the test's exit status: 0 is good, 1 to 127 (except 125) is bad, 125 is skip [153] [154]. `git bisect reset` returns to where you started [153].

```bash
git bisect start <bad> <good>
git bisect run sh tests/run.sh
git bisect reset
```

### push --force-with-lease

After a rebase, a normal push is refused [154]. `--force` can delete others' commits; `--force-with-lease` refuses (`stale info`) unless the remote branch still matches your remote-tracking branch [154]. A background `git fetch` silently defeats this check [154].

## The lab (40 min)

Needs Git and Bash. From `resources/ch03`:

1. `bash make_lab_repo.sh ~/git-lab`, then `cd ~/git-lab/repo && git log --oneline --graph --all`.
2. Solve the tasks in this order: 6A, 1, 2, 3, 4, 5, 6B.
3. `bash /path/to/resources/ch03/check_lab.sh ~/git-lab` until it prints `All tasks pass.`
4. Then read `LAB_SOLUTIONS.md`; its hashes match the ones the script made.

**6A.** `main` has a modified `NOTES.md` and an untracked `scratch-plan.txt`. Stash both.

**1.** `Add JSON output for report` sits on `docs`; move it to `feature/report` and remove it from `docs`.

**2.** A hard reset dropped `Tune retry backoff` from `experiment`. Get it back.

**3.** `sh tests/run.sh` fails on `main` and passes on tag `v1.0`. Find the first bad commit with `git bisect run` and tag it `found-bug`.

**4.** `Switch default region to dc-test` is on `origin/release`. Undo it without rewriting history, then push.

**5.** Rebase `feature/quota` onto `main`. `README.md` conflicts; keep both command lines.

**6B.** Turn the stash into a branch `wip/notes` and commit it there.

## Which undo when

| Situation | Command |
|---|---|
| Last commit not pushed | `git reset --soft HEAD~1` or `git commit --amend` [153] |
| Commit already pushed | `git revert <commit>` [154] |
| A commit vanished | `git reflog <branch>`, then reset to it [154] |
| Commit on the wrong branch | `git cherry-pick`, then reset the wrong branch [154] |
| Switch branches mid-edit | `git stash push -u` [154] |
| Rewrote a branch you pushed alone | `git push --force-with-lease` [154] |

## Gotchas

- **Bisect exit codes.** A test that exits 125 skips every commit; above 127 aborts the bisect. Exit 0 or 1. [154]
- **Forgetting `git bisect reset`.** Tag `refs/bisect/bad` first, then reset. [153] [154]

:::key-takeaways
- `reset` moves the branch; `--soft` stops there, `--mixed` also resets the index, `--hard` also the working directory. [153]
- `revert` adds an inverse commit and is the undo for shared history. [154]
- The reflog keeps old branch positions locally for 30 to 90 days. [154]
- `git bisect run` turns a test script's exit status into a binary search. [154]
- Force-push with `--force-with-lease`, never plain `--force`. [154]
:::

:::glossary
- **Reflog**: a local log of where each branch and HEAD pointed over time.
- **Remote-tracking branch**: your local copy of where a branch on the remote pointed at the last fetch.
:::
