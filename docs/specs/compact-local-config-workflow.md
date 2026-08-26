# Compact local configuration workflow

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-27

## Purpose and behavior

Repo Context Ledger provides a compact lifecycle for small, tracked configuration changes whose effect is limited to the current worktree or machine. The Agent records scoped Git evidence and real verification while the runtime generates the semantic handoff sections, marks the record `Scope: worktree-local`, and avoids claiming that another checkout has the same local state.

## Entry points and code map

| Path / symbol | Responsibility |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::start_change` | Records the task kind and reserves a private draft plus atomic publication target. |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Runs direct executable arguments outside the write lock and enforces sensitive evidence persistence. |
| `src/repo_context_ledger/runtime.py.tmpl::complete_local_config_draft` | Generates the bounded worktree-local handoff from the user-visible result and scoped Git paths. |
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Renders evidence in memory, validates outside the write lock, and rechecks a bounded input signature before short atomic publication. |
| `src/repo_context_ledger/runtime.py.tmpl::doctor_legacy_workflow_findings` | Warns when unmanaged legacy active-handoff instructions compete with private sessions. |
| `skills/repo-context-ledger/SKILL.md` | Routes eligible Agent work through the compact path and prohibits nested shell retry loops. |

## Data flow and contracts

- Input: `start --kind local-config` receives a title and feature. `verify --sensitive` receives a direct executable and arguments. `finish` requires one or more repository-relative `--path` values; it accepts no free-form result text.
- Flow: The task remains a private session while configuration is edited and checked. Sensitive verification executes normally but replaces its persisted command with `<sensitive verification>`, suppresses captured output from the console and record, and stores only status, exit code, duration, and time. `finish` rejects paths not classified as `config`, requires the final recorded check to be a passing sensitive verification, validates each explicit path against Git dirt, renders a fixed-value-free semantic record in memory, applies the stable-spec exception, and performs long validation outside the lock. A short final lock rechecks the session, draft digest, and bounded input signature before atomic publication; derived summaries follow after the lock.
- Persistence / dependencies: Unfinished state remains below worktree Git metadata. The completed sanitized Change is Git-tracked because it records an operation and its evidence, but `Scope: worktree-local` prevents it from representing local values as portable repository truth. Configuration values never enter Ledger Markdown.
- Output: A successful compact finish produces one completed Change with no TODO placeholders, an explicit worktree-local scope, evidence paths, a sanitized verification entry, and `Specs: none`. A failed check or finish leaves the private draft available for correction.

## Boundaries and failure modes

- Invariants: Sensitive command arguments and captured output are neither displayed nor persisted; explicit evidence paths must be real Git configuration changes; the latest verification must pass; another task session is never paused, contacted, or absorbed; ordinary behavior changes reject compact finish evidence and retain the full lifecycle.
- Permissions / concurrency: The existing principal, session ID, epoch, bounded wait, and short-lock rules remain authoritative. Finish preparation is lock-free; the final compare-and-swap boundary fails closed if its private draft or bounded repository inputs changed. `finish --path` selects documentation evidence only and does not claim, lock, copy, or merge source files.
- Failure / recovery: A missing or non-config path, a non-sensitive or failed final verification, a stale epoch, or a handoff validation error returns a precise nonzero result and preserves the private draft. Doctor warnings are read-only and never delete legacy prose automatically.
- Non-goals: This workflow does not store secrets, synchronize machine configuration through Git, replace service-specific validation, hide real failed checks, or classify a source-code behavior change as local configuration merely to bypass documentation.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py -k local_config` for the compact public CLI and adapter policy. Run `python -m unittest discover -s tests -p test_doctor.py -k legacy_active_handoff` for legacy workflow diagnostics, and `python scripts/build_runtime.py --check` for generated-runtime parity.

## Related changes

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Accelerate small-task closeout](../changes/2026/08/20260827060627-gviiisen-2e52131353-accelerate-small-task-closeout.md)
- [Close compact workflow review gaps](../changes/2026/08/20260827031910-gviiisen-bb7acfb439-close-compact-workflow-review-gaps.md)
- [Reduce Ledger overhead for local configuration changes](../changes/2026/08/20260827025332-gviiisen-90a3dd7099-reduce-ledger-overhead-for-local-configuration-c.md)
<!-- repo-context-ledger:changes:end -->
