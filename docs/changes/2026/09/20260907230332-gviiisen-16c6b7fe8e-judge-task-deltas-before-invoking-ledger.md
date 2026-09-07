# Judge task deltas before invoking Ledger

Status: completed
Feature: workflow-planning
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260907230332-gviiisen-16c6b7fe8e
Session ID: 20260907230332-gviiisen-16c6b7fe8e
Actor: gviiisen
Branch: feat/small-fix-closeout
Started: 2026-09-07T23:03:32+08:00
Completed: 2026-09-07T23:12:50+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 1a0f4bf5e0c8199efdd4930435270406a1d95907
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/workflow-planning.md
Spec exception: none

## Intent

Let the Agent judge the actual incremental work from already loaded context before invoking Ledger. Repeated routine follow-ups should not restart the workflow, related unfinished changes should keep the current draft, and similar but genuinely new behavior must still receive current evidence without rewriting completed history.

## Changed behavior

Before: The Skill allowed reuse of a known task but later lifecycle guidance still directed ordinary work through plan/context/focus. Generated resume guidance treated a request to continue as a reason to query and resume even within an already known active window, creating contradictory repeated-work instructions.

After: A silent Agent-level delta decision precedes Ledger calls. Routine reads and requested rechecks with sufficient context use ordinary tools. Known unfinished work keeps its session/epoch and updates only new changes and findings. Missing context, a paused task or an actual handover uses the existing bounded commands. A new change after publication receives a new record; a similar request never justifies reusing stale verification or inferring authorization.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/SKILL.md` | Guides the Agent before tool use. | Adds a compact delta-first decision, makes routing conditional, and distinguishes unfinished continuation from new work after publication without a new command or document. |
| `skills/repo-context-ledger/references/production-workflow.md` | Defines detailed workflow decisions and counterexamples. | Documents ordinary rechecks, known active continuation, similar new interfaces, published history, actual handover and time-sensitive operations; explicitly states the limits of deterministic tests. |
| `src/repo_context_ledger/runtime.py.tmpl::context_plan_policy`, `resume_plan_policy`, `managed_rules` | Render native Agent instructions. | Remove unconditional repeat routing and same-window resume advice, and align all adapters with new-fact judgment and existing ownership/safety checks. |
| `skills/repo-context-ledger/scripts/ledger.py`, `.context-ledger/ledger.py`, `AGENTS.md` | Distribute the generated runtime and root instructions. | Rebuilt and synchronized while retaining all runtime command behavior. AST comparison against the prior installed artifact changed only the three instruction renderers. |
| `tests/test_small_fix_closeout.py` | Exercises real task lifecycle behavior. | Adds consecutive edits and fresh checks in one session without resume, retained reasoning, one publication, rejection of writes to a completed task, and a distinct later session. |

## Boundaries and risks

- Invariant: Reuse known background and methods, not stale passes or permissions. New behavior remains recorded, completed records remain immutable, and uncertain relevant boundaries still require code inspection.
- Failure / recovery: Missing or stale task identity uses the existing bounded lookup/resume path; never guess an epoch or adopt another task. Scope changes require fresh evidence as applicable. Installed files and consumer entry instructions were backed up before synchronization, outside Skill discovery.
- Not changed: No new CLI, classification document, semantic-deduplication service, test-result cache, permission bypass, or change to runtime mutation logic was introduced. No repository was initialized, no production operation was executed, and no history, business code, Git commit, push or Release was changed.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_small_fix_closeout.py`
  - Status: passed
  - Exit code: 0
  - Duration: 35.25s
  - Recorded: 2026-09-07T23:08:43+08:00
  - Output evidence: sha256:7a35b0511c1a7f11e2f1852f22edf0e064012bced5017227a3ae448af67b5679 (115 characters captured; content not persisted; last=OK)
- Command: `python -B -m unittest discover -s tests -p test_workflow_plan.py`
  - Status: passed
  - Exit code: 0
  - Duration: 11.34s
  - Recorded: 2026-09-07T23:08:55+08:00
  - Output evidence: sha256:2405121d3dd904bda04d91b9217333fa38b0e4879bc84044f6f00986119e80cb (106 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/production-workflow.md`, `AGENTS.md`, `README.md`, `README.zh-CN.md`, `docs/specs/workflow-planning.md`, `docs/ai/context-packs/workflow-planning.md`, and fingerprints in the other affected current Packs.

Reason: Make the user-facing and native Agent entry instructions agree about when routing is necessary and when an existing task can continue directly. The global Skill and consumer adapters were synchronized so the revised policy is actually available without copying a consumer runtime or rebuilding its documentation indexes.

## Open questions

The regression tests exercise lifecycle support and deterministic planner contracts, not the ability of every AI model to recognize every repeated task. Models must still judge new facts from current evidence. This instruction-focused change used targeted regression rather than rerunning the entire previously passing suite; installed/source byte identity, Skill validation and adapter checks were also verified.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `1a0f4bf5e0c8199efdd4930435270406a1d95907`
- Current commit: `1a0f4bf5e0c8199efdd4930435270406a1d95907`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `AGENTS.md`
  - `README.md`
  - `README.zh-CN.md`
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
  - `docs/specs/workflow-planning.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_small_fix_closeout.py`
<!-- repo-context-ledger:evidence:end -->
