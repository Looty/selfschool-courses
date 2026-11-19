---
id: l14
title: "Network and SSH troubleshooting"
quiz: quiz-03.yaml
sources: [112, 113, 117, 118, 123, 124]
---
After this lesson you can find out why a service cannot be reached by checking five layers in order, and set up SSH key login, a jump host and a port forward from memory.

## The routine: five questions, bottom up

"I can't reach the API" has many causes. Ask the same five questions every time, in order, and stop at the first "no":

| # | Question | Command |
| --- | --- | --- |
| 1 | Is the process running? | `systemctl status vmapi` [118] or `ps -o user,pid,cmd -p PID` |
| 2 | Is it listening, on which address and port? | `ss -ltnp` [112] |
| 3 | Does the machine have that address and a route? | `ip -br addr`, `ip route` [113] |
| 4 | Can a client reach it, from where? | a request from the box itself, then from a neighbour |
| 5 | What did the service log? | `journalctl -u vmapi -n 50 --no-pager` [117] |

`ss` lists sockets: `-l` only listening ones, `-t` TCP, `-u` UDP, `-n` numeric ports, `-p` the owning process. [112] With no options it shows only established connections, which is why a listener seems "missing" until you add `-l`. [112] `ip` takes an object and a command: `ip addr`, `ip route`, `ip link set eth0 up`; `-br` gives a short table. [113]

## Worked example: listening on the wrong address

This is fault 2 of the lab in lesson 4, from the course's test run. Step 1: the process is up. Step 2:

```console
# ss -ltn
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 0      5          127.0.0.1:8080      0.0.0.0:*
```

Step 3:

```console
# ip -br addr
lo               UNKNOWN        127.0.0.1/8 ::1/128
eth0@if115       UP             172.17.0.2/16
# ip route
default via 172.17.0.1 dev eth0
172.17.0.0/16 dev eth0 proto kernel scope link src 172.17.0.2
```

Step 4: the box has no `curl`, but bash can open a TCP connection through the special file name `/dev/tcp/HOST/PORT`. [124]

```console
# (exec 3<>/dev/tcp/127.0.0.1/8080 && echo open)
open
# (exec 3<>/dev/tcp/172.17.0.2/8080 && echo open)
bash: connect: Connection refused
bash: line 1: /dev/tcp/172.17.0.2/8080: Connection refused
```

The socket is bound to `127.0.0.1`, the loopback address, so only connections made to loopback on the same machine reach it. Clients on other machines arrive at `172.17.0.2` and are refused. The fix is in the service's configuration (`bind = 0.0.0.0`), not in the network. After a restart, `ss` shows `0.0.0.0:8080`, meaning every IPv4 address of the box.

How to read `Local Address`:

| You see | Meaning |
| --- | --- |
| `127.0.0.1:8080` | loopback only: same machine |
| `0.0.0.0:8080` | all IPv4 addresses |
| `[::]:8080` or `*:8080` | all addresses (IPv6 socket, often IPv4 too) |
| `10.0.3.7:8080` | that one interface only |
| no line at all | not listening: wrong port, crashed, or not started |

:::low-confidence
"Connection refused" (nothing listens at that address and port; the test run shows it) and a timeout (packets dropped, often by a firewall or a missing route) are different symptoms with different causes. The notes for this course do not cover firewalls, `ping`, `curl` or `nc`, nor the IPv4 behaviour of `[::]` sockets; check `nft list ruleset` or `iptables -L` on your distribution, the curl(1) man page, and `net.ipv6.bindv6only` in the kernel's ip-sysctl documentation.
:::

## SSH key login

`ssh [user@]host [command]` logs in, or runs one command and exits with that command's status; ssh itself exits with 255 on its own errors. [123] Public key login works like this: you create a key pair with `ssh-keygen`; the private key stays on your machine in `~/.ssh/id_*`; the public key goes on one line of `~/.ssh/authorized_keys` on the server. [123]

```console
$ ssh-keygen -q -t ed25519 -N "" -f ~/.ssh/id_ed25519
$ ls -l ~/.ssh
-rw------- 1 ops ops 399 Nov 19 12:24 id_ed25519
-rw-r--r-- 1 ops ops  92 Nov 19 12:24 id_ed25519.pub
```

`-i FILE` picks a private key; without it ssh tries the default `~/.ssh/id_rsa`, `id_ecdsa`, `id_ed25519` and a few others. [123] `-v` (up to `-vvv`) shows which keys it offers and what the server accepts. [123]

