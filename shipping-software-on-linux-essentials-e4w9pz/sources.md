# Sources

Numbers are stable: lessons and questions cite them as `[n]`. Never renumber; append new sources at the end.
Only list sources that were actually read during research. Never invent a URL.

All pages were read on 2026-11-02 through a fetch tool that returns the page's extracted text. `read: full` means the whole page text was retrieved and read; `partly` names what was covered. Man pages are the Debian trixie (13) or man7.org versions unless a URL says otherwise; trixie pages were used where manpages.debian.org redirected from bookworm.

1. [PEP 668 – Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/) · Python Software Foundation · accessed 2026-11-02 · reliability: high · read: full
   - Notes: the EXTERNALLY-MANAGED marker in the stdlib directory, the `[externally-managed]` INI section and `Error` key, the installer rule (outside a venv and marker present means refuse), the `--break-system-packages` override "should not be enabled by default", venv detection via `sys.prefix == sys.base_prefix`, and the recommendation that distros separate local (`/usr/local`) and distro (`/usr`) paths. The PEP is marked historical; the living text is source 4.
2. [venv — Creation of virtual environments](https://docs.python.org/3/library/venv.html) · Python documentation · accessed 2026-11-02 · reliability: high · read: full
   - Notes: `pyvenv.cfg` and its `home` and `include-system-site-packages` keys, `sys.prefix` vs `sys.base_prefix`, activation only changes `PATH` and is optional, `VIRTUAL_ENV` cannot be relied on, the CLI options, and why environments are disposable and not portable (absolute shebangs).
3. [site — Site-specific configuration hook](https://docs.python.org/3/library/site.html) · Python documentation · accessed 2026-11-02 · reliability: high · read: full
   - Notes: how `site` builds `sys.path` from the prefixes, the venv rule for `include-system-site-packages`, `.pth` files, the user site directory and `ENABLE_USER_SITE`, `-S`, `-s`/`PYTHONNOUSERSITE`, and `python -m site` output and exit codes. The page does not mention Debian's `dist-packages` or the `home` key.
4. [Externally Managed Environments (specification)](https://packaging.python.org/en/latest/specifications/externally-managed-environments/) · Python Packaging Authority · accessed 2026-11-02 · reliability: high · read: full
   - Notes: the living version of PEP 668; the example Debian error text, the Debian path split (`/usr/local/lib/python3/dist-packages` vs `/usr/lib/python3/dist-packages`), the recommendation to suggest pipx. Approved June 2022.
5. [How pipx works](https://pipx.pypa.io/stable/explanation/how-pipx-works.html) · pipx project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
   - Notes: one venv per application under `PIPX_HOME` (`~/.local/share/pipx/venvs/`), console scripts linked into `~/.local/bin`, the shared pip under the pip backend, `pipx_metadata.json` used by upgrade and reinstall. The pipx landing page (pipx.pypa.io/stable/) was also read for the one-line description and the uv/pip backend note.
6. [Use a private index (pipx)](https://pipx.pypa.io/stable/how-to/use-private-index.html) · pipx project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
   - Notes: `--index-url`, `--pip-args`, `PIP_INDEX_URL`, offline installs with `--no-index --find-links`, options recorded for upgrade, the empty-URL refusal and its error message.
7. [Python versions (uv concepts)](https://docs.astral.sh/uv/concepts/python-versions/) · Astral · accessed 2026-11-02 · reliability: high · read: full
   - Notes: managed vs system Pythons, discovery order, `uv python install`, `.python-version` and `uv python pin`, python-build-standalone builds, `python-preference`. Does not say whether managed Pythons carry an EXTERNALLY-MANAGED marker.
8. [pyenv README](https://github.com/pyenv/pyenv/blob/master/README.md) · pyenv project · accessed 2026-11-02 · reliability: high · read: partly (How It Works and installation sections)
   - Notes: shims at the front of `PATH`, rehashing, version selection order, `~/.pyenv/versions`, builds from source and needs build dependencies.
9. [pip User Guide](https://pip.pypa.io/en/stable/user_guide/) · pip project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
   - Notes: `python -m pip`, `--user` rules, requirements and constraints files, `pip check` and the warning that pip may break already-installed packages.
10. [Secure installs (pip)](https://pip.pypa.io/en/stable/topics/secure-installs/) · pip project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: hash-checking mode, `--require-hashes`, pinning rules, `--hash=sha256:`, multiple hashes per requirement, `--only-binary :all:`, installing your own project with `--no-deps`; implicit hash mode from pip 26.2.
11. [pyproject.toml specification](https://packaging.python.org/en/latest/specifications/pyproject-toml/) · Python Packaging Authority · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `[build-system]` defaults, `[project]` required and dynamic fields, dependencies and extras, `[project.scripts]`, `dynamic` rules and errors, `license` as an SPDX expression and `license-files`, the `[tool]` table. The page has no full example file.
12. [PEP 517 – A build-system independent format for source trees](https://peps.python.org/pep-0517/) · Python Software Foundation · accessed 2026-11-02 · reliability: high · read: full
    - Notes: build frontend vs backend, the mandatory `build_wheel` and `build_sdist` hooks, optional hooks, build isolation recommendation, `backend-path`, legacy fallback.
13. [PEP 518 – Specifying minimum build system requirements](https://peps.python.org/pep-0518/) · Python Software Foundation · accessed 2026-11-02 · reliability: high · read: full
    - Notes: the setup.py chicken-and-egg problem, `[build-system] requires`, why TOML, the default when the table is missing (only `setuptools` is shown).
14. [PEP 440 – Version identification and dependency specification](https://peps.python.org/pep-0440/) · Python Software Foundation · accessed 2026-11-02 · reliability: high · read: full
    - Notes: the public version scheme, local versions, suffix ordering and the long ordered example, epochs, `~=`, prefix matching, `===`, pre-release exclusion, normalisation rules. Marked historical; the living spec is on packaging.python.org.
15. [Platform compatibility tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/) · Python Packaging Authority · accessed 2026-11-02 · reliability: high · read: full
    - Notes: the `{python tag}-{abi tag}-{platform tag}` format, `none`, `any`, `abi3`, how installers choose, compressed tag sets, `manylinux_x_y` and the legacy aliases with their glibc versions, musllinux.
16. [src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) · Python Packaging Authority · accessed 2026-11-02 · reliability: high · read: full
    - Notes: why src layout stops the in-development copy from shadowing the installed one (the current directory comes first on the import path).
17. [Development mode (editable installs)](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) · setuptools project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: PEP 660 editable installs (setuptools 64+), `.pth` or import-hook implementation, what needs a reinstall, strict and compat modes.
18. [Packaging Python Projects (tutorial)](https://packaging.python.org/en/latest/tutorials/packaging-projects/) · Python Packaging Authority · accessed 2026-11-02 · reliability: high · read: full
    - Notes: src layout tree, `[build-system]` tables for hatchling, setuptools, flit and pdm with their minimum versions, the `[project]` example, `python3 -m build` and its two output files, `twine upload --repository testpypi`.
19. [Entry points specification](https://packaging.python.org/en/latest/specifications/entry-points/) · Python Packaging Authority · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `console_scripts`, the `module:attr` object reference, wrapper scripts created by installers, `entry_points.txt` in `.dist-info`.
20. [Build configuration (Hatch)](https://hatch.pypa.io/latest/config/build/) · Hatch project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: hatchling `[build-system]`, the `packages` option for src layout, the wheel, sdist and custom targets, reproducible builds with `SOURCE_DATE_EPOCH`. The page does not describe automatic src-layout detection.
21. [Locking and syncing (uv)](https://docs.astral.sh/uv/concepts/projects/sync/) · Astral · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `uv lock`, `uv sync`, `--locked` (error if stale) vs `--frozen` (no check), `uv export --format requirements.txt`. The page does not discuss hashes in exports or libraries vs applications.
22. [Package indexes (uv)](https://docs.astral.sh/uv/concepts/indexes/) · Astral · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `[[tool.uv.index]]`, `explicit = true`, the default index has lowest priority, `index-strategy` (`first-index` default, `unsafe-best-match` closest to pip), dependency confusion, credentials from environment variables.
23. [pip install (CLI reference)](https://pip.pypa.io/en/stable/cli/pip_install/) · pip project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `--index-url`, `--extra-index-url` and the warning that using it for private packages is unsafe, "There is no priority in the locations that are searched", `--no-index`, `--find-links`, `--only-binary`, `--no-deps`, `--dry-run`, `--break-system-packages`.
24. [Configuration (pip)](https://pip.pypa.io/en/stable/topics/configuration/) · pip project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: global, user and site `pip.conf` locations and their order, `PIP_CONFIG_FILE`, `PIP_<UPPER_LONG_NAME>` variables, precedence of CLI over env over files, `pip config debug`.
25. [pypiserver on PyPI](https://pypi.org/project/pypiserver/) · pypiserver project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: version 2.4.2 (2026-09-20); `pypi-server run -p 8080 <dir>`, default port 8080, `-a`/`-P` authentication and `-a . -P .` to disable it, installing with `--extra-index-url http://localhost:8080/simple/`, `.pypirc` upload example.
26. [Twine documentation](https://twine.readthedocs.io/en/stable/) · twine project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `twine upload` with `-r` and `--repository-url`, `.pypirc`, `TWINE_USERNAME`/`TWINE_PASSWORD`/`TWINE_REPOSITORY_URL`, `twine check`, why twine (verified HTTPS).
27. [pip-tools documentation](https://pip-tools.pypa.io/en/stable/) · pip-tools project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `pip-compile` from `requirements.in` or `pyproject.toml`, `--generate-hashes`, `--upgrade`, `--upgrade-package`, `pip-sync` (install, upgrade and uninstall to match), layered `-c requirements.txt`.
28. [pipdeptree on PyPI](https://pypi.org/project/pipdeptree/) · pipdeptree project · accessed 2026-11-02 · reliability: high · read: partly (first half of the page: description, quick start, reverse lookup)
    - Notes: version 4.2.13 (2026-10-29); dependency tree vs `pip freeze`, the example tree with a ⚠ conflict marker, `pipdeptree --reverse --packages`.
29. [Dependency resolution (pip)](https://pip.pypa.io/en/stable/topics/dependency-resolution/) · pip project (PyPA) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: backtracking, the `package_coffee`/`package_tea`/`package_water` conflict example, the four strategies for conflicts, constraints for indirect dependencies, lockfiles for deployment.
30. [install_requires vs requirements files](https://packaging.python.org/en/latest/discussions/install-requires-vs-requirements/) · Python Packaging Authority · accessed 2026-11-02 · reliability: high · read: full
    - Notes: abstract minimal dependencies in project metadata vs concrete, pinned, index-bound requirements files. The page does not use the words library or application.
31. [Debian Policy Manual, chapter 7: Declaring relationships between packages](https://www.debian.org/doc/debian-policy/ch-relationships.html) · Debian Project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: relationship syntax, Depends, Pre-Depends, Recommends, Suggests, Enhances, Breaks, Conflicts, Provides (versioned only with `=`), Replaces for file takeover and whole-package replacement, and the foo/foo-data split example.
32. [Debian Policy Manual, chapter 6: Package maintainer scripts](https://www.debian.org/doc/debian-policy/ch-maintainerscripts.html) · Debian Project · accessed 2026-11-02 · reliability: high · read: partly (6.1 to 6.8; the Appendix 9 flowcharts were not read)
    - Notes: the four scripts, idempotency, `set -e`, exit status, call order for install, upgrade, remove and purge, error unwind (`abort-upgrade`, `abort-install`) and the states left behind (Half-Installed, Half-Configured, Config-Files).
33. [deb-version(7)](https://manpages.debian.org/bookworm/dpkg-dev/deb-version.7.en.html) · Debian dpkg · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `[epoch:]upstream-version[-debian-revision]`, allowed characters, split at the last hyphen, a missing revision sorts earlier, the comparison algorithm, tilde sorts before anything.
34. [Debian Policy Manual, chapter 5: Control files and their fields](https://www.debian.org/doc/debian-policy/ch-controlfields.html) · Debian Project · accessed 2026-11-02 · reliability: high · read: partly (5.3 binary control file and 5.6 field definitions used here)
    - Notes: mandatory binary control fields, Version and epochs ("must be used with care", not for rollbacks), the tilde ordering example, Architecture `all`/`any`, Section, Priority, Installed-Size, Description format.
35. [Debian Policy Manual, chapter 10: Files (10.7 configuration files)](https://www.debian.org/doc/debian-policy/ch-files.html) · Debian Project · accessed 2026-11-02 · reliability: high · read: partly (10.7)
    - Notes: conffiles vs configuration files, preserving local changes, removal vs purge, maintainer scripts must not alter conffiles, the two styles must not be mixed.
36. [dpkg(1)](https://manpages.debian.org/trixie/dpkg/dpkg.1.en.html) · Debian dpkg · accessed 2026-11-02 · reliability: high · read: full
    - Notes: package states and selection states, `--configure -a`, `--compare-versions` operators including the `-nl` forms, `--audit`, `-L`, `-S`, `-s`, `--force-depends`, `--force-overwrite`, `--force-confnew`/`confold`, `--unpack` vs `--install`.
37. [dpkg-query(1)](https://manpages.debian.org/trixie/dpkg/dpkg-query.1.en.html) · Debian dpkg · accessed 2026-11-02 · reliability: high · read: full
    - Notes: the three status columns of `dpkg -l` and every code, "An uppercase status or error letter indicates the package is likely to cause severe problems", `-W --showformat`, `-S`.
38. [deb(5)](https://manpages.ubuntu.com/manpages/noble/en/man5/deb.5.html) · dpkg manual page (Ubuntu noble copy) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: the `ar` container, member order (`debian-binary` 2.0, `control.tar`, `data.tar`), contents of the control archive, supported compressions and the dpkg versions that added them. The Debian copy of this page returned 404, so the Ubuntu copy of the same dpkg man page was read.
39. [apt_preferences(5)](https://manpages.debian.org/trixie/apt/apt_preferences.5.en.html) · Debian APT · accessed 2026-11-02 · reliability: high · read: full
    - Notes: default priorities (1, 100, 500, 990), what each priority range does, the example stanzas (version, release `a=`/`n=`/`o=`, origin).
40. [apt-get(8)](https://manpages.debian.org/trixie/apt/apt-get.8.en.html) · Debian APT · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `-s` simulation (Inst, Conf, Remv), `-f`, `pkg=version` and `pkg/release`, `--allow-downgrades`, upgrade vs dist-upgrade, `--no-install-recommends`.
41. [apt-mark(8)](https://manpages.debian.org/trixie/apt/apt-mark.8.en.html) · Debian APT · accessed 2026-11-02 · reliability: high · read: full
    - Notes: hold, unhold, showhold, auto, manual, showmanual.
42. [apt-cache(8)](https://manpages.debian.org/trixie/apt/apt-cache.8.en.html) · Debian APT · accessed 2026-11-02 · reliability: high · read: full
    - Notes: policy, depends, rdepends, showpkg, show. The page does not show the policy output format; it is shown in the labs from real runs.
43. [dpkg-deb(1)](https://manpages.debian.org/trixie/dpkg/dpkg-deb.1.en.html) · Debian dpkg · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `--build` with a `DEBIAN/` directory, the checks it runs, `--root-owner-group`, `--info`, `--contents`, `--field`, `-x`/`-R`, `-Z` (default xz).
44. [dh(1)](https://manpages.debian.org/trixie/debhelper/dh.1.en.html) · Debian debhelper · accessed 2026-11-02 · reliability: high · read: full
    - Notes: dh runs a sequence of debhelper commands, the minimal `debian/rules`, `override_dh_*` targets, `--with` addons, `--no-act`.
45. [pybuild(1)](https://manpages.debian.org/trixie/dh-python/pybuild.1.en.html) · Debian dh-python · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `dh $@ --with python3 --buildsystem=pybuild`, the pyproject plugin (PEP 517), `PYBUILD_NAME`, install into `dist-packages`, `debian/python3-foo` destination.
46. [dh-virtualenv documentation (overview and tutorial)](https://dh-virtualenv.readthedocs.io/en/latest/) · dh-virtualenv project · accessed 2026-11-02 · reliability: medium · read: partly (overview, changelog headings, tutorial page)
    - Notes: combines Debian packaging with a pre-built virtualenv, adds `dh_virtualenv` to the sequence, `dh $@ --with python-virtualenv`. Medium because the tutorial still shows Python 2 era control fields.
47. [dh-virtualenv usage](https://dh-virtualenv.readthedocs.io/en/latest/usage.html) · dh-virtualenv project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: default install path `/opt/venvs/<package>`, `--python`, `--builtin-venv`, requirements handling. The page does not state that the build and target Python must match.
48. [nFPM](https://nfpm.goreleaser.com/) · GoReleaser project · accessed 2026-11-02 · reliability: high · read: partly (home page)
    - Notes: deb, rpm, apk and other formats from a single Go binary with no Ruby or tar dependency. The page does not compare itself to fpm.
49. [Debian repository format](https://wiki.debian.org/DebianRepository/Format) · Debian wiki · accessed 2026-11-02 · reliability: medium · read: full
    - Notes: `dists/<suite>/InRelease` (inline-signed), `Release` plus `Release.gpg`, required Release fields, `binary-<arch>/Packages` paths, the pool, flat repositories. Medium: a wiki page marked work in progress.
50. [sources.list(5)](https://manpages.debian.org/trixie/apt/sources.list.5.en.html) · Debian APT · accessed 2026-11-02 · reliability: high · read: full
    - Notes: one-line and deb822 formats, `Signed-By`, `Trusted`, the `file:` and `copy:` schemes, flat repository paths ending in `/`, the deb822 example stanza.
51. [reprepro(1)](https://manpages.debian.org/trixie/reprepro/reprepro.1.en.html) · Debian reprepro · accessed 2026-11-02 · reliability: high · read: partly (first 100,000 of 110,000 characters: concepts, conf/distributions, commands)
    - Notes: `conf/distributions` fields (Codename, Suite, Architectures, Components, Origin, Label, SignWith), `includedeb`, `list`, `remove`, `export`, signing output.
52. [aptly overview](https://www.aptly.info/doc/overview/) · aptly project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: mirrors, local repos, snapshots as immutable package lists, published repositories.
53. [aptly publish repo](https://www.aptly.info/doc/aptly/publish/repo/) · aptly project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `aptly publish repo <name>`, `-distribution`, `-component`, `-skip-signing`, `-gpg-key`, the served `public/` directory.
54. [The USE Method](https://www.brendangregg.com/usemethod.html) · Brendan Gregg · accessed 2026-11-02 · reliability: high · read: partly (text; the flowchart is an image)
    - Notes: "For every resource, check utilization, saturation, and errors" and the definitions of each term.
55. [USE Method: Linux Performance Checklist](https://www.brendangregg.com/USEmethod/use-linux.html) · Brendan Gregg · accessed 2026-11-02 · reliability: high · read: full
    - Notes: per-resource commands: `vmstat` r vs CPU count, si/so, `dmesg` for the OOM killer, `iostat -xz` %util and queue size, file descriptor counts vs `ulimit -n`, EMFILE via strace.
56. [Linux Load Averages: Solving the Mystery](https://www.brendangregg.com/blog/2017-08-08/linux-load-averages.html) · Brendan Gregg · accessed 2026-11-02 · reliability: high · read: full
    - Notes: Linux load averages count uninterruptible tasks, the 1993 patch, damped moving sums, what to use instead (run queue latency, `vmstat 1` r, `pidstat 1`).
57. [Control Group v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) · Linux kernel documentation · accessed 2026-11-02 · reliability: high · read: partly (basics and the memory controller interface files)
    - Notes: mounting cgroup2, `cgroup.controllers`, `memory.current`, `memory.max` (OOM killer invoked in the cgroup), `memory.high`, `memory.events` fields, `memory.stat` anon/file, `memory.oom.group`, `memory.peak`.
58. [proc_pid_stat(5)](https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: partly (state field)
    - Notes: the process state letters, including D "Waiting in uninterruptible disk sleep".
59. [proc_pid_status(5)](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: State, VmPeak, VmSize, VmRSS (with the inaccuracy note), RssAnon, RssFile, VmSwap, Threads, context switches, FDSize.
60. [proc_pid_limits(5)](https://man7.org/linux/man-pages/man5/proc_pid_limits.5.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: soft limit, hard limit and units for each resource limit. No sample output on the page.
61. [strace(1)](https://man7.org/linux/man-pages/man1/strace.1.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `-f`, `-p`, `-e trace=` with `%file` and `%network`, `-c`, `-T`, `-tt`, `-r`, `-y`, `-o`, `-s` (default 32).
62. [ss(8)](https://man7.org/linux/man-pages/man8/ss.8.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `-t -u -a -n -p -l -s -e -i`, state filters, example commands.
63. [open(2)](https://man7.org/linux/man-pages/man2/open.2.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: partly (ERRORS)
    - Notes: EMFILE (per-process limit, RLIMIT_NOFILE), ENFILE (system-wide), ENOSPC.
64. [unlink(2)](https://man7.org/linux/man-pages/man2/unlink.2.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: an unlinked file stays in existence until the last file descriptor referring to it is closed.
65. [py-spy README](https://github.com/benfred/py-spy/blob/master/README.md) · py-spy project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `record`, `top`, `dump --pid`, `--locals`, `--native`, `SYS_PTRACE` in Docker and Kubernetes, no restart or code change needed.
66. [lsof(8)](https://man7.org/linux/man-pages/man8/lsof.8.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: partly (first 100,000 of 162,000 characters, which include the options)
    - Notes: `+L1` selects open files that have been unlinked; `-p`; `-i`.
67. [vmstat(8)](https://man7.org/linux/man-pages/man8/vmstat.8.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: field meanings: r, b, swpd, free, buff, cache, si, so, bi, bo, in, cs, us, sy, id, wa, st.
68. [iostat(1)](https://man7.org/linux/man-pages/man1/iostat.1.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: extended fields r/s, w/s, rkB/s, r_await, w_await, aqu-sz (formerly avgqu-sz), %util and its caveat for devices that serve requests in parallel.
69. [proc_pid_oom_score_adj(5)](https://man7.org/linux/man-pages/man5/proc_pid_oom_score_adj.5.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: range -1000 to +1000, -1000 disables OOM killing for the task, the badness heuristic.
70. [perf-top(1)](https://man7.org/linux/man-pages/man1/perf-top.1.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: real-time profile, `-p`, `-g`. The page does not discuss `perf_event_paranoid` or permissions.
71. [pidstat(1)](https://man7.org/linux/man-pages/man1/pidstat.1.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: `-u` (%usr, %system, %wait, %CPU), `-r` (faults, VSZ, RSS), `-d` (kB_rd/s, kB_wr/s, iodelay), `-w` (context switches), `-p`, `-t`.
72. [Services, Load Balancing, and Networking](https://kubernetes.io/docs/concepts/services-networking/) · Kubernetes documentation · accessed 2026-11-02 · reliability: high · read: full
    - Notes: the Kubernetes network model and which external components implement which part (CRI, CNI plugins, kube-proxy, NetworkPolicy).
73. [Virtual IPs and Service Proxies](https://kubernetes.io/docs/reference/networking/virtual-ips/) · Kubernetes documentation · accessed 2026-11-02 · reliability: high · read: full (in two parts)
    - Notes: kube-proxy modes; iptables is the default in 1.37 with nftables to become the default later; iptables DNAT to a random backend; ipvs deprecated since 1.35, off by default from 1.40, removed in 1.43; nftables needs kernel 5.13; the conntrack bug before kernel 6.1 and `--conntrack-tcp-be-liberal`.
74. [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/) · Kubernetes documentation · accessed 2026-11-02 · reliability: high · read: full (in two parts)
    - Notes: the pod `resolv.conf` with `ndots:5`, search expansion, `dnsPolicy` values, the `dnsConfig` example with `ndots: "2"`.
75. [resolv.conf(5)](https://man7.org/linux/man-pages/man5/resolv.conf.5.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: partly (search and options)
    - Notes: `ndots:n` threshold, default 1; the search list; the last `search` line wins.
76. [Basic Network Options (K3s)](https://docs.k3s.io/networking/basic-network-options) · K3s project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: flannel's default backend is vxlan; the other backends; `--flannel-iface`; example cluster and service CIDRs. The page does not say which kube-proxy mode K3s uses.
77. [Air-Gap Install (RKE2)](https://docs.rke2.io/install/airgap) · RKE2 project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: the four image-loading methods, `rke2-images.linux-amd64.tar.zst`, `/var/lib/rancher/rke2/agent/images/`, `INSTALL_RKE2_ARTIFACT_PATH`. The registries.yaml guide it links to was not read.
78. [Debugging Kubernetes nodes with crictl](https://kubernetes.io/docs/tasks/debug/debug-cluster/crictl/) · Kubernetes documentation · accessed 2026-11-02 · reliability: high · read: partly (all but the last 1,500 characters)
    - Notes: what crictl is, `/etc/crictl.yaml` endpoints, `crictl pods`, `images`, `ps -a`, `exec`, `logs`.
79. [Node-pressure Eviction](https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/) · Kubernetes documentation · accessed 2026-11-02 · reliability: high · read: full (in two parts)
    - Notes: eviction signals, the mapping to MemoryPressure, DiskPressure and PIDPressure, default hard thresholds, `oom_score_adj` per QoS class.
80. [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/) · Kubernetes documentation · accessed 2026-11-02 · reliability: high · read: full (in two parts)
    - Notes: nslookup checks, the `resolv.conf` check and why `ndots:5`, EndpointSlices, the kube-proxy check, the `iptables-save` example with KUBE-SERVICES, KUBE-SVC and KUBE-SEP chains, `ipvsadm -ln`, bypassing the Service.
81. [CNI Specification](https://github.com/containernetworking/cni/blob/main/SPEC.md) · Container Network Interface project (CNCF) · accessed 2026-11-02 · reliability: high · read: partly (overview, operations, environment, configuration format)
    - Notes: spec version 1.1.0, the ADD, DEL, CHECK, VERSION, GC and STATUS operations, `CNI_*` variables, chained plugin lists.
82. [Flannel backends](https://github.com/flannel-io/flannel/blob/master/Documentation/backends.md) · flannel project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: VXLAN VNI 1 and port 8472 on Linux, `DirectRouting`, the MTU option (defaults to the external interface's MTU), host-gw needs layer 2 connectivity, WireGuard.
83. [nsenter(1)](https://man7.org/linux/man-pages/man1/nsenter.1.html) · Linux man-pages (man7.org) · accessed 2026-11-02 · reliability: high · read: full
    - Notes: run a program in another process's namespaces: `-t`, `-n`, `-m`, `-p`.
84. [Version Skew Policy](https://kubernetes.io/releases/version-skew-policy/) · Kubernetes · accessed 2026-11-02 · reliability: high · read: full
    - Notes: supported minors (1.37, 1.36, 1.35), skew rules for kube-apiserver, kubelet, kube-proxy and kubectl, the upgrade order, no skipping minors, drain before a kubelet minor upgrade.
85. [k3d](https://k3d.io/stable/) · k3d project · accessed 2026-11-02 · reliability: high · read: full
    - Notes: k3d runs K3s in Docker; `k3d cluster create`; needs Docker 20.10.5 or later for v5.
86. [pypiserver README](https://github.com/pypiserver/pypiserver/blob/main/README.md) · pypiserver project · accessed 2026-11-02 · reliability: high · read: partly (run command help, client-side configuration tip)
    - Notes: `--disable-fallback` turns off "the default redirect to PyPI for packages not found in the local index"; `--fallback-url`; the tip that pypiserver redirects clients to pypi.org when it lacks a package. Confirmed in Lab 2 with `pypi-server run --help` from pypiserver 2.4.2.
