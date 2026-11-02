---
id: l22
title: "Asking apt why: policy, dependencies, simulation and holds"
quiz: quiz-01.yaml
resources: [../resources/lab4-apt-scenarios.sh]
sources: [39, 40, 41, 42]
---
After this lesson you can find out which version apt will install and why, see what an install would do before running it, read "held broken packages" correctly, and use holds and pins on purpose rather than by accident.

## Two layers

`dpkg` installs, configures and removes single `.deb` files and keeps the package database. `apt` sits on top. It knows the repositories, picks versions, resolves dependencies and then calls dpkg. Most "apt is broken" problems are apt making a choice you did not expect. Chapter 04 covers what is inside a `.deb`. This lesson is about asking apt to explain itself.

## `apt-cache policy`: which version, from where, at what priority

`apt-cache policy` exists to debug preference problems. With no arguments it prints the priority of each source. [42] Given a package, it shows the installed version, the **candidate** (what `install` or `upgrade` would choose) and a version table. This one comes from Lab 4's local repository:

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

`***` marks the installed version. Each version gets a priority from the sources it is found in. Without pins, versions that are not from the target release get 500, and the installed version gets 100 from `/var/lib/dpkg/status`. [39] apt picks the version with the highest priority. Here both versions sit at 500, and apt chose the higher version, 1.0-2, as candidate.

## Pins change the candidate

A file in `/etc/apt/preferences.d/` can raise or lower priorities. The ranges matter: [39]

| Priority | Effect |
| --- | --- |
| P ≥ 1000 | installed even if it means a downgrade |
| 990 ≤ P < 1000 | installed even if not from the target release |
| 500 ≤ P < 990 | installed unless the target release has a version |
| 100 ≤ P < 500 | installed unless another distribution has a version |
| 0 < P < 100 | installed only if no version is installed |
| P < 0 | never installed |

Lab 4's scenario 5 pins `libdemo` to 1.0-1 at 1001. The newer 1.0-2 then never installs, and nothing prints an error:

```text
 *** 1.0-1 1001
        500 file:/srv/lab4-repo ./ Packages
```

A pin silently overrides "upgrade". When an upgrade "does nothing", run `apt-cache policy <pkg>` before anything else. The pin stanzas follow the forms in the manual: `Package:`, `Pin: version 5.32*` or `Pin: release a=stable` / `n=<codename>` / `o=<origin>`, and `Pin-Priority:`. [39]

## Dependencies both ways

`apt-cache depends` lists what a package needs; `apt-cache rdepends` lists what needs it. [42] Before removing or holding something, `rdepends` tells you who you are about to break. `apt-cache show` prints the full package record, and `showpkg` prints more detail about versions and dependencies. [42]

## Simulate before you act

`apt-get -s` performs "a simulation of events that would occur based on the current system state" and changes nothing. Its output lines are `Inst` (unpack), `Conf` (configure) and `Remv` (remove). [40] Run it before any risky install on a production host, especially one that might remove packages. `dist-upgrade` may remove packages, while plain `upgrade` leaves packages whose upgrade needs new installs or removals at their current version. [40]

Other flags you will use: `pkg=version` selects an exact version and `pkg/release` selects a distribution. `--no-install-recommends` stops Recommends from being installed. `--allow-downgrades` is described in the manual as "a dangerous option". [40]

## Holds

`apt-mark hold pkg` prevents the package from being automatically installed, upgraded or removed. `unhold` removes the hold, and `showhold` lists held packages. [41] `apt-mark auto` and `manual` change whether a package counts as automatically installed, which decides what `autoremove` may remove. [41]

A hold is the classic cause of this message, from Lab 4 scenario 4:

```text
The following packages have unmet dependencies:
 demo-app : Depends: libdemo (>= 1.0-2) but 1.0-1 is to be installed
E: Unable to correct problems, you have held broken packages.
```

Read it literally. `demo-app` needs `libdemo >= 1.0-2`, and apt has decided 1.0-1 "is to be installed", here because of the hold. Despite the wording, "held broken packages" does not always mean an `apt-mark hold`. The real reason can be a pin or a missing version in your sources. Check, in order: `apt-mark showhold`, `apt-cache policy libdemo`, then whether the needed version exists in any configured repository.

:::key-takeaways
- `apt-cache policy pkg` shows installed version, candidate and priority per source; the highest priority wins. [39] [42]
- Default priorities: 500 for normal sources, 100 for the installed version; P ≥ 1000 even downgrades. [39]
- `apt-get -s` simulates; `Inst`/`Conf`/`Remv` lines show what would happen. [40]
- `apt-mark hold` blocks automatic install, upgrade or removal; `showhold` lists holds. [41]
- "you have held broken packages" means apt chose a version that cannot satisfy a dependency; check holds, pins and sources. [40] [41]
:::

:::glossary
- **dpkg**: the low-level tool that installs, configures and removes individual `.deb` files.
- **apt**: the high-level tool that fetches packages from repositories, resolves dependencies and calls dpkg.
- **Candidate**: the version apt would install if asked now.
- **Priority (pin priority)**: the number apt uses to choose between versions of a package.
- **Pin**: a rule in `/etc/apt/preferences.d/` that changes a version's priority.
- **Hold**: a mark that stops apt from automatically changing a package.
- **Recommends**: a strong but optional dependency that apt installs by default.
- **Target release**: the release you told apt to prefer, with `-t` or a configuration setting.
:::
