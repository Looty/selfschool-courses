---
id: l20
title: "apt repositories: layout, signing, pinning and offline use"
quiz: quiz-03.yaml
resources: [../resources/lab3/build-deb.sh, ../resources/lab3/lab3-run.sh]
sources: [39, 49, 50, 51, 52, 53]
---
After this lesson you can describe what an apt client downloads from a repository, publish packages with reprepro or aptly, make clients verify the signature with `Signed-By`, serve a repository offline, and steer versions with pins.

## What a repository is

A repository is static files over HTTP (or a local directory). The client starts at `dists/<suite>/InRelease`: the distribution's metadata and the checksums of its index files, inline-signed. Older clients use the unsigned `Release` plus a detached `Release.gpg`. [49] `Release` must carry at least `Suite` and/or `Codename`, `Architectures`, `Components`, `Date` and `SHA256`, with `Origin`, `Label`, `Version` and `Description` optional; `Valid-Until` is one of the functional fields. [49] The package lists live at `dists/<suite>/<component>/binary-<arch>/Packages`, and the `.deb` files usually live in a shared `pool/`. [49] A **flat** repository skips the `dists/` tree entirely: one directory with `Packages`, used as `deb uri directory/`. [49]

Lab 3's published tree started like this:

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

## Publishing with reprepro

reprepro manages a repository of Debian packages. Its `conf/distributions` file declares each distribution: `Codename` (required, the directory name under `dists/`), `Architectures` and `Components` (required), and `Suite`, `Origin` and `Label`, which are copied into `Release`. [51] With `SignWith`, it generates `Release.gpg`; `yes` or `default` uses gpg's default key. [51] Day-to-day commands: `includedeb <codename> <file.deb>`, `list`, `remove <codename> <pkg>` and `export`, which regenerates the index files. [51]

Lab 3's config:

```text
Origin: shiplab
Label: shiplab
Codename: stable
Architectures: amd64 arm64
Components: main
SignWith: <key fingerprint>
```

Two behaviours the lab exposed: reprepro refused a package without `Section` and `Priority` (`No section given for 'shiplab-suite', skipping.`), and including the hotfix `0.1.1-1` printed `Deleting files no longer referenced...`. In the lab's setup the distribution held one version of each package, so the old `.deb` left the pool when the new one came in. Keep your build artifacts elsewhere if you need fast rollbacks.

## aptly: snapshots

aptly models the same job differently: **mirrors** of remote repositories, **local repos** you add packages to, **snapshots** ("immutable list of packages, basic block to implement repeatability and controlled changes") and **published** repositories made from a repo or snapshot. [52] `aptly publish repo <name>` publishes with `-distribution`, `-component` (default `main`), `-gpg-key` or `-skip-signing`. [53] Snapshots answer the rollback problem above: publish snapshot N+1, and if it is bad, switch the published endpoint back to snapshot N.

## Clients: trust one key for one source

In deb822 format, a source is a stanza in `/etc/apt/sources.list.d/*.sources`. `Signed-By` requires the repository to verify against the named keyring "rather than all trusted keys apt has configured". [50] Lab 3's client:

```text
Types: deb
URIs: http://shiplab-repo-http:8000/
Suites: stable
Components: main
Signed-By: /usr/share/keyrings/shiplab-archive-keyring.gpg
```

Pointing `Signed-By` at the wrong keyring, as the lab does at the end, is refused:

```text
W: GPG error: http://shiplab-repo-http:8000 stable InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 63C93A0783F2DEC8
```

`Trusted: yes` (or `[trusted=yes]` in one-line format) tells apt to treat a source as trusted "even if it doesn't pass authentication checks". [50] Use it only for throwaway local repositories, as Lab 4 does.

## Offline and air-gapped

The `file:` scheme makes any directory an archive, for example `deb file:/home/apt/debian stable main`; `copy:` does the same but copies packages into apt's cache. [50] An exact path with no components must end in `/` (flat repository). [50] For an air-gapped site, publish a signed repository to removable media or an internal HTTP server, ship the keyring with your installer, and use `Signed-By`. Nothing about signing changes offline.

## Pinning your own repository

`apt_preferences` decides between versions from different sources (chapter 06). Typical uses for a product repository: `Pin: origin "<host>"` or `Pin: release o=<Origin>` to prefer your repository over another source of the same package, `Pin: version 0.1.*` to hold a component on a series, and a negative priority to make sure a package never comes from a given origin. [39] Lab 3's `Origin: shiplab` line is what `o=shiplab` would match.

:::key-takeaways
- Clients read `dists/<suite>/InRelease` (inline-signed), then `binary-<arch>/Packages`, then files from `pool/`. [49]
- reprepro: `conf/distributions` + `includedeb`; `SignWith` signs `Release`. [51]
- aptly snapshots are immutable package lists, useful for repeatable releases and rollbacks. [52]
- `Signed-By` binds a source to one keyring; `Trusted: yes` skips verification and is for labs only. [50]
- `file:` URIs and flat repositories serve packages offline. [50]
:::

:::glossary
- **Suite / codename**: the distribution name in a repository (`stable`, `bookworm`).
- **Component**: a section of a distribution such as `main`.
- **InRelease**: the inline-signed metadata file at the top of a distribution.
- **Keyring**: a file of public keys apt uses to verify signatures.
- **Pool**: the directory that stores package files shared across distributions.
- **Snapshot (aptly)**: an immutable, named list of packages.
- **deb822**: the multi-line `Field: value` format of `.sources` files.
:::
