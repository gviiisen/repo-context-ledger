# Accelerate small-task closeout

Status: completed
Feature: compact-local-config
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827060627-gviiisen-2e52131353
Session ID: 20260827060627-gviiisen-2e52131353
Actor: gviiisen
Branch: feat/v0.7.2-fast-closeout
Started: 2026-08-27T06:06:27+08:00
Completed: 2026-08-27T06:50:16+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: b7e4eb53249faa64881e37401a764093faf476b7
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/task-session-integrity.md, docs/specs/compact-local-config-workflow.md, docs/specs/runtime-architecture.md
Spec exception: none

## Intent

Reduce the bookkeeping latency of small code fixes without weakening task isolation, evidence quality, or finish safety. The accepted result is a measured workflow in which independent checks can overlap, transient verification writers do not fail on a momentary lock, and `finish` holds the repository lock only for bounded state validation and atomic publication.

## Changed behavior

Before: Agent instructions routed ordinary small fixes through repeated context, focus, evidence, and serial verification steps. Independent `verify` writers could fail immediately on the global write lock, and `finish` held that lock while collecting evidence, validating documents and Packs, publishing, and regenerating derived files.

After: A known single-session small fix follows start, implementation, concurrent independent verification, and finish; the separate evidence step is omitted unless scoping requires it. Short writers wait up to a bounded interval, optional private timings expose command stages, and `finish` prepares and validates unlocked before a compare-and-swap publication section. The three-run synthetic fixture improved median end-to-end closeout from 3.560 seconds to 2.306 seconds while median finish lock hold remained about 20 milliseconds.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::repo_lock` | Serializes short repository and private-state writes. | Adds bounded polling and private wait/hold timing instead of failing on transient contention. |
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Validates and publishes one completed task session. | Moves evidence rendering and validation outside the lock, verifies a bounded input signature at commit time, and delays derived synchronization until after publication. |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Executes and records one verification result. | Records execution-stage timing while retaining the existing unlocked command and short append phases. |
| `skills/repo-context-ledger/SKILL.md` | Defines the Agent-owned development lifecycle. | Adds the measured small-fix route, parallel-check boundary, and automatic finish evidence guidance. |
| `benchmarks/closeout_workflow_benchmark.py` | Measures serial and overlapped closeout in disposable Git repositories. | Adds a production-data-free timing fixture and zero-stagger verification collision check. |

## Boundaries and risks

- Invariant: Private drafts remain session-owned, every verification result is appended under a short repository lock, and only validated completed records enter `docs/changes/`.
- Failure / recovery: Persistent lock contention still fails closed. If the session, draft, spec, Pack, evidence file, or publication target changes during unlocked preparation, finish preserves the active draft and requires a retry. A derived-sync failure after publication leaves the completed Change authoritative and can be repaired with a later sync.
- Not changed: Checks that share mutable infrastructure remain serial; the runtime does not add event logs, session-level source locks, worktree copying, background daemons, or a new package distribution model.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T06:46:38+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py <REPO_ROOT>\skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T06:46:38+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -B benchmarks/closeout_workflow_benchmark.py --iterations 3 --verification-delay 0.6`
  - Status: passed
  - Exit code: 0
  - Duration: 33.38s
  - Recorded: 2026-08-27T06:47:11+08:00
  - Output evidence: sha256:f8f9dbad7053d40e5034cb7f4b28b065fdd886fe912a3b2bfb73e36302c56082 (1273 characters captured; content not persisted; last=})
- Command: `python -B -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 199.09s
  - Recorded: 2026-08-27T06:49:57+08:00
  - Output evidence: sha256:62c14cd1b51a570722bc284dbebfafe71a1c6a107787c5406b2316076fae2f3b (17235 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `benchmarks/README.md`, `docs/specs/task-session-integrity.md`, `docs/specs/compact-local-config-workflow.md`, `docs/specs/runtime-architecture.md`, `docs/ai/context-packs/task-session-integrity.md`, `docs/ai/context-packs/compact-local-config-workflow.md`, `docs/ai/context-packs/runtime-architecture.md`, `skills/repo-context-ledger/references/production-workflow.md`, and generated Agent rules.

Reason: The release changes the public Agent workflow, concurrency and recovery contracts, optional diagnostic output, deterministic runtime version, and published performance evidence.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `b7e4eb53249faa64881e37401a764093faf476b7`
- Current commit: `b7e4eb53249faa64881e37401a764093faf476b7`
- Changed paths:
  - `benchmarks/README.md`
  - `benchmarks/closeout_workflow_benchmark.py`
  - `docs/ai/context-packs/compact-local-config-workflow.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/compact-local-config-workflow.md`
  - `docs/specs/runtime-architecture.md`
  - `docs/specs/task-session-integrity.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_ledger.py`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
