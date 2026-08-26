# Close compact workflow review gaps

Status: completed
Feature: compact-local-config-workflow
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827031910-gviiisen-bb7acfb439
Session ID: 20260827031910-gviiisen-bb7acfb439
Actor: gviiisen
Branch: feat/v0.7.1-compact-local-config
Started: 2026-08-27T03:19:10+08:00
Completed: 2026-08-27T03:24:58+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 645a736f8220153a77d8cb041d6317eb85d10b9d
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/compact-local-config-workflow.md
Spec exception: none

## Intent

Close the correctness and privacy gaps found by the independent spec review before v0.7.1 leaves its feature branch. Acceptance requires compact finish to consume only explicit configuration evidence, require a final passing sensitive check, persist no free-form result text, and remain unavailable to ordinary source changes.

## Changed behavior

Before: A local-config session could omit `--path`, use an implementation path, finish after an ordinary or stale passing check, and persist arbitrary `--summary` text. Ordinary sessions could also pass `finish --path`, and a pass followed by a failed verification was not blocked by the general handoff gate.

After: Compact finish requires repeated explicit paths classified as `config`, rejects the option for ordinary sessions, and requires the final recorded check to be a passing `<sensitive verification>`. The generated After statement is fixed and value-free; the general gate now blocks whenever the latest executed verification failed.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Selects evidence and validates one session before publication. | Requires explicit config-classified paths for local-config, rejects compact paths for ordinary sessions, and enforces a final sensitive pass. |
| `src/repo_context_ledger/runtime.py.tmpl::complete_local_config_draft` | Generates the compact semantic handoff. | Removed free-form summary persistence and emits a fixed value-free After statement. |
| `src/repo_context_ledger/runtime.py.tmpl::evidence_handoff_errors` | Applies verification-quality gates to all completed Changes. | Changed the gate from “any pass exists” to “the latest executed check must not be failed.” |
| `tests/test_ledger.py` | Exercises public compact and ordinary CLI boundaries. | Added ordinary-check rejection, pass-then-fail recovery, missing-path, source-path, and ordinary-session isolation cases. |
| `docs/specs/compact-local-config-workflow.md`, `skills/repo-context-ledger/SKILL.md` | Define stable behavior and Agent routing. | Aligned the public workflow with the stricter config-only, final-sensitive-pass contract. |

## Boundaries and risks

- Invariant: Only paths matched by configured `coverage.config_globs` may use the automatic no-spec exception, and arbitrary configuration values are never accepted as handoff prose.
- Failure / recovery: Missing, non-config, or ordinary-session paths and a non-sensitive or failed final check return a precise error while preserving the private draft; a corrected sensitive pass permits retry.
- Not changed: Principal ownership, continuation epochs, Git path validation, lock scope, atomic publication, JSON schemas, and ordinary evidence/spec/Pack gates remain unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -v`
  - Status: failed
  - Exit code: 1
  - Duration: 255.55s
  - Recorded: 2026-08-27T03:23:34+08:00
  - Output evidence: sha256:2715b6787ffdff378463c2e9e91d647ea43fbcf12ee20540fb0631df57f47ea4 (17654 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... Injected post-publication failure. | Published record validation failed; the private draft and session were preserved for recovery. | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("failed verification", blocked.stderr) | AssertionError: 'failed verification' not found in 'Handoff latest verification failed; run a later passing verification.\nHandoff requires a passed ledger verify record or a substantive not-run exception.\n' | FAILED (failures=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -k <redacted-token>`
  - Status: passed
  - Exit code: 0
  - Duration: 3.22s
  - Recorded: 2026-08-27T03:24:00+08:00
  - Output evidence: sha256:7d35b91ff01182460df7dfef94b0266007ca06d4bfdf82d69aa5f56f71f60923 (98 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T03:24:01+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-27T03:24:02+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `docs/specs/compact-local-config-workflow.md`, `docs/ai/context-packs/compact-local-config-workflow.md`, `skills/repo-context-ledger/SKILL.md`, and the original v0.7.1 Change record.

Reason: The review changed the public CLI contract and narrowed the privacy/coverage boundary, so every user-facing description now matches the enforced runtime behavior.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `645a736f8220153a77d8cb041d6317eb85d10b9d`
- Current commit: `645a736f8220153a77d8cb041d6317eb85d10b9d`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `AGENTS.md`
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-packs/compact-local-config-workflow.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/changes/2026/08/20260827025332-gviiisen-90a3dd7099-reduce-ledger-overhead-for-local-configuration-c.md`
  - `docs/specs/compact-local-config-workflow.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
