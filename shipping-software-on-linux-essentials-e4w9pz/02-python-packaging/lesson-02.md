---
id: l04
title: "What you ship: sdist vs wheel, wheel tags and PEP 440 versions"
quiz: quiz-02.yaml
resources: []
sources: [12, 14, 15, 18]
---
After this lesson you can read a wheel file name, explain what `manylinux_2_17` promises about glibc, work out why pip built from source, and write versions that sort correctly.

## sdist and wheel

`python -m build` produces two files. [18] From the course's test run, building the `devenv` CLI:

```text
dist/
├── shiplab_devenv-0.1.0-py3-none-any.whl
└── shiplab_devenv-0.1.0.tar.gz
```

- The **sdist** (`.tar.gz`) is source plus metadata. Installing it means building it first: the installer runs the backend's `build_wheel` hook, which may need a compiler and headers. [12]
- The **wheel** (`.whl`) is already built. Installing it means unpacking files into site-packages and writing wrappers.

## Reading a wheel name

After the name and version, a wheel name carries three tags: `{python tag}-{abi tag}-{platform tag}`. [15]

| Wheel | python | abi | platform | Meaning |
| --- | --- | --- | --- | --- |
| `shiplab_devenv-0.1.0-py3-none-any.whl` | `py3` | `none` | `any` | pure Python, any Python 3, any OS |
| `pyyaml-6.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl` | `cp312` | `cp312` | several `manylinux` tags | compiled for CPython 3.12 on x86-64 Linux |

`none` means no ABI requirement; `any` means any platform. [15] `abi3` is CPython's stable ABI: one build that works across several CPython versions. [15] The pyyaml name is a **compressed tag set**: each position may hold several dot-separated tags, and the wheel matches if any combination does. [15]

## How pip chooses, and what manylinux promises

The installer keeps a list of tag triples the running interpreter supports. A wheel can be installed only if its tag is in that list, and the most specific match is preferred. [15] `pip debug --verbose` prints the list. On a `python:3.12-slim-bookworm` container it listed 987 tags, starting with:

```text
cp312-cp312-manylinux_2_36_x86_64
cp312-cp312-manylinux_2_35_x86_64
cp312-cp312-manylinux_2_34_x86_64
```

If no wheel matches, pip falls back to the sdist and tries to build it.

A compiled extension links against the C library of the system it was built on. `manylinux_x_y` states the oldest glibc the wheel needs. [15] Older names are aliases: `manylinux1` = glibc 2.5, `manylinux2010` = 2.12, `manylinux2014` = 2.17. [15] The rule is one-way: a wheel built for an old glibc runs on newer systems, not the reverse. [15] Debian 12 has glibc 2.36:

```text
$ ldd --version | head -1
ldd (Debian GLIBC 2.36-9+deb12u14) 2.36
```

That is why the tag list starts at `manylinux_2_36`. On musl-based systems such as Alpine, the family is `musllinux_x_y`. [15] `auditwheel` checks and retags wheels; the `manylinux_x_y` style needs version 3.3.0 or newer. [15]

Ship your own CLI tools as pure `py3-none-any` wheels: one file for every target.

## PEP 440: the version scheme

Every public Python version fits this pattern: [14]

```text
[N!]N(.N)*[{a|b|rc}N][.postN][.devN]
```

`N!` is an optional **epoch** (0 if absent); `N(.N)*` is the release; `a`, `b`, `rc` are **pre-releases**; `.postN` is a **post-release** that fixes packaging or docs; `.devN` is a **dev release**. A **local version** follows a `+`, as in `1.0+abc.5`, for builds that never go to a public index. [14]

Within one release, the order is: [14]

```text
.devN  <  aN  <  bN  <  rcN  <  (no suffix)  <  .postN
```

A slice of PEP 440's own example, earliest first: [14]

```text
1.0.dev456
1.0a1
1.0b2.post345
1.0rc1
1.0
1.0+abc.5
1.0.post456
1.0.15
1.1.dev1
```

A local version sorts after its public version, and `1.0.15` is later than `1.0.post456`, because post-releases belong to `1.0`. [14] The course CLI's `devenv compare` uses the `packaging` library, which implements these rules:

```text
$ devenv compare 1.0rc1 1.0
1.0rc1 < 1.0
$ devenv compare 1.0.post1 1.0
1.0.post1 > 1.0
```

