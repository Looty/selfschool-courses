---
id: l09
title: "Building .debs and putting Python in them"
quiz: quiz-01.yaml
resources: [../resources/tiny-deb/build.sh, ../resources/tiny-deb/install-test.sh, ../resources/lab3/build-deb.sh]
sources: [2, 43, 44, 45, 46, 47, 48]
---
After this lesson you can build a binary package directly with `dpkg-deb`, test it in a clean container, explain what `dh` and `debian/rules` add, and choose between packaging a Python application against the system Python, bundling its own virtualenv, or wrapping it with a generic packager.

## Level 1: a directory and `dpkg-deb --build`

For a package whose contents you already have (scripts, a prebuilt binary, a bundled venv), the whole build is: lay out the filesystem tree, add `DEBIAN/control` (and scripts), and run `dpkg-deb --build`. `dpkg-deb` needs a `DEBIAN` subdirectory, parses the control file and checks the maintainer-script permissions unless you pass `--no-check`. [43] The course's `tiny-deb/build.sh` does exactly that and nothing more:

```bash
cp -r tiny-deb/hello-ship "$WORK/hello-ship"
find hello-ship -type d -exec chmod 0755 {} +
find hello-ship -type f -exec chmod 0644 {} +
chmod 0755 hello-ship/DEBIAN/postinst hello-ship/usr/bin/hello-ship
dpkg-deb --root-owner-group --build hello-ship hello-ship_1.0-1_all.deb
```

The copy-and-chmod step exists because files on a Windows or macOS mount do not carry Unix permissions. `--root-owner-group` makes every file root-owned in the archive regardless of who built it. [43]

Build and test, entirely locally, never committing the output:

```bash
cd resources
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh 1.0-2
docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/install-test.sh
```

Windows PowerShell users: write the mount as `-v "${PWD}:/lab"` (the whole value in quotes); `"$PWD":/lab` splits into two arguments in PowerShell and Docker fails with "invalid reference format".

The last command installs 1.0-1 into a **fresh** container, upgrades to 1.0-2, removes and purges (chapter 04 shows the output). A clean container shows what a customer's host will see; your workstation already has every dependency.

`dpkg-deb` packages whatever is in the tree; it does not build anything. [43] For software that has to be compiled and integrated with the distribution, use debhelper.

## Level 2: a source package and `dh`

A Debian **source** package is your source tree plus a `debian/` directory holding its own control file and `debian/rules`. `debian/rules` is a makefile, and with debhelper it is usually three lines: [44]

```make
#!/usr/bin/make -f
%:
	dh $@
```

`dh` runs a sequence of debhelper commands for each target (configure, build, install, package). To change one step, add an `override_dh_<command>` target. `dh binary-arch --no-act` prints the commands a sequence would run without running them, and `--with <addon>` inserts an add-on's commands. [44]

For Python, `dh-python` provides **pybuild**, which "invokes various build systems for requested Python versions". The usual rules line is: [45]

```make
%:
	dh $@ --with python3 --buildsystem=pybuild
```

pybuild's `pyproject` plugin drives the PEP 517 interface from chapter 02, and files go into a `dist-packages` directory. [45] Python tools are not run by default, so the `--with python3` add-on is required. [44]

## Three ways to ship Python

| | dh-python (pybuild) | Bundled venv (dh-virtualenv, or by hand) | Generic packager (nfpm, fpm) |
| --- | --- | --- | --- |
| Where the code goes | system `dist-packages` [45] | `/opt/venvs/<package>` by default [47] | wherever you list |
| Dependencies come from | Debian packages | PyPI or your index, frozen into the venv | whatever you put in the tree |
| Build input | a Debian source package | requirements file and your project [47] | a config file and files |
| Best for | libraries and tools that are part of the OS | applications with their own pinned stack | prebuilt payloads, many formats at once |

**dh-python.** Dependencies are Debian packages (`python3-requests`, not `requests>=2.31`). [45] You get the distribution's security updates and one copy of each module. You pay with a constraint: every runtime **and** build dependency must exist as a Debian package for the release you target.

