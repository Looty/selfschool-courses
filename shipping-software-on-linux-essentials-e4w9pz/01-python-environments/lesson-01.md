---
id: l01
title: "How Python finds packages, venvs and PEP 668"
quiz: quiz-01.yaml
resources: []
sources: [1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 23]
---
After this lesson you can explain how one `import` turns into a file on disk, read `python -m site`, say what `python -m venv` creates and how Python knows it is inside one, explain why Debian's pip refuses `sudo pip install`, and choose between pyenv, uv and pipx.

## Imports walk `sys.path`

`import requests` walks a list of directories, `sys.path`, in order, and takes the first match. Most "works on my machine" bugs are either the wrong interpreter or an unexpected directory on that list.

At start-up the interpreter imports the `site` module, unless you pass `-S`. `site` adds site-packages directories built from `sys.prefix` and `sys.exec_prefix`, and reads any configuration files there [3]. The order on a typical Linux box:

| Order | Entry | Note |
| --- | --- | --- |
| 1 | Script's directory (current directory for `python -c` and the REPL) | A folder with the same name as an installed package wins over the installed copy [16] |
| 2 | Standard library | |
| 3 | User site, `~/.local/lib/pythonX.Y/site-packages` | Only if enabled [3] |
| 4 | site-packages under the prefixes | Built by `site` [3] |

**`.pth` files.** Any `name.pth` file in a site directory adds one path per line to `sys.path`; a line starting with `import` is executed (deprecated as of Python 3.15) [3]. Editable installs use them.

**The user site** is switched off with `-s` or `PYTHONNOUSERSITE` [3]. Inside a venv that does not include system site-packages, it is left out too [3].

**Debian's split.** apt installs Python modules into `/usr/lib/python3/dist-packages`; local installs go to `/usr/local/lib/python3/dist-packages` [4]. PEP 668 asks that the local directory come first [1].

## Look, don't guess

`python -m site` prints `sys.path`, the user base and site, and whether the user site is enabled [3]. On the `debian:bookworm` container from Lab 1:

```text
$ python3 -m site
sys.path = [
    '/',
    '/usr/lib/python311.zip',
    '/usr/lib/python3.11',
    '/usr/lib/python3.11/lib-dynload',
    '/usr/local/lib/python3.11/dist-packages',
    '/usr/lib/python3/dist-packages',
]
```

The local `dist-packages` comes first, as PEP 668 recommends [1]. When an import fails, ask the interpreter before reaching for `pip install`:

```bash
python3 -c 'import sys; print(sys.executable); print(*sys.path, sep="\n")'
python3 -c 'import requests; print(requests.__file__)'
```

The first line tells you which binary ran and where it looks. The second tells you which copy of a package won.

## Virtual environments

One installation has one site-packages, so two applications needing different versions of a library cannot share it. On Debian the system interpreter also belongs to apt [4], and pip writing there can replace a module a system tool depends on. A virtual environment ("venv") reuses an existing interpreter but has its own site-packages; you can delete and recreate it without touching the system [2].

`python -m venv DIR` writes a `pyvenv.cfg` with a `home` key pointing at the base installation and an `include-system-site-packages` key, which is `true` only with `--system-site-packages` [2]. From Lab 1:

```text
home = /usr/bin
include-system-site-packages = false
version = 3.11.2
executable = /usr/bin/python3.11
command = /usr/bin/python3 -m venv /opt/app/.venv
```

**How Python knows.** Started from a venv, `sys.prefix` points at the venv and `sys.base_prefix` at the base installation; `sys.prefix != sys.base_prefix` is enough to tell you are in one [2]. `site` reads `pyvenv.cfg`; if `include-system-site-packages` is not `true`, neither the system site-packages nor the user site are searched [3]. That is the whole isolation mechanism.

```bash
/opt/app/.venv/bin/python -c 'import sys; print(sys.prefix, sys.base_prefix)'
# /opt/app/.venv /usr
```

Two rules follow:

- **Activation is optional.** `source .venv/bin/activate` only puts the venv's `bin` first on `PATH` and sets `VIRTUAL_ENV`. Calling `.venv/bin/python` by full path works the same, scripts in the venv run without activation, and `VIRTUAL_ENV` cannot be relied on to detect a venv [2]. In services, cron jobs and systemd units, use the full path.
- **Venvs are disposable, not portable.** Installed scripts get a shebang with the absolute path of the venv's interpreter, so a venv cannot be moved or copied. Delete it and recreate it from a requirements file [2].

## PEP 668: "externally-managed-environment"

A distribution marks its interpreter with an `EXTERNALLY-MANAGED` file in the standard-library directory: INI, an `[externally-managed]` section, and an `Error` key holding the message [1]. An installer that finds the marker and is not running in a venv must refuse and show that message [1]. On bookworm:

```text
$ pip install requests
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
```

The message goes on to advise a venv or pipx [4]. Inside a venv the marker does not apply [1].

PEP 668 suggests an override named `--break-system-packages` that should not be enabled by default [1]; pip describes it as "Allow pip to modify an EXTERNALLY-MANAGED Python installation" [23]. `pip install --user` is no way out: pip refuses it inside a venv that hides site-packages [9], and outside a venv it is still what the marker forbids [1].

