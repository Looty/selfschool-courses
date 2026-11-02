"""Command-line entry point: `devenv doctor` and `devenv compare`."""

import argparse
import sys
import sysconfig
from pathlib import Path

from packaging.version import InvalidVersion, Version

from . import __version__


def doctor(_args: argparse.Namespace) -> int:
    """Print which interpreter runs this tool and whether it is isolated."""
    in_venv = sys.prefix != sys.base_prefix
    marker = Path(sysconfig.get_path("stdlib")) / "EXTERNALLY-MANAGED"
    print(f"devenv        {__version__}")
    print(f"executable    {sys.executable}")
    print(f"prefix        {sys.prefix}")
    print(f"base_prefix   {sys.base_prefix}")
    print(f"in a venv     {'yes' if in_venv else 'no'}")
    print(f"PEP 668 mark  {'present' if marker.exists() else 'absent'} on the base interpreter")
    return 0


def compare(args: argparse.Namespace) -> int:
    """Compare two PEP 440 versions and print the ordering."""
    try:
        a, b = Version(args.a), Version(args.b)
    except InvalidVersion as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    sign = "<" if a < b else (">" if a > b else "==")
    print(f"{a} {sign} {b}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="devenv", description="Tiny developer helper.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="show which Python runs this tool").set_defaults(func=doctor)
    cmp_parser = sub.add_parser("compare", help="compare two PEP 440 versions")
    cmp_parser.add_argument("a")
    cmp_parser.add_argument("b")
    cmp_parser.set_defaults(func=compare)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
