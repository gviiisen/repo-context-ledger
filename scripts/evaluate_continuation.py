#!/usr/bin/env python3
"""Evaluate private task continuation and Resume Capsule quality on synthetic data."""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
DEFAULT_CORPUS = ROOT / "tests" / "fixtures" / "continuation-eval-v1.json"


def load_runtime():
    spec = importlib.util.spec_from_file_location("repo_context_ledger_continuation_runtime", RUNTIME_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generated runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_pack(raw: dict[str, object]) -> dict[str, object]:
    feature = str(raw["feature"])
    return {
        **raw,
        "rel": f"docs/ai/context-packs/{feature}.md",
        "status": "current",
        "superseded_by": "",
        "fingerprints_ok": True,
        "characters": 1000,
    }


def synthetic_view(raw: dict[str, object], base_commit: str = "none") -> dict[str, object]:
    evidence = [str(item) for item in raw.get("evidence", [])]
    return {
        "session_id": str(raw["id"]),
        "title": str(raw.get("title", "Synthetic continuation task")),
        "feature": str(raw["feature"]),
        "status": "paused",
        "updated_at": "2026-01-01T00:00:00+00:00",
        "checkpointed": "2026-01-01T00:00:00+00:00",
        "summary": str(raw.get("summary", "")),
        "next_step": str(raw.get("next", "")),
        "base_commit": base_commit,
        "branch": "main",
        "evidence_paths": evidence,
        "source_evidence_count": len(evidence),
        "verification": "unit verification passed",
        "resume_epoch": 1,
        "continuation_tool": "codex",
        "access": str(raw.get("access", "owner")),
    }


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


def build_case_capsule(runtime, raw_view: dict[str, object], pack: dict[str, object]) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as raw:
        repo = Path(raw) / "repo"
        repo.mkdir()
        run_git(repo, "init", "-b", "main")
        run_git(repo, "config", "user.name", "Synthetic Evaluator")
        run_git(repo, "config", "user.email", "evaluator@example.test")
        paths = list(dict.fromkeys([
            *[str(item) for item in pack.get("tracked", [])],
            *[str(item) for item in raw_view.get("evidence", [])],
        ]))
        for raw_path in paths:
            target = repo / raw_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("BASE = 1\n", encoding="utf-8")
        run_git(repo, "add", "-A")
        run_git(repo, "commit", "-m", "Create synthetic continuation fixture")
        base_commit = run_git(repo, "rev-parse", "HEAD")
        for raw_path in raw_view.get("evidence", []):
            target = repo / str(raw_path)
            target.write_text(target.read_text(encoding="utf-8") + "DIRTY = 1\n", encoding="utf-8")
        return runtime.build_resume_capsule(repo, synthetic_view(raw_view, base_commit), pack)


def evaluate(corpus_path: Path) -> dict[str, object]:
    runtime = load_runtime()
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    if corpus.get("schema") != "continuation-eval-v1":
        raise ValueError("unsupported continuation corpus schema")
    packs = {str(raw["feature"]): synthetic_pack(raw) for raw in corpus.get("packs", [])}
    started = time.perf_counter()
    top1_cases = top1_correct = ambiguity_count = foreign_overlap_count = 0
    privacy_violations = capsule_budget_violations = anchor_failures = expectation_failures = 0
    results: list[dict[str, object]] = []
    for case in corpus.get("cases", []):
        query = str(case["query"])
        tokens = runtime.resume_query_tokens(query)
        ranked: list[tuple[int, dict[str, object], list[str], dict[str, object] | None]] = []
        foreign_overlap = False
        for raw_session in case.get("sessions", []):
            feature = str(raw_session["feature"])
            pack = packs.get(feature)
            if raw_session.get("access") == "foreign":
                foreign_overlap = foreign_overlap or runtime.foreign_session_query_match(
                    {"feature": feature}, query, tokens, pack
                )
                continue
            view = synthetic_view(raw_session)
            score, reasons = runtime.score_resume_session(view, query, tokens, pack)
            if score > 0:
                ranked.append((score, raw_session, reasons, pack))
        ranked.sort(key=lambda item: (-item[0], str(item[1]["id"])))
        near = [] if not ranked else [
            item for item in ranked
            if item[0] >= int(ranked[0][0] * runtime.RESUME_NEAR_SCORE_RATIO)
        ]
        blocked = len(near) > 1
        selected = None if not ranked or blocked else ranked[0]
        selected_id = "" if selected is None else str(selected[1]["id"])
        mode = "blocked" if blocked else "guided" if selected is None and foreign_overlap else "none" if selected is None else "ready"
        capsule = None
        if selected is not None and selected[3] is not None:
            capsule = build_case_capsule(runtime, selected[1], selected[3])
            mode = str(capsule["mode"])
            capsule_budget_violations += int(
                int(capsule["budget"]["used_characters"]) > int(capsule["budget"]["max_characters"])
            )
        expected_session = case.get("expected_session")
        if expected_session is not None:
            top1_cases += 1
            top1_correct += int(selected_id == expected_session)
        expected_anchor = str(case.get("expected_anchor", ""))
        anchor_ok = not expected_anchor or (
            capsule is not None and expected_anchor in capsule.get("code_anchors", [])
        )
        anchor_failures += int(not anchor_ok)
        private_marker = str(case.get("private_marker", ""))
        public_projection = json.dumps({
            "selected_session": selected_id,
            "mode": mode,
            "foreign_overlap": foreign_overlap,
            "capsule": capsule,
        }, ensure_ascii=False)
        privacy_ok = not private_marker or private_marker not in public_projection
        privacy_violations += int(not privacy_ok)
        expected_ok = (
            selected_id == (expected_session or "")
            and mode == case.get("expected_mode")
            and foreign_overlap == bool(case.get("expected_foreign_overlap", False))
            and anchor_ok
            and privacy_ok
        )
        expectation_failures += int(not expected_ok)
        ambiguity_count += int(blocked)
        foreign_overlap_count += int(foreign_overlap)
        results.append({
            "name": case.get("name", "unnamed"),
            "selected_session": selected_id,
            "mode": mode,
            "foreign_overlap": foreign_overlap,
            "capsule_schema": "" if capsule is None else capsule.get("schema", ""),
            "capsule_characters": 0 if capsule is None else capsule["budget"]["used_characters"],
            "anchor_ok": anchor_ok,
            "privacy_ok": privacy_ok,
            "expected_ok": expected_ok,
        })
    return {
        "schema": "continuation-eval-report-v1",
        "corpus_schema": corpus["schema"],
        "case_count": len(results),
        "top1_cases": top1_cases,
        "top1_correct": top1_correct,
        "ambiguity_count": ambiguity_count,
        "foreign_overlap_count": foreign_overlap_count,
        "privacy_violations": privacy_violations,
        "capsule_budget_violations": capsule_budget_violations,
        "anchor_failures": anchor_failures,
        "expectation_failures": expectation_failures,
        "latency_ms": round((time.perf_counter() - started) * 1000, 3),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--format", choices=("json",), default="json")
    args = parser.parse_args()
    print(json.dumps(evaluate(args.corpus.resolve()), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
