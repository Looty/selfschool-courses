---
id: l16
title: "DNS, MTU and air-gapped clusters"
quiz: quiz-02.yaml
resources: [../resources/lab6/lab6-run.sh, ../resources/lab6/lab6.yaml]
sources: [73, 74, 75, 76, 77, 80, 82, 84]
---
After this lesson you can explain every line of a pod's `resolv.conf` and the extra queries `ndots:5` causes, recognise a broken search list, find an overlay MTU mismatch hop by hop, install a cluster offline, and plan upgrades for a Kubernetes distribution you ship.

Outputs below come from the course's test runs on K3s 1.37.1; IPs differ between excerpts.

## A pod's resolv.conf

The kubelet writes each pod's `/etc/resolv.conf`. [74] In the course's test run it read:

```text
search default.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.43.0.10
options ndots:5
```

`nameserver` is the cluster DNS Service. `search` lists suffixes to try: a lookup for `web` can become `web.default.svc.cluster.local`. [74] `ndots:n` is the threshold: a name with **fewer** than `n` dots is tried with each search suffix first, and only then as an absolute name. With the resolver's default of 1, any dotted name is tried as-is first. [75] Kubernetes sets 5, "high enough to cover all of the DNS names it generates". [80]

## The cost of ndots:5

`example.com` has one dot, fewer than five, so the search list goes first. In the test run, `dig +search +showsearch example.com` showed every query it sent:

```text
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN
;example.com.default.svc.cluster.local. IN A
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN
;example.com.svc.cluster.local.	IN	A
;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN
;example.com.cluster.local.	IN	A
;; ->>HEADER<<- opcode: QUERY, status: NOERROR
;example.com.			IN	A
```

Four queries for one external name: CoreDNS load and latency for a service that calls external APIs heavily. The fixes: write external names fully qualified with a trailing dot (`api.example.com.`), or lower `ndots` for that pod with `dnsConfig`. The documentation's example sets `ndots: "2"`, giving `options ndots:2 edns0`. [74]

## A broken search list

A second test pod used `dnsPolicy: "None"`, so all its DNS settings came from `dnsConfig`. [74] Its `searches` list was empty:

```text
$ cat /etc/resolv.conf
nameserver 10.43.0.10
options ndots:5
$ nslookup web
** server can't find web: SERVFAIL
$ nslookup web.default.svc.cluster.local
Address: 10.43.50.176
```

With no search suffix, the short name means nothing; the FQDN still works. "The FQDN works, the short name fails" is the debugging guide's signal to check `resolv.conf`. [80] Other `dnsPolicy` values: `Default` inherits the node's resolver configuration, `ClusterFirst` sends non-cluster names upstream through cluster DNS, and `ClusterFirstWithHostNet` is needed for `hostNetwork` pods to get cluster DNS at all. [74]

## MTU in an overlay

K3s's default flannel backend is vxlan. [76] VXLAN wraps each pod packet in UDP, and the wrapping costs bytes. That is why in the test run `flannel.1` and the pods had MTU 1450 while the node's `eth0` had 1500. flannel's `MTU` option defaults to the external interface's MTU when unset. [82] flannel's `host-gw` backend avoids the overlay by installing plain routes, but needs direct layer-2 connectivity between hosts. [82]

**Healthy.** The pod's `eth0` was 1450. `ping -M do -s 1422` to the web pod on the other node worked: 1422 bytes of data plus 28 bytes of headers is 1450. `-s 1423` failed inside the pod with `local error: message too long, mtu=1450`. That is correct behaviour, not a fault.

**Broken.** The pod's `eth0` was then set to 1500 through `nsenter`, behind the CNI's back. Now `ping -M do -s 1472` failed with `sendmsg: No buffer space available`, and `tracepath` printed `send failed` with `pmtu 1500`.

**Found.** Comparing MTUs along the path, from the pod, then the node:

```text
mtu 1500    # pod eth0 (wrong)
mtu 1450    # cni0
mtu 1450    # flannel.1
mtu 1500    # node eth0
```

The pod is the only hop claiming more than the overlay carries. In a real cluster the fix is in the CNI configuration, not in pods: since flannel takes the external interface's MTU unless set, an MTU problem usually means the node network is smaller than the CNI assumed (VPN, tunnel, cloud overlay). [82]

