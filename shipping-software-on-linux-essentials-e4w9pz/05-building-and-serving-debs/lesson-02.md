---
id: l10
title: "Lab 2: a signed apt repo, pinning and a hotfix"
quiz: quiz-02.yaml
resources: [../resources/lab3/lab3-run.sh, ../resources/lab3/build-deb.sh, ../resources/lab2-devenv/pyproject.toml]
sources: [2, 31, 33, 39, 43, 49, 50, 51, 52, 53]
---
After this lab you can describe what an apt client downloads from a repository, and you will have packaged the course's `devenv` CLI (the script builds it itself from `../resources/lab2-devenv`) as a `.deb` with a bundled virtualenv, published it with a product meta-package in a GPG-signed repository, installed it over HTTP into a clean container, and shipped a hotfix of just that one component.

## What a repository is, in one screen

A repository is static files over HTTP (or a local directory). The client starts at `dists/<suite>/InRelease`: the distribution's metadata and the checksums of its index files, inline-signed. [49] The package lists live at `dists/<suite>/<component>/binary-<arch>/Packages`, and the `.deb` files usually live in a shared `pool/`. [49] A **flat** repository skips the `dists/` tree: one directory with `Packages`. [49]

| Job | Tool or setting |
| --- | --- |
| Publish | reprepro: `conf/distributions` declares `Codename`, `Architectures`, `Components`; `SignWith` signs `Release`; `includedeb <codename> <file.deb>` adds a package [51] |
| Repeatable releases | aptly: **snapshots** are an "immutable list of packages" [52]; `aptly publish repo` takes `-distribution`, `-component`, `-gpg-key` [53] |
| Trust one key | `Signed-By` makes the source verify against the named keyring "rather than all trusted keys apt has configured" [50] |
| Offline | `file:` makes any directory an archive; `copy:` does the same but copies packages into apt's cache [50] |
| Steer versions | `Pin: release o=<Origin>` or `Pin: origin "<host>"` to prefer your repository, `Pin: version 0.1.*` to hold a series, a negative priority to block an origin [39] |

Lab 2's `Origin: shiplab` line is what `o=shiplab` would match. [39] Air-gapped sites work the same way: a signed repository on media or an internal server, the keyring shipped with your installer, and `Signed-By`.

## Shortcut: the ready-made script

`lab3-run.sh` was run end to end on Docker Desktop while writing this course; every output below is from that run. It needs internet access once, for apt packages and the build dependencies in `../resources/lab2-devenv/pyproject.toml`. From the resources folder, on Linux, macOS or Git Bash on Windows:

```bash
bash lab3/lab3-run.sh
```

Windows PowerShell users: this script runs its own `docker` commands, so there is no `"$PWD":/lab` mount to rewrite; run the same line from Git Bash.

The script creates a Docker network and two volumes (repository, GPG home), builds and publishes inside containers, and deletes everything on exit. Nothing is written to your checkout, and no `.deb` is stored in the course repository.

## Step 1: build and publish 0.1.0-1

`build-deb.sh init` creates a signing key and reprepro's `conf/distributions` with `SignWith`. [51] The config:

```text
Origin: shiplab
Label: shiplab
Codename: stable
Architectures: amd64 arm64
Components: main
SignWith: <key fingerprint>
```

`build-deb.sh build 0.1.0 1` then:

1. creates a venv **at** `/opt/shiplab-devenv`, because venvs cannot be moved [2];
2. copies the `devenv` CLI project from `../resources/lab2-devenv` and `pip install`s it into the venv;
3. copies the tree into a package directory, adds `/usr/bin/devenv` as a symlink, writes `DEBIAN/control`;
4. runs `dpkg-deb --root-owner-group --build` [43];
5. builds the meta-package `shiplab-suite 1.0-1` with `Depends: shiplab-devenv (>= 0.1.0-1), shiplab-devenv (<< 0.2)` [31];
6. `reprepro includedeb stable` for both. [51]

```text
stable|main|amd64: shiplab-devenv 0.1.0-1
stable|main|amd64: shiplab-suite 1.0-1
```

