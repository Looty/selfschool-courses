---
id: l15
title: "The node view and pod networking"
quiz: quiz-01.yaml
resources: [../resources/lab6/lab6-run.sh, ../resources/lab6/lab6.yaml]
sources: [72, 73, 76, 78, 79, 80, 81, 82, 83]
---
After this lesson you can debug a Kubernetes node when `kubectl` is not enough: list pods straight from the runtime, enter a pod's network namespace from the host, read the node conditions the kubelet acts on, and follow one packet from a pod through a Service to a backend pod on another node.

All outputs here come from the course's test run (K3s 1.37.1 in k3d, one server and one agent). To try it yourself (optional), the cluster script and manifest are in `../resources/lab6`.

## Who does what on a node

Setting up a pod's network namespace is the job of the container runtime behind the Container Runtime Interface (CRI); the pod network is a CNI plugin's job; Service traffic is handled by kube-proxy or a CNI's own proxy. [72] So a misbehaving pod has three layers to check:

| Layer | Component | Tool |
| --- | --- | --- |
| What should run | kubelet | `kubectl describe node` |
| What runs | containerd (CRI runtime) | `crictl` |
| How packets move | CNI plugin, kube-proxy rules | `nsenter`, `ip`, `iptables-save`, `conntrack` |

## crictl: the runtime's view

`crictl` is a command-line interface for CRI-compatible runtimes, for debugging on a node. It reads its endpoint from `/etc/crictl.yaml`. Everyday commands: `crictl pods` (pod sandboxes, filterable by `--name` and `--label`), `crictl ps -a` (all containers, including exited ones), `crictl images`, `crictl logs <id>` and `crictl exec -it <id> <cmd>`. [78]

```text
$ crictl pods --name '^client$'
POD ID              CREATED             STATE               NAME                NAMESPACE
868072eda2f4a       17 seconds ago      Ready               client              default
$ crictl inspectp -o go-template --template '{{.info.pid}}' 868072eda2f4a...
671
```

`crictl` talks to the runtime directly, so it still answers when the API server is down. Use it to look and read logs; the kubelet stays in charge of what runs.

## nsenter: stand inside the pod's network

Every pod has its own network namespace shared by its containers. [72] `nsenter` runs a program in another process's namespaces: `-t PID` picks the target, `-n` the network namespace, `-m` mount, `-p` PID. [83] With the sandbox PID, the **node's** tools see the pod's network, even if the image has no shell:

```text
$ nsenter -t 671 -n ip -o addr show eth0
eth0 10.42.0.5/24
$ nsenter -t 671 -n ip link show eth0
2: eth0@if8: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1450 ...
```

`eth0@if8` says the other end of this veth pair is interface 8 on the node.

## Node conditions and eviction

The kubelet watches eviction signals and maps them to node conditions: `MemoryPressure` (`memory.available`), `DiskPressure` (`nodefs.available`, `nodefs.inodesFree`, `imagefs.*`, `containerfs.*`) and `PIDPressure` (`pid.available`). [79] Default hard thresholds on Linux are `memory.available<100Mi`, `nodefs.available<10%`, `imagefs.available<15%`, `nodefs.inodesFree<5%` and `imagefs.inodesFree<5%`. [79]

Eviction is not an OOM kill. If the kernel runs out of memory before the kubelet reclaims, the OOM killer acts, guided by the `oom_score_adj` the kubelet set per QoS class (-997 for Guaranteed, 1000 for BestEffort). An OOM-killed container restarts per its `restartPolicy`; an evicted pod does not come back on that node. [79]

## The pod network and CNI

Every pod gets its own cluster-wide IP, and pods talk to each other without NAT whether or not they share a node. [72] The CNI plugin builds that. CNI is a small spec: the runtime calls a plugin binary with `CNI_COMMAND` set to `ADD`, `DEL`, `CHECK`, `GC` or `VERSION`; chained plugins run `ADD` in order and `DEL` in reverse. [81]

K3s's default CNI is flannel with the `vxlan` backend. [76] On the client pod's node:

```text
# inside the pod (nsenter -n)
2: eth0@if8: ... mtu 1450
# on the node
veth5d803367@if2: ... mtu 1450 qdisc noqueue master cni0 state UP
10.42.0.0/24 dev cni0 proto kernel scope link src 10.42.0.1
10.42.1.0/24 via 10.42.1.0 dev flannel.1 onlink
3: flannel.1: ... mtu 1450
    vxlan id 1 local 172.19.0.4 dev eth0 srcport 0 0 dstport 8472
```

The pod's `eth0` and the node's `veth5d803367` are two ends of one virtual cable (`@if8` and `@if2` point at each other). The node end sits on the `cni0` bridge, which owns this node's pod subnet. Traffic for the other node's subnet is routed to `flannel.1`, a VXLAN device that wraps each pod packet in UDP and sends it to the other node's real address. flannel's VXLAN backend uses VNI 1 and, on Linux, the kernel's default port, currently 8472. [82] The next lesson explains the 1450 MTU.

## A Service is a set of NAT rules

kube-proxy watches Services and EndpointSlices and programs the node so traffic to a `clusterIP:port` goes to one endpoint. On Linux its modes are `iptables`, `ipvs` and `nftables`; in Kubernetes 1.37 the default is `iptables`. [73] In iptables mode it installs per-Service and per-endpoint chains; a rule picks a backend at random by default, and the per-endpoint chain DNATs to the pod. [73] The test run's rules for Service `web`:

```text
-A KUBE-SERVICES -d 10.43.47.135/32 -p tcp ... --dport 80 -j KUBE-SVC-LOLE4ISW44XBNF3G
-A KUBE-SVC-LOLE4ISW44XBNF3G ... -m statistic --mode random --probability 0.50000000000 -j KUBE-SEP-PPB...
-A KUBE-SVC-LOLE4ISW44XBNF3G ... -j KUBE-SEP-RGD2WMRN4PLP5TTK
-A KUBE-SEP-RGD2WMRN4PLP5TTK -p tcp ... -j DNAT --to-destination 10.42.1.5:80
```

The debugging guide describes this shape: one `KUBE-SERVICES` rule per Service port, one `KUBE-SVC-<hash>` chain, one `KUBE-SEP-<hash>` chain per endpoint. [80] With two endpoints, the first gets probability 0.5 and the last is the fall-through.

## conntrack: the NAT is remembered

DNAT happens on the first packet; conntrack remembers it for the rest of the connection and rewrites replies. After `curl http://web`:

```text
tcp 6 119 TIME_WAIT src=10.42.0.4 dst=10.43.47.135 sport=39598 dport=80 src=10.42.1.5 dst=10.42.0.4 sport=80 dport=39598 [ASSURED]
```

The first tuple is what the client sent (to the Service IP), the second is what came back (from pod `10.42.1.5`).

## Triage order

For "the Service doesn't answer", the Kubernetes guide's order is: check DNS, check that the Service has endpoints, check kube-proxy is running, inspect the rules (`iptables-save | grep <svc>` or `ipvsadm -ln`), and bypass the Service by calling pod IPs directly. [80]

## Gotchas

- **Changing one eviction threshold zeroes the rest.** Set only `memory.available` and the other defaults become zero unless you set all of them or enable `MergeDefaultEvictionSettings`. You notice when a full disk no longer triggers DiskPressure. Fix: list every threshold. [79]
- **DiskPressure with free space.** `nodefs.inodesFree` is a DiskPressure signal, so millions of small files trip it while `df -h` looks fine. Check `df -i`. [79]
- **`free -m` disagrees with the kubelet.** `memory.available` comes from cgroupfs and excludes inactive file cache, so trust the kubelet's number, not `free`. [79]
- **Slow `crictl`.** Without an endpoint configured it tries a list of known endpoints, which costs time. Fix: write `/etc/crictl.yaml`. [78]
- **An upgrade changes the kube-proxy mode.** A future release will switch the default to `nftables`, and the docs advise setting the mode explicitly. `ipvs` is deprecated since 1.35, disabled by default from 1.40 and due for removal in 1.43; `nftables` needs kernel 5.13 or later. [73]
- **Long-lived connections reset.** Kernels before 6.1 have a conntrack bug that can reset long-lived TCP connections to Service IPs; iptables mode works around it, nftables mode does not by default. [73]
- **Service with no backends.** `kubectl get endpointslices -l kubernetes.io/service-name=<svc>` showing `<none>` means the selector matches no pods; the rules are fine. [80]

:::key-takeaways
- The CRI runtime sets up pod network namespaces; CNI plugins build the pod network; kube-proxy handles Services. [72]
- `crictl` gives pods, containers, logs and the sandbox PID without the API server; `nsenter -t PID -n` runs host tools inside the pod's network. [78] [83]
- MemoryPressure, DiskPressure and PIDPressure come from eviction signals; eviction (kubelet) and OOM kill (kernel) differ. [79]
- Pod `eth0` → veth on `cni0` → `flannel.1` (VXLAN, VNI 1, UDP 8472) for other nodes. [82]
- kube-proxy iptables mode: KUBE-SERVICES → KUBE-SVC (random choice) → KUBE-SEP (DNAT), and conntrack keeps the DNAT for the connection. [73] [80]
:::

:::glossary
- **kubelet**: the node agent that runs pods as the API server tells it to.
- **containerd**: the container runtime K3s and many clusters use.
- **CRI**: Container Runtime Interface, the API between the kubelet and the runtime.
- **crictl**: a CLI that talks to a CRI runtime directly.
- **Pod sandbox**: the runtime object that holds a pod's namespaces.
- **Network namespace**: a separate copy of the network stack (interfaces, routes, iptables) for a group of processes.
- **nsenter**: a tool that runs a command inside another process's namespaces.
- **Node condition**: a status flag such as DiskPressure that the kubelet reports.
- **CNI**: Container Network Interface, the spec for plugins that wire pods into the network.
- **veth pair**: two virtual interfaces connected back to back, one in the pod, one on the node.
- **Bridge (`cni0`)**: a virtual switch on the node joining the pods' veth ends.
- **Overlay / VXLAN**: carrying pod packets inside UDP packets between nodes.
- **VNI**: VXLAN network identifier.
- **ClusterIP**: a Service's virtual IP, which exists only as NAT rules.
- **DNAT**: rewriting a packet's destination address.
- **conntrack**: the kernel table that tracks connections and their NAT translations.
- **EndpointSlice**: the object listing the pod IPs behind a Service.
:::
