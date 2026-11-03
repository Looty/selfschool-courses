#!/usr/bin/env bash
# Lab 2: build the devenv CLI (distribution name shiplab-devenv), publish it to a local pypiserver index,
# install it with pipx from that index only, then publish 0.1.1 and upgrade. Run from the resources folder:
#   docker run --rm -it -v "$PWD":/lab -w /lab python:3.12-slim-bookworm bash lab2-run.sh
# Needs internet access to reach PyPI for the tools (build, twine, pypiserver, pipx) and to mirror `packaging`.
set -euo pipefail
step() { printf '\n========== %s ==========\n' "$*"; }
run()  { printf '$ %s\n' "$*"; bash -c "$*"; }

WORK=/tmp/devenv
rm -rf "$WORK" && cp -r /lab/lab2-devenv "$WORK"
cd "$WORK"
LOCAL=http://localhost:8080/simple/

step "Tools in their own venv"
python -m venv /opt/tools
/opt/tools/bin/python -m pip install -q build twine pypiserver pipx
export PATH="/opt/tools/bin:/root/.local/bin:$PATH"
run "python -m build --version"

step "Build the sdist and the wheel"
run "python -m build 2>&1 | tail -n 1"
run "ls dist/"

step "Look inside the wheel"
run "python -m zipfile -l dist/shiplab_devenv-0.1.0-py3-none-any.whl"
run "python -m zipfile -e dist/shiplab_devenv-0.1.0-py3-none-any.whl /tmp/whl && cat /tmp/whl/shiplab_devenv-0.1.0.dist-info/entry_points.txt"
run "grep -E '^(Name|Version|Requires-Dist|Requires-Python):' /tmp/whl/shiplab_devenv-0.1.0.dist-info/METADATA"

step "Start a local index (pypiserver, no auth, no PyPI fallback) and upload with twine"
mkdir -p /srv/packages
# --disable-fallback: by default pypiserver redirects names it does not have to PyPI.
pypi-server run -p 8080 -a . -P . --disable-fallback /srv/packages >/tmp/pypiserver.log 2>&1 &
sleep 3
run "twine upload --repository-url http://localhost:8080/ -u lab -p lab dist/* >/dev/null 2>&1 && echo uploaded"
# Mirror the one runtime dependency, plus pip itself (pipx refreshes its shared pip from the same index),
# so installs need the local index only.
run "pip download -q 'packaging>=23' pip --only-binary :all: -d /srv/packages && ls /srv/packages"
run "pip index versions shiplab-devenv --index-url $LOCAL 2>/dev/null"

step "Install the CLI with pipx from the local index only"
run "pipx install shiplab-devenv --index-url $LOCAL 2>&1 | tail -n 3"
run "devenv doctor"
run "devenv compare 1.0rc1 1.0"
run "devenv compare 1.0.post1 1.0"

step "Ship 0.1.1 and upgrade"
sed -i 's/^version = "0.1.0"/version = "0.1.1"/' pyproject.toml
run "python -m build --wheel 2>&1 | tail -n 1"
run "twine upload --repository-url http://localhost:8080/ -u lab -p lab dist/shiplab_devenv-0.1.1-py3-none-any.whl >/dev/null 2>&1 && echo uploaded"
run "pipx upgrade shiplab-devenv >/dev/null 2>&1; devenv --version"

step "Dependency confusion, observed safely: a public name that clashes"
# Suppose the internal package had been called plain 'devenv'. A different, unrelated 'devenv' exists on PyPI.
# Publish a copy of our wheel under that name locally, then ask pip which versions it can see.
# `pip index versions` lists versions without downloading or installing anything.
mkdir -p /tmp/clash && cd /tmp/clash && cp -r /lab/lab2-devenv src && cd src
sed -i 's/^name = "shiplab-devenv"/name = "devenv"/; s/^version = .*/version = "0.0.9"/' pyproject.toml
python -m build --wheel >/dev/null 2>&1
twine upload --repository-url http://localhost:8080/ -u lab -p lab dist/devenv-0.0.9-py3-none-any.whl >/dev/null 2>&1
cd /tmp
run "pip index versions devenv --index-url $LOCAL 2>&1 | head -n 2"
run "pip index versions devenv --index-url $LOCAL --extra-index-url https://pypi.org/simple/ 2>&1 | head -n 2"
# A pypiserver left on its default settings redirects unknown names to PyPI as well.
mkdir -p /srv/empty
pypi-server run -p 8081 -a . -P . /srv/empty >/tmp/pypiserver-fallback.log 2>&1 &
sleep 3
run "pip index versions devenv --index-url http://localhost:8081/simple/ 2>&1 | head -n 2"
