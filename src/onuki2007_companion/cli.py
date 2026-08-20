"""CLI for running existing companion verification scripts by stable check ID."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from .checks import CHECKS, Check, by_id


def repository_root() -> Path:
    """Locate the installed editable source tree without a machine-local path."""

    root = Path(__file__).resolve().parents[2]
    if not root.joinpath("scripts", "python").is_dir():
        raise RuntimeError("the CLI requires the companion source tree; install it with pip -e .")
    return root


def run(check: Check) -> int:
    """Run one unchanged script with the interpreter used for this CLI."""

    return subprocess.run([sys.executable, check.script], cwd=repository_root(), check=False).returncode


def render(check: Check) -> str:
    """Render compact deterministic metadata suitable for terminals and tests."""

    kind = "dimensional" if check.dimensional else "symbolic_or_structural"
    availability = "public" if check.public else "canonical_only"
    return f"{check.check_id}\t{check.topic}\t{kind}\t{availability}\t{check.script}\t{check.scope}"


def parser() -> argparse.ArgumentParser:
    """Create the public command parser."""

    command = argparse.ArgumentParser(description=__doc__)
    sub = command.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list public check IDs")
    run_parser = sub.add_parser("run", help="run one check by ID")
    run_parser.add_argument("check_id")
    topic_parser = sub.add_parser("topic", help="run every check for one topic")
    topic_parser.add_argument("topic")
    sub.add_parser("python-all", help="run all public Python/SymPy/Pint scripts")
    sub.add_parser("dimensions", help="run dimensional checks only")
    show_parser = sub.add_parser("show", help="show script, scope, and topic for one check")
    show_parser.add_argument("check_id")
    return command


def run_many(checks: tuple[Check, ...]) -> int:
    """Run checks in manifest order and stop at the first nonzero exit."""

    for check in checks:
        print(f"RUN\t{render(check)}")
        if (code := run(check)):
            return code
    return 0


def main(argv: list[str] | None = None) -> int:
    """Dispatch a reader-requested route without changing the underlying algebra."""

    args = parser().parse_args(argv)
    if args.command == "list":
        print("check_id\ttopic\tkind\tavailability\tscript\tscope")
        for check in CHECKS:
            print(render(check))
        return 0
    if args.command == "show":
        print(render(by_id(args.check_id)))
        return 0
    if args.command == "run":
        return run(by_id(args.check_id))
    if args.command == "topic":
        selected = tuple(check for check in CHECKS if check.topic == args.topic)
        if not selected:
            parser().error(f"unknown topic: {args.topic}")
        return run_many(selected)
    if args.command == "dimensions":
        return run_many(tuple(check for check in CHECKS if check.dimensional))
    return run_many(tuple(check for check in CHECKS if check.public))


if __name__ == "__main__":
    raise SystemExit(main())
