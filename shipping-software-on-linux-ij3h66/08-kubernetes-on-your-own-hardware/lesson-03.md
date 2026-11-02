---
id: l32
title: "DNS and ndots, air-gapped installs, and versioning a cluster you ship"
quiz: quiz-03.yaml
resources: [../resources/lab6/lab6.yaml]
sources: [74, 75, 77, 80, 84]
---
After this lesson you can explain every line of a pod's `resolv.conf` and the extra queries `ndots:5` causes, install a cluster with no internet access, and plan component versions and upgrades for a Kubernetes distribution you ship as part of a product.

## A pod's resolv.conf

The kubelet writes each pod's `/etc/resolv.conf`. [74] From Lab 6:

```text
search default.svc.cluster.local svc.cluster.local cluster.local
nameserver 10.43.0.10
options ndots:5
```

`nameserver` is the cluster DNS Service. `search` lists suffixes to try: a lookup for `web` can become `web.default.svc.cluster.local`. [74] `ndots:n` is the threshold: a name with **fewer** than `n` dots is tried with each search suffix first, and only then as an absolute name. With the resolver's default of 1, any dotted name is tried as-is first. [75] Kubernetes sets 5, "high enough to cover all of the DNS names it generates". [80]

## The cost of ndots:5

`example.com` has one dot, fewer than five, so the search list goes first. Lab 6 shows every query `dig` sent, with `+search +showsearch`:

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

Four queries for one external name. For a service that calls external APIs heavily, that is load on CoreDNS and added latency. The fixes: write external names fully qualified with a trailing dot (`api.example.com.`), or lower `ndots` for that pod with `dnsConfig`. The documentation's example sets `ndots: "2"`, and the resulting file reads `options ndots:2 edns0`. [74]

## Breaking DNS on purpose

Lab 6's second client uses `dnsPolicy: "None"`, so all DNS settings come from `dnsConfig`. [74] Its `searches` list is empty:

```text
$ cat /etc/resolv.conf
nameserver 10.43.0.10
options ndots:5
$ nslookup web
** server can't find web: SERVFAIL
$ nslookup web.default.svc.cluster.local
Address: 10.43.50.176
```

With no search suffix, the short Service name means nothing; the fully qualified name still works. That pattern of "the FQDN works, the short name fails" is the debugging guide's signal to check `resolv.conf`. [80] Other `dnsPolicy` values: `Default` inherits the node's resolver configuration, `ClusterFirst` sends non-cluster names upstream through cluster DNS, and `ClusterFirstWithHostNet` is needed for `hostNetwork` pods to get cluster DNS at all. [74]

## Air-gapped installs (RKE2 as the example)

RKE2's air-gap guide lists four ways to get images onto nodes: a private registry, manually deployed image tarballs, Hauler, and an embedded registry mirror. [77] The tarball method places `rke2-images.linux-amd64.tar.zst` (or the core tarball plus a CNI-specific one) in `/var/lib/rancher/rke2/agent/images/`. The install script runs offline with `INSTALL_RKE2_ARTIFACT_PATH` pointing at the downloaded artifacts. [77] For a private registry, the guide points to a separate `registries.yaml` configuration page, which this course did not read. [77] The rest of an offline product follows the same idea as chapters 03 and 05: Helm charts as files, OS packages from your signed apt repository, Python wheels from your index, each pinned and checksummed.

## Versioning a cluster you ship

The upstream rules constrain your product's upgrade path: [84]

- The project maintains the three most recent minor releases (1.37, 1.36 and 1.35 at the time of reading), each with about a year of patches.
- HA API servers must be within one minor version of each other; kube-apiserver may not skip minor versions when upgrading.
- kubelet and kube-proxy must not be newer than kube-apiserver and may be up to three minors older; kubectl is supported within one minor either way.
- Upgrade order: kube-apiserver, then controller-manager, scheduler and cloud-controller-manager, then kubelets (drain first; in-place minor kubelet upgrades are not supported), then kube-proxy.
- Before a minor upgrade, move to the latest patch of the current minor, then to the latest patch of the target.

For a product, that becomes a release policy: your version maps to one tested Kubernetes minor plus pinned component versions. Patch releases (one CVE, one component) bump only that component, the way Lab 3 hotfixed one `.deb`. Minor upgrades are a documented, ordered procedure that never skips a minor. And the kube-proxy mode (lesson 31) and the overlay MTU are pinned explicitly in configuration, so an upgrade cannot change them underneath a customer.

:::key-takeaways
- Pod `resolv.conf`: cluster DNS server, `<ns>.svc.cluster.local svc.cluster.local cluster.local` search list, `ndots:5`. [74] [80]
- Names with fewer dots than `ndots` try every search suffix first; external lookups cost extra queries. [75]
- Trailing-dot FQDNs or a per-pod `dnsConfig` with lower `ndots` avoid the extra queries. [74]
- RKE2 air-gap: image tarballs in `/var/lib/rancher/rke2/agent/images/` or a private registry; offline install via `INSTALL_RKE2_ARTIFACT_PATH`. [77]
- Skew policy: no minor skips for the API server; kubelet ≤ API server and at most three minors behind; upgrade control plane first. [84]
:::

:::glossary
- **CoreDNS**: the DNS server most clusters run as the cluster DNS Service.
- **Search list**: domain suffixes the resolver appends to short names.
- **`ndots`**: the dot count below which the search list is tried first.
- **FQDN**: fully qualified domain name; a trailing dot marks it absolute.
- **`dnsPolicy` / `dnsConfig`**: pod fields that choose and customise DNS settings.
- **Air-gapped**: with no network path to the internet.
- **Version skew**: the allowed version difference between cluster components.
- **Minor version**: the middle number, as in 1.**37**.
:::
