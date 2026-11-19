---
id: l30
title: "KVM, QEMU, Vagrant and cloud-init"
quiz: quiz-01.yaml
resources: [../resources/ch11/Vagrantfile, ../resources/ch11/user-data.yaml]
sources: [86, 87, 88, 89, 90, 91, 99, 100, 101, 102, 104]
---
After this lesson you can explain how KVM, QEMU and libvirt stack up on a hypervisor host, check a host for KVM support, build a qcow2 overlay disk, and describe a dev VM with Vagrant and a first-boot configuration with cloud-init.

## The stack, bottom to top

| Layer | Job |
| --- | --- |
| CPU extensions | Intel VT or AMD-V (SVM) let a guest run directly on the host CPU [104]. |
| KVM | Kernel modules: `kvm.ko` for the core, plus `kvm-intel.ko` or `kvm-amd.ko` [87]. In mainline Linux since 2.6.20 [87]. |
| `/dev/kvm` | The device a user-space program opens to talk to KVM [86]. |
| QEMU | User-space emulator that models the machine (memory, disks, network cards) and asks KVM to run the CPU [89] [104]. |
| libvirt | A management API and daemon over QEMU and others (lesson l31) [89]. |
| Vagrant, your provisioning service | Call libvirt or QEMU to create machines for people. |

The KVM API is a set of `ioctl` calls: open `/dev/kvm`, `KVM_CREATE_VM` returns a VM file descriptor, `KVM_CREATE_VCPU` on that returns a vCPU descriptor, and `KVM_RUN` runs one vCPU [86]. A new VM has no vCPUs and no memory until user space adds them [86]. That user space is QEMU, which is why a running VM is an ordinary Linux process you can see in `top` and stop with `kill` [104].

**Containers versus VMs.** A container is an isolated process sharing the host kernel; a VM boots its own kernel on virtual hardware, so it isolates more strongly and starts more slowly [102]. Chapter 7 covers containers; a typical private cloud runs containers inside VMs [102].

## Does this host support KVM?

```bash
egrep '^flags.*(vmx|svm)' /proc/cpuinfo    # prints lines if the CPU has VT [104]
ls -l /dev/kvm                             # the device must exist too
kvm-ok                                     # Ubuntu, package cpu-checker [88]
```

`kvm-ok` checks both: the CPU flags, then `/dev/kvm`, and as root whether the BIOS disabled VT; it exits 0 when KVM is usable [88]. Both checks matter. In a Debian container in the course's test run, the flags were there and the device was not:

```text
$ egrep -c '^flags.*(vmx|svm)' /proc/cpuinfo
8
$ ls -l /dev/kvm
ls: cannot access '/dev/kvm': No such file or directory
```

Users need access to `/dev/kvm`, usually through a `kvm` group [104].

## QEMU: KVM or TCG

QEMU is a machine emulator and virtualizer [89]. It can fully emulate a CPU with TCG, its Tiny Code Generator, or hand the CPU to an accelerator such as KVM [89]. **TCG is the default**, so you must request a hardware accelerator explicitly, or the guest runs under pure emulation [89]. The docs' example selects one with `-accel tcg` [89]; their accelerator table names KVM as the Linux choice [89]. libvirt picks the accelerator from the domain type, as lesson l31 shows.

For devices, prefer **virtio**: paravirtualized devices designed to be cheap to emulate, recommended unless you are testing a driver for real hardware [90].

## Disks: qcow2 and qemu-img

qcow2 is QEMU's own format: it grows as data is written, supports compression and snapshots, and can sit on a **backing file** [91]. An overlay stores only its differences from the base, and the base is never modified unless you run `commit` [91]. That is how one golden image serves hundreds of VMs. Run in the test container (qemu-img 7.2):

```bash
qemu-img create -f qcow2 base.qcow2 10G
qemu-img create -f qcow2 -b base.qcow2 -F qcow2 vm-demo-01.qcow2
qemu-img info --backing-chain vm-demo-01.qcow2
```

```text
image: vm-demo-01.qcow2
file format: qcow2
virtual size: 10 GiB (10737418240 bytes)
disk size: 196 KiB
backing file: base.qcow2
backing file format: qcow2
```

| Command | Use |
| --- | --- |
| `qemu-img info [--backing-chain]` | format, virtual vs real size, backing file [91] |
| `qemu-img convert -O qcow2 in.vmdk out.qcow2` | change format; `-c` compresses [91] |
| `qemu-img resize disk.qcow2 +10G` | grow; then grow the partition inside the guest; shrinking needs `--shrink` [91] |
| `qemu-img snapshot -l / -c / -a / -d` | list, create, apply, delete internal snapshots [91] |
| `qemu-img commit` / `rebase` | merge an overlay into its base / change the base [91] |

Never run `qemu-img` on an image a running VM is using; it can destroy it [91].

## Vagrant

Vagrant is a command-line tool for the lifecycle of development VMs [99]. One `Vagrantfile` per project, written in Ruby syntax, committed to Git [99]. The current version is 2.4.9 [99]. Its licence is in flux: the 2.4.9 release ships under the Business Source License, while the development branch now carries MIT-style terms [99].

A **box** is the packaged base image, and boxes are provider-specific [99]. VirtualBox, Hyper-V and Docker providers ship with Vagrant; others are plugins [99]. **vagrant-libvirt** adds a libvirt provider, supporting KVM and QEMU only [100].

