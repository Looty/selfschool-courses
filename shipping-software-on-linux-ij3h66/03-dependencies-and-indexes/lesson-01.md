---
id: l10
title: "Ranges for libraries, locks for applications"
quiz: quiz-01.yaml
resources: [../resources/lab-deps-demo.sh]
sources: [9, 10, 21, 27, 29, 30]
---
After this lesson you can decide where a version range belongs and where an exact pin belongs, produce a lock with uv or pip-tools, and make CI fail when the lock is stale or a downloaded file does not match its hash.

## Abstract vs concrete requirements

The PyPA draws the line like this. The dependencies in a project's metadata say what the project **minimally** needs to run, and pinning them to exact versions is not considered good practice. Requirements files usually describe a **whole environment**, often as an exhaustive list of pinned versions, sometimes tied to a particular index. [30] The page does not use the words "library" and "application", but that is how it plays out:

- A **library** (`packaging`, your shared client SDK) declares ranges such as `packaging>=23`. If it pinned `==26.3`, every application that also needs `packaging` would be forced onto that exact version.
- An **application** you deploy (a service, a CLI shipped in a .deb) keeps the ranges in `pyproject.toml` and adds a **lock**: every package, transitive ones included, at one exact version, ideally with hashes.

pip's own advice matches: lock during development so deployment does not repeat the resolution. [29]

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

Each entry records the version, the index it came from and the file hashes. The two CI flags are what make the lock useful: [21]

- `uv sync --locked` raises an error if the lock is out of date instead of quietly updating it;
- `uv sync --frozen` uses the lock without checking it.

After adding `click>=8` to `pyproject.toml` without relocking:

```text
$ uv sync --locked
error: The lockfile at `uv.lock` needs to be updated, but `--locked` was provided.

hint: To update the lockfile, run `uv lock`.
```

Use `--locked` in CI. A stale lock fails the build instead of shipping something nobody reviewed. `uv export --format requirements.txt` writes the lock out for tools that only read requirements files. [21]

## Locking with pip-tools

`pip-compile` turns `requirements.in`, or the dependencies in `pyproject.toml`, into a pinned `requirements.txt`. `--generate-hashes` adds hashes, `--upgrade` and `--upgrade-package` move pins on purpose, and `pip-sync` installs, upgrades and uninstalls until the environment matches the file. [27] From the lab project:

```text
click==8.5.0 \
    --hash=sha256:255bc9599cf7748b4b1a446ccc735421bd08a2ae529a8b88597d3de5664ee360 \
    --hash=sha256:ba0d2089de75ea0310e2dde03160e6ca10009947fb95a182f9b54021bb272e34
    # via shiplab-devenv (pyproject.toml)
```

There are two hashes because one release has two files, a wheel and an sdist. Hash-checking needs a hash for every file you are willing to accept. [10] For layered files, start `dev-requirements.in` with `-c requirements.txt`. Dev tools are then constrained to the same pins as production. [27]

## Constraints files

A constraints file looks like a requirements file but only controls **which version** gets installed. Listing a package there does not install it. [9] Use one to cap a transitive dependency for a whole build without making it a direct dependency.

## Hash-checking mode

With `--require-hashes`, or as soon as any line carries `--hash`, pip requires a hash for every requirement and every dependency, and every requirement must be pinned with `==` (or be a URL or path). [10] The lab hit both failure modes:

```text
$ pip install -r bad-hash.txt
        Expected sha256 0000000000000000000000000000000000000000000000000000000000000000
             Got        d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c

$ pip install --require-hashes -r unpinned.txt
ERROR: In --require-hashes mode, all requirements must have their versions pinned with ==. These do not:
    click from https://files.pythonhosted.org/.../click-8.5.0-py3-none-any.whl
```

From pip 26.2, one hashed requirement makes hashes mandatory for all of them, and `--no-require-hashes` switches that off. [10] For the strictest installs, pip's security page adds `--only-binary :all:` so no sdist is ever built, and suggests installing your own project with `--no-deps`. [10]

:::key-takeaways
- Project metadata holds minimal ranges; a lock or requirements file holds the exact environment. [30]
- `uv sync --locked` fails on a stale lock; `--frozen` skips the check. [21]
- `pip-compile --generate-hashes` produces pinned, hashed requirements; `pip-sync` makes the environment match. [27]
- Constraints files limit versions without installing anything. [9]
- Hash mode needs `==` pins and a hash for every file you accept; a mismatch stops the install. [10]
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
:::
