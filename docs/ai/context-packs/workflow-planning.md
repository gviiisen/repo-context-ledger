# Workflow Planning context pack

Status: current
Feature: workflow-planning
Aliases: workflow plan | task planning | 工作流规划 | 任务判断
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 1a0f4bf5e0c8199efdd4930435270406a1d95907
Base branch: main
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Last refreshed: 2026-09-08T00:02:31+08:00

## Purpose

Routes a natural-language coding request through a deterministic, read-only preflight when task identity or required background is missing. The Skill first asks the Agent to judge new facts/effects from loaded context, so a routine follow-up or known active task does not restart routing. Actual routing still conservatively recognizes only explicit low-risk small fixes, preserves tool identity, and returns the existing stable plan contract; there is no new semantic-deduplication engine.

## Load order

- Read first: Read `docs/specs/workflow-planning.md`, then `src/repo_context_ledger/workflow.pyfrag` and the context integration call sites.
- Read if needed: Read `tests/test_workflow_plan.py`, the synthetic evaluation fixture, and the golden schema when changing classification, ambiguity, or public fields; read session routing only when resume selection changes.
- Do not load by default: Do not open completed Change bodies, all Context Packs, verification implementation, or private drafts outside the selected owned session.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `src/repo_context_ledger/workflow.pyfrag::build_workflow_plan` | Owns deterministic mode, confidence, reasons, confirmation, and next-action selection. |
| `src/repo_context_ledger/workflow.pyfrag::workflow_plan_command` | Returns the standalone text/JSON Workflow Plan through context preflight. |
| `src/repo_context_ledger/runtime.py.tmpl::context_search` | Embeds the same plan in `context-bundle-v1`. |
| `src/repo_context_ledger/runtime.py.tmpl::start_change` | Rejects read-only/resume modes before creating private state. |
| `src/repo_context_ledger/runtime.py.tmpl::resolve_resumable_session` | Reuses the privacy-bounded session route for actual continuation. |
| `skills/repo-context-ledger/SKILL.md` | Puts Agent delta judgment before tool calls, reuses unfinished task context, and routes only missing information through plan. |
| `src/repo_context_ledger/runtime.py.tmpl::context_plan_policy`, `resume_plan_policy`, `managed_rules` | Make generated Agent entry points conditional and distinguish same-window continuation from actual resume. |
| `tests/test_workflow_plan.py` | Protects English/Chinese classification, resume selection/ambiguity, contract fields, and Skill budget. |

## Contracts and boundaries

- Invariants and contracts: `plan` is read-only, emits `workflow-plan-v1`, never executes `next_action`, and never exposes foreign private state. Quantity and one-line wording do not independently establish small scope; one-line is auxiliary only for named low-risk documentation/comment/copy/text/example targets. Supplied tool identity propagates to executable guidance.
- Failure / recovery: uncertain or ambiguous input returns `requires_confirmation=true`, `next_action.kind=clarify`, and an empty argv array. `start --workflow readonly|resume` fails before session creation.
- Non-goals: no LLM classification, semantic diff-size inference, automatic start/resume, foreign session adoption, or claim that routed documentation replaces code verification.

## Verification

`python -m unittest discover -s tests -p test_workflow_plan.py -v` checks classification, ambiguity, integration, and schema shape. `python -m unittest discover -s tests -p test_contract_stability.py -v` protects additive public compatibility. The Skill validator and runtime build check protect progressive disclosure and generated outputs.

`tests/test_small_fix_closeout.py` also exercises consecutive real edits in one session without resume, preservation of earlier reasoning/checks, one publication, rejection of writes to the completed task, and a distinct later task. It validates the lifecycle's support for the guidance, not an LLM's ability to recognize every repeat.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Workflow Planning](../../specs/workflow-planning.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/workflow.pyfrag` — `sha256:6099dec2fe65490a333c98ce9b61b363c56fc1012281ca83398c48088a33cc09`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:c01e9bee65a2e168ee22d0a8e1fe5b1b7686f61c7cd4320d17cbfb25f1c6ccf4`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:1d78f4e2545641efce1a3ef6db9948769ec39cfd530d795a4727a3c7214dcd7f`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:ee85dce70f9f4f43abd9369b6ca7bb45e2fdbfe0513a89e2a58ebea2e8b5d135`
- `skills/repo-context-ledger/SKILL.md` — `sha256:5ded6a55fcd32c9cd6ae07eef809b7c33a9c158fdc13a26b70752eb3288a3e69`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:e9b3f1fbf7b1e5f25486f17d1d4fb6756f7b90d408c108be514c1b5c882cc6e7`
- `ARCHITECTURE.md` — `sha256:b06788c0dc2e1ae5bf2f5292d3fda91e3876ebc2395976655f29dab5aeafcdd5`
- `COMPATIBILITY.md` — `sha256:e25fd7bd143072cca9bf88f008b023a23d360496717cbd6c2c8ca1096e309876`
- `MIGRATIONS.md` — `sha256:e4021bd7e3de33818069f3339cb143e5233a468d2178e8596a14aec14d959b04`
- `tests/test_workflow_plan.py` — `sha256:92233e4c35291a02b612563bf3c63a39acef72d88f5ead2a9ad77bb339e0235f`
- `tests/fixtures/workflow-plan-eval-v1.json` — `sha256:6fbee688d02ab3801129c8e1f6da918a9b68981170eddc2d8ff9a64506f565bb`
- `tests/golden/workflow-plan-v1.json` — `sha256:9ed5dc04cc4afadbb651ff61ed387a6c77145fff7e85d2f846b6d3071d154802`
<!-- repo-context-ledger:pack-files:end -->
