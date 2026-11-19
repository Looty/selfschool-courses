---
id: l33
title: "AI tools in engineering work, Kubernetes and AWS in brief"
quiz: quiz-01.yaml
resources: [../resources/ch13/deployment.yaml]
sources: [160, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184]
---
After this lesson you can use AI coding tools without leaking secrets or shipping unchecked output, read a Kubernetes Deployment and triage a failing one with `kubectl`, and explain the core AWS building blocks next to the private-cloud pieces you already run.

## 1. Working with AI tools

A **large language model (LLM)** is a model with many parameters, trained on a vast amount of text, that generates text, answers questions and summarises. [181] It reads and writes **tokens**, units that may be words, parts of words, characters or bytes. [181] The **context window** is all the text the model can refer to while answering, including the answer itself: its working memory, separate from its training data. [181] More context is not automatically better, because accuracy and recall fall as the token count grows. [181]

Even the best models sometimes produce text that is factually wrong or contradicts the context they were given; this is **hallucination**. [181] Reduce it by allowing the model to say "I don't know", asking for direct quotes from the material you supplied, and asking for a citation behind each claim. These measures reduce hallucination but do not remove it, so validate anything critical. [181]

How to get useful output:

- **Give context and be specific.** Name the file, the symptom and what "fixed" means, for example: "login fails after the session times out; look at token refresh in src/auth/, write a failing test, then fix it". [182] Point at the files that matter and leave out the ones that do not. [180]
- **Break the task down.** Split a complex task into smaller prompts. [180]
- **Review it like a colleague's code.** Understand it before you use it, check it for function, security, readability and maintainability, and run tests, linters and code scanning on it. [180] Give the tool a check that passes or fails, and ask for the command it ran and its output; "all tests pass" on its own says little. [182]

**What not to paste.** OWASP's LLM02, Sensitive Information Disclosure, lists credentials, personal data and confidential business data, and tells users to avoid entering sensitive data that the model may later disclose. [183] For platform work that means no API tokens, SSH keys, `.env` files, kubeconfigs or customer records. Tools that can read the repository can be blocked from secret files; Claude Code's example is a deny rule on `Read(./.env)`. [182]

**Prompt injection** (LLM01) is input that changes the model's behaviour in ways nobody intended. In indirect injection the instructions hide in content the tool reads, such as a web page or a file. [183] No method is known to prevent it fully, so limit the damage: least privilege for the tool, human approval for high-risk actions, and keeping external content clearly separate from instructions. [183]

The **Model Context Protocol (MCP)** is an open standard for connecting AI applications to external systems. [184] A host application, such as Claude Code, opens one MCP client per MCP server, and each server offers tools (actions), resources (data) and prompts (templates). [184] Every MCP server you add is another set of actions the model can take, so the least-privilege rule applies to it too. [183]

Sensible uses in platform work: explaining unfamiliar code, writing tests and regular expressions [180], triaging a log (`cat error.log | claude -p "what's going on here"`) [182], and a first draft of a pipeline or manifest that you then review and run. The tools are not designed to replace your expertise. [180]

## 2. Kubernetes

A cluster is a **control plane** plus one or more worker nodes. [166] The current minor release is v1.37 (stable patch v1.37.2 on 2026-11-19). [165]

| Component | Runs on | Job |
| --- | --- | --- |
| kube-apiserver | control plane | Serves the Kubernetes HTTP API [166] |
| etcd | control plane | Consistent key-value store for all API data [166] |
| kube-scheduler | control plane | Assigns new Pods to a suitable node [166] |
| kube-controller-manager | control plane | Runs the built-in controllers [166] |
| kubelet | every node | Makes sure the Pods' containers are running [166] |
| kube-proxy (optional) | every node | Network rules that implement Services [166] |
| container runtime | every node | Runs the containers [166] |

**Controllers** are control loops: each one watches the `spec` (desired state) of its objects and pushes the current state towards it, usually by asking the API server to create or delete Pods. [160] It is the same idea as the reconcile loop of a provisioning service.

A **Pod** is one or more containers that share network and storage and are always scheduled together; each Pod gets its own IP address. [167] You rarely create Pods directly. [167] A **Deployment** manages them: `replicas` defaults to 1, and the default `RollingUpdate` strategy uses `maxUnavailable` 25% and `maxSurge` 25%, so at least 75% and at most 125% of the desired Pods are up during a rollout. [168] `Recreate` kills every old Pod first. [168] The two cannot both be 0. [168]

A **Service** gives a set of Pods, usually chosen by a label selector, one stable address. [169] `ClusterIP` (the default) is reachable only inside the cluster, `NodePort` opens a port from 30000-32767 on every node, `LoadBalancer` uses an external load balancer, and `ExternalName` returns a DNS CNAME. [169]

A **ConfigMap** holds configuration (up to 1 MiB) and provides no secrecy. [170] A **Secret** holds small sensitive values, but is stored unencrypted in etcd by default, and anyone who can create a Pod in the namespace can read it; turn on encryption at rest and restrict access with RBAC. [170]

| Probe | On failure |
| --- | --- |
| Liveness | The kubelet restarts the container [171] |
| Readiness | The Pod is removed from the Service's endpoints; no restart [171] |
| Startup | Holds off the other two until it succeeds; on failure the container is killed [171] |

**Requests** tell the scheduler where the Pod fits; **limits** cap usage. CPU over the limit is throttled, and memory over it can be OOM-killed. [172] `250m` is a quarter of a CPU; memory `400m` means 0.4 bytes, so write `400Mi`. [172] `deployment.yaml` puts this together: three replicas, `maxSurge: 1` with `maxUnavailable: 0`, all three probes and a ClusterIP Service. It passed a schema check in the course's test run:

