---
id: l31
title: "libvirt: domains, virsh and the Python bindings"
quiz: quiz-02.yaml
resources: [../resources/ch11/domain.xml, ../resources/ch11/provision_vm.py]
sources: [92, 93, 94, 95, 96, 97, 98]
---
After this lesson you can read and write libvirt domain XML, drive a VM through its lifecycle with `virsh`, explain pools, networks, snapshots and live migration, and write an idempotent define-and-start script with the Python bindings.

## What libvirt is

libvirt is a toolkit with a stable API, usable from C, Python, Go and more, for managing KVM, QEMU, Xen, LXC and other platforms [92]. Its words: a **node** is one physical machine, a **hypervisor** turns it into virtual machines, and a **domain** is one guest [92]. It covers one node at a time (migration is the exception) and leaves policies such as load balancing to tools built on top [92]. Your provisioning service is such a tool.

## Daemons and connection URIs

| Layout | Daemons |
| --- | --- |
| Monolithic | one `libvirtd` for every driver, config in `/etc/libvirt/libvirtd.conf` [92] |
| Modular | one daemon per driver: `virtqemud` for QEMU/KVM, `virtnetworkd`, `virtstoraged` and others, plus `virtproxyd` for remote access [92] |

New distributions are likely to use modular mode; `systemctl is-active virtqemud.socket` or `libvirtd.socket` tells you which is live [92]. In both, `virtlogd` keeps QEMU logs and `virtlockd` holds disk locks; do not stop them while VMs run [92].

A client picks a driver and host with a URI [92]:

| URI | Meaning |
| --- | --- |
| `qemu:///system` | local system daemon, running as root [92] |
| `qemu:///session` | a per-user daemon with your own UID [92] |
| `qemu+ssh://root@kvm-017/system` | a remote host, tunnelled over SSH [92] |
| `test:///default` | the test driver from the docs' `virsh -c test:///default list` example [92]; in the test run it needed no hypervisor |

With no URI, libvirt uses `LIBVIRT_DEFAULT_URI`, then the client config, then probes [92]. A read-write `qemu:///system` connection is equivalent to a root shell [92], so guard whoever holds one.

## Domain XML

`resources/ch11/domain.xml` describes a two-vCPU, 2 GiB guest. The parts that matter:

| Element | Meaning |
| --- | --- |
| `<domain type='kvm'>` | which hypervisor: `kvm`, `qemu` and others [93] |
| `<name>`, `<uuid>` | unique short name; a UUID is generated if missing [93] |
| `<memory unit='KiB'>`, `<currentMemory>` | maximum at boot and current allocation (lower means ballooning) [93] |
| `<vcpu>` | maximum vCPUs; `current=` starts fewer [93] |
| `<os><type>hvm</type>`, `<boot dev='hd'/>` | full virtualization, boot from disk [93] |
| `<features><acpi/>` | needed for graceful shutdown of KVM guests [93] |
| `<cpu mode='host-model'/>` | copy the host CPU model; `host-passthrough` exposes the exact host CPU but ties the guest to that hardware [93] |
| `<disk type='file' device='disk'>` + `<driver type='qcow2' cache='none'/>` + `<target dev='vda' bus='virtio'/>` | the qcow2 overlay on virtio; `dev` is only an ordering hint [93] |
| `<disk device='cdrom'>` + `<readonly/>` | the cloud-init seed ISO from lesson l30 [93] |
| `<interface type='network'><source network='default'/>` | the NAT network, 192.168.122.0/24 [93] |
| `<console type='pty'>` | serial console for `virsh console` [93] |

The file passed `virt-xml-validate` in the test run (libvirt 9.0, Debian 12): `domain.xml validates`.

## Lifecycle: transient and persistent

A **persistent** domain is defined first, then started, and survives shutdown as "defined" [94]. A **transient** domain is created and started in one step and disappears when it stops [94]. States: undefined, defined (shut off), running, paused, saved [94]. This session ran against the test driver; one `virsh` process keeps its state across `;`. Output condensed (blank lines removed):