## Step 2: serve it

`python -m http.server` serves the repository volume. The signed metadata is in place under `dists/stable/`. [49]

```text
$ ls /repo/dists/stable
InRelease  Release  Release.gpg  main
$ head -n 8 /repo/dists/stable/InRelease
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA256

Origin: shiplab
Label: shiplab
Codename: stable
Date: Mon, 02 Nov 2026 17:41:47 UTC
Architectures: amd64 arm64
```

## Step 3: a clean client installs the product

In deb822 format, a source is a stanza in `/etc/apt/sources.list.d/*.sources`. [50] The client's:

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

`Signed-By` binds the source to the product keyring. [50] The `python3` range is the previous lesson's fix.

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

`0.1.1-1` sorts after `0.1.0-1` and before `0.2`, so it satisfies both the upgrade and the suite's upper bound. You can check that with `dpkg --compare-versions` (chapter 04). [33]

## Step 5: a wrong key is refused

The script finally points `Signed-By` at Debian's own keyring:

```text
W: GPG error: http://shiplab-repo-http:8000 stable InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 63C93A0783F2DEC8
```

apt keeps the old index and refuses the unverified one.

## Gotchas

- **reprepro skips packages without `Section` and `Priority`.** In the lab, reprepro refused the meta-package with `No section given for 'shiplab-suite', skipping.`, so it never reached the repository. Put both fields in `DEBIAN/control`, then check with `reprepro list stable`. [51]
- **A hotfix deletes the old `.deb`.** Including `0.1.1-1` printed `Deleting files no longer referenced...`: the distribution held one version per package, so `0.1.0-1` left the pool. Keep build artifacts elsewhere, or publish aptly snapshots and switch back to snapshot N if N+1 is bad. [51] [52]
- **`Trusted: yes` defeats `Signed-By`.** It tells apt to treat a source as trusted "even if it doesn't pass authentication checks". Use it only for throwaway local repositories. [50]
- **Wrong keyring.** Symptom: `NO_PUBKEY <id>` in a `W: GPG error` line while apt keeps the old index. Point `Signed-By` at the product keyring under `/usr/share/keyrings`. [50]
- **Flat repository paths.** A flat repository is used as `deb uri directory/`, and an exact path with no components must end in `/`. When a flat or `file:` source misbehaves, check that trailing slash first. [49] [50]
- **An exact meta-package pin forces a suite release.** The hotfix shipped alone only because the suite says `(>= 0.1.0-1)` and `(<< 0.2)`; with `=` every component fix would need a new suite. [31] [33]

## Check yourself

- Change the suite's upper bound to `<< 0.1.1` and rerun. What does `apt-get install --only-upgrade shiplab-devenv` say now?

:::key-takeaways
- Clients read `dists/<suite>/InRelease` (inline-signed), then `binary-<arch>/Packages`, then files from `pool/`. [49]
- reprepro + `SignWith` publishes a signed repository; clients pin trust with `Signed-By`, and `Trusted: yes` is for labs only. [50] [51]
- A meta-package with version ranges lets one component be hotfixed alone. [31]
- aptly snapshots are immutable package lists, useful for repeatable releases and rollbacks. [52]
- Build outputs live in containers and volumes, never in the source repository.
:::

:::glossary
- **Suite / codename**: the distribution name in a repository (`stable`, `bookworm`).
- **Component**: a section of a distribution such as `main`.
- **InRelease**: the inline-signed metadata file at the top of a distribution.
- **Keyring**: a file of public keys apt uses to verify signatures.
- **Pool**: the directory that stores package files shared across distributions.
- **Snapshot (aptly)**: an immutable, named list of packages.
- **deb822**: the multi-line `Field: value` format of `.sources` files.
- **Meta-package**: a package that only depends on the components of a product.
- **Hotfix**: an urgent new version of one component.
- **GPG key**: the key pair used to sign repository metadata; clients hold the public half.
- **`--only-upgrade`**: an apt option that upgrades a package only if it is already installed.
:::
