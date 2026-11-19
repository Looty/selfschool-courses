---
id: l25
title: "Designing a self-service VM provisioning service"
quiz: quiz-01.yaml
resources: [../resources/ch09/vm-provisioning.svg]
sources: [50, 52, 58, 92, 120, 155, 156, 157, 158]
---
After this lesson you can run a 30 to 40 minute whiteboard design session with a fixed routine, and use it to design a private-cloud service where engineers request VMs through an API and workers build them on KVM hosts.

## The routine

A design session goes wrong in two ways: you draw boxes before you know the load, or you spend 25 minutes on requirements and never reach failures. A fixed routine with a clock prevents both.

| Step | Minutes | What you produce |
| --- | --- | --- |
| 1. Requirements and scale | 5 to 7 | functional list, non-functional targets, three or four numbers |
| 2. API | 3 to 5 | endpoints, status codes, one example request |
| 3. Components | 5 to 7 | boxes and arrows, one sentence of ownership per box |
| 4. One request end to end | 5 | numbered walk through the boxes |
| 5. Failure modes | 5 to 8 | what breaks at each arrow, and the fix |
| 6. Scaling and operations | 3 to 5 | what grows first, what you measure |

The rest of this lesson applies steps 1 to 4 to one problem. The next lesson goes deep on step 5 and parts of step 6.

## Step 1: requirements and scale

**The prompt.** About a thousand engineers want VMs on demand. The company runs a few hundred KVM hypervisors holding a couple of thousand VMs.

| Functional | Non-functional (targets you propose and defend) |
| --- | --- |
| create a VM from an image and a flavour (a named size: vCPUs, RAM, disk) | create to SSH-able in under 5 minutes at p95 |
| read its state and IP; list my project's VMs | the API stays up when some hypervisors are down |
| delete one; enforce per-project quotas | never one IP for two VMs; never place beyond the overcommit policy |
| inject the user's SSH key | database and hypervisors agree within minutes, even after crashes |
| out of scope: resize, snapshots, web console | |

**Back-of-envelope numbers.** Assume 300 hosts, each with 32 physical cores and 256 GiB of RAM, 8 GiB of it reserved for the host. The average VM is 4 vCPUs and 8 GiB.

| Quantity | Working | Result |
| --- | --- | --- |
| Create requests | 1000 engineers × 2 per working day | ~2000 a day, ~0.07 per second over 8 hours |
| Burst | a CI pipeline asking for 50 VMs at once | ~1 per second for a minute |
| Status reads | a client polls every 5 s for 3 minutes | ~36 GETs per create, ~72,000 a day |
| VMs per host now | 2000 / 300 | ~7 |
| Capacity, no overcommit | CPU: 32 / 4 = 8; RAM: 248 / 8 = 31; take the smaller | 8 per host, 2400 in total |
| Capacity, CPU ratio 4.0 | CPU: 128 / 4 = 32; RAM still 31 | 31 per host, ~9300 in total |

Two conclusions follow. The API load is tiny: one relational database handles it easily, so the hard parts are correctness and the slow work on the hosts. And without CPU overcommit the fleet is 83% allocated: 400 free slots is thin headroom when a failed rack, hosts drained for patching and a month of growth all draw on it. OpenStack Nova, the open-source compute service used as a reference in this chapter, multiplies capacity by an allocation ratio per resource; its current initial defaults are 4.0 for CPU, 1.0 for RAM and 1.0 for disk [155] [156]. The formula (total minus reserved) × ratio is this course's working model; the Nova pages read do not state it.

The price of CPU overcommit is contention: at 4.0, four busy vCPUs share one core, and VMs slow down when many are busy at once. Memory overcommit fails harder: when a Linux host runs out of memory, by default the OOM killer picks a process and kills it [120], and each guest is a QEMU process on the host [92]. So RAM stays at 1.0, and the CPU ratio rises only while measured contention stays low.

## Step 2: the API

