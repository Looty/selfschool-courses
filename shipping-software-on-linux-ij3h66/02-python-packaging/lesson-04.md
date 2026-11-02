---
id: l08
title: "sdist vs wheel, and what wheel tags promise"
quiz: quiz-04.yaml
resources: []
sources: [12, 15, 18]
---
After this lesson you can read any wheel file name, tell a pure wheel from a platform wheel, explain what `manylinux_2_17` promises about glibc, and work out why pip fell back to building from source on a given host.

## Two kinds of distribution

`python -m build` produces two files. [18] From Lab 2:

```text
dist/
├── shiplab_devenv-0.1.0-py3-none-any.whl
└── shiplab_devenv-0.1.0.tar.gz
```

- The **sdist** (`.tar.gz`) is source plus metadata. Installing it means building it first: the installer runs the backend's `build_wheel` hook, which may need a compiler and headers. [12]
- The **wheel** (`.whl`) is already built; installing is unpacking files into site-packages and writing wrappers.

On an offline host or in a slim container, the difference decides whether an install takes one second or fails for lack of `gcc`. That is why Lab 2 mirrored dependencies with `--only-binary :all:`.

## Reading a wheel name

After the name and version, a wheel file name carries three tags: `{python tag}-{abi tag}-{platform tag}`. [15]

| Wheel | python | abi | platform | Meaning |
| --- | --- | --- | --- | --- |
| `shiplab_devenv-0.1.0-py3-none-any.whl` | `py3` | `none` | `any` | pure Python, any Python 3, any OS |
| `pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl` | `cp312` | `cp312` | several `manylinux` tags | compiled for CPython 3.12 on x86-64 Linux |

`none` as an ABI means no ABI requirement, and `any` as a platform means the wheel runs anywhere. [15] `abi3` is CPython's stable ABI: one build that works across several CPython versions. [15] The pyyaml name shows a **compressed tag set**: each position may hold several dot-separated tags, and the wheel matches if any combination does. [15] The pyyaml wheel was downloaded for this lesson on a `python:3.12-slim-bookworm` container. Its name is real, not taken from a source.

## How pip chooses

The installer keeps a list of tag triples that the running interpreter supports. A wheel can be installed if its tag is in the list, and the installer should prefer the most specific match. [15] `pip debug --verbose` prints that list. On the bookworm container it listed 987 compatible tags, starting with:

```text
cp312-cp312-manylinux_2_36_x86_64
cp312-cp312-manylinux_2_35_x86_64
cp312-cp312-manylinux_2_34_x86_64
```

If no wheel for a release matches any tag in that list, pip falls back to the sdist and tries to build it. On a slim image that is the moment you see compiler errors for a package you thought was "just a pip install".

## manylinux: a promise about glibc

A Linux wheel cannot say `linux_x86_64` and hope for the best, because a compiled extension links against the C library of the system it was built on. The `manylinux_x_y` tag states the oldest glibc the wheel needs: `x` and `y` are the glibc major and minor versions. [15] The older names are aliases: `manylinux1` means glibc 2.5, `manylinux2010` means 2.12 and `manylinux2014` means 2.17. [15] The rule is one-way: a wheel built for an old glibc runs on newer systems, not the other way round. [15]

Debian 12's glibc is 2.36:

```text
$ ldd --version | head -1
ldd (Debian GLIBC 2.36-9+deb12u14) 2.36
```

That is why the tag list above starts at `manylinux_2_36`: the host accepts any wheel needing glibc 2.36 or older. A wheel tagged only `manylinux_2_39` would not match, and pip would build from source instead. The `auditwheel` tool checks and retags wheels; version 3.3.0 or newer is needed for the `manylinux_x_y` style. [15] On Alpine and other musl-based systems the matching family is `musllinux_x_y`. [15]

## Pure vs platform wheels when you ship

- Pure (`py3-none-any`): one file for every target. Your own CLI tools should be this.
- Platform: one file per Python version, ABI and platform you support. An air-gapped mirror needs the exact wheels for each target host. Download them with `--only-binary :all:` and the matching interpreter, or pip will try to build sdists on the offline host.

:::key-takeaways
- An sdist must be built before install; a wheel is unpacked. [12]
- Wheel names end in `{python}-{abi}-{platform}` tags; `py3-none-any` means pure Python. [15]
- pip installs a wheel only if its tag is in the interpreter's supported list; `pip debug --verbose` shows the list. [15]
- `manylinux_x_y` names the oldest glibc needed; manylinux2014 = glibc 2.17; older-glibc wheels run on newer systems, not the reverse. [15]
:::

:::glossary
- **sdist**: a source distribution that must be built before installing.
- **Wheel**: a pre-built distribution, a zip file that installers unpack.
- **Tag**: a short label in a wheel name saying which Pythons, ABIs and platforms it supports.
- **ABI**: application binary interface, the low-level contract between compiled code and the interpreter.
- **Stable ABI (`abi3`)**: a subset of CPython's ABI that stays the same across versions.
- **glibc**: the GNU C library, the standard C library on Debian and most Linux systems.
- **manylinux**: the wheel platform tag family that promises compatibility with glibc-based Linux systems.
- **musl**: an alternative C library used by Alpine Linux.
- **auditwheel**: a tool that checks a Linux wheel's library dependencies and assigns manylinux tags.
:::
