#!/usr/bin/env python3
"""Compare serial and overlapped Repo Context Ledger closeout workflows."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
FEATURE = "synthetic-closeout"
TIMINGS_PREFIX = "repo-context-ledger-timings: "


def run(*args: str, cwd: Path | None = None, expected: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != expected:
        raise RuntimeError(
            f"command returned {result.returncode}, expected {expected}: {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def ledger(
    repo: Path,
    *args: str,
    expected: int = 0,
    timings: bool = False,
) -> subprocess.CompletedProcess[str]:
    timing_args = ["--timings"] if timings else []
    return run(
        sys.executable,
        str(LEDGER),
        *timing_args,
        "--repo",
        str(repo),
        *args,
        expected=expected,
    )


def timing_report(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    for line in reversed(result.stderr.splitlines()):
        if line.startswith(TIMINGS_PREFIX):
            return json.loads(line.removeprefix(TIMINGS_PREFIX))
    raise RuntimeError(f"command did not emit private timings: {result.stderr}")


def load_runtime():
    spec = importlib.util.spec_from_file_location("closeout_benchmark_runtime", LEDGER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import runtime: {LEDGER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RUNTIME = load_runtime()


def session_id(result: subprocess.CompletedProcess[str]) -> str:
    for line in result.stdout.splitlines():
        if line.startswith("Session: "):
            return line.removeprefix("Session: ").strip()
    raise RuntimeError(f"start output did not contain a session ID: {result.stdout}")


def private_draft(repo: Path, session: str) -> Path:
    record = RUNTIME.load_context_state(repo)["task_sessions"][session]
    return RUNTIME.resolve_session_draft(repo, RUNTIME.load_config(repo), session, record)


def fill_pack(path: Path) -> None:
    text = path.read_text(encoding="utf-8").replace("Language: auto", "Language: en")
    replacements = [
        "Routes a synthetic closeout task without using production repository data.",
        "Read `src/service.py` first.",
        "Read the completed synthetic change only when benchmark history is required.",
        "Do not load unrelated files for this isolated benchmark.",
        "src/service.py",
        "Provides the synthetic implementation path used by the benchmark.",
        "The fake service value changes only inside the temporary repository.",
        "A failed benchmark preserves the temporary private draft for process-local diagnosis.",
        "Production behavior, network access, and external repositories are out of scope.",
        "Run `python -B benchmarks/closeout_workflow_benchmark.py` to verify closeout scheduling and publication.",
    ]
    for replacement in replacements:
        text = re.sub(r"TODO:[^|`\r\n]*", replacement, text, count=1)
    path.write_text(text, encoding="utf-8")


def fill_handoff(path: Path) -> None:
    text = path.read_text(encoding="utf-8").replace("Language: auto", "Language: en")
    replacements = [
        "Measure a complete synthetic small-fix closeout without production data.",
        "The synthetic service returned its original fixture value before this task.",
        "The synthetic service now returns the updated fixture value and publishes one record.",
        "src/service.py",
        "Owns the only synthetic behavior changed by this benchmark.",
        "Updates the fixture value without changing unrelated generated integration files.",
        "Session isolation, verification evidence, and atomic publication remain unchanged.",
        "A failed check leaves the private draft available and the temporary repository is discarded.",
        "Production behavior, external services, and real repository documentation are not changed.",
        "`docs/ai/context-packs/synthetic-closeout.md`",
        "The synthetic Pack is refreshed from the changed fixture before finish.",
        "None.",
    ]
    for replacement in replacements:
        text = re.sub(r"TODO:[^|`\r\n]*", replacement, text, count=1)
    path.write_text(text, encoding="utf-8")


def create_fixture(root: Path) -> tuple[Path, str]:
    repo = root / "repository"
    repo.mkdir()
    run("git", "init", "-b", "main", cwd=repo)
    run("git", "config", "user.name", "Synthetic Benchmark", cwd=repo)
    run("git", "config", "user.email", "benchmark@example.test", cwd=repo)
    source = repo / "src" / "service.py"
    source.parent.mkdir(parents=True)
    source.write_text("VALUE = 1\n", encoding="utf-8")
    ledger(repo, "init")
    created = ledger(
        repo,
        "pack",
        "--feature",
        FEATURE,
        "--title",
        "Synthetic closeout",
        "--file",
        "src/service.py",
        "--language",
        "en",
    )
    pack = repo / created.stdout.splitlines()[0]
    fill_pack(pack)
    run("git", "add", "-A", cwd=repo)
    run("git", "commit", "-m", "Create synthetic closeout fixture", cwd=repo)

    started = ledger(
        repo,
        "start",
        "--title",
        "Benchmark synthetic closeout",
        "--feature",
        FEATURE,
        "--tool",
        "benchmark",
        "--language",
        "en",
    )
    session = session_id(started)
    fill_handoff(private_draft(repo, session))
    source.write_text("VALUE = 2\n", encoding="utf-8")
    return repo, session


def verification_command(repo: Path, session: str, delay: float) -> list[str]:
    return [
        sys.executable,
        str(LEDGER),
        "--repo",
        str(repo),
        "verify",
        "--timeout",
        "30",
        "--session",
        session,
        "--",
        sys.executable,
        "-c",
        f"import time; time.sleep({delay!r}); print('synthetic verification passed')",
    ]


def refresh_record_inputs(repo: Path, session: str, explicit_evidence: bool) -> None:
    ledger(repo, "pack", "--feature", FEATURE, "--file", "src/service.py")
    if explicit_evidence:
        ledger(
            repo,
            "evidence",
            "--session",
            session,
            "--path",
            "src/service.py",
            "--path",
            "docs/ai/context-packs/synthetic-closeout.md",
        )


def finish(repo: Path, session: str) -> dict[str, object]:
    result = ledger(
        repo,
        "finish",
        "--session",
        session,
        "--no-spec",
        "--reason",
        "The isolated synthetic fixture has no durable product contract to maintain.",
        timings=True,
    )
    return timing_report(result)


def serial_trial(root: Path, delay: float) -> dict[str, float]:
    repo, session = create_fixture(root)
    started = time.perf_counter()
    verification_started = time.perf_counter()
    for _ in range(2):
        result = subprocess.run(
            verification_command(repo, session, delay),
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode != 0:
            raise RuntimeError(result.stdout + result.stderr)
    verification_ms = (time.perf_counter() - verification_started) * 1000
    preparation_started = time.perf_counter()
    refresh_record_inputs(repo, session, explicit_evidence=True)
    preparation_ms = (time.perf_counter() - preparation_started) * 1000
    finish_started = time.perf_counter()
    finish_timings = finish(repo, session)
    finish_ms = (time.perf_counter() - finish_started) * 1000
    finish_stages = finish_timings["stages"]
    assert isinstance(finish_stages, dict)
    return {
        "total_ms": (time.perf_counter() - started) * 1000,
        "verification_ms": verification_ms,
        "preparation_ms": preparation_ms,
        "finish_ms": finish_ms,
        "finish_lock_hold_ms": float(finish_stages.get("lock_hold_ms", 0.0)),
        "finish_lock_wait_ms": float(finish_stages.get("lock_wait_ms", 0.0)),
        "finish_derived_sync_ms": float(finish_stages.get("derived_sync_ms", 0.0)),
        "finish_validation_ms": float(finish_stages.get("validation_ms", 0.0)),
        "finish_evidence_ms": float(finish_stages.get("evidence_ms", 0.0)),
        "finish_publish_ms": float(finish_stages.get("publish_ms", 0.0)),
    }


def overlapped_trial(root: Path, delay: float, stagger: float) -> dict[str, float]:
    repo, session = create_fixture(root)
    started = time.perf_counter()
    processes = []
    for index in range(2):
        processes.append(
            subprocess.Popen(
                verification_command(repo, session, delay),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf-8",
                errors="replace",
            )
        )
        if index == 0 and stagger:
            time.sleep(stagger)
    preparation_started = time.perf_counter()
    refresh_record_inputs(repo, session, explicit_evidence=False)
    preparation_ms = (time.perf_counter() - preparation_started) * 1000
    for process in processes:
        stdout, stderr = process.communicate(timeout=30)
        if process.returncode != 0:
            raise RuntimeError(stdout + stderr)
    barrier_ms = (time.perf_counter() - started) * 1000
    finish_started = time.perf_counter()
    finish_timings = finish(repo, session)
    finish_ms = (time.perf_counter() - finish_started) * 1000
    finish_stages = finish_timings["stages"]
    assert isinstance(finish_stages, dict)
    return {
        "total_ms": (time.perf_counter() - started) * 1000,
        "verification_barrier_ms": barrier_ms,
        "preparation_ms": preparation_ms,
        "finish_ms": finish_ms,
        "finish_lock_hold_ms": float(finish_stages.get("lock_hold_ms", 0.0)),
        "finish_lock_wait_ms": float(finish_stages.get("lock_wait_ms", 0.0)),
        "finish_derived_sync_ms": float(finish_stages.get("derived_sync_ms", 0.0)),
        "finish_validation_ms": float(finish_stages.get("validation_ms", 0.0)),
        "finish_evidence_ms": float(finish_stages.get("evidence_ms", 0.0)),
        "finish_publish_ms": float(finish_stages.get("publish_ms", 0.0)),
    }


def collision_trial(root: Path, delay: float) -> dict[str, object]:
    repo, session = create_fixture(root)
    processes = [
        subprocess.Popen(
            verification_command(repo, session, delay),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
        )
        for _ in range(2)
    ]
    results = []
    for process in processes:
        stdout, stderr = process.communicate(timeout=30)
        results.append({"exit_code": process.returncode, "lock_error": "write is active" in stderr})
    return {"passed": sum(item["exit_code"] == 0 for item in results), "results": results}


def aggregate(trials: list[dict[str, float]]) -> dict[str, float]:
    keys = sorted(trials[0])
    return {
        f"{key}_median": round(statistics.median(trial[key] for trial in trials), 3)
        for key in keys
    }


def benchmark(iterations: int, delay: float, stagger: float) -> dict[str, object]:
    serial: list[dict[str, float]] = []
    overlapped: list[dict[str, float]] = []
    for _ in range(iterations):
        with tempfile.TemporaryDirectory(prefix="ledger-closeout-serial-") as raw:
            serial.append(serial_trial(Path(raw), delay))
        with tempfile.TemporaryDirectory(prefix="ledger-closeout-overlap-") as raw:
            overlapped.append(overlapped_trial(Path(raw), delay, stagger))
    with tempfile.TemporaryDirectory(prefix="ledger-closeout-collision-") as raw:
        collision = collision_trial(Path(raw), delay)
    serial_summary = aggregate(serial)
    overlapped_summary = aggregate(overlapped)
    serial_total = serial_summary["total_ms_median"]
    overlapped_total = overlapped_summary["total_ms_median"]
    return {
        "schema": "closeout-benchmark-v1",
        "fixture": "synthetic",
        "iterations": iterations,
        "verification_delay_seconds": delay,
        "serial": serial_summary,
        "overlapped": overlapped_summary,
        "total_speedup": round(serial_total / max(overlapped_total, 0.001), 2),
        "median_time_saved_ms": round(serial_total - overlapped_total, 3),
        "zero_stagger_parallel_verify": collision,
        "production_data_used": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--verification-delay", type=float, default=0.6)
    parser.add_argument("--stagger", type=float, default=0.08)
    args = parser.parse_args()
    if args.iterations < 1 or args.verification_delay < 0 or args.stagger < 0:
        parser.error("iterations must be positive and timing values cannot be negative")
    print(json.dumps(benchmark(args.iterations, args.verification_delay, args.stagger), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
