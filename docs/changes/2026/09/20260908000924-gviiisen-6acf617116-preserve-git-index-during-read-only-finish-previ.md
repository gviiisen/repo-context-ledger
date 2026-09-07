# Preserve Git index during read-only finish preview

Status: completed
Feature: repository-reliability
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260908000924-gviiisen-6acf617116
Session ID: 20260908000924-gviiisen-6acf617116
Actor: gviiisen
Branch: feat/small-fix-closeout
Started: 2026-09-08T00:09:24+08:00
Completed: 2026-09-08T00:14:59+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 44630d3805a54ae02184131497c715d64fa88e5a
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/runtime-architecture.md
Spec exception: none

## Intent

Fix the release-blocking CI failure where finish --dry-run changed a repository snapshot. Reproduce the mutation deterministically without weakening snapshot coverage, then keep all preview paths and bytes unchanged while preserving Git query results and required locking.

## Changed behavior

Before: Git status/diff subprocesses inherited optional-lock behavior. Git could refresh .git/index stat metadata even when Ledger itself did not write documents, caches or task state. The fast Ubuntu CI fixture exposed that mutation, while the slower local fixture usually did not.

After: Runtime Git subprocesses explicitly set GIT_OPTIONAL_LOCKS=0 in their own environment. A preview leaves .git/index unchanged even when a clean tracked file has stale stat metadata or the parent enables optional locks. The regression checks every snapshot path and byte and reports differing paths precisely.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/git.pyfrag::run_git` | Executes bounded Git commands. | Disables optional index-refresh writes only in the subprocess environment, preserving caller environment and required Git locking. |
| `tests/test_small_fix_closeout.py::test_preview_keeps_git_index_when_clean_file_stat_cache_is_outdated` | Exercises the real preview path against stale stat data. | Changes a clean file timestamp without changing its bytes and asserts the entire repository snapshot remains unchanged. This failed on .git/index before the fix and passed afterward. |
| `tests/test_small_fix_closeout.py::assert_snapshot_unchanged` | Explains byte-for-byte snapshot failures. | Reports exact changed paths instead of an unreadable multi-megabyte dictionary diff, without excluding Git metadata. |
| `skills/repo-context-ledger/scripts/ledger.py`, `.context-ledger/ledger.py` | Distribute the corrected Git read behavior. | Rebuilt from the canonical fragment with the unchanged v1.0.3 release identifier. |

## Boundaries and risks

- Invariant: A preview must preserve Git metadata as well as documents and private state. Actual Git query results and required repository locks must remain intact.
- Failure / recovery: The deterministic failing test remains as regression coverage; release stays blocked until the updated PR CI completes. No test ignores .git/index or relaxes its byte comparison.
- Not changed: Parent environment, user repositories, production operations, existing completed history and branch protection are untouched. No force merge or automatic lock deletion is used.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_small_fix_closeout.py`
  - Status: passed
  - Exit code: 0
  - Duration: 39.12s
  - Recorded: 2026-09-08T00:12:59+08:00
  - Output evidence: sha256:70e200c31a4c7193ca54f66385f76ae57a62c100774ae085b77e1b80c8d3c936 (116 characters captured; content not persisted; last=OK)
- Command: `python -B -m unittest discover -s tests -p test_repository_reliability.py`
  - Status: passed
  - Exit code: 0
  - Duration: 6.39s
  - Recorded: 2026-09-08T00:13:05+08:00
  - Output evidence: sha256:8170185f2522937a4dc8697e383cabae54a3eab5d9a25bbb4d762c72a0807682 (117 characters captured; content not persisted; last=OK (skipped=3))
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `docs/specs/runtime-architecture.md`, and affected current Context Pack fingerprints.

Reason: Explain the read-only Git-index guarantee as part of v1.0.3 and keep current Pack dependencies aligned with the generated runtime and Git fragment.

## Open questions

The initial Ubuntu Python 3.10 PR job failed and matrix fail-fast cancelled the remaining jobs. The targeted local closeout suite now passes all 16 cases; the repository-reliability suite passes four cases with three POSIX-only skips. Updated cross-platform PR validation remains required before release.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `44630d3805a54ae02184131497c715d64fa88e5a`
- Current commit: `44630d3805a54ae02184131497c715d64fa88e5a`
- Changed paths:
  - `.context-ledger/ledger.py`
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
  - `docs/ai/context-packs/verification-presets.md`
  - `docs/ai/context-packs/workflow-planning.md`
  - `docs/specs/runtime-architecture.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/git.pyfrag`
  - `tests/test_small_fix_closeout.py`
<!-- repo-context-ledger:evidence:end -->
