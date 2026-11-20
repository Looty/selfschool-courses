---
id: l09
title: "Lab: undo, recover and find the bad commit"
quiz: quiz-09.yaml
resources: [../resources/ch03/make_lab_repo.sh, ../resources/ch03/check_lab.sh, ../resources/ch03/LAB_SOLUTIONS.md]
sources: [153, 154]
---
After this lab you can pick the right undo and find a bad commit with `git bisect run`. Test repo (Git 2.55): commit A wrote `v1` into `f.txt`, commit B changed it to `v2`.

## reset: move the branch, then maybe overwrite

**Prerequisite:** a file has three copies: the last commit (HEAD), the **index** (staging area: your next commit) and the disk (working directory) [153].

**Rule:** `git reset X` always moves the current branch to X; `--soft` stops there, `--mixed` (the default) also copies X into the index, `--hard` also onto disk [153]. Hook: soft, mixed, hard touch 1, 2, 3 places.

```console
$ git reset --soft HEAD~1      # each reset run separately from B
$ git status --short
M  f.txt                       # change still staged
$ git reset --mixed HEAD~1
Unstaged changes after reset:
M	f.txt
$ git reset --hard HEAD~1
HEAD is now at b9a41ec A
```

| From B | branch | index | disk |
| --- | --- | --- | --- |
| `reset --soft HEAD~1` | A | v2 | v2 |
| `reset HEAD~1` (mixed) | A | v1 | v2 |
| `reset --hard HEAD~1` | A | v1 | v1 |

Edge case: `git reset f.txt` (a path) moves nothing and only unstages that file [153].

**P1.** At B with a clean tree you run `git reset HEAD~1`, no flag. What does `f.txt` contain on disk?

## reflog: find a commit that vanished

**Rule:** the reflog is a local diary of every place HEAD and each branch pointed, so a commit dropped by reset is still listed [154].

```console
$ git reset --hard HEAD~1
HEAD is now at b9a41ec A
$ git reflog                   # git log now shows only A
b9a41ec HEAD@{0}: reset: moving to HEAD~1
6934894 HEAD@{1}: commit: B    # still here
b9a41ec HEAD@{2}: commit (initial): A
$ git reset --hard HEAD@{1}
HEAD is now at 6934894 B
```

Edge cases: `HEAD@{1}` means "one move ago" [154]. Uncommitted edits are never logged: `reset --hard` wiped an unsaved `v3`, and recovery brought back only `v2` [153]. Entries expire after 30 to 90 days [154].

**P2.** Right after `git reset --hard HEAD~1` you commit C, then run `git reflog`. Is B still `HEAD@{1}`?

## revert vs reset: add an undo, or rewind

**Rule:** `git revert X` adds a new commit that does the opposite of X; nothing is rewritten, so it is the undo for pushed commits [154].

```console
$ git revert --no-edit HEAD    # at B
$ git log --oneline
b80bc71 Revert "B"             # f.txt back to v1
6934894 B                      # B is still there
b9a41ec A
```

Edge case: revert needs a clean working tree [154]; with an edited `f.txt` it refused.

| From A, B | `reset --hard HEAD~1` | `revert HEAD` |
| --- | --- | --- |
| History (`f.txt` = v1 in both) | A | A, B, Revert "B" |
| Safe after push | no [153] | yes [154] |

**P3.** B is on `origin/main` and a colleague pulled it. Which undo do you use?

## bisect: binary search for the first bad commit

**Rule:** from one good and one bad commit, bisect tests the middle and halves the range until one commit is left [153]. `git bisect run` reads the test's exit status: 0 good, 1 to 127 bad except 125, 125 skip [153] [154].

```console
# c1 (good) to c8 (bad); the bug was born in c6
$ git bisect start main good
$ git bisect run sh ../test.sh    # output shortened
[a0ea6a4...] c4                    # passes: bug is later
[faf37f7...] c6                    # fails: c6 or earlier
[e555f2a...] c5                    # passes: so c6
faf37f7... is the first 'bad' commit
$ git bisect reset                 # back to where you started
```

8 commits, 3 tests. Edge case: a test that always exits 125 skips everything: `We cannot bisect more!`.

**P4.** About how many tests does bisect need for 1,000 commits?

## The lab (40 min)

Git and Bash, from `resources/ch03`:

1. `bash make_lab_repo.sh ~/git-lab`, then `cd ~/git-lab/repo && git log --oneline --graph --all`.
2. Solve in order: 6A, 1, 2, 3, 4, 5, 6B.
3. `bash /path/to/resources/ch03/check_lab.sh ~/git-lab` until it prints `All tasks pass.` Then read `LAB_SOLUTIONS.md`.

**6A.** `main` has a modified `NOTES.md` and an untracked `scratch-plan.txt`. Stash both.

**1.** `Add JSON output for report` sits on `docs`; move it to `feature/report` and remove it from `docs`.

**2.** A hard reset dropped `Tune retry backoff` from `experiment`. Get it back.

**3.** `sh tests/run.sh` fails on `main` and passes on tag `v1.0`. Find the first bad commit with `git bisect run` and tag it `found-bug`.

**4.** `Switch default region to dc-test` is on `origin/release`. Undo it without rewriting history, then push.

**5.** Rebase `feature/quota` onto `main`. `README.md` conflicts; keep both command lines.

**6B.** Turn the stash into a branch `wip/notes` and commit it there.

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| `reset --soft` / (mixed) / `--hard` | branch; + index; + disk | from B: staged / unstaged / gone |
| `reflog` | every past HEAD position | `HEAD@{1}` → B |
| `revert X` | new opposite commit | A, B, Revert |
| `bisect run cmd` | 0 good, 1-127 bad, 125 skip | 8 commits → 3 tests |
| `cherry-pick X` | copy X's change here as a new commit [154] | task 1 |
| `stash push -u` / `stash branch n` | shelve edits incl. untracked / restore on a new branch [154] | tasks 6A, 6B |
| rebase conflict | fix the file, `git add`, `git rebase --continue` [154] | task 5 |

## Answers

**P1.** v2. Mixed resets the index, not the disk; the change shows unstaged.

**P2.** No. C is `HEAD@{0}`, the reset `HEAD@{1}`, B `HEAD@{2}`.

**P3.** `git revert`: it adds a commit instead of removing B.

**P4.** About 10: each test halves the range; 2^10 = 1,024.

**R1.** `--mixed`.

**R2.** No; only committed states are logged.

**R3.** Yes; nothing is rewritten.

**R4.** Skip that commit.

## If you missed a quiz question

| If you thought... | Reread | Re-check |
| --- | --- | --- |
| No flag means `--hard` | reset | **R1.** Which mode is the default? |
| The reflog saves uncommitted edits | reflog | **R2.** Can it restore a never-committed edit? |
| Revert deletes the commit | revert vs reset | **R3.** Is B still in `git log` after `git revert B`? |
| Any non-zero exit means "bad" | bisect | **R4.** What does exit 125 mean? |

:::key-takeaways
- `reset` moves the branch; `--mixed` also resets the index, `--hard` also the disk. [153]
- The reflog finds dropped commits, not uncommitted edits; `revert` undoes shared history. [154]
:::

:::glossary
- **Index**: the staging area that holds what the next commit will contain.
- **Reflog**: a local log of where each branch and HEAD pointed over time.
:::
