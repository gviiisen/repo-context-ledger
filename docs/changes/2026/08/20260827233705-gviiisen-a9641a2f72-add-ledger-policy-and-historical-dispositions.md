# Add ledger policy and historical dispositions

Status: completed
Feature: coverage-integrity
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827233705-gviiisen-a9641a2f72
Session ID: 20260827233705-gviiisen-a9641a2f72
Actor: gviiisen
Branch: fix/v1.0.2-ledger-policy-audit
Started: 2026-08-27T23:37:05+08:00
Completed: 2026-08-28T00:01:44+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/coverage-integrity.md, docs/specs/contract-stability.md
Spec exception: none

## Intent

Close the two v1 review gaps: expose one deterministic pull-request policy that handles ordinary and derived-only deltas, and make historical failures auditable without rewriting immutable Change records. Acceptance requires focused and full tests, a current standalone runtime, an unresolved-history audit with zero findings, and a PR workflow named `ledger-policy`.

## Changed behavior

Before: Pull requests chained separate team, Coverage, and diff commands; a derived-index-only PR was rejected solely because it ran on a feature branch. Full strict history also treated a genuine old failed verification as a permanent error with no append-only resolution mechanism.

After: `policy --base <ref>` classifies the actual merge-base delta as ordinary or derived-only and applies the matching aggregate gate. `audit --history --policy as-recorded` preserves recorded outcomes, while exact-hash `historical-disposition-v1` records can resolve known findings through a later completed Change and become invalid after any history edit.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::ledger_policy` | Owns aggregate PR classification and validation. | Added actual-diff derived classification, in-memory derived idempotence, ordinary Coverage, team overlap, runtime/adapter/Manifest, and diff gates. |
| `src/repo_context_ledger/runtime.py.tmpl::load_historical_dispositions` | Validates append-only historical resolutions. | Added strict JSON shape, repository path, completed Change, SHA-256, finding, later-resolution, approver, timestamp, and duplicate checks. |
| `src/repo_context_ledger/runtime.py.tmpl::audit_history` | Separates as-recorded integrity from unresolved findings. | Added read-only history audit and optional unresolved-finding failure policy. |
| `.github/workflows/test.yml` | Publishes the required GitHub PR check. | Replaced the multi-command `ledger-gates` job with one `ledger-policy` job. |
| `tests/test_policy_and_audit.py` | Protects both review gaps. | Added real Git derived/ordinary policy scenarios and hash-bound disposition/audit scenarios. |

## Boundaries and risks

- Invariant: Derived-only eligibility comes from file content, not a branch name or caller assertion; original completed Change bytes and their verification outcomes are never rewritten.
- Failure / recovery: A mixed or non-canonical derived delta falls back to ordinary checks or fails closed. A malformed, stale-hash, duplicate, or unsupported disposition remains an explicit audit error until the separate disposition is corrected.
- Not changed: Existing `team-check`, `check`, public JSON schemas, repository/private-state schema v8, session ownership, Pack/spec/Change layers, and the single-file runtime distribution remain compatible.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_policy_and_audit.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 8.41s
  - Recorded: 2026-08-27T23:48:58+08:00
  - Output evidence: sha256:4f92e006c2c33b9774c8ec10911d09640319d9d5563ee6508d6862e75f6b6c04 (746 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-27T23:48:59+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -B -m unittest discover -s tests -v`
  - Status: failed
  - Exit code: 1
  - Duration: 309.28s
  - Recorded: 2026-08-27T23:54:15+08:00
  - Output evidence: sha256:9959ee416f5714515c4fbf3b55057b81b5bc5fc903946b1c9670b28694127bad (27201 characters captured; content not persisted; failure=<redacted-token> (test_runtime_build.RuntimeBuildTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_runtime_build.RuntimeBuildTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("repo-context-ledger 1.0.1", version.stdout) | AssertionError: 'repo-context-ledger 1.0.1' not found in 'repo-context-ledger 1.0.2\n' | FAILED (failures=1, skipped=4))
- Command: `python -B -m unittest discover -s tests -p test_runtime_build.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 0.84s
  - Recorded: 2026-08-27T23:55:43+08:00
  - Output evidence: sha256:d19c071a5e0cd89194cb9ec66e1998d5adcc11a6bcd0963cb29c326e116a0e80 (1134 characters captured; content not persisted; last=OK (skipped=1))
- Command: `python -B -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 288.02s
  - Recorded: 2026-08-28T00:00:36+08:00
  - Output evidence: sha256:002208908f7846c162d04b77836409f8b700f61ab7f1d08955bb3f20661a2797 (26569 characters captured; content not persisted; last=OK (skipped=4))
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `COMPATIBILITY.md`, `MIGRATIONS.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/production-workflow.md`, `docs/specs/coverage-integrity.md`, `docs/specs/contract-stability.md`, and affected Context Packs.

Reason: Users, Agent integrations, and maintainers need one documented PR entry point plus an explicit immutable-history resolution protocol.

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
