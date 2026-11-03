---
id: l11
title: "Debugging apt and dpkg: a field guide"
quiz: quiz-01.yaml
resources: [../resources/lab4-apt-scenarios.sh]
sources: [31, 32, 36, 37, 39, 40, 41, 42]
---
After this lesson you can ask apt which version it will install and why, simulate an install, read the status letters in `dpkg -l`, and repair a broken system without a force flag.

`dpkg` installs, configures and removes single `.deb` files and keeps the package database; `apt` picks versions, resolves dependencies and calls dpkg. Most "apt is broken" problems are apt making a choice you did not expect.

## Which version and why: `apt-cache policy`

`apt-cache policy` exists to debug preference problems. [42] Given a package, it shows the installed version, the **candidate** (what `install` or `upgrade` would choose) and a version table. From the local repository in the course's test run:

```text
$ apt-cache policy libdemo
libdemo:
  Installed: 1.0-1
  Candidate: 1.0-2
  Version table:
     1.0-2 500
        500 file:/srv/lab4-repo ./ Packages
 *** 1.0-1 500
        500 file:/srv/lab4-repo ./ Packages
        100 /var/lib/dpkg/status
```

`***` marks the installed version. Without pins, versions that are not from the target release get 500, and the installed version gets 100 from `/var/lib/dpkg/status`. apt picks the version with the highest priority. [39] Here both versions sit at 500, so apt chose the higher version, 1.0-2.

A file in `/etc/apt/preferences.d/` (a **pin**) can raise or lower priorities, using `Package:`, `Pin:` (a version, or a release such as `a=stable`) and `Pin-Priority:`. [39] The ranges:

| Priority | Effect |
| --- | --- |
| P ≥ 1000 | installed even if it means a downgrade |
| 990 ≤ P < 1000 | installed even if not from the target release |
| 500 ≤ P < 990 | installed unless the target release has a version |
| 100 ≤ P < 500 | installed unless another distribution has a version |
| 0 < P < 100 | installed only if no version is installed |
| P < 0 | never installed |

## Depends, simulate, hold

Use these before you change anything. [40] [41] [42]

| Command | What it tells you or does |
| --- | --- |
| `apt-cache depends pkg` / `rdepends pkg` | what pkg needs / what needs pkg; run `rdepends` before removing or holding |
| `apt-get -s install pkg` | simulates and changes nothing; lines are `Inst` (unpack), `Conf` (configure), `Remv` (remove) |
| `apt-mark hold pkg` | stops automatic install, upgrade or removal; `unhold` undoes it, `showhold` lists holds |

## Reading `dpkg -l`

The first three columns are the desired action, the package status and the error flags. [37]

| Column | Letters |
| --- | --- |
| Desired | `u` unknown, `i` install, `h` hold, `r` remove, `p` purge |
| Status | `n` not-installed, `c` config-files, `H` half-installed, `U` unpacked, `F` half-configured, `W` triggers-awaiting, `t` triggers-pending, `i` installed |
| Error | empty, or `R` reinst-required |

An uppercase status or error letter means the package is likely to cause severe problems. [37] So `ii` is healthy, `rc` is "removed, config files left", and `iU`, `iF` or anything with `R` needs action. [31] [32]

- **unpacked** (`U`): `Depends` only take effect at configure time, so dpkg unpacks and then refuses to configure while dependencies are missing.
- **half-configured** (`F`): a failing `postinst configure` gets no unwind; the package stays half-configured.

## Five failures from the course's test run

Real outputs from a `debian:bookworm` run. [31] [32] [36] [37] [39] [40] [41] [42]

| # | Symptom | Command that explains it | Fix |
| --- | --- | --- | --- |
| 1 | "dependency problems - leaving unconfigured", `iU` | `apt-get check` → `needs-jq : Depends: jq but it is not installed` | `apt-get -f install` fetches `jq`, then configures needs-jq (now `ii`) |
| 2 | flaky-svc: "post-installation script subprocess returned error exit status 1", `iF` | `dpkg --audit` → "only half configured"; read `/var/lib/dpkg/info/flaky-svc.postinst` | create the missing `/etc/lab4/ready`, then `dpkg --configure -a` |
| 3 | `trying to overwrite '/usr/bin/lab4-tool', which is also in package tool-a 1.0-1` | `dpkg -S /usr/bin/lab4-tool` → `tool-a` | tool-b 2.0-1 with `Breaks` + `Replaces`, tool-a 1.1-1 without the file, both through apt |
| 4 | `you have held broken packages` | `apt-mark showhold` → `libdemo`, then `apt-cache policy libdemo` | find out why it was held, then `apt-mark unhold libdemo` |
| 5 | `apt-get install --only-upgrade libdemo` exits cleanly, version stays 1.0-1 | `apt-cache policy libdemo` → `*** 1.0-1 1001` | remove or correct the pin in `/etc/apt/preferences.d/` |

