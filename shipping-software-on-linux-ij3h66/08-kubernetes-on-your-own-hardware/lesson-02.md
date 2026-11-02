---
id: l31
title: "Pod networking and Services under the hood"
quiz: quiz-02.yaml
resources: [../resources/lab6/lab6-run.sh, ../resources/lab6/lab6.yaml]
sources: [72, 73, 76, 80, 81, 82]
---
After this lesson you can follow one packet from a pod to a Service and on to a backend pod on another node, name every interface, route and rule it crosses, and explain where MTU problems come from in an overlay.

## The rules the network must follow

Every pod gets its own cluster-wide IP, pods talk to each other without NAT whether or not they share a node, and agents on a node can reach all pods on that node. [72] How that is built is up to the CNI plugin. CNI itself is a small spec (version 1.1.0): the runtime calls a plugin binary with `CNI_COMMAND` set to `ADD`, `DEL`, `CHECK`, `GC` or `VERSION`, plus `CNI_CONTAINERID`, `CNI_NETNS` and `CNI_IFNAME`. Configured plugins run in a chain, `ADD` in order and `DEL` in reverse. [81]

## Inside a node: veth pairs and a bridge

Lab 6 runs K3s, whose default CNI is flannel with the `vxlan` backend. [76] On the client pod's node:

```text
# inside the pod (nsenter -n)
2: eth0@if8: ... mtu 1450
# on the node
veth5d803367@if2: ... mtu 1450 qdisc noqueue master cni0 state UP
10.42.0.0/24 dev cni0 proto kernel scope link src 10.42.0.1
10.42.1.0/24 via 10.42.1.0 dev flannel.1 onlink
```

The pod's `eth0` and the node's `veth5d803367` are two ends of one virtual cable (`@if8` and `@if2` point at each other). The node end is attached to the `cni0` bridge, which owns this node's pod subnet `10.42.0.0/24`. Traffic for the other node's subnet `10.42.1.0/24` is routed to `flannel.1`.

## Between nodes: VXLAN

```text
3: flannel.1: ... mtu 1450
    vxlan id 1 local 172.19.0.4 dev eth0 srcport 0 0 dstport 8472
```

`flannel.1` is a VXLAN device: it wraps each pod packet in UDP and sends it to the other node's real address. flannel's VXLAN backend uses VNI 1 and, on Linux, the kernel's default port, currently 8472. [82] That matches the `vxlan id 1 ... dstport 8472` above. The wrapping costs bytes, which is why `flannel.1` and the pods get MTU 1450 while the node's `eth0` has 1500. flannel's `MTU` option defaults to the external interface's MTU when unset. [82] flannel's `host-gw` backend avoids the overlay by installing plain routes, but needs direct layer-2 connectivity between hosts. [82] Other CNI plugins offer routed designs (BGP among them). This course read no source on them, so check your plugin's documentation.

## A Service is a set of NAT rules

kube-proxy watches Services and EndpointSlices and programs the node so traffic to a `clusterIP:port` is redirected to one endpoint. On Linux its modes are `iptables`, `ipvs` and `nftables`. In Kubernetes 1.37 the default is `iptables`, a future release will switch it to `nftables`, and the docs advise setting the mode explicitly so an upgrade does not change it underneath you. [73] `ipvs` is deprecated since 1.35, disabled by default from 1.40 and due for removal in 1.43. [73] `nftables` needs kernel 5.13 or later. [73]

In iptables mode, kube-proxy installs per-Service and per-endpoint chains; a rule picks a backend at random by default, and the per-endpoint chain DNATs to the pod. [73] Lab 6's rules for Service `web` (K3s 1.37.1, so iptables mode):

```text
-A KUBE-SERVICES -d 10.43.47.135/32 -p tcp ... --dport 80 -j KUBE-SVC-LOLE4ISW44XBNF3G
-A KUBE-SVC-LOLE4ISW44XBNF3G ... -m statistic --mode random --probability 0.50000000000 -j KUBE-SEP-PPB...
-A KUBE-SVC-LOLE4ISW44XBNF3G ... -j KUBE-SEP-RGD2WMRN4PLP5TTK
-A KUBE-SEP-RGD2WMRN4PLP5TTK -p tcp ... -j DNAT --to-destination 10.42.1.5:80
```

That is the shape the Kubernetes debugging guide describes: one rule in `KUBE-SERVICES` per Service port, one `KUBE-SVC-<hash>` chain, and one `KUBE-SEP-<hash>` chain per endpoint. [80] With two endpoints, the first gets probability 0.5 and the last is the fall-through.

## conntrack: the NAT is remembered

DNAT happens on the first packet; conntrack remembers the translation for the rest of the connection and rewrites replies. After `curl http://web` from the client:

```text
tcp 6 119 TIME_WAIT src=10.42.0.4 dst=10.43.47.135 sport=39598 dport=80 src=10.42.1.5 dst=10.42.0.4 sport=80 dport=39598 [ASSURED]
```

The first tuple is what the client sent (to the Service IP), the second is what came back (from pod `10.42.1.5`). kube-proxy's docs also record a conntrack pitfall: kernels before 6.1 have a bug that can reset long-lived TCP connections to Service IPs, which iptables mode works around and nftables mode does not by default. [73]

## Debug order for "the Service doesn't answer"

From the Kubernetes guide: check DNS, check that the Service has endpoints (`kubectl get endpointslices -l kubernetes.io/service-name=<svc>`, where `<none>` means the selector matches no pods), check kube-proxy is running, inspect the rules (`iptables-save | grep <svc>` or `ipvsadm -ln`), and bypass the Service by calling pod IPs directly. [80]

:::key-takeaways
- Pods get cluster-wide IPs and talk without NAT; CNI plugins (ADD/DEL/CHECK) build that. [72] [81]
- A pod's `eth0` is one end of a veth pair whose other end sits on the node's bridge (`cni0` here).
- flannel VXLAN: VNI 1, UDP 8472, overlay MTU below the node's (1450 vs 1500 in the lab). [82]
- kube-proxy iptables mode: KUBE-SERVICES → KUBE-SVC (random choice) → KUBE-SEP (DNAT); default in 1.37, ipvs deprecated. [73] [80]
- conntrack holds the DNAT for the life of the connection. [73]
:::

:::glossary
- **CNI**: Container Network Interface, the spec for plugins that wire pods into the network.
- **veth pair**: two virtual interfaces connected back to back, one in the pod, one on the node.
- **Bridge (`cni0`)**: a virtual switch on the node joining the pods' veth ends.
- **Overlay / VXLAN**: carrying pod packets inside UDP packets between nodes.
- **VNI**: VXLAN network identifier.
- **MTU**: maximum transmission unit, the largest packet an interface sends.
- **ClusterIP**: a Service's virtual IP, which exists only as NAT rules.
- **DNAT**: rewriting a packet's destination address.
- **conntrack**: the kernel table that tracks connections and their NAT translations.
- **EndpointSlice**: the object listing the pod IPs behind a Service.
:::
