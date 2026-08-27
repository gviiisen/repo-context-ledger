# Continuation Quality

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-27

## Purpose and behavior

Continuation Quality lets a fresh Codex, Cursor, Claude, Copilot, Grok, or other Agent window route a short human phrase to one owned unfinished task and receive bounded, actionable guidance. The deterministic runtime combines explicit Pack aliases and code-map anchors with the existing private checkpoint, evidence, verification, and Git position. It does not recreate vendor Memory, persist chat, or infer hidden task progress.

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::query_tokens` | Produces deterministic Latin/path and CJK tokens without a model dependency. |
| `src/repo_context_ledger/runtime.py.tmpl::parse_context_pack_metadata` | Loads explicit aliases, code-map anchors, invariants, tracked paths, and linked specs into disposable routing metadata. |
| `src/repo_context_ledger/runtime.py.tmpl::score_context_pack` | Gives exact human aliases and explicit `path::Symbol` anchors explainable routing weight. |
| `src/repo_context_ledger/runtime.py.tmpl::score_resume_session` | Applies the same public Pack vocabulary to owned active/paused session selection. |
| `src/repo_context_ledger/runtime.py.tmpl::build_resume_capsule` | Emits additive `resume-capsule-v2` guidance inside `context-bundle-v1`. |
| `scripts/evaluate_continuation.py` | Measures synthetic continuation accuracy, ambiguity, privacy, anchors, budget, and latency through production scoring and Capsule code. |
| `tests/fixtures/continuation-eval-v1.json` | Contains only synthetic multilingual, path, symbol, ownership, and no-match cases. |

## Data flow and contracts

- Input: a natural-language query; current Git-tracked Pack feature, title, purpose, optional explicit `Aliases`, code-map entries, tracked paths, invariants, and specs; and active/paused session data accessible to the current principal.
- Flow: the router tokenizes the query, shortlists Packs from explicit metadata, scores accessible session checkpoints with the selected Pack vocabulary, blocks near-equal owned matches, and builds a Capsule only for one selected accessible session. A foreign session is never opened; its feature may be compared with public Pack aliases/anchors only to return a coarse overlap signal.
- Persistence / dependencies: aliases, anchors, invariants, specs, and tracked fingerprints are Git-tracked Pack facts. Parsed metadata is disposable private cache. The Capsule is generated on demand and is not written to Markdown, Git, or vendor Memory. Python 3.10+ standard library and Git remain the only runtime dependencies.
- Output: the public envelope remains `context-bundle-v1`. An owned match may contain additive `resume-capsule-v2`, preserving all previous Capsule fields and adding goal, current state, next action, explicit code anchors, must-preserve contracts, verified facts, unresolved questions, Required reads, and do-not-load guidance. The serialized Capsule stays within its declared character budget.

## Boundaries and failure modes

- Invariants: exact aliases and anchors are human-maintained facts, not generated translations or code guesses; ambiguous owned sessions fail closed; foreign private drafts are never read; code and executed verification remain stronger than Capsule/Pack prose; Required reads start investigation but never cap behavior-relevant code reading.
- Permissions / concurrency: Pack aliases and anchors are shared through Git. Private session content remains principal-scoped. Another principal may receive only a boolean-style overlap signal unless an explicit unexpired read-only, fork, or transfer grant exists.
- Failure / recovery: missing aliases fall back to existing feature/title/path routing; a missing Pack yields guided continuation from accessible checkpoint data; stale Pack fingerprints produce warnings; over-budget output drops lower-priority guidance before checkpoint identity; multiple near matches require an explicit session ID.
- Privacy: evaluation fixtures and public reports contain no production repository, branch, commit, username, session, path, log, or Capsule body. A fixture's foreign private marker must never appear in evaluation output.
- Non-goals: v0.8.0 does not automatically infer task completion, inspect source bodies to discover symbols, generate translations, collect diffs into checkpoints, summarize chat, auto-resume a blocked match, or decide that routed context is semantically complete.

## Verification

Run `python scripts/evaluate_continuation.py --format json` and `python -m unittest discover -s tests -p test_continuation_evaluation.py -v` for the synthetic continuation gate. Run `python -m unittest discover -s tests -p test_ledger.py -v` for real CLI, principal isolation, Capsule compatibility, alias persistence, cache invalidation, and code-anchor routing. Run `python scripts/build_runtime.py --check` to prove both standalone outputs match the editable source.

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Build continuation quality engine](../changes/2026/08/20260827075252-gviiisen-c783c8332f-build-continuation-quality-engine.md)
<!-- repo-context-ledger:changes:end -->
