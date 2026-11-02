---
id: l02
title: Virtual environments and PEP 668
quiz: quiz-02.yaml
resources: []
sources: [1, 2, 3, 4, 9, 23]
---
After this lesson you can explain why virtual environments exist, what `python -m venv` actually creates, how the interpreter knows it is inside one, and why Debian's pip refuses `sudo pip install`.

## Why virtual environments exist

One Python installation has one set of site-packages. If two applications on the same machine need different versions of the same library, one shared directory cannot hold both. Installing into the system interpreter has a second cost on Debian: that interpreter belongs to the operating system. apt installs Python modules into it under `/usr/lib/python3/dist-packages`. [4] Anything pip writes there can replace a module that a system tool was packaged and tested against. (That is the reasoning behind the rule, not a quote from it.) PEP 668's answer is to let the distribution mark its interpreter as "externally managed" and to steer installs to a venv instead. [1]

A virtual environment ("venv") is that elsewhere. It is a small directory that reuses an existing interpreter but has its own site-packages. Each application gets its own copy of its dependencies. You can create, delete and recreate it without touching the system. [2]

## What `python -m venv` creates

`python -m venv DIR` creates the directory. It writes a `pyvenv.cfg` file with a `home` key pointing at the installation the command was run from. It adds an `include-system-site-packages` key, which is `true` only with `--system-site-packages`. [2] This is the file from Lab 1, made on `debian:bookworm`:

```text
home = /usr/bin
include-system-site-packages = false
version = 3.11.2
executable = /usr/bin/python3.11
command = /usr/bin/python3 -m venv /opt/app/.venv
```

There is no copy of the standard library. `bin/python` is a link to (or copy of) the base interpreter, and `lib/python3.11/site-packages` starts almost empty.

## How the interpreter knows it is in a venv

When Python starts from a venv, `sys.prefix` and `sys.exec_prefix` point at the venv, while `sys.base_prefix` and `sys.base_exec_prefix` point at the base installation. Checking `sys.prefix != sys.base_prefix` is enough to tell that you are in one. [2] The `site` module then reads `pyvenv.cfg`. If `include-system-site-packages` is not `true`, the system site-packages are not searched, and neither is the user site. [3] That is the whole isolation mechanism: the import list is built from the venv's directory instead of the system's.

```bash
/opt/app/.venv/bin/python -c 'import sys; print(sys.prefix, sys.base_prefix)'
# /opt/app/.venv /usr
```

## Activation is optional

`source .venv/bin/activate` only puts the venv's `bin` directory first on `PATH`, so `python` resolves to the venv's interpreter, and sets `VIRTUAL_ENV`. You never need to activate. Calling `.venv/bin/python` by full path works the same, and scripts installed in the venv run without activation. [2] For the same reason, `VIRTUAL_ENV` cannot be relied on to detect a venv. [2] In services, cron jobs and systemd units, call the venv's interpreter by its full path.

## Venvs are disposable, not portable

Scripts installed into a venv get a shebang line with the absolute path of the venv's interpreter, so a venv cannot be moved or copied. The documentation's advice is to delete it and recreate it from a requirements file. [2] Treat a venv like a build artifact, never like source code.

## PEP 668: the "externally-managed-environment" error

A distribution marks its interpreter by placing an `EXTERNALLY-MANAGED` file in the standard-library directory. The file is INI with an `[externally-managed]` section and an `Error` key holding the message to show. [1] An installer that finds the marker and is not running in a venv must refuse to install and show that message. [1] On bookworm:

```text
$ pip install requests
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
```

The message continues with advice to create a venv or use pipx. [4] Inside a venv the marker does not apply, because the venv owns its own site-packages. [1]

## Why `sudo pip install` is wrong, and the escape hatch

`sudo pip install` aims at the very directories apt manages. PEP 668 lets installers offer an override and suggests the flag name `--break-system-packages`. It also says the override should not be enabled by default. [1] pip's own description of the flag is "Allow pip to modify an EXTERNALLY-MANAGED Python installation". [23] `pip install --user` is no way out either. pip will not do a `--user` install inside a venv that hides site-packages. [9] On a marked system it is still an install outside a venv, which is exactly what the marker forbids. [1]

The right choices, in order: an apt package (`python3-xyz`) for something the system itself needs; a venv for an application; pipx for a command-line tool (next lesson). [4]

:::key-takeaways
- A venv exists so each application has its own site-packages and the system interpreter stays owned by apt. [1] [2]
- `pyvenv.cfg` (`home`, `include-system-site-packages`) plus `sys.prefix != sys.base_prefix` is the whole mechanism. [2] [3]
- Activation only edits `PATH`; call `.venv/bin/python` directly in automation. [2]
- Venvs are not portable because shebangs hold absolute paths; recreate them, never copy them. [2]
- The `EXTERNALLY-MANAGED` marker makes pip refuse system installs outside a venv; `--break-system-packages` overrides it and should stay off by default. [1] [23]
:::

:::glossary
- **Virtual environment (venv)**: a directory with its own site-packages that reuses an existing Python interpreter.
- **`pyvenv.cfg`**: the file at the root of a venv that tells Python which base interpreter to use and whether to see system packages.
- **Activation**: sourcing `bin/activate` to put the venv first on `PATH`; convenient, never required.
- **Shebang**: the `#!` first line of a script naming the interpreter that runs it.
- **Externally managed**: a Python installation owned by another package manager, such as apt, marked by an `EXTERNALLY-MANAGED` file.
- **apt**: Debian's package manager.
- **pipx**: a tool that installs each Python command-line application into its own venv.
:::
