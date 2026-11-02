---
id: l14
title: "What is inside a .deb"
quiz: quiz-01.yaml
resources: [../resources/tiny-deb/build.sh, ../resources/tiny-deb/hello-ship/DEBIAN/control, ../resources/tiny-deb/hello-ship/DEBIAN/conffiles, ../resources/tiny-deb/hello-ship/DEBIAN/postinst, ../resources/tiny-deb/hello-ship/usr/bin/hello-ship, ../resources/tiny-deb/hello-ship/etc/hello-ship.conf]
sources: [34, 38, 43]
---
After this lesson you can take a `.deb` apart with standard tools, say what each of its three members holds, and write a valid binary `control` file from memory.

## Build one first

This chapter and the next use a tiny package, `hello-ship`, that you build yourself from the files in this lesson's Resources. No package files are downloaded or stored in the course; you build them locally:

```bash
cd resources
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh          # 1.0-1
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh 1.0-2    # a newer revision
```

The script copies `tiny-deb/hello-ship/` to a temporary directory, fixes permissions and runs `dpkg-deb --build`. The `.deb` files land in `tiny-deb/dist/`, which git ignores. The source tree is just a filesystem image plus a `DEBIAN/` directory:

```text
hello-ship/
├── DEBIAN/
│   ├── control       # the package's metadata
│   ├── conffiles     # files dpkg must treat as configuration
│   └── postinst      # a maintainer script
├── etc/hello-ship.conf
└── usr/bin/hello-ship
```

## Three members in an `ar` archive

A `.deb` is an `ar` archive (magic `!<arch>`) whose members must appear in this exact order: [38]

1. `debian-binary`: the format version, `2.0`;
2. `control.tar` (optionally `.gz`, `.xz` or `.zst`): the control information, with `control` mandatory and optional `md5sums`, `conffiles`, `triggers`, `shlibs`, `symbols` and the maintainer scripts `preinst`, `postinst`, `prerm`, `postrm`;
3. `data.tar` (optionally compressed): the files to install. [38]

From the build of `hello-ship`:

```text
$ ar t hello-ship_1.0-1_all.deb
debian-binary
control.tar.xz
data.tar.xz
```

xz is `dpkg-deb`'s default compression; `-Z` chooses gzip, xz, zstd or none. [43] Because a `.deb` is just archives, you can always inspect one with `ar x` and `tar` on a machine without dpkg.

## Looking without installing

`dpkg-deb --info` describes the package and `--contents` lists the data archive; `--field` prints single control fields, and `-x` extracts the files. [43]

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

The `*` marks an executable control file. Ownership is `root/root` because the build used `--root-owner-group`, which sets every entry's owner and group to root. [43] Without it, the files would carry the UID of whoever built the package.

## The binary control file

`DEBIAN/control` is a single stanza of fields. The mandatory ones are `Package`, `Version`, `Architecture`, `Maintainer` and `Description`; `Section` and `Priority` are recommended. [34]

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

- `Architecture: all` means architecture-independent, such as scripts or pure Python; `any` (in source packages) means "build for every architecture". [34]
- `Description` has a one-line synopsis, then an extended description where each line starts with a space; a line with a single space and a full stop is a blank line, and tabs are not allowed. [34]
- `Installed-Size` estimates the disk space the package needs. [34]

`dpkg-deb --build` parses `DEBIAN/control` and checks the permissions of the maintainer scripts unless you pass `--no-check`. [43] In Lab 3 a missing `Section` was accepted by `dpkg-deb` but rejected later by the repository tool, so set the recommended fields even when the build does not insist.

:::key-takeaways
- A `.deb` is an `ar` archive of `debian-binary`, `control.tar*` and `data.tar*`, in that order. [38]
- `dpkg-deb --info`, `--contents`, `--field` and `-x` inspect a package without installing it. [43]
- Mandatory binary control fields: Package, Version, Architecture, Maintainer, Description. [34]
- `--root-owner-group` makes every file root-owned in the archive. [43]
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
:::
