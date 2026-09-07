# Harden derived-only policy regression coverage

Status: completed
Feature: coverage-integrity
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260828000442-gviiisen-0e6663b20a
Session ID: 20260828000442-gviiisen-0e6663b20a
Actor: gviiisen
Branch: fix/v1.0.2-ledger-policy-audit
Started: 2026-08-28T00:04:42+08:00
Completed: 2026-08-28T00:05:51+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Dirty paths: none
Resume summary:
Next step:
Specs: none
Spec exception: The stable v1.0.2 policy contract is already documented; this follow-up adds executable regression coverage and clarifies one error message.

## Intent

Harden the final derived-only review boundary with explicit regression cases for manual generated-index edits and README prose outside managed markers. Acceptance requires the focused policy/audit suite and deterministic runtime build to pass.

## Changed behavior

Before: The implementation covered both cases, but the focused suite only proved a canonical derived delta and an ordinary source change, leaving two important fail-closed boundaries implicit.

After: Tests prove a hand-edited generated index fails derived idempotence and README prose outside the managed block cannot receive derived-only classification; the derived drift message now reports the exact planned action clearly.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `tests/test_policy_and_audit.py` | Protects aggregate policy classification and failure boundaries. | Added manual-index drift and unmanaged README prose cases. |
| `src/repo_context_ledger/runtime.py.tmpl::ledger_policy` | Reports derived synchronization drift. | Reworded the deterministic error to report the planned create/update/delete action without malformed inflection. |

## Boundaries and risks

- Invariant: Generated paths are eligible for derived-only policy only when their entire current output equals canonical synchronization; README human prose is never treated as generated content.
- Failure / recovery: A manual derived edit fails with the path and planned sync action, allowing maintainers to regenerate rather than weaken the gate.
- Not changed: Ordinary Coverage, historical disposition validation, public schemas, and repository/private-state formats are unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_policy_and_audit.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 13.23s
  - Recorded: 2026-08-28T00:05:11+08:00
  - Output evidence: sha256:2abd30a4a7de59124378acd36c5951fcf2b1f97f4513e9228de687b984e97ece (1272 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-28T00:05:11+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: None — the behavior and boundaries were already documented in the v1.0.2 specification; this change adds missing executable coverage and clarifies one error.

Reason: No stable contract changed after the preceding specification update.

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
  - `docs/changes/2026/08/20260828000221-gviiisen-43054cb61c-classify-historical-dispositions-as-ledger-docum.md`
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
