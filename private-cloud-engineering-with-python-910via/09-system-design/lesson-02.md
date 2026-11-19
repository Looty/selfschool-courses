---
id: l26
title: "Design deep dives: placement, failures and reconciliation"
quiz: quiz-02.yaml
resources: [../resources/ch09/ip_claim_demo.py]
sources: [35, 50, 51, 91, 94, 95, 96, 97, 98, 101, 155, 156, 158, 159, 160]
---
After this lesson you can answer the follow-up questions that come after the boxes are drawn: how a host is chosen, what happens when a worker or a hypervisor dies halfway, how the database and the hosts are kept in agreement, and how IP addresses are handed out without duplicates.

## Placement: filter, then weigh

Nova's scheduler works in three passes: prefilters narrow the request sent to Placement, filters remove hosts that cannot take the VM, and weighers rank the rest [155]. The default filter list is `ComputeFilter`, `ComputeCapabilitiesFilter`, `ImagePropertiesFilter`, `ServerGroupAntiAffinityFilter` and `ServerGroupAffinityFilter` [156]. Each weigher's score is normalised and multiplied by its multiplier, and the sum is the host's weight [155].

```text
weight = w1_multiplier * norm(w1) + w2_multiplier * norm(w2) + ...
```

For this service, the same shape in plain Python is enough: filter on enabled, has the image's architecture, has free CPU and RAM after the allocation ratio, not already holding a member of the same anti-affinity group; then sort by a weight.

**Spread or pack** is the weighing decision, and it is yours to defend. Spreading (prefer the emptiest host) shares CPU contention out and limits how many VMs one host failure takes down. Packing (prefer the fullest host that still fits) leaves whole hosts empty for big flavours and for maintenance. A sensible default: spread for general VMs, pack for a CI pool whose VMs live minutes.

**Overcommit.** Nova's initial ratios were 16.0 for CPU and 1.5 for RAM before the Antelope release (27.0.0) lowered them to 4.0 and 1.0 [155].

**Anti-affinity.** Three database replicas should never share a host. Nova expresses this as a server group with an anti-affinity policy, enforced by `ServerGroupAntiAffinityFilter`; a soft version exists as a weigher, `ServerGroupSoftAntiAffinityWeigher` [155]. A filter can refuse a host, a weigher can only rank it lower, so the soft version prefers separation without requiring it.

**Two workers, one last slot.** If both read "kvm-017 has room" and both place there, the host is over its limit. Make the claim a conditional write that fails when the room is gone, then try the next host:

```sql
UPDATE hosts
   SET vcpus_used = vcpus_used + 4, ram_mb_used = ram_mb_used + 8192
 WHERE name = 'kvm-017' AND enabled
   AND vcpus_used + 4    <= vcpus_total * 4.0
   AND ram_mb_used + 8192 <= ram_mb_total - ram_mb_reserved;
-- 1 row updated: the slot is ours. 0 rows: someone was faster, try the next host.
```

Nova has a `scheduler.max_attempts` option, default 3 [156], and a `BuildFailureWeigher` whose multiplier defaults to a very high value [155]. This design does the same: try at most three hosts, count recent build failures per host and rank failing hosts last. Placement, the service that holds these counts, models any consumable as a resource provider (a compute node, a shared storage pool or an IP allocation pool) with resource classes such as `VCPU`, `MEMORY_MB` and `DISK_GB` [159].

## Make every step idempotent

A step is idempotent when running it twice leaves the same result as running it once. The worker's job is a list of such steps, each of the form "check, then act":

