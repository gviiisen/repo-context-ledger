# Modularize runtime source and stabilize protocols

Status: completed
Feature: runtime-architecture
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827185543-gviiisen-9afe5ba1c7
Session ID: 20260827185543-gviiisen-9afe5ba1c7
Actor: gviiisen
Branch: feat/v1.0-modular-runtime-contracts
Started: 2026-08-27T18:55:43+08:00
Completed: 2026-08-27T19:10:10+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 2c5ea2f81b7b8f8939ad274f44094a6b937faca5
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/runtime-architecture.md
Spec exception: none

## Intent

Establish a maintainable v1 source architecture and a formal integration contract without changing the one-file installation model. Acceptance requires independently owned source fragments for security/protocol-sensitive subsystems, deterministic standalone output, checked-in schemas for every public JSON protocol, and real CLI reports validated against those declarations.

## Changed behavior

Before: constants, errors, and result models were extracted, but lock ownership, core Git access, and Workflow Planning still lived in the monolithic template. Public JSON compatibility was described through prose and golden required-field lists rather than published schema documents.

After: ordered `locks.pyfrag`, `git.pyfrag`, and `workflow.pyfrag` sources are compiled with the existing fragments into the same standalone runtime. Five Draft 2020-12 schema files define the stable 1.x top-level fields, types, and enums, and a protocol test executes each real JSON command against those declarations.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `scripts/build_runtime.py::FRAGMENTS` | Deterministic source ordering. | Added locks, Git, and Workflow Planning markers after the existing low-coupling fragments. |
| `src/repo_context_ledger/locks.pyfrag::repo_lock` | Repository mutation coordination. | Moved the existing nonce/identity-safe lock implementation out of the template without behavior change. |
| `src/repo_context_ledger/git.pyfrag::run_git` | Core Git execution and fail-closed errors. | Moved repository detection, revision, branch, and actor access behind one explicit source boundary. |
| `src/repo_context_ledger/workflow.pyfrag::build_workflow_plan` | Public workflow decision contract. | Moved classification and rendering into a separately reviewed protocol fragment. |
| `schemas/workflow-plan-v1.schema.json` | Public JSON protocol declaration set. | Added Draft 2020-12 schemas for plan, context, doctor, status, and check, with open additive extension boundaries. |
| `tests/test_protocol_schemas.py` | Executable protocol compatibility check. | Added real CLI sample generation and stable top-level field/type/enum validation. |

## Boundaries and risks

- Invariant: both generated runtimes remain byte-identical, Python 3.10+ standard-library only, and independently executable; every marker occurs exactly once and no extracted definition remains in the template.
- Failure / recovery: a missing/duplicate fragment marker, generated drift, invalid schema JSON, missing required field, or incompatible emitted type fails the build/test gate. Recovery is to repair canonical fragments or publish a new versioned schema, never hand-edit one generated runtime.
- Not changed: repository/private schema v8, installed single-file shape, lifecycle behavior, permissions, lock semantics, Git fail-closed behavior, Workflow Plan semantics, and existing public exit classes remain unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python tests/test_runtime_build.py`
  - Status: passed
  - Exit code: 0
  - Duration: 0.81s
  - Recorded: 2026-08-27T19:05:18+08:00
  - Output evidence: sha256:a718eb7ddca63b6abd967f3378d6c1e77cce2c80644905d32a3f91c7f9cd325d (116 characters captured; content not persisted; last=OK (skipped=1))
- Command: `python tests/test_protocol_schemas.py`
  - Status: passed
  - Exit code: 0
  - Duration: 2.05s
  - Recorded: 2026-08-27T19:05:20+08:00
  - Output evidence: sha256:83efc01b0b176b0b6a0638af7a70a9a23dffe8bc18bdb9d416eaeba5e8cf24ce (100 characters captured; content not persisted; last=OK)
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 276.27s
  - Recorded: 2026-08-27T19:09:57+08:00
  - Output evidence: sha256:06f4106c9e5eaada0f17d48e004b3fb52563e4eb22ea8358fb8dccbffa7bca86 (25021 characters captured; content not persisted; last=OK (skipped=3))
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `ARCHITECTURE.md`, `COMPATIBILITY.md`, `MIGRATIONS.md`, `schemas/README.md`, `docs/specs/runtime-architecture.md`, `docs/specs/contract-stability.md`, and their Context Packs.

Reason: v1 source ownership, standalone distribution, protocol guarantees, integration rules, and upgrade behavior must be reviewable without reverse-engineering the builder or runtime.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `2c5ea2f81b7b8f8939ad274f44094a6b937faca5`
- Current commit: `2c5ea2f81b7b8f8939ad274f44094a6b937faca5`
- Changed paths:
  - `ARCHITECTURE.md`
  - `COMPATIBILITY.md`
  - `MIGRATIONS.md`
  - `docs/ai/context-packs/compact-local-config-workflow.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/continuation-quality.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/ai/context-packs/verification-presets.md`
  - `docs/ai/context-packs/workflow-planning.md`
  - `docs/specs/contract-stability.md`
  - `docs/specs/runtime-architecture.md`
  - `docs/specs/workflow-planning.md`
  - `schemas/README.md`
  - `schemas/check-v1.schema.json`
  - `schemas/context-bundle-v1.schema.json`
  - `schemas/doctor-v1.schema.json`
  - `schemas/status-v1.schema.json`
  - `schemas/workflow-plan-v1.schema.json`
  - `scripts/build_runtime.py`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/contracts.pyfrag`
  - `src/repo_context_ledger/git.pyfrag`
  - `src/repo_context_ledger/locks.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `src/repo_context_ledger/workflow.pyfrag`
  - `tests/test_protocol_schemas.py`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
