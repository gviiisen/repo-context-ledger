# Task session integrity

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-12

## Purpose and behavior

Repo Context Ledger isolates lifecycle state, unfinished handoff content, evidence paths, and finish validation by task session within each Git worktree. Multiple tasks may keep private active or paused drafts concurrently; only a session-scoped validated `finish` publishes a completed change into formal history, and ambiguous lifecycle operations fail until the caller supplies a session ID.

## Entry points and code map

| Path / symbol | Responsibility |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::normalize_context_state` | Validates the v7 private-draft session map and reserved publication paths. |
| `skills/repo-context-ledger/scripts/ledger.py::migrate_workspace_state` | Moves registered legacy active/paused records into private drafts without changing completed history. |
| `skills/repo-context-ledger/scripts/ledger.py::resolve_task_session` | Resolves an explicit session or fails closed when multiple candidates exist. |
| `skills/repo-context-ledger/scripts/ledger.py::capture_evidence` | Requires explicit changed paths when foreign sessions exist and records only the selected task's evidence. |
| `skills/repo-context-ledger/scripts/ledger.py::task_session_finish_errors` | Validates the selected session without treating foreign worktree dirt or unrelated stale Packs as blockers. |
| `skills/repo-context-ledger/scripts/ledger.py::record_verification` | Binds and records a verification under short write locks while executing the command unlocked. |
| `skills/repo-context-ledger/scripts/ledger.py::managed_rules` | Generates the repository policy that forbids unsolicited cross-task steering. |
| `skills/repo-context-ledger/SKILL.md` | Defines tool-independent task-session and cross-task coordination behavior. |

## Data flow and contracts

- Input: A lifecycle command receives the repository, an optional `--session` ID, and command-specific evidence or verification arguments.
- Flow: The runtime reads private worktree state, filters sessions by required status, resolves one private draft, and updates only that session. With parallel sessions, evidence accepts only explicit changed paths. `finish` validates that recorded set, explicit specs, and relevant Pack fingerprints, publishes its reserved target atomically, updates stable links and derived context, then removes the session.
- Persistence / dependencies: Git repositories store both the task-session map and drafts under worktree Git metadata; non-Git directories use `.context-ledger/sessions/`. Completed handoffs remain Git-tracked Markdown.
- Output: Active commands name the selected session and reserved publication target. `finish` outputs one completed change path, or preserves the draft and returns an error.

## Boundaries and failure modes

- Invariants: An unfinished draft belongs to exactly one task session and never appears in formal history; lifecycle commands never infer among multiple matches; a session never absorbs foreign dirty paths; successful finish publishes once and removes only the selected session.
- Permissions / concurrency: A repository write lock protects short state, draft, and publication writes. External verification commands run without that lock. Agents may not contact or steer another user-owned task unless the user explicitly authorized cross-task coordination.
- Failure / recovery: Missing explicit evidence, a falsely claimed path, or the current session's stale Pack preserves the draft. Foreign dirt and unrelated stale Packs do not block it. If publication completes before a later focused check fails, retry recognizes the same completed Session ID, reruns links and checks, and cleans the draft without duplicating history.
- Non-goals: Task sessions do not copy, lock, claim, merge, or coordinate source files, provide distributed locking across machines, or enforce Codex application messaging permissions at runtime.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` to cover v7 migration, explicit parallel evidence, foreign-stale isolation, current-session fail-closed behavior, atomic/idempotent publication, session ambiguity, adapter policy, and unlocked verification. Run `python skills/repo-context-ledger/scripts/ledger.py --repo . check --strict` as the repository-wide integration validation.

## Related changes

<!-- repo-context-ledger:changes:start -->
## Related changes

- [隔离并发任务的 evidence 与 finish 校验](../changes/2026/08/20260812041915-gviiisen-c1688f4523-evidence-finish.md)
- [将并发 handoff 改为私有草稿并安全归档](../changes/2026/08/20260812034448-gviiisen-6c5673170f-handoff.md)
- [隔离并发任务会话与验证锁](../changes/2026/08/20260812025946-gviiisen-ec71978b50-change.md)
<!-- repo-context-ledger:changes:end -->
