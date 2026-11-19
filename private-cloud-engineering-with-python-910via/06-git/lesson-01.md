---
id: l16
title: "Objects, branches, merge and rebase"
quiz: quiz-01.yaml
sources: [153, 154]
---
After this lesson you can explain what a commit, a branch and HEAD really are, predict whether a merge fast-forwards or creates a merge commit, resolve a conflict, and choose between merge and rebase with a reason.

Every output below comes from a throwaway repository built in the course's test run with Git 2.55.0.windows.3 in Git Bash, with a fixed author and fixed dates.

## Objects: blob, tree, commit

At its core Git is a key-value store: you give it content and it gives back a key, the SHA-1 of a short header plus the content [153]. `git hash-object` computes that key; with `-w` it also writes the object into `.git/objects` [153].

```console
$ printf "hello\n" | git hash-object --stdin
ce013625030ba8dba906f756967f9e9ca394464a
```

Three object types carry a project's history [153]:

- A **blob** holds the contents of one file and nothing else; the file name is not in it.
- A **tree** is one directory: each entry has a mode, a type, a hash and a name. Mode `100644` is a normal file, `100755` executable, `120000` a symlink, `040000` a subdirectory.
- A **commit** points to the top-level tree of a snapshot and to zero, one or more parents, and records author, committer and message.

Git stores snapshots, not lists of differences [153]. After a first commit of `vm.yaml` and `lib/boot.sh`, the repository held five objects: two blobs, two trees (root and `lib`) and one commit. Each file is named by the first two hex characters of the hash (the directory) and the remaining 38 [153].

```console
$ git cat-file -p HEAD
tree a48c777e12ab03ef2c7cc63a01d5b539babb2628
author Lab User <lab@example.com> 1767600000 +0000
committer Lab User <lab@example.com> 1767600000 +0000

Add VM spec
$ git cat-file -p HEAD^{tree}
040000 tree e2a0824373c7ca7d6a4cceb0eda2b92da5721eb8	lib
100644 blob 9860ccf50df12ed127935c5854152f54d1fed81d	vm.yaml
```

`git cat-file -p` prints an object and `-t` prints its type [153].

## Branches and HEAD

A branch is a movable pointer to a commit: a small file holding the 40-character hash, so creating one costs about 41 bytes [153]. **HEAD** points to the branch you are on [153]. A new commit moves only the branch HEAD points to [153].

```console
$ cat .git/HEAD
ref: refs/heads/main
$ cat .git/refs/heads/main
f729253c9c7bc898af1df8883a656a3ba5665f79
```

Pro Git describes three "trees" (collections of files): **HEAD**, the last commit and the parent of the next one; the **index** (staging area), the proposed next commit; and the **working directory**, where you edit [153]. `git add` copies from the working directory to the index; `git commit` turns the index into a snapshot and moves the branch [153]. The next lesson uses this model to explain `reset`.

## Merging: fast-forward or three-way

If the commit you merge in is reachable by following history forward from where you are, there is nothing to combine and Git only moves the pointer: a **fast-forward** [153].

```console
$ git merge hotfix
Updating f729253..044e0a7
Fast-forward
 vm.yaml | 1 +
 1 file changed, 1 insertion(+)
```

When both branches have new commits, Git does a **three-way merge** using the two branch tips and their common ancestor, and records a merge commit with more than one parent [153]. The default strategy for merging one branch is `ort`; `recursive` is now a synonym for it [154]. Pro Git's sample output still prints `recursive` [153].

```console
$ git merge --no-edit feature
Merge made by the 'ort' strategy.
 lib/boot.sh | 1 +
 1 file changed, 1 insertion(+)
$ git log --oneline --graph
*   832feb4 Merge branch 'feature'
|\
| * dac4a0b Bring up network
* | 7ffbb96 Set cpus
|/
* 044e0a7 Set memory
* f729253 Add VM spec
```

Two flags change the shape [154]:

- `--no-ff` always creates a merge commit, even when a fast-forward is possible, so the branch stays visible in history. `--ff-only` refuses unless a fast-forward is possible.
- `--squash` builds the merged result in the index and working tree but makes no commit and records no second parent; your next `git commit` adds one ordinary commit.

```console
$ git merge --squash tidy
Updating f441d08..a879b40
Fast-forward
Squash commit -- not updating HEAD
 lib/boot.sh | 2 ++
 1 file changed, 2 insertions(+)
$ git status --short
M  lib/boot.sh
```

## Conflicts

When both sides changed the same lines, Git stops and writes markers into the file [153]. The index then holds up to three versions of the path: stage 1 the common ancestor, stage 2 HEAD, stage 3 the other branch [154].

