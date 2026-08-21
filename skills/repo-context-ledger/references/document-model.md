# Document model

Use three layers of repository knowledge.

New records use `Quality profile: evidence-v1`. Their language and detail metadata come from `.context-ledger/config.json`; legacy documents remain valid and are not rewritten automatically. Use [writing-quality.md](writing-quality.md) for evidence, language, and purpose-specific form rules.

## `docs/ai/`: repository orientation

Store information that applies across features: repository purpose, major modules, shared architecture, environment conventions, and navigation guidance. Keep it concise and link to stable feature specs.

`docs/ai/context-manifest.json` is a derived, machine-readable route index. It lists Context Packs, stable specs, tracked entry paths, source commits, and recent handoffs. Rebuild it from source documents; never treat manual edits to the manifest as canonical knowledge.

### `docs/ai/context-packs/`: minimal feature loading

Keep one compact Context Pack per feature or bounded subsystem. Use it as the first document loaded after a context switch. Record the minimum load order, entry points, contracts, boundaries, verification, stable-spec links, and tracked-file fingerprints.

Context Packs route an agent to current truth; they do not replace stable specs. Refresh a pack after its tracked files change. Strict validation treats changed or missing fingerprints as stale context.

`context --query` is a router over current Context Packs and private sessions available to the current principal. It prefers exact feature, title, tracked path, and path-token matches, excludes superseded/archived Packs from Required reads, penalizes stale fingerprints, and returns one `context-bundle-v1` with a primary Pack, linked specs, selection reason, optional PR baseline, and an optional bounded Resume Capsule for a unique owned active/paused match. It does not rank every Markdown file by word count or persist the Capsule as another document. A reverse index shortlists expensive fingerprint checks while a cheap all-Pack metadata scan remains as a correctness safety net. Pack parsing and file digests may be cached only below Git metadata; cache loss or corruption rebuilds from current files. The Context Manifest may accelerate discovery when it matches live Packs; live Pack metadata remains authoritative because feature branches may defer derived-index updates. Two current Packs may track the same shared file; an explicit `Superseded by` or non-current status makes a Pack cold and ineligible for routing.

`doctor` is a read-only health projection, not a fourth knowledge layer. Its `doctor-v1` report aggregates runtime/configuration, adapters, Manifest, private-state integrity, Pack freshness and lifecycle, local links, and feature-branch derived-file safety. Shared tracked files produce an overlap warning only: the runtime never infers semantic replacement from file overlap. A Pack becomes cold only through explicit non-current status or explicit lineage. Repair suggestions are plans, not mutations.

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

Each task reserves a unique timestamp/actor/token publication path plus `Handoff ID`, `Session ID`, `Actor`, and `Branch` metadata. The handoff ID is also the lifecycle session ID. While active or paused, the content remains a private draft; only a successful `finish` publishes the completed file.

Use a chronological evidence form: Before/After behavior, path/symbol responsibilities, invariants, failure/recovery, deliberate non-changes, documentation impact, open questions, Git-derived changed paths, and verification executed by the runtime.

Paused drafts keep `Status: paused`, a resume summary, the next action, base commit, and dirty paths. In a Git repository, the task-session map and draft files live under worktree Git metadata. State schema v8 stores each private draft reference, reserved publication path, feature, status, owner principal, continuation epoch/tool, expiring grants, and update time. In a non-Git directory, the fallback lives under `.context-ledger/sessions/`. Agents use `status` and lifecycle commands rather than editing state directly.

An active handoff may also carry `Checkpointed`, `Checkpoint actor`, `Resume summary`, and `Next step`. A checkpoint preserves the task as active so another Agent window using the same human principal can continue it without pretending to import the previous tool's private Memory. The principal is a pseudonymous hash of a configured local identity or OS account, not the Agent tool name and not a Git-tracked secret.

Keyword resume searches active and paused sessions available to that principal. A unique match produces a bounded Resume Capsule on demand; `resume` keeps the same task session, changes the continuation tool, increments its epoch, and requires that epoch on later lifecycle writes. This prevents a stale pre-resume window from writing without first reloading current state. The Capsule is initial navigation, not proof of complete context: the Agent must continue into every caller, implementation, configuration, persistence, permission, concurrency, retry, test, or external boundary that can affect behavior.

Another principal cannot see private Capsule fields or mutate the session by default. It may learn only that a matching foreign scope exists, then use committed Git context. With explicit user authorization, an expiring `read-only` grant exposes only the Capsule, `fork` creates a new recipient-owned child session while preserving the source, and `transfer` changes ownership only after the source is paused and the recipient accepts it. These checks provide logical workflow isolation; filesystem and OS permissions remain the actual security boundary.

When exactly one active or paused session matches an operation, the CLI may infer it for compatibility. When multiple sessions match, it must fail and require `--session <id>`; it must never guess. In a Git worktree with another registered session, evidence capture also requires repeated explicit `--path` values and records only those changed paths. Verification holds the repository write lock only while binding the target session and while appending the completed result, not while the external command runs.