```bash
virsh -c test:///default "define domain.xml; list --all; start vm-demo-01; list --all; suspend vm-demo-01; domstate vm-demo-01; resume vm-demo-01; shutdown vm-demo-01; domstate vm-demo-01; start vm-demo-01; destroy vm-demo-01; domstate vm-demo-01; undefine vm-demo-01; list --all"
```

```text
Domain 'vm-demo-01' defined from domain.xml
 Id   Name         State
-----------------------------
 1    test         running
 -    vm-demo-01   shut off
Domain 'vm-demo-01' started
 Id   Name         State
----------------------------
 1    test         running
 2    vm-demo-01   running
Domain 'vm-demo-01' suspended
paused
Domain 'vm-demo-01' resumed
Domain 'vm-demo-01' is being shutdown
shut off
Domain 'vm-demo-01' started
Domain 'vm-demo-01' destroyed
shut off
Domain 'vm-demo-01' has been undefined
 Id   Name   State
----------------------
 1    test   running
```

The test driver has no guest OS, so `shutdown` completes at once; a real guest takes time, or ignores the request.

| Verb | Effect |
| --- | --- |
| `define FILE` / `create FILE` | register persistent, not started / create and start transient [95] |
| `start`, `shutdown`, `reboot` | boot; ask the guest OS to stop (not guaranteed, returns before it finishes) [95] |
| `destroy` | immediate power-off; storage is kept, a persistent domain can start again [95] |
| `suspend` / `resume` | stop scheduling it, keeping RAM / continue [95] |
| `save` / `restore` / `managedsave` | RAM to a file and stop; disks are not saved [95] |
| `undefine` | remove the config of a stopped domain; on a running one it becomes transient [95] |
| `dumpxml`, `edit` | print the XML; edit it for the next boot [95] |
| `autostart`, `console`, `dominfo`, `domstate` | start at host boot, serial console (exit with `^]`), details, state [95] |
| `setmem --live` / `--config` | change the running guest / the next start [95] |

## Storage pools and networks

A **storage pool** is storage set aside for VMs, split into **volumes** that become guest disks [96]. Types include `dir`, `fs`, `netfs`, `logical` (LVM), `iscsi` and `rbd` [96]. `pool-list`, `vol-create-as POOL NAME 20G --format qcow2 --backing-vol base.qcow2 --backing-vol-format qcow2`, `vol-list`, `vol-delete` [95]. `pool-destroy` stops a pool and keeps data; `pool-delete` destroys the underlying storage [95].

A **virtual network** is a software switch, by default `virbr0` [96]. The default network is NAT: guests reach out through the host's address, outsiders cannot connect in; `dnsmasq` serves DHCP and DNS [96]. Routed and isolated modes exist, and `forward mode='bridge'` uses an existing host bridge [96]. `net-list --all`, `net-dhcp-leases default`, `net-autostart` [95].

## Snapshots and migration

`snapshot-create-as DOM NAME` captures disk, memory and device state; `--disk-only --quiesce` freezes guest filesystems through the guest agent [95]. `snapshot-list`, `snapshot-revert` (destructive: later changes are lost), `snapshot-delete` [95].

**Live migration** copies memory while the guest keeps running and switches once the copies match [94]. It needs shared storage at the same paths (or `--copy-storage-all`), matching hypervisor versions and network, and a destination CPU with the same or more features [94] [96]:

```bash
virsh migrate --live --persistent --undefinesource web1 qemu+ssh://kvm-018/system
```

`--persistent` defines it on the destination and `--undefinesource` removes it from the source; by default neither host's config changes [95] [96]. The stream carries full guest RAM, so use a separate network or the encrypted `--p2p --tunnelled` transport [96]. libvirt may refuse disks not using `cache='none'` [95].

## Python bindings

The `libvirt` module is generated from the C API: `virDomainCreate(dom)` becomes `dom.create()`, `virDomainDefineXML(conn, xml)` becomes `conn.defineXML(xml)`, and errors raise `libvirt.libvirtError` [97]. These Python names follow the documented naming rule from the C prototypes [97]. `createXML` makes a transient guest, `defineXML` a persistent one, and `defineXML` also turns a running transient guest persistent [98].

