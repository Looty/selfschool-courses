---
id: l13
title: "Design: a self-service VM provisioning service"
quiz: quiz-13.yaml
resources: [../resources/ch05/vm-provisioning.svg]
sources: [50, 51, 52, 58, 92, 120, 155, 156, 160]
---
After this lesson you can talk through, in five steps, a design where a thousand engineers request VMs by API and workers build them on a few hundred KVM hosts.

## The five steps

| Step | Minutes | Say out loud |
| --- | --- | --- |
| 1. Requirements and numbers | 5 | "Here is what it does, what it guarantees, and the load." |
| 2. API | 5 | "Create is slow, so it returns 202 and a status URL." |
| 3. Components | 7 | "The database is the source of truth; everything else acts on it." |
| 4. One request end to end | 5 | "Let me walk one create through the boxes." |
| 5. Failures and scaling | 8 | "Here is what breaks at each arrow, and how it heals." |

## Step 1: requirements and numbers

Create, read, list, delete, quotas. Targets: SSH-able in 5 minutes at p95; never one IP twice; database and hosts agree after crashes. Assume 300 hosts of 32 cores and 248 GiB; a VM is 4 vCPUs and 8 GiB.

| Quantity | Result |
| --- | --- |
| Creates | ~2000 a day, ~0.07 per second |
| No overcommit | min(32/4, 248/8) = 8 per host, 2400 total: 83% full |
| CPU ratio 4.0 | min(128/4, 31) = 31 per host |

So API load is tiny; the hard parts are correctness and slow host work. Nova's default allocation ratios are 4.0 for CPU and 1.0 for RAM [155] [156]. CPU overcommit costs contention; RAM overcommit risks the OOM killer [120]. Keep RAM at 1.0.

## Step 2: the API

| Call | Success | Errors |
| --- | --- | --- |
| `POST /v1/vms` | 202 + `Location` [52] | 400, 401, 403 quota, 422 unknown flavour |
| `GET /v1/vms/{id}` | 200: state, host, IP | 404 |
| `DELETE /v1/vms/{id}` | 202, state DELETING | 404 |

POST is not idempotent, so clients retry with an `Idempotency-Key` header (an IETF draft) [52] [58].

## Step 3: components

![Architecture: client, API, database, job queue, worker with scheduler and IPAM, hypervisors, image store, reconciler.](../resources/ch05/vm-provisioning.svg)

Stateless API; PostgreSQL for desired state; RQ workers; a scheduler library; IPAM as a table with uniqueness constraints; a reconciler. libvirt manages one host only; workers reach hosts over `qemu+ssh://root@kvm-017/system`, which is root-equivalent, so guard the key [92].

## Step 4: one request

1. API authenticates; one transaction reserves quota, inserts the BUILDING row, stores the key.
2. After commit, it enqueues a job carrying only the VM id and returns 202.
3. A worker picks a host, claims an IP, creates the disk, defines and starts the domain.
4. It writes ACTIVE with host and IP, or ERROR with a reason.

## Step 5: failures and scaling

**Placement.** Filter out hosts that cannot fit, then rank by weight [155]; spread general VMs, pack CI VMs. Claim the slot with a conditional `UPDATE ... WHERE used + 4 <= total * 4.0`; zero rows means another worker won, try the next host.

**A worker dies halfway.** `kill -9` gives RQ no chance to mark the job failed [50]. Every step is check-then-act (host set? IP claimed? disk exists? running?), so a rerun finishes the job. A lock, `SET lock:vm:<id> <token> NX EX 600`, stops overlapping runs [51].

**Reconciliation.** A controller loop moves current state towards desired state [160]:

| Database | Host | Action |
| --- | --- | --- |
| ACTIVE | no domain | ERROR and alert; never recreate silently |
| no row | domain exists | orphan: shut down after a grace period |
| BUILDING, stale 15 min | anything | re-enqueue the idempotent job |

Act only on a difference seen twice. Scale on queue depth and free slots per flavour.

## Exercise (20 minutes)

Close this page. With a timer, say all five steps aloud while sketching the boxes. Then open `vm-provisioning.svg` and note what you missed.

:::key-takeaways
- Without CPU overcommit the fleet is 83% full; keep RAM at 1.0. [120] [155]
- Slow creates return 202; POST retries need an idempotency key. [52] [58]
- Claims are conditional writes; steps are check-then-act; a reconciler repairs drift. [160]
:::
