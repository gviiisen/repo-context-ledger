# Workflow Planning context pack

Status: current
Feature: workflow-planning
Aliases: workflow plan | task planning | 工作流规划 | 任务判断
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: cc673f18238af119ecfe5cf08ffc2b4b3fc698e8
Base branch: main
Base commit: cc673f18238af119ecfe5cf08ffc2b4b3fc698e8
Last refreshed: 2026-08-27T20:39:26+08:00

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

- Invariants and contracts: `plan` is read-only, emits `workflow-plan-v1`, never executes `next_action`, and never exposes foreign private state. Quantity words do not establish small scope; high-risk change signals veto `small-fix`; supplied tool identity propagates to executable guidance. Required reads remain an initial route rather than a code-reading cap.
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

- `src/repo_context_ledger/workflow.pyfrag` — `sha256:6aa6619ae6bed53008de3fa1b8320efd8b58bd16c69d66f682c51a558ffa92ba`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:703ce2da25b3f3455576ce0bbe2ef3e1307d076113de234b20fc8ac02f209603`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:81a8fb3f2c0e857b28f88b9a6d75e31e6d40e485835517d7c50c95296ff5ed44`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:b9dfc812d8554191ad300a6816092ff171d9062c76af51d5dfc6f13f4c6ba0f7`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c49a692005ff85c62c4fc3ebb5617af4725c55bba3857a3413b5c4d8bba4e12a`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:61b308e7b737e2677cf0f4c8740ad281710bc6e33740098cee5e17beb2b36d48`
- `ARCHITECTURE.md` — `sha256:bf31211631f032b07e11ae1da428b3eed5b025bc511534f8f1b7c1d7c0cd2285`
- `COMPATIBILITY.md` — `sha256:8d8836a2a0bd7f96e863309eead81a2044272c58212d7e6fde88303352b8525d`
- `MIGRATIONS.md` — `sha256:3883ad8ec72e7ddda2e05d04fef4c851083d85bb511667e70fe84cec7b72ab48`
- `tests/test_workflow_plan.py` — `sha256:92233e4c35291a02b612563bf3c63a39acef72d88f5ead2a9ad77bb339e0235f`
- `tests/fixtures/workflow-plan-eval-v1.json` — `sha256:42d475cff93b253bbe74a78f5cb1a3807f161d830c368b72adcad03513c38b7f`
- `tests/golden/workflow-plan-v1.json` — `sha256:9ed5dc04cc4afadbb651ff61ed387a6c77145fff7e85d2f846b6d3071d154802`
<!-- repo-context-ledger:pack-files:end -->
