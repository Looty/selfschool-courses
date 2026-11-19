---
id: l32
title: "Ansible and Fabric: configuration and remote execution"
quiz: quiz-01.yaml
resources: [../resources/ch12/site.yml, ../resources/ch12/inventory.ini, ../resources/ch12/templates/vmapi.service.j2, ../resources/ch12/fabfile.py]
sources: [126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140]
---
After this lesson you can read and write an Ansible playbook that rolls a Python service across a group of hosts, explain why it is safe to run twice, and script the same fleet imperatively with Fabric, knowing when each tool fits.

## Ansible's model

Three parts: the **control node**, where Ansible is installed and you run `ansible-playbook`; the **inventory**, a list of managed nodes; and the **managed nodes**, the hosts Ansible controls. [127] Ansible is agentless: it reaches hosts over SSH with existing credentials. [127] A managed node does not need Ansible, but it needs Python to run the code Ansible generates and an account that can log in over SSH. [127] Ansible pushes small programs, its **modules**, to the nodes, runs them and removes them afterwards. [139] The exception is `ansible-pull`, which checks out a Git repository on the node and runs `ansible-playbook` locally; the docs call that setup rare and not recommended. [127] [129]

Red Hat, which sponsors Ansible, contrasts this with Puppet's agent on every device and argues agents must be installed, patched and allowed on every target. [140] Treat that as the vendor's view.

Versions: the current community package is Ansible 14, built on ansible-core 2.21, whose control node needs Python 3.12 to 3.14 and whose managed nodes need Python 3.9 to 3.14. [126] ansible-core 2.22 was listed for November 2026. [126]

## Inventory

```ini
[hv_mgmt]
hvm01 ansible_host=192.0.2.11
hvm04 ansible_host=192.0.2.14 vmapi_workers=4

[hv_mgmt:vars]
ansible_user=deploy
vmapi_port=8080
vmapi_workers=2

[production:children]
hv_mgmt
```

`[name:vars]` sets group variables, a `key=value` after a host sets a host variable, and `:children` makes a parent group. [128] Every host is also in `all`. [128] Host variables merge over group ones [128], as `ansible-inventory` showed in the course's test run (ansible-core 2.21.6):

```text
$ ansible-inventory -i inventory.ini --host hvm04
{
    "ansible_host": "192.0.2.14",
    "ansible_user": "deploy",
    "vmapi_port": 8080,
    "vmapi_workers": 4
}
```

The YAML form nests `hosts:`, `vars:` and `children:` under each group. [128] For more than a few variables, use `group_vars/<group>.yml` and `host_vars/<host>.yml` files. [128]

## A playbook, keyword by keyword

A playbook is a list of **plays**. Each play maps a host pattern to an ordered list of tasks, and each task calls one module. [129] By default each task runs on every host before the next task starts. [129] The deploy play in `site.yml`, trimmed:

```yaml
- name: Deploy vmapi, one host at a time
  hosts: hv_mgmt
  become: true
  serial: 1
  tasks:
    - name: Install the operating system packages
      ansible.builtin.apt:
        name: [python3, python3-venv, curl]
        state: present
      when: ansible_facts['os_family'] == "Debian"
    - name: Create the service directories
      ansible.builtin.file:
        path: "{{ item.path }}"
        state: directory
        mode: "{{ item.mode }}"
      loop: "{{ vmapi_dirs }}"
    - name: Create the virtual environment
      ansible.builtin.command:
        cmd: "python3 -m venv {{ vmapi_home }}/venv"
        creates: "{{ vmapi_home }}/venv/bin/python"
    - name: Write the systemd unit
      ansible.builtin.template:
        src: templates/vmapi.service.j2
        dest: /etc/systemd/system/vmapi.service
      notify: [Reload systemd, Restart vmapi]
    - ansible.builtin.meta: flush_handlers
  handlers:
    - name: Reload systemd
      ansible.builtin.command: {cmd: systemctl daemon-reload}
    - name: Restart vmapi
      ansible.builtin.service: {name: vmapi, state: restarted}
```

