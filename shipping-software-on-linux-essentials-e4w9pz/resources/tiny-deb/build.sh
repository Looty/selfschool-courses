#!/usr/bin/env bash
# Build the hello-ship .deb with dpkg-deb. Run inside a Debian container from the resources folder:
#   docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh          # builds 1.0-1
#   docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/build.sh 1.0-2    # builds a newer revision
# The .deb files land in tiny-deb/dist/.
set -euo pipefail
VERSION="${1:-1.0-1}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mktemp -d)"

# Copy the tree so permissions are correct even when the source is on a Windows or macOS mount.
cp -r "$HERE/hello-ship" "$WORK/hello-ship"
cd "$WORK"
find hello-ship -type d -exec chmod 0755 {} +
find hello-ship -type f -exec chmod 0644 {} +
chmod 0755 hello-ship/DEBIAN/postinst hello-ship/usr/bin/hello-ship
sed -i "s/^Version: .*/Version: ${VERSION}/" hello-ship/DEBIAN/control

mkdir -p "$HERE/dist"
OUT="$HERE/dist/hello-ship_${VERSION}_all.deb"
dpkg-deb --root-owner-group --build hello-ship "$OUT"

echo "--- ar members (the .deb is an ar archive)"
if ! command -v ar >/dev/null; then
  # ar ships in binutils, which the slim Debian image does not include.
  (apt-get update -qq && apt-get install -y -qq binutils) >/dev/null 2>&1
fi
ar t "$OUT"
echo "--- dpkg-deb --info"
dpkg-deb --info "$OUT"
echo "--- dpkg-deb --contents"
dpkg-deb --contents "$OUT"
