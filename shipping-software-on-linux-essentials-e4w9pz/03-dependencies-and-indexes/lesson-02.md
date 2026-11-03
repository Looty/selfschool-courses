---
id: l06
title: "Private indexes and dependency confusion"
quiz: quiz-02.yaml
resources: [../resources/lab2-run.sh, ../resources/lab2-devenv/pyproject.toml, ../resources/lab2-devenv/src/devenv/cli.py, ../resources/lab2-devenv/src/devenv/__init__.py]
sources: [5, 6, 18, 22, 23, 24, 25, 26, 86]
---
After this lesson you can explain dependency confusion in terms of how pip and uv pick between indexes, configure pip, pipx and uv to use one private index safely, and publish internal packages from CI with twine.

## What an index is to pip

`--index-url` is the base URL of a package index and defaults to `https://pypi.org/simple`. It must follow the "simple repository API" (PEP 503) or be a local directory in the same layout. `--extra-index-url` adds more indexes. `--no-index` turns indexes off entirely and uses only `--find-links`, which can be a directory full of wheels. [23]

The rule that matters most: **"There is no priority in the locations that are searched."** pip checks every index and picks the best match. [23] For a version range, "best" means the highest version found on any index.

## Dependency confusion

Say your internal package is called `devenv`, it lives on a private index, and your machines use:

```bash
pip install devenv --index-url https://pypi.org/simple/ --extra-index-url https://pkgs.internal/simple/
```

Anyone can publish a package called `devenv` to PyPI. If theirs has a higher version, pip installs it. pip's own reference calls using `--extra-index-url` for private packages "unsafe" for this reason. [23]

In the course's test run, a small CLI was published to a local pypiserver as `devenv 0.0.9`; an unrelated `devenv` exists on PyPI. Port 8081 was a second, empty pypiserver on default settings:

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

With PyPI as an extra index, the public 0.1.1 wins, because pip does not rank indexes. [23] The third result is subtler: a pypiserver on default settings leaks the public package even with a single `--index-url`, because it redirects names it lacks to PyPI. [86] `pip index versions` only lists versions and installs nothing, so the check is safe. An earlier draft of the course's test hit the real thing: `pipx install devenv` with PyPI as an extra index installed the public package, hence the demo's real name, `shiplab-devenv`. The PyPI versions shown were current on 2026-11-02 and will change.

## Defences

| Defence | Why it works |
|---|---|
| One index only | Point `--index-url` at a private index that mirrors or proxies the public packages you approve; never add PyPI as an extra index. |
| Turn off proxy fallback | pypiserver by default redirects requests for packages it does not have to PyPI; `--disable-fallback` stops that. [86] |
| A tool with index priority | uv's default `first-index` strategy only takes a package's versions from the first index that has it. [22] |
| Hash-pin applications | A swapped package fails the hash check (previous lesson). |

An index without fallback must hold everything you install, so the test run mirrored its one dependency, `packaging`, rather than let PyPI back-fill it.

## uv: index strategies

uv does rank indexes. Its default `index-strategy` is `first-index`: for each package it only takes versions from the first index that has that package, which its docs say is to prevent dependency confusion. `unsafe-best-match`, the strategy closest to pip's behaviour, re-opens the risk. Marking an index `explicit = true` means it is only used for packages pinned to it. [22]

uv reads index credentials from environment variables named after the index, such as `UV_INDEX_INTERNAL_PROXY_USERNAME`, so they stay out of `pyproject.toml`. [22]

## Where the pip index setting lives

pip reads `pip.conf` from several places, and each later file overrides the earlier ones. The order is global (`/etc/xdg/pip/pip.conf`, then `/etc/pip.conf`), then user (`~/.config/pip/pip.conf`), then site (`$VIRTUAL_ENV/pip.conf`). Command-line options beat `PIP_*` environment variables, which beat the files. [24]

```ini
# /etc/pip.conf on a build host
[global]
index-url = https://pkgs.internal/simple/
```

Every option has an environment variable form, `PIP_<UPPER_LONG_NAME>`, such as `PIP_INDEX_URL`. `PIP_CONFIG_FILE` names a file loaded last, and pointing it at `/dev/null` disables all config files. `pip config debug` shows which files are in play. [24]

## pipx with a private index

pipx takes the same index flags as pip:

