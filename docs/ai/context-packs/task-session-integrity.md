# Task Session Integrity context pack

Status: current
Feature: task-session-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: 650c18896bea6c287caae74a5b431cd68fa15cae
Base branch: main
Base commit: bd61e06cff7a1374cf842d8850604b1ab9567107
Last refreshed: 2026-08-15T15:56:30+08:00

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

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:702a0569ffe0731b9fbffb07a84b26d96e827f11ab27274d9a759f57d5e5f7d1`
- `skills/repo-context-ledger/SKILL.md` — `sha256:87b83e43decd4db8a3ed5f002a3a31a15bd37f1a7584827983708956ee35b448`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:f0acc36162fd1e36a8dee438fd7160ad03845df4da6739c1811994b366271ec1`
- `tests/test_ledger.py` — `sha256:0bbbbf7d6b5494aa5d7288e503343d9c1740eb9bdce38dd5db484063a6604650`
<!-- repo-context-ledger:pack-files:end -->
