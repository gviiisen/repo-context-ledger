# Prepare the v1.0.3 release

Status: completed
Feature: runtime-architecture
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260907235433-gviiisen-0423b7d012
Session ID: 20260907235433-gviiisen-0423b7d012
Actor: gviiisen
Branch: feat/small-fix-closeout
Started: 2026-09-07T23:54:33+08:00
Completed: 2026-09-08T00:03:45+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 1a0f4bf5e0c8199efdd4930435270406a1d95907
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/runtime-architecture.md
Spec exception: none

## Intent

Prepare the accumulated feature work for the requested public v1.0.3 release. Preserve the previously proposed v1.0.2 policy/audit work, publish clear bilingual version and migration notes, and validate the exact release runtime before committing and sending it through protected-branch CI.

## Changed behavior

Before: The local runtime reported 1.0.3-dev, the public latest release was v1.0.1, and PR 27 proposed v1.0.2 policy/audit work that had not been released. The feature branch already included its runtime capabilities but not the complete associated history/disposition or aggregate CI step.

After: Both standalone artifacts report 1.0.3, the version tests expect the final release identifier, and Windows/Ubuntu PR CI uses the aggregate ledger-policy gate. Existing policy/audit records and their unchanged hash-bound disposition are included. English and Chinese release notes explicitly state that unreleased v1.0.2 work is included in v1.0.3; no earlier release/tag is fabricated. Shared indexes remain deferred until after merge.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/constants.pyfrag::TOOL_VERSION` | Declares the distributed version. | Finalizes the development identifier as 1.0.3 without changing schema v8. |
| `skills/repo-context-ledger/scripts/ledger.py`, `.context-ledger/ledger.py` | Standalone release artifacts. | Rebuilt with the final version and verified byte-identical. |
| `tests/test_runtime_build.py` | Verifies deterministic standalone generation and executable version output. | Expects the final 1.0.3 identifier. |
| `.github/workflows/test.yml` | Runs pull-request gates and cross-platform tests. | Replaces separate team/check/diff steps with policy --base while preserving the Windows/Ubuntu Python matrix and macOS release checks. |
| `docs/audit-dispositions/20260822003651-final-verification-failed.json` | Preserves an existing maintainer disposition. | Imports the unchanged proposal from PR 27 with its original approval and matching historical record hash; no old result is rewritten. |

## Boundaries and risks

- Invariant: Do not bypass required CI or branch protection. Historical outcomes and approvals retain their original content; source and generated runtime versions agree and private application data stays out of the release.
- Failure / recovery: A failed local or remote gate blocks merge/release until explained and corrected. An existing release tag must never be overwritten. The existing consumer repository and global installation remain separate from Git staging of this release.
- Not changed: No business application, production deployment, credential, consumer-private draft, or old completed record is changed. This preparation does not claim that remote CI has already passed or that the final tag/Release already exists.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python .context-ledger/ledger.py audit --history --policy as-recorded --fail-on unresolved`
  - Status: passed
  - Exit code: 0
  - Duration: 0.30s
  - Recorded: 2026-09-07T23:57:03+08:00
  - Output evidence: sha256:a13fa94e9a15802792bc2e63d93afbcc26364a49239f013e1e13dfef1d828673 (129 characters captured; content not persisted; last=Historical audit passed.)
- Command: `python -B -m unittest discover -s tests -p test_*.py`
  - Status: passed
  - Exit code: 0
  - Duration: 282.34s
  - Recorded: 2026-09-08T00:00:28+08:00
  - Output evidence: sha256:434ae488b36ae1ab65377b19da454e79b47e48b71b223911234b909d548d372f (3630 characters captured; content not persisted; last=OK (skipped=4))
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `MIGRATIONS.md`, `COMPATIBILITY.md`, `docs/specs/runtime-architecture.md`, affected current Context Packs, and the original policy/audit Change records from the previously unreleased branch.

Reason: Users need an unambiguous final version, a truthful account of the skipped standalone v1.0.2 release, the global-versus-bundled upgrade boundary, and correct descriptions of bounded verification summaries. Existing audit evidence must accompany the incorporated policy/audit implementation.

## Open questions

The local Windows suite ran 166 tests with four POSIX-only skips. Windows/Ubuntu remote CI, post-merge derived-index synchronization and macOS release validation are the remaining release workflow gates; this preparation record does not pre-claim their outcomes. The referenced disposition matched the historical record in both the current worktree and an isolated Windows checkout probe.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `1a0f4bf5e0c8199efdd4930435270406a1d95907`
- Current commit: `1a0f4bf5e0c8199efdd4930435270406a1d95907`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `.github/workflows/test.yml`
  - `COMPATIBILITY.md`
  - `MIGRATIONS.md`
  - `README.md`
  - `README.zh-CN.md`
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
  - `docs/specs/runtime-architecture.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
