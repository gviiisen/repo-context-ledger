# Compact local configuration workflow

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-09-05

## Purpose and behavior

Repo Context Ledger provides a compact lifecycle for small, tracked configuration changes whose effect is limited to the current worktree or machine. The Agent records scoped Git evidence and real verification while the runtime generates the semantic handoff sections, marks the record `Scope: worktree-local`, and avoids claiming that another checkout has the same local state.

For known low-risk repository corrections, `start --workflow small-fix` keeps the evidence-v1 contract with nine authoring prompts. The Agent explains the cause, Before/After, each meaningful change and why, boundaries, documentation rationale, and uncertainty. Only the documentation Updated list is generated from scoped evidence. One logical request, including its code, tests, and related docs, produces one completed record; meaningful findings and decisions accumulate in the same private draft before final publication. This is separate from local-config's fixed sanitized semantic rendering.

## Entry points and code map

| Path / symbol | Responsibility |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::start_change` | Records the task kind and reserves a private draft plus atomic publication target. |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Runs direct executable arguments, including a resolved reviewed preset, outside the write lock and enforces sensitive evidence persistence. |
| `src/repo_context_ledger/runtime.py.tmpl::complete_local_config_draft` | Generates the bounded worktree-local handoff from the user-visible result and scoped Git paths. |
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Renders evidence in memory, validates outside the write lock, and rechecks a bounded input signature before short atomic publication. |
| `src/repo_context_ledger/runtime.py.tmpl::complete_small_fix_draft` | Fills only the documentation Updated placeholder, requires explanations for new short publications, and retains manually authored reasoning. |
| `src/repo_context_ledger/runtime.py.tmpl::small_fix_explanation_errors` | Rejects path-only records, missing exact changed-path references, and the former generated documentation rationale. |
| `src/repo_context_ledger/runtime.py.tmpl::labeled_value` | Reads inline fields without letting empty values borrow following lines, for LF and CRLF text. |
| `src/repo_context_ledger/runtime.py.tmpl::refresh_context_pack` | Separates optional reading references from fingerprint dependencies without automatically downgrading old tracked paths. |
| `src/repo_context_ledger/runtime.py.tmpl::doctor_legacy_workflow_findings` | Warns when unmanaged legacy active-handoff instructions compete with private sessions. |
| `skills/repo-context-ledger/SKILL.md` | Routes eligible Agent work through the compact path and prohibits nested shell retry loops. |

## Data flow and contracts

- Input: `start --kind local-config` receives a title and feature. `verify --sensitive` receives direct executable arguments, or `verify --preset <name>` selects a reviewed preset whose `sensitive` setting cannot be weakened. `finish` requires one or more repository-relative `--path` values; it accepts no free-form result text.
- Flow: The task remains a private session while configuration is edited and checked. Sensitive verification executes normally but replaces its persisted command with `<sensitive verification>`, suppresses captured output from the console and record, and stores only status, exit code, duration, and time. `finish` rejects paths not classified as `config`, requires the final recorded check to be a passing sensitive verification, validates each explicit path against Git dirt, renders a fixed-value-free semantic record in memory, applies the stable-spec exception, and performs long validation outside the lock. A short final lock rechecks the session, draft digest, and bounded input signature before atomic publication; derived summaries follow after the lock.
- Persistence / dependencies: Unfinished state remains below worktree Git metadata. The completed sanitized Change is Git-tracked because it records an operation and its evidence, but `Scope: worktree-local` prevents it from representing local values as portable repository truth. Configuration values never enter Ledger Markdown.
- Output: A successful compact finish produces one completed Change with no TODO placeholders, an explicit worktree-local scope, evidence paths, a sanitized verification entry, and `Specs: none`. A failed check or finish leaves the private draft available for correction.

The repository small-fix form preserves all evidence-v1 headings, managed checks, and spec/Coverage requirements; existing full drafts are not rewritten. Its auto evidence includes changed README and native instruction Markdown while leaving their Coverage classification non-production. In parallel sessions, evidence must still be explicit; broad or foreign dirty work is not automatically owned by one session.

New short publications carry `Record format: small-fix-explained-v1`. Their Code paths section requires substantive prose beyond a path list and exact repository-relative citations for all implementation evidence paths, or all evidence paths when none are implementation. `file.py::Symbol` remains supported. The generated documentation list is not a rationale; the Agent must provide Reason. Blank labeled fields cannot consume a following label or managed marker. Coupled files may share an explanation and refer to shared boundaries/checks without repeating them. These are structural checks, not proof of semantic accuracy or a complete list of changes within a file.

Completed records without the new marker retain their existing record-format contract; no historical body is rewritten. An older unfinished short draft must supply explanations before finish. If the task expands, set Workflow to ordinary-change and Detail to standard in the same draft while preserving its marker, decisions, and managed checks; finish still resolves its documentation placeholder. Checkpoint/resume preserve the body and executed failed attempts, and publication creates one final record. Failed validation preserves the original private draft for correction.

Optional `finish --dry-run` uses the same preparation and validation as publication and returns 0 ready or 2 invalid. It aggregates resolvable draft, verification, spec, and relevant Pack problems. Unsafe paths, inaccessible sessions, and missing scoped evidence remain early failures. Preview does not acquire a write lock, persist a cache, mutate a draft/spec, or reserve publication. Actual finish always revalidates its own inputs. Related-path checks read Pack metadata without computing unrelated fingerprint hashes.

`pack --reference` adds repository-local Reading references, not validity dependencies. They are checked for broken targets and overlap with tracked files; editing their contents alone does not stale this Pack or provide production Coverage. A `--file` dependency is never automatically demoted. Existing refresh-without-files preserves all dependencies; explicit replacement requires reviewing the complete file list and the Pack's facts.

## Boundaries and failure modes

- Invariants: Sensitive command arguments and captured output are neither displayed nor persisted; explicit evidence paths must be real Git configuration changes; the latest verification must pass; another task session is never paused, contacted, or absorbed; ordinary behavior changes reject compact finish evidence and retain the full lifecycle.
- Permissions / concurrency: The existing principal, session ID, epoch, bounded wait, and short-lock rules remain authoritative. Finish preparation is lock-free; the final compare-and-swap boundary fails closed if its private draft or bounded repository inputs changed. `finish --path` selects documentation evidence only and does not claim, lock, copy, or merge source files.
- Failure / recovery: A missing or non-config path, a non-sensitive or failed final verification, a stale epoch, or a handoff validation error returns a precise nonzero result and preserves the private draft. Doctor warnings are read-only and never delete legacy prose automatically.
- Non-goals: This workflow does not store secrets, synchronize machine configuration through Git, replace service-specific validation, hide real failed checks, or classify a source-code behavior change as local configuration merely to bypass documentation.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py -k local_config` for the compact public CLI and adapter policy. Run `python -m unittest discover -s tests -p test_doctor.py -k legacy_active_handoff` for legacy workflow diagnostics, and `python scripts/build_runtime.py --check` for generated-runtime parity.

