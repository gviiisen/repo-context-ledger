# Task Session Integrity context pack

Status: current
Feature: task-session-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: e009aa650ed1928cfda06285b410c37aabb806be
Base branch: main
Base commit: e009aa650ed1928cfda06285b410c37aabb806be
Last refreshed: 2026-08-13T02:46:27+08:00

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

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:905f6d5cf5c9977aee606c912eac4be118f30b4ba77c6706e0198118ca5b67e2`
- `skills/repo-context-ledger/SKILL.md` — `sha256:9ce8ae0180b0c92c9495693f719f2fa11462bac3ea21d31d1bc81319b5af9ebc`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:f0acc36162fd1e36a8dee438fd7160ad03845df4da6739c1811994b366271ec1`
- `tests/test_ledger.py` — `sha256:187cfc68cf34317de08ff96942288439f38a6c136aa18ca19cec2d8afe2b83c2`
<!-- repo-context-ledger:pack-files:end -->
