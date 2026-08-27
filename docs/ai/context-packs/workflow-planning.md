# Workflow Planning context pack

Status: current
Feature: workflow-planning
Aliases: workflow plan | task planning | 工作流规划 | 任务判断
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 2c5ea2f81b7b8f8939ad274f44094a6b937faca5
Base branch: main
Base commit: 0d7e1f289e726edc4ae2b621361f89c621de5623
Last refreshed: 2026-08-27T19:19:45+08:00

## Purpose

Routes a natural-language coding request through one deterministic, read-only preflight before an Agent loads broad context or mutates task state. It returns a stable workflow mode, reasons, confidence, confirmation requirement, and one structured next action while keeping later code inspection open-ended.

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

- `src/repo_context_ledger/workflow.pyfrag` — `sha256:2f2418090cf30008b9d4f738696628be1bba89d2f97a238105a3b38dc5215bca`
- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:6552c343fb986f841042fae89716668ad7612165eaf594b7bb6f0bd8022e57aa`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:e4b8e16789bce7ba8e405f0069f0372dd0ff25fcbfd9dc805cb460b0fbe5a62a`
- `skills/repo-context-ledger/scripts/ledger.py` — `sha256:0bfead16d1f3312ac8a0eacbb907905be4159c123f85f96dab4bc7ed4e0c985a`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c49a692005ff85c62c4fc3ebb5617af4725c55bba3857a3413b5c4d8bba4e12a`
- `skills/repo-context-ledger/references/production-workflow.md` — `sha256:61b308e7b737e2677cf0f4c8740ad281710bc6e33740098cee5e17beb2b36d48`
- `ARCHITECTURE.md` — `sha256:7f87435665f8dadc0cc6896858d0fd0aef127cae3b27e049d9da991d2ae0e67c`
- `COMPATIBILITY.md` — `sha256:b5afe2c85b82ffa977be569d1ca666ad335bb3739b5607b9e061c15ea8026373`
- `MIGRATIONS.md` — `sha256:bcf00e3571a68fc8f8308977feec77af91cbf2b37ec21aa44403b00a4a2358fd`
- `tests/test_workflow_plan.py` — `sha256:b5803f4d2fc05763d0bb94f02c4108d198eb4b742f3493bb87dce62c26a33283`
- `tests/fixtures/workflow-plan-eval-v1.json` — `sha256:0f4ccb3f8c666bd6576f76291d527d86bceeb1ec49fda5e2a39094bea1f1d78f`
- `tests/golden/workflow-plan-v1.json` — `sha256:9ed5dc04cc4afadbb651ff61ed387a6c77145fff7e85d2f846b6d3071d154802`
<!-- repo-context-ledger:pack-files:end -->
