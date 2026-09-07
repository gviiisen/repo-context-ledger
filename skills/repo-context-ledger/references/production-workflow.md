# Production-scale context and validation

Use this reference in repositories where accumulated Packs, specs, and completed changes make broad context loading or full local audits expensive.

## Judge the delta before lifecycle work

First judge new facts/effects from the current request and loaded task context. Do not run a classifier command, scan Git again, or write a classification document for every reply. Routine follow-ups with adequate context use ordinary tools, not a fresh lifecycle. A known unfinished task receives only its new delta and useful findings; retain existing background and methods, and do not finish it merely because one reply ends. New behavior after completion needs a new record, even if the task sounds similar; never rewrite completed history. Operational facts may require an update, but code preparation, questions and identical status rechecks do not each need a new Change.

Run `plan --query "<user request>" --tool <agent>` only when task identity or a required route is missing. Its read-only `workflow-plan-v1` result selects a mode and structured next action; honor requires_confirmation. A paused task or real handover uses resume and its new epoch; a same-window continue on a known active task does not. Reuse only results still valid for the relevant code, inputs, environment and acceptance phase; time-sensitive safety checks stay fresh. This is Agent guidance, not a new semantic-deduplication engine or test-result cache.

Examples for reviewing the guidance:

| Request and known state | Expected decision |
| --- | --- |
| "再看一下刚才的日志"; task and log location already known | Perform the requested read normally; no plan/start/finish or synthetic new verification entry. |
| "继续刚才的修复"; same active window, session and epoch known | Continue that draft, adding new facts only; no resume/epoch bump. |
| "另一个接口也修同样的问题" | Reuse the method, inspect the new interface boundary, and record its actual delta; do not recycle the old pass. |
| New behavioral correction after the earlier task was published | Start a new record and reference relevant background; leave the completed record unchanged. |
| "继续公告抓取" in a fresh window with unknown session | Route the keywords; resume only the uniquely permitted task, or resolve ambiguity. |
| Repeat deployment request or changed authorization/environment | Respect the explicit request and safety gates; similarity neither authorizes a side effect nor justifies skipping required checks. |

These examples document the expected Agent decisions; deterministic runtime tests alone do not prove that a model will always choose them.

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

Use ordinary tools for reads, searches, file generation, preparation, and authorized deployment. Select managed verification by acceptance goal, not by helper-script count. Run a required acceptance script through verify at first execution; do not rerun it simply to log it. Group checks with the same goal using an existing reviewed project script, preserving failed and not-run substeps. Pre-deployment, authorization, and post-deployment boundaries stay ordered and separate; no hard invocation quota justifies dropping a check or replaying a state-changing action. Meaningful operational facts still belong in the same draft, clearly distinguished from managed verification.

Keep one session open for the complete logical request, including its tests and documentation. Do not finish the code and then open a second session just to update the same request's README. Archive once, but preserve meaningful progress in the same private draft when a diagnosis changes, a key decision is made, or a failed approach reveals an important boundary. Before switching windows, checkpoint the result and next step without replacing the reasoning in the draft. Do not log every command or delay publication across unrelated later user requests.

`start --workflow small-fix` uses the existing evidence-v1 headings with nine authoring prompts: intent, Before/After, change explanations, invariants, failure/recovery, unchanged scope, documentation rationale, and uncertainty. Explain what each meaningful change does and why, citing its exact repository-relative file/symbol; coupled files can share an explanation and refer to common boundaries and verification. Only the documentation `Updated` list is generated from scoped evidence, never its `Reason` or the change explanation. There is no fixed limit on change items. Auto evidence includes changed README and native instruction Markdown, but these remain non-production Coverage paths. Generated runtime/configuration files are still filtered. A broad dirty tree or multiple sessions requires explicit task-scoped evidence; a single session alone never proves all dirty changes belong to it.

New short records carry `Record format: small-fix-explained-v1`. The gate rejects path-only explanations and missing implementation-path references (all evidence paths if none are implementation), but it cannot prove business semantics or detect every omitted change inside one file. Review the actual diff against the record. If multiple independent behaviors, high-risk boundaries, or uncertainty appear, expand this same draft to `Workflow: ordinary-change` and `Detail: standard`, preserving its format marker, decisions, and checks. Do not replace the session or erase evidence to make it fit the short form. Historical completed records are preserved; older unfinished short forms need explanations before publication.

Use optional `finish --dry-run` with the same session/epoch/spec arguments when the closeout requirements are uncertain. It uses real preparation and validation, reports draft, verification, spec, and related Pack problems together where inputs can safely be resolved, and returns 0 when ready or 2 when invalid. It does not lock, save router caches, update drafts/specs, publish history, or change ownership. An invalid path, inaccessible session, or missing scoped evidence still stops before unsafe inspection. A successful preview is a point-in-time check, not a reservation; actual finish revalidates. Do not add this preview to every small task or poll it after every field edit.

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
- `pack --file` declares validity dependencies: changing one requires code-informed Pack review and a fresh fingerprint. Use `pack --reference <path>` for optional reading links whose contents do not determine this Pack's correctness. They live in Reading references, are checked for broken links, and neither invalidate fingerprints on content edits nor satisfy Coverage. Never move a real behavior dependency there to get a green check.
- Existing `--file` dependencies are never automatically demoted. Refreshing without `--file` retains the full list; supplying any `--file` still explicitly replaces it. A path cannot be both tracked and a reading reference. Review both the code boundary and Pack prose before explicitly changing dependency roles. Optional references are read only for a named question, never as an instruction to load every linked file.
- Reading references currently use simple local Markdown links. Paths with Markdown delimiters (brackets, parentheses, backticks, a fragment marker, or newlines) are rejected before writing instead of emitting a broken link; ordinary spaces are supported. Remove obsolete reading links from the Pack when their targets move, then review the new path.
- Update specs only when current behavior, contracts, boundaries, or navigation truth changes.
- Regenerate shared indexes on the default branch rather than every feature branch.
