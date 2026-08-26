# Add safe verification presets

Status: completed
Feature: verification-presets
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827065951-gviiisen-6daa4a6c38
Session ID: 20260827065951-gviiisen-6daa4a6c38
Actor: gviiisen
Branch: feat/v0.7.3-verification-presets
Started: 2026-08-27T06:59:51+08:00
Completed: 2026-08-27T07:20:52+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: e9589ed8c0474590bc6266d9d92424ac1b5050cb
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/verification-presets.md, docs/specs/compact-local-config-workflow.md, docs/specs/task-session-integrity.md, docs/specs/contract-stability.md
Spec exception: none

## Intent

Add repository-owned verification templates that Agents can execute by name without reconstructing long shell commands. The accepted result is a portable, reviewable argv contract that eliminates nested PowerShell quoting retries while preserving actual subprocess execution, private task evidence, sensitivity, and platform boundaries.

## Changed behavior

Before: Every verification required an Agent to assemble executable arguments at run time. Repeated or Windows-specific checks could be rebuilt differently across sessions, and a malformed nested PowerShell command could fail before the intended program ran.

After: Maintainers may define named `verification.presets` in repository configuration and Agents may explicitly run `verify --preset <name>`. The runtime validates the complete definition, resolves a repository-relative working directory and current platform, executes the stored argv without a shell, and records the preset identity with the normal verification result.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::normalize_verification_config` | Validates Git-tracked repository configuration. | Added bounded preset names, argv, cwd, timeout, sensitivity and platform normalization plus unsafe shell-wrapper rejection. |
| `src/repo_context_ledger/runtime.py.tmpl::resolve_verification_preset` | Resolves one explicitly selected check before execution. | Added fail-closed name, platform and working-directory checks and returns the direct subprocess contract. |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Executes a check outside the repository write lock and appends session evidence. | Added explicit working directory and preset metadata while retaining `shell=False`, redaction, sensitivity and concurrent short-lock writes. |
| `src/repo_context_ledger/runtime.py.tmpl::run_main` | Dispatches CLI verification modes. | Made preset, direct argv and not-run evidence mutually exclusive and defined timeout/sensitivity override precedence. |
| `.context-ledger/config.json::verification.presets` | Dogfoods stable repository checks. | Added focused, full-suite and generated-runtime presets as real cross-platform examples. |
| `skills/repo-context-ledger/references/verification-presets.md` | Guides Agents and maintainers without enlarging unrelated initial context. | Added safe Python, Go and PowerShell `-File` examples and the trust/non-goal boundaries. |
| `tests/test_ledger.py::LedgerFlowTests` | Exercises end-to-end standalone runtime behavior. | Added preset execution, default normalization, sensitive persistence, platform isolation, selection ambiguity, repository escape and unsafe shell rejection coverage. |

## Boundaries and risks

- Invariant: A preset is never run implicitly, never invokes a shell, never escapes the repository working directory, and cannot weaken `sensitive: true`; existing direct argv verification remains compatible.
- Failure / recovery: Malformed definitions, unknown names, unsupported platforms and missing working directories fail before execution. A missing executable or failing check produces the ordinary recoverable failed-verification record and leaves the private handoff active.
- Not changed: The runtime does not manage environment variables or secrets, infer the correct suite, replace project scripts or CI, or automatically execute all configured presets.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_ledger.py -k verification_preset -v`
  - Status: passed
  - Preset: `verification-presets-focused`
  - Working directory: `.`
  - Exit code: 0
  - Duration: 6.36s
  - Recorded: 2026-08-27T07:10:29+08:00
  - Output evidence: sha256:5351af860b1193a1701619bc03005de9ce382bb7cceba43237f6272155c87771 (959 characters captured; content not persisted; last=OK)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py <REPO_ROOT>\skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T07:12:17+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Preset: `runtime-build-check`
  - Working directory: `.`
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T07:12:17+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -B -m unittest discover -s tests -v`
  - Status: failed
  - Preset: `unit-full`
  - Working directory: `.`
  - Exit code: 1
  - Duration: 199.94s
  - Recorded: 2026-08-27T07:15:37+08:00
  - Output evidence: sha256:3a0f5b4edaeddd24b78570351c1e1e5ecfc64829444d954291af2887eebea4c6 (24412 characters captured; content not persisted; failure=<redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) ... FAIL | FAIL: <redacted-token> (test_ledger.LedgerFlowTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("skip context/focus and a separate evidence command", rules) | AssertionError: 'skip context/focus and a separate evidence command' not found in '# Agent instructions\n\n<!-- repo-context-ledger:rules:start -->\n## Repository context ledger\n\nChoose the shortest applicable path. Read-only work uses `context` only when routing is needed and never starts a session. A small worktree-local configuration change uses `status` �� `start --kind local-config --language <en|zh-CN>` �� `verify --sensitive -- <direct executable and arguments>` �� `finish --path <changed-config>`. A single-session small fix…)
- Command: `python -B -m unittest discover -s tests -p test_ledger.py -k generated_agent_rules -v`
  - Status: passed
  - Exit code: 0
  - Duration: 0.75s
  - Recorded: 2026-08-27T07:16:16+08:00
  - Output evidence: sha256:792361863f424f0f2d711bb128a5add2cdfc0b9d807d7598471771b2544d531a (276 characters captured; content not persisted; last=OK)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Preset: `runtime-build-check`
  - Working directory: `.`
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T07:16:23+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -B -m unittest discover -s tests -v`
  - Status: passed
  - Preset: `unit-full`
  - Working directory: `.`
  - Exit code: 0
  - Duration: 205.77s
  - Recorded: 2026-08-27T07:19:49+08:00
  - Output evidence: sha256:d8199dad58b41cdbea5c406380092257840dfe69546234aa5540db21877555a9 (18096 characters captured; content not persisted; last=OK)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `COMPATIBILITY.md`, `MIGRATIONS.md`, `docs/specs/verification-presets.md`, `docs/specs/compact-local-config-workflow.md`, `docs/specs/task-session-integrity.md`, `docs/specs/contract-stability.md`, `docs/ai/context-packs/verification-presets.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/verification-presets.md`, and `skills/repo-context-ledger/references/production-workflow.md`.

Reason: The new Git-tracked configuration and CLI selection contract affects maintainers, Agents, migrations, compatibility, task evidence, Windows command guidance, and future code navigation.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `e9589ed8c0474590bc6266d9d92424ac1b5050cb`
- Current commit: `e9589ed8c0474590bc6266d9d92424ac1b5050cb`
- Changed paths:
  - `COMPATIBILITY.md`
  - `MIGRATIONS.md`
  - `docs/ai/context-packs/compact-local-config-workflow.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/ai/context-packs/verification-presets.md`
  - `docs/specs/compact-local-config-workflow.md`
  - `docs/specs/contract-stability.md`
  - `docs/specs/task-session-integrity.md`
  - `docs/specs/verification-presets.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/references/verification-presets.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_ledger.py`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
