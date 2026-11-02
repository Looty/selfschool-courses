---
id: l17
title: "Maintainer scripts and conffiles"
quiz: quiz-04.yaml
resources: [../resources/tiny-deb/install-test.sh, ../resources/tiny-deb/hello-ship/DEBIAN/postinst, ../resources/tiny-deb/hello-ship/DEBIAN/conffiles]
sources: [32, 35, 36, 37]
---
After this lesson you can say which maintainer script runs, with which arguments, during install, upgrade, remove and purge; write a `postinst` that is safe to run twice; and predict what happens to a configuration file the admin edited.

## The four scripts

A package may ship `preinst`, `postinst`, `prerm` and `postrm` in its control archive. Each must start with a `#!` line, return 0 on success and non-zero on failure, and be **idempotent**: running it again after it succeeded must be harmless, and after a failure it should finish the job, because dpkg's error recovery reruns scripts. Shell scripts should use `set -e`. [32]

## Who runs when

The calls, simplified from Policy chapter 6: [32]

| Operation | Calls, in order |
| --- | --- |
| Install | `new-preinst install` → unpack → `new-postinst configure` (empty previous version) |
| Upgrade | `old-prerm upgrade NEW` → `new-preinst upgrade OLD NEW` → unpack → `old-postrm upgrade NEW` → `new-postinst configure OLD` |
| Remove | `prerm remove` → files removed → `postrm remove` |
| Purge | (after remove) conffiles deleted → `postrm purge` |

`postinst configure` receives the most recently configured version, which is how a script tells a first install from an upgrade. `hello-ship`'s postinst prints it:

```text
$ apt-get install ./hello-ship_1.0-1_all.deb
Setting up hello-ship (1.0-1) ...
hello-ship postinst: configure (previous version: 'none')
$ apt-get install ./hello-ship_1.0-2_all.deb
Setting up hello-ship (1.0-2) ...
hello-ship postinst: configure (previous version: '1.0-1')
```

(From `tiny-deb/install-test.sh`, run on `debian:bookworm`. Build the two packages first, as in lesson 14.)

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

The `case "$1"` pattern is the habit to keep: a script that ignores its first argument will do install-time work during an abort or an upgrade it did not expect.

## When scripts fail

dpkg tries to unwind: if a new `preinst` fails during an upgrade, it calls `new-postrm abort-upgrade` and `old-postinst abort-upgrade NEW` to put the old version back. [32] A failing `postinst configure` gets **no** unwind: the files are already in place, the package stays **half-configured** (`iF` in `dpkg -l`), and the fix is to correct the cause and run `dpkg --configure -a`. [32] [36] [37] A failing `postrm purge` leaves the package in the config-files state. [32] Past a certain point in an upgrade there is no going back; only a successful reinstall recovers. [32]

Chapter 06 and Lab 4 break a `postinst` on purpose and recover it.

## Conffiles

A **conffile** is a file listed in the package's `conffiles` control file, and dpkg treats it specially. Almost all conffiles are configuration files, but not every configuration file is a conffile. [35] The rules: [35]

- local changes must survive upgrades;
- configuration must survive `remove` and disappear only on `purge`;
- maintainer scripts must never modify a conffile, of their own package or any other;
- a file must not be both a conffile and managed by scripts. If you mix the styles, dpkg asks about overwriting the file on every upgrade.

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

The edit survived the upgrade, `remove` left the package in state `rc` with its config in place, and `purge` removed both. [35] [37] When the packaged version of a conffile changes **and** the admin also edited it, dpkg prompts. In automation you choose up front with `--force-confold` (keep the admin's file) or `--force-confnew` (take the package's), both of which skip the prompt. [36] The test passes `--force-confold` through apt so the run never stops for input.

## Script-managed configuration

The alternative style: the package does not ship the file; `postinst` creates it (for example from a template and debconf answers) and `postrm purge` deletes it. Then the file must **not** be in `conffiles` and must not be in the package's data. [35] Choose one style per file.

:::key-takeaways
- Four scripts, each idempotent, `set -e`, exit 0 on success; `case "$1"` on the action. [32]
- `postinst configure` gets the previously configured version, empty on first install. [32]
- A failed `postinst configure` leaves the package half-configured with no unwind; fix and `dpkg --configure -a`. [32] [36]
- Conffiles keep local edits on upgrade, stay after remove (`rc`), go on purge; scripts must never edit them. [35] [37]
- `--force-confold` / `--force-confnew` decide conffile prompts non-interactively. [36]
:::

:::glossary
- **Maintainer script**: `preinst`, `postinst`, `prerm` or `postrm`, run by dpkg at fixed points.
- **Conffile**: a file listed in `conffiles` whose local changes dpkg preserves.
- **Purge**: removing a package together with its configuration files.
- **Unwind**: dpkg calling scripts with `abort-*` arguments to undo a failed step.
- **debconf**: Debian's system for asking configuration questions during install.
- **`rc` state**: removed, configuration files remain.
:::
