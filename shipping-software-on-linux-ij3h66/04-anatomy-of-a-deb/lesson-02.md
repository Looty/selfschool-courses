---
id: l15
title: "Relationship fields: Depends to Provides"
quiz: quiz-02.yaml
resources: []
sources: [31, 40]
---
After this lesson you can choose the right relationship field for each situation, explain when each one is enforced, and write the `Breaks` + `Replaces` pair for moving a file between packages.

## Syntax

All relationship fields share one syntax: a comma-separated list of package names, each optionally with a version relation in parentheses. The relations are `<<`, `<=`, `=`, `>=` and `>>` (strictly earlier, earlier or equal, exactly equal, later or equal, strictly later). Alternatives are separated by `|`, and an architecture restriction in square brackets limits a clause to some architectures. [31]

```text
Depends: python3 (>= 3.11), python3 (<< 3.12), libssl3 | libssl1.1
```

The two `python3` clauses together express a range; Lab 3's bundled-venv package uses exactly this line (chapter 05).

## The dependency fields

| Field | Meaning | Enforced |
| --- | --- | --- |
| `Depends` | absolute dependency | the package will not be **configured** until every Depends is configured [31] |
| `Pre-Depends` | like Depends, but dpkg completes the installation of the named packages before even starting this one's | at **unpack**; "should be used sparingly" [31] |
| `Recommends` | "a strong, but not absolute, dependency" [31] | apt installs them unless told `--no-install-recommends` [40] |
| `Suggests` | related packages that may be useful | not installed by default |
| `Enhances` | the reverse of Suggests: this package enhances another | informational |

The "enforced at configure time" detail explains chapter 06's `iU` state: `dpkg -i` happily unpacks a package whose dependencies are missing and then refuses to configure it. [31]

## Saying "not with that"

- **`Breaks`**: dpkg refuses to unpack the declaring package while the broken package is installed and configured, unless it can deconfigure the broken one first. It normally carries an "earlier than" version, and it tells apt the broken package must be upgraded before the new one. [31]
- **`Conflicts`**: dpkg refuses to have both packages unpacked at the same time. It is stronger, so Policy prefers `Breaks` unless the two packages really cannot be unpacked side by side. [31]

## Virtual packages: `Provides`

A virtual package is a name that appears in another package's `Provides` field; anything depending on the virtual name is satisfied by any provider. [31] Versioned Provides are only allowed with `=` (`Provides: foo-api (= 2)`). An unversioned Provides does not satisfy a versioned dependency, and does not trigger a versioned `Conflicts` or `Breaks`. [31] That is a common surprise: `Depends: mta (>= 2)` is never satisfied by a package that just says `Provides: mta`.

## `Replaces`: taking over files

It is usually an error for a package to contain a file that is already on the system in another package. `Replaces` is how a package says it may overwrite files of another package, and Policy says it should normally be used together with `Breaks`. [31] The textbook case is a split: package `foo` becomes `foo` plus `foo-data` from version 1.2-3. [31]

```text
# foo-data
Replaces: foo (<< 1.2-3)
Breaks: foo (<< 1.2-3)

# the new foo
Depends: foo-data (>= 1.2-3)
```

- `Replaces` lets `foo-data` take over the files the old `foo` owned;
- `Breaks` makes sure the old `foo` is upgraded to 1.2-3 (which no longer ships those files) rather than left half-overwritten;
- the new `foo` depends on `foo-data`, so users get both.

`Replaces` has a second use: combined with `Conflicts`, it tells the package system which package to remove when the two conflict, for example when one package fully replaces another (even a virtual one). [31] Lab 4's file-conflict scenario walks through the first use step by step.

## Relationships in a product you ship

When a product is several packages, relationships are your compatibility contract:

- a meta-package (`shiplab-suite` in Lab 3) depends on every component with **ranges**, not exact pins, so a component hotfix (0.1.0-1 to 0.1.1-1) installs without rebuilding the suite;
- a component that changes an interface bumps its upstream version and the suite's upper bound (`<< 0.2`) stops an incompatible upgrade from being pulled in silently;
- when files move between your own packages, ship the `Breaks` + `Replaces` pair in the same release.

:::key-takeaways
- Relations: `<<`, `<=`, `=`, `>=`, `>>`; alternatives with `|`. [31]
- `Depends` is enforced at configure time; `Pre-Depends` before unpack, and sparingly. [31]
- Prefer `Breaks` (usually versioned) over `Conflicts`. [31]
- Versioned Provides only with `=`; an unversioned Provides never satisfies a versioned dependency. [31]
- Moving files between packages: `Replaces` + `Breaks` on the new owner, with an earlier-than version. [31]
:::

:::glossary
- **Relationship field**: a control field that relates a package to others, such as Depends or Breaks.
- **Virtual package**: a name no real package has, provided by one or more packages through `Provides`.
- **Meta-package**: a package with no real content that depends on a set of other packages.
- **Configure**: dpkg's step after unpacking, which runs `postinst configure`.
- **Deconfigure**: dpkg temporarily marking an installed package as not configured so another can be unpacked.
:::
