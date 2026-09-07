#!/usr/bin/env python3
"""Measure mechanics and authoring fields, not AI thinking time or token cost."""

import argparse
import json
import statistics
import sys
import tempfile
import time
from pathlib import Path

import closeout_workflow_benchmark as fixture


def trial(root: Path, workflow: str) -> dict:
    repo, session = fixture.create_fixture(root, workflow, branch="fix/fixture")
    draft = fixture.private_draft(repo, session)
    raw_template = fixture.RUNTIME.template_source("handoff-template.md", repo).read_text(encoding="utf-8")
    if workflow == "small-fix":
        raw_template = fixture.RUNTIME.small_fix_draft(raw_template)
    start = time.perf_counter()
    fixture.ledger(repo, "verify", "--session", session, "--", sys.executable, "-B", "-c",
                   "from src.service import VALUE; assert VALUE == 2; print('fixture value verified')")
    fixture.refresh_record_inputs(repo, session, explicit_evidence=workflow == "ordinary-change")
    fixture.finish(repo, session)
    elapsed = (time.perf_counter() - start) * 1000
    published = list((repo / "docs/changes").glob("*/*/*-*.md"))
    assert len(published) == 1 and not draft.exists(), "Expected one publication and no draft"
    text = published[0].read_text(encoding="utf-8")
    errors = fixture.RUNTIME.handoff_validation_errors(
        text, repo, fixture.RUNTIME.load_config(repo), expected_status="completed"
    )
    assert not errors, errors
    return {
        "authoring_prompts": raw_template.count("TODO:"),
        "draft_template_lines": len(raw_template.splitlines()),
        "published_record_lines": len(text.splitlines()),
        "closeout_commands": 4 if workflow == "ordinary-change" else 3,
        "closeout_ms": round(elapsed, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args()
    if not 1 <= args.iterations <= 20:
        parser.error("--iterations must be between 1 and 20")
    result = {}
    for workflow in ("ordinary-change", "small-fix"):
        trials = []
        for _ in range(args.iterations):
            with tempfile.TemporaryDirectory(prefix="ledger-authoring-") as raw:
                trials.append(trial(Path(raw), workflow))
        result[workflow] = {
            "trials": trials,
            "median_closeout_ms": round(statistics.median(item["closeout_ms"] for item in trials), 2),
        }
    print(json.dumps({
        "schema": "synthetic-small-fix-authoring-v1",
        "scope": "Temporary fixtures only; excludes setup, AI/code investigation and document composition time.",
        "workflows": result,
    }, indent=2))


if __name__ == "__main__":
    main()
