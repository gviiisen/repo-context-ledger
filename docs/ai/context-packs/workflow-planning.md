# Workflow Planning context pack

Status: current
Feature: workflow-planning
Aliases: workflow plan | task planning | 工作流规划 | 任务判断
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 4800d58e9bde70c8f0b55a9afe0f6e7df90480d2
Base branch: main
Base commit: cc673f18238af119ecfe5cf08ffc2b4b3fc698e8
Last refreshed: 2026-08-27T21:54:20+08:00

## Purpose

Routes a natural-language coding request through one deterministic, read-only preflight before an Agent loads broad context or mutates task state. It conservatively recognizes only explicit low-risk small fixes, preserves the calling tool in executable guidance, and returns a stable workflow mode, reasons, confidence, confirmation requirement, and one structured next action while keeping later code inspection open-ended.

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
| `skills/repo-context-ledger/SKILL.md` | Makes `plan` the short Agent front door and sends detailed procedures to references. |
| `tests/test_workflow_plan.py` | Protects English/Chinese classification, resume selection/ambiguity, contract fields, and Skill budget. |

## Contracts and boundaries

- Invariants and contracts: `plan` is read-only, emits `workflow-plan-v1`, never executes `next_action`, and never exposes foreign private state. Quantity and one-line wording do not independently establish small scope; one-line is auxiliary only for named low-risk documentation/comment/copy/text/example targets. Supplied tool identity propagates to executable guidance.
- Failure / recovery: uncertain or ambiguous input returns `requires_confirmation=true`, `next_action.kind=clarify`, and an empty argv array. `start --workflow readonly|resume` fails before session creation.
- Non-goals: no LLM classification, semantic diff-size inference, automatic start/resume, foreign session adoption, or claim that routed documentation replaces code verification.

## Verification

`python -m unittest discover -s tests -p test_workflow_plan.py -v` checks classification, ambiguity, integration, and schema shape. `python -m unittest discover -s tests -p test_contract_stability.py -v` protects additive public compatibility. The Skill validator and runtime build check protect progressive disclosure and generated outputs.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Workflow Planning](../../specs/workflow-planning.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/workflow.pyfrag` — `sha256:6099dec2fe65490a333c98ce9b61b363c56fc1012281ca83398c48088a33cc09`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:aabb91b17f8a9bae7d42d2932d20eeb5b37819e6c358a0b517c253d71c8c6a39`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:81a8fb3f2c0e857b28f88b9a6d75e31e6d40e485835517d7c50c95296ff5ed44`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:f00aafdd16ed109963ed90b5bc4d77b2fc2b0c4f230a09e4cba7e52b8fa45d49`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c49a692005ff85c62c4fc3ebb5617af4725c55bba3857a3413b5c4d8bba4e12a`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:61b308e7b737e2677cf0f4c8740ad281710bc6e33740098cee5e17beb2b36d48`
- `ARCHITECTURE.md` — `sha256:b06788c0dc2e1ae5bf2f5292d3fda91e3876ebc2395976655f29dab5aeafcdd5`
- `COMPATIBILITY.md` — `sha256:5688484d4886d09f7aa34fa064eff2c562fd88ac16c5b85da46525e0efe398d3`
- `MIGRATIONS.md` — `sha256:3883ad8ec72e7ddda2e05d04fef4c851083d85bb511667e70fe84cec7b72ab48`
- `tests/test_workflow_plan.py` — `sha256:92233e4c35291a02b612563bf3c63a39acef72d88f5ead2a9ad77bb339e0235f`
- `tests/fixtures/workflow-plan-eval-v1.json` — `sha256:6fbee688d02ab3801129c8e1f6da918a9b68981170eddc2d8ff9a64506f565bb`
- `tests/golden/workflow-plan-v1.json` — `sha256:9ed5dc04cc4afadbb651ff61ed387a6c77145fff7e85d2f846b6d3071d154802`
<!-- repo-context-ledger:pack-files:end -->
