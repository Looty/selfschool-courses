#!/usr/bin/env bash
# make_lab_repo.sh: build the Git recovery lab.
#
# Usage:  bash make_lab_repo.sh <lab-dir>
#
# Creates two repositories inside <lab-dir>:
#   <lab-dir>/repo        your working repository (start here)
#   <lab-dir>/remote.git  a bare repository that plays the shared server ("origin")
#
# The history is deterministic: fixed author, committer and dates, so the commit
# hashes in LAB_SOLUTIONS.md match the ones you get. Commits you make yourself
# during the lab get new hashes. Needs only git and Bash (tested with
# Git 2.55.0.windows.3 in Git Bash).
set -euo pipefail

if [ $# -ne 1 ]; then
    echo "usage: bash make_lab_repo.sh <lab-dir>" >&2
    exit 2
fi

lab=$1
if [ -e "$lab" ] && [ -n "$(ls -A "$lab" 2>/dev/null)" ]; then
    echo "refusing to build into non-empty directory: $lab" >&2
    exit 2
fi
mkdir -p "$lab"
lab=$(cd "$lab" && pwd)

# Fixed identity and clock for every commit the script makes.
export GIT_AUTHOR_NAME="Lab User" GIT_AUTHOR_EMAIL="lab@example.com"
export GIT_COMMITTER_NAME="Lab User" GIT_COMMITTER_EMAIL="lab@example.com"
base=1767600000   # 2026-01-05 08:00 UTC
n=0
tick() {
    n=$((n + 1))
    export GIT_AUTHOR_DATE="$((base + n * 3600)) +0000"
    export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
}
commit() {
    tick
    git add -A
    git commit -q -m "$1"
}

git init -q --bare -b main "$lab/remote.git"
git init -q -b main "$lab/repo"
cd "$lab/repo" || exit 1

git config user.name "Lab User"
git config user.email "lab@example.com"
git config core.autocrlf false
git config commit.gpgsign false
git remote add origin "$lab/remote.git"

mkdir -p lib tests config

# ---------------------------------------------------------------- C0, v1.0
cat > README.md <<'EOF'
# vmtools

Small shell helpers for a self-service VM platform.

## Commands

- `to_mib`: convert a size such as 2G to MiB
EOF

cat > lib/size.sh <<'EOF'
# size.sh: convert human sizes such as 512M or 2G to MiB.
to_mib() {
    value=${1%[MG]}
    unit=${1#"$value"}
    case $unit in
        M) echo "$value" ;;
        G) echo $((value * 1024)) ;;
        *) echo "unknown unit: $1" >&2; return 1 ;;
    esac
}
EOF

cat > tests/run.sh <<'EOF'
#!/bin/sh
# Exit 0 when every check passes, 1 on the first failure (git bisect run reads this).
cd "$(dirname "$0")/.." || exit 1
. ./lib/size.sh
check() {
    got=$(to_mib "$1")
    if [ "$got" != "$2" ]; then
        echo "FAIL: to_mib $1 gave $got, expected $2"
        exit 1
    fi
}
check 512M 512
check 2G 2048
echo "all checks passed"
EOF

cat > config/defaults.env <<'EOF'
REGION=dc1
DEFAULT_FLAVOUR=small
EOF

cat > NOTES.md <<'EOF'
# Notes

- [x] Size helper
EOF

commit "Initial import"
git tag v1.0

# ---------------------------------------------------------------- C1, C2
cat >> lib/size.sh <<'EOF'

to_gib() {
    mib=$(to_mib "$1") || return 1
    echo $((mib / 1024))
}
EOF
commit "Add to_gib helper"

cat > CONTRIBUTING.md <<'EOF'
# Contributing

Run `sh tests/run.sh` before you push. Reviews recieve an answer within a day.
EOF
commit "Add contributing guide"
c2=$(git rev-parse HEAD)

# ---------------------------------------------------------------- release branch (pushed)
git switch -q -c release v1.0
cat > config/defaults.env <<'EOF'
REGION=dc1
DEFAULT_FLAVOUR=medium
EOF
commit "Prepare release 1.1"
cat > config/defaults.env <<'EOF'
REGION=dc-test
DEFAULT_FLAVOUR=medium
EOF
commit "Switch default region to dc-test"

# ---------------------------------------------------------------- feature/report and docs (task 1)
git switch -q -c feature/report "$c2"
cat > lib/report.sh <<'EOF'
# report.sh: print one line per VM.
report() {
    printf '%s\t%s\n' "$1" "$2"
}
EOF
commit "Add report command"

git switch -q -c docs "$c2"
cat > CONTRIBUTING.md <<'EOF'
# Contributing

Run `sh tests/run.sh` before you push. Reviews receive an answer within a day.
EOF
commit "Fix typo in contributing guide"
cat > lib/report_json.sh <<'EOF'
# report_json.sh: print one JSON object per VM.
report_json() {
    printf '{"name": "%s", "state": "%s"}\n' "$1" "$2"
}
EOF
commit "Add JSON output for report"