`resources/ch11/provision_vm.py` makes "this VM exists and runs" safe to repeat:

1. Read `<name>` from the XML.
2. `conn.listAllDomains()` [97]; if the name is absent, `defineXML`; if it is transient, `defineXML` again to make it persistent [98].
3. If `dom.isActive()` is false, `dom.create()` [97].

Matching names with `listAllDomains()` instead of catching any `libvirtError` from `lookupByName` means a dropped connection is reported as an error, not mistaken for "no such VM". A paused domain counts as active, so the script leaves it paused.

The test driver starts fresh in every process, with one running domain called `test`, so a second command-line run would define again. To see idempotency, call the function twice on one connection. In a Debian 12 container (`apt-get install libvirt-clients python3-libvirt`), next to the two files:

```python
import libvirt
import provision_vm

xml = open("domain.xml").read()
conn = libvirt.open("test:///default")
print("run 1:", provision_vm.ensure_running(conn, xml))
print("run 2:", provision_vm.ensure_running(conn, xml))
conn.lookupByName("vm-demo-01").destroy()
print("run 3:", provision_vm.ensure_running(conn, xml))
```

```text
run 1: ['defined', 'started']
run 2: ['already running']
run 3: ['started']
```

A second check started the domain as a transient guest with `createXML` and then called the function: it returned `['made persistent', 'already running']`.

The fixed `<uuid>` matters: without it, redefining over the running transient guest failed with `domain 'vm-demo-01' already exists with uuid ...`, because each define generated a new UUID.

## Gotchas

- **`destroy` sounds final.** It only pulls the power; `undefine` removes the definition. [95]
- **`shutdown` returns early.** It is asynchronous and the guest may ignore it; poll `domstate`. [95]
- **`create` for a long-lived VM.** It makes a transient domain that vanishes at the first stop. [94] [95]
- **Read-write system URI.** Root-equivalent; restrict who holds it. [92]
- **Migration without `--persistent`.** The guest runs on the destination with no saved config there. [96]
- **Sharing `/etc/libvirt` between hosts.** The docs say never to. [96]

:::low-confidence
Nothing ran on KVM: the course's test machine has no `/dev/kvm`. `virsh`, `virt-xml-validate` and `provision_vm.py` ran in a Debian 12 container (libvirt 9.0, Python 3.11) against the test driver, which accepted `type='kvm'` without starting anything. The pool, volume, network and migration commands are from the virsh man page and libvirt docs, not tested. The Python method names are derived from the C prototypes by the naming rule; the readthedocs guide that confirms `create()` is a community site with typos. The notes do not give the `listAllDomains` filter flags or numeric state values, so the script avoids them.
:::

:::key-takeaways
- libvirt manages domains on one node through daemons reached by URI; `qemu:///system` is root-equivalent. [92]
- Domain XML is the whole VM: type, name, UUID, memory, vCPUs, disks, NICs, console. [93]
- `define` + `start` for persistent VMs; `destroy` is a power cut, `undefine` forgets the config. [94] [95]
- Live migration needs shared or copied storage, matching CPUs and `--persistent --undefinesource` to move the config. [94] [95] [96]
- Idempotent provisioning: look up by name, define if missing, start if not active, with a fixed UUID. [97] [98]
:::

:::glossary
- **Domain**: libvirt's name for one virtual machine.
- **Node**: one physical host in libvirt's vocabulary.
- **Connection URI**: a string that tells libvirt which driver and which host to talk to.
- **Persistent**: a domain whose definition is stored and survives shutdown.
- **Transient**: a domain that exists only while it runs.
- **Storage pool**: storage that libvirt manages for VMs, divided into volumes.
- **Virtual network**: a software switch on the host, such as `virbr0`, that guests plug into.
- **Live migration**: moving a running VM to another host while it keeps running.
- **Idempotent**: safe to run again; a repeat leaves the system in the same state.
:::
