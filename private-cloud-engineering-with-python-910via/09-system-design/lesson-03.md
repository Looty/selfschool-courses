---
id: l27
title: "Designing a CI and build system"
quiz: quiz-03.yaml
sources: [144, 148, 149, 151, 152, 161, 162, 163, 164]
---
After this lesson you can design a CI and build system shared by many teams on the same whiteboard routine: size the agent fleet, keep untrusted code away from secrets, make builds fast with caching and affected-only testing, and say how you would measure the result.

## Step 1: requirements and scale

**The prompt.** A thousand engineers in many teams push code to one Git server. Every change must be built and tested before merge, and the main branch must produce deployable artefacts.

| Functional | Non-functional |
| --- | --- |
| pipeline on every push and pull request | presubmit feedback under 15 minutes at p95 |
| status reported back to the review | one team's load cannot starve another |
| artefacts built on main and promoted | untrusted code never sees deploy credentials |
| logs and test results searchable | the same commit always gives the same artefact |

**Back-of-envelope numbers** (your assumptions, stated aloud):

| Quantity | Working | Result |
| --- | --- | --- |
| Presubmit runs | 1000 engineers × 3 pushes a day | 3000 a day |
| Post-submit runs | 600 merges a day | 600 a day |
| Agent time | 3600 runs × 20 agent-minutes | 72,000 agent-minutes a day |
| Average busy agents | 72,000 / 480 working minutes | 150 |
| Peak | 3 × average in the busiest hour | ~450 agents |

A fixed fleet sized for the peak of 450 sits two-thirds idle even across an average working day, and almost entirely idle at night. That is the case for agents created on demand.

## Step 2: components

| Component | Owns | Choice |
| --- | --- | --- |
| Controller | pipeline definitions, the queue, scheduling, the UI | Jenkins (chapter 10), several controllers by team group |
| Agents | running build steps | ephemeral VMs or containers, one build each |
| Agent provisioner | creating and destroying agents to match the queue | calls the VM service from the first lesson of this chapter, or a container platform |
| Remote cache | outputs of build steps, keyed by hash | HTTP cache server |
| Artefact store | immutable build outputs, by version and digest | an artefact repository |
| Results store | logs, test results, timings | searchable by commit and by test |

Jenkins uses this split. The controller is the central process that stores configuration, loads plugins and renders the UI; an agent is a machine or container that connects to it and runs tasks; an executor is a slot for one concurrent task on a node; a label is text that groups agents by capability, such as `linux` or `docker` [148]. An agent is a small Java process and "is assumed to be unreliable"; one executor per node is the safest configuration [149]. Running builds on the controller's built-in node is discouraged for security, performance and scalability [149]. Builds there get the same access to the controller's file system as Jenkins itself [151]. When one controller is not enough, add controllers for new teams or projects (horizontal growth) [152].

**Queueing and labels.** Each job asks for a label (`linux-x86`, `gpu`, `macos`). The provisioner watches queue length per label and starts agents for it. Give each team a share of the fleet so one team's 500-job burst waits behind its own share, not everyone's.

## Step 3: isolating builds

What runs in a build is often controlled by people less trusted than the administrator: anyone who can edit a build script or a test [151]. So:

- **One build per fresh agent.** An ephemeral agent starts from a clean image and is destroyed afterwards. Nothing leaks from one build to the next, and a compromised build dies with its VM.
- **Two trust levels.** Presubmit runs on code not yet reviewed. It gets no deploy credentials and no write access to the shared cache. Post-submit runs only reviewed code on main and may use credentials. Jenkins masks credential values in logs, but its docs say masking only reduces accidental exposure and does not stop a malicious build from capturing the value; their rule is not to let untrusted Pipeline jobs use trusted credentials [144].
- **Short-lived credentials.** The same page calls static cloud keys stored in Jenkins not very secure, and prefers a role attached to the machine when the agents run in that cloud [144].

:::low-confidence
How a pull request from a fork is treated (whether it runs automatically, and with which credentials) depends on the Git hosting platform and its plugin settings. The sources read for this course do not cover it; check your platform's documentation and default to "maintainer approval before any fork build runs".
:::

## Step 4: making builds fast

**Where do 40 minutes go?** Measure before changing anything. Split a slow build into queue wait, agent start, checkout, dependency download, compile, and each test shard. Typical fixes, in order of payoff: an agent pool sized for the peak (queue wait), a warm image with dependencies preinstalled (downloads), a remote cache (compile), affected-only tests, then parallel shards (tests).

