# Build continuation quality engine

Status: completed
Feature: continuation-quality
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827075252-gviiisen-c783c8332f
Session ID: 20260827075252-gviiisen-c783c8332f
Actor: gviiisen
Branch: feat/v0.8.0-continuation-quality
Started: 2026-08-27T07:52:52+08:00
Completed: 2026-08-27T08:11:59+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 45055d81262efa4ef1ec627ac22e578fb1be61d3
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/continuation-quality.md
Spec exception: none

## Intent

Ship v0.8.0 continuation quality after v0.7.3: evaluate real resume selection with synthetic data, generate a more actionable bounded Capsule, and route Chinese/English phrases plus explicit code symbols without introducing automatic task-state inference. Acceptance requires additive public contracts, deterministic privacy behavior, and passing runtime, evaluator, build, and Skill validation.

## Changed behavior

Before: owned-session continuation used feature/title/checkpoint/path token overlap and returned an unversioned flat Capsule. The existing six-case router corpus did not exercise private session selection, cross-language aliases, code symbols, foreign overlap, or Capsule guidance budgets.

After: Pack authors can maintain bounded aliases and explicit `path::Symbol` anchors; Pack and owned-session routing use them deterministically while foreign drafts remain unread. `context-bundle-v1` may now contain additive `resume-capsule-v2` guidance, and an eight-case synthetic continuation gate measures Top-1 selection, ambiguity, privacy, anchors, character budgets, and latency.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::parse_context_pack_metadata` | Loads disposable Pack routing metadata. | Added explicit aliases, code-map anchors, and bounded invariants without source scanning. |
| `src/repo_context_ledger/runtime.py.tmpl::score_context_pack`, `score_resume_session` | Selects a Pack and one accessible private task. | Added explainable exact alias and `path::Symbol` ranking shared by Pack/session routes. |
| `src/repo_context_ledger/runtime.py.tmpl::build_resume_capsule` | Builds private continuation guidance. | Added the compatible `resume-capsule-v2` structured route while retaining all prior Capsule fields. |
| `scripts/evaluate_continuation.py::evaluate` | Runs the release-quality continuation corpus. | Added production-scoring/Capsule evaluation over synthetic owned, ambiguous, foreign, multilingual, path, symbol, and no-match cases. |
| `skills/repo-context-ledger/SKILL.md` | Defines Agent behavior around routed context. | Requires explicit aliases/anchors and forbids inferred task progress, translation, diff, or symbols. |

## Boundaries and risks

- Invariant: The public envelope remains `context-bundle-v1`; old Capsule fields remain present; foreign private drafts are never read; Required reads remain a starting route rather than a code-reading cap.
- Failure / recovery: Missing aliases fall back to existing routing, stale Packs warn, near-equal owned sessions block, and the Capsule drops lower-priority guidance before exceeding its declared budget.
- Not changed: Repository/private-state schema stays v8. The runtime does not infer progress or diffs, discover symbols from source, generate translations, persist Capsule Markdown, auto-resume ambiguous work, or coordinate source files.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: failed
  - Exit code: 1
  - Duration: 0.08s
  - Recorded: 2026-08-27T08:08:03+08:00
  - Output evidence: sha256:abdc62d1372171445860a137fca3c03ff23520a7a84c7e274ff36091ee6b9bc5 (694 characters captured; content not persisted; failure=Traceback (most recent call last): | UnicodeDecodeError: 'gbk' codec can't decode byte 0x92 in position 2522: illegal multibyte sequence)
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T08:08:03+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -X utf8 <CODEX_HOME>\skills\.system\skill-creator\scripts\quick_validate.py skills\repo-context-ledger`
  - Status: passed
  - Exit code: 0
  - Duration: 0.06s
  - Recorded: 2026-08-27T08:08:20+08:00
  - Output evidence: sha256:db349825903d66adffea3ecf1bd8e1803043e8a71cf1a051235dabc5371f5bb0 (16 characters captured; content not persisted; last=Skill is valid!)
- Command: `python -m unittest discover -s tests -v`
  - Status: passed
  - Exit code: 0
  - Duration: 208.14s
  - Recorded: 2026-08-27T08:11:31+08:00
  - Output evidence: sha256:7dca7f5f213bb255bbd76396659815563bcd7fdea8cc4bef992907b43b0fe4a9 (18475 characters captured; content not persisted; last=OK)
- Command: `python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main`
  - Status: passed
  - Exit code: 0
  - Duration: 5.84s
  - Recorded: 2026-08-27T08:11:49+08:00
  - Output evidence: sha256:28aafb62394e95228fb5e773103d8b4d8613dae88bb749ef24a2a1332eeff076 (187 characters captured; content not persisted; last=Changed-scope Repo Context Ledger check passed.)
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `COMPATIBILITY.md`, `MIGRATIONS.md`, `docs/specs/continuation-quality.md`, `docs/specs/task-session-integrity.md`, `docs/specs/context-routing-performance.md`, affected Context Packs, and `skills/repo-context-ledger/SKILL.md`.

Reason: The release adds an optional Pack authoring field, an additive private Capsule schema, new routing semantics, explicit non-goals, and a public synthetic quality gate that users and automation need to understand.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `45055d81262efa4ef1ec627ac22e578fb1be61d3`
- Current commit: `45055d81262efa4ef1ec627ac22e578fb1be61d3`
- Changed paths:
  - `.context-ledger/ledger.py`
  - `COMPATIBILITY.md`
  - `MIGRATIONS.md`
  - `README.md`
  - `README.zh-CN.md`
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
  - `docs/specs/context-routing-performance.md`
  - `docs/specs/continuation-quality.md`
  - `docs/specs/task-session-integrity.md`
  - `scripts/evaluate_continuation.py`
  - `skills/repo-context-ledger/SKILL.md`
  - `skills/repo-context-ledger/assets/context-pack-template.md`
  - `skills/repo-context-ledger/scripts/ledger.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/fixtures/continuation-eval-v1.json`
  - `tests/test_continuation_evaluation.py`
  - `tests/test_ledger.py`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
