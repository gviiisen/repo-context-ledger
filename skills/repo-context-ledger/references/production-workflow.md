# Production-scale context and validation

Use this reference in repositories where accumulated Packs, specs, and completed changes make broad context loading or full local audits expensive.

## Plan before lifecycle work

Run `plan --query "<user request>" --tool <agent>` before `start`, `resume`, or broad routing. Its read-only `workflow-plan-v1` result selects `readonly`, `small-fix`, `ordinary-change`, or `resume` and returns a structured next action. Do not execute that action when `requires_confirmation` is true; ask the user to clarify the requested outcome. The planner never replaces code investigation and never writes repository or private session state.

## Context Bundle is the initial read boundary

Run:

```text
python .context-ledger/ledger.py context --query "<task>"
```

The runtime returns one `context-bundle-v1` with one current primary Pack, bounded Required reads, cold-history summaries, the configured character budget, an optional PR baseline, and—when one owned private task matches—a bounded Resume Capsule. Superseded or archived Packs are never eligible as Required reads. A disposable cache below Git metadata reuses Pack parsing and tracked-file digests; it never replaces current Pack/code verification and never enters Git.

Run `doctor --format json` as a scheduled or release health observation, not on every edit. It groups Pack debt and caps detail items so a large repository does not emit one line per stale file. Treat warnings and repairable findings as planned maintenance; errors identify broken deterministic contracts. Doctor is strictly read-only and never refreshes fingerprints, changes Pack status, rewrites lineage, repairs links, or cleans private sessions.

- Read Required reads in order.
- Do not recursively read `docs/ai`, `docs/specs`, or `docs/changes`.
- Treat completed Change bodies as cold history. ID/title/feature/date/summary/evidence metadata is not permission to load a body.
- Open a completed Change only when the user asks for historical reasoning, a Required Pack cites it for a named reason, or the unresolved question cannot be answered from current code/specs.
- If more context is needed, state the unresolved question before opening another document. Always expand into behavior-relevant callers, implementations, configuration, persistence, permissions, concurrency, retries, tests, and external APIs. The budget limits only the initial route; it never limits necessary code investigation.

Use `--format json` when a native Agent integration needs the exact Bundle, budget, baseline, cache state, and local timing metrics. At PR time, add `--baseline origin/main`; an unresolved ref remains an explicit warning rather than silently pretending a delta was loaded.

## Resume without replaying a long chat

When a user starts a fresh Agent window and supplies earlier task keywords, route them before broad code or documentation search:

```text
python .context-ledger/ledger.py context --query "continue <task keywords>" --tool <agent>
```

The router searches only active/paused sessions available to the current principal. A unique match receives an on-demand Resume Capsule containing the checkpoint summary, next action, bounded implementation evidence paths, last verification, Git position, Pack, warnings, previous tool, and continuation epoch. The Capsule is private state, not a new Markdown document and not a copy of the previous conversation.

Continue the same Ledger session with `resume --query ... --tool ...`. This increments its epoch; pass that epoch to every later lifecycle write so a stale window fails instead of overwriting the newer continuation. Ambiguous matches require an explicit session ID.

Another principal gets no Capsule by default—only a minimal overlap signal—and cannot mutate the source task. An explicit expiring grant may provide read-only Capsule access, create a recipient-owned fork, or transfer a paused task. Git-tracked Packs, specs, and completed Changes remain readable to every collaborator through normal Git workflows.

The ownership boundary is logical workflow isolation. Anyone with unrestricted access to the same filesystem can inspect Git metadata, so OS accounts and repository permissions remain the security boundary. Private sessions also do not travel to a different clone or computer.

## Keep validation proportional to the change

Use the existing session-scoped `finish` gate for local task completion. It validates the selected draft and related Pack/spec evidence only.

For a small single-session fix, avoid a separate `evidence` command; `finish` captures the bounded dirty set. After code is stable, launch checks concurrently only when they do not share a database, port, generated directory, or mutable fixture. Refresh the Pack and spec while those checks run, then wait for every `verify` process to record before `finish`. Verification commands may append concurrently through short lock phases, but an Agent must not hand-edit the private draft at the same time.

Use `--timings` before the command when diagnosing lifecycle overhead. It emits one `private-command-timings-v1` JSON object to stderr and never persists machine paths or timing data in Git. `finish` validates outside the write lock, rechecks a bounded input signature under the lock, publishes atomically, and regenerates derived indexes afterward. A draft, evidence file, Pack, spec, or publication target that changes during preparation causes `finish` to fail closed and preserve the session.

For repeated project checks, prefer reviewed `verification.presets` over shell strings assembled by each Agent. Presets store executable arguments as JSON arrays, may constrain the repository-relative working directory and platform, and are executed only after an explicit `verify --preset <name>`. Keep one-off commands direct. See [verification-presets.md](verification-presets.md) for the schema and safe Windows/Linux examples.

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