| Step | Check | Act |
| --- | --- | --- |
| Claim host | `vm.host` already set? | conditional `UPDATE` above, then store `vm.host` |
| Claim IP | row for this VM in `allocations`? | insert, as in the demo below |
| Disk | `vm-7f3a.qcow2` exists on the host? | `qemu-img create -f qcow2 -b debian-13-v4.qcow2 -F qcow2 vm-7f3a.qcow2` |
| Seed | `seed-7f3a.iso` exists? | write `meta-data` (with `instance-id`) and `user-data`, build the ISO |
| Domain | `lookupByName` finds it? | `defineXML(xml)` |
| Running | `isActive()`? | `create()` |
| Record | state already ACTIVE? | `UPDATE vms SET state='ACTIVE' WHERE id=? AND state='BUILDING'` |

The disk is a qcow2 overlay: it records only differences from its backing file, and the backing file is never modified [91]. Never run `qemu-img` against an image a running VM is using [91]. The seed disk is cloud-init's NoCloud source, where `meta-data` must contain an `instance-id` [101]. Use the VM id: cloud-init treats a new `instance-id` as a first boot, and `runcmd` runs only on first boot [101]. In libvirt, `lookupByName` raises `libvirtError` when the domain does not exist [97], `defineXML` stores a persistent definition and `create` boots it [98].

```python
def ensure_running(conn, name, xml):
    try:
        dom = conn.lookupByName(name)
    except libvirt.libvirtError:
        dom = conn.defineXML(xml)
    if not dom.isActive():
        dom.create()
    return dom
```

:::low-confidence
`ensure_running` was not run for this course (no KVM host was available). The method names follow libvirt's documented naming rule and the provisioning guide [97] [98]; check them against chapter 11 and a real host. A production version should also tell "not found" apart from other `libvirtError` causes, such as a lost connection.
:::

## When things die halfway

**The worker dies after the disk exists, before the VM starts.** RQ waits for the running job on `SIGTERM`, but `kill -9` gives it no chance to mark the job failed; a later cleanup marks it abandoned [50]. The chapter 8 lab saw a slightly different outcome, so the design does not depend on the queue. Each VM row carries `step` and `updated_at`. The reconciler re-enqueues any BUILDING row with no progress for 15 minutes. The new run finds the host claimed, the IP claimed and the disk present, skips all three, and defines and starts the domain. A per-VM lock stops two runs overlapping: `SET lock:vm:<id> <token> NX EX 600`, released only by its owner [51]. Redis's own page prefers the Redlock algorithm for stronger guarantees [51], so treat this lock as protection against accidents, and let the conditional `UPDATE`s be the real guard.

| Event | Response |
| --- | --- |
| A hypervisor stops answering | after missed heartbeats, disable it so placement skips it (Nova has a mandatory prefilter that drops disabled compute nodes [155]); its VMs go to ERROR with a reason |
| The user wants that VM back | rebuild elsewhere on request only: a Nova root disk is ephemeral, and only separate volumes outlive the instance [158] |
| DELETE, or cleanup after ERROR | run the steps backwards, "already gone" counts as success: `destroy` (hard stop, keeps storage [95]), `undefine` (removes the inactive definition [95]), delete overlay and seed, release IP, host claim and quota |

## Reconciliation

Kubernetes calls this a controller: a loop that watches current state and moves it towards the desired state, like a thermostat [160]. Its docs favour many simple controllers over one big one, and assume controllers can fail [160]. Here the database is desired state and `listAllDomains` on each host [97] is current state.

| Database says | Host says | Action |
| --- | --- | --- |
| ACTIVE | no such domain | mark ERROR, alert; never recreate silently |
| no row, or DELETED | domain exists | orphan: shut down after a grace period, delete after a longer one |
| BUILDING, stale | anything | re-enqueue the idempotent job |
| ACTIVE | domain shut off | record power state; restart only if policy says so |

Act only on a difference seen on two passes in a row, cap destructive actions per pass, and log every repair.

## IP addresses without double assignment

The database is the referee. `ip_claim_demo.py` uses one table with two constraints: `address` is the primary key and `vm_id` is unique. `ipaddress` gives the pool, and `hosts()` skips the network and broadcast addresses [35]. Run `python ip_claim_demo.py`; the course's test run on Python 3.13 and 3.11 printed:

