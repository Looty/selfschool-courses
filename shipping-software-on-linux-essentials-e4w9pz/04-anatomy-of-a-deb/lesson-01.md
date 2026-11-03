---
id: l07
title: "Inside a .deb and its relationship fields"
quiz: quiz-01.yaml
resources: [../resources/tiny-deb/build.sh, ../resources/tiny-deb/hello-ship/DEBIAN/control, ../resources/tiny-deb/hello-ship/DEBIAN/conffiles, ../resources/tiny-deb/hello-ship/DEBIAN/postinst, ../resources/tiny-deb/hello-ship/usr/bin/hello-ship, ../resources/tiny-deb/hello-ship/etc/hello-ship.conf]
sources: [31, 34, 38, 40, 43]
---
After this lesson you can take a `.deb` apart with standard tools, write a valid binary `control` file, and pick the right relationship field (Depends, Breaks, Provides, Replaces and the rest) for each situation.

## Build one first

This chapter uses a tiny package, `hello-ship`, that you build yourself from this lesson's Resources:

```bash
cd resources
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh          # 1.0-1
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh 1.0-2    # a newer revision
```

In Windows PowerShell, write the mount as `-v "${PWD}:/lab"` (the whole value in quotes): `"$PWD":/lab` splits into two arguments there and Docker fails with "invalid reference format".

The script runs `dpkg-deb --build` on `tiny-deb/hello-ship/` (a filesystem image plus a `DEBIAN/` directory holding `control`, `conffiles` and `postinst`) and writes the `.deb` files to `tiny-deb/dist/`.

## Three members in an `ar` archive

A `.deb` is an `ar` archive (magic `!<arch>`) whose members must appear in this exact order [38]:

| # | Member | Holds |
| --- | --- | --- |
| 1 | `debian-binary` | the format version, `2.0` |
| 2 | `control.tar` (optionally `.gz`, `.xz`, `.zst`) | `control` (mandatory), and optionally `md5sums`, `conffiles`, `triggers`, `shlibs`, `symbols` and the maintainer scripts `preinst`, `postinst`, `prerm`, `postrm` |
| 3 | `data.tar` (optionally compressed) | the files to install |

```text
$ ar t hello-ship_1.0-1_all.deb
debian-binary
control.tar.xz
data.tar.xz
```

xz is `dpkg-deb`'s default compression; `-Z` chooses gzip, xz, zstd or none [43].

## Looking without installing

`dpkg-deb --info` describes the package, `--contents` lists the data archive, `--field` prints single control fields, and `-x` extracts the files [43].

```text
$ dpkg-deb --info hello-ship_1.0-1_all.deb
 new Debian package, version 2.0.
 size 1392 bytes: control archive=680 bytes.
      21 bytes,     1 lines      conffiles
     388 bytes,    11 lines      control
     255 bytes,     9 lines   *  postinst             #!/bin/sh
 Package: hello-ship
 Version: 1.0-1
 Architecture: all
 ...
$ dpkg-deb --contents hello-ship_1.0-1_all.deb
-rw-r--r-- root/root       108 ... ./etc/hello-ship.conf
-rwxr-xr-x root/root       291 ... ./usr/bin/hello-ship
```

The `*` marks an executable control file. Ownership is `root/root` because the build used `--root-owner-group`, which sets every entry's owner and group to root [43].

## The binary control file

`DEBIAN/control` is a single stanza of fields. The mandatory ones are `Package`, `Version`, `Architecture`, `Maintainer` and `Description`; `Section` and `Priority` are recommended [34].

```text
Package: hello-ship
Version: 1.0-1
Architecture: all
Maintainer: Course Lab <lab@example.invalid>
Depends: bash
Section: utils
Priority: optional
Description: tiny example package for the Shipping Software on Linux course
 Installs one shell command, hello-ship, and one configuration file,
 /etc/hello-ship.conf, so you can watch dpkg handle a binary, a conffile
 and a postinst script.
```

`Architecture: all` means architecture-independent, such as scripts or pure Python; `any` (in source packages) means "build for every architecture" [34].

## Relationship fields

All relationship fields share one syntax: a comma-separated list of package names, each optionally with a version relation in parentheses: `<<`, `<=`, `=`, `>=`, `>>` (strictly earlier, earlier or equal, exactly equal, later or equal, strictly later). Alternatives are separated by `|`, and square brackets restrict a clause to some architectures [31].

```text
Depends: python3 (>= 3.11), python3 (<< 3.12), libssl3 | libssl1.1
```

The two `python3` clauses together express a range.

