#!/usr/bin/env bash
# Lab 4: five broken apt/dpkg scenarios, each with a break, a diagnosis, a solution and a reset.
# Run inside a fresh Debian container, from the resources folder:
#   docker run --rm -it -v "$PWD":/lab -w /lab debian:bookworm bash
#   bash lab4-apt-scenarios.sh setup        # build the lab packages and a local apt repo (needs internet once)
#   bash lab4-apt-scenarios.sh break 1      # then diagnose it yourself
#   bash lab4-apt-scenarios.sh solve 1      # the reference solution
#   bash lab4-apt-scenarios.sh reset 1      # back to a clean state
#   bash lab4-apt-scenarios.sh all          # every scenario: break, diagnose, solve (the run used for the lesson)
set -uo pipefail
export DEBIAN_FRONTEND=noninteractive
REPO=/srv/lab4-repo
PKGS=/tmp/lab4-pkgs
say() { printf '\n$ %s\n' "$*"; bash -c "$*"; }
hdr() { printf '\n==================== %s ====================\n' "$*"; }

# mkdeb NAME VERSION "control extra lines" [postinst body] [file-to-ship]
mkdeb() {
  local name=$1 ver=$2 extra=$3 postinst=${4:-} file=${5:-/usr/share/$1/README}
  local d="$PKGS/build/${name}_${ver}"
  rm -rf "$d" && mkdir -p "$d/DEBIAN" "$d$(dirname "$file")"
  printf 'Package: %s\nVersion: %s\nArchitecture: all\nMaintainer: Lab <lab@example.invalid>\n%bDescription: Lab 4 package %s\n' \
    "$name" "$ver" "$extra" "$name" > "$d/DEBIAN/control"
  echo "$name $ver" > "$d$file"
  if [ -n "$postinst" ]; then
    printf '#!/bin/sh\nset -e\n%s\nexit 0\n' "$postinst" > "$d/DEBIAN/postinst"
    chmod 0755 "$d/DEBIAN/postinst"
  fi
  dpkg-deb --root-owner-group --build "$d" "$PKGS/${name}_${ver}_all.deb" >/dev/null
}

setup() {
  apt-get update -qq >/dev/null
  apt-get install -y -qq apt-utils >/dev/null 2>&1
  mkdir -p "$PKGS" "$REPO"
  # 1: depends on a real Debian package that is not installed yet
  mkdeb needs-jq 1.0-1 'Depends: jq\n'
  # 2: postinst fails unless /etc/lab4/ready exists
  mkdeb flaky-svc 1.0-1 '' 'if [ ! -f /etc/lab4/ready ]; then echo "flaky-svc: /etc/lab4/ready missing" >&2; exit 1; fi'
  # 3: two packages ship the same file; 2.0-1 of the second one declares Breaks + Replaces
  mkdeb tool-a 1.0-1 '' '' /usr/bin/lab4-tool
  mkdeb tool-b 1.0-1 '' '' /usr/bin/lab4-tool
  mkdeb tool-b 2.0-1 'Breaks: tool-a (<< 1.1)\nReplaces: tool-a (<< 1.1)\n' '' /usr/bin/lab4-tool
  mkdeb tool-a 1.1-1 ''   # the file moved to tool-b, so tool-a 1.1 no longer ships it
  # 4 and 5: a library with two versions and an app that needs the newer one, served from a local repo
  mkdeb libdemo 1.0-1 ''
  mkdeb libdemo 1.0-2 ''
  mkdeb demo-app 1.0-1 'Depends: libdemo (>= 1.0-2)\n'
  cp "$PKGS"/libdemo_*.deb "$PKGS"/demo-app_*.deb "$REPO"/
  (cd "$REPO" && apt-ftparchive packages . > Packages && apt-ftparchive release . > Release)
  echo "deb [trusted=yes] file:$REPO ./" > /etc/apt/sources.list.d/lab4.list
  apt-get update -qq >/dev/null
  echo "setup done: packages in $PKGS, local repo in $REPO"
}

