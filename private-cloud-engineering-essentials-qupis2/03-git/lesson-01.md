---
id: l08
title: "Objects, branches, merge and rebase"
quiz: quiz-08.yaml
sources: [153, 154]
---
After this lesson you can say what a commit, a branch and HEAD are, predict whether a merge fast-forwards, and choose merge or rebase with a reason. Outputs are from a test repository (Git 2.55).

## Git objects: blob, tree, commit

**Rule:** a **blob** is one file's contents, a **tree** is one folder (names pointing to blobs), a **commit** points to one tree plus its parents; each is named by the SHA-1 hash of its content [153].

```console
$ printf "hello\n" | git hash-object --stdin
ce013625030ba8dba906f756967f9e9ca394464a     # same content = same name, on any machine
$ printf "hello\n" > a.txt; cp a.txt b.txt   # two files, identical contents
$ git add . && git commit -qm A
$ git cat-file -p HEAD                       # -p: print. No parent line: first commit
tree b5b0cccf7401633f12e0fafc6b85731251b86850
author L <l@x> 1767225600 +0000
committer L <l@x> 1767225600 +0000

A
$ git cat-file -p HEAD^{tree}
100644 blob ce013625030ba8dba906f756967f9e9ca394464a	a.txt
100644 blob ce013625030ba8dba906f756967f9e9ca394464a	b.txt
```

Edge case: two files, **one** blob; the repository held 3 objects. The file name lives in the tree, never in the blob [153]. Git stores snapshots, not differences [153].

**P1.** You rename `b.txt` to `c.txt` and commit. Does Git store a new blob?

:::answer
No. Same contents, same blob hash; Git writes only a new tree and commit (the rename added two objects in the test repo).
:::

## A branch is a pointer, HEAD names the branch

**Rule:** a branch is a tiny file holding one commit hash; `HEAD` holds the name of your current branch, and a commit moves only that branch [153].

```console
$ cat .git/HEAD
ref: refs/heads/main
$ wc -c < .git/refs/heads/main
41                                # 40 hex characters + newline
$ git branch feature              # one more 41-byte file; nothing copied
```

| Step (start: commit A) | main | feature | HEAD |
| --- | --- | --- | --- |
| `git switch -c feature` | A | A | feature |
| `git commit -m B` | A | B | feature |
| `git switch main`, `git commit -m C` | C | B | main |

**P2.** A repository is 2 GB. Roughly how much does `git branch hotfix` write?

:::answer
About 41 bytes: one file with a 40-character hash and a newline.
:::

## Merge: fast-forward or three-way

**Rule:** if your branch has no new commits of its own, merge just slides your pointer forward (**fast-forward**); if both sides moved, Git combines both tips with their common ancestor into a **merge commit** with two parents [153].

```console
$ git merge feature              # repo 1: main at A, feature at B
Updating 9145479..12e9981
Fast-forward
$ git merge --no-edit feature    # repo 2: main at C, feature at B
Merge made by the 'ort' strategy.
$ git log --oneline --graph
*   a72c3f1 Merge branch 'feature'
|\
| * 9c775df B
* | 9cac067 C
|/
* 4ed7ade A
```

`ort` is the default strategy; `--no-ff` forces a merge commit [154]. Edge case: if both sides changed the same lines, Git stops with a conflict [153].

**P3.** `main` is at A; `feature` has A, B, C. On `main` you run `git merge feature`. How many new commits appear?

:::answer
None: `main` has nothing of its own, so it fast-forwards to C.
:::

## Merge or rebase: same files, different history

**Rule:** rebase replays your commits on top of the other branch as **copies with new hashes**; merge keeps them and adds a merge commit [153].

```console
$ git branch backup feature                  # repo 2 again, before merging
$ git switch feature && git rebase main
Successfully rebased and updated refs/heads/feature.
$ git log --oneline --graph --all
* 9c775df B                 # old B, still on backup
| * 8ac974d B               # the copy, on top of C
| * 9cac067 C
|/
* 4ed7ade A
$ git switch main && git merge feature
Updating 9cac067..8ac974d
Fast-forward
```

The old tip stays in the reflog and `ORIG_HEAD` [154]. B's hash changed because a commit records its parent.

| Same history | `git merge feature` on main | `git rebase main` on feature |
| --- | --- | --- |
| Commits after | A, B, C, merge | A, C, B' (new hash) |
| Shape | fork and join | straight line |
| Final files | same | same |
| Safe on pushed commits | yes | no |

Only history differs [153]. Rebase local work before pushing, never commits others may have built on [153]; rewriting them forces everyone downstream to repair their history [154].

**P4.** You rebase `feature`, which a colleague already pulled. Why does B show up twice after their next pull?

:::answer
They still have old B; you have B' with a new hash. Two commits, same message; merging brings in both.
:::

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| blob, tree, commit | contents, folder, snapshot + parents | 2 identical files → 1 blob |
| branch | 41-byte file holding a hash | `git branch x` copies nothing |
| `HEAD` | names the current branch | `ref: refs/heads/main` |
| `git merge` | fast-forward if one side moved | else a 2-parent commit |
| `git rebase main` | replay commits on main | B → B' with a new hash |

## If you missed a quiz question

**If you thought** every merge creates a merge commit: reread "Merge". **R1.** `main` at A, `feature` at B. What does merging do?

:::answer
A fast-forward: the pointer just moves.
:::

**If you thought** the blob stores the file name: reread "Git objects". **R2.** Which object holds file names?

:::answer
The tree.
:::

**If you thought** rebase keeps the same commits: reread "Merge or rebase". **R3.** Does a new parent mean a new hash?

:::answer
Yes: the hash covers the parent.
:::

**If you thought** rebasing a pushed branch is harmless: reread "Merge or rebase". **R4.** Merge or rebase a branch colleagues pulled?

:::answer
Merge: never rebase commits others have.
:::

**If you thought** a commit moves every branch: reread "Branch". **R5.** On `feature` you commit. Which branch moves?

:::answer
Only `feature` (and HEAD, which names it).
:::

:::key-takeaways
- Blob = contents, tree = folder, commit = tree + parents; all named by hash. [153]
- A branch is a file holding one hash; a commit moves only the current branch. [153]
- Rebase makes copies with new hashes; never rebase shared commits. [153]
:::

:::glossary
- **Blob**: a stored file content, without its name.
- **Tree**: a stored folder listing that maps names to blobs and other trees.
- **HEAD**: the pointer to the branch you currently have checked out.
- **Fast-forward**: a merge that only moves the branch pointer because there is nothing to combine.
- **Reflog**: a local log of where each branch and HEAD pointed over time.
- **SHA-1**: the hash function Git uses to turn content into a 40-character name.
:::
