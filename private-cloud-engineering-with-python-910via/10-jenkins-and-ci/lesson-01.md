---
id: l28
title: "Jenkins architecture and declarative pipelines"
quiz: quiz-01.yaml
resources: [../resources/ch10/Jenkinsfile]
sources: [141, 142, 143, 144, 146, 147, 148, 149, 150, 151, 152]
---
After this lesson you can draw how a Jenkins controller hands work to agents, explain why builds stay off the controller, and read or write a Declarative `Jenkinsfile` with parallel stages, a branch-only deploy and `post` actions.

## The moving parts

| Term | What it is |
| --- | --- |
| Controller | The central process: stores configuration, loads plugins, serves the UI [148]. Decides how, when and where tasks run [149]. |
| Node | Any machine that can run Pipelines or jobs; agents and the built-in node are both nodes [148]. |
| Agent | A small Java client (one 170 KB jar) that connects to the controller and runs tasks; Jenkins assumes it is unreliable [149]. |
| Executor | A slot on a node, effectively a thread; the number of executors is the number of concurrent tasks on that node [149]. |
| Label | Free text grouping agents by capability, such as `linux` or `docker` [148]. |
| Workspace | A disposable directory on a node where the work happens [148]. |
| Artifact | An immutable build output archived on the controller [148]. |

Agents can be static or provisioned on demand by a cloud such as Kubernetes or Amazon EC2 [149]. One executor per node is the safest setting; one per CPU core works for small tasks [149].

## Keep builds off the controller

Out of the box Jenkins runs builds on the built-in node, inside the controller process [151]. A build there has the same access to the controller's file system as Jenkins itself [151], and build scripts, test code and job settings are often written by people less trusted than an administrator [151]. Running jobs on the controller is also how a single controller runs out of resources as projects grow [152]. The fix: set the built-in node's executors to 0 and give builds agents [151] [150]. Then the controller only handles HTTP and scheduling, and you scale by adding agents [152].

## Pipeline and the Jenkinsfile

Jenkins Pipeline is a suite of plugins for modelling a delivery pipeline as code [142]. The definition lives in a `Jenkinsfile` committed with the application, so it is reviewed and versioned like the rest of the code [142]. Pipelines survive controller restarts and can pause for human approval [142].

There are two syntaxes. Declarative is a stricter, pre-defined structure that is easier to read; Scripted is general-purpose Groovy with few limits [143]. Lesson l29 covers Scripted; use Declarative unless it gets in your way.

## Declarative skeleton

```groovy
pipeline {                    // required top-level block
    agent any                 // required at top level: where to run
    stages {                  // required: one or more stage
        stage('Build') {
            steps {           // required in a stage: one or more steps
                sh 'make'
            }
        }
    }
    post { always { echo 'done' } }   // optional, conventionally last
}
```

Rules that differ from plain Groovy: no semicolons, one statement per line, and blocks hold only sections, directives, steps or assignments [143]. `agent` takes `any`, `none` (then every stage needs its own), `label 'x'` (label expressions with `&&` and `||` work), `docker` or `dockerfile` [143]. A `docker` agent needs the Docker Pipeline plugin [147].

## Walking through `resources/ch10/Jenkinsfile`

The file builds `vmapi`, the Flask service from chapter 8, as a Multibranch job.

| Block | What it does |
| --- | --- |
| `agent none` | No executor held for the whole run; each stage picks its own [143]. |
| `options` | `timeout` aborts a hung run, `buildDiscarder` keeps 20 runs, `disableConcurrentBuilds` queues a second run [143]. |
| `environment { IMAGE = ... }` | An environment variable for every step [143]. |
| `Lint` | Runs in a `python:3.13-slim` container on an agent labelled `docker` [143] [147]. |
| `Test` with `parallel` | Two nested stages run at once, on Python 3.12 and 3.13; `failFast true` aborts the other when one fails [143]. Each stage's `post { always { junit ... } }` publishes test reports [142] [143]. |
| `Build image` | `REGISTRY = credentials('registry-push')` binds a username/password credential and adds `REGISTRY_USR` and `REGISTRY_PSW` [143] [144]. The `sh` strings are single-quoted, so the shell reads the secret (lesson l29 explains why). |
| `Deploy` | `when { branch 'main' }` runs it on `main` only; `beforeAgent true` checks the condition before grabbing a `deploy` agent [143]. |
| top-level `post` | `success`, `failure` (sends mail), `fixed` [143]. |

