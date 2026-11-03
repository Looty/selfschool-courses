---
id: l03
title: "pyproject.toml and the build: backends, isolation, src layout and entry points"
quiz: quiz-01.yaml
resources: [../resources/lab2-devenv/pyproject.toml, ../resources/lab2-devenv/src/devenv/__init__.py, ../resources/lab2-devenv/src/devenv/cli.py]
sources: [2, 11, 12, 13, 16, 17, 18, 19, 20]
---
After this lesson you can write a `pyproject.toml`, explain what `python -m build` does, debug a build that fails only in CI, and trace how the `devenv` command reaches `devenv.cli:main`.

## pyproject.toml: three tables

`pyproject.toml` holds information for different readers: [11]

| Table | Says | Read by |
| --- | --- | --- |
| `[build-system]` | which packages the build needs (`requires`, mandatory once the table exists) and which backend to call | build tools |
| `[project]` | name, version, dependencies, commands | installers and indexes, once it becomes a wheel's `METADATA` |
| `[tool.<name>]` | settings for one tool; only if you own `<name>` on PyPI | that tool |

PEP 518 introduced `[build-system]` because `setup.py` could not declare its own build dependencies without being run first. [13]

This is the course's `devenv` CLI, the project that Lab 2 (chapter 05) packages as a `.deb`:

```toml
[build-system]
requires = ["hatchling >= 1.26"]
build-backend = "hatchling.build"

[project]
name = "shiplab-devenv"
version = "0.1.0"
description = "A tiny developer CLI used in the Shipping Software on Linux course labs"
requires-python = ">=3.9"
dependencies = [
    "packaging>=23",
]
license = "MIT"

[project.scripts]
devenv = "devenv.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/devenv"]
```

The PyPA tutorial gives equivalent `[build-system]` blocks for hatchling, setuptools (backend `setuptools.build_meta`), flit and pdm, and does not rank them. [18]

## The rules that cause build errors

- Only `name` must be static and can never be dynamic. `version` is required but may be listed in `dynamic`, so the backend computes it. [11]
- A key set statically and also listed in `dynamic` is an error, except list-like keys such as `dependencies` or `scripts`, where the backend may only append. A dynamic key the backend cannot work out is an error too. [11]
- `license` is now an SPDX string such as `"MIT"`; the table form is deprecated by PEP 639. [11]

Each entry in `dependencies` becomes one `Requires-Dist` line in the wheel's metadata (the lab's shows `Requires-Dist: packaging>=23`); each key of `optional-dependencies` becomes a `Provides-Extra`. [11]

## Frontend and backend: what `python -m build` does

PEP 517 splits building into two roles: [12]

- The **frontend** is the tool you run, such as `pip` or `build`. It turns a source tree into wheels.
- The **backend** does the building for that project. `build-backend` names it, for example `hatchling.build` or `setuptools.build_meta`. [12] [18]

The contract is a set of hooks the frontend imports from the backend. `build_wheel` writes a `.whl` and returns its file name; `build_sdist` does the same for a `.tar.gz`. [12]

`python -m build` runs these steps:

1. Read `[build-system]`; `requires` lists the build dependencies. [13]
2. Create a fresh, isolated environment and install those requirements. PEP 517 says a frontend "SHOULD, by default, create an isolated environment for each build". [12]
3. Import the backend there and call its hooks. [12]

```text
$ python -m build
Successfully built shiplab_devenv-0.1.0.tar.gz and shiplab_devenv-0.1.0-py3-none-any.whl
```

Isolation is deliberate. Projects can need conflicting build tools, and isolation forces authors to declare build dependencies accurately. [12] With no `build-backend`, the frontend falls back to the legacy setuptools path. [12] With no `[build-system]` table at all, tools assume `requires = ["setuptools"]`. [11] [13]

## src layout: test what you ship

In a **flat layout** the package sits at the repository root (`./devenv/`). In a **src layout** it sits under `./src/devenv/`. [16] The current directory is the first entry on `sys.path`, so in a flat layout `import devenv` from the repository root loads the working copy, not the installed one. [16] With a src layout there is no `devenv/` at the root, so the import must come from an installed copy. [16]

