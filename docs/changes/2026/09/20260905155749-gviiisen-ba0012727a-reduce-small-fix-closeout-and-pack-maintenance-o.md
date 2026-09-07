# Reduce small-fix closeout and Pack maintenance overhead

Status: completed
Feature: small-fix-closeout
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260905155749-gviiisen-ba0012727a
Session ID: 20260905155749-gviiisen-ba0012727a
Actor: gviiisen
Branch: feat/small-fix-closeout
Started: 2026-09-05T15:57:49+08:00
Completed: 2026-09-05T16:27:49+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 1a0f4bf5e0c8199efdd4930435270406a1d95907
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/compact-local-config-workflow.md
Spec exception: none

## Intent

Reduce repetitive bookkeeping for a known low-risk fix while retaining evidence, verification, ownership, and feature knowledge. One logical request must close once, including its code, tests, and documentation; intermediate work stays private.

## Changed behavior

Before: Selecting small-fix printed a workflow label but created the same full handoff as ordinary-change. Authors repeated code-path and documentation facts, finish returned semantic errors before checking related Packs, and its preflight could save a router cache. Pack CLI paths were all fingerprint dependencies.

After: New small-fix drafts retain evidence-v1 with seven semantic prompts and runtime-generated scoped path/documentation fields. Optional finish --dry-run shares real preflight and reports resolvable errors without writes. Pack reading references are distinct from validity dependencies. Skill and generated rules keep the complete request in one session and make preview optional.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::small_fix_draft` | Selects the low-risk authoring form. | Keeps existing headings and seven semantic prompts without rewriting old drafts. |
| `src/repo_context_ledger/runtime.py.tmpl::complete_small_fix_draft` | Derives mechanical facts from session evidence. | Fills only generated placeholders; retains manual path/symbol explanations and the existing validation gate. |
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Prepares and atomically publishes this session. | Adds write-free optional preview and aggregated preflight while preserving ownership, epochs, draft checks, and final input revalidation. |
| `src/repo_context_ledger/runtime.py.tmpl::refresh_context_pack` | Maintains Pack dependencies. | Adds validated optional reading links without silently downgrading existing fingerprints or granting Coverage. |
| `tests/test_small_fix_closeout.py` | Exercises the public CLI in isolated temporary repositories. | Covers real verification, one-record completion, immutable preview, errors, session isolation, epochs, and dependency/reference behavior. |
| `benchmarks/small_fix_authoring_benchmark.py` | Measures reproducible fixture authoring fields and command overhead. | Verifies a changed constant and compares the full/explicit-evidence and short/auto-evidence forms without production data. |

## Boundaries and risks

- Invariant: Semantics remain Agent-authored; file lists come from scoped Git changes; claimed checks come from managed verification. Reading references never satisfy production Coverage or replace real behavior dependencies.
- Failure / recovery: Failed validation preserves the private draft. Preview does not lock or persist caches. Actual publication rechecks concurrent inputs. Multiple sessions require explicit evidence and stale continuation epochs or foreign owners fail before writing.
- Not changed: No production repository, installed global Skill, remote PR, Git history, or completed legacy Change is modified. Existing full and sensitive local-config workflows retain their contracts; risky changes are not reclassified by line count.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_*.py`
  - Status: passed
  - Exit code: 0
  - Duration: 275.22s
  - Recorded: 2026-09-05T16:23:39+08:00
  - Output evidence: sha256:9c614ec7a46446f4305aac2d505290f2b9f793a33450e16028e75a2f5a47fa12 (3610 characters captured; content not persisted; last=OK (skipped=4))
- Command: `python -B benchmarks/small_fix_authoring_benchmark.py --iterations 3`
  - Status: passed
  - Exit code: 0
  - Duration: 23.66s
  - Recorded: 2026-09-05T16:25:32+08:00
  - Output evidence: sha256:aeb13da773765c8db3d1d8473087e4051de339b0e6937091fa9e53375d104d33 (1565 characters captured; content not persisted; last=})
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `docs/specs/compact-local-config-workflow.md`, `docs/ai/context-packs/compact-local-config-workflow.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/production-workflow.md`, `skills/repo-context-ledger/references/writing-quality.md`, `README.md`, `README.zh-CN.md`, `benchmarks/README.md`, generated runtime/Agent entry points, and existing affected Pack fingerprints.

Reason: Document the smaller authoring contract, optional preview, reading-reference boundary, and measurement limitations. Preserve old dependency lists and history; shared derived indexes remain deferred on this feature branch.

## Open questions

Real Agent code-reading, reasoning, and writing time is not measured by the fixture. POSIX-only tests remain skipped on this Windows host. The separate pending policy/audit branch and installed v1.0.2 are not merged or downgraded by this work; publication and rollout are separate actions.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `1a0f4bf5e0c8199efdd4930435270406a1d95907`
- Current commit: `1a0f4bf5e0c8199efdd4930435270406a1d95907`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `.context-ledger/writing-quality.md`
  - `AGENTS.md`
  - `README.md`
  - `README.zh-CN.md`
  - `benchmarks/README.md`
  - `benchmarks/closeout_workflow_benchmark.py`
  - `benchmarks/small_fix_authoring_benchmark.py`
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
  - `docs/specs/compact-local-config-workflow.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/references/writing-quality.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_small_fix_closeout.py`
<!-- repo-context-ledger:evidence:end -->
