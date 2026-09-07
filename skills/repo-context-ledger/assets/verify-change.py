#!/usr/bin/env python3
"""Optional project-owned acceptance script: configure existing checks before use.

Copy only when several checks share one acceptance goal; prefer existing project scripts.
Run once through ledger.py verify (or an existing preset). This is not a deployment runner.
Use sys.executable for Python and direct argument arrays for Go/Rust/PowerShell -File.
Keep authorization boundaries and pre/post-deployment checks in their original phases.
"""

from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]  # For a copy in <project>/scripts/.
CHECKS = []  # (short-name, [executable, argument, ...]); empty configuration fails closed.
TIMEOUT_SECONDS = 300


def run_checks(checks, root, timeout=TIMEOUT_SECONDS):
    if not checks or not 1 <= len(checks) <= 16:
        raise ValueError("Configure 1-16 named acceptance checks, not deployment operations.")
    seen = set()
    for name, argv in checks:
        if (not isinstance(name, str) or not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", name)
                or name in seen or not isinstance(argv, list) or not argv
                or any(not isinstance(arg, str) or not arg for arg in argv)):
            raise ValueError("Checks need unique short names and nonempty direct argv arrays.")
        seen.add(name)
    for index, (name, argv) in enumerate(checks):
        try:
            result = subprocess.run(argv, cwd=root, shell=False, timeout=timeout)
            code = result.returncode
        except subprocess.TimeoutExpired:
            print(f"ERROR: {name} timed out", file=sys.stderr)
            code = 124
        except OSError:
            print(f"ERROR: {name} could not start", file=sys.stderr)
            code = 127
        print(f"ledger-step: {name} {'passed' if code == 0 else 'failed'}", flush=True)
        if code:
            for pending, _ in checks[index + 1:]:
                print(f"ledger-step: {pending} not-run", flush=True)
            return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run_checks(CHECKS, ROOT))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
