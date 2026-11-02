---
id: l09
title: "Versions that sort the way you think: PEP 440"
quiz: quiz-05.yaml
resources: []
sources: [14]
---
After this lesson you can write version numbers that sort correctly for pre-releases, post-releases and hotfixes, read `~=` and `==1.4.*` specifiers, and explain why `pip install pkg` skipped the release candidate you just uploaded.

## The scheme

Every public Python version must fit this pattern: [14]

```text
[N!]N(.N)*[{a|b|rc}N][.postN][.devN]
```

- `N!` is an optional **epoch**, written first. If absent, the epoch is 0. [14]
- `N(.N)*` is the release: `1`, `1.4`, `2.7.3`.
- `a`, `b`, `rc` mark alpha, beta and release-candidate **pre-releases**.
- `.postN` marks a **post-release**: a fix to packaging or docs after the final release.
- `.devN` marks a **developmental release**.

A **local version** may follow a `+`, as in `1.0+abc.5`. [14] It is for builds that never go to a public index, such as a distribution's patched rebuild.

## Ordering

Within one release, suffixes sort in this order: [14]

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

Three rules hide in that list. A dev release of a pre-release sorts before the pre-release itself. A local version sorts after its public version. And `1.0.15` is a later release than `1.0.post456`, because post-releases belong to `1.0`. Lab 2's `devenv compare` uses the `packaging` library, which implements these rules:

```text
$ devenv compare 1.0rc1 1.0
1.0rc1 < 1.0
$ devenv compare 1.0.post1 1.0
1.0.post1 > 1.0
```

## Normalisation: many spellings, one version

Tools accept loose spellings and normalise them. Some examples from the PEP: `1.1RC1` → `1.1rc1`; `1.1-a1` or `1.1.a1` → `1.1a1`; `1.2-post2` → `1.2.post2`; `1.0-1` → `1.0.post1`; `1.2dev2` → `1.2.dev2`; `1.0+ubuntu-1` → `1.0+ubuntu.1`. [14]

The `1.0-1` case matters for this course. In Debian, `1.0-1` means upstream version 1.0, packaging revision 1 (chapter 04). In Python it normalises to the post-release `1.0.post1`. The same string means different things to the two packaging systems.

## Specifiers you will actually write

| Specifier | Means |
| --- | --- |
| `==1.4.*` | any version with the prefix 1.4, such as `1.4.0` or `1.4.7.post1` [14] |
| `~=1.4.5` | `>=1.4.5, ==1.4.*`: patch updates only [14] |
| `~=2.2` | `>=2.2, ==2.*`: minor updates allowed [14] |
| `===foobar` | plain string equality, for versions that do not follow the scheme [14] |

`~=` must not be used with a single number (`~=1` is invalid). [14] Prefix matching has a trap. Given `1.1.post1`, `== 1.1` does **not** match, while `== 1.1.*` does. [14]

## Pre-releases are excluded by default

Pre-releases of any kind, including dev releases, are implicitly excluded from all version specifiers. [14] So after you upload `2.0rc1`, `pip install pkg` still installs `1.9`. To test the candidate, ask for it explicitly (`pkg==2.0rc1`) or use the installer's pre-release option.

:::low-confidence
The exclusion is about how an installer picks among available candidates. In a test for this course, the `packaging` library was asked whether the single version `1.4.6rc1` satisfies `~=1.4.5`, and it answered yes. Only the PEP's one-line rule was read, not its full list of exceptions. Check the version specifiers specification on packaging.python.org before relying on edge cases.
:::

## Epochs: the last resort

An epoch comes before every other part of the version and has an implicit value of 0. [14] So `1!1.0` sorts after `2024.10`, and a project can restart its numbering, say from date-based versions to `1.0`. Dropping the epoch later would make new versions sort below old ones, so treat it as a one-way door. Debian's epochs carry the same warning (chapter 04).

:::key-takeaways
- Public versions follow `[N!]N(.N)*[{a|b|rc}N][.postN][.devN]`; local versions add `+label`. [14]
- Order within a release: dev < a < b < rc < final < post. [14]
- `~=1.4.5` means `>=1.4.5, ==1.4.*`; `~=1` is invalid. [14]
- Pre-releases are excluded unless requested explicitly. [14]
- `1.0-1` normalises to `1.0.post1` in Python but means "revision 1" in Debian. [14]
:::

:::glossary
- **Pre-release**: an alpha (`a`), beta (`b`) or release candidate (`rc`) published before the final version.
- **Post-release**: a release after the final one that fixes packaging or documentation, such as `1.0.post1`.
- **Dev release**: an in-development build such as `1.0.dev3`.
- **Epoch**: a leading `N!` that overrides normal ordering; once added it cannot be dropped.
- **Local version**: a `+label` suffix for builds that are never published to a public index.
- **Specifier**: a version rule such as `>=1.4` or `~=1.4.5`.
- **Normalisation**: rewriting a loosely written version into its one canonical spelling.
:::
