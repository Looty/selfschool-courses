---
id: l12
title: "Private indexes and dependency confusion"
quiz: quiz-03.yaml
resources: []
sources: [6, 22, 23, 24, 25, 26, 86]
---
After this lesson you can configure pip, pipx and uv to use a private index safely, explain dependency confusion in terms of how each tool picks between indexes, and publish from CI with twine.

## What an index is to pip

`--index-url` is the base URL of a package index and defaults to `https://pypi.org/simple`. It must follow the "simple repository API" (PEP 503) or be a local directory in the same layout. `--extra-index-url` adds more indexes. `--no-index` turns indexes off entirely and uses only `--find-links`, which can be a directory full of wheels. [23]

The rule that matters most: **"There is no priority in the locations that are searched."** pip checks every index and picks the best match for the requirement. [23] For a version range, "best" means the highest version found on any index.

## Dependency confusion

Say your internal package is called `devenv`, it lives on a private index, and your machines use:

```bash
pip install devenv --index-url https://pypi.org/simple/ --extra-index-url https://pkgs.internal/simple/
```

Anyone can publish a package called `devenv` to PyPI. If theirs has a higher version, pip installs it. pip's own reference calls using `--extra-index-url` for private packages "unsafe" for this reason: an attacker publishes a same-named package to the public index, and it may be chosen instead of yours. [23]

Lab 2 shows this with a real name clash, safely, without installing anything. A copy of the lab CLI was published locally as `devenv 0.0.9`. An unrelated `devenv` already exists on PyPI.

```text
$ pip index versions devenv --index-url http://localhost:8080/simple/
devenv (0.0.9)
Available versions: 0.0.9
$ pip index versions devenv --index-url http://localhost:8080/simple/ --extra-index-url https://pypi.org/simple/
devenv (0.1.1)
Available versions: 0.1.1, 0.1.0, 0.0.9
```

With the extra index, pip would choose the public 0.1.1. An earlier draft of the lab hit exactly this: `pipx install devenv` with PyPI as an extra index installed the public package. That is why the lab's distribution is named `shiplab-devenv`.

## Defences

1. **Use one index.** Point `--index-url` at a private index that also mirrors or proxies the public packages you approve, and never add PyPI as an extra index. Lab 2 mirrors its one dependency, `packaging`, into the local index for this reason.
2. **Know your proxy's fallback.** pypiserver, by default, redirects requests for packages it does not have to PyPI. `--disable-fallback` turns that off. [86] The lab showed the default in action: an empty pypiserver on port 8081 answered `pip index versions devenv` with PyPI's versions.
3. **Use a tool with index priority.** uv's default `index-strategy` is `first-index`: for each package it only takes versions from the first index that has that package. Its docs say this is to prevent dependency confusion. `unsafe-best-match`, the closest to pip's behaviour, re-opens the risk. [22] Marking an index `explicit = true` means it is only used for packages pinned to it. [22]
4. **Hash-pin applications** (lesson 10), so a swapped package fails the hash check.

## Where the index setting lives

pip reads `pip.conf` from several places, and each later file overrides the earlier ones. The order is global (`/etc/xdg/pip/pip.conf`, then `/etc/pip.conf`), then user (`~/.config/pip/pip.conf`), then site (`$VIRTUAL_ENV/pip.conf`). Command-line options beat `PIP_*` environment variables, which beat the files. [24] `PIP_CONFIG_FILE` names a file loaded last, and pointing it at `/dev/null` disables all config files. `pip config debug` shows which files are in play. [24]

```ini
# /etc/pip.conf on a build host
[global]
index-url = https://pkgs.internal/simple/
```

Every option has an environment variable form, `PIP_<UPPER_LONG_NAME>`, such as `PIP_INDEX_URL`. [24] pipx forwards `PIP_*` variables only under its pip backend. Its uv backend needs `UV_INDEX_URL` instead. [6] uv reads index credentials from variables named after the index, such as `UV_INDEX_INTERNAL_PROXY_USERNAME`, so they stay out of `pyproject.toml`. [22]

## Publishing with twine

twine uploads built distributions. `--repository-url` names the target directly and overrides `-r/--repository`, which names a section of `~/.pypirc`. In CI, credentials come from `TWINE_USERNAME` and `TWINE_PASSWORD`, and the URL can come from `TWINE_REPOSITORY_URL`. [26] twine's docs give verified HTTPS uploads as the main reason to use it over the old `setup.py upload`. [26] `twine check` verifies that the long description will render on PyPI. [26]

```bash
python -m build
twine upload --repository-url "$INDEX_UPLOAD_URL" dist/*
```

pypiserver accepts uploads by default with authentication on `update`. `-a . -P .` disables authentication, which is fine for a lab and wrong anywhere else. [25]

:::key-takeaways
- pip treats all indexes equally and takes the best version, so `--extra-index-url` for private packages is unsafe. [23]
- pypiserver falls back to PyPI for unknown names unless started with `--disable-fallback`. [86]
- uv's default `first-index` strategy exists to prevent dependency confusion. [22]
- pip config precedence: CLI > `PIP_*` env > config files (global, then user, then site). [24]
- twine uploads with `--repository-url` or `.pypirc` and takes credentials from `TWINE_*` variables in CI. [26]
:::

:::glossary
- **Simple repository API**: the plain HTML (or JSON) listing of package files that pip reads from an index.
- **Private index**: a package index your organisation runs for internal packages.
- **Dependency confusion**: a supply-chain attack where a public package with the same name as an internal one gets installed instead.
- **Fallback (proxy)**: an index forwarding requests it cannot serve to another index, often PyPI.
- **Mirror**: a copy of selected public packages on your own index.
- **twine**: the tool for uploading distributions to an index.
- **`.pypirc`**: a user config file that names upload repositories for twine.
:::
