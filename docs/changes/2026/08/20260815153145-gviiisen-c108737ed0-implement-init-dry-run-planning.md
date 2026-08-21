# Implement init dry-run planning

Status: completed
Feature: native-context-bridge
Quality profile: evidence-v1
Language: en
Detail: standard
Handoff ID: 20260815153145-gviiisen-c108737ed0
Session ID: 20260815153145-gviiisen-c108737ed0
Actor: gviiisen
Branch: agent/v0.5.7-init-dry-run
Started: 2026-08-15T15:31:45+08:00
Completed: 2026-08-15T15:50:46+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: bd61e06cff7a1374cf842d8850604b1ab9567107
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/native-context-bridge.md
Spec exception: none

## Intent

Ship v0.5.7 with a trustworthy `init --dry-run` preview so an Agent can inspect adoption impact before changing an existing repository. Acceptance requires the preview to leave repository and private Git state unchanged, describe the planned file and migration operations, and match the operations subsequently applied by real `init`.

## Changed behavior

Before: `init` parsed no preview flag and immediately created the runtime, templates, configuration, adapters, indexes, README blocks, manifest, and migrated workspace state under a write lock.

After: `init --dry-run` computes the same in-memory filesystem plan used by real `init`, prints create/update/delete/migration operations plus module and team summaries, and exits without acquiring the write lock or writing repository/private workspace files. Running `init` applies that exact plan atomically and preserves the existing initialization and migration results.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/scripts/ledger.py::InitPlan` | Represents final initialization file contents, deletions, directories, modes, and migration notes. | Added a read-through in-memory overlay, deterministic change classification, atomic application, and compact plan rendering shared by preview and apply. |
| `skills/repo-context-ledger/scripts/ledger.py::build_init_plan` | Builds repository runtime, documentation, adapters, derived files, and workspace-state migration. | Refactored initialization writes through the planning overlay and passed the normalized config into derived synchronization so planning never depends on an already-written config file. |
| `skills/repo-context-ledger/scripts/ledger.py::main` | Parses commands and chooses write-lock behavior. | Added `init --dry-run` and excluded preview from mutating-command locking while retaining the lock for real initialization. |
| `.context-ledger/ledger.py` | Repository-local distributable runtime mirror. | Synchronized the v0.5.7 runtime byte-for-byte with the canonical Skill script. |
| `tests/test_ledger.py` | Runtime behavior and migration regression suite. | Added byte-level read-only, preview/apply parity, idempotent preview, and legacy Git-state migration coverage; updated the manifest version expectation. |

## Boundaries and risks

- Invariant: Existing prose outside managed markers, custom documentation paths, mature history layouts, nested Git boundaries, and task-session recovery semantics remain governed by the same init logic for preview and apply.
- Failure / recovery: Planning raises the same validation or migration error as real initialization before any plan is applied; dry-run has no cleanup requirement because it creates neither files nor a write lock. Real apply retains atomic per-file replacement.
- Not changed: This version does not add `pack --from-session`, Pack lineage, Tool provenance, workflow modes, source-code locking, worktree creation, or cross-task coordination.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -m unittest discover -s tests -p test_ledger.py -k init_dry_run`
  - Status: failed
  - Exit code: 1
  - Duration: 1.14s
  - Recorded: 2026-08-15T15:38:08+08:00
  - Output evidence: sha256:43d9f8c5f1b47ef9d3bef1898ff85afdb36af2e536dc883e84698bdd2d8b3aa5 (2109 characters captured; content not persisted; failure=AssertionError: command returned 2, expected 0 | ledger.py: error: unrecognized arguments: --dry-run | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.fail( | AssertionError: command returned 2, expected 0 | ledger.py: error: unrecognized arguments: --dry-run | FAILED (failures=2))
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: failed
  - Exit code: 1
  - Duration: 102.55s
  - Recorded: 2026-08-15T15:44:39+08:00
  - Output evidence: sha256:ee57ea4b99d0843950046b25eda85704bbc49653bc30b7d6950f555d9496ad51 (2730 characters captured; content not persisted; failure=Traceback (most recent call last): | self.assertEqual("0.5.6", manifest["tool_version"]) | AssertionError: '0.5.6' != '0.5.7' | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("Removed obsolete generated change indexes: 1", result.stdout) | AssertionError: 'Removed obsolete generated change indexes: 1' not found in 'Repo Context Ledger init plan for <TEMP_DIR>\\<test-run>\nCREATE .context-ledger/config.json [configuration]\nCREATE .context-ledger/context-state.json [private workspace state]\nCREATE .context-ledger/ledger.py [runtime]\nCREATE .context-ledger/templates/context-pack-template.md [template]\nCREATE .context-ledger/templates/handoff-template.md [template]\nCREATE .cont…)
- Command: `python -m unittest discover -s tests -p test_ledger.py`
  - Status: passed
  - Exit code: 0
  - Duration: 129.16s
  - Recorded: 2026-08-15T15:49:13+08:00
  - Output evidence: sha256:5bdf70864fdb7b80176de8ddb6db03209fd5a57fada61df62a66fb3f056fe66c (282 characters captured; content not persisted; last=OK)
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: failed
  - Exit code: 1
  - Duration: 0.14s
  - Recorded: 2026-08-15T15:49:20+08:00
  - Output evidence: sha256:80296fc1bbf2c36740ec3883f05a20c4cbe942c24dd4c9148c5ed1a50e2971d7 (693 characters captured; content not persisted; failure=Traceback (most recent call last): | UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 2037: illegal multibyte sequence)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills/repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-15T15:49:30+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `skills/repo-context-ledger/SKILL.md`, `docs/specs/native-context-bridge.md`, `docs/ai/context-packs/native-context-bridge.md`, `docs/ai/context-packs/coverage-integrity.md`, and `docs/ai/context-packs/task-session-integrity.md`.

Reason: The release notes and tutorial explain safe preview usage, the Skill now previews adoption before applying it, and the stable spec plus Context Pack record the shared-plan and read-only contracts.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `bd61e06cff7a1374cf842d8850604b1ab9567107`
- Current commit: `bd61e06cff7a1374cf842d8850604b1ab9567107`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `README.md`
  - `README.zh-CN.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/specs/native-context-bridge.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `tests/test_ledger.py`
<!-- repo-context-ledger:evidence:end -->