:::low-confidence
In the test run, a plain `curl` from the mis-configured pod to the remote web pod still returned 200. Our reading is that TCP's MSS (maximum segment size) negotiation kept segments small enough, so TCP can hide a mismatch that ICMP and UDP expose. No source read for this course states that; test your own traffic (large uploads, UDP, traffic leaving the cluster).
:::

Optional: `../resources/lab6/lab6-run.sh` rebuilds the cluster behind these outputs.

## Air-gapped installs (RKE2 as the example)

RKE2's air-gap guide lists four ways to get images onto nodes: a private registry, manually deployed image tarballs, Hauler, and an embedded registry mirror. [77] The tarball method places `rke2-images.linux-amd64.tar.zst` (or the core tarball plus a CNI-specific one) in `/var/lib/rancher/rke2/agent/images/`. The install script runs offline with `INSTALL_RKE2_ARTIFACT_PATH` pointing at the downloaded artifacts. [77] Private-registry setup lives on a separate `registries.yaml` page, which this course did not read. [77]

The rest of an offline product follows the same idea as chapters 03 and 05: Helm charts as files, OS packages from your signed apt repository, Python wheels from your index, each pinned and checksummed.

## Versioning a cluster you ship

The upstream rules constrain your product's upgrade path: [84]

- The project maintains the three most recent minor releases (1.37, 1.36 and 1.35 at the time of reading), each with about a year of patches.
- HA API servers must be within one minor version of each other; kube-apiserver may not skip minor versions when upgrading.
- kubelet and kube-proxy must not be newer than kube-apiserver and may be up to three minors older; kubectl is supported within one minor either way.
- Upgrade order: kube-apiserver, then controller-manager, scheduler and cloud-controller-manager, then kubelets (drain first; in-place minor kubelet upgrades are not supported), then kube-proxy.
- Before a minor upgrade, move to the latest patch of the current minor, then to the latest patch of the target.

For a product, that becomes a release policy: your version maps to one tested Kubernetes minor plus pinned component versions. Patch releases (one CVE, one component) bump only that component, the way Lab 2 hotfixed one `.deb`. Minor upgrades are a documented, ordered procedure that never skips a minor. And settings an upgrade could change are pinned: the kube-proxy docs advise setting the mode explicitly, since a future release will switch the default from `iptables` to `nftables`. [73] Pin the overlay MTU the same way.

## Gotchas

- **External calls slow, CoreDNS busy.** `ndots:5` sends external names through three search suffixes first; `dig +search +showsearch` shows the NXDOMAINs. Fix: trailing dots or a lower `ndots`. [74] [75]
- **Short names fail, FQDNs work.** The `search` line is missing, for example after `dnsPolicy: "None"`. Check the pod's `/etc/resolv.conf`. [74] [80]
- **Large packets fail, small ones work.** Some hop's MTU exceeds the path's, often a VPN or tunnel under an unset flannel MTU; `ping -M do -s <size>` and `tracepath` show it. Compare MTUs hop by hop; set the CNI's MTU, not the pod's. [82]
- **Proxy mode changes after an upgrade.** An unset mode follows the release default, which will move to `nftables`. Set it explicitly. [73]
- **An unsupported upgrade plan.** Skipping a minor on the API server, upgrading kubelets first, or a minor kubelet upgrade in place without draining are all outside the skew policy. [84]

:::key-takeaways
- `ndots:5` sends dotted external names through every search suffix first; trailing dots or a lower `ndots` avoid it. [74] [75]
- "FQDN works, short name fails" points at the search list. [80]
- Overlay MTU sits below the node's; a mismatch shows as failing large packets. [82]
- RKE2 air-gap: image tarballs or a private registry; offline install via `INSTALL_RKE2_ARTIFACT_PATH`. [77]
- Skew policy: no minor skips for the API server; kubelet never newer than it; drain before kubelets. [84]
:::

:::glossary
- **CoreDNS**: the DNS server most clusters run as the cluster DNS Service.
- **Search list**: domain suffixes the resolver appends to short names.
- **`ndots`**: the dot count below which the search list is tried first.
- **FQDN**: fully qualified domain name; a trailing dot marks it absolute.
- **`dnsPolicy` / `dnsConfig`**: pod fields that choose and customise DNS settings.
- **MTU**: maximum transmission unit, the largest packet an interface sends.
- **Path MTU**: the smallest MTU along a network path.
- **Air-gapped**: with no network path to the internet.
- **Version skew**: the allowed version difference between cluster components.
:::
