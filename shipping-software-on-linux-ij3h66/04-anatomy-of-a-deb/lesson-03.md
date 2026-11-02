---
id: l16
title: "Debian versions: epoch, upstream, revision and the tilde"
quiz: quiz-03.yaml
resources: []
sources: [14, 33, 34, 36, 39, 40]
---
After this lesson you can predict how dpkg orders any two versions, choose a version for a hotfix or a backport that sorts where you need it, and check your choice with `dpkg --compare-versions` instead of guessing.

## The format

```text
[epoch:]upstream-version[-debian-revision]
```

- **epoch**: a single, usually small, unsigned integer; if it is missing, it is 0. [33]
- **upstream-version**: the version of the software itself; alphanumerics and `. + - ~` (hyphen only if there is a revision, colon only if there is an epoch), and it should start with a digit. [33]
- **debian-revision**: the version of the packaging of that upstream version, compared the same way. dpkg splits at the **last** hyphen, and a version without a revision sorts earlier than the same version with one. [33]

So `1.0-1` is "upstream 1.0, first packaging". Note how this differs from Python, where `1.0-1` normalises to the post-release `1.0.post1` (lesson 9). [14]

## The comparison algorithm

dpkg compares the epoch first, then the upstream part, then the revision. Within a part it alternates between a run of non-digits and a run of digits: non-digit runs are compared character by character, with **all letters sorting before all non-letters** and a **tilde sorting before anything, even the end of the part**; digit runs are compared as numbers. [33] Policy's illustration of the tilde rule: `~~` < `~~a` < `~` < (the empty part) < `a`, and `1.0~beta1~svn1245` < `1.0~beta1` < `1.0`. [34]

## Check, don't guess

`dpkg --compare-versions v1 op v2` exits 0 when the relation holds, 1 otherwise. The operators are `lt le eq ne ge gt` (the symbolic `<< <= = >= >>` forms exist for compatibility), plus `lt-nl le-nl ge-nl gt-nl`, which treat an empty version as later than any version. [36] Every line below was run on `debian:bookworm` for this lesson:

```text
dpkg --compare-versions 1.0~rc1        lt  1.0            -> true
dpkg --compare-versions 1.0            lt  1.0-1          -> true
dpkg --compare-versions 1.0-1          lt  1.0-1+hotfix1  -> true
dpkg --compare-versions 1.0-1+hotfix1  lt  1.0-2          -> true
dpkg --compare-versions 1:0.9          gt  2.0            -> true
dpkg --compare-versions 1.0.15         gt  1.0.9          -> true
dpkg --compare-versions 1.0-1~bpo12+1  lt  1.0-1          -> true
dpkg --compare-versions 0.1.1-1        lt  0.2            -> true
```

Use it in build scripts: `dpkg --compare-versions "$new" gt "$old" || exit 1` stops a release that would never be offered as an upgrade.

## Choosing versions on purpose

| Situation | Version | Why it sorts right |
| --- | --- | --- |
| Pre-release of 2.0 | `2.0~rc1-1` | `~` sorts before the final `2.0-1` |
| Repackaging the same upstream | `1.4-2` | only the revision changes |
| Emergency hotfix on top of `1.4-2`, before the next proper revision | `1.4-2+hotfix1` | later than `1.4-2`, earlier than `1.4-3` |
| Backport to an older release | `1.4-2~bpo12+1` | earlier than the real `1.4-2`, so the official package wins later |
| Upstream numbering went backwards | `1:0.9-1` | epoch beats everything else |

On epochs, Policy says they "can help when the upstream version numbering scheme changes, but they must be used with care", and that they should not be used to roll a package back. [34] Once a package has epoch 1, every later version needs it too, forever.

## Rolling back

There is no "downgrade" version trick that is safe across a fleet. Options, in order of preference: ship the old code under a **new, higher** version (`1.4-3` containing 1.4-1's code); pin the old version with `apt_preferences` at priority 1000 or more, which allows downgrades (chapter 06); or install an explicit version with `apt-get install pkg=version`. [39] [40] An epoch is the wrong tool here. [34]

:::key-takeaways
- `[epoch:]upstream[-revision]`; missing epoch is 0, and dpkg splits at the last hyphen. [33]
- Letters sort before non-letters; `~` sorts before everything, even the end of the part. [33] [34]
- `dpkg --compare-versions a op b` is the source of truth; `lt-nl` and friends treat empty as latest. [36]
- `+hotfix1` and `~bpo` suffixes place a version just after or just before a revision. Verified with dpkg above.
- Epochs are for upstream renumbering, never for rollbacks. [34]
:::

:::glossary
- **Upstream version**: the version of the software as its authors released it.
- **Debian revision**: the version of the packaging, after the last hyphen.
- **Epoch**: a leading `N:` that overrides the rest of the comparison.
- **Tilde (`~`)**: the character that sorts before everything, used for pre-releases and backports.
- **Backport**: a newer package rebuilt for an older distribution release.
- **Hotfix**: an urgent fix shipped outside the normal release cycle.
:::
