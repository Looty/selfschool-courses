---
id: l14
title: "Jenkins pipelines and KVM in brief"
quiz: quiz-14.yaml
resources: [../resources/ch06/Jenkinsfile, ../resources/ch06/domain.xml]
sources: [86, 87, 89, 92, 93, 94, 95, 104, 143, 146, 149]
---
After this lesson you can read a Declarative `Jenkinsfile`, predict its `post` blocks, place KVM, QEMU and libvirt, and drive a VM with `virsh`.

## Declarative skeleton: pipeline, agent, stages, steps, post

**Rule:** a Declarative pipeline is nested boxes: `pipeline` holds `agent` (where), `stages` (what, in order) and `post` (after) [143]. The **controller** schedules; **agents** run the steps [149].

```groovy
// rung 1: the smallest valid file
pipeline {
    agent any                       // any free agent
    stages {
        stage('Build') { steps { sh 'make' } }
    }
}

// rung 2: a second stage, and post after all stages
        stage('Test')  { steps { sh 'make check' } }
    post { always { echo 'done' } }

// rung 3: agent none at the top -> every stage names its own
    agent none
    stage('Test') {
        agent { label 'docker' }
        steps { sh 'make check' }
    }

// rung 4: deploy only from main, checked before taking an agent
    stage('Deploy') {
        when {
            beforeAgent true
            branch 'main'
        }
        agent { label 'deploy' }
        steps { sh './deploy.sh' }
    }
```

Rungs 2 to 4 show only the changed part.

Edge case: `branch` works only in a Multibranch Pipeline, one job per branch [143] [146]. In a plain Pipeline job (course test run), the stage never ran:

```text
Stage "Deploy" skipped due to when conditional
```

**P1.** You delete the `when { branch 'main' }` line from a Multibranch job. Which branches deploy now?

:::answer
Every branch the job builds.
:::

## `post` conditions: compare with the last run

**Rule:** `always` and `cleanup` always run; `success`/`failure` look at this run; `changed`, `fixed` and `regression` compare it with the previous run [143].

| Previous → this run | Which of these seven run [143] |
| --- | --- |
| SUCCESS → SUCCESS | always, success, cleanup |
| FAILURE → FAILURE | always, failure, cleanup |
| SUCCESS → FAILURE | always, changed, regression, failure, cleanup |
| FAILURE → SUCCESS | always, changed, fixed, success, cleanup |

Hook: **fixed** = back to green; **regression** = fell back to red. `cleanup` runs last [143].

**P2.** The previous run failed and this one failed too. Does `changed` run? Does `fixed`?

:::answer
Neither: the status did not change, and `fixed` needs a success.
:::

## KVM vs QEMU vs libvirt: who does what

**Rule:** KVM runs the guest's CPU in the kernel, QEMU builds the rest of the machine as a process, and libvirt manages VMs on one host [86] [89] [92].

| Layer | Is | Job |
| --- | --- | --- |
| Intel VT / AMD-V | CPU feature | let guest code run on the real CPU [104] |
| KVM | kernel modules `kvm.ko` + `kvm-intel.ko` or `kvm-amd.ko` [87] | exposed as `/dev/kvm` [86] |
| QEMU | user-space process | models memory, disks, NICs; one process per VM [89] [104] |
| libvirt | API and daemon | define, start, stop VMs on one host [92] |

```bash
egrep -c '^flags.*(vmx|svm)' /proc/cpuinfo   # 8 lines: the CPU has VT
ls -l /dev/kvm                               # No such file or directory
```

The course's test container: flags present, device missing, no KVM. Both checks must pass [104].

Edge case: QEMU defaults to TCG, pure software emulation; KVM must be requested [89]. libvirt requests it with `<domain type='kvm'>` [93].

**P3.** `/dev/kvm` is missing, yet QEMU starts the VM. Why, and how will it feel?

:::answer
It runs on TCG, QEMU's default software emulation, not KVM: it works, but slowly.
:::

