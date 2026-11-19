---
id: l34
title: "A two-hour practice run"
quiz: quiz-01.yaml
resources: [../resources/ch14/practice-run.md]
sources: none
---
After this lesson you can run a two-hour, self-timed rehearsal of a broad technical screen covering the whole course, score yourself honestly, and know which lesson to reread for every question you missed.

This lesson adds no new material. It is a script: a clock, a set of questions to answer aloud, and a way to score the result. The questions point to the lessons that answer them; do not look while the clock runs.

## Before you start

- **Print or open the question sheet** `practice-run.md` from the resources. It has the same questions as below without the lesson pointers, so you cannot peek at where the answer lives.
- **Editor.** A blank browser editor or a plain text editor with autocomplete, linting and AI assistance switched off. The same setup as chapter 1.
- **Paper** for the design block, and a timer you can see.
- **Record yourself** on your phone (audio is enough). Talking aloud is the skill being trained; listening back is how you find the silences and the "um, so basically" loops.
- **No notes, no search, no shell** during the blocks. Checking happens after each block, not during it.

## The clock

| Time | Block | Minutes | Then check against |
| --- | --- | --- | --- |
| 0:00 | Live coding | 40 | the problem's test file and reference solution |
| 0:40 | Linux and Git | 20 | chapters 5 and 6 |
| 1:00 | Containers and virtualisation | 15 | chapters 7 and 11 |
| 1:15 | System design, on paper | 25 | chapter 9 |
| 1:40 | Python backend | 10 | chapter 8 |
| 1:50 | Jenkins, Ansible, AI tools, Kubernetes, AWS | 10 | chapters 10, 12 and 13 |
| 2:00 | Score yourself | 15 to 30 | the rubric below |

Keep the blocks strict. When the timer for a block ends, stop mid-sentence and move on; running over in one block is the most common way a real session goes wrong.

## Block 1: live coding (40 minutes)

Pick **one** problem from chapter 3 (Timed infrastructure problems) that you have not yet solved cleanly: log aggregation, reservations and VM placement, build dependency order, or caches and rate limiters. Open only its `_starter.py` docstring for the statement, then work in the blank editor. Talk through every decision as if someone were listening.

Habits for this block:

1. **Restate** the problem in your own words, including input format, output format and limits. Ask the questions you would ask a person: can the input be empty, are IDs unique, is the order of ties defined?
2. **Examples first.** Write two small examples by hand, one normal and one edge case (empty input, one item, duplicates), with the expected output.
3. **Brute force first.** Say the simplest correct approach and its complexity, even if it is slow. Then improve it only if the limits demand it.
4. **Code in small pieces** with names that say what they hold. Parse the input in one function and solve in another.
5. **Test by hand.** Walk your first example through the code line by line, out loud, before running anything. Then run it.
6. **Say the complexity** in time and space at the end, and name one alternative you did not choose and why.

At 0:35, stop adding features and make sure what you have runs. At 0:40, save your code as, say, `mine.py` next to the test file and run `python <name>_test.py mine` (the module name, without `.py`), then note the result.

## Block 2: Linux and Git (20 minutes)

Answer each aloud in about two minutes, then move on.

| # | Question | Where the answer is |
| --- | --- | --- |
| 1 | A service will not start after a reboot. Walk me through what you check. | Ch 5, Processes, signals and systemd |
| 2 | What is the difference between SIGTERM and SIGKILL, and why does it matter for a service that holds a lock? | Ch 5, Processes, signals and systemd |
| 3 | A process is a zombie. What does that mean and how do you get rid of it? | Ch 5, Processes, signals and systemd |
| 4 | A script fails with "Permission denied" on a file that exists. What do you look at? | Ch 5, Files, permissions and the filesystem |
| 5 | The disk is full but `du` adds up to much less than `df` reports. Why? | Ch 5, Files, permissions and the filesystem |
| 6 | You cannot SSH to a host that answered yesterday. Take me from the client side to the server side. | Ch 5, Network and SSH troubleshooting |
| 7 | What do `set -euo pipefail` each do in a Bash script, and what is one trap they leave? | Ch 5, Lab: the broken box and Bash strict mode |
| 8 | What is a commit in Git, physically? What does a branch point to? | Ch 6, Objects, branches, merge and rebase |
| 9 | Merge or rebase a feature branch: when do you pick which, and what must you never rebase? | Ch 6, Objects, branches, merge and rebase |
| 10 | You ran `git reset --hard` and lost a commit. Get it back. Then: a test started failing somewhere in the last 200 commits; find the commit. | Ch 6, Lab: undo, recover and find the bad commit |

