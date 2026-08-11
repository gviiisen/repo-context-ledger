# Document model

Use three layers of repository knowledge.

## `docs/ai/`: repository orientation

Store information that applies across features: repository purpose, major modules, shared architecture, environment conventions, and navigation guidance. Keep it concise and link to stable feature specs.

## `docs/specs/`: current feature truth

Create one document per durable feature, interface, or bounded subsystem. Describe:

- purpose and user-visible behavior;
- entry points and important code paths;
- data flow and external contracts;
- invariants, boundaries, failure modes, and non-goals;
- verification commands;
- related historical changes.

Update this layer when the current implementation changes. Do not append chronological notes to the narrative; the managed related-changes block provides history.

## `docs/changes/`: chronological handoffs

Create one document per behavior-changing task. Explain intent, the actual change, touched code paths, risks, verification, and documentation impact. Completed handoffs remain immutable except for corrections.

Store and index history by month:

```text
docs/changes/README.md
docs/changes/YYYY/MM/README.md
docs/changes/YYYY/MM/<individual-change>.md
```

The root history index lists months only. Each monthly index lists that month's individual changes, preventing a single document from growing without bound.

`docs/changes/.active-handoff` contains only the repository-relative path of the current handoff. An empty file means no task is active. Configured alternative documentation roots use the same internal layout.

## README summaries

The runtime owns only content between `repo-context-ledger` markers. Root and detected module READMEs retain human-authored content outside those markers. Generated blocks link readers and agents to current context and recent changes.

## Migration rules

- Reuse an existing `docs/specs/` or equivalent stable documentation area when it already serves this purpose.
- Preserve existing files and prose.
- Prefer adding indexes and managed blocks over reorganizing a mature repository.
- Configure exceptional paths in `.context-ledger/config.json` instead of duplicating documents.
