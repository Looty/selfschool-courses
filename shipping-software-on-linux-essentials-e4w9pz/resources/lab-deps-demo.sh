#!/usr/bin/env bash
# Chapter 03 demo: locks, hashes, resolver conflicts, pip check and pipdeptree, on real packages.
# Run from the resources folder (needs internet access to PyPI):
#   docker run --rm -it -v "$PWD":/lab -w /lab python:3.12-slim-bookworm bash lab-deps-demo.sh
set -uo pipefail
export PIP_DISABLE_PIP_VERSION_CHECK=1
step() { printf '\n========== %s ==========\n' "$*"; }
run()  { printf '$ %s\n' "$*"; bash -c "$*"; printf '(exit code %s)\n' "$?"; }

python -m venv /opt/tools && /opt/tools/bin/pip install -q uv pip-tools pipdeptree
export PATH="/opt/tools/bin:$PATH"
rm -rf /tmp/proj && cp -r /lab/lab2-devenv /tmp/proj && cd /tmp/proj

step "uv: lock the project, then catch a stale lock in CI"
run "uv lock 2>&1 | tail -n 1"
run "grep -A3 '^name = \"packaging\"' uv.lock"
sed -i 's/"packaging>=23",/"packaging>=23",\n    "click>=8",/' pyproject.toml
run "uv sync --locked 2>&1 | tail -n 3"
run "uv lock 2>&1 | tail -n 1 && uv sync --locked 2>&1 | tail -n 1"

step "pip-tools: a pinned, hashed requirements file from pyproject.toml"
run "pip-compile -q --generate-hashes -o requirements.txt pyproject.toml && sed -n '1,14p' requirements.txt"

step "Hash-checking mode refuses an unpinned or unhashed line"
python -m venv /tmp/h
printf 'packaging==26.3 --hash=sha256:%064d\n' 0 > /tmp/bad-hash.txt
run "/tmp/h/bin/pip install -q -r /tmp/bad-hash.txt 2>&1 | tail -n 4"
printf 'click\n' > /tmp/unpinned.txt
run "/tmp/h/bin/pip install -q --require-hashes -r /tmp/unpinned.txt 2>&1 | tail -n 3"

step "A resolver conflict, read line by line"
python -m venv /tmp/c
run "/tmp/c/bin/pip install 'requests==2.32.3' 'urllib3<1.21' 2>&1 | grep -v -e '^Collecting' -e 'Downloading' | tail -n 12"

step "A broken environment that pip check and pipdeptree catch"
run "/tmp/c/bin/pip install -q 'requests==2.32.3' && /tmp/c/bin/pip install -q --no-deps 'urllib3==1.20' 2>&1 | tail -n 2"
run "/tmp/c/bin/pip check"
run "pipdeptree --python /tmp/c/bin/python -p requests 2>&1 | head -n 8"
run "pipdeptree --python /tmp/c/bin/python --reverse --packages urllib3 2>&1 | head -n 4"
