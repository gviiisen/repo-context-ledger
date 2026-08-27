# Add deterministic Workflow Plan

Status: completed
Feature: cross-agent-context-relay
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827183113-gviiisen-f737fa1ffb
Session ID: 20260827183113-gviiisen-f737fa1ffb
Actor: gviiisen
Branch: feat/v0.9.0-workflow-plan
Started: 2026-08-27T18:31:13+08:00
Completed: 2026-08-27T18:54:09+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 25b94983f63d44d3f7134c37621957d531ad88f2
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/workflow-planning.md
Spec exception: none

## Intent

Add a deterministic, read-only Workflow Plan in front of lifecycle commands so an Agent can classify understanding requests, small fixes, ordinary changes, and resumptions before it creates or mutates a task session. The acceptance result is a versioned machine contract with explicit ambiguity handling, bilingual evaluation coverage, and a shorter progressive-disclosure Skill entry point.

## Changed behavior

Before: Native Agent instructions sent requests directly into `context`, `start`, or `resume`. Each integration had to infer the workflow itself, and ambiguous requests could cause unnecessary task sessions or duplicated continuation work.

After: `plan --query` returns `workflow-plan-v1` with one of four stable modes, bounded reasons, confidence, confirmation requirements, and a structured non-executing next action. `context` embeds the same decision, while `start` independently rejects read-only and resume workflows. Ambiguous automatic or resume routing returns an empty `clarify` action instead of mutating state.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::build_workflow_plan` | Canonical request classifier and next-action builder. | Added bounded English/Chinese signals, principal-owned Resume Capsule preflight, explicit intent handling, fail-closed ambiguity, text/JSON rendering, CLI wiring, and start guards. |
| `src/repo_context_ledger/constants.pyfrag::WORKFLOW_PLAN_SCHEMA` | Versioned runtime contract constants. | Added `workflow-plan-v1` and advanced the release version to 0.9.0. |
| `skills/repo-context-ledger/SKILL.md` | Agent-facing front door. | Replaced the long linear instructions with a Workflow Plan first path and progressive-disclosure references. |
| `tests/test_workflow_plan.py` | Behavioral and contract regression coverage. | Added explicit/automatic planning, bilingual evaluation, resume, ambiguity, read-only mutation, golden shape, and Skill-size checks. |

## Boundaries and risks

- Invariant: Planning is read-only; it does not execute the returned argv, create a session, alter a continuation epoch, or replace necessary code investigation.
- Failure / recovery: Unknown repository/private schemas preserve a versioned JSON error. Ambiguous intent returns `requires_confirmation=true`, `next_action.kind=clarify`, and an empty argv so the caller must obtain clarification.
- Not changed: Existing `start` callers remain compatible through the `ordinary-change` default; repository/private schema v8, `context-bundle-v1`, lifecycle evidence, permissions, locks, and Git collaboration behavior remain unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python tests/test_workflow_plan.py`
  - Status: passed
  - Exit code: 0
  - Duration: 9.03s
  - Recorded: 2026-08-27T18:49:20+08:00
  - Output evidence: sha256:43b5d30100ad36b251a38710f28a64ae833aafeb98eff435a181e3917997d2a9 (104 characters captured; content not persisted; last=OK)
- Command: `python tests/test_contract_stability.py`
  - Status: passed
  - Exit code: 0
  - Duration: 12.86s
  - Recorded: 2026-08-27T18:49:40+08:00
  - Output evidence: sha256:a16e247ca906fa640bc2b07daf8366e4672fa9d253af6665d8ffaf4d4d97a193 (108 characters captured; content not persisted; last=OK)
- Command: `python tests/test_runtime_build.py`
  - Status: passed
  - Exit code: 0
  - Duration: 0.80s
  - Recorded: 2026-08-27T18:49:42+08:00
  - Output evidence: sha256:c5a37b630d4e87b99f21cfb2226573043a6249b26492c887cc353a1fc8c6a37b (116 characters captured; content not persisted; last=OK (skipped=1))
- Command: `python -m unittest discover -s tests -p test_ledger.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 208.75s
  - Recorded: 2026-08-27T18:53:11+08:00
  - Output evidence: sha256:b1da97d4f527bb1c40c098f1b7d7c308cdcd378320812f80c82de166fc7df041 (13917 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `COMPATIBILITY.md`, `MIGRATIONS.md`, `ARCHITECTURE.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/production-workflow.md`, `docs/specs/workflow-planning.md`, and `docs/ai/context-packs/workflow-planning.md`.

Reason: The new public command/schema, native Agent entry path, compatibility boundary, migration behavior, and implementation map must be discoverable without reading runtime source.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `25b94983f63d44d3f7134c37621957d531ad88f2`
- Current commit: `25b94983f63d44d3f7134c37621957d531ad88f2`
- Changed paths:
  - `ARCHITECTURE.md`
  - `COMPATIBILITY.md`
  - `MIGRATIONS.md`
  - `docs/ai/context-packs/workflow-planning.md`
  - `docs/specs/workflow-planning.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/fixtures/workflow-plan-eval-v1.json`
  - `tests/golden/workflow-plan-v1.json`
  - `tests/test_contract_stability.py`
  - `tests/test_runtime_build.py`
  - `tests/test_workflow_plan.py`
<!-- repo-context-ledger:evidence:end -->
