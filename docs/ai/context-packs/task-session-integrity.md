# Task Session Integrity context pack

Status: current
Feature: task-session-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: 0745c24226099bffc29daee4e08715b254621205
Base branch: main
Base commit: 0745c24226099bffc29daee4e08715b254621205
Last refreshed: 2026-08-12T18:39:21+08:00

## Purpose

Routes fresh Agent windows to the private draft state model, explicit session evidence, focused finish gate, lifecycle resolver, atomic publication boundary, verification lock scope, and generated coordination policy. Use this pack when changing concurrent handoffs, publication recovery, state migration, or rules governing interaction with another user-owned task.

## Load order

- Read first: `docs/specs/task-session-integrity.md` and the lifecycle/state functions in `skills/repo-context-ledger/scripts/ledger.py`.
- Read if needed: `skills/repo-context-ledger/SKILL.md`, the handoff template, and `tests/test_ledger.py` when adapter policy, record identity, or concurrency behavior changes.
- Do not load by default: Coverage classification, Context Manifest ranking, README index generation, and unrelated stable feature specs.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::normalize_context_state` | Owns the v7 private draft and reserved publication state shape. |
| `skills/repo-context-ledger/scripts/ledger.py::migrate_workspace_state` | Moves registered unfinished history records into private session storage. |
| `skills/repo-context-ledger/scripts/ledger.py::resolve_task_session` | Enforces explicit targeting when more than one session matches. |
| `skills/repo-context-ledger/scripts/ledger.py::capture_evidence` | Refuses whole-worktree evidence capture when foreign sessions exist. |
| `skills/repo-context-ledger/scripts/ledger.py::task_session_finish_errors` | Checks only the selected task's evidence, specs, and relevant Pack fingerprints. |
| `skills/repo-context-ledger/scripts/ledger.py::finish_change` | Atomically publishes one completed record and cleans only its private draft. |
| `skills/repo-context-ledger/scripts/ledger.py::record_verification` | Defines the two short lock phases around an unlocked command. |
| `skills/repo-context-ledger/scripts/ledger.py::managed_rules` | Generates the prohibition on unsolicited cross-task steering. |

## Contracts and boundaries

- Invariants and contracts: Each unfinished draft belongs to one session and remains outside formal history; parallel evidence is explicit; ambiguous commands fail; foreign dirt cannot block finish; the current session's stale Pack fails closed; finish publishes at most once; verification commands never hold the repository write lock while running.
- Failure / recovery: Invalid drafts remain private. Interrupted publication is retried by Session ID without duplicating history, and registered v0.5.2 unfinished records migrate without rewriting completed history.
- Non-goals: Sessions do not copy, lock, claim, merge, or coordinate code and do not provide authority to message another task. Source conflicts remain outside the ledger.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` for private draft migration, isolated publication, recovery, adapter policy, and lock-scope coverage. Run `python skills/repo-context-ledger/scripts/ledger.py --repo . check --strict` for structural validation.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Task session integrity](../../specs/task-session-integrity.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:d7ee9215783a5ebe07c6f616859ab2b8d5cce7e423b42810f2d4222a3119f7f8`
- `skills/repo-context-ledger/SKILL.md` — `sha256:f92da03ac3e4c27781c8e7cf8fcf9f445e8583da9cfa5699a10cc36989df230e`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:f0acc36162fd1e36a8dee438fd7160ad03845df4da6739c1811994b366271ec1`
- `tests/test_ledger.py` — `sha256:65f63b717866c6aa2c26a2d6d0a0a855b2ab4ba453ca57f34e13e3ac08236bdc`
<!-- repo-context-ledger:pack-files:end -->