| Field | Meaning | Enforced |
| --- | --- | --- |
| `Depends` | absolute dependency | the package is not **configured** until every Depends is configured [31] |
| `Pre-Depends` | dpkg completes installing the named packages before even starting this one | at **unpack**; "should be used sparingly" [31] |
| `Recommends` | strong, but not absolute | apt installs them unless told `--no-install-recommends` [40] |
| `Suggests` | related packages that may be useful | not installed by default [31] |
| `Enhances` | the reverse of Suggests | informational [31] |
| `Breaks` | this is not unpacked while the broken package is configured, unless dpkg can deconfigure it; usually "earlier than" a version, so apt upgrades that package first | at unpack [31] |
| `Conflicts` | the two may never be unpacked together | at unpack; stronger, so Policy prefers `Breaks` [31] |

### Virtual packages: `Provides`

A virtual package is a name that appears in another package's `Provides` field; anything depending on the virtual name is satisfied by any provider [31]. Versioned Provides are only allowed with `=` (`Provides: foo-api (= 2)`). An unversioned Provides does not satisfy a versioned dependency, and does not trigger a versioned `Conflicts` or `Breaks` [31].

### `Replaces`: taking over files

A file owned by two packages is usually an error. `Replaces` says a package may overwrite another package's files, and normally comes with `Breaks` [31]. The textbook case is a split: `foo` becomes `foo` plus `foo-data` from version 1.2-3 [31].

```text
# foo-data
Replaces: foo (<< 1.2-3)
Breaks: foo (<< 1.2-3)

# the new foo
Depends: foo-data (>= 1.2-3)
```

`Replaces` lets `foo-data` take over the old `foo`'s files; `Breaks` forces the old `foo` up to 1.2-3, which no longer ships them; the new `foo` depends on `foo-data`, so users get both. Combined with `Conflicts` instead, `Replaces` says which package to remove when one fully replaces another [31].

For a product made of several packages, a meta-package should depend on each component with **ranges**, not exact pins: a hotfix (0.1.0-1 to 0.1.1-1) then installs without rebuilding it, and an upper bound such as `<< 0.2` stops an incompatible upgrade from arriving silently.

## Gotchas

- **Files owned by your UID.** Without `--root-owner-group`, files carry the builder's UID: `dpkg-deb --contents` shows `1000/1000` instead of `root/root`. Build with `dpkg-deb --root-owner-group --build` [43].
- **The build passes, the repository refuses.** `dpkg-deb` accepted a package with no `Section`, but the repository tool in Lab 2 (chapter 05) rejected it. Set `Section` and `Priority` anyway [34] [43].
- **Broken Description.** Every extended-description line must start with a space, a blank line is written as a space and a full stop, and tabs are not allowed [34]. Check the field with `dpkg-deb --field`.
- **Dependencies are checked at configure time, not unpack.** `dpkg -i` happily unpacks a package whose dependencies are missing and then refuses to configure it, leaving it in state `iU` [31]. Chapter 06 covers the recovery.
- **Unversioned Provides.** `Depends: mta (>= 2)` is never satisfied by a package that only says `Provides: mta`. The provider must declare `Provides: mta (= 2)` [31].
- **Breaks pointing the wrong way.** In a split, `Breaks: foo (>= 1.2-3)` breaks the new `foo` instead of the old one. Use the same earlier-than range as `Replaces`, and ship the pair in the same release [31].

:::key-takeaways
- A `.deb` is an `ar` archive of `debian-binary`, `control.tar*` and `data.tar*`, in that order. [38]
- `dpkg-deb --info`, `--contents`, `--field` and `-x` inspect a package without installing it; `--root-owner-group` makes every file root-owned. [43]
- Mandatory binary control fields: Package, Version, Architecture, Maintainer, Description. [34]
- `Depends` is enforced at configure time, `Pre-Depends` at unpack; prefer `Breaks` over `Conflicts`. [31]
- Versioned Provides only with `=`; moving files between packages takes `Replaces` + `Breaks` with an earlier-than version. [31]
:::

:::glossary
- **`.deb`**: a Debian binary package file.
- **`ar`**: a simple archive format; a `.deb` is one.
- **Control file**: `DEBIAN/control`, the package's metadata.
- **Control archive**: `control.tar*`, the member holding the control file and maintainer scripts.
- **Data archive**: `data.tar*`, the member holding the files to install.
- **`dpkg-deb`**: the low-level tool that builds and inspects `.deb` files.
- **`Architecture: all`**: the package's contents do not depend on the CPU type.
- **Stanza**: a block of `Field: value` lines.
- **Relationship field**: a control field that relates a package to others, such as Depends or Breaks.
- **Virtual package**: a name no real package has, provided by one or more packages through `Provides`.
- **Meta-package**: a package with no real content that depends on a set of other packages.
- **Configure**: dpkg's step after unpacking, which runs `postinst configure`.
- **Deconfigure**: dpkg temporarily marking an installed package as not configured so another can be unpacked.
:::
