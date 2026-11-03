---
id: l02
title: "Lab 1: break an environment three ways"
quiz: quiz-02.yaml
resources: [../resources/lab1-break-env.sh]
sources: [1, 2, 3, 4]
---
After this lab you will have hit the three most common Python environment failures on a Debian host, read the evidence for each, and fixed each one: the PEP 668 refusal, the wrong interpreter, and a system site-packages leak.

This is a hands-on lab. The script below was run end to end in a fresh `debian:bookworm` container while writing this course (Python 3.11.2 from apt, Docker 29 on a WSL2 kernel). Every output in this lesson is copied from that run. It needs internet access for apt and PyPI.

## Shortcut: the ready-made script

Download `lab1-break-env.sh` from this lesson's Resources, then from the folder that holds it:

```bash
docker run --rm -it -v "$PWD":/lab debian:bookworm bash /lab/lab1-break-env.sh
```

Windows PowerShell users: run `docker run --rm -it -v "${PWD}:/lab" debian:bookworm bash /lab/lab1-break-env.sh` instead, because `"$PWD":/lab` splits into two arguments in PowerShell and Docker then fails with "invalid reference format".

It installs `python3`, `python3-pip`, `python3-venv` and `python3-yaml` from apt, then prints each command and its output under a heading. To poke around yourself, start a shell instead (`docker run --rm -it -v "$PWD":/lab debian:bookworm bash`) and run the script's commands one at a time.

## Break 1: PEP 668

```text
$ pip install requests
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
```

The evidence is the marker file in the standard-library directory. [1]

```text
$ sed -n 1,3p /usr/lib/python3.11/EXTERNALLY-MANAGED
[externally-managed]
Error=To install Python packages system-wide, try apt install
 python3-xyz, where xyz is the package you are trying to
```

**Fix:** create a venv and install there. Inside a venv the marker does not apply. [1]

```text
$ python3 -m venv /opt/app/.venv
$ /opt/app/.venv/bin/python -m pip install -q requests
$ /opt/app/.venv/bin/python -c 'import requests; print("requests", requests.__version__)'
requests 2.34.2
```

Your version number will differ; it is whatever PyPI had that day.

## Break 2: the wrong interpreter

`/opt/app/main.py` imports `requests`. Running it the "normal" way fails:

```text
$ cd /opt/app && python3 main.py
ModuleNotFoundError: No module named 'requests'
$ python3 -c 'import sys; print(sys.executable, sys.prefix == sys.base_prefix)'
/usr/bin/python3 True
```

`sys.prefix == sys.base_prefix` is `True`, so this is not a venv interpreter. [2] The package is installed, just not where this interpreter looks.

**Fix:** run the venv's interpreter by path, or activate the venv so that `python` resolves to it. [2]

```text
$ .venv/bin/python main.py
ok 2.34.2
$ . /opt/app/.venv/bin/activate && command -v python
/opt/app/.venv/bin/python
```

In production (systemd units, cron, Dockerfiles) use the full path. Activation is a shell convenience.

## Break 3: the system site-packages leak

`config.py` imports `yaml`, but nobody declared PyYAML as a dependency. In a venv made with `--system-site-packages` it still works:

```text
$ python3 -m venv --system-site-packages /opt/leaky
$ grep include-system /opt/leaky/pyvenv.cfg
include-system-site-packages = true
$ /opt/leaky/bin/python /opt/app/config.py
yaml 6.0 from /usr/lib/python3/dist-packages/yaml/__init__.py
```

The path gives it away: the module came from Debian's `dist-packages`, installed by apt as `python3-yaml`. [4] `pip list` even shows `PyYAML 6.0`, which makes the leak easy to miss. The day this code runs in a clean container, it fails.

**Fix:** switch the leak off, see the real gap, and declare the dependency. With the key set to anything but `true`, `site` stops searching the system prefixes. [3]

```text
$ sed -i 's/^include-system-site-packages = true/include-system-site-packages = false/' /opt/leaky/pyvenv.cfg
$ /opt/leaky/bin/python /opt/app/config.py
ModuleNotFoundError: No module named 'yaml'
$ /opt/leaky/bin/python -m pip install -q pyyaml && /opt/leaky/bin/python /opt/app/config.py
yaml 6.0.3 from /opt/leaky/lib/python3.11/site-packages/yaml/__init__.py
```

Editing `pyvenv.cfg` is fine for a demonstration. In real work, recreate the venv without the flag. Venvs are disposable. [2]

## Compare the two search paths

```text
$ python3 -m site            # system
    '/usr/local/lib/python3.11/dist-packages',
    '/usr/lib/python3/dist-packages',
$ /opt/app/.venv/bin/python -m site
    '/opt/app/.venv/lib/python3.11/site-packages',
```

Only the tail of each list is shown. The standard library entries are the same in both.

## Gotchas

- **Reaching for the override.** On `error: externally-managed-environment`, the tempting fix is `--break-system-packages`. The marker exists because the system interpreter is apt's; the fix is a venv, where the marker does not apply. [1]
- **Trusting "pip says it's installed".** `ModuleNotFoundError` right after a successful install means the code ran on another interpreter. `sys.executable` and `sys.prefix == sys.base_prefix` printing `True` give it away; run `.venv/bin/python` instead. [2]
- **Relying on activation in production.** Activation only changes your shell's `PATH`. A systemd unit, cron job or Dockerfile never sees it, so write the venv interpreter's full path there. [2]
- **Believing `pip list`.** In a `--system-site-packages` venv, `pip list` showed `PyYAML 6.0`, but it was apt's copy. Print the module's `__file__`: a path under `/usr/lib/python3/dist-packages` means a leak. [4]
- **Patching instead of recreating.** Flipping `include-system-site-packages` in `pyvenv.cfg` shows the gap, because `site` then stops searching the system prefixes [3]. For real work, delete the venv and recreate it without the flag. [2]

## Check yourself

- In break 2, what would `command -v python3` print inside the activated venv, and why does `python3 main.py` then work?
- Recreate `/opt/leaky` without `--system-site-packages` instead of editing the file. What does `pip list` show now?

:::key-takeaways
- `error: externally-managed-environment` comes from the `EXTERNALLY-MANAGED` file; the fix is a venv, not `--break-system-packages`. [1]
- `ModuleNotFoundError` for an installed package usually means the wrong interpreter: check `sys.executable` and `sys.prefix`. [2]
- `--system-site-packages` lets apt-installed modules hide missing dependencies; the module's file path reveals the leak. [3] [4]
:::

:::glossary
- **Lab**: a hands-on exercise you run on your own machine.
- **Container**: an isolated process tree with its own filesystem, here started from the `debian:bookworm` image.
- **bookworm**: the code name of Debian 12.
- **`ModuleNotFoundError`**: the error Python raises when no directory on `sys.path` has the module.
- **PyYAML**: the Python library that provides the `yaml` module.
- **Leak**: a dependency that works by accident because it comes from outside the environment.
:::