`when { branch }` only works in a Multibranch Pipeline [143]. In a plain Pipeline job of the course's test run (Jenkins 2.580.2 in Docker), the stage was skipped, never run:

```text
[Pipeline] { (Deploy)
Stage "Deploy" skipped due to when conditional
```

The file passed the controller's Declarative linter, the `/pipeline-model-converter/validate` endpoint, in the same container:

```text
Jenkinsfile successfully validated.
```

A deliberate typo (`stepz` for `steps`) produced `Unknown stage section "stepz"`, so the linter does check structure.

## `post` conditions

They run in this fixed order: `always`, `changed`, `fixed`, `regression`, `aborted`, `failure`, `success`, `unstable`, `unsuccessful`, `cleanup` [143]. `fixed` means success after a failed or unstable run; `regression` means failure, unstable or aborted after a success; `cleanup` runs last, whatever the status [143].

## Multibranch

A Multibranch Pipeline scans a repository and creates one job per branch that has a `Jenkinsfile` [146]. It sets `BRANCH_NAME`, and `CHANGE_ID` for pull requests [146]. It does not re-index for new or deleted branches by default, so turn on periodic scanning [146]. Pull request support comes from branch-source plugins such as GitHub Branch Source [146].

## Versions

On 2026-11-19 the LTS (long-term support) release was 2.580.2 and the weekly release 2.591 [141]. A new LTS line arrives every 12 weeks [148].

## Gotchas

- **Executors on the built-in node.** The default lets builds run inside the controller with its file access; set them to 0. [151]
- **`branch` outside Multibranch.** The condition never matches, so the deploy silently never runs. [143]
- **Stage `timeout` with a stage agent.** It includes the time spent waiting for the agent. [143]
- **`when` before an expensive agent.** Without `beforeAgent true` the agent is allocated first, then the stage is skipped. [143]
- **Branch indexing.** New branches stay invisible until a scan runs. [146]

:::low-confidence
The `ruff` and `pytest` commands, `requirements-dev.txt` and `deploy.sh` are assumptions about the service repository, not facts from the Jenkins docs. The Jenkinsfile was linted, not run end to end: the test container had no Docker agents or registry.
:::

:::key-takeaways
- The controller schedules and stores; agents with executors do the work, matched by labels. [148] [149]
- Builds on the controller can touch `$JENKINS_HOME`; give it 0 executors. [151] [152]
- Declarative needs `pipeline`, `agent`, `stages`, `stage`, `steps`. [143]
- Gate deploys with `when { branch 'main' }` in a Multibranch job, plus `beforeAgent true`. [143] [146]
- `post` blocks run in a fixed order and `cleanup` is last. [143]
:::

:::glossary
- **Controller**: the central Jenkins server that stores settings, shows the web UI and schedules work.
- **Agent**: a worker process on another machine or container that runs build steps for the controller.
- **Executor**: one slot on a node that can run one build at a time.
- **Label**: a tag on agents, such as `docker`, that a pipeline uses to say where it may run.
- **Built-in node**: the executor slots inside the controller process itself, formerly called the master node.
- **Jenkinsfile**: a file in the repository that defines the pipeline as code.
- **Declarative**: the structured Jenkinsfile syntax that starts with `pipeline { }`.
- **Groovy**: the programming language that Jenkinsfiles are written in.
- **Multibranch Pipeline**: a job type that makes one pipeline per branch or pull request that has a Jenkinsfile.
- **LTS**: the long-term support release line, updated less often than the weekly line.
:::
