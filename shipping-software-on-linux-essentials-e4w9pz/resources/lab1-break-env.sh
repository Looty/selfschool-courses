#!/usr/bin/env bash
# Lab 1: break a Python environment three ways and fix each one.
# Run as root inside a fresh Debian container:
#   docker run --rm -it -v "$PWD":/lab debian:bookworm bash /lab/lab1-break-env.sh
# Needs internet access to reach deb.debian.org and pypi.org.
set -u

step() { printf '\n========== %s ==========\n' "$*"; }
run()  { printf '$ %s\n' "$*"; bash -c "$*"; printf '(exit code %s)\n' "$?"; }

step "Setup: system Python from apt"
apt-get update -qq >/dev/null
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3 python3-pip python3-venv python3-yaml >/dev/null
run "python3 --version"
run "python3 -c 'import sys, sysconfig; print(sys.prefix, sys.base_prefix); print(sysconfig.get_path(\"stdlib\"))'"
run "ls /usr/lib/python3.11/EXTERNALLY-MANAGED"

step "Break 1: PEP 668 refuses a system-wide pip install"
run "pip install requests 2>&1 | head -n 4"
run "sed -n 1,3p /usr/lib/python3.11/EXTERNALLY-MANAGED"

step "Fix 1: install into a virtual environment instead"
run "python3 -m venv /opt/app/.venv"
run "cat /opt/app/.venv/pyvenv.cfg"
run "/opt/app/.venv/bin/python -m pip install -q requests && /opt/app/.venv/bin/python -c 'import requests; print(\"requests\", requests.__version__)'"

step "Break 2: the wrong interpreter runs the code"
cat > /opt/app/main.py <<'EOF'
import requests
print("ok", requests.__version__)
EOF
run "cd /opt/app && python3 main.py 2>&1 | tail -n 1"
run "command -v python3; python3 -c 'import sys; print(sys.executable, sys.prefix == sys.base_prefix)'"

step "Fix 2: run the venv's interpreter (or activate the venv)"
run "/opt/app/.venv/bin/python -c 'import sys; print(sys.executable, sys.prefix == sys.base_prefix)'"
run "cd /opt/app && .venv/bin/python main.py"
run ". /opt/app/.venv/bin/activate && command -v python && python /opt/app/main.py"

step "Break 3: a system site-packages leak hides a missing dependency"
cat > /opt/app/config.py <<'EOF'
import yaml
print("yaml", yaml.__version__, "from", yaml.__file__)
EOF
run "python3 -m venv --system-site-packages /opt/leaky"
run "grep include-system /opt/leaky/pyvenv.cfg"
run "/opt/leaky/bin/python /opt/app/config.py"
run "/opt/leaky/bin/python -m pip list 2>/dev/null | grep -i pyyaml"

step "Fix 3: turn the leak off, see the real gap, declare the dependency"
run "sed -i 's/^include-system-site-packages = true/include-system-site-packages = false/' /opt/leaky/pyvenv.cfg"
run "/opt/leaky/bin/python /opt/app/config.py 2>&1 | tail -n 1"
run "/opt/leaky/bin/python -m pip install -q pyyaml && /opt/leaky/bin/python /opt/app/config.py"

step "Where each interpreter looks"
run "python3 -m site | head -n 8"
run "/opt/app/.venv/bin/python -m site | head -n 8"
