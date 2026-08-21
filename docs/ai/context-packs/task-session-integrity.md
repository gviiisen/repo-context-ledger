# Task Session Integrity context pack

Status: current
Feature: task-session-integrity
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 6bdf90c56b59fde8890632b113bd61ccb9239c73
Base branch: main
Base commit: b5086a53c21962593ada4a0b96903faf10a7e54c
Last refreshed: 2026-08-21T23:41:25+08:00

## Purpose

Routes fresh Agent windows to the private draft state model, principal ownership, keyword resume, bounded Capsule, continuation epoch, explicit sharing, session evidence, finish gate, publication boundary, verification lock scope, and coordination policy. Use this pack when changing cross-Agent continuation, concurrent handoffs, publication recovery, state migration, or interaction with another user-owned task.

## Load order

- Read first: `docs/specs/task-session-integrity.md` and the lifecycle/state functions in `skills/repo-context-ledger/scripts/ledger.py`.
- Read if needed: `skills/repo-context-ledger/SKILL.md`, the handoff template, and `tests/test_ledger.py` when adapter policy, record identity, or concurrency behavior changes.
- Do not load by default: Coverage classification, Context Manifest ranking, README index generation, and unrelated stable feature specs.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::normalize_context_state` | Owns the v8 private draft, principal, epoch/tool, grant, and publication state shape. |
| `skills/repo-context-ledger/scripts/ledger.py::migrate_workspace_state` | Moves registered unfinished history records into private session storage. |
| `skills/repo-context-ledger/scripts/ledger.py::current_principal`, `session_access_level` | Separates human ownership from the Agent tool and fails foreign access closed. |
| `skills/repo-context-ledger/scripts/ledger.py::route_resume_sessions`, `build_resume_capsule` | Routes one available active/paused task and builds bounded initial continuation guidance. |
| `skills/repo-context-ledger/scripts/ledger.py::resume_change`, `validate_session_epoch` | Continues the same task and rejects stale post-resume writers. |
| `skills/repo-context-ledger/scripts/ledger.py::share_session`, `fork_granted_session` | Implements expiring read-only, fork, and paused transfer grants. |
| `skills/repo-context-ledger/scripts/ledger.py::resolve_task_session` | Enforces owned explicit targeting when more than one session matches. |
| `skills/repo-context-ledger/scripts/ledger.py::capture_evidence` | Refuses whole-worktree evidence capture when foreign sessions exist. |
| `skills/repo-context-ledger/scripts/ledger.py::task_session_finish_errors` | Checks only the selected task's evidence, specs, and relevant Pack fingerprints. |
| `skills/repo-context-ledger/scripts/ledger.py::finish_change` | Atomically publishes one completed record and cleans only its private draft. |
| `skills/repo-context-ledger/scripts/ledger.py::record_verification` | Defines the two short lock phases around an unlocked command. |
| `skills/repo-context-ledger/scripts/ledger.py::redact_local_paths` | Replaces known repository, Codex, temporary, and user-home roots before verification evidence is persisted. |
| `skills/repo-context-ledger/scripts/ledger.py::redact_record_local_paths` | Re-sanitizes legacy private checks and interrupted-publication records at `finish`. |
| `skills/repo-context-ledger/scripts/ledger.py::managed_rules` | Generates the prohibition on unsolicited cross-task steering. |

## Contracts and boundaries

- Invariants and contracts: Each unfinished draft has one principal owner and remains outside formal history; keyword routing considers only available active/paused sessions; ambiguous matches fail; Resume Capsule data is bounded and private; resume rotates an epoch/tool on the same session; foreign principals receive only an overlap signal; fork preserves the source and transfer requires a paused source; parallel evidence remains explicit; finish publishes at most once; verification runs unlocked; persisted checks redact credentials and machine roots.
- Failure / recovery: Invalid drafts, stale epochs, expired grants, and unauthorized mutations fail closed without changing the source task. Another clone can continue only from Git-tracked context. `finish` sanitizes legacy checks; interrupted publication retries by Session ID without duplicating history; legacy unfinished records bind conservatively without rewriting completed history.
- Non-goals: A Capsule does not prove full code-boundary understanding. Sessions do not persist chats, provide filesystem security, synchronize private state through Git, copy or merge source code, or authorize messages to another task.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` for v8 migration, same-principal cross-Agent resume, epochs, foreign Capsule isolation, expiring grants, private draft publication, adapter policy, lock scope, and verification redaction. Run `python skills/repo-context-ledger/scripts/ledger.py --repo . check --strict` for structural validation.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Task session integrity](../../specs/task-session-integrity.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:15141c54d126e9d9d74b41163430e4c3d8bada1169b32e96a56e6fe8451ea9a9`
- `skills/repo-context-ledger/SKILL.md` — `sha256:5134159090f71af8c66ea5235e5ff683141ed1a5fa8ba5407e0b08ba2679341f`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:cfb76dcea9238ffc40384e8118608d3bd89891ef42de622a8aad69478acdf945`
- `tests/test_ledger.py` — `sha256:417f31c7d8b52d3ae18c759a6d256251b2325891364cc8430aad82933bd78ebf`
<!-- repo-context-ledger:pack-files:end -->
