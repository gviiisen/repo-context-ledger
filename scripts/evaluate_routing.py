#!/usr/bin/env python3
"""Evaluate the deterministic Context Pack router against a synthetic labeled corpus."""

from __future__ import annotations

import argparse
import importlib.util
import json
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "skills" / "repo-context-ledger" / "scripts" / "ledger.py"
DEFAULT_CORPUS = ROOT / "tests" / "fixtures" / "routing-eval-v1.json"


def load_runtime():
    spec = importlib.util.spec_from_file_location("repo_context_ledger_routing_runtime", RUNTIME_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load generated runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(corpus_path: Path) -> dict[str, object]:
    runtime = load_runtime()
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    if corpus.get("schema") != "routing-eval-v1":
        raise ValueError("unsupported routing corpus schema")
    started = time.perf_counter()
    top1_cases = top1_correct = ambiguity_count = fallback_count = expectation_failures = 0
    stale_selection_count = superseded_selection_count = required_read_characters = 0
    results = []
    for case in corpus.get("cases", []):
        query = str(case["query"])
        tokens = runtime.query_tokens(query)
        packs = []
        for raw in case.get("candidates", []):
            pack_text = (
                f"# {raw['title']} context pack\n\n"
                f"Status: {raw.get('status', 'current')}\nFeature: {raw['feature']}\n\n"
                f"## Purpose\n\n{raw['purpose']}\n\n"
                + "\n".join(f"- `{path}`" for path in raw.get("tracked", []))
                + "\n"
            )
            candidate = {
                **raw,
                "rel": f"docs/ai/context-packs/{raw['feature']}.md",
                "status": raw.get("status", "current"),
                "superseded_by": raw.get("superseded_by", ""),
                "fingerprints_ok": raw.get("fingerprints_ok", True),
                "specs": [],
                "characters": len(pack_text),
            }
            if runtime.routable_context_pack(candidate):
                packs.append(candidate)
        candidates, candidate_metrics = runtime.candidate_context_packs(
            packs, query, tokens, "", set()
        )
        ranked = runtime.rank_context_pack_candidates(candidates, query, tokens)
        ambiguous = len(ranked) > 1 and ranked[0][0] == ranked[1][0]
        selected = None if not ranked else ranked[0][1]
        fallback = selected is None
        ambiguity_count += int(ambiguous)
        fallback_count += int(fallback)
        selected_feature = "" if selected is None else str(selected["feature"])
        if case.get("expected_feature") is not None:
            top1_cases += 1
            top1_correct += int(selected_feature == case["expected_feature"])
        if selected is not None:
            required_read_characters += int(selected.get("characters", 0))
            stale_selection_count += int(not bool(selected.get("fingerprints_ok", True)))
            superseded_selection_count += int(selected.get("status") == "superseded")
        expected_ok = (
            (case.get("expected_feature") is None or selected_feature == case["expected_feature"])
            and ambiguous == bool(case.get("expected_ambiguous", False))
            and fallback == bool(case.get("expected_fallback", False))
            and (selected is None or (not bool(selected.get("fingerprints_ok", True))) == bool(case.get("expected_stale", False)))
        )
        expectation_failures += int(not expected_ok)
        results.append({
            "name": case.get("name", "unnamed"),
            "selected_feature": selected_feature,
            "ambiguous": ambiguous,
            "fallback": fallback,
            "candidate_fallback": bool(candidate_metrics["fallback"]),
            "expected_ok": expected_ok,
        })
    return {
        "schema": "routing-eval-report-v1", "corpus_schema": corpus["schema"], "case_count": len(results),
        "top1_cases": top1_cases, "top1_correct": top1_correct, "ambiguity_count": ambiguity_count,
        "fallback_count": fallback_count, "stale_selection_count": stale_selection_count,
        "superseded_selection_count": superseded_selection_count,
        "expectation_failures": expectation_failures,
        "required_read_characters": required_read_characters,
        "latency_ms": round((time.perf_counter() - started) * 1000, 3), "results": results,
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