Creating a VM takes minutes, so the create call must not wait for it. HTTP has a status for this: 202 Accepted means the request was accepted for processing but the processing has not been completed, and the response ought to point to a status monitor [52]. The VM resource itself is that monitor. This is the chapter 8 lab grown up: the same 202-and-poll contract, but with a relational database instead of Redis hashes, and a DELETE that also answers 202, because removing a real VM is slow work too.

```http
POST /v1/vms
Idempotency-Key: "8e03978e-40d5-43e8-bc93-6894a57f9324"
Content-Type: application/json

{"name": "build-01", "project": "ci", "image": "debian-13-v4", "flavor": "m.4x8", "ssh_key": "ssh-ed25519 AAAA..."}

HTTP/1.1 202 Accepted
Location: /v1/vms/7f3a
{"id": "7f3a", "state": "BUILDING", "ip": null}
```

| Call | Success | Errors worth naming |
| --- | --- | --- |
| `POST /v1/vms` | 202 + `Location` | 400 bad JSON, 401 no credentials, 403 quota exceeded, 422 unknown image or flavour |
| `GET /v1/vms/{id}` | 200 with state, host, IP, error reason | 404 |
| `GET /v1/vms?project=ci&state=ACTIVE` | 200, paginated list | 403 |
| `DELETE /v1/vms/{id}` | 202, state becomes DELETING | 404 |

POST is neither safe nor idempotent, so a client that times out cannot blindly retry it [52]. The `Idempotency-Key` header, still an IETF draft, lets the client send a unique value that the server uses to recognise retries of the same request [58]. DELETE is idempotent [52]: a second delete of the same VM changes nothing.

## Step 3: the components

![Architecture of the VM provisioning service: a client calls the API service, which checks auth and quotas, writes the database and enqueues a job; a worker asks the scheduler for a host and IPAM for an address, then drives a hypervisor through libvirt; hosts fetch base images from the image store; a reconciler compares the database with the hypervisors.](../resources/ch09/vm-provisioning.svg)

| Component | Owns | Choice |
| --- | --- | --- |
| API service | validation, auth, quotas, the 202 contract | stateless Flask or FastAPI, two or more copies |
| Database | desired state: VMs, hosts, IPs, quotas, idempotency keys | PostgreSQL; the single source of truth |
| Job queue | provisioning work waiting for a worker | RQ on Redis, as in chapter 8 |
| Worker | running the steps of one job | RQ workers |
| Scheduler | choosing a host | a library the worker calls, reading the database |
| Hypervisor execution | disks and domains on one host | libvirt over SSH (below) |
| Image store | versioned base images | HTTP file server; hosts cache images locally |
| IPAM | one address per VM | a table with uniqueness constraints |
| Reconciler | noticing drift and repairing it | a loop on a timer (next lesson) |

Nova splits the same way: an API, a SQL database, a scheduler that decides which host gets each instance, a compute service on each hypervisor, and Placement, which tracks resource inventories and usage [158]. Its compute nodes never touch the database directly; they go through a central conductor [158].

**libvirt in three sentences** (chapter 11 covers it). libvirt is a toolkit with a stable API, usable from Python, for creating, starting, stopping and migrating VMs, which it calls domains, on one physical host [92]. A client reaches a remote host's daemon through a URI such as `qemu+ssh://root@kvm-017/system` [92]. It deliberately stops at one node and leaves policies such as load balancing to tools built on top, which is exactly the job of this service [92].

**How the worker reaches a host.** A read-write system connection to libvirt is equivalent to a root shell [92], and Nova runs one compute process on each hypervisor [158]. The two options:

| Option | For | Against |
| --- | --- | --- |
| (a) central workers, libvirt over SSH | nothing to install on hosts | the workers' key controls the whole fleet |
| (b) an agent on each host pulls its own jobs | isolation, no fleet-wide key | one more service to deploy and upgrade on 300 machines |

**Choice:** (a) for a few hundred hosts, with the key in a secrets store and SSH allowed only from the worker subnet; move to (b) when host count or a security review demands it.