Tools normalise loose spellings: `1.1RC1` → `1.1rc1`; `1.1-a1` → `1.1a1`; `1.0-1` → `1.0.post1`; `1.2dev2` → `1.2.dev2`; `1.0+ubuntu-1` → `1.0+ubuntu.1`. [14]

## Specifiers

| Specifier | Means |
| --- | --- |
| `==1.4.*` | any version with the prefix 1.4, such as `1.4.0` or `1.4.7.post1` [14] |
| `~=1.4.5` | `>=1.4.5, ==1.4.*`: patch updates only [14] |
| `~=2.2` | `>=2.2, ==2.*`: minor updates allowed [14] |
| `===foobar` | plain string equality, for versions outside the scheme [14] |

`~=1` (a single number) is invalid. [14] Prefix matching compares whole release segments, so `1.10` does not match `== 1.1.*`. [14]

Pre-releases of any kind, including dev releases, are implicitly excluded from all version specifiers. [14]

:::low-confidence
The exclusion is about how an installer picks among available candidates. In a test for this course, the `packaging` library was asked whether the single version `1.4.6rc1` satisfies `~=1.4.5`, and it answered yes. Only the PEP's one-line rule was read, not its full list of exceptions. Check the version specifiers specification on packaging.python.org before relying on edge cases.
:::

An epoch comes before every other part of the version. [14] So `1!1.0` sorts after `2024.10`, which lets a project restart its numbering.

## Gotchas

- **`gcc` failed on a slim image.** `pip install somepkg` ends with `error: command 'gcc' failed`. No wheel matched the interpreter's tags, so pip fell back to the sdist and ran the backend's build. [12] [15] Compare `pip debug --verbose` with the files on the index, and install a matching wheel.
- **A newer-glibc wheel on an older host.** A wheel tagged only `manylinux_2_39` does not match Debian 12 (glibc 2.36, see `ldd --version`), so pip builds from source instead. Use a wheel with an older `manylinux` tag. [15]
- **Offline mirror built on the wrong machine.** Platform wheels downloaded on a laptop match the laptop's Python and platform, not the servers'. The offline host then tries to build sdists. Download with `--only-binary :all:` and the target's interpreter, so the tags match the target. [15]
- **The release candidate is ignored.** After you upload `2.0rc1`, `pip install pkg` still installs `1.9`, because pre-releases are excluded unless requested. Pin `pkg==2.0rc1` or use the installer's pre-release option. [14]
- **`== 1.1` misses the post-release.** Given `1.1.post1`, `== 1.1` does not match, while `== 1.1.*` does. [14]
- **`1.0-1` means two things.** In Python it normalises to the post-release `1.0.post1`; in Debian it means upstream 1.0, packaging revision 1 (chapter 04). [14]
- **Epochs are a one-way door.** Dropping an epoch later makes new versions sort below old ones. [14]

## Check yourself

1. A host runs glibc 2.31. Can pip install a `manylinux_2_34` wheel there?

:::key-takeaways
- An sdist must be built before install; a wheel is unpacked. [12]
- Wheel names end in `{python}-{abi}-{platform}`; `py3-none-any` means pure Python, and pip installs a wheel only if its tag is in the interpreter's list (`pip debug --verbose`). [15]
- `manylinux_x_y` names the oldest glibc needed; old-glibc wheels run on newer systems, not the reverse. [15]
- Order within a release: dev < a < b < rc < final < post; pre-releases are excluded unless requested. [14]
- `~=1.4.5` means `>=1.4.5, ==1.4.*`; `1.0-1` normalises to `1.0.post1`. [14]
:::

:::glossary
- **sdist**: a source distribution that must be built before installing.
- **Wheel**: a pre-built distribution, a zip file that installers unpack.
- **ABI**: application binary interface, the low-level contract between compiled code and the interpreter.
- **Stable ABI (`abi3`)**: a subset of CPython's ABI that stays the same across versions.
- **glibc**: the GNU C library, the standard C library on Debian and most Linux systems.
- **manylinux**: the wheel platform tag family that promises compatibility with glibc-based Linux systems.
- **Pre-release**: an alpha (`a`), beta (`b`) or release candidate (`rc`) published before the final version.
- **Post-release**: a release after the final one that fixes packaging or documentation, such as `1.0.post1`.
- **Epoch**: a leading `N!` that overrides normal ordering; once added it cannot be dropped.
- **Local version**: a `+label` suffix for builds that are never published to a public index.
:::