**Bundled venv.** dh-virtualenv "aims to combine Debian packaging with self-contained Python software deployment". [46] It adds a `dh_virtualenv` step (`dh $@ --with python-virtualenv`) to the sequence. [46] [47] Lab 2 (next lesson) does the same by hand in `lab3/build-deb.sh`: create the venv **at its final path** (`/opt/shiplab-devenv`), `pip install` the project, copy the tree into the package, add a `/usr/bin/devenv` symlink. A venv's scripts contain the absolute path of its interpreter, so venvs cannot be moved. [2] You control every version; a security fix in a bundled dependency means rebuilding your package.

**Generic packagers.** nFPM is "A simple deb, rpm, apk, ipk, arch linux, and msix packager written in Go". [48] It takes files plus metadata and emits a package; it does not build Python for you. It suits a payload CI already built, or a product that needs `.deb` and `.rpm` from one config.

## The interpreter dependency: what Lab 2 hit

The first draft of the Lab 2 (chapter 05) package declared `Depends: python3.11`, installed cleanly, and then:

```text
$ devenv --version
bash: line 1: /usr/bin/devenv: cannot execute: required file not found
```

The venv's `bin/python3` is a symlink to `/usr/bin/python3`. On bookworm that file belongs to `python3-minimal` (`dpkg -S /usr/bin/python3`), which the `python3` package pulls in; installing `python3.11` alone left it missing. The fix was to depend on the interpreter package the venv was built with, as a range:

```text
Depends: python3 (>= 3.11), python3 (<< 3.12)
```

The upper bound matters as much as the lower one: a venv's `site-packages` lives under `lib/python3.11/`, so a host upgraded to Python 3.12 would leave every bundled package invisible. dh-virtualenv's usage page does not spell this out; the lab demonstrated it. [47]

## Gotchas

- **Wrong interpreter package.** `Depends: python3.11` installs, then fails with `cannot execute: required file not found`. Check `dpkg -S /usr/bin/python3`; depend on the `python3` range above. [2]
- **No upper bound.** Without `<< 3.12`, a Python 3.12 upgrade hides everything in `lib/python3.11/` and imports fail. Bound both sides. [2]
- **Venv built in a temp dir, then copied.** Its scripts keep the old interpreter path, so the installed commands break. Create the venv at its install path. [2]
- **Building from a Windows or macOS checkout.** The files have no Unix permissions and `dpkg-deb` checks script permissions. Copy and `chmod` inside the container first, as `tiny-deb/build.sh` does. [43]
- **`dh` skips Python.** Without `--with python3`, the Python tools are not run. `dh binary-arch --no-act` shows the sequence. [44]
- **Backend not in the archive.** pybuild uses Debian's packages, not PyPI. The lab project asks for `hatchling >= 1.26`; if your release ships an older one, package that backend first. [45]

:::key-takeaways
- `dpkg-deb --build DIR` turns a tree with `DEBIAN/control` into a `.deb`; it checks the control file and script permissions, and it builds nothing. [43]
- With a source package, `debian/rules` is usually `dh $@`; `dh $@ --with python3 --buildsystem=pybuild` builds Python into `dist-packages`. [44] [45]
- dh-virtualenv bundles a venv under `/opt/venvs/<package>` by default; nFPM packages prepared files into deb, rpm and other formats. [47] [48]
- A bundled venv must be built at its install path and depend on a bounded range of the exact `python3` it links to. [2]
:::

:::glossary
- **Binary package**: a `.deb` that installs files.
- **Source package**: the source tree plus `debian/`, from which binary packages are built.
- **debhelper**: a collection of `dh_*` tools that automate common packaging steps.
- **`dh`**: the debhelper sequencer that runs those tools in order.
- **`debian/rules`**: the makefile that drives a source package's build.
- **pybuild**: dh-python's build system for Python packages.
- **`dist-packages`**: Debian's name for site-packages of apt-installed Python modules.
- **dh-virtualenv**: a debhelper add-on that ships a prebuilt virtualenv inside a `.deb`.
- **nFPM**: a single-binary tool that builds deb, rpm and other packages from a config file.
- **Interpreter range**: a `Depends` with a lower and an upper bound on the Python package.
:::