```console
$ git merge bigger
Auto-merging vm.yaml
CONFLICT (content): Merge conflict in vm.yaml
Automatic merge failed; fix conflicts and then commit the result.
$ cat vm.yaml
name: vm-01
<<<<<<< HEAD
memory_mib: 1024
=======
memory_mib: 4096
>>>>>>> bigger
cpus: 2
```

The part above `=======` is your checked-out branch [153]. Edit the file to the result you want, delete the marker lines, `git add` the file to mark it resolved, then `git commit` [153]. `git merge --abort` tries to return to the state before the merge, but may not restore uncommitted changes, so commit or stash before merging [154]. Setting `merge.conflictStyle` to `diff3` adds a section with the ancestor's text, which often makes the right answer obvious [154].

## Rebase

Rebase takes the changes each of your commits introduced and replays them on top of another commit [153]. `git rebase main` on `topic` finds the commits since the two diverged, checks out `main`, reapplies them one by one, then moves `topic` to the last one [154].

```console
$ git rebase main
Rebasing (1/2)
Rebasing (2/2)
Successfully rebased and updated refs/heads/topic.
$ git reflog -3 topic
b8cb75b topic@{0}: rebase (finish): refs/heads/topic onto 87eda30593906301812345c62f710413b675b91a
5d9ced9 topic@{1}: commit: Grow disk
9a4afa1 topic@{2}: commit: Add disk spec
```

The commits got new hashes; the old tip is still in the reflog as `@{1}`, and `ORIG_HEAD` holds it too [154]. Afterwards `git merge topic` on `main` is a fast-forward [153].

`--onto` moves only part of a stack. `client` was branched from `server`; to ship `client` without `server`'s commits [153]:

```console
$ git rebase --onto main server client
Successfully rebased and updated refs/heads/client.
```

`git rebase -i HEAD~3` opens a todo list, oldest commit first, where each line can become `pick`, `reword`, `edit`, `squash`, `fixup` (squash and discard this message), `drop` or `exec` [153] [154]. In the test run, changing line 2 to `fixup` folded a "fix typo" commit into its parent:

```text
pick 1cde429 # Add image spec
fixup f55c157 # fix typo
pick 9475a16 # Add owner
```

On a conflict, rebase stops at that commit: fix it, `git add`, then `git rebase --continue`, or `--skip` the commit, or `--abort` to go back [154].

## Merge or rebase?

| | Merge | Rebase |
|---|---|---|
| Existing commits | Kept unchanged | Replaced by new copies |
| History | Records what actually happened, with merge commits | Linear, as if the work happened in series |
| Final snapshot | Same | Same |
| Safe on pushed branches | Yes | No |

The end snapshot is the same either way; only the history differs [153]. Pro Git's rule: rebase local work before pushing to tidy it, but never rebase commits that exist outside your repository and that others may have built on [153]. Rewriting them forces everyone downstream to repair their history by hand [154].

## Gotchas

- **Rebasing a shared branch.** The old commits live on in colleagues' clones and come back as duplicates with the same author and message. Rebase only unpushed work. [153]
- **"Ours" flips during a rebase.** In a rebase conflict the `HEAD` side is the branch you rebase onto plus commits replayed so far, and "theirs" is your own commit, the reverse of a merge. [154]
- **Expecting a merge commit.** A plain `git merge` fast-forwards when it can, leaving no trace of the branch. Use `--no-ff` if your team wants one. [154]
- **`--squash` loses the link.** No second parent and no `MERGE_HEAD` are recorded, so history does not show that the branch was merged; the branch's own commits stay outside `main`. [154]
- **Merging with a dirty tree.** `git merge --abort` may not bring back uncommitted changes. Commit or stash first. [154]
- **Trusting old book output.** Pro Git's samples print the `recursive` strategy; current Git uses `ort` by default. [153] [154]

:::key-takeaways
- Blob = file contents, tree = directory listing, commit = tree + parents + metadata; all addressed by hash. [153]
- A branch is a file holding one hash; HEAD names the current branch. [153]
- Fast-forward moves a pointer; a three-way merge makes a commit with two parents. [153]
- Rebase replays patches as new commits; the snapshot matches a merge, the history does not. [153]
- Never rebase commits others may have built on. [153]
:::

:::glossary
- **Blob**: a stored file content, without its name.
- **Tree**: a stored directory listing that maps names to blobs and other trees.
- **Commit**: a stored snapshot pointer with parents, author and message.
- **HEAD**: the pointer to the branch (or commit) you currently have checked out.
- **Index**: the staging area that holds what the next commit will contain.
- **Fast-forward**: a merge that only moves the branch pointer because there is nothing to combine.
- **Three-way merge**: a merge that compares both branch tips with their common ancestor.
- **Merge commit**: a commit with two or more parents.
- **Rebase**: replaying your commits on top of a different base, producing new commits.
- **Reflog**: a local log of where each branch and HEAD pointed over time.
:::
