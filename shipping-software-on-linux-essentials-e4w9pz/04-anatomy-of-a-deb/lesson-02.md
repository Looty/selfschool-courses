---
id: l08
title: "Debian versions, maintainer scripts and conffiles"
quiz: quiz-02.yaml
resources: [../resources/tiny-deb/install-test.sh, ../resources/tiny-deb/hello-ship/DEBIAN/postinst, ../resources/tiny-deb/hello-ship/DEBIAN/conffiles]
sources: [14, 32, 33, 34, 35, 36, 37, 39, 40]
---
After this lesson you can predict and check how dpkg orders versions, pick a version for a hotfix or backport, say which maintainer script runs when, and predict what happens to a configuration file the admin edited.

## Debian versions

```text
[epoch:]upstream-version[-debian-revision]
```

- **epoch**: a single, usually small, unsigned integer; missing means 0 [33].
- **upstream-version**: the software's own version; it should start with a digit [33].
- **debian-revision**: the version of the packaging. dpkg splits at the **last** hyphen, and a version without a revision sorts earlier than the same version with one [33].

So `1.0-1` is "upstream 1.0, first packaging". In Python, `1.0-1` normalises to the post-release `1.0.post1` instead [14].

dpkg compares the epoch first, then the upstream part, then the revision. Within a part it alternates between non-digit runs, compared character by character with **all letters before all non-letters** and a **tilde before anything, even the end of the part**, and digit runs, compared as numbers [33]. Policy's example: `1.0~beta1~svn1245` < `1.0~beta1` < `1.0` [34].

### Check, don't guess

`dpkg --compare-versions v1 op v2` exits 0 when the relation holds, 1 otherwise. The operators are `lt le eq ne ge gt`, plus `lt-nl le-nl ge-nl gt-nl`, which treat an empty version as later than any version [36]. Every line below was run on `debian:bookworm`:

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

In build scripts, `dpkg --compare-versions "$new" gt "$old" || exit 1` stops a release that would never be offered as an upgrade.

### Choosing versions on purpose

| Situation | Version | Why it sorts right |
| --- | --- | --- |
| Pre-release of 2.0 | `2.0~rc1-1` | `~` sorts before the final `2.0-1` |
| Emergency hotfix on top of `1.4-2` | `1.4-2+hotfix1` | later than `1.4-2`, earlier than `1.4-3` |
| Backport to an older release | `1.4-2~bpo12+1` | earlier than the real `1.4-2`, so the official package wins later |
| Upstream numbering went backwards | `1:0.9-1` | epoch beats everything else |

