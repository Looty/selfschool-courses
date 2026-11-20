---
id: l06
title: "Network and SSH troubleshooting"
quiz: quiz-06.yaml
sources: [112, 113, 117, 118, 123, 124]
---
After this lesson you can read `ss -ltnp`, tell "connection refused" from a timeout, fix SSH key permission errors, and answer "I can't reach the API" and "I can't SSH in" in order.

## ss -ltnp: who listens where

**Rule:** `ss -ltnp` lists **l**istening **T**CP sockets with **n**umeric ports and the owning **p**rocess; the `Local Address` column says which address the program accepts calls on. [112]

```console
# ss -ltn                       # course test run, the lab's vmapi
State  Recv-Q Send-Q Local Address:Port Peer Address:Port
LISTEN 0      5          127.0.0.1:8080      0.0.0.0:*
```

Reading `Local Address`, one rung per case:

```text
127.0.0.1:8080     loopback only: callers on the same machine
0.0.0.0:8080       every IPv4 address of the box
[::]:8080, *:8080  every address (IPv6 socket)
10.0.3.7:8080      that one interface only
(no line)          not listening: crashed, not started, wrong port
```

Edge: plain `ss` without `-l` shows only established connections, so a healthy listener looks "missing". [112]

**P1.** `ss -ltnp` shows `127.0.0.1:5432`. A colleague on another VM cannot connect. Is the fix in the network or in the program's config?

:::answer
The program's config: it listens on loopback only. Bind to `0.0.0.0` and restart.
:::

## Connection refused versus timeout

**Rule:** "refused" is a fast, polite "nobody lives at that port"; a timeout is silence, because nothing answered at all.

Bash can open a TCP connection itself through the file name `/dev/tcp/HOST/PORT`, so no `curl` is needed. [124]

```console
# (exec 3<>/dev/tcp/127.0.0.1/8080 && echo open)       # 1. listener there
open
# (exec 3<>/dev/tcp/172.17.0.2/8080 && echo open)      # 2. bound to loopback only
bash: connect: Connection refused
$ (exec 3<>/dev/tcp/127.0.0.1/1)                       # 3. nothing on port 1
bash: connect: Connection refused
$ timeout 4 bash -c 'exec 3<>/dev/tcp/10.255.255.1/80' # 4. edge: nothing answers
```

Rungs 1-2: course test run; 3-4: Ubuntu. Rung 4 printed nothing; it hung until `timeout` stopped it at 4 seconds.

**Contrast:**

| Symptom | What it means | Check next |
| --- | --- | --- |
| Connection refused, at once | the host answered; no listener on that address and port | `ss -ltnp` on the server |
| Hangs, then times out | no answer came back | firewall, route (`ip route`) |

:::low-confidence
The sources do not cover firewalls or timeouts. A firewall that drops packets or a missing route are the usual causes of a timeout; check `nft list ruleset` or `iptables -L` and the curl(1) man page.
:::

**P2.** A request from your laptop to `10.0.3.7:8080` hangs for a minute; the same request on the box answers. Refused or timeout, and which layer do you suspect?

:::answer
Timeout: nothing answered. Suspect a firewall or route between laptop and box, not the program.
:::

## SSH keys and their permissions

**Rule:** the private key stays on your machine and must be readable only by you; the public key goes on one line of `~/.ssh/authorized_keys` on the server. [123] ssh ignores a private key that others can access. [123]

```console
$ ssh-keygen -q -t ed25519 -N "" -f ~/.ssh/id_ed25519     # course test run
$ ls -l ~/.ssh
-rw------- 1 ops ops 399 Nov 19 12:24 id_ed25519          # 600: private
-rw-r--r-- 1 ops ops  92 Nov 19 12:24 id_ed25519.pub      # 644: public is fine
```

What happens to a key with looser modes (`ssh-keygen -y` loads the key; run on Ubuntu):

```console
$ chmod 644 id_test; ssh-keygen -y -f ./id_test
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
Permissions 0644 for './id_test' are too open.
This private key will be ignored.
Load key "./id_test": bad permissions
```

`600` and `400` loaded fine; edge: `640` was refused too, because the group can read it. On the server side, the course test run had sshd refuse a mode `666` `authorized_keys` (`Authentication refused: bad ownership or modes`); the client saw only `Permission denied (publickey)`. Keep `~/.ssh` at `700` and the files at `600`.

**Contrast:** three SSH failures to tell apart.

| Client sees | Cause | Fix |
| --- | --- | --- |
| exit status 255 | ssh's own error, not the remote command's [123] | read the message above it |
| `REMOTE HOST IDENTIFICATION HAS CHANGED` | host key differs from `~/.ssh/known_hosts` [123] | confirm a rebuild, then `ssh-keygen -R HOST` |
| `Permission denied (publickey)` | no offered key accepted [123] | `ssh -v`; key and `authorized_keys` modes |

**P3.** `ssh -i ~/.ssh/deploy_key ops@vm` fails, and `ls -l` shows `-rw-r----- deploy_key`. What is wrong and what is the one-command fix?

:::answer
The group can read the key, so ssh ignores it. `chmod 600 ~/.ssh/deploy_key`.
:::

## "I can't reach the API": the walk-through

Stop at the first "no":

1. `systemctl status vmapi`: is the process running? [118]
2. `ss -ltnp`: listening, on which address and port? [112]
3. `ip -br addr; ip route`: does the box have that address and a route? [113]
4. `/dev/tcp` from the box, then from a neighbour: refused or timeout? [124]
5. `journalctl -u vmapi -n 50 --no-pager`: what did it log? [117]

## "I can't SSH in": the walk-through

1. Exit 255? It is ssh failing, not your command. [123]
2. Host key warning? Confirm a rebuild before `ssh-keygen -R`. [123]
3. `Permission denied (publickey)`: `ssh -v` shows the keys offered. [123]
4. Modes: key `600`, `~/.ssh` `700`, `authorized_keys` `600`.

## Cheat sheet

| Tool | Rule | Tiny example → result |
| --- | --- | --- |
| `ss -ltnp` | listeners, numeric, with process | `127.0.0.1:8080` → local only |
| `/dev/tcp/H/P` | bash opens TCP | refused → no listener; hang → no answer |
| private key mode | only you may read it | `640` → ignored |
| ssh exit 255 | ssh's own failure | remote command never ran |

## If you missed a quiz question

**If you thought** plain `ss` shows listeners: reread "ss". **R1.** What does `ss` without `-l` list?

:::answer
Established connections only; add `-l`.
:::

**If you thought** refused means a firewall: reread "Refused vs timeout". **R2.** What does an instant "refused" prove?

:::answer
The host answered: no listener there.
:::

**If you thought** ssh exit 255 is the remote command's status: reread "SSH keys". **R3.** Did the remote command fail?

:::answer
No: 255 is ssh's own error.
:::

**If you thought** group-readable keys are fine: reread "SSH keys". **R4.** Is `640` OK for a private key?

:::answer
No: `640` lets the group read it; use `600`.
:::

:::key-takeaways
- `ss -ltnp`; `127.0.0.1` means same machine only. [112]
- Refused: no listener. Timeout: no answer.
- Private key `600`; ssh ignores keys others can read. [123]
:::

:::glossary
- **Socket**: one end of a network connection, or a listener waiting for connections.
- **Loopback**: the address 127.0.0.1, which only reaches the same machine.
- **Host key**: the server's own key, which proves it is the same server as last time.
- **known_hosts**: the client's list of host keys it has seen.
- **authorized_keys**: the server-side list of public keys allowed to log in as a user.
:::
