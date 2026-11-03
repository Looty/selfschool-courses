#!/usr/bin/env bash
# Lab 3: package the devenv CLI as a .deb, publish it in a signed apt repository, install it in a clean
# container, then ship a hotfix of that one package. Run on your host (Linux, macOS, or Git Bash on Windows)
# from the resources folder; needs Docker and internet access once:
#   bash lab3/lab3-run.sh
# Everything is built inside containers. Nothing is written to your checkout; the repository lives in a
# Docker volume that the script deletes at the end.
set -euo pipefail
export MSYS_NO_PATHCONV=1                       # keep Git Bash on Windows from rewriting paths
HERE="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$HERE"; command -v cygpath >/dev/null && SRC="$(cygpath -w "$HERE")"
NET=shiplab-net VOL=shiplab-repo GNUPG=shiplab-gnupg
say() { printf '\n$ %s\n' "$*"; }
cleanup() { docker rm -f shiplab-repo-http >/dev/null 2>&1 || true
            docker network rm "$NET" >/dev/null 2>&1 || true
            docker volume rm "$VOL" "$GNUPG" >/dev/null 2>&1 || true; }
trap cleanup EXIT
cleanup
docker network create "$NET" >/dev/null
docker volume create "$VOL" >/dev/null; docker volume create "$GNUPG" >/dev/null

builder() { docker run --rm -v "$SRC":/lab:ro -v "$VOL":/repo -v "$GNUPG":/root/.gnupg debian:bookworm \
              bash /lab/lab3/build-deb.sh "$@"; }

echo "== 1. Build 0.1.0-1 and publish it to a signed reprepro repository"
builder init
builder build 0.1.0 1

echo; echo "== 2. Serve the repository over HTTP"
docker run -d --name shiplab-repo-http --network "$NET" -v "$VOL":/repo:ro -w /repo \
  python:3.12-slim-bookworm python -m http.server 8000 >/dev/null
sleep 2
docker run --rm -v "$VOL":/repo:ro debian:bookworm bash -c 'ls /repo/dists/stable; head -n 8 /repo/dists/stable/InRelease'

echo; echo "== 3. A clean client: trust the key, add the source, install the suite"
docker run -d --name shiplab-client --network "$NET" -v "$VOL":/repo:ro debian:bookworm sleep 3600 >/dev/null
trap 'docker rm -f shiplab-client >/dev/null 2>&1 || true; cleanup' EXIT
client() { say "$*"; docker exec shiplab-client bash -c "$*"; }
client "install -m 0644 /repo/shiplab-archive-keyring.gpg /usr/share/keyrings/shiplab-archive-keyring.gpg"
client "printf 'Types: deb\nURIs: http://shiplab-repo-http:8000/\nSuites: stable\nComponents: main\nSigned-By: /usr/share/keyrings/shiplab-archive-keyring.gpg\n' > /etc/apt/sources.list.d/shiplab.sources && cat /etc/apt/sources.list.d/shiplab.sources"
client "apt-get update 2>&1 | grep -i shiplab"
client "apt-get install -y -qq shiplab-suite 2>&1 | grep -E '^Setting up (shiplab|python3 )'"
client "apt-cache show shiplab-devenv | grep -E '^(Version|Depends):'"
client "devenv --version && devenv doctor | head -n 5"
client "apt-cache policy shiplab-devenv | head -n 6"

echo; echo "== 4. Hotfix: rebuild only shiplab-devenv as 0.1.1-1 and publish it"
builder hotfix 0.1.1 1

echo; echo "== 5. The client upgrades just that package"
client "apt-get update -qq && apt list --upgradable 2>/dev/null | grep shiplab"
client "apt-get install -y -qq --only-upgrade shiplab-devenv 2>&1 | grep -E '^(Setting up|Unpacking)'"
client "devenv --version; dpkg-query -W 'shiplab-*'"

echo; echo "== 6. What an unsigned or wrongly signed repository looks like"
client "sed -i 's#^Signed-By: .*#Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg#' /etc/apt/sources.list.d/shiplab.sources && apt-get update 2>&1 | grep -E '^(W|E):' | head -n 3"
