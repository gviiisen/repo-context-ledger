#!/usr/bin/env python3
"""Measure cold and warm Context Bundle routing on a synthetic repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(args)}\n{result.stderr.strip()}"
        )
    return result


def ledger(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run(sys.executable, str(LEDGER), "--repo", str(repo), *args)


def pack_text(index: int, source_path: str, digest: str) -> str:
    feature = f"synthetic-route-{index:03d}"
    return f"""# Synthetic Route {index:03d} context pack

Status: current
Feature: {feature}
Quality profile: evidence-v1
Language: en
Detail: concise
Source commit: synthetic
Base branch: main
Base commit: synthetic
Last refreshed: 2026-01-01T00:00:00+00:00

## Purpose

Routes synthetic benchmark request marker-{index:03d} without using production data.

## Load order

- Read first: `{source_path}`.
- Read if needed: none.
- Do not load by default: every unrelated synthetic route.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `{source_path}` | Synthetic routing target {index:03d}. |

## Contracts and boundaries

- Invariants and contracts: only synthetic files are used.
- Failure / recovery: rebuild the temporary fixture.
- Non-goals: production behavior and production measurements.

## Verification

Run this benchmark and inspect its aggregate JSON result.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- None.
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `{source_path}` — `sha256:{digest}`
<!-- repo-context-ledger:pack-files:end -->
"""


def measured_bundle(repo: Path, query: str) -> tuple[dict, float]:
    started = time.perf_counter()
    result = ledger(repo, "context", "--query", query, "--tool", "benchmark", "--format", "json")
    wall_ms = (time.perf_counter() - started) * 1000
    return json.loads(result.stdout), wall_ms


def benchmark(pack_count: int) -> dict[str, object]:
    if pack_count < 2:
        raise ValueError("pack_count must be at least 2")
    with tempfile.TemporaryDirectory(prefix="repo-context-ledger-synthetic-") as raw:
        repo = Path(raw) / "repository"
        repo.mkdir()
        run("git", "init", "-b", "main", cwd=repo)
        run("git", "config", "user.name", "Synthetic Benchmark", cwd=repo)
        run("git", "config", "user.email", "benchmark@example.test", cwd=repo)
        ledger(repo, "init")
        packs_root = repo / "docs" / "ai" / "context-packs"
        sources_root = repo / "src" / "synthetic"
        packs_root.mkdir(parents=True, exist_ok=True)
        sources_root.mkdir(parents=True, exist_ok=True)
        for index in range(pack_count):
            source_rel = f"src/synthetic/route_{index:03d}.py"
            source = repo / source_rel
            content = f"ROUTE_MARKER = 'marker-{index:03d}'\n".encode("utf-8")
            source.write_bytes(content)
            digest = hashlib.sha256(content).hexdigest()
            (packs_root / f"synthetic-route-{index:03d}.md").write_text(
                pack_text(index, source_rel, digest),
                encoding="utf-8",
            )
        run("git", "add", "-A", cwd=repo)
        run("git", "commit", "-m", "Create synthetic routing fixture", cwd=repo)

        target = pack_count // 2
        started = ledger(
            repo,
            "start",
            "--title",
            f"Continue synthetic marker {target:03d}",
            "--feature",
            f"synthetic-route-{target:03d}",
            "--tool",
            "benchmark",
        )
        session = next(
            line.removeprefix("Session: ").strip()
            for line in started.stdout.splitlines()
            if line.startswith("Session: ")
        )
        ledger(
            repo,
            "checkpoint",
            "--session",
            session,
            "--summary",
            "Synthetic checkpoint used only to measure bounded Capsule generation.",
            "--next",
            "Read the selected synthetic Pack and verify its single fake source file.",
        )

        query = f"continue synthetic marker {target:03d}"
        cold, cold_wall_ms = measured_bundle(repo, query)
        warm, warm_wall_ms = measured_bundle(repo, query)
        expected_pack = f"docs/ai/context-packs/synthetic-route-{target:03d}.md"
        if cold["primary_pack"] != expected_pack or warm["primary_pack"] != expected_pack:
            raise AssertionError("cold and warm routes must select the same synthetic Pack")
        if cold["required_reads"] != warm["required_reads"]:
            raise AssertionError("cold and warm Required reads must be identical")
        if len(warm["required_reads"]) != 1:
            raise AssertionError("the synthetic Bundle must require exactly one initial file")
        serialized = json.dumps(warm, ensure_ascii=False, sort_keys=True)
        if str(repo) in serialized:
            raise AssertionError("Context Bundle exposed the temporary absolute repository root")
        capsule = warm.get("resume", {}).get("capsule") or {}
        capsule_characters = len(json.dumps(capsule, ensure_ascii=False, sort_keys=True))
        return {
            "fixture": "synthetic",
            "packs": pack_count,
            "schema": warm["schema"],
            "primary_pack_correct": True,
            "required_reads": len(warm["required_reads"]),
            "capsule_characters": capsule_characters,
            "cold_wall_ms": round(cold_wall_ms, 3),
            "warm_wall_ms": round(warm_wall_ms, 3),
            "cold_router_ms": cold["metrics"]["elapsed_ms"],
            "warm_router_ms": warm["metrics"]["elapsed_ms"],
            "warm_speedup": round(cold_wall_ms / max(warm_wall_ms, 0.001), 2),
            "warm_cache_state": warm["metrics"]["cache"]["state"],
            "packs_considered": warm["metrics"]["packs_considered"],
            "absolute_roots_exposed": False,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packs", type=int, default=59)
    args = parser.parse_args()
    print(json.dumps(benchmark(args.packs), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
