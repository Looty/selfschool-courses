#!/usr/bin/env bash
# End-to-end check of the running stack. Usage:
#   ./smoke.sh                          # Flask API on port 8808
#   ./smoke.sh http://127.0.0.1:8809    # FastAPI API
set -euo pipefail
BASE=${1:-http://127.0.0.1:8808}

field() {   # field NAME JSON  -> value of a top-level string or number field
  printf '%s' "$2" | sed -E "s/.*\"$1\": ?\"?([^\",}]*)\"?.*/\1/"
}

wait_for() {   # wait_for ID FINAL_STATUS
  local body status=""
  for _ in $(seq 1 40); do
    body=$(curl -s "$BASE/vms/$1")
    status=$(field status "$body")
    echo "  $(date +%H:%M:%S) status=$status attempts=$(field attempts "$body")"
    if [ "$status" = "$2" ]; then echo "  final: $body"; return 0; fi
    sleep 1
  done
  echo "  gave up waiting for $2" >&2
  return 1
}

echo "== 1. create a VM"
body=$(curl -s -w '\n%{http_code}' -X POST "$BASE/vms" \
  -H 'Content-Type: application/json' \
  -d '{"name": "web-1", "cpus": 2, "memory_mb": 2048}')
echo "  HTTP $(tail -n1 <<<"$body")  $(head -n1 <<<"$body")"
id=$(field id "$(head -n1 <<<"$body")")

echo "== 2. poll until active"
wait_for "$id" active

echo "== 3. delete it twice"
for _ in 1 2; do
  echo "  DELETE -> HTTP $(curl -s -o /dev/null -w '%{http_code}' -X DELETE "$BASE/vms/$id")"
done
echo "  GET after delete -> HTTP $(curl -s -o /dev/null -w '%{http_code}' "$BASE/vms/$id")"

echo "== 4. same Idempotency-Key twice"
key="smoke-$(date +%s)"
for _ in 1 2; do
  echo "  $(curl -s -X POST "$BASE/vms" -H 'Content-Type: application/json' \
    -H "Idempotency-Key: $key" \
    -d '{"name": "db-1", "cpus": 4, "memory_mb": 8192}')"
done

echo "== 5. an invalid request"
body=$(curl -s -w '\n%{http_code}' -X POST "$BASE/vms" \
  -H 'Content-Type: application/json' -d '{"name": "bad", "cpus": 0, "memory_mb": 2048}')
echo "  HTTP $(tail -n1 <<<"$body")  $(head -n1 <<<"$body")"

echo "== 6. a VM whose build always fails (3 attempts, retries after 2 s and 4 s)"
body=$(curl -s -X POST "$BASE/vms" -H 'Content-Type: application/json' \
  -d '{"name": "broken-1", "cpus": 1, "memory_mb": 512, "fail": true}')
wait_for "$(field id "$body")" error
