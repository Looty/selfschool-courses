#!/bin/bash
# nightly.sh: count the running VMs per hypervisor.
# Usage: nightly.sh [INPUT_DIR]
# Input:  INPUT_DIR/*.csv with lines "hypervisor,vm,state"
# Output: /srv/reports/out/running-vms.txt
# Installed as /opt/report/nightly.sh and run every night as user "report".

IN_DIR=${1:-/srv/reports/in}
OUT=/srv/reports/out/running-vms.txt

cd "$IN_DIR"
cat *.csv | grep ',running$' | cut -d, -f1 | sort | uniq -c > "$OUT"
echo "report written: $OUT"
