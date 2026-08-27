# Workflow Planning context pack

Status: current
Feature: workflow-planning
Aliases: workflow plan | task planning | 工作流规划 | 任务判断
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 25b94983f63d44d3f7134c37621957d531ad88f2
Base branch: main
Base commit: 0d7e1f289e726edc4ae2b621361f89c621de5623
Last refreshed: 2026-08-27T18:55:04+08:00

## Purpose

Routes a natural-language coding request through one deterministic, read-only preflight before an Agent loads broad context or mutates task state. It returns a stable workflow mode, reasons, confidence, confirmation requirement, and one structured next action while keeping later code inspection open-ended.

## Load order

- Read first: Read `docs/specs/workflow-planning.md`, then the `build_workflow_plan` and `workflow_plan_command` code paths.
- Read if needed: Read `tests/test_workflow_plan.py`, the synthetic evaluation fixture, and the golden schema when changing classification, ambiguity, or public fields; read session routing only when resume selection changes.
- Do not load by default: Do not open completed Change bodies, all Context Packs, verification implementation, or private drafts outside the selected owned session.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::build_workflow_plan` | Owns deterministic mode, confidence, reasons, confirmation, and next-action selection. |
| `src/repo_context_ledger/runtime.py.tmpl::workflow_plan_command` | Returns the standalone text/JSON Workflow Plan through context preflight. |
| `src/repo_context_ledger/runtime.py.tmpl::context_search` | Embeds the same plan in `context-bundle-v1`. |
| `src/repo_context_ledger/runtime.py.tmpl::start_change` | Rejects read-only/resume modes before creating private state. |
| `src/repo_context_ledger/runtime.py.tmpl::resolve_resumable_session` | Reuses the privacy-bounded session route for actual continuation. |
| `skills/repo-context-ledger/SKILL.md` | Makes `plan` the short Agent front door and sends detailed procedures to references. |
| `tests/test_workflow_plan.py` | Protects English/Chinese classification, resume selection/ambiguity, contract fields, and Skill budget. |

## Contracts and boundaries

- Invariants and contracts: `plan` is read-only, emits `workflow-plan-v1`, never executes `next_action`, and never exposes foreign private state. Required reads remain an initial route rather than a code-reading cap.
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

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:b5b0d9eba8bb211c07ba21e39e83ee8269ba598645a83872534bed4f3bdd7d7e`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:baf40f4ac0a9038f33d90975b07c5e7fdd581ab45561e8cf29e522b59954a95f`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:a54d09dbb14a7ca7b6368bb8ec957dfa5a4a4f4aafe06fc8ce507c97895384b6`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c49a692005ff85c62c4fc3ebb5617af4725c55bba3857a3413b5c4d8bba4e12a`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:61b308e7b737e2677cf0f4c8740ad281710bc6e33740098cee5e17beb2b36d48`
- `ARCHITECTURE.md` — `sha256:f100d252d793d5477d614f96f565fa43c1aebf0785a464c7bc996c853b0581f1`
- `COMPATIBILITY.md` — `sha256:3f488c7ba6fa8adc5ef2614ad8bed349cbc65067a2fa006cfb83fb52253df538`
- `MIGRATIONS.md` — `sha256:8ac48c4c34149cfa3452dab3c4758a3e86c0e942f20a22653aa183821001a961`
- `tests/test_workflow_plan.py` — `sha256:b5803f4d2fc05763d0bb94f02c4108d198eb4b742f3493bb87dce62c26a33283`
- `tests/fixtures/workflow-plan-eval-v1.json` — `sha256:0f4ccb3f8c666bd6576f76291d527d86bceeb1ec49fda5e2a39094bea1f1d78f`
- `tests/golden/workflow-plan-v1.json` — `sha256:9ed5dc04cc4afadbb651ff61ed387a6c77145fff7e85d2f846b6d3071d154802`
<!-- repo-context-ledger:pack-files:end -->