| Keyword | What it does |
| --- | --- |
| `become: true` | Privilege escalation; the default method is sudo, the default user root. [129] |
| `name:` as a list | apt takes a list, which is faster than a loop. [131] [135] |
| `when:` | A raw Jinja2 expression without `{{ }}`, evaluated per host. [131] |
| `loop:` / `item` | Repeats the task once per element. [131] |
| `"{{ ... }}"` | Quoted, because YAML breaks on a value that starts with `{{`. [130] |
| `template` | Renders a Jinja2 file from the control node onto the host. [135] |
| `notify` / `handlers` | A handler runs only when a task reports changed, once, at the end of the play, in the order the handlers are written. [131] |
| `meta: flush_handlers` | Runs pending handlers now, so the health check sees the new version. [131] |
| `register` + `until` | Saves a task's result and retries; `site.yml` polls `/healthz` with `retries: 10`, `delay: 3`. [130] [131] |

## Idempotency and why `command` needs help

Most modules compare the host with the desired state and do nothing if it already matches, so running a playbook twice gives the same result. [129] `command` and `shell` run arbitrary commands, so Ansible cannot know what they changed. The docs give `creates`/`removes` (skip the task if a path exists, or if it does not) and `changed_when` (you define "changed"). [135] [131] `site.yml` uses both:

```yaml
register: pip_result
changed_when: "'Successfully installed' in pip_result.stdout"
notify: Restart vmapi
```

Prefer `command` to `shell` unless you need pipes or redirects. [135] Watch other always-changed cases: `service` with `state: restarted` always bounces the service, and a date in a template changes the file every run. [135]

## Running it safely

```bash
ansible-playbook -i inventory.ini site.yml --syntax-check
ansible-playbook -i inventory.ini site.yml --check --diff    # predict, change nothing
ansible-playbook -i inventory.ini site.yml --limit hvm01     # one host first
ansible-playbook -i inventory.ini site.yml -f 20             # forks, default 5
```

`--check` reports what would change; `--limit` narrows the host pattern, for example `'hv_mgmt:!hvm04'`. [129] In check mode, a `command` task without `creates` is skipped. [135] `serial: 1` runs the whole play on one host before the next; `"30%"` or a list like `[1, 5, 10]` makes growing batches, and `max_fail_percentage` aborts when too many in a batch fail. [136] [131] The `--limit` example, from the course's test run, trimmed to the deploy play:

```text
$ ansible-playbook -i inventory.ini site.yml --list-hosts --limit 'hv_mgmt:!hvm04'
  play #2 (hv_mgmt): Deploy vmapi, one host at a time	TAGS: []
    pattern: ['hv_mgmt']
    hosts (3):
      hvm01
      hvm02
      hvm03
```

**Variable precedence**, lowest to highest, main rungs: role defaults, inventory group variables, inventory host variables, facts, play `vars`, role `vars`, task `vars`, registered variables, and extra vars (`-e`), which always win. [130] That is why `site.yml` does not set `vmapi_workers` in play `vars`: it would override hvm04's host value.

**Roles** package tasks, handlers, templates and variables in a fixed layout: `roles/vmapi/tasks/main.yml`, `handlers/`, `templates/`, `defaults/` (lowest precedence), `vars/` (high). [132]

**Vault** encrypts secrets so they can live in Git: `ansible-vault encrypt_string 's3cret' --name 'db_password'` for one value, `ansible-vault encrypt group_vars/all/secrets.yml` for a file, and `--ask-vault-pass` at run time. [133] It protects data at rest only; mark tasks that handle the decrypted value `no_log`. [133]

**Ad hoc commands** run one module without a playbook: `ansible hv_mgmt -m ansible.builtin.service -a "name=vmapi state=started" --become`; without `-m`, the module is `command`. [134]

## Fabric

Fabric is a Python library that runs shell commands over SSH and returns Python objects, built on Invoke (local execution and the CLI) and Paramiko (the SSH protocol). [137] Paramiko is a pure-Python SSHv2 implementation. [138] The changelog's newest entry was 3.2.2 [137]; `pip install fabric` gave 3.2.3 in the course's test run.

```python
from fabric import Connection, ThreadingGroup

c = Connection("deploy@hvm01:22")
r = c.run("uname -s", hide=True)       # Result: .stdout .exited .ok .failed .command
c.run("test -f /etc/vmapi.conf", warn=True).failed   # no exception on non-zero exit
c.put("vmapi.tgz", remote="/tmp/")      # get() downloads
c.sudo("systemctl restart vmapi")       # needs the sudo.password config value
results = ThreadingGroup("hvm01", "hvm02").run("uptime", hide=True)  # GroupResult
```