Scenario 2 retries safely because Policy requires maintainer scripts to be idempotent: error recovery runs them again. [32] In scenario 4 the full line was `demo-app : Depends: libdemo (>= 1.0-2) but 1.0-1 is to be installed`: apt decided on 1.0-1, here because of the hold. [41] Scenario 5's evidence (output shortened to the key lines):

```text
$ apt-cache policy libdemo
  Installed: 1.0-1
  Candidate: 1.0-1
     1.0-2 500
 *** 1.0-1 1001
```

In scenario 3, the new owner declares `Replaces` so it may take the file over, plus `Breaks` with an earlier-than version (`tool-a (<< 1.1)`) so the old package gets upgraded first. [31] Yet `dpkg -i tool-b_2.0-1` alone still failed with "deconfiguration is not permitted": `Breaks` means the old tool-a must not stay unpacked. [31] Installing both through apt let apt order the upgrade:

```text
$ apt-get install ./tool-a_1.1-1_all.deb ./tool-b_2.0-1_all.deb
Unpacking tool-a (1.1-1) over (1.0-1) ...
Unpacking tool-b (2.0-1) ...
$ dpkg -S /usr/bin/lab4-tool
tool-b: /usr/bin/lab4-tool
```

## The recovery order

1. `dpkg -l | grep -v '^ii'` and `dpkg --audit` to find what is not healthy. [36] [37]
2. Read the error or the failing maintainer script; fix the cause.
3. `dpkg --configure -a` for unpacked and half-configured packages. [36]
4. `apt-get -f install` ("attempt to correct a system with broken dependencies in place") for missing dependencies. [40]
5. If the package itself is wrong (a file conflict, a broken script), ship a fixed version. Force options are a last resort: `--force-depends` turns dependency problems into warnings. [36]

## Optional: try the scenario script

To reproduce the five failures yourself, the scenario script `lab4-apt-scenarios.sh` builds its own packages and a local repository; it needs internet once. Run it from the resources folder:

```bash
docker run --rm -it -v "$PWD":/lab -w /lab debian:bookworm bash
```

Windows PowerShell: use `docker run --rm -it -v "${PWD}:/lab" -w /lab debian:bookworm bash`, because `"$PWD":/lab` splits into two arguments there and Docker fails with "invalid reference format".

```bash
bash lab4-apt-scenarios.sh setup
bash lab4-apt-scenarios.sh break 1      # now diagnose it yourself, then:
bash lab4-apt-scenarios.sh solve 1
bash lab4-apt-scenarios.sh reset
```

## Gotchas

- **"Held broken packages" without a hold.** Despite the wording, the cause can be a pin or a needed version missing from your sources. Check in order: `apt-mark showhold`, `apt-cache policy pkg`, then whether the version exists in any configured repository. [41] [42]
- **The silent upgrade.** A pin at 1000 or more wins even over newer versions, and nothing prints an error. When an upgrade "does nothing", run `apt-cache policy pkg` first, then `grep -r . /etc/apt/preferences.d/` to find the file. [39]
- **`dpkg -i` never downloads.** With a missing dependency it leaves the package `iU`. Use `apt-get install ./pkg.deb` (with `./`), which resolves dependencies in one step, or repair with `apt-get -f install`. [31] [40]
- **Editing the postinst to "make it pass".** Changing `/var/lib/dpkg/info/app.postinst` to succeed hides the fault until the next upgrade runs the packaged script again. Fix the cause, then `dpkg --configure -a`. [32] [36]
- **`--force-overwrite` "works".** On a file conflict it overwrites one package's file with another's and leaves dpkg's records in conflict. Ship `Breaks` + `Replaces` instead, installed through apt. [31] [36]
- **`dist-upgrade` removes things.** It may remove packages; plain `upgrade` leaves packages whose upgrade needs installs or removals at their current version. Run `apt-get -s` and read the `Remv` lines first. [40]

## Check yourself

- In scenario 5, if the pin priority were 400, which version would be the candidate?

:::key-takeaways
- `apt-cache policy pkg` shows installed version, candidate and priority per source; the highest priority wins, and P ≥ 1000 even downgrades. [39] [42]
- `apt-get -s` simulates; `Inst`/`Conf`/`Remv` lines show what would happen. [40]
- `iU` → `apt-get -f install`; `iF` → fix the cause, then `dpkg --configure -a`. [36] [37] [40]
- "held broken packages" means apt chose a version that cannot satisfy a dependency; check holds, pins and sources. [41] [42]
- File conflicts are fixed with `Breaks` + `Replaces` in a new version, installed through apt. [31]
:::

:::glossary
- **Candidate**: the version apt would install if asked now.
- **Pin**: a rule in `/etc/apt/preferences.d/` that changes a version's priority.
- **Hold**: a mark that stops apt from automatically changing a package.
- **Unpacked**: files are on disk but the package has not been configured.
- **Half-configured**: configuration (the postinst) started but did not finish.
- **Maintainer script**: a script inside a package (`preinst`, `postinst`, `prerm`, `postrm`) that dpkg runs at set points.
- **Idempotent**: safe to run more than once with the same result.
:::