hatchling needs to be told where the package lives: `packages = ["src/devenv"]` ships it in the wheel as `devenv/`. [20] The distribution name (`shiplab-devenv`, what pip installs) and the import name (`devenv`, what Python imports) differ. `__init__.py` reads its version with `importlib.metadata.version("shiplab-devenv")`, which needs the distribution name and only works once the package is installed.

## Entry points: from command to function

`[project.scripts]` maps a command name to an object and becomes the `console_scripts` entry-point group. [11] The value is a module path, a colon, then an attribute path. [19] The backend writes the group into `entry_points.txt` inside the wheel's `.dist-info` directory: [19]

```text
$ cat shiplab_devenv-0.1.0.dist-info/entry_points.txt
[console_scripts]
devenv = devenv.cli:main
```

At install time the installer creates a small wrapper script for each entry point. [19] In a venv, installed scripts carry a shebang with the absolute path of that venv's interpreter. [2] That is how pipx can link `devenv` into `~/.local/bin` and still run it inside its own venv. The lab's `main()` returns an `int`, which becomes the exit status.

## Editable installs

`pip install -e .` installs dependencies, metadata and script wrappers, but not a copy of your code. setuptools uses a `.pth` file in site-packages or a custom import hook, and does not promise which. [17]

| Change | Seen without reinstall? |
| --- | --- |
| Edit to an existing `.py` file | yes [17] |
| New dependency | no, rerun `pip install -e .` [17] |
| New or changed entry point | no [17] |
| Other metadata (description, ...) | no [17] |

## Gotchas

- **Version both static and dynamic.** `version = "0.1.0"` plus `dynamic = ["version"]` makes the backend refuse to build. Remove one. [11]
- **`[project.entry-points.console_scripts]`.** A backend must raise an error, because it duplicates `[project.scripts]`. Use `[project.scripts]`. [11]
- **Works on the laptop, fails in CI.** The backend hits `ModuleNotFoundError` for a module the build imports, installed on your laptop but not listed in `requires`. Add it to `[build-system] requires`, not to `dependencies`; do not switch isolation off in CI. [12] [13]
- **Tests pass, wheel is broken.** With a flat layout, `pytest` from the repository root imports the working copy, so tests pass even when the wheel lacks a module. Use a src layout. [16]
- **New command "not found".** You added a `[project.scripts]` entry, but the editable install has no wrapper for it yet. Rerun `pip install -e .`. [17]
- **Odd file dates in the wheel.** Every file in the lab's wheel is dated `2020-02-02 00:00:00`. Not a bug: hatchling builds reproducibly, using `SOURCE_DATE_EPOCH` or a fixed default. [20]

:::key-takeaways
- `[build-system]` says how to build, `[project]` what the package is; only `name` must be static. [11]
- The frontend (pip, build) drives; the backend (hatchling, setuptools) builds, in an isolated environment by default. [12]
- A build that only works without isolation has an undeclared build dependency. [12] [13]
- The src layout stops the working copy from shadowing the installed package. [16]
- `[project.scripts]` becomes `console_scripts` in `entry_points.txt`; editable installs need a reinstall for new entry points, dependencies or metadata. [17] [19]
:::

:::glossary
- **`pyproject.toml`**: the standard configuration file at the root of a Python project.
- **Build backend**: the library that turns a source tree into a wheel or sdist, such as hatchling or setuptools.
- **Frontend**: the tool you run to build or install, such as `pip` or `python -m build`.
- **Build isolation**: building in a fresh temporary environment that holds only the declared build requirements.
- **Extra**: an optional group of dependencies, installed with `pkg[extra]`.
- **Entry point**: a named reference to a Python object that tools discover from installed metadata.
- **src layout**: keeping the import package under a `src/` directory instead of at the repository root.
- **Editable install**: an install that points at your source tree instead of copying it.
- **`.dist-info`**: the directory of metadata files that an installed distribution carries.
- **Distribution name**: the name pip installs (`shiplab-devenv`), which may differ from the import name (`devenv`).
- **`SOURCE_DATE_EPOCH`**: an environment variable that build tools use as the fixed timestamp for files.
:::