The client also checks the server. ssh records every host key it has seen in `~/.ssh/known_hosts`. [123] `StrictHostKeyChecking=accept-new` adds unknown hosts without asking; the default is `ask`. [123] If a known host's key changes, ssh warns of a possible man-in-the-middle attack and refuses. [123] In the test run, after the bastion's host keys were regenerated:

```console
$ ssh ops@pce-ch05-bastion hostname
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
...
Host key verification failed.
$ ssh-keygen -R pce-ch05-bastion
...
/home/ops/.ssh/known_hosts updated.
```

Remove the old entry only after you know why the key changed (for example, the VM was rebuilt).

## Jump hosts and port forwarding

Private VMs are often reachable only through a bastion. `-J` connects to the jump host first and forwards to the destination; several hops are comma-separated. [123] `-L [bind_address:]port:host:hostport` listens on a local port and connects to `host:hostport` from the remote side. [123] `-N` runs no remote command and `-f` goes to the background. [123] From the test run, where `vm` sat on a network only the bastion could reach, and served HTTP on its own loopback:

```console
$ ssh -o ConnectTimeout=5 ops@pce-ch05-vm hostname; echo "exit=$?"
ssh: Could not resolve hostname pce-ch05-vm: Name or service not known
exit=255
$ ssh -J ops@pce-ch05-bastion -o StrictHostKeyChecking=accept-new ops@pce-ch05-vm hostname
Warning: Permanently added 'pce-ch05-vm' (ED25519) to the list of known hosts.
vm
$ ssh -f -N -L 9000:127.0.0.1:8080 -J ops@pce-ch05-bastion ops@pce-ch05-vm
$ python3 -c 'import urllib.request as u; print(u.urlopen("http://127.0.0.1:9000/").status)'
200
```

In `-L 9000:127.0.0.1:8080`, `127.0.0.1` is resolved on the far end, so it means the VM's own loopback. Prefer `-J` over agent forwarding (`-A`): anyone who can bypass file permissions on the remote host can use a forwarded agent. [123]

## ~/.ssh/config

ssh takes options from the command line, then `~/.ssh/config`, then `/etc/ssh/ssh_config`, and the first value found wins, so specific `Host` blocks go at the top and `Host *` at the bottom. [123] `*` and `?` are wildcards. [123] This file made `ssh vm-01` work in the test run:

```text
Host bastion
    HostName pce-ch05-bastion
    User ops

Host vm-*
    HostName pce-ch05-%h
    User ops
    ProxyJump bastion
    IdentityFile ~/.ssh/id_ed25519

Host *
    ServerAliveInterval 30
    StrictHostKeyChecking accept-new
```

`%h` expanded to the name typed (`vm-01`), as `ssh -G vm-01` showed. The config file must not be writable by others. [123]

## Gotchas

- **Checking `ss` without `-l`.** Plain `ss` shows established connections only. [112]
- **"Works on the box, not from outside".** Look at the `Local Address` column first; `127.0.0.1` explains it. [112]
- **Options for the jump host on the command line.** They apply to the destination; put jump host settings in `~/.ssh/config`. [123]
- **Deleting known_hosts entries by reflex.** The warning exists to catch a spoofed server; confirm the rebuild first. [123]
- **Exit status 255.** It is ssh's own error (resolve, connect, auth), not the remote command's. [123]
- **Loose permissions on `authorized_keys`.** In the test run, sshd refused a mode `666` file: `Authentication refused: bad ownership or modes`, and the client saw only `Permission denied (publickey)`. Keep `~/.ssh` at `700` and the file at `600`.

:::key-takeaways
- Process, listener, address and route, reachability, logs: in that order. [112] [113] [117]
- `ss -ltnp` shows what listens where; `127.0.0.1` means local only. [112]
- Key login: private key stays local, public key goes into the server's `authorized_keys`. [123]
- `-J` for bastions, `-L local:host:port` for tunnels, `known_hosts` guards against spoofing. [123]
- In `~/.ssh/config` the first value wins: specific blocks first. [123]
:::

:::glossary
- **Loopback**: the address 127.0.0.1, which only reaches the same machine.
- **Socket**: one end of a network connection, or a listener waiting for connections.
- **Bastion**: a host you log in to first in order to reach machines behind it; also called a jump host.
- **Host key**: the server's own key pair, which proves to the client it is the same server as last time.
- **known_hosts**: the client's list of host keys it has seen.
- **authorized_keys**: the server-side list of public keys allowed to log in as a user.
- **Port forwarding**: carrying a TCP connection from one port through the SSH connection to another host and port.
:::
