# Two-hour practice run: question sheet

Print this page. Answer aloud, record yourself, and do not open the course while a block runs.
The lesson "A two-hour practice run" (chapter 14) lists where each answer is taught.

Start time: ________

## Block 1. Live coding, 0:00 to 0:40

Problem chosen from chapter 3: ______________________________

- [ ] Restated input, output and limits
- [ ] Wrote two examples by hand (one edge case)
- [ ] Named a brute force and its complexity
- [ ] Tests pass (save as `mine.py` beside the test file, run `python <name>_test.py mine`): ______ of ______
- [ ] Walked one example through the code before running
- [ ] Stated time and space complexity and one alternative

## Block 2. Linux and Git, 0:40 to 1:00

1. A service will not start after a reboot. Walk me through what you check.
2. What is the difference between SIGTERM and SIGKILL, and why does it matter for a service that holds a lock?
3. A process is a zombie. What does that mean and how do you get rid of it?
4. A script fails with "Permission denied" on a file that exists. What do you look at?
5. The disk is full but `du` adds up to much less than `df` reports. Why?
6. You cannot SSH to a host that answered yesterday. Take me from the client side to the server side.
7. What do `set -euo pipefail` each do in a Bash script, and what is one trap they leave?
8. What is a commit in Git, physically? What does a branch point to?
9. Merge or rebase a feature branch: when do you pick which, and what must you never rebase?
10. You ran `git reset --hard` and lost a commit. Get it back. Then: a test started failing somewhere in the last 200 commits; find the commit.

## Block 3. Containers and virtualisation, 1:00 to 1:15

1. What is a container, in terms of kernel features? Which namespaces matter most?
2. How is a memory limit on a container enforced, and what happens when it is exceeded?
3. Why did changing one line of source code make the whole `pip install` layer rebuild? Fix the Dockerfile.
4. A Compose stack starts, but the app cannot reach the database. What do you check?
5. What is the difference between KVM and QEMU, and what does each do when a VM runs?
6. How would you give 50 VMs the same base image without 50 full copies of the disk?
7. A VM boots but has no SSH key and the wrong hostname. Where do those come from?
8. Using libvirt, what is the difference between `define` and `create`, and between `shutdown` and `destroy`?

## Block 4. System design on paper, 1:15 to 1:40

Routine: requirements and scale (5 min), API, components, one request end to end, failure modes, scaling and operations.

Choose one:

1. Design a self-service VM provisioning service for about a thousand engineers on a few hundred KVM hosts.
2. Design a CI and build system shared by many teams.

Follow-ups for the VM service:

3. The worker dies after the disk is created but before the VM starts. What happens to that request?
4. How do you pick a host? What do you risk if you overcommit CPU and memory?
5. The database says a VM is running, but the host has never heard of it. Who notices, and what do they do?

Follow-ups for the CI system:

6. Builds take 40 minutes. Where does the time go, and what do you change first?
7. How do you run builds for pull requests from people you do not trust without leaking secrets?

## Block 5. Python backend, 1:40 to 1:50

1. Creating a VM takes three minutes. What should `POST /vms` return, and how does the client learn the result?
2. Which HTTP methods are idempotent, and why does it matter when a client retries?
3. What is the difference between 401 and 403? Between 400 and 422?
4. WSGI and ASGI: what is each, and what happens if you call blocking code inside an `async def` endpoint?
5. An RQ worker is killed with `kill -9` mid-job. What happens to the job?
6. How do you stop two workers from provisioning the same VM at the same time using Redis?

## Block 6. Jenkins, Ansible, AI tools, Kubernetes, AWS, 1:50 to 2:00

1. Write the skeleton of a declarative Jenkinsfile with build, test and a parallel lint stage.
2. Why should builds not run on the Jenkins controller itself?
3. What makes an Ansible task idempotent, and why is `shell` a risk to that?
4. When would you reach for Fabric instead of Ansible?
5. How do you use an AI coding assistant on infrastructure code without leaking secrets or trusting wrong output?
6. What is the difference between a Deployment and a Pod, and between a liveness and a readiness probe?
7. Security group or network ACL: what is the difference?

## Score sheet

0 = blank or wrong; 1 = partly, after a long silence; 2 = right but unstructured or over time; 3 = right, structured, on time, aloud.

| Block | Score (0 to 3) | Questions to reread |
| --- | --- | --- |
| 1. Coding (ticks above: 5 or 6 = 3, 3 or 4 = 2, 1 or 2 = 1, none = 0) | | |
| 2. Linux and Git | | |
| 3. Containers and virtualisation | | |
| 4. System design | | |
| 5. Python backend | | |
| 6. Jenkins, Ansible, AI, Kubernetes, AWS | | |
| **Total (out of 18)** | | |
