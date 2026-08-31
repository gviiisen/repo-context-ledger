# Align Skill UI metadata with ledger-first positioning

Status: completed
Feature: product-positioning
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260831183057-gviiisen-8ccc27959a
Session ID: 20260831183057-gviiisen-8ccc27959a
Actor: gviiisen
Branch: docs/feature-ledger-positioning
Started: 2026-08-31T18:30:57+08:00
Completed: 2026-08-31T18:32:13+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Dirty paths: none
Resume summary:
Next step:
Specs: none
Spec exception: This changes Skill UI discovery copy, not a stable runtime behavior contract.

## Intent

Keep the Codex-facing Skill metadata consistent with the ledger-first product positioning introduced in the public README and SKILL.md entry point.

## Changed behavior

Before: The Skill UI described Repo Context Ledger only as a verified-context bridge with private drafts, leaving functional change recording out of the first impression.

After: The short description leads with feature change recording and the default prompt asks the Agent to preserve the current feature change as verified knowledge for future windows and tools.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `skills/repo-context-ledger/agents/openai.yaml` | Defines the Skill's Codex-facing display metadata and default invocation prompt. | Aligned the short description and default prompt with the feature-change-ledger-first positioning. |

## Boundaries and risks

- Invariant: The Skill remains implicitly discoverable and retains the same display name.
- Failure / recovery: Metadata-only wording can be reverted without changing runtime or repository data.
- Not changed: Invocation policy, dependencies, runtime behavior, schemas, and lifecycle commands are unchanged.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py <REPO_ROOT>\skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.09s
  - Recorded: 2026-08-31T18:31:49+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `skills/repo-context-ledger/agents/openai.yaml`.

Reason: This is the UI-facing Skill metadata that users and Agents see before loading the full instructions.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `68c3b0cb9de9d1f975f847046d9db2b883fef00f`
- Current commit: `68c3b0cb9de9d1f975f847046d9db2b883fef00f`
- Changed paths:
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/changes/2026/08/20260831182446-gviiisen-8decd6bb1b-center-product-messaging-on-the-feature-change-l.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/agents/openai.yaml`
<!-- repo-context-ledger:evidence:end -->
