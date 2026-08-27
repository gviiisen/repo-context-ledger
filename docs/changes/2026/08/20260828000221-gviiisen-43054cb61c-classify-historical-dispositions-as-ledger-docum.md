# Classify historical dispositions as Ledger documentation

Status: completed
Feature: coverage-integrity
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260828000221-gviiisen-43054cb61c
Session ID: 20260828000221-gviiisen-43054cb61c
Actor: gviiisen
Branch: fix/v1.0.2-ledger-policy-audit
Started: 2026-08-28T00:02:21+08:00
Completed: 2026-08-28T00:03:40+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/coverage-integrity.md
Spec exception: none

## Intent

Correct the self-hosted PR policy so append-only historical disposition JSON is treated as Ledger documentation rather than production implementation. Acceptance requires the focused policy/audit suite and deterministic runtime build to pass, followed by the real aggregate policy.

## Changed behavior

Before: The default `implementation_globs: ["**"]` classified `docs/audit-dispositions/*.json` as behavior-changing code because the new documentation root was not part of the docs classifier.

After: Coverage derives the disposition directory from the configured Changes parent and classifies its JSON records as docs, so they remain audited without requiring an unrelated Context Pack code mapping.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::coverage_path_kind` | Classifies Git paths for Coverage. | Added the sibling `audit-dispositions/` root to deterministic Ledger documentation paths. |
| `tests/test_policy_and_audit.py::test_historical_dispositions_are_ledger_docs_not_implementation` | Protects the self-hosted policy boundary. | Added a regression assertion using an initialized repository configuration. |

## Boundaries and risks

- Invariant: Disposition contents still pass the strict historical audit; docs classification only prevents them from masquerading as production implementation.
- Failure / recovery: A custom Changes path still resolves the sibling disposition directory deterministically; malformed disposition JSON continues to fail audit and strict check.
- Not changed: Production, test, CI, config, generated, Pack/spec/Change, and managed README classifications are unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_policy_and_audit.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 10.00s
  - Recorded: 2026-08-28T00:03:00+08:00
  - Output evidence: sha256:e2cb095090800231e4572fc8ee5f14dd25c6d1f7cbf3cc097767334a229e57a3 (925 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-28T00:03:00+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `docs/specs/coverage-integrity.md` and the refreshed Coverage/runtime Context Packs.

Reason: The stable Coverage contract now explicitly identifies historical dispositions as Ledger documentation.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `68c3b0cb9de9d1f975f847046d9db2b883fef00f`
- Current commit: `68c3b0cb9de9d1f975f847046d9db2b883fef00f`
- Changed paths:
  - `.github/workflows/test.yml`
  - `COMPATIBILITY.md`
  - `MIGRATIONS.md`
  - `docs/ai/context-packs/compact-local-config-workflow.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/continuation-quality.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/ai/context-packs/verification-presets.md`
  - `docs/ai/context-packs/workflow-planning.md`
  - `docs/audit-dispositions/20260822003651-final-verification-failed.json`
  - `docs/changes/2026/08/20260827233705-gviiisen-a9641a2f72-add-ledger-policy-and-historical-dispositions.md`
  - `docs/specs/contract-stability.md`
  - `docs/specs/coverage-integrity.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_policy_and_audit.py`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
