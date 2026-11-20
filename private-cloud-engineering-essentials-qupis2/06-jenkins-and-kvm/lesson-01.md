---
id: l14
title: "Jenkins pipelines and KVM in brief"
quiz: quiz-14.yaml
resources: [../resources/ch06/Jenkinsfile, ../resources/ch06/domain.xml]
sources: [86, 87, 89, 92, 93, 94, 95, 104, 143, 144, 146, 148, 149, 151]
---
After this lesson you can read a Declarative `Jenkinsfile`, explain how KVM, QEMU and libvirt stack up, and drive a VM with `virsh`.

## Jenkins: who does the work

| Term | What it is |
| --- | --- |
| Controller | stores configuration, serves the UI, decides where tasks run [148] [149] |
| Agent | a small Java client that connects to the controller and runs tasks [149] |
| Executor | a slot on a node; the count is how many tasks run at once [149] |
| Label | text grouping agents by capability, such as `docker` [148] |

By default builds run on the built-in node, inside the controller, with its file access; set its executors to 0 [151].

## Declarative skeleton

```groovy
pipeline {                       // required
    agent any                    // required: any, none, label 'x', docker
    stages {                     // required
        stage('Build') {
            steps { sh 'make' }  // required in a stage
        }
    }
    post { always { echo 'done' } }
}
```

Walk through `resources/ch06/Jenkinsfile`:

- `agent none` at the top, so each stage picks its own agent [143].
- `Test` runs two stages in `parallel`, with `failFast true` [143].
- `REGISTRY = credentials('registry-push')` binds a username/password credential as `REGISTRY_USR` and `REGISTRY_PSW` [143] [144].
- `Deploy` has `when` with `branch 'main'` and `beforeAgent true`: only `main`, checked before grabbing an agent [143]. `branch` works only in a Multibranch Pipeline, one job per branch [143] [146].

`post` conditions include `always`, `changed`, `fixed` (success after a failure), `regression` (failure after a success), `failure`, `success`, and `cleanup`, which runs last [143].

## The virtualization stack

| Layer | Job |
| --- | --- |
| Intel VT / AMD-V | let guest code run on the real CPU [104] |
| KVM | kernel modules `kvm.ko` plus `kvm-intel.ko` or `kvm-amd.ko`, exposed as `/dev/kvm` [86] [87] |
| QEMU | user-space process that models memory, disks and NICs; each VM is one QEMU process [89] [104] |
| libvirt | management API and daemon for one host [92] |

```bash
egrep '^flags.*(vmx|svm)' /proc/cpuinfo   # CPU has VT? [104]
ls -l /dev/kvm                            # KVM usable? Both must pass
```

QEMU defaults to TCG, pure software emulation, so a hardware accelerator such as KVM must be requested [89]; libvirt picks it from `<domain type='kvm'>` [93].

## libvirt and virsh

URIs: `qemu:///system` (root daemon) or `qemu+ssh://root@kvm-017/system` (remote); read-write, it equals a root shell [92].

`resources/ch06/domain.xml` describes a 2-vCPU, 2 GiB guest [93]:

| Element | Meaning |
| --- | --- |
| `<domain type='kvm'>`, `<name>`, `<uuid>` | hypervisor, unique name, fixed id |
| `<memory>`, `<vcpu>` | maximum RAM and vCPUs |
| `<cpu mode='host-model'/>` | copy the host CPU model (portable) |
| `<disk>` with `type='qcow2'`, `bus='virtio'` | the overlay disk |
| `<interface type='network'>` `default` | the NAT network |

A **persistent** domain is defined, then started; a **transient** one is created and vanishes when it stops [94].

| Verb | Effect [95] |
| --- | --- |
| `define FILE` / `create FILE` | register persistent / create and start transient |
| `start`, `shutdown` | boot; ask the guest to stop (asynchronous, may be ignored) |
| `destroy` | power cut; storage and definition kept |
| `undefine` | remove the stored config |
| `list --all`, `domstate`, `dumpxml`, `console` | inspect |

Try it in `resources/ch06` with no hypervisor (5 minutes) [92]:

```bash
virsh -c test:///default "define domain.xml; start vm-demo-01; domstate vm-demo-01; destroy vm-demo-01; undefine vm-demo-01; list --all"
```

:::low-confidence
Nothing here ran on KVM: the course's test machine has no `/dev/kvm`; `virsh` ran against the test driver. The Jenkinsfile was linted, not run end to end; its `ruff`, `pytest` and `deploy.sh` commands are assumptions about the service repository. The notes do not say which flag belongs to which vendor; check `vmx` and `svm` against your CPU vendor's documentation.
:::

:::key-takeaways
- The controller schedules; agents with executors do the work; give the built-in node 0 executors. [149] [151]
- Declarative needs `pipeline`, `agent`, `stages`, `stage`, `steps`. [143]
- KVM is kernel modules plus `/dev/kvm`; QEMU models the machine and defaults to TCG. [86] [89]
- `define` + `start` for persistent VMs; `destroy` is a power cut, `undefine` forgets the config. [94] [95]
:::