`finish` is a session-scoped publication gate. It validates the selected draft, its recorded evidence paths, explicit specs, and only the relevant fingerprints inside Packs recorded by that session. Foreign dirty paths and unrelated stale Packs remain visible to repository-wide checks but cannot block or contaminate this session's publication. Run `check --strict --coverage` as an integration or PR gate after parallel work settles.

Task-session isolation covers ledger bookkeeping only. The runtime does not copy, lock, merge, claim, or coordinate source files. Native adapters prohibit contacting, steering, pausing, or interrupting another user-owned task unless the user explicitly requested cross-task coordination; source conflicts remain the responsibility of the host Agent and Git.

## Native adapters

Keep Agent-specific entry files thin. `AGENTS.md`, `CLAUDE.md`, Cursor rules, and GitHub Copilot instructions route tools to the same manifest, Context Packs, specs, and handoffs; they do not duplicate feature truth. Preserve prose outside managed markers.

Private vendor Memory is a non-authoritative cache. When it conflicts with the repository, use this precedence: current code and executed tests, verified stable specs, Context Packs, change history, then private Memory.

## README summaries

The runtime owns only content between `repo-context-ledger` markers. Root and detected module READMEs retain human-authored content outside those markers. Generated blocks link readers and agents to current context and recent changes.

Monthly indexes and managed README blocks are derived data. With the default team policy, feature branches do not regenerate them. After merge, run `sync --derived` on the default branch to rebuild the same result from committed handoffs, specs, and Context Packs. This keeps concurrent pull requests from repeatedly conflicting in shared summaries.

Context Packs record both a source commit and a base branch/commit. `team-check` compares a working branch with its base, detects overlapping code paths and feature handoffs, rejects derived-index edits on feature branches, and reports packs created against an outdated base. `check --coverage` separately classifies Git paths through validated repository-relative globs, requires changed production paths to appear in handoff evidence, requires a changed stable spec or explicit exception, and verifies that each production path is tracked by a Context Pack that was actually refreshed. An unrelated changed Pack never satisfies coverage.

## Migration rules

- Reuse an existing `docs/specs/` or equivalent stable documentation area when it already serves this purpose.
- Preserve existing files and prose.
- Prefer adding indexes and managed blocks over reorganizing a mature repository.
- Recognize mature `docs/changes/YYYY-MM/...` trees as a legacy monthly layout. Reuse an existing `YYYY-MM/index.md` without rewriting its human content, group nested handoffs at that month root, and do not create per-date or per-feature indexes. Delete a stale generated index only when its full content is reproducible from current sibling records; preserve ambiguous files.
- Treat nested Git repositories and worktrees as module-discovery boundaries.
- Configure exceptional paths in `.context-ledger/config.json` instead of duplicating documents.
- Re-running `init` migrates v2 shared `.active-handoff` and context state into private v3 workspace state after the new state is safely written.
- Upgrading to v0.4 adds the quality policy and templates without changing existing record language, format, filenames, or content. Strict evidence checks apply only to documents marked `evidence-v1`.
- Upgrading to v0.5 adds the Context Manifest, native adapter configuration, checkpoint metadata, and optional Git-diff coverage gate. It preserves existing semantic documents and user prose.
- Upgrading to v0.5.1 adds default Coverage path classes and related-Pack validation. Existing v5 configuration remains valid; rerunning `init` persists the new default glob policy without rewriting historical records.
- Upgrading to v0.5.2 migrates the single active pointer and paused stack into v6 task sessions, shortens `verify` lock scope, and refreshes native adapters with a no-unsolicited-cross-task-contact rule. Historical handoffs are preserved.
- Upgrading to v0.5.3 migrates registered active or paused handoffs from formal history into v7 private drafts, reserves their original publication paths, and leaves completed and legacy history unchanged. A validated `finish` atomically publishes one completed change and removes only that session's draft.
- Upgrading to v0.5.4 makes evidence and finish session-scoped in shared worktrees. Foreign dirty paths and stale Packs no longer contaminate or block another task, while repository-wide strict and coverage checks remain available for integration.
- Upgrading to v0.5.9 persists a bounded `context` budget, returns `context-plan-v1` Required reads plus cold-history metadata, and adds merge-base `check --changed-since` validation. Existing Packs, specs, completed changes, session drafts, and full-check behavior remain unchanged.
- Upgrading to v0.5.10 migrates private state to v8, adds principal ownership, continuation epochs/tools, bounded `context-plan-v2` Resume Capsules, keyword resume across active/paused work, and explicit expiring read-only/fork/transfer grants. Existing drafts are bound conservatively when their Actor matches the current Git actor; completed history and Git evidence rules remain unchanged.
- Upgrading to v0.6.0 returns `context-bundle-v1`, adds a disposable Git-metadata router cache, bounded reverse-index fingerprint candidates, optional `context --baseline`, and selected-Pack evidence filtering. Existing Packs, specs, Changes, private sessions, ownership, and Git sharing rules remain unchanged; no production data or private Capsule body is added to the cache benchmark or committed records.
