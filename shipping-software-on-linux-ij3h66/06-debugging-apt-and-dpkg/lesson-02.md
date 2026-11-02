---
id: l23
title: "Broken states and how to get out of them"
quiz: quiz-02.yaml
resources: [../resources/lab4-apt-scenarios.sh]
sources: [31, 32, 36, 37, 40]
---
After this lesson you can read the three status letters in `dpkg -l`, name the state a failed install left behind, and choose between `dpkg --configure -a`, `apt-get -f install` and a fixed package version to recover.

## The three letters in `dpkg -l`

The first three columns of `dpkg -l` are the desired action, the package status and the error flags, in that order. [37]

| Column | Letters |
| --- | --- |
| Desired | `u` unknown, `i` install, `h` hold, `r` remove, `p` purge |
| Status | `n` not-installed, `c` config-files, `H` half-installed, `U` unpacked, `F` half-configured, `W` triggers-awaiting, `t` triggers-pending, `i` installed |
| Error | empty, or `R` reinst-required |

"An uppercase status or error letter indicates the package is likely to cause severe problems." [37] So `ii` is healthy, `rc` is "removed, config files left", and `iU`, `iF` and anything with `R` need action.

## How packages get stuck

dpkg's states explain what happened. [36]

- **unpacked** (`U`): the files are on disk but the package is not configured. A package's `Depends` only take effect at configure time, so dpkg unpacks and then refuses to configure while dependencies are missing. [31]
- **half-configured** (`F`): configuration started and did not finish. A failing `postinst configure` gets no unwind: the package stays half-configured and an error is shown. [32]
- **half-installed** (`H`): installation started and did not finish, for example when an unwind after a failed `preinst` also failed. [32] [36]

## Scenario: a dependency dpkg cannot fetch

`dpkg -i` installs a single file and never downloads anything. With a missing dependency (Lab 4, scenario 1):

```text
$ dpkg -i needs-jq_1.0-1_all.deb
dpkg: error processing package needs-jq (--install):
 dependency problems - leaving unconfigured
$ dpkg -l needs-jq | tail -n 1
iU  needs-jq       1.0-1        all          Lab 4 package needs-jq
```

**Fix:** `apt-get -f install` ("attempt to correct a system with broken dependencies in place") [40] fetches `jq` and its libraries, then configures `needs-jq`. Better still, never use `dpkg -i` for a package with dependencies: `apt-get install ./needs-jq_1.0-1_all.deb` resolves them in one step.

## Scenario: a failing postinst

```text
$ dpkg -i flaky-svc_1.0-1_all.deb
flaky-svc: /etc/lab4/ready missing
dpkg: error processing package flaky-svc (--install):
 installed flaky-svc package post-installation script subprocess returned error exit status 1
$ dpkg -l flaky-svc | tail -n 1
iF  flaky-svc      1.0-1        all          Lab 4 package flaky-svc
```

`dpkg --audit` runs consistency checks [36]; here it says the package is "only half configured". **Fix the cause, then retry configuration:** `dpkg --configure -a` configures every unpacked but unconfigured package. [36] Running the script again must be safe, which is why Policy requires maintainer scripts to be idempotent. [32] Reading the script helps: it lives in `/var/lib/dpkg/info/flaky-svc.postinst`. Editing that file to "make it pass" is a last resort. It hides the problem until the next upgrade runs the packaged script again.

## Scenario: two packages, one file

```text
dpkg: error processing archive tool-b_1.0-1_all.deb (--install):
 trying to overwrite '/usr/bin/lab4-tool', which is also in package tool-a 1.0-1
```

`dpkg -S /usr/bin/lab4-tool` names the owner. Policy says it is usually an error for a package to contain files that are on the system in another package. The fix is in the packaging. When a file moves from one package to another, the new owner declares `Replaces` so it may take the file over, plus `Breaks` with an earlier-than version so the old package gets upgraded first. [31]

```text
Package: tool-b
Version: 2.0-1
Breaks: tool-a (<< 1.1)
Replaces: tool-a (<< 1.1)
```

Lab 4 showed a subtlety. `dpkg -i tool-b_2.0-1` alone still failed with `tool-b breaks tool-a (<< 1.1)` and `deconfiguration is not permitted`. `Breaks` means the old tool-a must not stay unpacked. [31] The solution is to install the new tool-a (1.1-1, which no longer ships the file) and tool-b together through apt, so apt orders the upgrade:

```text
$ apt-get install ./tool-a_1.1-1_all.deb ./tool-b_2.0-1_all.deb
Unpacking tool-a (1.1-1) over (1.0-1) ...
Unpacking tool-b (2.0-1) ...
$ dpkg -S /usr/bin/lab4-tool
tool-b: /usr/bin/lab4-tool
```

`dpkg --force-overwrite` also "works". It overwrites one package's file with another's [36], leaving dpkg's records in conflict, so keep it for emergencies.

## The recovery order

1. `dpkg -l | grep -v '^ii'` and `dpkg --audit` to find what is not healthy. [36] [37]
2. Read the error or the failing maintainer script; fix the cause.
3. `dpkg --configure -a` for unpacked and half-configured packages. [36]
4. `apt-get -f install` for missing dependencies. [40]
5. If the package itself is wrong (a file conflict, a broken script), ship a fixed version. Force options are a last resort: `--force-depends` turns dependency problems into warnings. [36]

:::key-takeaways
- `dpkg -l` columns: desired, status, error; uppercase status letters or `R` mean trouble. [37]
- Depends are checked at configure time, so `dpkg -i` with missing dependencies leaves the package unpacked (`iU`). [31]
- A failing `postinst configure` leaves the package half-configured (`iF`); fix the cause, then `dpkg --configure -a`. [32] [36]
- File conflicts are fixed with `Breaks` + `Replaces` in a new version, installed through apt. [31]
- `apt-get -f install` repairs missing dependencies. [40]
:::

:::glossary
- **Unpacked**: files are on disk but the package has not been configured.
- **Half-configured**: configuration (the postinst) started but did not finish.
- **Half-installed**: installation started but did not finish.
- **Maintainer script**: a script inside a package (`preinst`, `postinst`, `prerm`, `postrm`) that dpkg runs at set points.
- **Idempotent**: safe to run more than once with the same result.
- **`dpkg --audit`**: a consistency check of dpkg's database.
- **Force option**: a `--force-*` flag that tells dpkg to ignore a safety check.
:::
