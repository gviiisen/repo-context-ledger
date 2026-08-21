# Production-scale context and validation

Use this reference in repositories where accumulated Packs, specs, and completed changes make broad context loading or full local audits expensive.

## Context Plan is the initial read boundary

Run:

```text
python .context-ledger/ledger.py context --query "<task>"
```

The runtime returns one `context-plan-v1` with one current primary Pack, bounded Required reads, cold-history summaries, and the configured character budget. Superseded or archived Packs are never eligible as Required reads.

- Read Required reads in order.
- Do not recursively read `docs/ai`, `docs/specs`, or `docs/changes`.
- Treat completed Change bodies as cold history. ID/title/feature/date/summary/evidence metadata is not permission to load a body.
- Open a completed Change only when the user asks for historical reasoning, a Required Pack cites it for a named reason, or the unresolved question cannot be answered from current code/specs.
- If more context is needed, state the unresolved question before opening another document.

Use `--format json` when a native Agent integration needs the exact plan, budget, and local timing metrics.

## Keep validation proportional to the change

Use the existing session-scoped `finish` gate for local task completion. It validates the selected draft and related Pack/spec evidence only.

Before a pull request, use a merge-base delta:

```text
python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main
```

This checks changed handoffs, specs, Packs, Markdown links, adapter drift, directly related current Packs/specs, and Coverage without letting unrelated historical debt block the pull request. A source change that makes its related Pack stale still fails. Coverage accepts private task evidence or a spec exception only from a session whose recorded evidence intersects the changed implementation paths.

Keep the full audit explicit:

```text
python .context-ledger/ledger.py check --strict --coverage
```

Run it for scheduled repository health work, controlled integration, or release readiness. Do not run it merely to finish an unrelated parallel task.

## Configuration

The `context` object in `.context-ledger/config.json` controls the hard initial budget:

```json
{
  "max_required_files": 3,
  "max_linked_specs": 2,
  "max_change_summaries": 3,
  "max_total_characters": 30000,
  "show_close_candidates": 0
}
```

Keep the default unless a measured repository need justifies a larger budget. Increasing the budget is not a substitute for smaller Context Packs or clearer feature boundaries.

## Knowledge growth

- Keep one short completed Change per behavior-changing task; its body remains cold by default.
- Keep one current Pack per durable feature or bounded subsystem, not one Pack per fix.
- Update specs only when current behavior, contracts, boundaries, or navigation truth changes.
- Regenerate shared indexes on the default branch rather than every feature branch.
