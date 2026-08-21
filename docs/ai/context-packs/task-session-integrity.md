# Task Session Integrity context pack

Status: current
Feature: task-session-integrity
Quality profile: evidence-v1
Language: zh-CN
Detail: standard
Source commit: 5892ff462b3970d3e86555ac79d3cf304571c172
Base branch: main
Base commit: 5892ff462b3970d3e86555ac79d3cf304571c172
Last refreshed: 2026-08-21T15:03:51+08:00

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
| `skills/repo-context-ledger/scripts/ledger.py::redact_local_paths` | Replaces known repository, Codex, temporary, and user-home roots before verification evidence is persisted. |
| `skills/repo-context-ledger/scripts/ledger.py::redact_record_local_paths` | Re-sanitizes legacy private checks and interrupted-publication records at `finish`. |
| `skills/repo-context-ledger/scripts/ledger.py::managed_rules` | Generates the prohibition on unsolicited cross-task steering. |

## Contracts and boundaries

- Invariants and contracts: Each unfinished draft belongs to one session and remains outside formal history; parallel evidence is explicit; ambiguous commands fail; foreign dirt cannot block finish; the current session's stale Pack fails closed; finish publishes at most once; verification commands never hold the repository write lock while running; persisted checks redact credential values and machine-specific roots, including JSON-escaped Windows paths.
- Failure / recovery: Invalid drafts remain private. `finish` sanitizes checks created before an upgrade; interrupted publication is retried and re-sanitized by Session ID without duplicating history, and registered v0.5.2 unfinished records migrate without rewriting completed history.
- Non-goals: Sessions do not copy, lock, claim, merge, or coordinate code and do not provide authority to message another task. Source conflicts remain outside the ledger.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` for private draft migration, isolated publication, recovery, adapter policy, lock-scope coverage, and passed/failed verification path redaction. Run `python skills/repo-context-ledger/scripts/ledger.py --repo . check --strict` for structural validation.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Task session integrity](../../specs/task-session-integrity.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:c35cc09d2be70369bec0255253dc8ad44091af5a04ca0f33bfd329138a3835d2`
- `skills/repo-context-ledger/SKILL.md` — `sha256:e75be77d0ce3ec5b9e6e2db7f68afef2c3219ecbb4fdd759011f10c40847a66c`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:cfb76dcea9238ffc40384e8118608d3bd89891ef42de622a8aad69478acdf945`
- `tests/test_ledger.py` — `sha256:7a7aeea0a0880a31ee5d96801a6d12b88ee5606f67527154cac9a4f16eda45b6`
<!-- repo-context-ledger:pack-files:end -->
