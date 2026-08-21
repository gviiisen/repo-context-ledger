#!/usr/bin/env python3
"""Deterministically build the zero-dependency standalone Ledger runtime."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "src" / "repo_context_ledger" / "runtime.py.tmpl"
CONTRACTS = ROOT / "src" / "repo_context_ledger" / "contracts.pyfrag"
MARKER = "# @repo-context-ledger:contracts@"
DEFAULT_OUTPUTS = (
    ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py",
    ROOT / ".context-ledger" / "ledger.py",
)


def normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")


def render_runtime() -> bytes:
    template = normalized_text(TEMPLATE)
    if template.count(MARKER) != 1:
        raise ValueError(f"runtime template must contain exactly one {MARKER!r} marker")
    contracts = normalized_text(CONTRACTS).rstrip()
    return template.replace(MARKER, contracts).rstrip().encode("utf-8") + b"\n"


def write_atomic(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(raw_temp)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when an output differs; never write")
    parser.add_argument("--output", action="append", default=[], help="Output path; repeat as needed")
    args = parser.parse_args(argv)
    outputs = tuple(Path(raw).resolve() for raw in args.output) or DEFAULT_OUTPUTS
    try:
        content = render_runtime()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: cannot build standalone runtime: {exc}", file=sys.stderr)
        return 2
    stale = [path for path in outputs if not path.is_file() or path.read_bytes() != content]
    if args.check:
        if stale:
            for path in stale:
                try:
                    label = path.relative_to(ROOT).as_posix()
                except ValueError:
                    label = str(path)
                print(f"ERROR: standalone runtime output drift: {label}", file=sys.stderr)
            return 2
        print("Standalone runtime outputs are current.")
        return 0
    for path in outputs:
        write_atomic(path, content)
        try:
            label = path.relative_to(ROOT).as_posix()
        except ValueError:
            label = str(path)
        print(f"Built {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
