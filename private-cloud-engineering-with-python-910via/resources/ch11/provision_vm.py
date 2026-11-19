"""Idempotently define and start a libvirt domain from an XML file (lesson l31).

Run it twice and the second run changes nothing:

    python3 provision_vm.py domain.xml                       # qemu:///system
    python3 provision_vm.py --uri qemu+ssh://root@kvm-017/system domain.xml

libvirt's test driver (URI test:///default) needs no KVM, but it starts fresh in every
new process (with one domain called "test"), so to see the second run change nothing
there, call ensure_running() twice on one connection (lesson l31 shows how).

Steps, each safe to repeat:
  1. Read the domain name from the XML.
  2. If libvirt does not know the name, define it (persistent, not started).
     If it exists only as a transient domain, define it to make it persistent.
  3. If it is not running, start it. A paused domain counts as active and is left paused.

It never redefines a domain that already exists persistently: changing a running VM's
configuration is a separate, deliberate operation (virsh edit, or a reconciler).

Needs the libvirt Python binding (Debian/Ubuntu package python3-libvirt, or pip
package libvirt-python built against the host's libvirt). Exit status: 0 on success,
1 on a libvirt error, 2 on bad input.
"""

import argparse
import sys
import xml.etree.ElementTree as ET

import libvirt


def domain_name(xml: str) -> str:
    """Return the <name> of a domain XML document, or raise ValueError."""
    name = ET.fromstring(xml).findtext("name")
    if not name:
        raise ValueError("domain XML has no <name> element")
    return name.strip()


def ensure_running(conn: "libvirt.virConnect", xml: str) -> list[str]:
    """Make sure the domain described by xml is defined, persistent and running."""
    name = domain_name(xml)
    actions = []

    # listAllDomains returns active and inactive domains; match on the name.
    existing = {dom.name(): dom for dom in conn.listAllDomains()}
    dom = existing.get(name)

    if dom is None:
        dom = conn.defineXML(xml)
        actions.append("defined")
    elif not dom.isPersistent():
        dom = conn.defineXML(xml)
        actions.append("made persistent")

    if dom.isActive():
        actions.append("already running")
    else:
        dom.create()
        actions.append("started")
    return actions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("xml_file", help="path to the domain XML")
    parser.add_argument("--uri", default="qemu:///system", help="libvirt connection URI")
    args = parser.parse_args(argv)

    try:
        with open(args.xml_file, encoding="utf-8") as f:
            xml = f.read()
        name = domain_name(xml)
    except (OSError, ET.ParseError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    try:
        conn = libvirt.open(args.uri)
    except libvirt.libvirtError as exc:
        print(f"error: cannot connect to {args.uri}: {exc}", file=sys.stderr)
        return 1

    try:
        actions = ensure_running(conn, xml)
    except libvirt.libvirtError as exc:
        print(f"error: {name}: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    print(f"{name}: {', '.join(actions)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
