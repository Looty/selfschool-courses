---
id: l33
title: "Lab 6: trace a packet, break DNS, find an MTU mismatch"
quiz: quiz-04.yaml
resources: [../resources/lab6/lab6-run.sh, ../resources/lab6/lab6.yaml]
sources: [73, 74, 76, 78, 80, 82, 83, 85]
---
After this lab you will have followed one request from a pod to a Service and on to a backend pod using only node-level tools, watched `ndots` multiply DNS queries and seen a missing search list break short names, and caused and located an MTU mismatch between a pod and its overlay.

This is a hands-on lab. `lab6-run.sh` was run end to end while writing this course with k3d 5.9.0 and `rancher/k3s:v1.37.1-k3s1` (one server, one agent) on Docker Desktop. The outputs in this chapter come from several runs of the script, so pod IPs, Service IPs and PIDs differ between excerpts and will differ on your machine. `perf` is not needed here.

## Requirements and shortcut

k3d runs K3s in Docker. [85] The lab needs **k3d 5.9 or newer**: k3d 5.4.9 could not start current K3s images (the node container restarted without logging anything). If your k3d is older, run it from its image, as the course did:

```bash
cd resources
bash lab6/lab6-run.sh
# or, with an older local k3d:
K3D="docker run --rm -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/k3d-io/k3d:5.9.0" bash lab6/lab6-run.sh
bash lab6/lab6-run.sh delete      # when you are done
```

The script deploys `lab6.yaml`: a two-replica `web` Deployment spread over both nodes, a `web` Service, a `client` pod (the netshoot debug image) and `client-nosearch`, which has a hand-written DNS config. The cluster is kept so you can explore. Node shells are just `docker exec -it k3d-shiplab-agent-0 sh`.

## Part 1: from pod to node

1. `crictl pods --name '^client$'` on the client's node, then `crictl inspectp -o go-template --template '{{.info.pid}}' <id>` for the sandbox PID. [78]
2. `nsenter -t <pid> -n ip link show eth0` → `eth0@if8`. [83]
3. `ip -o link | grep '^8:'` on the node → `veth5d803367@if2 ... master cni0`.
4. `ip route` → the local pod subnet on `cni0`, the other node's subnet `via ... dev flannel.1`.
5. `ip -d link show flannel.1` → `vxlan id 1 ... dstport 8472`, `mtu 1450`. [82] K3s's default flannel backend is vxlan. [76]

## Part 2: one request to the Service

1. `iptables-save -t nat | grep default/web`: `KUBE-SERVICES` matches the ClusterIP, `KUBE-SVC-…` picks an endpoint with `--mode random --probability 0.5`, and `KUBE-SEP-…` does `DNAT --to-destination <pod>:80`. [73] [80] K3s 1.37.1 used iptables mode here, the documented default for 1.37. [73]
2. `kubectl exec client -- curl http://web` → `200 from 10.43.47.135`.
3. `conntrack -L -p tcp -d <clusterIP>` on the client's node: the original tuple goes to the ClusterIP, the reply tuple comes from the chosen pod.

**Your turn:** run the curl ten times and check which `KUBE-SEP` chain's packet counters grew (`iptables -t nat -L KUBE-SVC-… -v -n`).

## Part 3: DNS

1. `cat /etc/resolv.conf` in `client`: three search domains, `ndots:5`. [74]
2. `dig +search +showsearch example.com`: three NXDOMAIN answers (`example.com.default.svc.cluster.local.` and so on) before the real one.
3. In `client-nosearch` (`dnsPolicy: "None"`, empty `searches`): `nslookup web` → `SERVFAIL`, while `web.default.svc.cluster.local` resolves. [74] [80]

**Fix it yourself:** change `client-nosearch` to the default policy (delete the `dnsPolicy` and `dnsConfig` lines, recreate the pod) and rerun `nslookup web`. For the external-name cost, try `dig +search +showsearch example.com.` with a trailing dot and count the queries.

## Part 4: MTU

1. The pod's `eth0` is 1450. `ping -M do -s 1422` to the web pod on the other node works: 1422 bytes of data plus 28 bytes of headers is 1450. `-s 1423` fails inside the pod with `local error: message too long, mtu=1450`.
2. **Break it:** the script sets the pod's `eth0` to 1500 through `nsenter`, behind the CNI's back. Now `ping -M do -s 1472` fails with `sendmsg: No buffer space available`, and `tracepath` prints `send failed` with `pmtu 1500`.
3. **Find it:** compare MTUs along the path, from the pod, then the node:

```text
mtu 1500    # pod eth0 (wrong)
mtu 1450    # cni0
mtu 1450    # flannel.1
mtu 1500    # node eth0
```

The pod is the only hop that claims more than the overlay can carry.
4. **Fix:** set it back to 1450. In a real cluster the fix is in the CNI configuration, not in pods: flannel's MTU defaults to the external interface's MTU unless set. [82] So an MTU problem usually means the node network is smaller than the CNI assumed (VPN, tunnel, cloud overlay).

:::low-confidence
In this lab, a plain `curl` from the mis-configured pod to the remote web pod still returned 200. Our reading is that TCP's MSS negotiation kept segments small enough, so TCP between overlay pods can hide an MTU mismatch that ICMP and UDP expose. No source read for this course states that, so treat it as an observation and test your own traffic patterns (large uploads, UDP, traffic leaving the cluster).
:::

:::key-takeaways
- crictl gives the sandbox PID; nsenter puts host tools inside the pod's network namespace. [78] [83]
- A Service request is DNAT by `KUBE-SEP` rules, remembered by conntrack. [73] [80]
- `ndots:5` sends external names through every search domain first; an empty search list breaks short names. [74]
- An MTU mismatch shows up as failing large packets with odd errors; compare MTUs hop by hop. [82]
:::

:::glossary
- **k3d**: a tool that runs K3s clusters as Docker containers.
- **K3s**: a lightweight Kubernetes distribution.
- **netshoot**: a container image packed with network debugging tools.
- **ClusterIP**: a Service's virtual IP.
- **Path MTU**: the smallest MTU along a network path.
- **MSS**: maximum segment size, the largest TCP payload a side agrees to receive.
:::
