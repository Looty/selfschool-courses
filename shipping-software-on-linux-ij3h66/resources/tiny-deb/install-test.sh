#!/usr/bin/env bash
# Install, upgrade, remove and purge hello-ship in a clean container. Build 1.0-1 and 1.0-2 first (see build.sh), then:
#   docker run --rm -v "$PWD":/lab -w /lab debian:bookworm bash tiny-deb/install-test.sh
set -euo pipefail
DIST="$(cd "$(dirname "$0")" && pwd)/dist"
run() { printf '\n$ %s\n' "$*"; bash -c "$*"; }

apt-get update -qq >/dev/null

run "apt-get install -y -qq $DIST/hello-ship_1.0-1_all.deb 2>&1 | grep -E 'Setting up|postinst'"
run "hello-ship"
run "dpkg -l hello-ship | tail -n 1"
run "dpkg -L hello-ship"

echo; echo "--- edit the conffile, then upgrade to 1.0-2"
sed -i 's/^GREETING=.*/GREETING="hi, edited locally"/' /etc/hello-ship.conf
run "dpkg --compare-versions 1.0-2 gt 1.0-1 && echo '1.0-2 is newer than 1.0-1'"
run "apt-get install -y -qq -o Dpkg::Options::=--force-confold $DIST/hello-ship_1.0-2_all.deb 2>&1 | grep -E 'Setting up|postinst'"
run "hello-ship"

echo; echo "--- remove keeps the conffile (state rc), purge deletes it"
run "apt-get remove -y -qq hello-ship >/dev/null 2>&1; dpkg -l hello-ship | tail -n 1; ls -l /etc/hello-ship.conf"
run "apt-get purge -y -qq hello-ship >/dev/null 2>&1; dpkg -l hello-ship 2>&1 | tail -n 1; ls /etc/hello-ship.conf 2>&1 || true"
