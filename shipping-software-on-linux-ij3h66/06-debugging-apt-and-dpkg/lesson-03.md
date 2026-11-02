---
id: l24
title: "Lab 4: five broken apt and dpkg scenarios"
quiz: quiz-03.yaml
resources: [../resources/lab4-apt-scenarios.sh]
sources: [31, 32, 36, 37, 39, 40, 41, 42, 50]
---
After this lab you will have broken a Debian system five different ways, found each cause with the chapter's tools rather than guesswork, and fixed each one the way you would on a production host.

This is a hands-on lab. `lab4-apt-scenarios.sh` was run end to end (`all` mode) in a fresh `debian:bookworm` container while writing this course. Outputs below are from that run. The script builds its own small packages with `dpkg-deb` inside the container, so no package files are downloaded or committed. It also sets up a local apt repository and needs internet once to install `apt-utils` and `jq`.

## Shortcut

```bash
docker run --rm -it -v "$PWD":/lab -w /lab debian:bookworm bash
bash lab4-apt-scenarios.sh setup
bash lab4-apt-scenarios.sh break 1      # now diagnose it yourself, then:
bash lab4-apt-scenarios.sh solve 1
bash lab4-apt-scenarios.sh reset
```

`all` runs every scenario's break, diagnosis and solution in one go. Try each scenario yourself before you look at `solve`.

The local repository is a flat repository (chapter 05) served with a `file:` URI and marked trusted, which is fine inside a throwaway container. [50] The line it adds:

```text
deb [trusted=yes] file:/srv/lab4-repo ./
```

## Scenario 1: "dependency problems - leaving unconfigured"

**Break:** `dpkg -i needs-jq_1.0-1_all.deb` on a system without `jq`.

**Evidence:** `dpkg -l` shows `iU` [37]; `apt-get check` names the gap:

```text
The following packages have unmet dependencies:
 needs-jq : Depends: jq but it is not installed
```

**Fix:** `apt-get -f install` [40] installed `libonig5`, `libjq1`, `jq`, then configured `needs-jq` (now `ii`). Depends are only enforced at configure time, which is why dpkg could unpack the package at all. [31]

## Scenario 2: failing postinst

**Break:** `flaky-svc`'s postinst exits 1 unless `/etc/lab4/ready` exists.

**Evidence:** `iF` in `dpkg -l`; `dpkg --audit` says the package is "only half configured". [36] [37]

**Fix:** create the missing file, then `dpkg --configure -a`:

```text
Setting up flaky-svc (1.0-1) ...
ii  flaky-svc      1.0-1        all          Lab 4 package flaky-svc
```

The retry is safe because the script is idempotent, as Policy requires. [32]

## Scenario 3: file conflict

**Break:** `tool-a` and `tool-b` both ship `/usr/bin/lab4-tool`.

```text
 trying to overwrite '/usr/bin/lab4-tool', which is also in package tool-a 1.0-1
```

**Evidence:** `dpkg -S /usr/bin/lab4-tool` → `tool-a`; `dpkg -l` shows `tool-b` as `in` with version `<none>`, a failed unpack.

**Fix:** a packaging fix, not a force flag. `tool-b 2.0-1` declares `Breaks: tool-a (<< 1.1)` and `Replaces: tool-a (<< 1.1)`; `tool-a 1.1-1` no longer ships the file. [31] Installing tool-b 2.0-1 alone with dpkg still fails (`tool-b breaks tool-a (<< 1.1)`, `deconfiguration is not permitted`). Installing both through apt works:

```text
Unpacking tool-a (1.1-1) over (1.0-1) ...
Unpacking tool-b (2.0-1) ...
tool-b: /usr/bin/lab4-tool
```

## Scenario 4: "you have held broken packages"

**Break:** `libdemo` 1.0-1 is installed and held; `demo-app` needs `libdemo (>= 1.0-2)`.

```text
 demo-app : Depends: libdemo (>= 1.0-2) but 1.0-1 is to be installed
E: Unable to correct problems, you have held broken packages.
```

**Evidence:** `apt-mark showhold` → `libdemo` [41]; `apt-cache policy libdemo` shows that the candidate 1.0-2 exists in the repository. [42]

**Fix:** `apt-mark unhold libdemo`, then the install sets up `libdemo (1.0-2)` and `demo-app (1.0-1)`. In real life, first find out **why** the hold exists. Holds are often placed on purpose during an incident.

## Scenario 5: the upgrade that silently does nothing

**Break:** a file in `/etc/apt/preferences.d/` pins `libdemo` to 1.0-1 at priority 1001. `apt-get install --only-upgrade libdemo` exits cleanly, and the package stays at 1.0-1.

**Evidence:**

```text
$ apt-cache policy libdemo
  Installed: 1.0-1
  Candidate: 1.0-1
     1.0-2 500
 *** 1.0-1 1001
```

The pin gives 1.0-1 a priority of 1000 or more, which wins even over newer versions. [39] `grep -r . /etc/apt/preferences.d/` finds the file.

**Fix:** remove or correct the pin; the candidate becomes 1.0-2 and the upgrade goes through.

## Check yourself

- In scenario 1, what does `apt-get install ./needs-jq_1.0-1_all.deb` (with `./`) do differently from `dpkg -i`?
- In scenario 5, change the pin priority to 400 and predict the candidate before you check it.

:::key-takeaways
- `iU` + "unmet dependencies" → `apt-get -f install`. [37] [40]
- `iF` → fix the cause, then `dpkg --configure -a`. [32] [36]
- File conflict → a new version with `Breaks` + `Replaces`, installed through apt. [31]
- "held broken packages" → `apt-mark showhold` and `apt-cache policy`. [41] [42]
- An upgrade that does nothing → look for pins in `apt-cache policy`. [39]
:::

:::glossary
- **Flat repository**: an apt repository that is just a directory with a `Packages` index, without the `dists/` tree.
- **`[trusted=yes]`**: a sources.list option that skips signature checks for that source; only for throwaway setups.
- **`apt-ftparchive`**: a tool from `apt-utils` that writes `Packages` and `Release` index files for a directory of `.deb` files.
- **Reset**: returning the lab container to a clean state between scenarios.
:::
