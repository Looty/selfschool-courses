---
id: l07
title: "src layout, entry points and editable installs"
quiz: quiz-03.yaml
resources: [../resources/lab2-devenv/src/devenv/cli.py, ../resources/lab2-devenv/src/devenv/__init__.py]
sources: [2, 11, 16, 17, 19, 20]
---
After this lesson you can lay out a project so tests run against the installed code, explain how `devenv` on your `PATH` reaches `devenv.cli:main`, and say which changes an editable install picks up and which need a reinstall.

## src layout vs flat layout

In a **flat layout** the import package sits at the repository root (`./devenv/`). In a **src layout** it sits one level down (`./src/devenv/`). The packaging guide lists three differences: [16]

- the src layout needs the project to be installed before its code can run; the flat layout does not;
- the src layout prevents accidental use of the in-development copy;
- in an editable install, the src layout only exposes files that were meant to be importable.

The reason for the second point is the import path from lesson 1. The current directory is the first entry on `sys.path`, so with a flat layout, `python -c 'import devenv'` from the repository root imports the working copy, not the installed one. [16] Tests then pass even when the wheel is missing a module. With a src layout the repository root holds no `devenv/` directory, so the import must come from an installed copy. The guide's usual pattern: an editable install for development, a regular install for testing. [16]

hatchling needs to be told where the package lives. Lab 2 uses `packages = ["src/devenv"]`, which ships it in the wheel as `devenv/`. [20]

## Entry points: how a command reaches your function

The lab declares one command:

```toml
[project.scripts]
devenv = "devenv.cli:main"
```

`[project.scripts]` is the `console_scripts` entry-point group. [11] The value is an object reference: a module path, then a colon, then an attribute path. [19] The backend writes the group into `entry_points.txt` inside the wheel's `.dist-info` directory, in INI format. [19] From Lab 2:

```text
$ cat shiplab_devenv-0.1.0.dist-info/entry_points.txt
[console_scripts]
devenv = devenv.cli:main
```

At install time the installer creates a small command-line wrapper for each entry point. [19] In a venv, installed scripts carry a shebang with the absolute path of that venv's interpreter. [2] That is why pipx can link `devenv` into `~/.local/bin` and still have it run inside its own venv (lesson 3). The lab's `main()` returns an `int`, which becomes the command's exit status.

## Editable installs

`pip install -e .` installs the dependencies, the metadata and the script wrappers, but not a copy of your code. Edits to existing `.py` files show up without reinstalling. [17] setuptools implements this either with a `.pth` file in site-packages (lesson 1) or with a custom import hook, and makes no promise about which one it uses. [17] PEP 660 standardised the hooks; setuptools has supported them since version 64. [17]

What an editable install does **not** pick up without a fresh `pip install -e .`:

- new dependencies;
- new or changed entry points (a new CLI subcommand that is a new script, for example);
- other metadata changes. [17]

setuptools also has a strict mode (`--config-settings editable_mode=strict`). It builds a tree of links, so new files are not exposed until you reinstall, which is closer to what a wheel will contain. [17]

## Putting it together

A layout that avoids the common traps:

```text
shiplab-devenv/
├── pyproject.toml
└── src/
    └── devenv/
        ├── __init__.py
        └── cli.py
```

`__init__.py` reads its own version from the installed metadata with `importlib.metadata.version("shiplab-devenv")`. That works only once the package is installed, which a src layout guarantees anyway. Note that the distribution name (`shiplab-devenv`, what pip installs) and the import name (`devenv`, what Python imports) are different. Lab 2 shows why that can matter.

:::key-takeaways
- The src layout stops the working copy from shadowing the installed package, because the current directory is first on the import path. [16]
- `[project.scripts]` becomes `console_scripts` in `entry_points.txt`; installers create a wrapper per entry. [11] [19]
- Editable installs pick up code edits but need a reinstall for new dependencies, entry points or metadata. [17]
- hatchling's `packages = ["src/devenv"]` ships `src/devenv` as `devenv` in the wheel. [20]
:::

:::glossary
- **src layout**: keeping the import package under a `src/` directory instead of at the repository root.
- **Flat layout**: keeping the import package directly at the repository root.
- **Editable install**: an install that points at your source tree instead of copying it.
- **Object reference**: a `module:attribute` string naming a Python object.
- **`.dist-info`**: the directory of metadata files that an installed distribution carries.
- **Wrapper script**: the small executable an installer creates for an entry point.
- **Distribution name**: the name pip installs (`shiplab-devenv`), which may differ from the import name (`devenv`).
:::