## virsh verbs: define, start, destroy, undefine

**Rule:** a **persistent** domain is defined first, then started, and is remembered after it stops; a **transient** one is created and started at once and vanishes when it stops [94].

Ladder from `resources/ch06` on libvirt's test driver, no hypervisor needed (test run, condensed) [92] [95]:

```text
virsh -c test:///default "define domain.xml; start vm-demo-01; shutdown vm-demo-01; start vm-demo-01; destroy vm-demo-01; undefine vm-demo-01; list --all"
define domain.xml     Domain 'vm-demo-01' defined     -> shut off
start vm-demo-01      Domain 'vm-demo-01' started     -> running
shutdown vm-demo-01   Domain 'vm-demo-01' is being shutdown -> shut off
start vm-demo-01      Domain 'vm-demo-01' started     -> running
destroy vm-demo-01    Domain 'vm-demo-01' destroyed   -> shut off (still listed)
undefine vm-demo-01   Domain 'vm-demo-01' has been undefined -> gone
```

Edge case: the test driver has no guest OS, so `shutdown` was instant; a real guest may take time or ignore it [95].

| Verb | Sounds like | Really [95] |
| --- | --- | --- |
| `shutdown` | stop now | asks the guest OS; asynchronous, may be ignored |
| `destroy` | delete | pulls the power; storage and definition kept |
| `undefine` | stop | removes the stored config |
| `create FILE` | define | starts a transient VM that vanishes when stopped |

**P4.** You run `virsh destroy web1`. Can you `virsh start web1` afterwards?

:::answer
Yes: `destroy` only cut the power; the definition stays.
:::

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| `when { branch }` | Multibranch only | plain job → skipped |
| `fixed` / `regression` | red→green / green→red | FAILURE → SUCCESS → `fixed` |
| `/dev/kvm` | must exist | missing → no KVM |
| `destroy` | power cut | domain stays defined |
| `undefine` | forget config | gone from `list --all` |

## If you missed a quiz question

**If you thought** `fixed`/`regression` swapped: reread "`post`". **R1.** SUCCESS → FAILURE runs?

:::answer
`regression`, plus `always`, `changed`, `failure`, `cleanup`.
:::

**If you thought** KVM emulates disks: reread "KVM vs QEMU". **R2.** Who models disks?

:::answer
QEMU: KVM only runs the CPU.
:::

**If you thought** `destroy` deletes the VM: reread "virsh verbs". **R3.** Which verb forgets the config?

:::answer
`undefine`: it removes the stored config.
:::

**If you thought** `agent none` means the controller: reread "Skeleton". **R4.** What does `agent none` allocate?

:::answer
Nothing: each stage must declare its own agent.
:::

:::low-confidence
Nothing ran on KVM (no `/dev/kvm` on the test machine); `virsh` used the test driver; the Jenkinsfile was only linted. The notes do not say which of `vmx` and `svm` is which vendor's flag; check your CPU vendor's documentation.
:::

:::key-takeaways
- Declarative: `pipeline`, `agent`, `stages`, `steps`; `branch` needs Multibranch; `fixed` is red to green. [143]
- KVM runs the CPU; QEMU models the machine, TCG by default; libvirt manages one host. [86] [89] [92]
- `destroy` is a power cut; `undefine` forgets the config. [95]
:::

:::glossary
- **Controller**: the central Jenkins server that schedules work.
- **Agents**: machines or containers that run build steps.
- **Multibranch Pipeline**: a job type with one pipeline per branch.
- **KVM**: the Linux kernel part that runs a guest's CPU on the hardware.
- **QEMU**: the program that pretends to be the rest of the computer for each VM.
- **TCG**: QEMU's slow, software-only way of running guest code.
- **libvirt**: a library and daemon that manages VMs on one host.
- **Domain**: libvirt's word for one virtual machine.
- **virsh**: libvirt's command-line tool.
:::
