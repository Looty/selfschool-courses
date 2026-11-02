---
id: l21
title: "Lab 3: package the CLI, publish a signed repo, ship a hotfix"
quiz: quiz-04.yaml
resources: [../resources/lab3/lab3-run.sh, ../resources/lab3/build-deb.sh, ../resources/lab2-devenv/pyproject.toml]
sources: [2, 31, 33, 43, 49, 50, 51]
---
After this lab you will have packaged the chapter 03 `devenv` CLI as a `.deb` with a bundled virtualenv, published it with a product meta-package in a GPG-signed repository, installed it over HTTP into a clean container, and shipped a hotfix of just that one component.

This is a hands-on lab. `lab3-run.sh` was run end to end on Docker Desktop while writing this course. Every container is `debian:bookworm` except the tiny HTTP server (`python:3.12-slim-bookworm`). It needs internet access once, for apt packages and the project's build dependencies. Packages are built inside the builder container and published to a Docker volume. Nothing is written to your checkout, and no `.deb` is stored in the course repository.

## Shortcut

From the resources folder, on Linux, macOS or Git Bash on Windows:

```bash
bash lab3/lab3-run.sh
```

The script creates a Docker network and two volumes (repository, GPG home), runs every step, and deletes them on exit.

## Step 1: build and publish 0.1.0-1

`build-deb.sh init` creates a signing key and reprepro's `conf/distributions` with `SignWith`. [51] `build-deb.sh build 0.1.0 1` then:

1. creates a venv **at** `/opt/shiplab-devenv`, because venvs cannot be moved [2];
2. `pip install`s the lab project into it;
3. copies the tree into a package directory, adds `/usr/bin/devenv` as a symlink, writes `DEBIAN/control`;
4. runs `dpkg-deb --root-owner-group --build` [43];
5. builds the meta-package `shiplab-suite 1.0-1` with `Depends: shiplab-devenv (>= 0.1.0-1), shiplab-devenv (<< 0.2)` [31];
6. `reprepro includedeb stable` for both. [51]

```text
stable|main|amd64: shiplab-devenv 0.1.0-1
stable|main|amd64: shiplab-suite 1.0-1
```

## Step 2: serve it

`python -m http.server` serves the repository volume. The signed metadata is in place: `InRelease`, `Release`, `Release.gpg` under `dists/stable/`. [49]

## Step 3: a clean client installs the product

```text
Types: deb
URIs: http://shiplab-repo-http:8000/
Suites: stable
Components: main
Signed-By: /usr/share/keyrings/shiplab-archive-keyring.gpg
```

```text
$ apt-get install -y shiplab-suite
Setting up python3 (3.11.2-1+b1) ...
Setting up shiplab-devenv (0.1.0-1) ...
Setting up shiplab-suite (1.0-1) ...
$ apt-cache show shiplab-devenv | grep -E '^(Version|Depends):'
Version: 0.1.0-1
Depends: python3 (>= 3.11), python3 (<< 3.12)
$ devenv doctor
devenv        0.1.0
executable    /opt/shiplab-devenv/bin/python3
prefix        /opt/shiplab-devenv
base_prefix   /usr
in a venv     yes
```

`Signed-By` binds the source to the product keyring. [50] The first version of this package said `Depends: python3.11` and failed at run time with `cannot execute: required file not found`. Lesson 19 explains why, and the range above is the fix.

## Step 4: a hotfix of one component

`build-deb.sh hotfix 0.1.1 1` rebuilds **only** `shiplab-devenv`, as `0.1.1-1`. The meta-package is not touched, because its range already allows 0.1.1-1:

```text
stable|main|amd64: shiplab-devenv 0.1.1-1
stable|main|amd64: shiplab-suite 1.0-1
```

On the client:

```text
$ apt list --upgradable
shiplab-devenv/unknown 0.1.1-1 all [upgradable from: 0.1.0-1]
$ apt-get install --only-upgrade shiplab-devenv
Unpacking shiplab-devenv (0.1.1-1) over (0.1.0-1) ...
Setting up shiplab-devenv (0.1.1-1) ...
$ dpkg-query -W 'shiplab-*'
shiplab-devenv	0.1.1-1
shiplab-suite	1.0-1
```

`0.1.1-1` sorts after `0.1.0-1` and before `0.2`, so it satisfies both the upgrade and the suite's upper bound. You can check that with `dpkg --compare-versions` (lesson 16). [33]

## Step 5: a wrong key is refused

The script finally points `Signed-By` at Debian's own keyring:

```text
W: GPG error: http://shiplab-repo-http:8000 stable InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 63C93A0783F2DEC8
```

apt keeps the old index and refuses the unverified one.

## Check yourself

- Change the suite's upper bound to `<< 0.1.1` and rerun. What does `apt-get install --only-upgrade shiplab-devenv` say now?
- The hotfix removed `0.1.0-1` from the pool. How would you roll back, given lesson 20?

:::key-takeaways
- A bundled-venv `.deb` is built at its install path and depends on a bounded `python3` range. [2] [31]
- A meta-package with version ranges lets one component be hotfixed alone. [31]
- reprepro + `SignWith` publishes a signed repository; clients pin trust with `Signed-By`. [50] [51]
- Build outputs live in containers and volumes, never in the source repository.
:::

:::glossary
- **Meta-package**: a package that only depends on the components of a product.
- **Hotfix**: an urgent new version of one component.
- **GPG key**: the key pair used to sign repository metadata; clients hold the public half.
- **Docker volume**: storage managed by Docker and shared between containers.
- **`--only-upgrade`**: an apt option that upgrades a package only if it is already installed.
:::