`SerialGroup` and `ThreadingGroup` wrap several connections; Fabric 1's `@parallel` became `ThreadingGroup`. [137] A group call returns a dict-like `GroupResult` from each Connection to its Result, and raises `GroupException` when any host fails. [137] Tasks are functions decorated with `@task`; `fab -H web1,web2 mytask` runs the task once per host, passing a Connection as its first argument. [137] `fabfile.py` instead builds its own groups, `status` with `ThreadingGroup` and `rolling-restart` with `SerialGroup` plus a health poll. From the course's test run:

```text
$ fab --list
Available tasks:

  rolling-restart   Restart a service one host at a time; stop at the first
                    unhealthy host.
  status            Print uptime, load and free disk for every host, gathered
                    in parallel.
```

## Which tool when

| | Ansible | Fabric |
| --- | --- | --- |
| Style | Declared state, idempotent modules | Imperative Python steps |
| Fleet features | Inventory, groups, `serial`, check mode, Vault | Groups and threads; the rest you write |
| Lacks | Real programming; loops and logic in YAML get awkward | Idempotence, dry run, secret store, reporting of changes |

Use Ansible for configuration that must stay correct on every host. Use Fabric for an operational script, such as a status sweep or a custom restart, where Python logic matters more than declared state.

## Gotchas

- **Handler did not run.** It runs only when a notifying task reports changed, and by default not if a later task failed on that host (`--force-handlers`). [131] Handlers wait for the end of the play, so flush them before a health check. [131]
- **`changed` on every run.** An unguarded `command`/`shell` task breaks idempotency. Add `creates`, `removes` or `changed_when`. [135] [131]
- **Pipes do nothing.** `command` does not go through a shell, so `|`, `>` and `;` do not work; use `shell`, with `| quote` on variables. [135]
- **Wrong file mode.** An unquoted `mode: 644` is read as decimal; write `"0644"`. [135]
- **Extra vars are strings.** `-e count=3` passes the string `"3"`; use JSON for numbers and booleans. [130]
- **Fabric sudo hangs.** `run("sudo ...")` needs `pty=True` and an answer to the prompt; `sudo()` needs `sudo.password` configured. [137]

:::low-confidence
What was run for this lesson, and what was not. `site.yml` passed `ansible-playbook --syntax-check`, `--list-tasks` and `--list-hosts` with ansible-core 2.21.6 in a WSL Ubuntu environment; `ansible-inventory --graph` and `--host` gave the output above. No managed hosts were available, so the playbook was never applied, not even in check mode, and the vmapi package and index URL are placeholders. The template was rendered with Jinja2 and sample values. `fabfile.py` was tested only offline: its parsing and table code on canned `uptime` and `df` output, and `fab --list` with Fabric 3.2.3 on Python 3.13 and 3.11. No SSH connection was made. The `system` and `shell` options of `ansible.builtin.user` and the reading of `SerialGroup` as one host after another (confirmed in Fabric's installed source, not its docs) are outside the course notes; check the module docs and Fabric's API docs.
:::

:::key-takeaways
- The control node pushes modules over SSH; managed nodes need Python and an SSH account, not an agent. [127] [139]
- Plays map hosts to ordered tasks; each task calls one module. [129]
- Handlers run once, at the end of the play, only after a changed notification. [131]
- Guard `command`/`shell` with `creates` or `changed_when`; verify with `--check --diff` and `--limit`. [135] [129]
- `serial` turns a play into a rolling update; extra vars beat every other variable. [136] [130]
- Fabric is Python over SSH: `Connection.run` returns a Result, groups return a GroupResult. [137]
:::

:::glossary
- **Control node**: the machine where Ansible is installed and run.
- **Managed nodes**: the remote hosts that Ansible configures.
- **Inventory**: the file or script listing managed hosts, their groups and variables.
- **Playbook**: a YAML file holding one or more plays.
- **Plays**: blocks that map a set of hosts to an ordered list of tasks.
- **Modules**: small programs Ansible copies to a host to do one kind of action.
- **Handler**: a task that runs only when another task reports a change and notifies it.
- **Idempotency**: running the same thing twice leaves the system as running it once did.
- **Check mode**: a run that reports what would change without changing anything.
- **Vault**: Ansible's tool for encrypting secrets stored next to playbooks.
- **Fabric**: a Python library for running commands on remote hosts over SSH.
- **Paramiko**: the pure-Python SSH implementation underneath Fabric.
- **Invoke**: the Python library behind Fabric's local commands and `fab` CLI.
:::
