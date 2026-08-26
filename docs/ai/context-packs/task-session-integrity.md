# Task Session Integrity context pack

Status: current
Feature: task-session-integrity
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: e9589ed8c0474590bc6266d9d92424ac1b5050cb
Base branch: main
Base commit: b7e4eb53249faa64881e37401a764093faf476b7
Last refreshed: 2026-08-27T07:16:08+08:00

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
| `skills/repo-context-ledger/scripts/ledger.py::finish_change`, `finish_input_signature` | Prepares and validates outside the lock, then compare-and-swaps bounded inputs before short atomic publication. |
| `skills/repo-context-ledger/scripts/ledger.py::record_verification` | Defines the two short lock phases around an unlocked command and bounded waits between concurrent verification writers. |
| `skills/repo-context-ledger/scripts/ledger.py::redact_local_paths` | Replaces known repository, Codex, temporary, and user-home roots before verification evidence is persisted. |
| `skills/repo-context-ledger/scripts/ledger.py::redact_record_local_paths` | Re-sanitizes legacy private checks and interrupted-publication records at `finish`. |
| `skills/repo-context-ledger/scripts/ledger.py::managed_rules` | Generates the prohibition on unsolicited cross-task steering. |

## Contracts and boundaries

- Invariants and contracts: Each unfinished draft has one principal owner and remains outside formal history; keyword routing considers only available active/paused sessions; ambiguous matches fail; Resume Capsule data is bounded and private; resume rotates an epoch/tool on the same session; foreign principals receive only an overlap signal; fork preserves the source and transfer requires a paused source; parallel evidence remains explicit; finish publishes at most once; verification runs unlocked; transient short writers wait for a bounded interval; finish validation does not hold the repository lock; persisted checks redact credentials and machine roots; `--timings` remains private and path-free.
- Failure / recovery: Invalid drafts, stale epochs, expired grants, unauthorized mutations, persistent lock contention, and bounded inputs changed during finish preparation fail closed without changing the source task. Another clone can continue only from Git-tracked context. `finish` sanitizes legacy checks; interrupted publication retries by Session ID without duplicating history; a post-publication derived-sync failure is repaired by a later sync; legacy unfinished records bind conservatively without rewriting completed history.
- Non-goals: A Capsule does not prove full code-boundary understanding. Sessions do not persist chats, provide filesystem security, synchronize private state through Git, copy or merge source code, or authorize messages to another task.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py` for v8 migration, same-principal cross-Agent resume, epochs, foreign Capsule isolation, expiring grants, private draft publication, parallel verification, bounded waits, finish compare-and-swap behavior, interrupted recovery, timing privacy, adapter policy, lock scope, and verification redaction. Run `python skills/repo-context-ledger/scripts/ledger.py --repo . check --strict` for structural validation. Run `python benchmarks/closeout_workflow_benchmark.py` for the synthetic serial/overlapped comparison.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Task session integrity](../../specs/task-session-integrity.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:187328722f04f19285b4e95115a6bda0b565ab554419156797307229a911045c`
- `skills/repo-context-ledger/SKILL.md` — `sha256:819c709ed64de35af4cf57efc4967ccb68554d340ffc4aac673222fb5763b6d2`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:6dc2c1cc8f3483e2c977e0e58483559d93411247d69fe3623d047e4486279003`
- `skills/repo-context-ledger/assets/handoff-template.md` — `sha256:dd1e26e29993ac93d5f52de315df130b270982125b4037dc01c17d9cb63f9a52`
- `tests/test_ledger.py` — `sha256:bb1837198bb1324bea43b4f974991d59041780970efe5251a20085a83fd4a03a`
- `benchmarks/closeout_workflow_benchmark.py` — `sha256:33fb3dc82c2acd29e5bab6d3870046868a5d79858c2ac7641bb0a8102c089d6c`
- `benchmarks/README.md` — `sha256:9244091fc1202a9c40c54f2fb7f81d7e708dacd3d619f8e68e70f70ee633088a`
<!-- repo-context-ledger:pack-files:end -->