```text
pool: 10.20.0.1 to 10.20.0.6 (6 addresses)
vm-1 first claim : 10.20.0.1
vm-1 retry       : 10.20.0.1
vm-2 first claim : 10.20.0.2
stale insert     : IntegrityError - UNIQUE constraint failed: allocations.address
second address   : IntegrityError - UNIQUE constraint failed: allocations.vm_id
vm-3 after release: 10.20.0.1
vm-4 claim       : 10.20.0.3
vm-5 claim       : 10.20.0.4
vm-6 claim       : 10.20.0.5
vm-7 claim       : 10.20.0.6
vm-8 claim       : RuntimeError - address pool exhausted
final table      : [('10.20.0.1', 'vm-3'), ('10.20.0.2', 'vm-2'), ('10.20.0.3', 'vm-4'), ('10.20.0.4', 'vm-5'), ('10.20.0.5', 'vm-6'), ('10.20.0.6', 'vm-7')]
```

The retry returns the same address, and the stale insert loses to the constraint. The "check for a free address" step is only an optimisation; the constraint is the guarantee. Note `vm-3` got `10.20.0.1` straight after its release: in production, hold released addresses back for a while so stale DNS records and ARP caches do not send traffic to the wrong VM.

## Quotas, draining and observability

**Quotas.** Nova limits resources such as cores and RAM per project [158]. Check and reserve in the same transaction that inserts the VM row, and release on delete.

**Draining a host.** Disable it, then live-migrate its VMs away: the guest keeps running while memory is copied, and the destination takes over once memory matches [94]. By default it expects shared storage at the same paths, the same hypervisor version and compatible CPUs [94]. The command is `virsh migrate --live` [95]; `--copy-storage-all` copies local disks when storage is not shared [95] [96]. The stream carries all guest RAM, so use a separate network or encryption [96].

| Observability signal | Why |
| --- | --- |
| provision latency per step, p50 and p95 | shows which step got slow |
| queue depth and oldest job age | workers too few or stuck |
| ERROR rate by host and by image | a bad host or a bad image |
| reconciler repairs per pass | rising repairs are the earliest sign of an upstream bug |
| free slots per flavour | when to buy hosts |

## Gotchas

- **Check-then-insert without a constraint.** Two workers both see the address free. Only a uniqueness constraint or a conditional write closes the race.
- **Trusting the queue to rerun a dead job.** Abandoned-job handling depends on RQ's cleanup and version [50]; re-enqueue from database state instead.
- **A reconciler that deletes on first sight.** A host that answered slowly looks like "no domains". Require two passes and cap deletions.
- **Reusing `instance-id`.** cloud-init then treats a rebuilt VM as an old one and skips first-boot work [101].
- **`destroy` is not delete.** It stops the VM and leaves its storage [95]; cleanup must undefine and remove the disks too.

:::key-takeaways
- Placement is filter, then weigh; spread or pack is a choice you justify. [155]
- Claims (capacity, IP, quota) are conditional writes or constraints, never check-then-act.
- Every provisioning step is check-then-act, so a rerun after a crash finishes the job. [97] [98]
- A reconciler compares desired state with each host and repairs drift carefully. [160]
- Draining uses live migration, which by default expects shared storage and compatible hosts. [94] [95]
:::

:::glossary
- **Filter**: a test that removes hosts that cannot take a VM.
- **Weigher**: a scoring rule that ranks the hosts left after filtering.
- **Anti-affinity**: a rule that members of a group must run on different hosts.
- **Idempotent**: giving the same result whether it runs once or several times.
- **Overlay**: a qcow2 disk that stores only the changes on top of a shared, read-only base image.
- **Orphan**: a VM running on a host that the database does not know about.
- **Reconciler**: a loop that compares what should exist with what does exist and fixes differences.
- **Live migration**: moving a running VM to another host while it keeps running.
- **Drain**: moving every VM off a host so it can be maintained.
:::
