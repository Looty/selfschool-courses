---
id: l08
title: "Objects, branches, merge and rebase"
quiz: quiz-08.yaml
sources: [153, 154]
---
After this lesson you can explain what a commit, a branch and HEAD really are, predict whether a merge fast-forwards or creates a merge commit, resolve a conflict, and choose between merge and rebase with a reason.

## Objects: blob, tree, commit

Git is a key-value store: you give it content and it gives back a key, the SHA-1 of a short header plus the content [153]. Three object types carry history [153].

- A **blob** holds one file's contents; the file name is not in it.
- A **tree** is one directory: entries of mode, type, hash and name.
- A **commit** points to a top-level tree and to zero or more parents, and records author, committer and message.

Git stores snapshots, not lists of differences [153]. `git cat-file -p HEAD` prints the commit (its `tree` line, author, message); `-t` prints an object's type [153].

## Branches and HEAD

A branch is a movable pointer: a small file holding a 40-character commit hash [153]. **HEAD** points to the branch you are on (`.git/HEAD` holds `ref: refs/heads/main`), and a new commit moves only that branch [153].

Keep three "trees" in mind: **HEAD** (last commit), the **index** (proposed next commit) and the **working directory**. `git add` copies to the index; `git commit` snapshots the index and moves the branch [153].

## Merge: fast-forward or three-way

If the commit you merge is reachable by following history forward from where you are, Git only moves the pointer: a **fast-forward** [153]. When both branches have new commits, Git does a **three-way merge** of the two tips and their common ancestor and records a merge commit with more than one parent [153]. The default strategy is `ort` [154].

```console
$ git log --oneline --graph
*   832feb4 Merge branch 'feature'
|\
| * dac4a0b Bring up network
* | 7ffbb96 Set cpus
|/
* 044e0a7 Set memory
```

Three flags change the shape [154].

```bash
git merge --no-ff feature    # always make a merge commit
git merge --ff-only feature  # refuse unless a fast-forward is possible
git merge --squash tidy      # result in index and tree, no commit, no second parent
```

## Conflicts

When both sides changed the same lines, Git stops and writes markers [153].

```text
<<<<<<< HEAD
memory_mib: 1024      # your checked-out branch
=======
memory_mib: 4096      # the branch being merged in
>>>>>>> bigger
```

Edit to the result you want, delete the markers, `git add` the file, then `git commit` [153]. `git merge --abort` may not restore uncommitted changes, so commit or stash first [154].

## Rebase

Rebase replays each of your commits on top of another commit [153]. They get new hashes; the old tip stays in the reflog and in `ORIG_HEAD` [154]. `--onto` moves only part of a stack [153], and `-i` edits the list of commits [153] [154].

```bash
git rebase main                        # replay topic's commits onto main
git rebase --onto main server client   # move only client's own commits
git rebase -i HEAD~3                   # pick, reword, squash, fixup, drop...
git rebase --continue                  # after fixing a conflict and git add
git rebase --abort                     # go back
```

## Merge or rebase?

The final snapshot is the same; only the history differs [153]. Merge keeps commits and records what happened; rebase replaces them with copies and gives linear history. The rule: rebase local work before pushing, but never rebase commits others may have built on [153]. Rewriting them forces everyone downstream to repair their history [154].

## Gotchas

- **"Ours" flips during a rebase.** The `HEAD` side is the branch you rebase onto; "theirs" is your own commit [154].
- **`--squash` loses the link.** No second parent is recorded, so history does not show the merge [154].

:::key-takeaways
- Blob = file contents, tree = directory listing, commit = tree + parents + metadata; all addressed by hash. [153]
- A branch is a file holding one hash; HEAD names the current branch. [153]
- Fast-forward moves a pointer; a three-way merge makes a commit with two parents. [153]
- Rebase replays patches as new commits; never rebase commits others may have built on. [153]
:::

:::glossary
- **HEAD**: the pointer to the branch (or commit) you currently have checked out.
- **Index**: the staging area that holds what the next commit will contain.
- **Fast-forward**: a merge that only moves the branch pointer because there is nothing to combine.
:::
