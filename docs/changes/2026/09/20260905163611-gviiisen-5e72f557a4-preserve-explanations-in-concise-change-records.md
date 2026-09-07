# Preserve explanations in concise change records

Status: completed
Feature: compact-local-config-workflow
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260905163611-gviiisen-5e72f557a4
Session ID: 20260905163611-gviiisen-5e72f557a4
Actor: gviiisen
Branch: feat/small-fix-closeout
Started: 2026-09-05T16:36:11+08:00
Completed: 2026-09-05T17:00:34+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 1a0f4bf5e0c8199efdd4930435270406a1d95907
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/compact-local-config-workflow.md
Spec exception: none

## Intent

Preserve meaningful change explanations while reducing repetitive closeout work. One bounded request should archive once without losing its actual changes, rationale, boundaries, decisions, or useful failed attempts. Accept only explained new short records, preserve older history, and prove that continuation keeps the same draft and final record.

## Changed behavior

Before: The local seven-prompt candidate generated a code-path list and a generic documentation reason. It kept structural evidence but could replace the explanation of what changed and why with mechanically derived text. Blank inline values could also accidentally consume a following line during validation.

After: New short drafts have nine authoring prompts, retain Agent-authored change explanations and documentation rationale, and generate only the documentation Updated list. The new format marker requires exact evidence-path references and prose beyond a path list. Meaningful findings stay in the same private draft; scope growth expands that draft instead of discarding its notes. Inline values remain on their own line for LF and CRLF records.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::small_fix_draft` | Generates new short-form drafts. | Replaces seven automatic-heavy prompts with nine explained prompts and an additive small-fix-explained-v1 marker. |
| `src/repo_context_ledger/runtime.py.tmpl::complete_small_fix_draft` | Prepares a short publication in memory. | Fills only Updated, retains authored explanations and Reason, and requires older unfinished short forms to supply missing explanations. |
| `src/repo_context_ledger/runtime.py.tmpl::small_fix_explanation_errors` | Adds deterministic record-format checks. | Rejects path-only prose, missing exact implementation evidence references, ambiguous basename-only references, and the former generated rationale. |
| `src/repo_context_ledger/runtime.py.tmpl::labeled_value` | Parses inline semantic fields. | Stops blank values from borrowing the following label, heading, or managed marker without breaking CRLF records. |
| `src/repo_context_ledger/runtime.py.tmpl::finish_change` | Validates and publishes the selected task. | Completes explained-form placeholders even after expanding the same draft to ordinary-change, retaining the marker and existing checks. |
| `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/writing-quality.md`, `skills/repo-context-ledger/references/production-workflow.md` | Direct Agent authoring and continuation. | Require milestone reasoning in the same private draft, per-change explanation, shared boundary reuse, and diff-to-record review without new mandatory commands. |
| `tests/test_small_fix_closeout.py` | Exercises runtime boundaries in temporary Git fixtures. | Adds six cases for missing explanations, coupled file references and expansion, checkpoint/resume preservation, old-format compatibility, Chinese prose, and blank LF/CRLF fields. |
| `benchmarks/closeout_workflow_benchmark.py`, `benchmarks/small_fix_authoring_benchmark.py` | Simulate direct-argv verification and real publication. | Fill the explanation-preserving short form; the updated public benchmark reports nine prompts and explicitly excludes Agent investigation/composition time. |
| `skills/repo-context-ledger/scripts/ledger.py`, `.context-ledger/ledger.py`, `AGENTS.md` | Distribute runtime and generated instructions. | Rebuilt from canonical source and synchronized adapters without installing a global Skill or changing another project. |

## Boundaries and risks

- Invariant: Archive one bounded request once while preserving its meaningful changes and evidence; never attribute another task's dirty paths or rewrite completed history. Structural checks do not establish business correctness or full semantic completeness.
- Failure / recovery: Path-only explanations, missing citations, blank rationale, or a failed gate leave the original private draft intact. Preserve useful failures and decisions through checkpoint/resume; expand the same draft when boundaries grow rather than deleting evidence to fit a short form.
- Not changed: No event log, model call, extra mandatory CLI step, source-file lock, worktree copy, cross-task message, installation, version bump, Git commit, remote push, or production-project change is introduced. Existing ordinary-form, spec, Coverage, ownership, and short-lock requirements remain in place.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python -B -m unittest discover -s tests -p test_*.py`
  - Status: failed
  - Exit code: 1
  - Duration: 328.59s
  - Recorded: 2026-09-05T16:50:28+08:00
  - Output evidence: sha256:729ac0c2d57d4d7e8dbf9e929ea248a8c5dc725f76f400a3eb31deacd2d77bfc (4979 characters captured; content not persisted; failure=FAIL: <redacted-token> (test_small_fix_closeout.SmallFixCloseoutTests.<redacted-token>) | Traceback (most recent call last): | self.assertIn("Documentation updates requires a substantive Reason: value.", | AssertionError: 'Documentation updates requires a substantive Reason: value.' not found in ['Handoff Language must resolve to en or zh-CN; replace auto before completion.', 'Handoff Detail must be concise, standard, or detailed.', 'Handoff Changed behavior requires a substantive Before: value.', 'Handoff Changed behavior requires a substantive After: value.', 'Handoff Boundaries and risks requires a substantive Invariant: value.', 'Handoff Boundaries and risks requires a substantive Failure / recovery: value.', 'Handoff Boundaries and risks requires a substantive Not changed: value.', 'H…)
- Command: `python benchmarks/small_fix_authoring_benchmark.py --iterations 3`
  - Status: passed
  - Exit code: 0
  - Duration: 26.33s
  - Recorded: 2026-09-05T16:55:30+08:00
  - Output evidence: sha256:220b777ae20b79df7e0e03d19688319d675dc60a3486bae3b179adb4851544cc (1564 characters captured; content not persisted; last=})
- Command: `python benchmarks/closeout_workflow_benchmark.py --iterations 1 --verification-delay 0.1`
  - Status: passed
  - Exit code: 0
  - Duration: 12.66s
  - Recorded: 2026-09-05T16:57:28+08:00
  - Output evidence: sha256:b9fdfbe04de0bbab0acee46eee818865d2d6785592df97a292e2b809c609d922 (1275 characters captured; content not persisted; last=})
- Command: `python -B -m unittest discover -s tests -p test_*.py`
  - Status: passed
  - Exit code: 0
  - Duration: 288.14s
  - Recorded: 2026-09-05T16:57:44+08:00
  - Output evidence: sha256:04c5fdb6abcdd290065a6c87dd4475847f3e0019216f808d8675925e820da5a6 (3616 characters captured; content not persisted; last=OK (skipped=4))
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 10.20s
  - Recorded: 2026-09-05T17:00:03+08:00
  - Output evidence: sha256:9664f5f5547b693ec7fa5bdd0e0890c57c1e3226b2ca84a0f8828fb6ec21d024 (188 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `AGENTS.md`, `skills/repo-context-ledger/SKILL.md`, `skills/repo-context-ledger/references/production-workflow.md`, `skills/repo-context-ledger/references/writing-quality.md`, `.context-ledger/writing-quality.md`, `docs/specs/compact-local-config-workflow.md`, `docs/ai/context-packs/compact-local-config-workflow.md`, `benchmarks/README.md`, and fingerprints in the other affected current Packs.

Reason: The prior local prose promised automatic path/rationale completion and seven prompts, which no longer describes the explained form. Replace those claims with the actual nine authoring prompts, continuation and expansion behavior, legacy compatibility, and limits of deterministic checks. Refresh existing dependency fingerprints without removing dependencies; keep completed records and feature-branch derived indexes unchanged.

## Open questions

Machine checks cannot prove each business claim or detect every omitted behavior within a cited file; the Agent must compare the full relevant diff with its explanation. Windows regression ran 152 tests with four POSIX-only skips; it does not substitute for running those cases on Unix. Benchmark timings are temporary-fixture command costs under concurrent test load, not measured human/Agent authoring savings.

## Decisions and useful failures

The seven-prompt candidate was rejected: file paths and generic evidence-derived prose cannot replace an explanation or documentation rationale. Keep nine prompts, allow coupled files to share a paragraph and shared boundary/verification sections, and avoid arbitrary limits on meaningful change items.

The first full regression failed because an empty Reason field consumed the following managed evidence marker. The field parser used whitespace matching that crossed line boundaries. A bounded inline parser and LF/CRLF regression cases corrected that behavior; the later complete suite passed. Both verification attempts remain in this record rather than presenting only the final success.

Completed records without the new short-form marker remain historical evidence; require explanations only when publishing older unfinished short drafts. Expanding a short draft retains its marker and evidence, so the same-session publication still resolves its Updated placeholder.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `1a0f4bf5e0c8199efdd4930435270406a1d95907`
- Current commit: `1a0f4bf5e0c8199efdd4930435270406a1d95907`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `.context-ledger/writing-quality.md`
  - `AGENTS.md`
  - `README.md`
  - `README.zh-CN.md`
  - `benchmarks/README.md`
  - `benchmarks/closeout_workflow_benchmark.py`
  - `benchmarks/small_fix_authoring_benchmark.py`
  - `docs/ai/context-packs/compact-local-config-workflow.md`
  - `docs/ai/context-packs/context-routing-performance.md`
  - `docs/ai/context-packs/continuation-quality.md`
  - `docs/ai/context-packs/contract-stability.md`
  - `docs/ai/context-packs/coverage-integrity.md`
  - `docs/ai/context-packs/native-context-bridge.md`
  - `docs/ai/context-packs/pack-health-doctor.md`
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/ai/context-packs/task-session-integrity.md`
  - `docs/ai/context-packs/verification-presets.md`
  - `docs/ai/context-packs/workflow-planning.md`
  - `docs/specs/compact-local-config-workflow.md`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/references/production-workflow.md`
  - `skills/repo-context-ledger/references/writing-quality.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_small_fix_closeout.py`
<!-- repo-context-ledger:evidence:end -->
