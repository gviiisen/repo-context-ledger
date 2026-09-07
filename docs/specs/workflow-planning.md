# Workflow Planning

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-09-07

## Purpose and behavior

Workflow Planning provides a deterministic, read-only route when an Agent lacks the task identity or necessary repository background. It classifies a request as `readonly`, `small-fix`, `ordinary-change`, or `resume`, explains the observable signals, and returns one structured `next_action`. Automatic classification never mutates repository or private state.

Before invoking that route, the Agent judges the new delta from already loaded conversation and inspected facts. Routine questions, requested rechecks and existing operations with sufficient context use ordinary tools without a new Ledger lifecycle. Related unfinished work keeps its known session/epoch and adds only new findings and changes; a same-window continue is not a handover. Similar work on a different behavior/input still needs investigation and recorded evidence, and new changes after publication use a new record rather than reopening history. Missing identity/background, a paused task, and a real window/tool handover use the existing bounded commands as needed. This adds no classifier command, protocol field, extra document, cross-task result cache, or model call inside ledger.py.

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `src/repo_context_ledger/workflow.pyfrag::build_workflow_plan` | Classifies explicit intent, accessible Resume Capsule state, and bounded request signals into one workflow contract. |
| `src/repo_context_ledger/workflow.pyfrag::workflow_plan_command` | Exposes the standalone `plan` text/JSON front door through the same context preflight. |
| `src/repo_context_ledger/runtime.py.tmpl::context_search` | Embeds the same `workflow-plan-v1` object inside `context-bundle-v1`. |
| `src/repo_context_ledger/runtime.py.tmpl::start_change` | Accepts only change workflows; `readonly` and `resume` fail before session creation. |
| `src/repo_context_ledger/runtime.py.tmpl::resolve_resumable_session` | Uses the same privacy-bounded owned-session router as context and plan. |
| `src/repo_context_ledger/runtime.py.tmpl::managed_rules`, `context_plan_policy`, `resume_plan_policy` | Align native Agent instructions with delta-first judgment, conditional routing, and same-window versus actual-handover behavior. |
| `tests/test_workflow_plan.py` | Protects classification, explicit intent, resume ambiguity, start rejection, schema shape, and Skill size. |
| `tests/fixtures/workflow-plan-eval-v1.json` | Provides synthetic English/Chinese task-intent cases without production data. |
| `tests/golden/workflow-plan-v1.json` | Pins required public fields, modes, and structured next-action shape. |

## Data flow and contracts

- Input: a human task query, optional explicit intent, calling Agent ID, optional baseline ref, current principal-private session metadata, and Git-tracked Pack metadata.
- Decision order: explicit `resume` or a uniquely accessible matching session; explicit non-auto intent; change plus a strong small-scope signal with no risk veto; change signal; read-only signal; otherwise low-confidence read-only clarification. Quantity-only words never establish small scope, and uncertain changes default to `ordinary-change`.
- Output: `workflow-plan-v1` with `mode`, `confidence`, `requires_confirmation`, deterministic reasons, selected feature/session when safe, a structured argv-array `next_action`, and non-mutation/privacy safety flags. When the caller supplies `--tool`, executable `start`, `resume`, and context actions preserve it in that array.
- Flow: `plan` runs the existing bounded context/session preflight, builds one Workflow Plan, and renders text or JSON without executing its next action. `context` embeds the same object in its additive `workflow` field. `resume --query` uses the same session route. `start --workflow` refuses read-only/resume modes before private state creation.
- Persistence / dependencies: the planner uses the existing Python standard-library runtime, Git-tracked Pack metadata, and current-principal private session index. It creates no cache, lock, draft, Capsule file, repository document, or continuation epoch; the only new persisted artifacts are the Git-tracked schema/evaluation fixtures maintained by this project.

## Boundaries and failure modes

- Invariants: planning is read-only; it never executes the next action, reads foreign private drafts, invents task progress, or limits later behavior-relevant code inspection. Structured argv arrays are guidance, not shell command strings. Automatic `small-fix` classification is fail-safe: typo, spelling, or comment-only scope may qualify directly; one-line wording qualifies only with an explicit low-risk documentation/comment/copy/text/example target. Code risk remains `ordinary-change` when scope is uncertain.
- Ambiguity: multiple near resume matches, explicit resume without an accessible match, or an unclassified auto query sets `requires_confirmation=true` and returns `next_action.kind=clarify` with an empty argv array.
- Privacy: foreign overlap may influence a bounded warning in context routing but cannot populate a session ID, Capsule, summary, evidence, verification, tool, or epoch.
- Permissions / concurrency: planning inherits existing principal-scoped session visibility and performs no write-lock operation. Concurrent plans may read the same Pack metadata safely; a returned session is still revalidated by `resume`, and only lifecycle commands may acquire mutation authority.
- Failure / recovery: unsupported repository/private schemas retain a versioned error response. Missing or ambiguous continuation state and unclear automatic intent produce a confirmation-required clarify action; recovery is to refine the user request or explicitly choose a permitted intent/session, then run the planner again.
- Compatibility: `workflow-plan-v1` is additive to `context-bundle-v1`; v0.6.2 schemas and exit classes remain unchanged. Existing `start`, `context`, and `resume` calls remain valid without new options.
- Non-goals: the planner does not use an LLM, infer semantic code size from a query, auto-start/auto-resume work, claim that Required reads are sufficient, or replace user clarification on low confidence.

Existing context is reusable, not automatically authoritative: new or uncertain callers, code, configuration, environment and safety boundaries require fresh inspection. Similar wording cannot authorize a side effect, skip a requested recheck, recycle an old pass as new managed evidence, or bypass a stale epoch. Runtime tests protect these lifecycle boundaries but cannot prove every model's semantic judgment follows the Skill.

## Verification

Run `python -m unittest discover -s tests -p test_workflow_plan.py -v`, `python -m unittest discover -s tests -p test_contract_stability.py -v`, the bilingual positive/negative evaluation corpus, the Skill validator, runtime build drift check, and the complete unit suite.

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Judge task deltas before invoking Ledger](../changes/2026/09/20260907230332-gviiisen-16c6b7fe8e-judge-task-deltas-before-invoking-ledger.md)
- [Harden v1.0.1 workflow and repository boundaries](../changes/2026/08/20260827202058-gviiisen-0e61ed5004-harden-v1-0-1-workflow-and-repository-boundaries.md)
- [Add deterministic Workflow Plan](../changes/2026/08/20260827183113-gviiisen-f737fa1ffb-add-deterministic-workflow-plan.md)
<!-- repo-context-ledger:changes:end -->