**Remote caching.** Bazel splits a build into actions, each with declared inputs, outputs, a command line and environment [161]. Its remote cache holds an action cache, which maps action hashes to result metadata, and a content-addressable store (CAS) of output files [161]. A build checks local outputs, then the remote cache; on a miss it runs the action and uploads the result [161]. The docs suggest letting only CI write: developers read with `--remote_upload_local_results=false` [161]. One known trap: Bazel does not track tools outside the workspace, so machines with different system compilers can share wrong cache hits [161].

**Hermetic builds** make that safe. A hermetic build returns the same output for the same source and configuration, because it treats tools as source code and identifies inputs by hash [162]. Common leaks are timestamps or build IDs in outputs, binaries from `/usr/bin` that differ between hosts, and writing into the source tree [162]. A quick test: run the build twice; the second, null build should rebuild nothing [162].

**Affected-only and parallel.** With a dependency graph, run only the tests a change can affect. A 2020 book chapter on one very large monorepo's CI describes exactly that: its continuous build uses the build system's dependency graph to run only affected tests, in batches, and splits a failing batch to find the culprit [163]. The same graph is what lets a hermetic build run independent actions in parallel [162].

## Step 5: presubmit, post-submit and flaky tests

Presubmit should run only fast, reliable tests; the slower full suite runs after merge [163]. Presubmit alone is not enough: two changes can each pass and still break the build together (a "mid-air collision") [163]. That is why the book separates "true head", the newest commit, from "green head", the newest commit the continuous build has verified [163]. Its preferred fix for a broken build is a rollback [163].

**Flaky tests** waste everyone's time, and disabling a test with a tracking bug is one of the book's failure-management options [163]. Hermetic tests, run against a self-contained environment with no production backends, are more deterministic [163]. Design: record every test's pass/fail history, rerun a failure once, quarantine tests whose flake rate passes a threshold, and give each quarantine an owner and a deadline.

## Step 6: artefacts, promotion and metrics

Build once, promote the same artefact: a release candidate is assembled from code that passed the continuous build and is promoted through environments instead of being rebuilt [163]. Store artefacts outside the controller; Jenkins writes pipeline files to the controller's file system unless they are off-loaded to an artefact repository [149].

**DORA's metrics**, as the current guide lists them, are five [164]:

| Group | Metric | Definition |
| --- | --- | --- |
| Throughput | Change lead time | commit to running in production |
| Throughput | Deployment frequency | deployments per period |
| Throughput | Failed deployment recovery time | time to recover from a deployment that needs immediate intervention |
| Instability | Change fail rate | share of deployments that need immediate intervention |
| Instability | Deployment rework rate | share of deployments that are unplanned, caused by a production incident |

Use them per service and to track one team over time; comparing different applications, or turning a metric into a target, are pitfalls the guide names [164]. For the CI platform itself, also watch queue wait p95, agent start time, cache hit rate and flake rate.

## Gotchas

- **Builds on the controller.** They share its file system and permissions; set the built-in node's executors to zero. [149] [151]
- **Secrets in presubmit.** Masked log output is not protection against a hostile build. [144]
- **A cache everyone writes.** One bad machine poisons it for all; let CI write and others read. [161]
- **Non-hermetic steps.** A timestamp in an output defeats the cache and makes "same commit, same artefact" false. [162]
- **Rebuilding for production.** A rebuild is a different artefact from the one you tested; promote the tested one. [163]

:::key-takeaways
- Size the fleet from runs × minutes, and plan for the peak with agents created on demand.
- Controller schedules; disposable agents with one executor run the builds. [148] [149]
- Untrusted presubmit builds get no trusted credentials; masking is not protection. [144]
- Speed comes from measurement, a remote cache on hermetic builds, affected-only tests and parallelism. [161] [162] [163]
- Five DORA metrics, grouped into throughput and instability, used per service. [164]
:::

:::glossary
- **Presubmit**: checks that run on a change before it is merged.
- **Post-submit**: checks that run after a change is merged, usually the full suite.
- **Ephemeral agent**: a build machine created for one build and destroyed afterwards.
- **Executor**: a slot on a build machine for one build at a time.
- **Remote cache**: a shared server that stores build outputs so other machines can reuse them.
- **CAS (content-addressable store)**: storage where each file is found by the hash of its contents.
- **Hermetic build**: a build whose output depends only on its declared inputs, not on the machine.
- **Flaky test**: a test that sometimes passes and sometimes fails on the same code.
- **Artefact**: a file a build produces and keeps, such as a package or an image.
- **Release candidate**: a built, tested version that may be promoted to production.
:::
