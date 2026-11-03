#!/usr/bin/env bash
# Lab 6: Kubernetes from the node. Trace one pod-to-Service packet, break DNS search and fix it, and find an
# MTU mismatch. Needs Docker, kubectl and k3d 5.9 or newer (older k3d cannot start current k3s images).
# From the resources folder:
#   bash lab6/lab6-run.sh            # create the cluster, run every step, keep the cluster for exploring
#   bash lab6/lab6-run.sh delete     # remove the cluster
# If your k3d is too old, run it from its image instead:
#   K3D="docker run --rm -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/k3d-io/k3d:5.9.0" bash lab6/lab6-run.sh
set -uo pipefail
export MSYS_NO_PATHCONV=1
K3D=${K3D:-k3d}
CLUSTER=shiplab
HERE="$(cd "$(dirname "$0")" && pwd)"
KC="$HERE/.kubeconfig"
say() { printf '\n$ %s\n' "$*"; }
hdr() { printf '\n==================== %s ====================\n' "$*"; }
k() { kubectl --kubeconfig "$(command -v cygpath >/dev/null && cygpath -w "$KC" || echo "$KC")" "$@"; }
node() { local n=$1; shift; say "[node $n] $*"; docker exec "$n" sh -c "$*"; }

if [ "${1:-}" = delete ]; then $K3D cluster delete $CLUSTER; rm -f "$KC"; exit 0; fi

hdr "Cluster: one server and one agent, K3s v1.37.1"
$K3D cluster list 2>/dev/null | grep -q "^$CLUSTER " || \
  $K3D cluster create $CLUSTER --image rancher/k3s:v1.37.1-k3s1 --agents 1 --k3s-arg "--disable=traefik@server:0" --wait >/dev/null
$K3D kubeconfig get $CLUSTER 2>/dev/null | sed -E 's#server: https://[^:]+:#server: https://127.0.0.1:#' > "$KC"
k get nodes >/dev/null 2>&1 || { echo "cannot reach the cluster API; check $KC"; exit 1; }
k apply -f "$(command -v cygpath >/dev/null && cygpath -w "$HERE/lab6.yaml" || echo "$HERE/lab6.yaml")" >/dev/null
k wait --for=condition=Ready pod --all --timeout=240s >/dev/null
say "kubectl get pods -o wide"; k get pods -o wide | awk '{print $1, $6, $7}' | column -t

CLIENT_NODE=$(k get pod client -o jsonpath='{.spec.nodeName}')   # k3d names node containers like the nodes
SVC_IP=$(k get svc web -o jsonpath='{.spec.clusterIP}')
REMOTE_WEB_IP=$(k get pods -l app=web -o wide --no-headers | awk -v n="$CLIENT_NODE" '$7 != n {print $6; exit}')

hdr "1. The node view: containerd, crictl, the pod's network namespace"
node "$CLIENT_NODE" "crictl pods --name '^client\$' -o table | cut -c1-90"
POD_ID=$(docker exec "$CLIENT_NODE" crictl pods --name '^client$' -q)
PID=$(docker exec "$CLIENT_NODE" crictl inspectp -o go-template --template '{{.info.pid}}' "$POD_ID")
[ -n "$PID" ] && [ "$PID" != 1 ] || { echo "could not find the client pod's PID"; exit 1; }
say "[node $CLIENT_NODE] crictl inspectp -o go-template --template '{{.info.pid}}' $POD_ID"; echo "$PID"
node "$CLIENT_NODE" "nsenter -t $PID -n ip -o addr show eth0 | awk '{print \$2, \$4}'; nsenter -t $PID -n ip link show eth0 | head -n 1"
IFINDEX=$(docker exec "$CLIENT_NODE" sh -c "nsenter -t $PID -n ip link show eth0 | head -n1 | sed -n 's/.*@if\([0-9]*\).*/\1/p'")
node "$CLIENT_NODE" "ip -o link | grep '^$IFINDEX:' | cut -d' ' -f2-12"
node "$CLIENT_NODE" "ip route | grep -E 'cni0|flannel'"
node "$CLIENT_NODE" "ip -d link show flannel.1 | sed -n '1p;3p' | cut -c1-110"

