---
id: l05
title: "Ranges, locks and resolver conflicts"
quiz: quiz-01.yaml
resources: [../resources/lab-deps-demo.sh]
sources: [9, 10, 21, 27, 28, 29, 30]
---
After this lesson you can decide where a version range belongs and where an exact pin belongs, produce a lock with uv or pip-tools, make CI fail on a stale lock or a bad hash, read a `ResolutionImpossible` error, and find a broken environment with `pip check` and `pipdeptree`.

## Ranges for libraries, locks for applications

The PyPA draws the line like this. A project's metadata says what it **minimally** needs to run, and pinning those to exact versions is not good practice. Requirements files usually describe a **whole environment**, often as pinned versions, sometimes tied to one index. [30] In practice:

| | Library (`packaging`, your client SDK) | Application you deploy (a service, a CLI in a .deb) |
|---|---|---|
| `pyproject.toml` | ranges such as `packaging>=23` | ranges too |
| Lock | none | every package, transitive ones included, at one exact version, ideally with hashes |

If a library pinned `==26.3`, every application that also needs `packaging` would be forced onto that exact version. pip's own advice matches: lock during development so deployment does not repeat the resolution. [29]

## Locking with uv

`uv lock` resolves the project and writes `uv.lock`; `uv sync` installs from it. [21] On the lab project:

```text
$ uv lock
Resolved 2 packages in 366ms
$ grep -A3 '^name = "packaging"' uv.lock
name = "packaging"
version = "26.3"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "https://files.pythonhosted.org/.../packaging-26.3.tar.gz", hash = "sha256:94edc2...", ... }
```

Each entry records the version, the index it came from and the file hashes. Two flags matter in CI: `uv sync --locked` raises an error if the lock is out of date instead of quietly updating it, and `uv sync --frozen` uses the lock without checking it. [21] After adding `click>=8` to `pyproject.toml` without relocking:

```text
$ uv sync --locked
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
```

`uv export --format requirements.txt` writes the lock out for tools that only read requirements files. [21]

## Locking with pip-tools

`pip-compile` turns `requirements.in`, or the dependencies in `pyproject.toml`, into a pinned `requirements.txt`. `--generate-hashes` adds hashes, `--upgrade` and `--upgrade-package` move pins on purpose, and `pip-sync` installs, upgrades and uninstalls until the environment matches the file. [27] From the lab project:

```text
click==8.5.0 \
    --hash=sha256:255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360 \
    --hash=sha256:ba0d2089de75ea0310e2dde03160e6ca10009947fb95a182f9b54021bb272e34
    # via shiplab-devenv (pyproject.toml)
```

There are two hashes because one release has two files, a wheel and an sdist. Hash-checking needs a hash for every file you are willing to accept. [10] For layered files, start `dev-requirements.in` with `-c requirements.txt`, so dev tools are constrained to the same pins as production. [27]

A **constraints file** looks like a requirements file but only controls which version gets installed. Listing a package there does not install it. [9] Use one to cap a transitive dependency for a whole build without making it a direct dependency.

## Hash-checking mode

With `--require-hashes`, or as soon as any line carries `--hash`, pip requires a hash for every requirement and every dependency, and every requirement must be pinned with `==` (or be a URL or path). [10] The course's test run hit both failure modes:

```text
$ pip install -r bad-hash.txt
        Expected sha256 0000000000000000000000000000000000000000000000000000000000000000
             Got        d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c

$ pip install --require-hashes -r unpinned.txt
ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    click from https://files.pythonhosted.org/.../click-8.5.0-py3-none-any.whl
```

For the strictest installs, pip's security page adds `--only-binary :all:` so no sdist is ever built, and suggests installing your own project with `--no-deps`. [10]

## Reading `ResolutionImpossible`

pip resolves by making assumptions and checking them. When one turns out wrong, it backtracks and tries another candidate version. pip calls this expected behaviour, and warns it can take a long time when a package has many versions. [29] `pip is looking at multiple versions of X ... This could take a while` means pip is backtracking through X's versions.

When no solution exists, two requirements collide. [29] From the chapter's demo script:

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
2. **"The conflict is caused by"** has one line per side. "The user requested" comes from you or a requirements file; "X depends on" comes from a package's metadata. Put the ranges side by side: `<1.21` and `>=1.21.1,<3` do not overlap.
3. **Decide whose range moves.** pip's four strategies: drop stale top-level requirements; loosen your own ranges; get the dependency loosened, or fork it, which costs you its maintainers' support; and if every range is right, pick a different package or refactor. [29]

