# Reduce verification wrapping and support global runtime reuse

Status: completed
Feature: verification-presets
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260907222104-gviiisen-57768a4aa1
Session ID: 20260907222104-gviiisen-57768a4aa1
Actor: gviiisen
Branch: feat/small-fix-closeout
Started: 2026-09-07T22:21:04+08:00
Completed: 2026-09-07T22:47:01+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 1a0f4bf5e0c8199efdd4930435270406a1d95907
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/verification-presets.md, docs/specs/runtime-architecture.md, docs/specs/contract-stability.md
Spec exception: none

## Intent

Reduce repeated Ledger wrapping without discarding meaningful verification or change reasoning, update the local global Skill, and let an existing consumer repository use that executable without replacing its documentation or private state. Acceptance requires named failed/not-run substeps, fail-closed forwarding, unchanged consumer history, and preservation of the installed policy/audit capabilities.

## Changed behavior

Before: Guidance treated even one-off diagnostics as verify invocations and repeated task setup, encouraging a wrapper per helper rather than per acceptance goal. Subprocess duration was not clearly separated from total Ledger overhead. The consumer retained an older standalone runtime while the global Skill had newer policy/audit commands, so replacing the global installation directly from this earlier feature branch would lose those capabilities.

After: The development build uses ordinary tools for preparation/operations, reuses an identified session, and groups reviewed acceptance checks without replaying operations for logging. Optional bounded step annotations preserve passed/failed/not-run details while actual exit code controls the managed result. Timings separate subprocess, preparation, recording, and Ledger overhead. Opt-in global mode supplies a portable fail-closed forwarding entry, leaving configuration, ownership and history local. The global installation and consumer forwarding entry now use the same tested development runtime, retaining policy/audit commands.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification`, `verification_output_summary`, `emit_command_timings` | Execute and persist real acceptance results. | Add bounded redacted script-reported step summaries and distinguish child execution from preparation/recording/total overhead, without changing exit-code or sensitive-output gates. |
| `src/repo_context_ledger/runtime.py.tmpl::global_runtime_launcher`, `validate_config`, `build_init_plan`, `doctor_repo` | Select and validate the consuming repository runtime. | Add opt-in global mode, preserve it on init, preview the same launcher as apply, reject unsafe/missing targets, retain explicit repository selection, and diagnose launcher drift. |
| `src/repo_context_ledger/runtime.py.tmpl::ledger_policy`, `audit_history` | Preserve installed v1.0.2 integration and historical audit contracts. | Bring the existing local policy/audit implementation into this feature branch before upgrading the global Skill; retain hash-bound dispositions and actual-delta classification. |
| `src/repo_context_ledger/constants.pyfrag`, `tests/test_runtime_build.py` | Identify the development artifact and verify deterministic generation. | Set 1.0.3-dev and keep generated Skill/dogfood runtime copies byte-identical. |
| `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/production-workflow.md`, `skills/repo-context-ledger/references/verification-presets.md` | Guide task routing and acceptance boundaries. | Remove repeated setup inside a known task and per-helper wrapping, preserve separate safety phases, and prohibit replaying state-changing operations for missing evidence. |
| `skills/repo-context-ledger/assets/verify-change.py` | Optional project-owned grouped acceptance example. | Execute reviewed direct argv serially, stop on failure/timeout, report remaining checks as not-run, and fail when no checks are configured; it is not a deployment runner. |
| `tests/test_verification_boundaries.py` | Exercise real subprocesses and temporary Git repositories. | Verify forwarding across cwd changes, global upgrades, absent/recursive targets, launcher drift, grouped failure stopping, timing separation, and sensitive-summary suppression. |
| `tests/test_policy_and_audit.py` | Protect the previously installed integration gates. | Preserve eight regression cases for ordinary/derived-only classification, unmanaged prose, immutable-history dispositions, and unresolved findings. |

## Boundaries and risks

- Invariant: Actual subprocess exit code controls the managed result; script annotations are not independent attestations. Required pre/post-deployment and authorization checks stay ordered. Global executable sharing never shares configuration, private ownership, or task state; default bundled mode remains available.
- Failure / recovery: Empty acceptance configuration, failed/timed-out checks, a missing/recursive global target, and a drifted launcher fail closed. A failed check preserves the draft and marks remaining helper steps not-run. Installations were backed up outside Skill discovery; the old consumer runtime was moved to a recoverable backup, not erased. No deployment or trading operation was replayed.
- Not changed: No automatic preset execution, background event log, global source-file locking, cross-task steering, production deployment, Git commit, push, or Release was introduced. Earlier uncommitted feature work and completed history remain intact. Existing consumer Git hooks were not modified.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_*.py`
  - Status: failed
  - Exit code: 1
  - Duration: 293.62s
  - Recorded: 2026-09-07T22:35:24+08:00
  - Output evidence: sha256:9a28c2c9c04822ae71efff288f30086508bbeef23f6360e7e8d3b9c5ec456e88 (11565 characters captured; content not persisted; failure=FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("verify --sensitive", rules) | AssertionError: 'verify --sensitive' not found in '# Agent instructions\n\n<!-- repo-context-ledger:rules:start -->\n## Repository context ledger\n\nResolve an unidentified new request or fresh window with `plan --query "<user request>" --tool <agent>`. Follow its mode and `next_action`; clarify when `requires_confirmation` is true. Inside a known task, retain its session and epoch without repeating plan/status/context/focus unless identity, scope, repository, or an unresolved question changes. Read-only work never starts a session. A bounded configuration change uses `start --kind local-config --workflow small-fix` �� sensitive acceptanc…)
- Command: `python -B -m unittest discover -s tests -p test_ledger.py -k generated_agent_rules -v`
  - Status: failed
  - Exit code: 1
  - Duration: 0.78s
  - Recorded: 2026-09-07T22:36:15+08:00
  - Output evidence: sha256:04654bc7753bc23d6437b19b77046c3e09e8e455cca7731b0e78efbfa7c0b348 (8316 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("skip context/focus and a separate evidence command", rules) | AssertionError: 'skip context/focus and a separate evidence command' not found in '# Agent instructions\n\n<!-- repo-context-ledger:rules:start -->\n## Repository context ledger\n\nResolve an unidentified new request or fresh window with `plan --query "<user request>" --tool <agent>`. Follow its mode and `next_action`; clarify when `requires_confirmation` is true. Inside a known task, retain its session and epoch without repeating plan/status/context/focus unless identity, scope, repository, or an unresolved question changes. Read-on…)
- Command: `python -B -m unittest discover -s tests -p test_*.py`
  - Status: passed
  - Exit code: 0
  - Duration: 321.86s
  - Recorded: 2026-09-07T22:42:25+08:00
  - Output evidence: sha256:551a40a931aa7e72cbd17a0973636a115176ee0469b85c35a610c3474a3ac0df (3629 characters captured; content not persisted; last=OK (skipped=4))
- Command: `python .context-ledger/ledger.py policy --base origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 14.77s
  - Recorded: 2026-09-07T22:46:14+08:00
  - Output evidence: sha256:fee0df1f5e08af9a6076e04e69c0725e8310e921452e3848c00eaf4fe96f9cf7 (331 characters captured; content not persisted; last=Ledger policy passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `AGENTS.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/production-workflow.md`, `skills/repo-context-ledger/references/verification-presets.md`, `skills/repo-context-ledger/references/global-runtime.md`, `docs/specs/verification-presets.md`, `docs/specs/runtime-architecture.md`, `docs/specs/contract-stability.md`, and affected current Context Packs.

Reason: Document acceptance-goal granularity rather than per-command logging, accurate timing semantics, optional step summaries, and global/bundled runtime selection. Preserve the installed policy/audit instructions and legacy completed records. Consumer entry guidance was updated without rebuilding documentation indexes or migrating task state; no consumer source, logs, paths, or credentials were copied into public examples.

## Open questions

The Windows suite ran 165 tests with four POSIX-specific skips; those skipped cases still need Unix CI. Removing wrappers does not shorten deployment scripts or tests themselves. Substep annotations are bounded to 16 and additional annotations are explicitly counted as omitted. Global mode requires an installation on each machine, and updating it does not replace instructions already loaded into an Agent conversation.

## Migration and verification notes

The consumer migration preserved all 1,355 existing documentation files and 15 private-state files byte-for-byte, retained HEAD and an empty staging area, and changed only the intended runtime/configuration/Agent entry files. The project runtime is now a 1,065-byte forwarding entry. Its version and read-only status resolved through the global installation, enabled adapter checks passed, and global/source/dogfood executable SHA-256 values matched. Backups remain outside the Skill discovery directory.

The first full suite found that shortened generated guidance omitted the explicit sensitive-verification command; a targeted rerun then caught an omitted narrow-workflow skip instruction. Both instructions were restored without weakening tests or runtime gates. The final complete suite passed and retains earlier failed attempts in the managed verification block.

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
  - `docs/specs/contract-stability.md`
  - `docs/specs/runtime-architecture.md`
  - `docs/specs/verification-presets.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/assets/verify-change.py`
  - `skills/repo-context-ledger/references/global-runtime.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/references/verification-presets.md`
  - `skills/repo-context-ledger/references/writing-quality.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_policy_and_audit.py`
  - `tests/test_runtime_build.py`
  - `tests/test_small_fix_closeout.py`
  - `tests/test_verification_boundaries.py`
<!-- repo-context-ledger:evidence:end -->