Policy says epochs "must be used with care" and should not be used to roll a package back [34]. To roll back, prefer shipping the old code under a **new, higher** version (`1.4-3` containing 1.4-1's code); otherwise pin the old version with `apt_preferences` at priority 1000 or more, or install `apt-get install pkg=version` [39] [40].

## Maintainer scripts

A package may ship `preinst`, `postinst`, `prerm` and `postrm` in its control archive. Each starts with `#!`, exits 0 on success and non-zero on failure, and must be **idempotent**: dpkg's error recovery reruns scripts, so a second run must be harmless. Shell scripts should use `set -e` [32].

| Operation | Calls, in order [32] |
| --- | --- |
| Install | `new-preinst install` → unpack → `new-postinst configure` (empty previous version) |
| Upgrade | `old-prerm upgrade NEW` → `new-preinst upgrade OLD NEW` → unpack → `old-postrm upgrade NEW` → `new-postinst configure OLD` |
| Remove | `prerm remove` → files removed → `postrm remove` |
| Purge | (after remove) conffiles deleted → `postrm purge` |

`postinst configure` receives the most recently configured version, which is how a script tells a first install from an upgrade [32]. `hello-ship`'s postinst prints it:

```sh
#!/bin/sh
set -e
case "$1" in
  configure)
    echo "hello-ship postinst: configure (previous version: '${2:-none}')"
    ;;
esac
exit 0
```

```text
$ apt-get install ./hello-ship_1.0-1_all.deb
Setting up hello-ship (1.0-1) ...
hello-ship postinst: configure (previous version: 'none')
$ apt-get install ./hello-ship_1.0-2_all.deb
Setting up hello-ship (1.0-2) ...
hello-ship postinst: configure (previous version: '1.0-1')
```

(From `tiny-deb/install-test.sh` on `debian:bookworm`, after building both packages as in the previous lesson.) Keep the `case "$1"` habit, or the script does install-time work during an abort or upgrade.

If a new `preinst` fails during an upgrade, dpkg unwinds with `new-postrm abort-upgrade` and `old-postinst abort-upgrade NEW` [32]. Later failures have no such unwind (see Gotchas).

## Conffiles

A **conffile** is a file listed in the package's `conffiles` control file. Almost all conffiles are configuration files, but not every configuration file is a conffile [35]. The rules [35]:

- local changes must survive upgrades;
- configuration survives `remove` and disappears only on `purge`;
- maintainer scripts must never modify a conffile, of their own package or any other;
- a file must not be both a conffile and managed by scripts.

`hello-ship` lists `/etc/hello-ship.conf` in `DEBIAN/conffiles`. The test edits it, upgrades, removes and purges:

```text
$ hello-ship                      # after editing GREETING and upgrading to 1.0-2
hi, edited locally from hello-ship 1.0-2
$ apt-get remove hello-ship; dpkg -l hello-ship | tail -n 1; ls -l /etc/hello-ship.conf
rc  hello-ship     1.0-2        all          tiny example package ...
-rw-r--r-- 1 root root 121 Nov  2 17:11 /etc/hello-ship.conf
$ apt-get purge hello-ship; dpkg -l hello-ship
dpkg-query: no packages found matching hello-ship
```

While installed the package shows `ii` in `dpkg -l` [37]. The edit survived the upgrade, `remove` left the package in state `rc` with its config in place, and `purge` removed both [35] [37].

The other style is **script-managed** configuration: `postinst` creates the file (for example from debconf answers) and `postrm purge` deletes it, so it must not be in `conffiles` or the package's data [35].

## Gotchas

- **A tilde hotfix that never installs.** `3.2-4~hotfix1` sorts *before* `3.2-4`, so apt never offers it. Use `+hotfix1`, and gate releases with `dpkg --compare-versions "$new" gt "$old"` [33] [36].
- **An epoch used as a rollback.** Once a package has epoch 1, every later version needs it forever, and Policy says epochs are not for rollbacks. Ship the old code as a new higher version [34].
- **`1.0-1` means two things.** pip reads it as `1.0.post1`, dpkg as upstream 1.0, revision 1 [14] [33]. Map wheel and `.deb` versions deliberately.
- **Half-configured after a failed postinst.** A failing `postinst configure` gets **no** unwind: the files are in place and `dpkg -l` shows `iF`. Fix the cause, then run `dpkg --configure -a` [32] [36] [37].
- **An unattended upgrade stuck at a prompt.** When the packaged conffile changed **and** the admin edited it, dpkg asks. Decide up front with `--force-confold` (keep the admin's file) or `--force-confnew` (take the package's) [36].
- **A script editing its own conffile.** Mixing the styles makes dpkg ask about the file on every upgrade. Stop editing it from scripts, or make it fully script-managed [35].

:::key-takeaways
- `[epoch:]upstream[-revision]`; missing epoch is 0, dpkg splits at the last hyphen, and `~` sorts before everything. [33] [34]
- `dpkg --compare-versions a op b` is the source of truth; epochs are for upstream renumbering, never rollbacks. [34] [36]
- Maintainer scripts are idempotent, use `set -e` and `case "$1"`; `postinst configure` gets the previously configured version. [32]
- A failed `postinst configure` leaves the package half-configured; fix and run `dpkg --configure -a`. [32] [36]
- Conffiles keep local edits on upgrade, stay after remove (`rc`), go on purge; `--force-confold`/`--force-confnew` answer the prompt. [35] [36] [37]
:::

:::glossary
- **Upstream version**: the version of the software as its authors released it.
- **Debian revision**: the version of the packaging, after the last hyphen.
- **Epoch**: a leading `N:` that overrides the rest of the comparison.
- **Tilde (`~`)**: the character that sorts before everything, used for pre-releases and backports.
- **Backport**: a newer package rebuilt for an older distribution release.
- **Hotfix**: an urgent fix shipped outside the normal release cycle.
- **Maintainer script**: `preinst`, `postinst`, `prerm` or `postrm`, run by dpkg at fixed points.
- **Conffile**: a file listed in `conffiles` whose local changes dpkg preserves.
- **Purge**: removing a package together with its configuration files.
- **Unwind**: dpkg calling scripts with `abort-*` arguments to undo a failed step.
- **debconf**: Debian's system for asking configuration questions during install.
- **`rc` state**: removed, configuration files remain.
:::
