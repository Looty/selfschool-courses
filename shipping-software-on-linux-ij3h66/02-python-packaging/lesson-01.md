---
id: l05
title: "pyproject.toml: one file for metadata and build"
quiz: quiz-01.yaml
resources: [../resources/lab2-devenv/pyproject.toml]
sources: [11, 13, 18]
---
After this lesson you can read and write a `pyproject.toml` for a real project, say which fields are mandatory, and predict the errors a build backend raises for a bad `dynamic` list or a misplaced entry-point table.

## Two tables, two audiences

`pyproject.toml` holds two kinds of information for two different readers:

- `[build-system]` tells a build tool how to build the project: which packages must be installed before the build starts, and which backend to call. Its `requires` key is mandatory once the table exists. [11] PEP 518 introduced it because `setup.py` could not declare its own build dependencies: you could not run the file without knowing what it needed, and you could not know that without running it. [13]
- `[project]` is the package's metadata: its name, version, dependencies and commands. Installers and indexes read it once it is turned into a wheel's `METADATA`. [11]

Tools keep their own settings under `[tool.<name>]`. A project may only use a `tool.<name>` table if it owns `<name>` on PyPI. [11]

This is the course's lab project, used again in chapters 03 and 05:

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

The `[build-system]` block is the one the PyPA tutorial gives for hatchling. The tutorial lists equivalent blocks for setuptools (`setuptools >= 77.0.3`, backend `setuptools.build_meta`), flit and pdm. [18]

## What is required

Only `name` must be written out statically. `version` is required too, but it may be listed as dynamic instead, meaning the backend works it out at build time. Every other key is optional. [11] If there is no `pyproject.toml`, or the file has no `[build-system]` table, tools fall back to `requires = ["setuptools"]`. [11] [13]

## Dependencies and extras

`dependencies` is a list of dependency specifiers, each becoming one `Requires-Dist` line in the metadata. `optional-dependencies` is a table of extras, each becoming a `Provides-Extra`. [11] Lab 2 shows the result inside the built wheel:

```text
Name: shiplab-devenv
Version: 0.1.0
Requires-Python: >=3.9
Requires-Dist: packaging>=23
```

## Commands: `[project.scripts]`

`[project.scripts]` maps a command name to a Python object; it becomes the `console_scripts` entry-point group. `[project.gui-scripts]` does the same for `gui_scripts`. Other groups go under `[project.entry-points.<group>]`, one level deep only. A backend must raise an error if you define `[project.entry-points.console_scripts]`, because that would duplicate `[project.scripts]`. [11] Lesson 7 shows what an installer does with these entries.

## `dynamic`: what the backend may fill in

`dynamic = ["version"]` tells the backend to compute a field. The rules are strict, and each one is a build error you will meet in CI:

- `name` can never be dynamic. [11]
- A key set statically and also listed in `dynamic` is an error, except for list-like keys such as `dependencies`, `scripts` or `classifiers`, where the backend may only append. [11]
- If a key is listed in `dynamic` and the backend cannot work it out, that is an error too. [11]

## Licence fields changed

`license` is now a string holding an SPDX licence expression, such as `"MIT"`. The older table form (`{file = ...}` or `{text = ...}`) is deprecated by PEP 639. `license-files` takes glob patterns for licence files to include in every distribution. [11] The tutorial uses `license = "MIT"` and `license-files = ["LICEN[CS]E*"]`. [18] Older examples on the web still show the table form.

:::key-takeaways
- `[build-system]` says how to build, `[project]` says what the package is, `[tool.*]` holds tool settings. [11]
- Only `name` must be static; `version` is required but may be dynamic. [11]
- Defining `[project.entry-points.console_scripts]` is an error; use `[project.scripts]`. [11]
- A key cannot be both static and in `dynamic`, except list keys that the backend may append to. [11]
- `license` is an SPDX string now; the table form is deprecated. [11]
:::

:::glossary
- **`pyproject.toml`**: the standard configuration file at the root of a Python project.
- **TOML**: a simple configuration file format of tables and key-value pairs.
- **Build backend**: the library that turns a source tree into a wheel or sdist, such as hatchling or setuptools.
- **Metadata**: the facts about a package (name, version, dependencies) that installers read.
- **Dependency specifier**: a requirement string such as `packaging>=23`.
- **Extra**: an optional group of dependencies, installed with `pkg[extra]`.
- **Entry point**: a named reference to a Python object that tools discover from installed metadata.
- **SPDX expression**: a standard short licence identifier such as `MIT` or `Apache-2.0`.
:::
