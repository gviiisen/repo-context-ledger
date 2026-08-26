# Reduce Ledger overhead for local configuration changes

Status: completed
Feature: compact-local-config-workflow
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827025332-gviiisen-90a3dd7099
Session ID: 20260827025332-gviiisen-90a3dd7099
Actor: gviiisen
Branch: feat/v0.7.1-compact-local-config
Started: 2026-08-27T02:53:32+08:00
Completed: 2026-08-27T03:12:04+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: dd283c73130ec672e183fe8018c4b19217efdf52
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/compact-local-config-workflow.md
Spec exception: none

## Intent

Reduce the bookkeeping cost observed when an Agent changes one tracked, worktree-local configuration file. Acceptance requires a short public CLI path that scopes Git evidence, generates the completed record, preserves real verification, and prevents sensitive command arguments or output from entering the terminal transcript or Ledger Markdown.

## Changed behavior

Before: Every behavior-affecting configuration edit followed the ordinary context, focus, evidence, manual handoff, spec-exception, and finish sequence. Sensitive verification could redact recognized credential labels, but arbitrary local configuration values in command output were still visible to the Agent and could complicate safe record keeping.

After: `start --kind local-config`, `verify --sensitive`, and `finish --path ... --summary ...` provide a bounded worktree-local path. Finish captures only explicit Git-changed paths, generates the semantic handoff with `Scope: worktree-local`, applies the stable-spec exception, and preserves a failed draft for correction; sensitive verification stores only status, exit code, duration, and time.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::start_change` | Creates private sessions and renders their initial metadata. | Added the backward-compatible `change` / `local-config` task kind and scope metadata. |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Executes checks outside the write lock and writes managed verification evidence. | Added `--sensitive`, which suppresses command arguments and captured output while preserving status metadata. |
| `src/repo_context_ledger/runtime.py.tmpl::complete_local_config_draft`, `finish_change` | Captures scoped evidence, validates handoffs, and publishes completed Changes. | Added `finish --path` evidence capture and deterministic semantic completion for local configuration sessions. |
| `src/repo_context_ledger/runtime.py.tmpl::doctor_legacy_workflow_findings` | Produces read-only repository health findings. | Added a warning for unmanaged legacy active-handoff instructions that coexist with private sessions. |
| `skills/repo-context-ledger/SKILL.md`, `AGENTS.md` | Routes Agents through the appropriate lifecycle. | Added the compact path, direct-executable guidance, explicit language selection, and the boundary that ordinary behavior changes retain full gates. |
| `tests/test_ledger.py`, `tests/test_doctor.py` | Exercise public CLI and Doctor behavior. | Added secret non-disclosure, failed-check recovery, precise summary error, automatic finish, adapter-policy, and legacy-conflict regressions. |

## Boundaries and risks

- Invariant: Existing ordinary sessions, principal ownership, continuation epochs, explicit path evidence, atomic publication, JSON schemas, and exit classes remain compatible.
- Failure / recovery: Failed sensitive checks remain visible as a sanitized failed status; a later pass is required. Missing summary, invalid path, stale epoch, or validation failure returns nonzero and keeps the private draft active.
- Not changed: The runtime does not edit configuration values, synchronize machine state through Git, hide ordinary failed verification, coordinate source-file writers, or weaken medium/large behavior-change documentation.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 240.64s
  - Recorded: 2026-08-27T03:08:22+08:00
  - Output evidence: sha256:41c379ac5192742d60146a38e393dca6efd9ce8aeb2d2fccca467fa207bd33da (16675 characters captured; content not persisted; last=OK)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: failed
  - Exit code: 1
  - Duration: 0.12s
  - Recorded: 2026-08-27T03:08:33+08:00
  - Output evidence: sha256:4f520ae17f97392547f1a52ab3834eb199b0db6e8488ed71ce512d077ebfcdfe (694 characters captured; content not persisted; failure=Traceback (most recent call last): | UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 2521: illegal multibyte sequence)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T03:08:34+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T03:08:43+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -m unittest discover -s tests -p test_ledger.py -k local_config`
  - Status: passed
  - Exit code: 0
  - Duration: 6.95s
  - Recorded: 2026-08-27T03:10:25+08:00
  - Output evidence: sha256:962fe07d2d4be57880872fc85af0fe257dac53704d1e48e7bc765b99964ea4ab (100 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T03:10:26+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `docs/specs/compact-local-config-workflow.md`, `docs/ai/context-packs/compact-local-config-workflow.md`, `skills/repo-context-ledger/SKILL.md`, and generated Agent adapters.

Reason: The public commands, persistence boundary, recovery behavior, and Agent routing policy are stable cross-session contracts that must remain discoverable without reading the runtime implementation.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `dd283c73130ec672e183fe8018c4b19217efdf52`
- Current commit: `dd283c73130ec672e183fe8018c4b19217efdf52`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `.context-ledger/templates/handoff-template.md`
  - `AGENTS.md`
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-packs/compact-local-config-workflow.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/compact-local-config-workflow.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/assets/handoff-template.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_doctor.py`
  - `tests/test_ledger.py`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
