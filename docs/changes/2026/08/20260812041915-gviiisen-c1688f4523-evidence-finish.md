# 隔离并发任务的 evidence 与 finish 校验

Status: completed
Feature: task-session-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Handoff ID: 20260812041915-gviiisen-c1688f4523
Session ID: 20260812041915-gviiisen-c1688f4523
Actor: gviiisen
Branch: main
Started: 2026-08-12T04:19:15+08:00
Completed: 2026-08-12T04:35:09+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98
Dirty paths: none
Resume summary:
Next step: Run the complete regression suite, self-bootstrap the repository runtime, refresh affected Context Packs, and validate both the session finish gate and the repository-wide integration gate.
Specs: docs/specs/task-session-integrity.md, docs/specs/coverage-integrity.md
Spec exception: none

## Intent

Prevent parallel AI tasks in one worktree from contaminating or blocking each other's Ledger lifecycle. A task must capture only its explicitly owned paths, finish without reading foreign dirty paths or stale Packs as blockers, and still fail closed when its own evidence or related Pack is stale.

## Changed behavior

Before: v0.5.3 stored private drafts per session, but `evidence` copied the entire shared worktree dirty set into the selected draft and `finish` ran repository-wide strict validation. A foreign task's files or stale Context Pack could therefore block the current task and encourage an Agent to contact or pause another user task.

After: v0.5.4 requires repeated `--path` values when parallel sessions exist, verifies those paths are real Git changes, and records only that set. `finish` applies a session-scoped gate to the selected draft, explicit specs, and related Pack fingerprints; foreign dirty paths and stale Packs remain visible to the later repository-wide integration check but cannot block or redirect the current task.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py` | `capture_evidence`, `task_session_finish_errors`, and `finish_change` own evidence capture, session validation, and atomic publication. | Added repeatable explicit path selection; validates only session-owned paths, explicit specs, and related fingerprints; preserves private-draft recovery and idempotent publication. |
| `tests/test_ledger.py` | Exercises runtime lifecycle and coverage behavior in temporary Git repositories. | Added parallel evidence, foreign-stale isolation, current-session stale rejection, and updated publication recovery coverage. |

## Boundaries and risks

- Invariant: A completed record is published at most once; a task may only claim paths that Git reports as changed; the current task's stale related Pack still blocks completion.
- Failure / recovery: Invalid or omitted parallel evidence fails before mutating the draft. A failed finish preserves the private draft and session so the same task can correct evidence or refresh its Pack and retry.
- Not changed: `check --strict --coverage` remains the repository-wide integration gate and still reports all uncovered paths, stale Packs, adapter drift, and derived-document problems after concurrent tasks have settled. Runtime state schema remains v7.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 107.28s
  - Recorded: 2026-08-12T04:34:36+08:00
  - Output evidence: sha256:6e95e256bdb2737787c831d5327bd01fc84ec220113326ecefbe3f1097e90747 (275 characters captured; content not persisted)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py <REPO_ROOT>\skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-12T04:34:45+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted)
- Command: `python .context-ledger/ledger.py --repo . check --strict --coverage`
  - Status: passed
  - Exit code: 0
  - Duration: 1.47s
  - Recorded: 2026-08-12T04:34:47+08:00
  - Output evidence: sha256:74952ea792336837ef8400c980dc0f9978862f98d9f3a3af55dc87a68840e681 (34 characters captured; content not persisted)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/document-model.md`, `docs/specs/task-session-integrity.md`, `docs/specs/coverage-integrity.md`, `docs/ai/context-packs/task-session-integrity.md`, `docs/ai/context-packs/native-context-bridge.md`, `docs/ai/context-packs/coverage-integrity.md`.

Reason: The public workflow and durable context model must explicitly distinguish per-session completion from whole-repository integration and prohibit treating foreign failures as cross-task coordination authority.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98`
- Current commit: `da095bc00c8acfa6f0fd60c88ba9b8f117ce0e98`
- Changed paths:
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/coverage-integrity.md`
  - `docs/specs/task-session-integrity.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/document-model.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