## Block 3: containers and virtualisation (15 minutes)

| # | Question | Where the answer is |
| --- | --- | --- |
| 1 | What is a container, in terms of kernel features? Which namespaces matter most? | Ch 7, What a container is: namespaces, cgroups and runtimes |
| 2 | How is a memory limit on a container enforced, and what happens when it is exceeded? | Ch 7, What a container is: namespaces, cgroups and runtimes |
| 3 | Why did changing one line of source code make the whole `pip install` layer rebuild? Fix the Dockerfile. | Ch 7, Images, layers and Dockerfiles |
| 4 | A Compose stack starts, but the app cannot reach the database. What do you check? | Ch 7, Lab: networking, limits, Compose and a failing stack |
| 5 | What is the difference between KVM and QEMU, and what does each do when a VM runs? | Ch 11, KVM, QEMU, Vagrant and cloud-init |
| 6 | How would you give 50 VMs the same base image without 50 full copies of the disk? | Ch 11, KVM, QEMU, Vagrant and cloud-init |
| 7 | A VM boots but has no SSH key and the wrong hostname. Where do those come from? | Ch 11, KVM, QEMU, Vagrant and cloud-init |
| 8 | Using libvirt, what is the difference between `define` and `create`, and between `shutdown` and `destroy`? | Ch 11, libvirt: domains, virsh and the Python bindings |

## Block 4: system design on paper (25 minutes)

Choose one prompt and use the routine from chapter 9: clarify requirements and scale, state the API, draw the components, walk one request end to end, then failure modes, then scaling and operations. Spend no more than 5 minutes on requirements.

| # | Prompt or follow-up | Where the answer is |
| --- | --- | --- |
| 1 | Design a self-service VM provisioning service for about a thousand engineers on a few hundred KVM hosts. | Ch 9, Designing a self-service VM provisioning service |
| 2 | Or: design a CI and build system shared by many teams. | Ch 9, Designing a CI and build system |
| 3 | (VM) The worker dies after the disk is created but before the VM starts. What happens to that request? | Ch 9, Design deep dives: placement, failures and reconciliation |
| 4 | (VM) How do you pick a host? What do you risk if you overcommit CPU and memory? | Ch 9, Design deep dives: placement, failures and reconciliation; Designing a self-service VM provisioning service |
| 5 | (VM) The database says a VM is running, but the host has never heard of it. Who notices, and what do they do? | Ch 9, Design deep dives: placement, failures and reconciliation |
| 6 | (CI) Builds take 40 minutes. Where does the time go, and what do you change first? | Ch 9, Designing a CI and build system |
| 7 | (CI) How do you run builds for pull requests from people you do not trust without leaking secrets? | Ch 9, Designing a CI and build system |

## Block 5: Python backend (10 minutes)

| # | Question | Where the answer is |
| --- | --- | --- |
| 1 | Creating a VM takes three minutes. What should `POST /vms` return, and how does the client learn the result? | Ch 8, HTTP semantics and Flask |
| 2 | Which HTTP methods are idempotent, and why does it matter when a client retries? | Ch 8, HTTP semantics and Flask |
| 3 | What is the difference between 401 and 403? Between 400 and 422? | Ch 8, HTTP semantics and Flask |
| 4 | WSGI and ASGI: what is each, and what happens if you call blocking code inside an `async def` endpoint? | Ch 8, FastAPI, Pydantic, and WSGI vs ASGI |
| 5 | An RQ worker is killed with `kill -9` mid-job. What happens to the job? | Ch 8, RQ and Redis: jobs, workers and retries; Lab: a VM request API with a job queue |
| 6 | How do you stop two workers from provisioning the same VM at the same time using Redis? | Ch 8, RQ and Redis: jobs, workers and retries |

