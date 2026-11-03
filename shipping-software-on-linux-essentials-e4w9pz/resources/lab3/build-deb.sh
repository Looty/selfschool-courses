#!/usr/bin/env bash
# Runs inside the builder container. Builds the shiplab-devenv .deb (a bundled venv under /opt) and the
# shiplab-suite meta-package, then adds them to the reprepro repository in /repo.
#   build-deb.sh init                   # create the GPG key and the reprepro config
#   build-deb.sh build 0.1.0 1          # build shiplab-devenv 0.1.0-1 and shiplab-suite, publish both
#   build-deb.sh hotfix 0.1.1 1         # rebuild only shiplab-devenv at a new version, publish it
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
REPO=/repo
APP=/opt/shiplab-devenv          # venvs are not relocatable: build at the install path

prepare_tools() {
  apt-get update -qq >/dev/null
  apt-get install -y -qq python3 python3-venv reprepro gnupg >/dev/null 2>&1
  chmod 700 /root/.gnupg
}

init() {
  prepare_tools
  mkdir -p "$REPO/conf"
  gpg --batch --passphrase '' --quick-gen-key "Shiplab Lab Repository <repo@example.invalid>" ed25519 sign never 2>/dev/null
  KEYID=$(gpg --list-keys --with-colons | awk -F: '/^fpr/ {print $10; exit}')
  cat > "$REPO/conf/distributions" <<EOF
Origin: shiplab
Label: shiplab
Codename: stable
Architectures: amd64 arm64
Components: main
Description: Course lab repository
SignWith: $KEYID
EOF
  gpg --export > "$REPO/shiplab-archive-keyring.gpg"
  echo "repository initialised, signing key $KEYID"
}

build_devenv() {
  local version=$1 rev=$2 src=/tmp/src stage=/tmp/stage-devenv
  rm -rf "$src" "$stage" "$APP"
  cp -r /lab/lab2-devenv "$src"
  sed -i "s/^version = .*/version = \"$version\"/" "$src/pyproject.toml"
  python3 -m venv "$APP"
  "$APP/bin/pip" install -q "$src"
  mkdir -p "$stage/DEBIAN" "$stage/opt" "$stage/usr/bin"
  cp -a "$APP" "$stage/opt/"
  ln -s /opt/shiplab-devenv/bin/devenv "$stage/usr/bin/devenv"
  # The venv's bin/python is a symlink to the /usr/bin/python3 it was built with, so depend on that
  # exact minor version of the python3 package (a newer minor would leave the venv's packages behind).
  local pyver next
  pyver=$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
  next=$(python3 -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1] + 1}")')
  cat > "$stage/DEBIAN/control" <<EOF
Package: shiplab-devenv
Version: ${version}-${rev}
Architecture: all
Maintainer: Course Lab <lab@example.invalid>
Depends: python3 (>= ${pyver}), python3 (<< ${next})
Section: devel
Priority: optional
Description: devenv developer CLI with its own bundled virtualenv
 Installs the devenv command. The Python dependencies live in a virtual
 environment under /opt/shiplab-devenv, built against /usr/bin/python3 ${pyver}.
EOF
  dpkg-deb --root-owner-group --build "$stage" "/tmp/shiplab-devenv_${version}-${rev}_all.deb" >/dev/null
  reprepro -b "$REPO" includedeb stable "/tmp/shiplab-devenv_${version}-${rev}_all.deb"
}

build_suite() {
  local stage=/tmp/stage-suite
  rm -rf "$stage" && mkdir -p "$stage/DEBIAN" "$stage/usr/share/doc/shiplab-suite"
  echo "shiplab product meta-package" > "$stage/usr/share/doc/shiplab-suite/README"
  cat > "$stage/DEBIAN/control" <<EOF
Package: shiplab-suite
Version: 1.0-1
Architecture: all
Maintainer: Course Lab <lab@example.invalid>
Depends: shiplab-devenv (>= 0.1.0-1), shiplab-devenv (<< 0.2)
Section: metapackages
Priority: optional
Description: the whole lab product
 Pulls in every component at a compatible version range.
EOF
  dpkg-deb --root-owner-group --build "$stage" /tmp/shiplab-suite_1.0-1_all.deb >/dev/null
  reprepro -b "$REPO" includedeb stable /tmp/shiplab-suite_1.0-1_all.deb
}

case ${1:-} in
  init) init;;
  build) prepare_tools; gpg --list-keys >/dev/null; build_devenv "$2" "$3"; build_suite;;
  hotfix) prepare_tools; build_devenv "$2" "$3";;
  *) echo "usage: $0 init | build VERSION REV | hotfix VERSION REV"; exit 2;;
esac
reprepro -b "$REPO" list stable 2>/dev/null || true