The right choices: an apt package (`python3-xyz`) for something the system needs, a venv for an application, pipx for a command-line tool [4].

## Other Python versions and CLI tools

A venv reuses whatever interpreter created it, so it cannot give you a Python version Debian does not ship. pyenv and uv do that; pipx installs command-line tools.

| | pyenv | uv | pipx |
| --- | --- | --- | --- |
| Solves | Another Python version | Another Python version | A CLI application for one user |
| Mechanism | Shims at the front of `PATH` [8] | Managed interpreters in `UV_PYTHON_INSTALL_DIR`, checked before `PATH` [7] | One venv per application under `PIPX_HOME`, commands linked into `~/.local/bin` [5] |
| Version choice | `PYENV_VERSION`, then `.python-version` in the current directory, then in a parent, then `$(pyenv root)/version` [8] | `.python-version` (written by `uv python pin`); `python-preference` defaults to `managed` [7] | Uses an interpreter, does not install one |
| Install cost | Most versions built from source; needs build dependencies [8] | Downloads prebuilt python-build-standalone builds, nothing compiled [7] | A venv per tool |

pipx records index options and passes them again on `pipx upgrade` and `pipx reinstall` [6]:

```bash
pipx install devenv --index-url http://localhost:8080/simple/
pipx install devenv --pip-args="--no-index --find-links /srv/wheels"
```

## Gotchas

- **A local folder shadows the package.** A `requests/` folder where you run wins, because that directory is first on the import path [16]. `requests.__file__` points into your repository; rename the folder or run from elsewhere.
- **A stray `.pth` file.** Every line of a `.pth` file lands on `sys.path`, so one leftover file changes what every program on that interpreter imports [3]. Spot the odd entry in `python -m site` and remove the file.
- **Works in the shell, fails in cron.** `ModuleNotFoundError` there usually means a different interpreter. Print `sys.executable` and `sys.path`, then call `.venv/bin/python` by full path; activation does not carry over [2].
- **A copied venv breaks.** After a move, shebangs still hold the old absolute path, so scripts such as `pytest` fail to start. Recreate the venv [2].
- **`--break-system-packages` "fixes" the error.** It lets pip write where apt manages, and PEP 668 says it should not be on by default [1]. Use a venv, pipx or an apt package [4].
- **`python` runs an unexpected version.** With pyenv, `command -v python` shows whether you hit a shim, which then follows the order in the table [8].
- **pipx ignores `PIP_INDEX_URL`.** The uv backend ignores `PIP_*` variables and wants uv's own, such as `UV_INDEX_URL` [6].

## Check yourself

- Your app imports a module from `/usr/lib/python3/dist-packages` inside a venv. Which `pyvenv.cfg` key do you check?
- Why is `sys.prefix != sys.base_prefix` a better venv test than `VIRTUAL_ENV`?

:::key-takeaways
- Imports walk `sys.path` in order and take the first match; the script's directory comes first. [3] [16]
- `pyvenv.cfg` (`home`, `include-system-site-packages`) plus `sys.prefix != sys.base_prefix` is the whole venv mechanism; activation only edits `PATH`. [2] [3]
- Venvs are not portable because shebangs hold absolute paths; recreate them, never copy them. [2]
- The `EXTERNALLY-MANAGED` marker makes pip refuse system installs outside a venv; `--break-system-packages` overrides it and should stay off. [1] [23]
- pyenv and uv add Python versions (uv without compiling); pipx gives each CLI its own venv. [5] [7] [8]
:::

:::glossary
- **`sys.path`**: the ordered list of directories Python searches for imports.
- **site-packages / dist-packages**: the directories where installed third-party packages live; Debian uses the second name.
- **`site` module**: the standard module that adds site-packages and `.pth` entries to `sys.path` at start-up.
- **`.pth` file**: a small text file in site-packages whose lines are added to `sys.path`.
- **User site**: a per-user site-packages directory under `~/.local`.
- **Prefix (`sys.prefix`)**: the root directory of the Python installation or environment that is running.
- **Virtual environment (venv)**: a directory with its own site-packages that reuses an existing Python interpreter.
- **`pyvenv.cfg`**: the file at the root of a venv that tells Python which base interpreter to use and whether to see system packages.
- **Activation**: sourcing `bin/activate` to put the venv first on `PATH`; convenient, never required.
- **Shebang**: the `#!` first line of a script naming the interpreter that runs it.
- **Externally managed**: a Python installation owned by another package manager, such as apt, marked by an `EXTERNALLY-MANAGED` file.
- **Shim**: a small stand-in executable that decides which real program to run.
- **pyenv**: a tool that installs several Python versions and switches between them with shims.
- **uv**: a fast Python package and project manager that can also install Python itself.
- **Managed interpreter**: a Python that uv installed itself.
- **python-build-standalone**: Astral's project that publishes portable prebuilt CPython builds.
- **pipx**: a tool that installs each Python CLI application into its own venv.
:::
