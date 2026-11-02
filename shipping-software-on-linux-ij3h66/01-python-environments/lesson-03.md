---
id: l03
title: "Interpreters and CLI tools: pyenv, uv and pipx"
quiz: quiz-03.yaml
resources: []
sources: [5, 6, 7, 8]
---
After this lesson you can choose how to get a second Python version onto a Debian host, explain how pyenv and uv each pick an interpreter, and install a developer CLI with pipx without touching the system Python.

## Two separate problems

A venv answers "where do this application's packages go?". It does not answer "which Python version runs it?". A venv reuses whatever interpreter created it (lesson 2). If Debian ships 3.11 and your tool needs 3.12, you need another interpreter first. pyenv and uv solve that. pipx solves a third problem: installing command-line tools for a user.

## pyenv: shims on `PATH`

pyenv inserts a directory of shims at the front of your `PATH`. A shim is a tiny executable named `python`, `pip` and so on. It works out which version you want and runs the real binary. pyenv keeps the shims up to date through "rehashing". [8] It picks the version from, in order:

1. the `PYENV_VERSION` environment variable;
2. a `.python-version` file in the current directory;
3. the first `.python-version` found in a parent directory;
4. the global `$(pyenv root)/version` file. [8]

Each version lives in its own directory under `$(pyenv root)/versions`, which defaults to `~/.pyenv/versions`. Most versions are built from source during install, which is why you need the build dependencies first. [8] On a fleet of servers, that compile step and its dependency list are the cost. On a developer laptop it is a one-off.

Debugging tip: if `python` runs an unexpected version, `command -v python` shows whether you hit a shim. The shim's choice then follows the order above.

## uv: managed interpreters, no compile

uv divides interpreters into "managed" (ones it installed) and "system" (everything else, including pyenv's). [7] It checks managed installs in `UV_PYTHON_INSTALL_DIR` first, then interpreters on `PATH`. [7] `uv python install` installs the latest version, or the one named in a `.python-version` file. `uv python pin` writes that file. [7] The builds are not compiled on your machine. uv downloads them from Astral's python-build-standalone project rather than using official CPython binaries. [7] The `python-preference` setting controls the choice: `managed` (the default) prefers managed installs, `only-managed` never uses system Pythons, and `system`/`only-system` do the reverse. [7]

The uv page does not say whether its managed interpreters carry an `EXTERNALLY-MANAGED` marker. [7] Treat them like any other interpreter: create venvs from them.

## pipx: one venv per command-line tool

Developer CLIs (linters, your team's `devenv` tool from chapter 03) are applications, not libraries, so they should not share site-packages with anything. pipx creates a separate venv for each application under `PIPX_HOME`, for example `~/.local/share/pipx/venvs/black`. It links the application's commands into `~/.local/bin`. [5] With the pip backend, every venv borrows one shared pip through a `.pth` file. With the uv backend there is no shared environment. [5] pipx also writes a `pipx_metadata.json` per venv, which `upgrade` and `reinstall` read back to rebuild the same state. [5]

Installing from a private index or offline (chapter 03 and the labs) uses the same flags you know from pip:

```bash
pipx install devenv --index-url http://localhost:8080/simple/
pipx install devenv --pip-args="--no-index --find-links /srv/wheels"
```

pipx records these options and passes them again on `pipx upgrade` and `pipx reinstall`. [6] Under the pip backend it forwards `PIP_*` environment variables to every pip call. The uv backend ignores them and wants uv's own variables, such as `UV_INDEX_URL`. [6] pipx also refuses an empty index URL. Otherwise a variable that was never set would silently send you to PyPI. [6]

## Which one when

| Need | Tool |
| --- | --- |
| A Python version Debian does not ship, on a laptop | pyenv or `uv python install` |
| The same, in CI or a container, without compiling | `uv python install` [7] |
| A developer CLI for one user | pipx [5] |
| An application's dependencies | a venv per application (lesson 2) |
| A Python tool the operating system depends on | an apt package (chapter 05) |

:::key-takeaways
- pyenv puts shims first on `PATH` and picks a version from `PYENV_VERSION`, then `.python-version`, then the global file; it builds from source. [8]
- uv separates managed and system interpreters, prefers managed ones by default, and downloads prebuilt python-build-standalone builds. [7]
- pipx gives each CLI its own venv and links its commands into `~/.local/bin`. [5]
- pipx remembers `--index-url` and `--pip-args` for upgrades, and the uv backend ignores `PIP_*` variables. [6]
:::

:::glossary
- **Shim**: a small stand-in executable that decides which real program to run.
- **`PATH`**: the list of directories the shell searches for commands, left to right.
- **pyenv**: a tool that installs several Python versions and switches between them with shims.
- **uv**: a fast Python package and project manager that can also install Python itself.
- **Managed interpreter**: a Python that uv installed itself.
- **python-build-standalone**: Astral's project that publishes portable prebuilt CPython builds.
- **pipx**: a tool that installs each Python CLI application into its own venv.
- **CLI**: command-line interface, a program you run from the shell.
- **Index**: a server that hosts Python packages, such as PyPI.
:::