## Broken environments: `pip check` and pipdeptree

The resolver only protects the packages in the current command. pip says it may break packages that are already installed and does not guarantee the environment stays consistent. [9] The demo forces it:

```text
$ pip install 'requests==2.32.3'
$ pip install --no-deps 'urllib3==1.20'
$ pip check
requests 2.32.3 has requirement urllib3<3,>=1.21.1, but you have urllib3 1.20.
```

`pip check` reports inconsistencies in what is installed. [9] It exited with status 1 in the demo, so it can gate a CI job or a container build.

`pip freeze` gives a flat list. `pipdeptree` adds the parent–child relationships and reports conflicts. [28] Against the same environment:

```text
$ pipdeptree --python /tmp/c/bin/python -p requests
Warning: dependency problems found:
* requests==2.32.3
  - urllib3 [required: >=1.21.1,<3, installed: 1.20]
```

(Output shortened: the tree that follows is cut.) The reverse view answers "who pulled this in?" before you force an upgrade or removal: `pipdeptree --reverse --packages urllib3`. [28] Then change the narrowest range you own, or add a constraints file if the cap must apply across the build.

## Gotchas

- **A stale lock ships unreviewed.** `uv sync --frozen` installs from the lock without checking it, so a `pyproject.toml` change that nobody relocked goes out silently. Use `uv sync --locked` in CI; it fails with "The lockfile at `uv.lock` needs to be updated". [21]
- **Keeping only one of two hashes.** A release often has a wheel and an sdist, each with its own hash, and pip accepts a file only if its hash is listed. Trim one and installs fail whenever pip picks the other file, for example on a platform without a matching wheel. Keep every hash `pip-compile --generate-hashes` writes. [10] [27]
- **One hashed line changes the whole file.** From pip 26.2, one hashed requirement makes hashes mandatory for all of them, so an unpinned `colorama>=0.4` next to hashed lines makes the install fail: in hash mode every requirement must be pinned with `==` and carry a hash. Pin and hash every line, or pass `--no-require-hashes` to switch the implicit mode off. [10]
- **`--no-deps` breaks things quietly.** `--no-deps`, a manual `pip install` on a live host, or two tools installing into one venv can leave unmet requirements behind, because pip does not guarantee the environment stays consistent. Add `RUN pip check` after the install layer so the build exits 1. [9]
- **Endless backtracking at deploy time.** Resolving on every deploy repeats the slow search. Lock during development so deployment does not repeat it. [29]

:::low-confidence
The pipdeptree page section read for this course does not document `--python`; it is shown working in the demo script. Check `pipdeptree --help` for your version.
:::

:::key-takeaways
- Project metadata holds minimal ranges; a lock or requirements file holds the exact, pinned environment. [30]
- `uv sync --locked` fails on a stale lock; `--frozen` skips the check. [21]
- Hash mode needs `==` pins and a hash for every file you accept; a mismatch stops the install. [10]
- In `ResolutionImpossible`, "The user requested" is your side and "X depends on" is package metadata; move the narrowest range you own. [29]
- pip does not guarantee consistency across commands: run `pip check`, and `pipdeptree --reverse --packages X` to see who requires X. [9] [28]
:::

:::glossary
- **Lock / lockfile**: a file that records the exact version, source and hash of every package in an environment.
- **Transitive dependency**: a dependency of a dependency.
- **Pin**: an exact version requirement such as `==26.3`.
- **Range**: a version requirement that allows several versions, such as `>=23`.
- **Hash**: a fingerprint (here SHA-256) of a file; any change to the file changes it.
- **Constraints file**: a file that restricts versions without asking for installs.
- **CI**: continuous integration, the automated build and test pipeline.
- **uv**: a fast Python package and project manager.
- **pip-tools**: the `pip-compile` and `pip-sync` commands for pinned requirements files.
- **Resolver**: the part of pip that picks one version of every package so that all requirements are satisfied.
- **Backtracking**: undoing an earlier version choice and trying another.
- **`ResolutionImpossible`**: pip's error when no set of versions satisfies every requirement.
- **Top-level requirement**: a package you asked for directly, as opposed to one pulled in by another package.
- **`pip check`**: a command that reports installed packages whose requirements are not met.
- **pipdeptree**: a tool that prints installed packages as a dependency tree.
- **Fork**: your own copy of someone else's project that you maintain.
:::
