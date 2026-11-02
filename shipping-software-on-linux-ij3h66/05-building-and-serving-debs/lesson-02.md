---
id: l19
title: "Putting Python into a .deb: dh-python, dh-virtualenv or nfpm"
quiz: quiz-02.yaml
resources: [../resources/lab3/build-deb.sh]
sources: [2, 45, 46, 47, 48]
---
After this lesson you can choose between packaging a Python application against the system Python, bundling it with its own virtualenv, or wrapping it with a generic packager, and you know the failure each choice invites.

## Three strategies

| | dh-python (pybuild) | Bundled venv (dh-virtualenv, or by hand) | Generic packager (nfpm, fpm) |
| --- | --- | --- | --- |
| Where the code goes | system `dist-packages` [45] | `/opt/venvs/<package>` by default [47] | wherever you list |
| Dependencies come from | Debian packages | PyPI or your index, frozen into the venv | whatever you put in the tree |
| Build input | a Debian source package | requirements file and your project [47] | a config file and files |
| Best for | libraries and tools that are part of the OS | applications with their own pinned stack | prebuilt payloads, many formats at once |

## dh-python: be part of the distribution

pybuild builds your project for the distribution's Python and installs it into `dist-packages`, with dependencies expressed as Debian packages (`python3-requests`, not `requests>=2.31`). [45] You get security updates for shared libraries from the distribution and one copy of each module on the system. You pay with the constraint from lesson 18: every runtime **and** build dependency, including the PEP 517 backend version your `pyproject.toml` asks for, must exist as a Debian package for the release you target.

## Bundled venv: ship your own stack

dh-virtualenv "aims to combine Debian packaging with self-contained Python software deployment" by building a virtualenv during the package build. [46] It adds a `dh_virtualenv` step to the debhelper sequence (`dh $@ --with python-virtualenv`), installs into `/opt/venvs/<packagename>` by default, takes the interpreter from `--python` (default: the system's), and can use the standard-library `venv` module with `--builtin-venv`. [46] [47] Its tutorial still shows Python 2 era fields, so read it with care. [46]

Lab 3 builds the same thing by hand with `dpkg-deb`, which makes the mechanics visible: create the venv **at its final path** (`/opt/shiplab-devenv`), `pip install` the project into it, copy the tree into the package, add a `/usr/bin/devenv` symlink. Building at the final path is not optional: a venv's scripts contain the absolute path of its interpreter, so venvs cannot be moved. [2]

The trap Lab 3 hit on the first run. The package declared `Depends: python3.11`, installed cleanly, and then:

```text
$ devenv --version
bash: line 1: /usr/bin/devenv: cannot execute: required file not found
```

The venv's `bin/python3` is a symlink to `/usr/bin/python3`. On bookworm that file belongs to `python3-minimal` (`dpkg -S /usr/bin/python3`), which the `python3` package pulls in; installing `python3.11` alone left it missing. The fix was to depend on the interpreter package the venv was built with, as a range:

```text
Depends: python3 (>= 3.11), python3 (<< 3.12)
```

The upper bound matters as much as the lower one: a venv's `site-packages` lives under `lib/python3.11/`, so a host upgraded to Python 3.12 would leave every bundled package invisible. dh-virtualenv's usage page does not spell this out; it is what the lab demonstrated. [47]

Trade-off: you control every version, and a security fix in a bundled dependency means rebuilding and shipping your package. That is exactly the "patch one component" flow of Lab 3.

## Generic packagers

nFPM describes itself as "A simple deb, rpm, apk, ipk, arch linux, and msix packager written in Go" with "No Ruby, no tar, no external dependencies". [48] Tools in this family take a list of files plus metadata and emit a package; they do not build Python for you. They pair well with a CI step that already produced the payload (a venv tree, a binary) and with products that need `.deb` and `.rpm` from one config. The nFPM page read for this course does not compare itself with fpm. [48]

## Choosing

- An internal service or CLI with pinned dependencies, deployed to hosts you control: bundled venv.
- A library or tool that should look native and follow the distribution's updates: dh-python, if its dependencies are packaged.
- Several package formats, or a payload built elsewhere: nFPM, with the same `Depends` discipline as above.

Whatever you choose, the hard rules from this lesson hold: depend on the interpreter your code actually runs, never assume a venv can move, and test the result in a clean container.

:::key-takeaways
- pybuild installs into system `dist-packages` with dependencies as Debian packages. [45]
- dh-virtualenv bundles a venv under `/opt/venvs/<package>` by default. [47]
- A bundled venv must be built at its install path and depend on a bounded range of the exact `python3` it links to. [2]
- nFPM packages prepared files into deb, rpm and other formats from a single Go binary. [48]
:::

:::glossary
- **dh-python**: Debian's helpers for packaging Python, including pybuild.
- **dh-virtualenv**: a debhelper add-on that ships a prebuilt virtualenv inside a `.deb`.
- **nFPM**: a single-binary tool that builds deb, rpm and other packages from a config file.
- **Bundled dependencies**: libraries shipped inside your package instead of taken from the distribution.
- **Interpreter range**: a `Depends` with a lower and an upper bound on the Python package.
:::