`resources/ch11/Vagrantfile`, line by line:

| Setting | Effect |
| --- | --- |
| `config.vm.box = "fedora/36-cloud-base"` | the base box, the one from the vagrant-libvirt quickstart [100] |
| `config.vm.network "forwarded_port", guest: 8000, host: 8080, host_ip: "127.0.0.1"` | guest port 8000 at host `127.0.0.1:8080`; without `host_ip` most providers bind all interfaces [99] |
| `config.vm.synced_folder ".", "/vagrant", disabled: true` | turns off the default share [99] |
| `config.vm.provider :libvirt do lv` | `memory` (MB), `cpus`, `cpu_mode`, `disk_bus`, `nic_model_type`; the defaults are 512 MB, 1 CPU, `host-model`, virtio [100] |
| `config.vm.provision "shell", inline:` | runs as root on the first `up` and on `vagrant provision` [99] |

| Command | Does |
| --- | --- |
| `vagrant up --provider=libvirt` | create, boot, provision [99] [100] |
| `vagrant ssh [-c cmd]` | shell or one command in the VM [99] |
| `vagrant provision` | re-run provisioners [99] |
| `vagrant halt [-f]` | graceful shutdown, power off if that fails [99] |
| `vagrant destroy -f` | delete the VM, not the box [99] |
| `vagrant status` | running, suspended, not created [99] |

The file passed `ruby -c` (Ruby 3.3) in the test run: `Syntax OK`.

## cloud-init

cloud-init configures a machine on first boot: hostname, network, users, SSH keys, packages, scripts [101]. It reads its input from a **datasource**: meta-data from the platform, user-data from you [101]. For a private KVM cloud the simple choice is **NoCloud**: a small ISO labelled `cidata` holding `user-data` and `meta-data`, attached to the VM [101]. `meta-data` must contain an `instance-id` [101].

`resources/ch11/user-data.yaml` starts with `#cloud-config`, then sets the hostname, creates user `ops` with an SSH key and passwordless sudo, installs packages and runs two `runcmd` commands. **Replace the sample key with your own public key first**: the file locks the password and disables password SSH, so with the sample key nobody can log in. `runcmd` runs on the first boot only; `bootcmd` runs on every boot [101]. Boot stages run in order: detect, local, network, config, final [101]. `cloud-init status --wait` blocks until it is done [101].

The schema check passed in an Ubuntu 24.04 container with cloud-init 26.2:

```text
$ cloud-init schema --config-file user-data.yaml
Valid schema user-data.yaml
```

Build the seed ISO (the comment at the top of the file also creates `meta-data`) and an overlay disk on the base image [101] [91]:

```bash
genisoimage -output vm-demo-01-seed.iso -volid cidata -joliet -rock user-data meta-data
qemu-img create -f qcow2 -b base.qcow2 -F qcow2 vm-demo-01.qcow2
```

## Gotchas

- **CPU flags but no `/dev/kvm`.** A container, a missing module or VT disabled in the BIOS; check both. [88] [104]
- **Forgetting the accelerator.** Plain `qemu-system-x86_64` defaults to TCG emulation. [89]
- **Changing a base image.** Overlays store only their differences, so every VM on that base sees the change; treat bases as read-only. [91]
- **Changed user-data ignored.** cloud-init keys first boot on `instance-id`; change it or start from a fresh disk. [101]
- **Box for the wrong provider.** A VirtualBox box will not boot under libvirt. [99]

:::low-confidence
Nothing here ran on KVM: the course's test machine has no `/dev/kvm`. `qemu-img`, the CPU-flag check, `ruby -c` and `cloud-init schema` ran in containers as shown; `vagrant up` and booting with the seed ISO did not. The `fedora/36-cloud-base` box comes from the vagrant-libvirt quickstart and is old; pick a current box built for libvirt. The notes do not say which flag belongs to which vendor, so check `vmx` and `svm` against your CPU vendor's documentation. The licence wording comes from the repository's LICENSE files, with no announcement explaining the change.
:::

:::key-takeaways
- KVM is kernel modules plus `/dev/kvm`; QEMU is the user-space process that models the machine. [86] [87] [104]
- QEMU defaults to TCG; request KVM or you get emulation. [89]
- qcow2 overlays on a read-only base give fast, thin VM disks. [91]
- Vagrant describes dev VMs in a Vagrantfile; vagrant-libvirt runs them on KVM. [99] [100]
- cloud-init applies user-data on first boot per `instance-id`; NoCloud is an ISO labelled `cidata`. [101]
:::

:::glossary
- **KVM**: the Linux kernel feature that lets a normal process run a virtual machine's CPU on real hardware.
- **QEMU**: the program that pretends to be a whole computer, with disks and network cards, for a guest operating system.
- **TCG**: QEMU's pure software CPU emulation, used when no hardware acceleration is requested.
- **virtio**: a family of virtual devices designed for virtual machines, faster than imitating real hardware.
- **qcow2**: QEMU's disk image format that grows on demand and can sit on top of a base image.
- **Backing file**: the read-only base image underneath an overlay disk.
- **Box**: Vagrant's packaged base image for one provider.
- **Provider**: the virtualization product Vagrant drives, such as VirtualBox or libvirt.
- **Datasource**: where cloud-init finds its configuration on a given platform.
- **NoCloud**: a cloud-init datasource that reads configuration from a local disk or ISO.
:::