# ---------------------------------------------------------------- experiment (task 2: lost commit)
git switch -q -c experiment "$c2"
cat > lib/retry.sh <<'EOF'
# retry.sh: run a command up to N times.
retry() {
    tries=$1; shift
    i=1
    while [ "$i" -le "$tries" ]; do
        "$@" && return 0
        sleep 1
        i=$((i + 1))
    done
    return 1
}
EOF
commit "Add retry helper"
cat > lib/retry.sh <<'EOF'
# retry.sh: run a command up to N times, doubling the wait each time.
retry() {
    tries=$1; shift
    i=1
    wait=1
    while [ "$i" -le "$tries" ]; do
        "$@" && return 0
        sleep "$wait"
        wait=$((wait * 2))
        i=$((i + 1))
    done
    return 1
}
EOF
commit "Tune retry backoff"
# The accident: a hard reset throws the newest commit off the branch.
tick
git reset -q --hard HEAD~1

# ---------------------------------------------------------------- main C3 and feature/quota (task 5)
git switch -q main
cat > README.md <<'EOF'
# vmtools

Small shell helpers for a self-service VM platform.

## Usage

Source the files under `lib/` from your shell scripts.

## Commands

- `to_mib`: convert a size such as 2G to MiB
EOF
commit "Add usage section to README"

git switch -q -c feature/quota
cat > lib/quota.sh <<'EOF'
# quota.sh: VMs allowed per team.
quota() {
    echo 10
}
EOF
cat >> README.md <<'EOF'
- `quota`: show how many VMs a team may run
EOF
commit "Add quota command"
mkdir -p docs
cat > docs/quota.md <<'EOF'
# Quota

Each team may run 10 VMs unless an exception is filed.
EOF
commit "Document quota limits"

# ---------------------------------------------------------------- main C4 to C12 (task 3: bisect)
git switch -q main
cat > lib/size.sh <<'EOF'
# size.sh: convert human sizes such as 512M or 2G to MiB.
to_mib() {
    value=${1%[MGmg]}
    unit=${1#"$value"}
    case $unit in
        M|m) echo "$value" ;;
        G|g) echo $((value * 1024)) ;;
        *) echo "unknown unit: $1" >&2; return 1 ;;
    esac
}

to_gib() {
    mib=$(to_mib "$1") || return 1
    echo $((mib / 1024))
}
EOF
commit "Accept lowercase units"

cat > Makefile <<'EOF'
test:
	sh tests/run.sh
EOF
commit "Add Makefile"

cat > CHANGELOG.md <<'EOF'
# Changelog

## 1.1
- Lowercase units accepted.
EOF
commit "Add changelog"

cat > lib/size.sh <<'EOF'
# size.sh: convert human sizes such as 512M or 2G to MiB.
to_mib() {
    value=${1%[MGmg]}
    unit=${1#"$value"}
    case $unit in
        M|m) factor=1 ;;
        G|g) factor=1000 ;;
        *) echo "unknown unit: $1" >&2; return 1 ;;
    esac
    echo $((value * factor))
}

to_gib() {
    mib=$(to_mib "$1") || return 1
    echo $((mib / 1024))
}
EOF
commit "Refactor unit parsing"

cat >> README.md <<'EOF'
- `to_gib`: convert a size to whole GiB
EOF
commit "Document to_gib in README"

cat > .shellcheckrc <<'EOF'
shell=sh
EOF
commit "Add shellcheck config"

cat >> CHANGELOG.md <<'EOF'
- to_gib helper documented.
EOF
commit "Update changelog"

cat > lib/version.sh <<'EOF'
# version.sh: print the tool version.
version() {
    echo 1.1.0
}
EOF
commit "Add version helper"

cat > Makefile <<'EOF'
test:
	sh tests/run.sh

check: test
EOF
commit "Add check target"

cat >> NOTES.md <<'EOF'
- [x] Version helper
EOF
commit "Update notes"

cat > lib/size.sh <<'EOF'
# size.sh: convert sizes such as 512M, 2G or 2g to MiB (binary units).
to_mib() {
    value=${1%[MGmg]}
    unit=${1#"$value"}
    case $unit in
        M|m) factor=1 ;;
        G|g) factor=1000 ;;
        *) echo "unknown unit: $1" >&2; return 1 ;;
    esac
    echo $((value * factor))
}

to_gib() {
    mib=$(to_mib "$1") || return 1
    echo $((mib / 1024))
}
EOF
commit "Tidy size.sh comments"

# ---------------------------------------------------------------- publish main and release
git push -q -u origin main release 2>/dev/null

# ---------------------------------------------------------------- work in progress (task 6)
cat >> NOTES.md <<'EOF'
- [ ] WIP: compare quota numbers with the capacity sheet
EOF
cat > scratch-plan.txt <<'EOF'
Ask the storage team about thin provisioning before raising quotas.
EOF

echo "Lab ready in $lab/repo (remote: $lab/remote.git)."
echo "You are on branch main with uncommitted work. Start with task 6, part A."
