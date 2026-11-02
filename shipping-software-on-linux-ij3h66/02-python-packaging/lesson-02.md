---
id: l06
title: "Build frontends and backends: PEP 517 and 518"
quiz: quiz-02.yaml
resources: []
sources: [11, 12, 13, 18, 20]
---
After this lesson you can explain what happens when you run `python -m build`, tell a frontend from a backend, and debug a build that works on your laptop but fails in CI because of build isolation.

## Two roles

PEP 517 splits building into two roles:

- A **frontend** is the tool you run. It takes a source tree or source distribution and produces wheels. `pip` and `build` are frontends. [12]
- A **backend** does the actual building for that project. It is named by `build-backend` in `pyproject.toml`, for example `hatchling.build` or `setuptools.build_meta`. [12] [18]

The contract between them is a handful of Python functions (hooks) the frontend imports from the backend:

```python
def build_wheel(wheel_directory, config_settings=None, metadata_directory=None): ...
def build_sdist(sdist_directory, config_settings=None): ...
```

`build_wheel` writes a `.whl` into the directory and returns its file name; `build_sdist` does the same for a `.tar.gz`. [12] Optional hooks let the frontend ask for extra build dependencies (`get_requires_for_build_wheel`) or prepare metadata without a full build (`prepare_metadata_for_build_wheel`). [12]

## What `python -m build` does, step by step

1. Reads `[build-system]` from `pyproject.toml`; PEP 518 made `requires` the place to list build dependencies. [13]
2. Creates a fresh, isolated environment and installs those requirements into it. PEP 517 says a frontend "SHOULD, by default, create an isolated environment for each build". [12]
3. Imports the backend in that environment and calls its hooks to produce the sdist and the wheel. [12]

In Lab 2 the result was:

```text
$ python -m build
Successfully built shiplab_devenv-0.1.0.tar.gz and shiplab_devenv-0.1.0-py3-none-any.whl
```

## Build isolation: why CI and laptops differ

Isolation is deliberate. Two projects can need conflicting build tools, and isolation forces authors to declare their build dependencies accurately. [12] The common failure is the reverse case: a build script imports something (say, `numpy` to read a version, or a code generator) that happens to be installed on your laptop but is not listed in `requires`. It works locally with isolation switched off and fails in a clean CI runner. The fix is to add it to `[build-system] requires`, not to switch isolation off in CI.

## When there is no `build-backend`

If `pyproject.toml` is missing or has no `build-backend`, the frontend falls back to the legacy behaviour: running `setup.py`, or the `setuptools.build_meta:__legacy__` backend. [12] Projects can also ship a backend inside the repository and point at it with `backend-path`. [12]

## Choosing a backend

The PyPA tutorial lets you pick hatchling, setuptools, flit or pdm and gives a `[build-system]` block for each. It does not rank them. [18] Practical differences you will meet:

- **setuptools** is the default when no `[build-system]` table exists, and the legacy fallback uses it. [11] [12]
- **hatchling** is configured under `[tool.hatch.build]`. For a src layout you name the package directory: `packages = ["src/devenv"]` on the wheel target. [20] It makes reproducible builds by default, using `SOURCE_DATE_EPOCH` for timestamps or a fixed default when that variable is unset. [20]

That last point is visible in Lab 2: every file inside the wheel had the same timestamp, which hatchling sets on purpose.

```text
devenv/__init__.py                             2020-02-02 00:00:00          274
devenv/cli.py                                  2020-02-02 00:00:00         1835
```

The Hatch page does not say why it chose that exact date; it only says an unchanging default is used. [20]

:::key-takeaways
- The frontend (pip, build) drives; the backend (hatchling, setuptools) builds, through `build_wheel` and `build_sdist`. [12]
- `[build-system] requires` lists build dependencies, installed into an isolated environment by default. [12] [13]
- A build that only works without isolation has an undeclared build dependency. [12]
- No `build-backend` means the legacy setuptools path. [12]
- hatchling builds are reproducible by default via `SOURCE_DATE_EPOCH` or a fixed timestamp. [20]
:::

:::glossary
- **Frontend**: the tool you run to build or install, such as `pip` or `python -m build`.
- **Backend**: the library a project names to do the build, such as `hatchling.build`.
- **Hook**: a function with an agreed name and signature that one tool calls in another.
- **Build isolation**: building in a fresh temporary environment that holds only the declared build requirements.
- **sdist**: a source distribution, a `.tar.gz` of the source plus metadata.
- **Wheel**: a built distribution, a `.whl` zip that installers can unpack without running code.
- **Reproducible build**: a build that produces byte-identical output from the same input.
- **`SOURCE_DATE_EPOCH`**: an environment variable that build tools use as the fixed timestamp for files.
:::
