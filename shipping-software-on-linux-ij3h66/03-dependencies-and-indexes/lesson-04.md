---
id: l13
title: "Lab 2: build a CLI, publish it to a private index, install it with pipx"
quiz: quiz-04.yaml
resources: [../resources/lab2-run.sh, ../resources/lab2-devenv/pyproject.toml, ../resources/lab2-devenv/src/devenv/cli.py, ../resources/lab2-devenv/src/devenv/__init__.py]
sources: [5, 6, 18, 19, 23, 25, 26, 86]
---
After this lab you will have built a small developer CLI as a wheel, published it to a private index you run yourself, installed it with pipx from that index only, shipped a 0.1.1 and upgraded, and watched dependency confusion happen on a real package name.

This is a hands-on lab. `lab2-run.sh` was run end to end in a `python:3.12-slim-bookworm` container while writing this course. Every output below is from that run. It needs internet access once, to install the tools and to mirror one dependency.

## Shortcut: the ready-made script

Download the lab files from this lesson's Resources, keeping the `lab2-devenv/` folder next to `lab2-run.sh`. Then:

```bash
docker run --rm -it -v "$PWD":/lab -w /lab python:3.12-slim-bookworm bash lab2-run.sh
```

The script never changes your copy of the project. It copies it to `/tmp/devenv` first.

## The project

`shiplab-devenv` is a src-layout project (lesson 7) with one dependency, `packaging>=23`, and one command, `devenv`, with two subcommands:

- `devenv doctor` prints which interpreter runs the tool, whether it is a venv and whether the base interpreter carries the PEP 668 marker (chapter 01);
- `devenv compare A B` compares two PEP 440 versions (lesson 9).

## Step 1: build

The build tools live in their own venv (`/opt/tools`), not in the project's. Then `python -m build`: [18]

```text
Successfully built shiplab_devenv-0.1.0.tar.gz and shiplab_devenv-0.1.0-py3-none-any.whl
```

Inside the wheel, `entry_points.txt` holds the command [19] and `METADATA` holds the dependency:

```text
[console_scripts]
devenv = devenv.cli:main

Requires-Dist: packaging>=23
```

## Step 2: run a private index and upload

```bash
pypi-server run -p 8080 -a . -P . --disable-fallback /srv/packages &
twine upload --repository-url http://localhost:8080/ -u lab -p lab dist/*
```

`-a . -P .` disables authentication [25]; `--disable-fallback` stops pypiserver from redirecting names it lacks to PyPI. [86] twine's `--repository-url` names the upload target directly. [26]

The index now has the project but not its dependency. Rather than let PyPI back-fill it, the script mirrors it as a wheel:

```text
$ pip download 'packaging>=23' pip --only-binary :all: -d /srv/packages && ls /srv/packages
packaging-26.3-py3-none-any.whl
pip-26.2.2-py3-none-any.whl
shiplab_devenv-0.1.0-py3-none-any.whl
shiplab_devenv-0.1.0.tar.gz
```

Why `pip` too? Without it, the first run failed. pipx refreshes its shared pip from the same `--index-url`, and the call `pip install --upgrade --index-url http://localhost:8080/simple/ ... pip >= 26.2.2` had nothing to install. pipx documents the shared pip and its refresh [5]; the failure itself was observed in this lab. An offline index has to carry the tooling as well as your dependencies.

## Step 3: install with pipx from that index only

```text
$ pipx install shiplab-devenv --index-url http://localhost:8080/simple/
  installed package shiplab-devenv 0.1.0, installed using Python 3.12.16
  These apps are now available
    - devenv
$ devenv doctor
devenv        0.1.0
executable    /root/.local/share/pipx/venvs/shiplab-devenv/bin/python
prefix        /root/.local/share/pipx/venvs/shiplab-devenv
base_prefix   /usr/local
in a venv     yes
PEP 668 mark  absent on the base interpreter
```

The tool runs in its own pipx venv. [5] The marker is absent because the `python:` images install Python under `/usr/local`, not through apt. On `debian:bookworm`'s apt-installed Python, Lab 1 found the marker file in place.

```text
$ devenv compare 1.0rc1 1.0
1.0rc1 < 1.0
$ devenv compare 1.0.post1 1.0
1.0.post1 > 1.0
```

## Step 4: ship 0.1.1 and upgrade

The script bumps `version` in `pyproject.toml`, builds a wheel, uploads it, and runs `pipx upgrade shiplab-devenv`:

```text
$ devenv --version
devenv 0.1.1
```

You did not pass `--index-url` again. pipx recorded it at install time and reuses it on upgrade. [6]

## Step 5: dependency confusion on a real name

The script publishes a copy of the CLI under the plain name `devenv`, version 0.0.9. PyPI already has an unrelated `devenv`, so the clash is real:

```text
$ pip index versions devenv --index-url http://localhost:8080/simple/
devenv (0.0.9)
$ pip index versions devenv --index-url http://localhost:8080/simple/ --extra-index-url https://pypi.org/simple/
devenv (0.1.1)
Available versions: 0.1.1, 0.1.0, 0.0.9
$ pip index versions devenv --index-url http://localhost:8081/simple/   # empty pypiserver, default settings
devenv (0.1.1)
Available versions: 0.1.1, 0.1.0
```

With an extra index, the public 0.1.1 wins, because pip does not rank indexes. [23] With a pypiserver on default settings, the public package leaks in even with a single `--index-url`. [86] `pip index versions` only lists versions. It downloads and installs nothing, so the demo is safe.

## Check yourself

- Remove `--disable-fallback` from the first `pypi-server` line and rerun. Does the pip mirroring step still matter for pipx? What would happen if PyPI were unreachable?
- Run `devenv doctor` from a venv created with `debian:bookworm`'s system Python. What does the marker line say now?

:::low-confidence
PyPI's own `devenv` project, its versions (0.1.0, 0.1.1) and the versions of pip and packaging were current on 2026-11-02 and will change. If the public name stops existing, step 5 will show only the local 0.0.9, and the lesson still holds.
:::

:::key-takeaways
- `python -m build` gives an sdist and a wheel; the wheel carries `entry_points.txt` and `Requires-Dist`. [18] [19]
- A private index for offline installs must hold your package, its dependencies and pip itself if pipx is used.
- `pipx install --index-url` is remembered for `pipx upgrade`. [6]
- `--extra-index-url` and default proxy fallback both let a public name win. [23] [86]
:::

:::glossary
- **pypiserver**: a minimal PyPI-compatible index server.
- **twine**: the tool that uploads distributions to an index.
- **Mirror (verb)**: copy selected packages from a public index onto your own.
- **Shared pip (pipx)**: one pip installation that pipx links into every app's venv under its pip backend.
- **`pip index versions`**: a pip command that lists the versions an index offers, without installing.
:::
