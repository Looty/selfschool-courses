---
id: l18
title: "Building .debs: dpkg-deb by hand, then debhelper"
quiz: quiz-01.yaml
resources: [../resources/tiny-deb/build.sh, ../resources/tiny-deb/install-test.sh]
sources: [43, 44, 45]
---
After this lesson you can build a binary package directly with `dpkg-deb`, test it in a clean container, and explain what `dh` and `debian/rules` add once a package has a source tree and needs a proper build.

## Level 1: a directory and `dpkg-deb --build`

For a package whose contents you already have (scripts, a prebuilt binary, a bundled venv), the whole build is: lay out the filesystem tree, add `DEBIAN/control` (and scripts), and run `dpkg-deb --build`. `dpkg-deb` needs a `DEBIAN` subdirectory, parses the control file and checks the maintainer-script permissions unless you pass `--no-check`. [43] The course's `tiny-deb/build.sh` does exactly that and nothing more:

```bash
cp -r tiny-deb/hello-ship "$WORK/hello-ship"
find hello-ship -type d -exec chmod 0755 {} +
find hello-ship -type f -exec chmod 0644 {} +
chmod 0755 hello-ship/DEBIAN/postinst hello-ship/usr/bin/hello-ship
dpkg-deb --root-owner-group --build hello-ship hello-ship_1.0-1_all.deb
```

Two details from running it on a Windows checkout: the copy-and-chmod step exists because files on a Windows or macOS mount do not carry Unix permissions, and `--root-owner-group` makes every file root-owned in the archive regardless of who built it. [43]

Build and test, entirely locally, never committing the output:

```bash
cd resources
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh 1.0-2
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/install-test.sh
```

The last command installs 1.0-1 into a **fresh** container, edits the conffile, upgrades to 1.0-2, removes and purges (lesson 17 shows the output). Testing in a clean container is the point: your workstation already has every dependency, a clean container shows what a customer's host will see.

`dpkg-deb` packages whatever is in the tree; it does not build anything. [43] For prebuilt payloads that is all you need. For software that has to be compiled and integrated with the distribution, use debhelper.

## Level 2: a source package and `dh`

A Debian **source** package is your source tree plus a `debian/` directory holding, among other files, its own control file and `debian/rules`. `debian/rules` is a makefile, and with debhelper it is usually three lines: [44]

```make
#!/usr/bin/make -f
%:
	dh $@
```

`dh` runs a sequence of debhelper commands for each target (configure, build, install, package). [44] To change one step, add an `override_dh_<command>` target; the man page's example replaces `dh_auto_configure`: [44]

```make
override_dh_auto_configure:
	./mondoconfig
```

`dh binary-arch --no-act` prints the commands a sequence would run without running them, which is the fastest way to learn what `dh` will do for your package. [44] Add-ons extend the sequence: `--with <addon>` inserts the add-on's commands. [44]

## Python under debhelper: pybuild

For Python, `dh-python` provides **pybuild**, which "invokes various build systems for requested Python versions". The usual rules line is: [45]

```make
%:
	dh $@ --with python3 --buildsystem=pybuild
```

pybuild's `pyproject` plugin drives the standard PEP 517 interface, the same build-backend mechanism as chapter 02; there are also `distutils`, `cmake`, `flit` (deprecated) and `custom` plugins. [45] Files go into a `dist-packages` directory, and naming the build (`--name foo` or `PYBUILD_NAME=foo`) makes the default destination `debian/python3-foo`. [45] dh's own man page notes that Python tools are not run by default, so the `--with python3` add-on is required. [44]

The constraint that matters on Debian: every build dependency comes from Debian's archive, not PyPI. If `pyproject.toml` needs a newer backend than the distribution ships (this course's lab project asks for `hatchling >= 1.26`), the pybuild route needs that backend packaged first. That is the trade-off of the next lesson.

:::key-takeaways
- `dpkg-deb --build DIR` turns a tree with `DEBIAN/control` into a `.deb`; it checks the control file and script permissions. [43]
- Build outputs are built locally and tested in a clean container; they are not committed.
- With a source package, `debian/rules` is usually `dh $@`; customise with `override_dh_*`. [44]
- `dh $@ --with python3 --buildsystem=pybuild` builds Python packages through PEP 517 into `dist-packages`. [45]
:::

:::glossary
- **Binary package**: a `.deb` that installs files.
- **Source package**: the source tree plus `debian/`, from which binary packages are built.
- **debhelper**: a collection of `dh_*` tools that automate common packaging steps.
- **`dh`**: the debhelper sequencer that runs those tools in order.
- **`debian/rules`**: the makefile that drives a source package's build.
- **pybuild**: dh-python's build system for Python packages.
- **`dist-packages`**: Debian's name for site-packages of apt-installed Python modules.
:::