Run `python -B -m unittest discover -s tests -p test_small_fix_closeout.py` for concise records, real verification, dry-run immutability and error aggregation, dependency/reference separation, continuation epochs, and principal/session isolation. `python benchmarks/small_fix_authoring_benchmark.py --iterations 3` measures fixture command overhead and authoring-field counts, not Agent thinking time or production latency.

## Related changes

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Preserve explanations in concise change records](../changes/2026/09/20260905163611-gviiisen-5e72f557a4-preserve-explanations-in-concise-change-records.md)
- [Reduce small-fix closeout and Pack maintenance overhead](../changes/2026/09/20260905155749-gviiisen-ba0012727a-reduce-small-fix-closeout-and-pack-maintenance-o.md)
- [Add safe verification presets](../changes/2026/08/20260827065951-gviiisen-6daa4a6c38-add-safe-verification-presets.md)
- [Accelerate small-task closeout](../changes/2026/08/20260827060627-gviiisen-2e52131353-accelerate-small-task-closeout.md)
- [Close compact workflow review gaps](../changes/2026/08/20260827031910-gviiisen-bb7acfb439-close-compact-workflow-review-gaps.md)
- [Reduce Ledger overhead for local configuration changes](../changes/2026/08/20260827025332-gviiisen-90a3dd7099-reduce-ledger-overhead-for-local-configuration-c.md)
<!-- repo-context-ledger:changes:end -->
