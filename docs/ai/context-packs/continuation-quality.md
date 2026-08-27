# Continuation Quality context pack

Status: current
Feature: continuation-quality
Aliases: 跨窗口续接 | cross-agent continuation | resume capsule
Quality profile: evidence-v1
Language: en
Detail: standard
Source commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Base branch: main
Base commit: 68c3b0cb9de9d1f975f847046d9db2b883fef00f
Last refreshed: 2026-08-28T00:07:38+08:00

## Purpose

Routes a short phrase from a fresh Agent window to one owned unfinished task and returns bounded continuation guidance. It uses explicit cross-language aliases and Pack code-map anchors alongside private checkpoint evidence; it never invents translations, scans source to guess symbols, or infers task progress.

## Load order

- Read first: `docs/specs/continuation-quality.md`, then the routing and Capsule functions in `src/repo_context_ledger/runtime.py.tmpl`.
- Read if needed: `scripts/evaluate_continuation.py` and `tests/fixtures/continuation-eval-v1.json` when selection, privacy, ambiguity, budget, or evaluation behavior changes.
- Do not load by default: completed Change bodies, README derivation, unrelated finish/coverage internals, or production repository data.

## Entry points and code map

| Path / symbol | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::pack_aliases`, `pack_code_anchors` | Parse explicit Pack vocabulary without inspecting source bodies. |
| `src/repo_context_ledger/runtime.py.tmpl::score_context_pack` | Ranks aliases and `path::Symbol` anchors while preserving feature/title/path behavior. |
| `src/repo_context_ledger/runtime.py.tmpl::score_resume_session` | Applies public Pack vocabulary to accessible private session routing. |
| `src/repo_context_ledger/runtime.py.tmpl::build_resume_capsule` | Builds additive, bounded `resume-capsule-v2` guidance. |
| `scripts/evaluate_continuation.py::evaluate` | Runs the synthetic continuation correctness and privacy gate. |

## Contracts and boundaries

- Invariants and contracts: The public envelope remains `context-bundle-v1`; every older Capsule field remains available; aliases and anchors are explicit Git-tracked facts; ambiguous matches fail closed; foreign drafts are never read; Required reads do not cap necessary code investigation.
- Failure / recovery: Missing aliases fall back to feature/title/path routing; a missing or stale Pack produces guided warnings; multiple near matches require an explicit session; lower-priority v2 guidance is truncated before identity when the Capsule reaches its character budget.
- Non-goals: v0.8.0 does not infer task progress or diffs, discover symbols from source, generate translations, persist Capsule Markdown, summarize chat, or declare semantic code-boundary completeness.

## Verification

Run `python scripts/evaluate_continuation.py --format json` for the synthetic selection/privacy/budget report. Run `python -m unittest discover -s tests -p test_continuation_evaluation.py -v` and the focused routing/Capsule cases in `test_ledger.py`. Run `python scripts/build_runtime.py --check` before release.

<!-- repo-context-ledger:pack-specs:start -->
## Stable context

- [Continuation Quality](../../specs/continuation-quality.md)
<!-- repo-context-ledger:pack-specs:end -->

<!-- repo-context-ledger:pack-files:start -->
## Tracked file fingerprints

- `src/repo_context_ledger/runtime.py.tmpl` — `sha256:288d4092f23898a34866d4769bd21d25a2276a44809fdcb8346a330f4d50f9cf`
- `src/repo_context_ledger/constants.pyfrag` — `sha256:fe008b1cafebdd774a0d1cb14e239cadf11038be0d99ec577d56cf1e9addc315`
- `skills/repo-context-ledger/assets/context-pack-template.md` — `sha256:b5f282aa01d34cbd59a085e8844e1b997f202b01ba64cbb69638bfca9a410dfa`
- `skills/repo-context-ledger/SKILL.md` — `sha256:c63b2a91a103321129a819986d4e778c974d57a421fad6f157f8e7aa3217c893`
- `scripts/evaluate_continuation.py` — `sha256:8e105e174ef7c4560ed5c1e34b7420f4db568d54661eb0c1b38a272c0a62ed63`
- `tests/test_continuation_evaluation.py` — `sha256:c4f76cdbefcacda985b35eb860cdeda9a48123f800a31e75c3d7f9ce0801f141`
- `tests/fixtures/continuation-eval-v1.json` — `sha256:665ce216ccd359416d8f8a8748a89613700ad6047e599f760ec7a681a9efb4d7`
<!-- repo-context-ledger:pack-files:end -->