## The VM state machine

Clients see one `state` field. Nova's names are a good vocabulary: it lists ACTIVE, BUILDING, STOPPED, DELETED and ERROR among its VM states, lets every state move to DELETED and ERROR, and allows delete from Building and Error [157]. Nova also tracks a separate task state and power state [157]; this design keeps a `step` column for progress and lets the reconciler record power state.

| From | Event | To |
| --- | --- | --- |
| (none) | POST accepted | BUILDING |
| BUILDING | worker finished, domain running | ACTIVE |
| BUILDING | retries exhausted or timeout | ERROR |
| ACTIVE | stop / start | STOPPED / ACTIVE |
| any | DELETE accepted | DELETING |
| DELETING | host resources removed | DELETED |

Keep the queue's job status out of the API. An RQ job moves through statuses such as `queued`, `started`, `finished` and `failed` [50]; a VM can need several jobs (create, then delete), so the VM state is the product's contract and job status is plumbing.

## Step 4: one request end to end

The numbers match the diagram.

1. The client sends `POST /v1/vms` with an idempotency key.
2. The API authenticates the caller and checks the project's quota.
3. In one transaction it reserves the quota, inserts the VM row in BUILDING and stores the key. Commit.
4. It enqueues a provision job whose only argument is the VM id, and returns 202. The worker reads everything else from the database, so a rerun always sees current state.
5. A worker takes the job.
6. The scheduler filters and weighs hosts and records a capacity claim on the chosen one.
7. IPAM reserves an address for the VM.
8. Over libvirt, the worker creates the disk, defines the domain and starts it.
9. The host pulls the base image from the image store if it is not cached.
10. The worker writes ACTIVE with host and IP, or ERROR with a reason.

The reconciler (R) runs beside this flow, comparing the database with what each hypervisor reports.

## Gotchas

- **Enqueue after commit.** Enqueue before the commit and a fast worker can look for a row that does not exist yet. Enqueue after it and a crash in between leaves a BUILDING row with no job; the reconciler must re-enqueue BUILDING rows that have no live job.
- **The queue's default timeout.** RQ kills a job after 180 seconds by default and marks it failed [50]. A slow image pull exceeds that; set `job_timeout` above the slowest real provision.
- **201 for work not done.** 201 Created means a resource was created [52]. The VM is not created yet; use 202 and a status URL.
- **A fleet-wide root key.** With libvirt over SSH, whoever holds the worker key holds every host [92]. Treat it like a production database password.
- **Designing before the numbers.** Without the capacity table you cannot say why overcommit or a second database replica is or is not needed.

:::key-takeaways
- Routine: requirements and scale, API, components, one request, failures, scaling and operations, on a clock.
- Do the arithmetic: here the API load is trivial and the fleet is 83% full without CPU overcommit.
- CPU overcommit costs contention; RAM overcommit risks the OOM killer, so keep RAM at 1.0. [120]
- Long operations return 202 with a status resource; POST retries need an idempotency key. [52] [58]
- The relational database is the source of truth; queue, workers and hosts act on it.
- libvirt manages one host; placement, quotas and IPs are this service's job. [92]
:::

:::glossary
- **Flavour**: a named VM size, such as 4 vCPUs, 8 GiB of RAM and a 40 GiB disk.
- **Hypervisor**: the host software, here KVM with QEMU, that runs virtual machines.
- **Overcommit**: promising VMs more virtual CPU or memory in total than the host physically has.
- **OOM killer**: the part of the Linux kernel that kills a process when the machine runs out of memory.
- **Allocation ratio**: the multiplier applied to a host's real capacity to get what the scheduler may hand out.
- **libvirt**: a library and daemon that manages VMs on one host through a stable API.
- **Domain**: libvirt's word for one virtual machine.
- **IPAM**: IP address management, the part that hands out and tracks addresses.
- **Source of truth**: the one place whose data wins when two places disagree.
- **Idempotency key**: a unique value a client sends so the server can recognise a retried request.
:::
