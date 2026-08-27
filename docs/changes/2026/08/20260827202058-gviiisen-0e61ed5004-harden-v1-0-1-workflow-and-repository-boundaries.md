# Harden v1.0.1 workflow and repository boundaries

Status: completed
Feature: runtime-architecture
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827202058-gviiisen-0e61ed5004
Session ID: 20260827202058-gviiisen-0e61ed5004
Actor: gviiisen
Branch: main
Started: 2026-08-27T20:20:58+08:00
Completed: 2026-08-27T20:46:39+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: cc673f18238af119ecfe5cf08ffc2b4b3fc698e8
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/workflow-planning.md, docs/specs/runtime-architecture.md, docs/specs/task-session-integrity.md
Spec exception: none

## Intent

Harden the v1.0.1 planner, Git-path coverage, and filesystem permission boundaries identified during review. Acceptance requires risky requests to avoid `small-fix`, planned lifecycle commands to retain the calling tool, rename evidence to preserve its former implementation path, and POSIX public/private files to receive distinct default modes without changing existing-file behavior.

## Changed behavior

Before: Quantity words such as “one”, “single”, and “一个” could classify risky changes as `small-fix`; generated `start` and `resume` argv dropped `--tool`; rename parsing kept only the destination, so moving implementation code under tests could bypass Coverage; new atomic-write targets inherited `mkstemp()` mode and new private drafts used process defaults.

After: Only explicit typo, spelling, comment-only, or one-line scope can select `small-fix`, and risk vocabulary vetoes it. Planned executable actions preserve an explicit tool. Structured Git transitions feed both rename paths into evidence and Coverage while copies count only their destination. New public repository files use `0644` and private task/state/cache/trust files use `0600` on POSIX; replacement retains an existing mode.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/workflow.pyfrag::build_workflow_plan` | Classifies natural-language requests and builds structured next actions. | Replaced quantity-based small scope with conservative strong signals plus risk vetoes, expanded change vocabulary, and propagated explicit tool identity. |
| `src/repo_context_ledger/models.pyfrag::GitPathChange` | Represents one Git status transition without losing old/new identity. | Added an immutable standalone-runtime-compatible status, old-path, and new-path model. |
| `src/repo_context_ledger/runtime.py.tmpl::git_dirty_path_changes` | Parses NUL-delimited worktree status. | Preserves rename/copy source and destination while keeping destination-oriented `git_dirty_paths` compatibility. |
| `src/repo_context_ledger/runtime.py.tmpl::git_changed_path_changes` | Parses committed diff path transitions. | Uses `--name-status -z --find-renames` and exposes both rename endpoints to evidence and Coverage. |
| `src/repo_context_ledger/runtime.py.tmpl::atomic_write` | Atomically writes public and private repository/runtime files. | Assigns `0644` to new public files and `0600` to new private files, while preserving existing or explicitly copied modes. |
| `tests/test_workflow_plan.py` | Protects planner modes and action argv. | Added bilingual risk-negative cases and start/resume tool propagation coverage. |
| `tests/test_repository_reliability.py` | Protects Git path and POSIX permission contracts. | Added dirty/committed rename regression coverage and public/private mode assertions. |

## Boundaries and risks

- Invariant: `workflow-plan-v1` keeps its required fields and remains read-only; destination-oriented path-list callers retain their existing output; copy sources are not classified as modified implementation; existing file modes remain unchanged.
- Failure / recovery: Malformed or incomplete NUL-delimited rename records fail closed with `GIT_COMMAND_FAILED`. A failed full test run remains recorded, followed by the successful corrected run. POSIX-only mode assertions must pass in Ubuntu/macOS CI before release because Windows does not enforce them.
- Not changed: This patch does not add ordered Workflow Plan steps, route fields, a new JSON schema, configurable Git timeouts, transaction journaling, parent-directory `fsync`, or Windows ACL/ownership guarantees.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Preset: `runtime-build-check`
  - Working directory: `.`
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-27T20:36:46+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -B -m unittest discover -s tests -v`
  - Status: failed
  - Preset: `unit-full`
  - Working directory: `.`
  - Exit code: 1
  - Duration: 28.69s
  - Recorded: 2026-08-27T20:37:14+08:00
  - Output evidence: sha256:a693b75c516f43f261b86e19087e90210ba1880d3026dc6090c3b0a7f9371708 (18566 characters captured; content not persisted; failure=AssertionError: 0 != 1 : Traceback (most recent call last): | AttributeError: 'NoneType' object has no attribute '__dict__'. Did you mean: '__dir__'? | FAIL: <redacted-token> (test_routing_evaluation.RoutingEvaluationTests.<redacted-token>) | Traceback (most recent call last): | self.assertEqual(0, result.returncode, result.stdout + result.stderr) | AssertionError: 0 != 1 : Traceback (most recent call last): | AttributeError: 'NoneType' object has no attribute '__dict__'. Did you mean: '__dir__'? | FAILED (failures=2, errors=5, skipped=4))
- Command: `python -B -m unittest discover -s tests -v`
  - Status: passed
  - Preset: `unit-full`
  - Working directory: `.`
  - Exit code: 0
  - Duration: 284.12s
  - Recorded: 2026-08-27T20:44:18+08:00
  - Output evidence: sha256:9dd9c23588748152e4ad6743c2957e3e95cf3228499fa5c049e33bcd96c17f9b (25740 characters captured; content not persisted; last=OK (skipped=4))
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `ARCHITECTURE.md`, `COMPATIBILITY.md`, `MIGRATIONS.md`, `docs/specs/workflow-planning.md`, `docs/specs/runtime-architecture.md`, `docs/specs/task-session-integrity.md`, and the affected Context Packs.

Reason: These files define the public v1.0.1 behavior, compatibility boundary, upgrade guidance, Git transition semantics, planner classification rule, and POSIX public/private permission contract.

## Open questions

The POSIX-only mode assertions were skipped on this Windows host and require Ubuntu/macOS CI confirmation before release. No implementation uncertainty remains in the Windows-tested paths.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `cc673f18238af119ecfe5cf08ffc2b4b3fc698e8`
- Current commit: `cc673f18238af119ecfe5cf08ffc2b4b3fc698e8`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `ARCHITECTURE.md`
  - `COMPATIBILITY.md`
  - `MIGRATIONS.md`
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-manifest.json`
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
  - `docs/specs/runtime-architecture.md`
  - `docs/specs/task-session-integrity.md`
  - `docs/specs/workflow-planning.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/models.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `src/repo_context_ledger/workflow.pyfrag`
  - `tests/fixtures/workflow-plan-eval-v1.json`
  - `tests/test_repository_reliability.py`
  - `tests/test_runtime_build.py`
  - `tests/test_workflow_plan.py`
<!-- repo-context-ledger:evidence:end -->