brk() {
  case $1 in
    1) say "dpkg -i $PKGS/needs-jq_1.0-1_all.deb 2>&1 | tail -n 4";;
    2) rm -f /etc/lab4/ready; say "dpkg -i $PKGS/flaky-svc_1.0-1_all.deb 2>&1 | tail -n 5";;
    3) say "dpkg -i $PKGS/tool-a_1.0-1_all.deb >/dev/null 2>&1; dpkg -i $PKGS/tool-b_1.0-1_all.deb 2>&1 | tail -n 6";;
    4) say "apt-get install -y -qq libdemo=1.0-1 >/dev/null 2>&1; apt-mark hold libdemo"
       say "apt-get install -y demo-app 2>&1 | tail -n 7";;
    5) say "apt-get install -y -qq libdemo=1.0-1 >/dev/null 2>&1; printf 'Package: libdemo\nPin: version 1.0-1\nPin-Priority: 1001\n' > /etc/apt/preferences.d/lab4-pin"
       say "apt-get install -y -qq --only-upgrade libdemo 2>&1 | tail -n 2; dpkg-query -W libdemo";;
  esac
}

diagnose() {
  case $1 in
    1) say "dpkg -l needs-jq | tail -n 1"; say "apt-get check 2>&1 | tail -n 4";;
    2) say "dpkg -l flaky-svc | tail -n 1"; say "dpkg --audit";;
    3) say "dpkg -S /usr/bin/lab4-tool"; say "dpkg -l 'tool-*' | tail -n 2";;
    4) say "apt-mark showhold"; say "apt-cache policy libdemo";;
    5) say "apt-cache policy libdemo"; say "grep -r . /etc/apt/preferences.d/";;
  esac
}

solve() {
  case $1 in
    1) say "apt-get -f install -y -qq 2>&1 | grep -E '^(Setting up|Correcting)' "; say "dpkg -l needs-jq | tail -n 1";;
    2) say "mkdir -p /etc/lab4 && touch /etc/lab4/ready && dpkg --configure -a 2>&1 | tail -n 2"; say "dpkg -l flaky-svc | tail -n 1";;
    3) say "dpkg -i $PKGS/tool-b_2.0-1_all.deb 2>&1 | grep -E 'breaks|deconfigur'"
       say "apt-get install -y -qq $PKGS/tool-a_1.1-1_all.deb $PKGS/tool-b_2.0-1_all.deb 2>&1 | grep -E '^(Setting up|Unpacking)'"
       say "dpkg -S /usr/bin/lab4-tool"; say "dpkg -l 'tool-*' | tail -n 2";;
    4) say "apt-mark unhold libdemo && apt-get install -y -qq demo-app 2>&1 | grep -E '^Setting up'";;
    5) say "rm /etc/apt/preferences.d/lab4-pin && apt-cache policy libdemo | head -n 3"
       say "apt-get install -y -qq --only-upgrade libdemo >/dev/null 2>&1; dpkg-query -W libdemo";;
  esac
}

reset() {
  rm -f /etc/apt/preferences.d/lab4-pin
  apt-mark unhold libdemo >/dev/null 2>&1 || true
  touch /etc/lab4/ready 2>/dev/null || { mkdir -p /etc/lab4 && touch /etc/lab4/ready; }
  dpkg --configure -a >/dev/null 2>&1 || true
  apt-get -f install -y -qq >/dev/null 2>&1 || true
  dpkg --purge needs-jq flaky-svc tool-a tool-b demo-app libdemo jq libjq1 libonig5 >/dev/null 2>&1 || true
  rm -rf /etc/lab4
  echo "reset done"
}

case ${1:-} in
  setup) setup;;
  break) brk "$2";;
  diagnose) diagnose "$2";;
  solve) solve "$2";;
  reset) reset;;
  all)
    setup
    for n in 1 2 3 4 5; do
      hdr "Scenario $n: break"; brk $n
      hdr "Scenario $n: diagnose"; diagnose $n
      hdr "Scenario $n: solve"; solve $n
      reset >/dev/null
    done;;
  *) echo "usage: $0 setup | break N | diagnose N | solve N | reset | all"; exit 2;;
esac
