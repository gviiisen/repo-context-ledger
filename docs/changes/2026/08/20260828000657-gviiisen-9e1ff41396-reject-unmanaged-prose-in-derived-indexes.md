# Reject unmanaged prose in derived indexes

Status: completed
Feature: coverage-integrity
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260828000657-gviiisen-9e1ff41396
Session ID: 20260828000657-gviiisen-9e1ff41396
Actor: gviiisen
Branch: fix/v1.0.2-ledger-policy-audit
Started: 2026-08-28T00:06:57+08:00
Completed: 2026-08-28T00:08:26+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Dirty paths: none
Resume summary:
Next step:
Specs: none
Spec exception: The v1.0.2 policy specification already requires deterministic managed outputs; this follow-up closes an implementation edge case without changing the contract.

## Intent

Close the final derived-only classification gap by distinguishing generated managed-block updates from human prose edits outside those blocks. Acceptance requires focused tests for both paths and a current deterministic runtime build.

## Changed behavior

Before: Any path recognized as a generated index was eligible for derived-only mode; because synchronization preserves prose outside managed markers, a hand-added paragraph could remain idempotent and pass the narrower policy.

After: Existing generated Markdown indexes qualify only when content outside their managed block matches the merge base. Newly generated index files qualify only with their exact canonical heading, while a full JSON Manifest remains wholly derived.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::generated_index_only_change` | Determines whether a generated index delta is purely derived. | Added base comparison for unmanaged text and canonical-heading validation for newly created indexes. |
| `tests/test_policy_and_audit.py` | Protects aggregate policy fail-closed boundaries. | Split managed-block drift from unmanaged prose and asserted their derived/ordinary classifications independently. |

## Boundaries and risks

- Invariant: Human prose outside managed markers never receives a derived-only exemption; canonical newly created spec/change indexes remain eligible for deterministic sync PRs.
- Failure / recovery: Unmanaged prose switches the delta to ordinary policy, while managed content drift remains derived-only and fails with the required sync action.
- Not changed: Manifest generation, ordinary Coverage, README managed-block checks, historical audit, and public schemas are unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_policy_and_audit.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 15.34s
  - Recorded: 2026-08-28T00:08:01+08:00
  - Output evidence: sha256:0c968676fa8a744b3116e3b90109512f0cbb6a532582b4e1c64b347dcd48eb2d (1443 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-28T00:08:02+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: None — the published v1.0.2 contract already states that only managed README blocks and deterministic generated outputs qualify; this closes its executable edge case.

Reason: No stable contract changed; implementation now matches the documented fail-closed boundary.

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
  - `docs/changes/2026/08/20260828000442-gviiisen-0e6663b20a-harden-derived-only-policy-regression-coverage.md`
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
