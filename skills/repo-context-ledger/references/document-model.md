# Document model

Use three layers of repository knowledge.

New v0.4 records use `Quality profile: evidence-v1`. Their language and detail metadata come from `.context-ledger/config.json`; legacy documents remain valid and are not rewritten automatically. Use [writing-quality.md](writing-quality.md) for evidence, language, and purpose-specific form rules.

## `docs/ai/`: repository orientation

Store information that applies across features: repository purpose, major modules, shared architecture, environment conventions, and navigation guidance. Keep it concise and link to stable feature specs.

### `docs/ai/context-packs/`: minimal feature loading

Keep one compact Context Pack per feature or bounded subsystem. Use it as the first document loaded after a context switch. Record the minimum load order, entry points, contracts, boundaries, verification, stable-spec links, and tracked-file fingerprints.

Context Packs route an agent to current truth; they do not replace stable specs. Refresh a pack after its tracked files change. Strict validation treats changed or missing fingerprints as stale context.

Use a compact navigation form: `Read first`, `Read if needed`, and `Do not load by default`. Context Packs have a configurable maximum line count.

## `docs/specs/`: current feature truth

Create one document per durable feature, interface, or bounded subsystem. Describe:

- purpose and user-visible behavior;
- entry points and important code paths;
- data flow and external contracts;
- invariants, boundaries, failure modes, and non-goals;
- verification commands;
- related historical changes.

Update this layer when the current implementation changes. Do not append chronological notes to the narrative; the managed related-changes block provides history.

Use a current-state form: concrete path/symbol ownership, input → flow → persistence/dependency → output, boundaries, and reliable verification commands. Never copy a handoff's chronological narration into a spec.

## `docs/changes/`: chronological handoffs

Create one document per behavior-changing task. Explain intent, the actual change, touched code paths, risks, verification, and documentation impact. Completed handoffs remain immutable except for corrections.

Store and index history by month:

```text
docs/changes/README.md
docs/changes/YYYY/MM/README.md
docs/changes/YYYY/MM/<individual-change>.md
```

The root history index lists months only. Each monthly index lists that month's individual changes, preventing a single document from growing without bound.

Each handoff has a unique timestamp/actor/token filename plus `Handoff ID`, `Actor`, and `Branch` metadata. This allows contributors to create changes concurrently without claiming the same path.

Use a chronological evidence form: Before/After behavior, path/symbol responsibilities, invariants, failure/recovery, deliberate non-changes, documentation impact, open questions, Git-derived changed paths, and verification executed by the runtime.

Paused handoffs keep `Status: paused`, a resume summary, the next action, base commit, and dirty paths. In a Git repository, active handoff, active feature, paused stack, and recent features are private workspace state under Git metadata and isolated by branch/worktree. They are not committed. In a non-Git directory, the fallback state remains `.context-ledger/context-state.json`. Agents use `status` and lifecycle commands rather than editing state directly.

## README summaries

The runtime owns only content between `repo-context-ledger` markers. Root and detected module READMEs retain human-authored content outside those markers. Generated blocks link readers and agents to current context and recent changes.

Monthly indexes and managed README blocks are derived data. With the default team policy, feature branches do not regenerate them. After merge, run `sync --derived` on the default branch to rebuild the same result from committed handoffs, specs, and Context Packs. This keeps concurrent pull requests from repeatedly conflicting in shared summaries.

Context Packs record both a source commit and a base branch/commit. `team-check` compares a working branch with its base, detects overlapping code paths and feature handoffs, rejects derived-index edits on feature branches, and reports packs created against an outdated base.

## Migration rules

- Reuse an existing `docs/specs/` or equivalent stable documentation area when it already serves this purpose.
- Preserve existing files and prose.
- Prefer adding indexes and managed blocks over reorganizing a mature repository.
- Recognize mature `docs/changes/YYYY-MM/...` trees as a legacy monthly layout. Reuse an existing `YYYY-MM/index.md` without rewriting its human content, group nested handoffs at that month root, and do not create per-date or per-feature indexes. Delete a stale generated index only when its full content is reproducible from current sibling records; preserve ambiguous files.
- Treat nested Git repositories and worktrees as module-discovery boundaries.
- Configure exceptional paths in `.context-ledger/config.json` instead of duplicating documents.
- Re-running `init` migrates v2 shared `.active-handoff` and context state into private v3 workspace state after the new state is safely written.
- Upgrading to v0.4 adds the quality policy and templates without changing existing record language, format, filenames, or content. Strict evidence checks apply only to documents marked `evidence-v1`.