```text
$ docker run --rm -v "$PWD:/m:ro" ghcr.io/yannh/kubeconform:v0.6.7 -strict -summary /m/deployment.yaml
Summary: 2 resources found in 1 file - Valid: 2, Invalid: 0, Errors: 0, Skipped: 0
```

A first look at a failing workload, with commands from the kubectl quick reference and the Deployment page: [173] [168]

```bash
kubectl get pods -o wide                         # status, restarts, node
kubectl describe pods my-pod                     # details and recent events
kubectl logs my-pod --previous                   # output of the previous (crashed) container
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl rollout status deployment/vmapi          # exit 1 if the rollout fails to progress
kubectl rollout undo deployment/vmapi
```

## 3. AWS

**EC2** provides virtual servers, called instances. [174] An instance starts from an AMI (a template with the operating system and software), and its instance type fixes CPU, memory and network. [174] It has EBS volumes for persistent disks and key pairs for login. [174]

A **VPC** is a logically isolated virtual network. [175] A subnet is an IP range that lives in a single Availability Zone, route tables decide where traffic from a subnet goes, and an internet gateway connects the VPC to the internet. [175]

| | Security group | Network ACL |
| --- | --- | --- |
| Applies to | Instances | Subnets |
| Rules | Allow only | Allow and deny |
| Evaluation | All rules, then decide | In ascending order, first match wins |
| Return traffic | Allowed automatically (stateful) | Must be allowed explicitly (stateless) |

[176] AWS recommends security groups as the main control and network ACLs as a coarse second layer. [176]

**S3** stores objects (a file plus metadata) under keys in buckets, which are private by default. [177] S3 Standard is designed for 99.999999999% durability, "eleven nines", over a year. [177]

**IAM** controls who is authenticated and what they are authorised to do. [178] Policies are mostly JSON documents attached to identities or resources; an explicit deny overrides any allow. [178] Least privilege means granting only the actions a task needs, on specific resources. [178] Do not use the root user for daily work, and prefer roles, which issue temporary credentials. [178]

**Shared responsibility.** AWS secures the cloud itself: hardware, network, facilities and the virtualisation layer. [179] You secure what you put in it: for EC2, the guest OS patches, your applications and the security group rules. [179]

An analogy, not an equivalence, from the private cloud you know:

| Private cloud | AWS | Kubernetes |
| --- | --- | --- |
| KVM hypervisor fleet plus a placement scheduler | EC2 | Nodes plus kube-scheduler |
| A VM from a golden image | Instance from an AMI | Pod from a container image |
| libvirt network, bridge, VLAN | VPC, subnet, route table | Pod network, Service |
| Host firewall rules | Security group | (not covered here) |
| Provisioning service's reconcile loop | EC2 Auto Scaling | Controllers |

## Gotchas

- **Fluent and wrong.** A hallucinated answer looks like any other answer; check critical facts against a source or a test. [181]
- **Secrets in a prompt.** Anything you enter may be disclosed later; strip tokens and keys first. [183]
- **Liveness probe on a dependency.** A failing liveness probe restarts the container, so a database outage becomes a restart loop; use readiness for "cannot serve right now". [171]
- **`400m` of memory.** Lower-case `m` means milli, so 0.4 bytes. [172]
- **A Secret is not a vault.** It is stored unencrypted in etcd by default, and anyone allowed to create Pods in the namespace can read it. [170]
- **Stateless ACL.** A network ACL does not allow return traffic automatically; a rule set that admits requests but not the replies breaks the connection. [176]

:::low-confidence
`deployment.yaml` passed kubeconform v0.6.7 in strict mode against its default schemas and against Kubernetes 1.34.0 schemas, but it was not applied to a cluster, and its image name is a placeholder. Probe timing defaults (`periodSeconds`, `failureThreshold`) were not in the notes, so the manifest sets them explicitly. One-line definitions of IAM users and groups were not captured either; read "IAM identities" in the IAM User Guide. No vendor page in the notes says "do not paste secrets" in those words: that advice rests on OWASP LLM02.
:::

:::key-takeaways
- An LLM works within a limited context window and can be wrong; give it specific context and verify its output with tests. [181] [180] [182]
- Keep secrets out of prompts (LLM02) and treat content a tool reads as a possible injection (LLM01). [183]
- Control plane: API server, etcd, scheduler, controller manager; nodes: kubelet, kube-proxy, runtime. [166]
- Rolling updates default to 25% max unavailable and 25% max surge; readiness removes a Pod from traffic, liveness restarts it. [168] [171]
- Security groups are stateful allow lists on instances; network ACLs are stateless, ordered rules on subnets. [176]
- AWS secures the cloud; you secure your instances, data and IAM policies. [179]
:::

:::glossary
- **Large language model (LLM)**: a program trained on huge amounts of text that predicts and generates text.
- **Tokens**: the small chunks of text a language model reads and writes.
- **Context window**: everything the model can see at once while it answers.
- **Hallucination**: a fluent answer that is factually wrong.
- **Prompt injection**: hidden or planted instructions that steer a model away from what its user wanted.
- **Model Context Protocol (MCP)**: an open standard for plugging tools and data sources into AI applications.
- **Control plane**: the Kubernetes components that store and act on the cluster's desired state.
- **Controllers**: loops that keep nudging the current state towards the desired state.
- **Pod**: one or more containers scheduled together with a shared IP address.
- **Deployment**: a Kubernetes object that keeps a number of identical Pods running and rolls out changes.
- **Service**: a stable address in front of a changing set of Pods.
- **VPC**: a private, isolated network inside AWS.
- **Security group**: a stateful firewall attached to instances.
- **Network ACL**: a stateless, ordered rule list attached to a subnet.
- **IAM**: AWS's system for identities and permissions.
- **Least privilege**: giving each identity only the permissions its task needs.
:::
