---
id: l01
title: How Python finds packages
quiz: quiz-01.yaml
resources: []
sources: [1, 3, 4, 16]
---
After this lesson you can explain how one `import` statement turns into a file on disk, read the output of `python -m site`, and say why the same import works for one interpreter and fails for another.

## The short version

`import requests` does not search your disk. Python walks a list of directories, `sys.path`, in order, and takes the first match. Almost every "it works on my machine" packaging bug comes down to one of two things. Either the interpreter you ran was not the one you installed into, or its `sys.path` holds a directory you didn't expect. This lesson covers how that list is built.

## Where the entries come from

At start-up the interpreter imports the `site` module, unless you pass `-S`. `site` builds the site-packages part of the path. It takes up to four directories from two heads, `sys.prefix` and `sys.exec_prefix`. Each is combined with two tails: the empty string and `lib/pythonX.Y/site-packages` on Unix. Each combination that exists as a directory is added to `sys.path`, and `site` reads any configuration files it finds there. [3]

The full order on a typical Linux box is:

1. The directory of the script you ran, or the current directory for `python -c` and the REPL. The packaging guide warns that the current directory comes first on the import path. So a folder with the same name as an installed package wins over the installed copy. [16]
2. The standard library.
3. The user site directory, `~/.local/lib/pythonX.Y/site-packages`, if it is enabled. [3]
4. The site-packages directories under the prefixes. [3]

## `.pth` files: lines that extend the path

Any `name.pth` file in a site directory adds one path per line to `sys.path`. Lines naming directories that don't exist are skipped, duplicates are dropped and `#` lines are comments. For backward compatibility, a line that starts with `import` is executed. That behaviour is deprecated as of Python 3.15. [3] Editable installs and some tools use `.pth` files, so a stray one in site-packages can quietly change what every program on that interpreter imports. Chapter 02 comes back to this.

## The user site and how to switch it off

`site.ENABLE_USER_SITE` reports whether the user directory is on the path. It is `True` when enabled, `False` when you disabled it with `-s` or the `PYTHONNOUSERSITE` variable, and `None` when Python disabled it for security reasons or an administrator did. [3] Inside a virtual environment that does not include system site-packages, the user site is also left out. [3] That is the first hint of why a venv isolates you: it controls this list.

## Debian's twist: `dist-packages` and two trees

Debian and Fedora split the system interpreter's path in two. One directory holds packages from the distribution, and the other holds what the local administrator installs. Debian uses `/usr/lib/python3/dist-packages` for apt-installed Python modules and `/usr/local/lib/python3/dist-packages` for local installs. [4] PEP 668 recommends this split and asks that the local directory come first, so local installs take precedence. [1] Python's own `site` documentation does not mention `dist-packages`, which is a distribution choice. [3]

## Look, don't guess: `python -m site`

Run with no arguments, `python -m site` prints `sys.path`, then `USER_BASE` and `USER_SITE` with whether each exists, then `ENABLE_USER_SITE`. The exit code is 0 if the user site is enabled, 1 if the user disabled it, and 2 if it was disabled for security or by an administrator. [3] This is the first command to run when an import fails in production. It shows exactly where that interpreter looks. On the `debian:bookworm` container used for this course's labs, the system interpreter printed:

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

The local `dist-packages` comes before the distro one, as PEP 668 recommends. [1] The output above comes from Lab 1, the lab at the end of this chapter, and is not quoted from a source.

## A debugging habit

When an import fails, ask the interpreter about itself before reaching for `pip install`:

```bash
python3 -c 'import sys; print(sys.executable); print(*sys.path, sep="\n")'
python3 -c 'import requests; print(requests.__file__)'
```

The first line tells you which binary ran and where it looks. The second tells you which copy of a package won. Most surprises come from a second interpreter on `PATH` or an unexpected entry early in the list.

:::key-takeaways
- Imports walk `sys.path` in order and take the first match; the script's directory comes first. [3] [16]
- `site` adds site-packages from `sys.prefix` and `sys.exec_prefix`, and processes `.pth` files there. [3]
- The user site (`~/.local/lib/pythonX.Y/site-packages`) can be disabled with `-s` or `PYTHONNOUSERSITE`. [3]
- Debian splits `dist-packages` into a distro tree under `/usr/lib` and a local tree under `/usr/local/lib`. [4]
- `python -m site` shows the real search path for the interpreter you are running. [3]
:::

:::glossary
- **Interpreter**: the `python3` program that runs your code; a machine can have several.
- **`sys.path`**: the ordered list of directories Python searches for imports.
- **site-packages / dist-packages**: the directories where installed third-party packages live; Debian uses the second name.
- **`site` module**: the standard module that adds site-packages and `.pth` entries to `sys.path` at start-up.
- **`.pth` file**: a small text file in site-packages whose lines are added to `sys.path`.
- **User site**: a per-user site-packages directory under `~/.local`.
- **Prefix (`sys.prefix`)**: the root directory of the Python installation or environment that is running.
- **PEP**: Python Enhancement Proposal, the documents that define Python standards.
:::
