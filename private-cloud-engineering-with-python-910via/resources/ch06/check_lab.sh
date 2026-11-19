#!/usr/bin/env bash
# check_lab.sh: verify the end state of each task in the Git recovery lab.
#
# Usage:  bash check_lab.sh <lab-dir>      (the same directory you gave make_lab_repo.sh)
#
# Prints PASS or FAIL for each task and exits 0 only when all six pass.
# It reads branches, tags and the remote; it changes nothing.
set -uo pipefail

if [ $# -ne 1 ]; then
    echo "usage: bash check_lab.sh <lab-dir>" >&2
    exit 2
fi
lab=$(cd "$1" && pwd) || exit 2
repo="$lab/repo"
remote="$lab/remote.git"
g() { git -C "$repo" "$@"; }

failed=0
report() {  # report <task> <ok 0/1> <message>
    if [ "$2" -eq 0 ]; then
        echo "PASS  task $1: $3"
    else
        echo "FAIL  task $1: $3"
        failed=1
    fi
}
# first commit reachable from $1 whose subject is exactly $2 (empty if none)
find_subject() {
    g log --format='%H %s' "$1" 2>/dev/null | while read -r sha subject; do
        if [ "$subject" = "$2" ]; then echo "$sha"; break; fi
    done
}
in_progress() {
    gd=$(g rev-parse --git-dir)
    case $gd in /*|?:*) ;; *) gd="$repo/$gd" ;; esac
    [ -d "$gd/rebase-merge" ] || [ -d "$gd/rebase-apply" ] || [ -f "$gd/CHERRY_PICK_HEAD" ] ||
        [ -f "$gd/REVERT_HEAD" ] || [ -f "$gd/MERGE_HEAD" ] || [ -f "$gd/BISECT_LOG" ]
}

# ---- Task 1: the JSON commit lives on feature/report, and no longer on docs
ok=1
if [ -n "$(find_subject feature/report 'Add JSON output for report')" ] &&
   g cat-file -e feature/report:lib/report_json.sh 2>/dev/null &&
   [ -z "$(find_subject docs 'Add JSON output for report')" ] &&
   [ "$(g log -1 --format=%s docs 2>/dev/null)" = "Fix typo in contributing guide" ]; then
    ok=0
fi
report 1 $ok "JSON commit moved from docs to feature/report"

# ---- Task 2: experiment has its lost commit back
ok=1
if [ "$(g log -1 --format=%s experiment 2>/dev/null)" = "Tune retry backoff" ]; then ok=0; fi
report 2 $ok "experiment tip is 'Tune retry backoff' again"

# ---- Task 3: tag found-bug marks a commit whose tests fail while its parent's pass
ok=1
msg="tag found-bug points at the first bad commit"
if g rev-parse -q --verify 'found-bug^{commit}' >/dev/null; then
    tmp=$(mktemp -d)
    mkdir "$tmp/bad" "$tmp/parent"
    g archive found-bug | tar -x -C "$tmp/bad"
    g archive 'found-bug^' | tar -x -C "$tmp/parent"
    if ! sh "$tmp/bad/tests/run.sh" >/dev/null 2>&1 && sh "$tmp/parent/tests/run.sh" >/dev/null 2>&1 &&
       g merge-base --is-ancestor found-bug main; then
        ok=0
    fi
    rm -rf "$tmp"
else
    msg="$msg (tag missing)"
fi
report 3 $ok "$msg"

# ---- Task 4: release undone by a new commit, history kept, pushed
ok=1
bad=$(find_subject release 'Switch default region to dc-test')
if [ -n "$bad" ] &&
   [ "$(g rev-parse release)" != "$bad" ] &&
   g diff --quiet "$bad^" release -- config/defaults.env &&
   [ "$(git -C "$remote" rev-parse release 2>/dev/null)" = "$(g rev-parse release)" ]; then
    ok=0
fi
report 4 $ok "region change reverted on release, old commit still in history, pushed to origin"

# ---- Task 5: feature/quota rebased onto main, conflict resolved with both lines
ok=1
readme=$(g show feature/quota:README.md 2>/dev/null)
if g merge-base --is-ancestor main feature/quota &&
   [ "$(g rev-list --count main..feature/quota)" -eq 2 ] &&
   [ "$(g rev-list --merges --count main..feature/quota)" -eq 0 ] &&
   printf '%s\n' "$readme" | grep -q '^- `to_gib`' &&
   printf '%s\n' "$readme" | grep -q '^- `quota`' &&
   ! printf '%s\n' "$readme" | grep -qE '^(<<<<<<<|=======|>>>>>>>)'; then
    ok=0
fi
report 5 $ok "feature/quota sits on top of main, README keeps both command lines"

# ---- Task 6: the work in progress was shelved and ends up committed on wip/notes
ok=1
if g rev-parse -q --verify refs/heads/wip/notes >/dev/null &&
   g show wip/notes:NOTES.md 2>/dev/null | grep -q 'WIP: compare quota numbers' &&
   g cat-file -e wip/notes:scratch-plan.txt 2>/dev/null &&
   ! g show main:NOTES.md | grep -q 'WIP:' &&
   [ -z "$(g stash list)" ]; then
    ok=0
fi
report 6 $ok "stash turned into branch wip/notes with NOTES.md and scratch-plan.txt; stash list empty"

if in_progress; then
    echo "NOTE  a merge, rebase, cherry-pick, revert or bisect is still in progress; finish or abort it"
    failed=1
fi

if [ "$failed" -eq 0 ]; then
    echo "All tasks pass."
else
    echo "Some tasks are not done yet."
fi
exit "$failed"
