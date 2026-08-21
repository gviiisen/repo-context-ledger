# Task session integrity

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-21

## Purpose and behavior

Repo Context Ledger isolates lifecycle state, unfinished handoff content, evidence paths, and finish validation by task session within each Git worktree. Multiple tasks may keep private active or paused drafts concurrently. A fresh Agent window can route task keywords to one session owned by the same human principal and continue it without replaying the old chat; another principal cannot read or mutate that private task unless the owner creates an explicit expiring grant. Only a session-scoped validated `finish` publishes a completed change into formal history.

## Entry points and code map

| Path / symbol | Responsibility |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::normalize_context_state` | Validates the v8 private-draft session map, principal ownership, continuation epochs/tools, grants, and reserved publication paths. |
| `skills/repo-context-ledger/scripts/ledger.py::migrate_workspace_state` | Moves registered legacy active/paused records into private drafts without changing completed history. |
| `skills/repo-context-ledger/scripts/ledger.py::current_principal`, `session_access_level` | Derives a pseudonymous local principal and applies owner/read-only/fork/transfer access without using the Agent tool as identity. |
| `skills/repo-context-ledger/scripts/ledger.py::route_resume_sessions`, `build_resume_capsule` | Selects one owned active/paused task from keywords and builds a bounded private continuation route. |
| `skills/repo-context-ledger/scripts/ledger.py::resume_change`, `validate_session_epoch` | Continues the same session, rotates its continuation epoch/tool, and rejects stale lifecycle writers. |
| `skills/repo-context-ledger/scripts/ledger.py::share_session`, `fork_granted_session` | Creates expiring explicit access and keeps forked child work separate from the source task. |
| `skills/repo-context-ledger/scripts/ledger.py::resolve_task_session` | Resolves an owned explicit session or fails closed when multiple candidates exist. |
| `skills/repo-context-ledger/scripts/ledger.py::capture_evidence` | Requires explicit changed paths when foreign sessions exist and records only the selected task's evidence. |
| `skills/repo-context-ledger/scripts/ledger.py::task_session_finish_errors` | Validates the selected session without treating foreign worktree dirt or unrelated stale Packs as blockers. |
| `skills/repo-context-ledger/scripts/ledger.py::record_verification` | Binds and records a verification under short write locks while executing the command unlocked. |
| `skills/repo-context-ledger/scripts/ledger.py::redact_local_paths` | Replaces repository, Codex, temporary, and user-home roots before verification evidence enters a private draft or completed record. |
| `skills/repo-context-ledger/scripts/ledger.py::redact_record_local_paths` | Re-sanitizes the managed checks block at the atomic finish/recovery boundary. |
| `skills/repo-context-ledger/scripts/ledger.py::managed_rules` | Generates the repository policy that forbids unsolicited cross-task steering. |
| `skills/repo-context-ledger/SKILL.md` | Defines tool-independent task-session and cross-task coordination behavior. |

## Data flow and contracts

- Input: Lifecycle commands receive the repository, task keywords or an optional `--session`, the calling `--tool`, an expected `--epoch` after continuation, and command-specific evidence or verification arguments. Explicit sharing also receives a recipient principal, mode, and expiry.
- Flow: `context` scores only active/paused sessions available to the current principal, emits at most one bounded Capsule, and reports foreign overlap without private fields. `resume` keeps the selected session, increments its epoch, and changes its continuation tool. Owner writes validate that epoch. Read-only grants cannot resume; fork grants create a new recipient-owned draft; paused transfer grants change ownership when accepted. With parallel sessions, evidence accepts only explicit changed paths. `finish` validates the selected set, specs, and Pack fingerprints, publishes atomically, updates stable links and derived context, then removes only that session.
- Persistence / dependencies: Git repositories store the task-session map, drafts, principal hash, continuation metadata, and grants under worktree Git metadata; non-Git directories use `.context-ledger/sessions/`. Resume Capsules are generated on demand rather than persisted as Markdown. Completed handoffs remain Git-tracked Markdown.
- Output: Context Plan v2 returns an initial Resume Capsule with summary, next step, implementation evidence paths, verification, Git position, Pack, warnings, tool, and epoch. Active commands name the selected session and publication target. Verification results use stable local-root placeholders. `finish` outputs one completed change path, or preserves the draft and returns an error.

## Boundaries and failure modes

- Invariants: An unfinished draft has one owner principal and never appears in formal history; ambiguous keyword or lifecycle matches fail; a foreign principal receives no private Capsule fields; a continuation epoch must be reloaded before post-resume writes; forks never mutate their source; transfer requires a paused source; a session never absorbs foreign dirty paths; persisted verification evidence contains neither credential values nor known machine-specific absolute roots; successful finish publishes once and removes only the selected session.
- Permissions / concurrency: A repository write lock protects short state, draft, grant, and publication writes. External verification commands run without that lock. The principal defaults to the OS account and may use a repository-local configured identity for shared workstations; this is logical isolation, while filesystem permissions remain the security boundary. Agents may not contact or steer another user-owned task unless the user explicitly authorized cross-task coordination.
- Failure / recovery: Missing evidence, a false path, a stale continuation epoch, an expired grant, a foreign access attempt, or the current session's stale Pack preserves the draft. Ambiguous resume returns candidates without choosing. A different clone can recover only Git-tracked Packs/specs/completed Changes because private state does not travel. Interrupted publication recovery remains idempotent by Session ID.
- Non-goals: Task sessions do not persist full chats, guarantee semantic completeness from the Capsule, copy or merge source files, provide filesystem security or distributed locking across machines, synchronize private state through Git, or enforce Codex application messaging permissions at runtime.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` to cover v8 migration, same-principal cross-Agent resume, continuation epochs, foreign Capsule isolation, expiring read-only/fork/transfer grants, explicit parallel evidence, atomic publication, ambiguity, adapter policy, unlocked verification, and local-root redaction. Run `python skills/repo-context-ledger/scripts/ledger.py --repo . check --strict` as the repository-wide integration validation.

## Related changes

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Add cross-Agent session resume ownership](../changes/2026/08/20260821171622-gviiisen-67c0a5a3f9-add-cross-agent-session-resume-ownership.md)
- [Make fingerprints portable and redact local paths](../changes/2026/08/20260821144634-gviiisen-60f90c607e-make-fingerprints-portable-and-redact-local-path.md)
- [隔离并发任务的 evidence 与 finish 校验](../changes/2026/08/20260812041915-gviiisen-c1688f4523-evidence-finish.md)
- [将并发 handoff 改为私有草稿并安全归档](../changes/2026/08/20260812034448-gviiisen-6c5673170f-handoff.md)
- [隔离并发任务会话与验证锁](../changes/2026/08/20260812025946-gviiisen-ec71978b50-change.md)
<!-- repo-context-ledger:changes:end -->
