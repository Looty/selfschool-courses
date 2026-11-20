---
id: l06
title: "Network and SSH troubleshooting"
quiz: quiz-06.yaml
sources: [112, 113, 117, 118, 123, 124]
---
After this lesson you can answer "I can't reach the service" and "I can't SSH in" by checking layers in order, and set up key login, a jump host and a port forward from memory.

## "I can't reach the API": five questions, bottom up

Stop at the first "no":

```bash
systemctl status vmapi                   # 1. is the process running?
ss -ltnp                                 # 2. listening, on which address and port?
ip -br addr; ip route                    # 3. does the box have that address and a route?
(exec 3<>/dev/tcp/127.0.0.1/8080 && echo open)   # 4. reachable? from the box, then a neighbour
journalctl -u vmapi -n 50 --no-pager     # 5. what did the service log?
```

[112] [113] [117] [118]

`ss` flags: `-l` listening, `-t` TCP, `-u` UDP, `-n` numeric, `-p` owning process. [112] Without `-l` it shows only established connections, so a listener seems "missing". [112] Step 4 works without `curl`: bash opens a TCP connection for the file name `/dev/tcp/HOST/PORT`. [124]

## Worked example: works on the box, not from outside

```console
# ss -ltn
State  Recv-Q Send-Q Local Address:Port Peer Address:Port
LISTEN 0      5          127.0.0.1:8080      0.0.0.0:*
# (exec 3<>/dev/tcp/172.17.0.2/8080 && echo open)
bash: connect: Connection refused
```

The socket is bound to loopback, so only the same machine reaches it. The fix is the service's config (`bind = 0.0.0.0`), not the network. Read `Local Address` like this:

```text
127.0.0.1:8080     loopback only: same machine
0.0.0.0:8080       all IPv4 addresses
[::]:8080, *:8080  all addresses (IPv6 socket)
10.0.3.7:8080      that one interface only
(no line)          not listening: wrong port, crashed, not started
```

:::low-confidence
"Connection refused" (nothing listens there; the test run shows it) and a timeout (packets dropped, often by a firewall or a missing route) are different symptoms. The notes do not cover firewalls, `ping`, `curl` or `nc`; check `nft list ruleset` or `iptables -L` and the curl(1) man page.
:::

## SSH key login

The private key stays in `~/.ssh/id_*` on your machine; the public key goes on one line of `~/.ssh/authorized_keys` on the server. [123]

```bash
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519   # create the pair
ssh -i ~/.ssh/id_ed25519 ops@host            # pick a key; default tries id_rsa, id_ed25519...
ssh -vvv ops@host                            # which keys are offered and accepted
ssh ops@host systemctl restart vmapi         # run one command; exits with its status
```

[123]

## "I can't SSH in": the walk-through

1. **Exit status 255** is ssh's own error (resolve, connect, host key, auth), not the remote command's. [123]
2. **`Could not resolve hostname`**: the name is wrong or reachable only through a bastion.
3. **`REMOTE HOST IDENTIFICATION HAS CHANGED`** then `Host key verification failed`: the key differs from `~/.ssh/known_hosts`, a possible man-in-the-middle. [123] Only after you confirm a rebuild, run `ssh-keygen -R HOST`. `StrictHostKeyChecking=accept-new` adds unknown hosts without asking. [123]
4. **`Permission denied (publickey)`**: no offered key was accepted. Use `-v` to see which were tried. [123] In the test run, sshd refused a mode `666` `authorized_keys` (`bad ownership or modes`); keep `~/.ssh` at `700` and the file at `600`.

## Jump hosts and port forwarding

`-J` connects through a jump host; `-L [bind:]port:host:hostport` listens locally and connects to `host:hostport` from the far side; `-N` runs no command, `-f` backgrounds. [123]

```bash
ssh -J ops@bastion ops@vm hostname
ssh -f -N -L 9000:127.0.0.1:8080 -J ops@bastion ops@vm   # laptop:9000 -> vm's loopback:8080
```

`127.0.0.1` in `-L` is resolved on the far end. Prefer `-J` over agent forwarding (`-A`): anyone who can bypass file permissions on the remote host can use a forwarded agent. [123]

## ~/.ssh/config

For each option the first value found wins (command line, then `~/.ssh/config`, then `/etc/ssh/ssh_config`), so specific `Host` blocks go first and `Host *` last. [123]

```text
Host vm-*
    User ops
    ProxyJump bastion
Host *
    ServerAliveInterval 30
```

:::key-takeaways
- Process, listener, address and route, reachability, logs: in that order. [112] [113] [117]
- `ss -ltnp`; `127.0.0.1` means local only. [112]
- ssh exit 255 is ssh's own failure; `-v` shows the key exchange. [123]
- `-J` for bastions, `-L local:host:port` for tunnels; in `~/.ssh/config` the first value wins. [123]
:::

:::glossary
- **Loopback**: the address 127.0.0.1, which only reaches the same machine.
- **Bastion**: a host you log in to first in order to reach machines behind it; also called a jump host.
- **authorized_keys**: the server-side list of public keys allowed to log in as a user.
:::