hdr "2. One packet to the Service: iptables rules and the conntrack entry"
node "$CLIENT_NODE" "iptables-save -t nat | grep -E 'default/web' | cut -c1-150"
say "kubectl exec client -- curl -s -o /dev/null -w '%{http_code} from %{remote_ip}' http://web"
k exec client -- curl -s -o /dev/null -w '%{http_code} from %{remote_ip}\n' http://web
node "$CLIENT_NODE" "conntrack -L -p tcp -d $SVC_IP 2>/dev/null | head -n 2"

hdr "3. DNS: search domains, ndots, and what breaks without them"
say "kubectl exec client -- cat /etc/resolv.conf"; k exec client -- cat /etc/resolv.conf
say "kubectl exec client -- dig +search +showsearch +short web | tail -n 1"; k exec client -- dig +search +showsearch +short web | tail -n 1
say "kubectl exec client -- dig +search +showsearch example.com | grep -E '^;; (Got|QUESTION)|^;example' "
k exec client -- dig +search +showsearch example.com 2>&1 | grep -E 'status:|^;example' | head -n 8
say "kubectl exec client-nosearch -- cat /etc/resolv.conf"; k exec client-nosearch -- cat /etc/resolv.conf
say "kubectl exec client-nosearch -- nslookup web"; k exec client-nosearch -- nslookup web 2>&1 | tail -n 3
say "kubectl exec client-nosearch -- nslookup web.default.svc.cluster.local"; k exec client-nosearch -- nslookup web.default.svc.cluster.local 2>&1 | tail -n 2

hdr "4. MTU: pod, overlay, and a mismatch"
say "kubectl exec client -- ip link show eth0 | grep -o 'mtu [0-9]*'"; k exec client -- sh -c "ip link show eth0 | grep -o 'mtu [0-9]*'"
say "kubectl exec client -- ping -c1 -W2 -M do -s 1422 $REMOTE_WEB_IP"; k exec client -- ping -c1 -W2 -M do -s 1422 "$REMOTE_WEB_IP" 2>&1 | sed -n '2p;5p'
say "kubectl exec client -- ping -c1 -W2 -M do -s 1423 $REMOTE_WEB_IP"; k exec client -- ping -c1 -W2 -M do -s 1423 "$REMOTE_WEB_IP" 2>&1 | head -n 2
echo; echo "--- break it: raise the pod's MTU to 1500 behind the CNI's back"
node "$CLIENT_NODE" "nsenter -t $PID -n ip link set eth0 mtu 1500 && nsenter -t $PID -n ip link show eth0 | grep -o 'mtu [0-9]*'"
say "kubectl exec client -- ping -c1 -W2 -M do -s 1472 $REMOTE_WEB_IP"; k exec client -- ping -c1 -W2 -M do -s 1472 "$REMOTE_WEB_IP" 2>&1 | sed -n '1,3p'
say "kubectl exec client -- tracepath -n $REMOTE_WEB_IP"; k exec client -- tracepath -n "$REMOTE_WEB_IP" 2>&1 | head -n 5
say "kubectl exec client -- curl http://$REMOTE_WEB_IP/"; k exec client -- curl -s -m 5 -o /dev/null -w '%{http_code} in %{time_total}s\n' "http://$REMOTE_WEB_IP/"
node "$CLIENT_NODE" "nsenter -t $PID -n ip -o link show eth0 | grep -o 'mtu [0-9]*'; ip -o link show cni0 | grep -o 'mtu [0-9]*'; ip -o link show flannel.1 | grep -o 'mtu [0-9]*'; ip -o link show eth0 | grep -o 'mtu [0-9]*'"
echo; echo "--- fix it: back to the CNI's MTU"
node "$CLIENT_NODE" "nsenter -t $PID -n ip link set eth0 mtu 1450 && echo restored"
say "kubectl exec client -- ping -c1 -W2 -M do -s 1422 $REMOTE_WEB_IP"; k exec client -- ping -c1 -W2 -M do -s 1422 "$REMOTE_WEB_IP" 2>&1 | sed -n '2p'

echo; echo "Cluster kept for exploring. Remove it with: bash lab6/lab6-run.sh delete"
