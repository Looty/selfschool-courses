---
id: l11
title: "Reading resolver conflicts and broken environments"
quiz: quiz-02.yaml
resources: [../resources/lab-deps-demo.sh]
sources: [9, 28, 29]
---
After this lesson you can read a `ResolutionImpossible` error and name the two requirements that collide, find a broken environment with `pip check`, and trace who needs a package with `pipdeptree --reverse`.

## Why resolvers backtrack

pip resolves by making assumptions and checking them. When it finds an earlier assumption was wrong, it backtracks and tries another candidate version. pip's documentation calls this expected behaviour, not a bug, and warns it can take a long time when a package has many versions. [29] When you see `pip is looking at multiple versions of X ... This could take a while`, pip is backtracking through X's versions.

## Reading `ResolutionImpossible`

pip's documentation uses made-up packages (`package_coffee`, `package_tea`, `package_water`) to show the shape. Two top-level packages need incompatible versions of a third. [29] Here is the same shape with real packages, from the chapter's demo script:

```text
$ pip install 'requests==2.32.3' 'urllib3<1.21'
ERROR: Cannot install requests==2.32.3 and urllib3<1.21 because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested urllib3<1.21
    requests 2.32.3 depends on urllib3<3 and >=1.21.1

To fix this you could try to:
1. loosen the range of package versions you've specified
2. remove package versions to allow pip to attempt to solve the dependency conflict

ERROR: ResolutionImpossible: ...
```

Read it in three passes:

1. **The headline** names the top-level requirements that cannot coexist.
2. **"The conflict is caused by"** lists one line per side. Each line is either "The user requested" (you, or a requirements file) or "X depends on" (metadata of a package). Put the ranges side by side: `<1.21` and `>=1.21.1,<3` have no overlap.
3. **Decide whose range moves.** pip's guide lists four strategies. Audit your top-level requirements and drop stale ones. Loosen your own ranges. Get the dependency's maintainers to loosen theirs, or fork it, which costs you their support. And if every range is right and still no solution exists, pick a different package or refactor. [29]

## Environments break after install

The resolver only protects the packages in the current command. pip says it may break packages that are already installed and does not guarantee the environment stays consistent. [9] `--no-deps`, manual `pip install` on a live host, and installs from two tools into one venv all leave room for that. The demo forces it:

```text
$ pip install 'requests==2.32.3'
$ pip install --no-deps 'urllib3==1.20'
$ pip check
requests 2.32.3 has requirement urllib3<3,>=1.21.1, but you have urllib3 1.20.
```

`pip check` reports inconsistencies in what is installed. [9] It exited with status 1 in the demo, so it can gate a CI job or a container build: add `RUN pip check` after the install layer.

## Who needs what: pipdeptree

`pip freeze` gives a flat list. `pipdeptree` adds the parent–child relationships and reports conflicts and cycles. [28] Against the same broken environment:

```text
$ pipdeptree --python /tmp/c/bin/python -p requests
Warning: dependency problems found:
* requests==2.32.3
  - urllib3 [required: >=1.21.1,<3, installed: 1.20]
------------------------------------------------------------------------

requests==2.32.3
├── certifi [required: >=2017.4.17, installed: 2026.10.23]
├── charset-normalizer [required: >=2,<4, installed: 3.5.2]
```

The reverse view answers "who pulled this in?", which is the question before every forced upgrade or removal: [28]

```bash
pipdeptree --reverse --packages urllib3
```

`--python` points pipdeptree at another environment's interpreter, so the tool itself does not need to live in the venv you inspect. The pipdeptree page section read for this course does not document `--python`; it is shown working in the demo script. Check `pipdeptree --help` for your version.

## A routine for "pip can't install this"

1. Read the "conflict is caused by" lines and write the ranges down.
2. `pipdeptree --reverse --packages <the shared dependency>` in a working environment, to see every consumer.
3. Change the narrowest range you own; add a constraints file (lesson 10) if the cap must apply across the build.
4. After installing, run `pip check`.

:::key-takeaways
- Backtracking is normal; long backtracking points at a dependency with many candidate versions. [29]
- `ResolutionImpossible` lists each side of the conflict: "The user requested" vs "X depends on". [29]
- pip's four strategies: audit, loosen your ranges, get dependencies loosened, or change the design. [29]
- `pip check` finds inconsistencies already installed; pip does not guarantee consistency across commands. [9]
- `pipdeptree --reverse --packages X` shows who requires X. [28]
:::

:::glossary
- **Resolver**: the part of pip that picks one version of every package so that all requirements are satisfied.
- **Backtracking**: undoing an earlier version choice and trying another.
- **`ResolutionImpossible`**: pip's error when no set of versions satisfies every requirement.
- **Top-level requirement**: a package you asked for directly, as opposed to one pulled in by another package.
- **`pip check`**: a command that reports installed packages whose requirements are not met.
- **pipdeptree**: a tool that prints installed packages as a dependency tree.
- **Fork**: your own copy of someone else's project that you maintain.
:::