```bash
pipx install devenv --index-url http://localhost:8080/simple/
pipx install devenv --pip-args="--no-index --find-links /srv/wheels"
```

It records these options and passes them again on `pipx upgrade` and `pipx reinstall`. [6] Under the pip backend it forwards `PIP_*` environment variables to every pip call; the uv backend ignores them and needs uv's own variables, such as `UV_INDEX_URL`. [6] pipx refuses an empty index URL, so a variable that was never set cannot silently send you to PyPI. [6]

With the pip backend, every app's venv borrows one shared pip, and pipx refreshes it. [5] In the course's test run, against an index with fallback off, the first `pipx install` failed during that refresh: it asked the same `--index-url` for pip, and there was no pip wheel. Mirroring pip fixed it (the `devenv doctor` lines that followed are cut):

```text
$ pipx install shiplab-devenv --index-url http://localhost:8080/simple/
  installed package shiplab-devenv 0.1.0, installed using Python 3.12.16
  These apps are now available
    - devenv
```

A later `pipx upgrade shiplab-devenv` picked up 0.1.1 without `--index-url` being passed again. [6]

## Publishing with twine

`python -m build` produces an sdist and a wheel. [18] twine uploads them. `--repository-url` names the target directly and overrides `-r/--repository`, which names a section of `~/.pypirc`. In CI, credentials come from `TWINE_USERNAME` and `TWINE_PASSWORD`, and the URL can come from `TWINE_REPOSITORY_URL`. [26]
```bash
python -m build
twine upload --repository-url "$INDEX_UPLOAD_URL" dist/*
```

pypiserver accepts uploads by default, with authentication on `update`. `-a . -P .` disables authentication, which is fine for a throwaway test index and wrong anywhere else. [25]

## Gotchas

- **PyPI as `--extra-index-url`.** The public package with the higher version wins; `pip index versions <name>` shows it. Use one private index that mirrors approved packages. [23]
- **A proxy that falls back.** A default pypiserver redirects unknown names to PyPI, so even a single `--index-url` leaks public packages, as port 8081 showed above. Start it with `--disable-fallback`. [86]
- **`unsafe-best-match` in uv.** It behaves like pip, so a higher public version of an internal name wins again. Keep the default `first-index`. [22]
- **pipx's uv backend ignores `PIP_INDEX_URL`.** A pipx install does not use the index your `PIP_*` variables name; set `UV_INDEX_URL` for that backend. [6]
- **An offline index without pip.** With fallback off, `pipx install` fails while refreshing its shared pip. Mirror pip itself next to your dependencies. [5]
- **A config file you did not know about.** A `PIP_*` variable or a later file overrides `/etc/pip.conf`. Run `pip config debug`. [24]

## Check yourself

- Build agents set `PIP_INDEX_URL` to an internal pypiserver on default flags. Is an internal name exposed? Which flag changes that?

Optional, try it yourself: `../resources/lab2-run.sh` runs the whole flow (build, private index, pipx, the `pip index versions` check) in a `python:3.12-slim-bookworm` container.

:::key-takeaways
- pip treats all indexes equally and takes the best version, so `--extra-index-url` for private packages is unsafe. [23]
- pypiserver falls back to PyPI for unknown names unless started with `--disable-fallback`. [86]
- uv's default `first-index` strategy exists to prevent dependency confusion; `unsafe-best-match` re-opens it. [22]
- pip config precedence: CLI > `PIP_*` env > config files (global, then user, then site). [24]
- pipx remembers `--index-url` for upgrades and forwards `PIP_*` only under its pip backend. [6]
- twine takes the target from `--repository-url` or `.pypirc` and credentials from `TWINE_*` variables in CI. [26]
:::

:::glossary
- **Simple repository API**: the plain HTML (or JSON) listing of package files that pip reads from an index.
- **Dependency confusion**: a supply-chain attack where a public package with the same name as an internal one gets installed instead.
- **Fallback (proxy)**: an index forwarding requests it cannot serve to another index, often PyPI.
- **Mirror**: a copy of selected public packages on your own index.
- **Index strategy (uv)**: the rule uv uses to choose between indexes that offer the same package.
- **pypiserver**: a minimal PyPI-compatible index server.
- **twine**: the tool that uploads distributions to an index.
- **Shared pip (pipx)**: one pip installation that pipx links into every app's venv under its pip backend.
:::