## Block 6: Jenkins, Ansible, AI tools, Kubernetes, AWS (10 minutes)

| # | Question | Where the answer is |
| --- | --- | --- |
| 1 | Write the skeleton of a declarative Jenkinsfile with build, test and a parallel lint stage. | Ch 10, Jenkins architecture and declarative pipelines |
| 2 | Why should builds not run on the Jenkins controller itself? | Ch 10, Jenkins architecture and declarative pipelines |
| 3 | What makes an Ansible task idempotent, and why is `shell` a risk to that? | Ch 12, Ansible and Fabric: configuration and remote execution |
| 4 | When would you reach for Fabric instead of Ansible? | Ch 12, Ansible and Fabric: configuration and remote execution |
| 5 | How do you use an AI coding assistant on infrastructure code without leaking secrets or trusting wrong output? | Ch 13, AI tools in engineering work, Kubernetes and AWS in brief |
| 6 | What is the difference between a Deployment and a Pod, and between a liveness and a readiness probe? | Ch 13, AI tools in engineering work, Kubernetes and AWS in brief |
| 7 | Security group or network ACL: what is the difference? | Ch 13, AI tools in engineering work, Kubernetes and AWS in brief |

## Scoring yourself

Listen to the recording and score each block from 0 to 3.

| Score | Meaning |
| --- | --- |
| 0 | Blank, or wrong in a way you would not have caught |
| 1 | Partly right, but only after a long silence or by guessing |
| 2 | Right, but unstructured, or you ran over time |
| 3 | Right, structured (claim, reason, example), on time, and said aloud |

For the coding block, tick the six habits instead: restated the problem, wrote examples, named a brute force, tests pass, tested by hand before running, stated the complexity. Five or six ticks score 3, three or four score 2, one or two score 1, none scores 0. The total is out of 18.

Every 0 or 1 becomes a line in a "reread" list with the lesson it points to. Reread those lessons the same day, then answer the same questions again aloud the next morning without notes.

## Suggested study order over three days

| Day | Work |
| --- | --- |
| 1 | Chapters 1 and 2: the editor setup, then Python from memory. Type every drill without autocomplete. |
| 2 | Chapters 3 to 7: the timed problems, Python and the system, Linux, Git and containers, including the three labs. |
| 3 | Chapters 8 to 13; a 45-minute reread of chapter 7 of the companion course "Shipping Software on Linux: Essentials" (Linux performance triage); then this practice run, ideally late in the day. |

On day 3, leave at least two hours and fifteen minutes for the run and its scoring. If you have one more day, run it again with the other design prompt and a different coding problem.

## Gotchas

- **Peeking.** Opening the lesson "just to check one word" during a block turns a rehearsal into reading. Write the doubt down and check it when the block ends.
- **Silent coding.** Long silences are what a listener notices first. If you are thinking, say what you are thinking about.
- **Skipping the brute force.** Jumping to the clever solution and getting stuck leaves nothing working at minute 40. A slow correct answer beats a fast broken one.
- **Design without numbers.** A design with no request rate, host count or VM count cannot justify any choice. Do the back-of-envelope step even when it feels obvious.
- **Generous scoring.** "I knew that, I just could not say it" is a 1. The skill is saying it.

:::key-takeaways
- Two hours: 40 coding, 20 Linux and Git, 15 containers and VMs, 25 design, 10 backend, 10 on the rest.
- Coding habits: restate, examples, brute force first, test by hand, state the complexity.
- Design routine: requirements and scale, API, components, one request end to end, failures, scaling and operations.
- Score each block 0 to 3 from a recording; every low score becomes a reread with a named lesson.
:::

:::glossary
- **Technical screen**: a timed session where someone checks your skills by asking questions and watching you code.
- **Brute force**: the simplest correct solution, usually trying every possibility, before any optimisation.
- **Back-of-envelope numbers**: rough estimates of load and size, worked out in a minute, that justify a design choice.
- **Rubric**: a fixed list of what earns each score, decided before you mark yourself.
:::
