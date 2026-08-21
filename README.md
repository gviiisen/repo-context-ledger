# Repo Context Ledger

[English](README.md) | [简体中文](README.zh-CN.md)

An open Agent Skill that bridges verified repository context across Codex, Claude, Cursor, GitHub Copilot, Grok, and other coding agents while keeping feature documentation, change handoffs, and README summaries synchronized.

You make ordinary coding requests. The AI owns the documentation lifecycle.

## Why it exists

AI coding sessions often start without the context accumulated in earlier windows. The next agent must read a large part of the codebase again, and implementation details or important boundaries can be lost between sessions.

Repo Context Ledger gives every AI session a small, durable map of the repository:

- where a feature lives;
- how its code path works;
- which contracts and edge cases must remain stable;
- what changed, why it changed, and how it was verified;
- which project and module README summaries need refreshing.

## What's new in v0.5.8

- Context Pack fingerprints are portable across Windows and Unix checkouts: logically identical UTF-8 text receives the same digest with LF or CRLF line endings.
- Git attributes remain authoritative. Files marked `-text`, files containing NUL bytes, and non-UTF-8 content remain byte-sensitive, so binary changes cannot be hidden by normalization.
- Existing LF-based `sha256:` fingerprints remain compatible; a real text change still makes the related Pack stale.
- Persisted verification commands, successful result lines, failure capsules, and not-run reasons replace repository, Codex, temporary, and user-home roots with `<REPO_ROOT>`, `<CODEX_HOME>`, `<TEMP_DIR>`, and `<USER_HOME>`.
- Redaction recognizes ordinary Windows paths, slash-normalized paths, and JSON-escaped double-backslash paths. The currently visible historical records were corrected to remove five local absolute paths without rewriting Git history.

## What's new in v0.5.7

- `init --dry-run` builds the exact same initialization plan as real `init`, then prints file creates, managed-block updates, deletions, migrations, detected modules, and a compact summary without writing repository files or private workspace state.
- Preview and apply share one in-memory filesystem plan, so the preview cannot drift into a separate approximation of initialization behavior.
- Dry-run does not acquire the repository write lock and remains read-only even while inspecting legacy workspace-state migrations.
- Existing prose, mature change history, custom documentation paths, nested Git boundaries, and session drafts keep the same preservation rules during preview and apply.

> Version note: v0.5.5 was reserved for this work but never released. The completed feature ships in v0.5.7; no published release or functionality is missing.

## Added in v0.5.6

- `context --query` is a Context Pack router: it reads live Pack metadata, prefers feature/title/tracked-path matches, demotes superseded or stale Packs, and returns one primary Pack plus linked specs and the selection reason.
- Omitting `--repo` walks up from the current directory to the nearest `.context-ledger/config.json` and stops at a nested Git repository boundary. An explicit `--repo` still wins.
- Failed `verify` records a redacted Failure Capsule instead of only a hash. Success still stores a hash plus the last result line. Raw logs are not persisted.
- Handoff Code paths may cite `file.go::Symbol`; the path part is matched against Git evidence.
- Automatic single-session evidence skips generated/managed paths and refuses oversized dirty trees, so a shared worktree cannot silently swallow unrelated files.
- The Skill now leads with the shortest path: read-only `context`/`focus`, small single-task `start → verify → finish`, and the full evidence/spec/Pack flow only for larger work.

## What's new in v0.5.4

- Parallel-session evidence is explicit: when another task session exists, `evidence --session <id>` requires repeated `--path <path>` values and refuses to absorb the shared worktree's entire dirty set.
- `finish` now uses a session-scoped gate. It validates only the selected draft, its recorded paths, explicit specs, and relevant Context Pack fingerprints.
- Dirty paths and stale Context Packs belonging to another session no longer block the current session's publication; the current session's own stale Pack still fails closed.
- Repository-wide `check --strict --coverage` remains the integration/PR gate instead of being an implicit per-session finish dependency.
- Generated Agent rules explicitly forbid contacting another task because of foreign dirt, a stale Pack, or a failed global check.

## Added in v0.5.3

- Active and paused handoffs are private session drafts under worktree Git metadata; `start`, `checkpoint`, `evidence`, and `verify` no longer add unfinished records to `docs/changes/`.
- `finish` reserves a unique history path, validates the draft, atomically publishes one completed change, and deletes only that session's private draft after repository checks pass.
- Interrupted publication is idempotent: a matching completed record can be validated and cleaned up on retry without duplicating history.
- Registered v0.5.2 active or paused records migrate into private v7 drafts while completed and legacy history remains unchanged.
- Ledger concurrency is explicitly limited to bookkeeping. It does not copy, lock, claim, merge, or coordinate source-code files; the host Agent and Git retain that responsibility.

## Added in v0.5.2

- Task-scoped sessions replace the single active-handoff pointer: multiple coding tasks can keep independent active or paused handoffs in one worktree.
- Every lifecycle command accepts `--session <id>`; when several sessions match, omission fails closed instead of selecting, pausing, or completing another task.
- `verify` binds its target under a short lock, runs the external command without the repository write lock, then records the result under another short lock.
- Generated Agent instructions prohibit unsolicited cross-task messages, delegation, steering, and interruption. Sharing a worktree does not grant coordination authority.
- Existing v2-v5 active and paused state migrates into v6 task sessions without rewriting historical change records.

## Added in v0.5.1

- Coverage path classes distinguish production implementation from tests, CI, configuration, generated output, managed ledger files, and project-specific ignored paths.
- Repository-relative glob policies under `coverage` are validated, persisted by `init`, and remain optional for existing v5 repositories.
- Context Pack coverage is now relational: every changed production path must be tracked by a Context Pack, and that related Pack must be refreshed.
- Changing an unrelated Context Pack no longer satisfies `check --coverage`.
- Coverage failures name the uncovered implementation path and the related Pack that was not updated.
- Root translated READMEs and configured module READMEs are treated as managed documentation rather than production implementation.

## Added in v0.5.0

- Native Context Bridge: `AGENTS.md`, `CLAUDE.md`, Cursor rules, and GitHub Copilot instructions route every supported agent to the same Git-tracked source of truth.
- Context Manifest: `docs/ai/context-manifest.json` provides a deterministic machine-readable map from features to Context Packs, stable specs, tracked code paths, and recent changes.
- Cross-agent checkpoints: an active task can record its verified state and next action without pausing, allowing another agent in the same worktree to continue it.
- Adapter lifecycle: `adapters sync/check/status` preserves user prose while detecting missing or drifted native entry files.
- Git-diff coverage gate: `check --coverage` reports behavior-changing paths that lack handoff evidence, a stable spec or explicit exception, or an updated Context Pack.
- Private-memory boundary: Codex, Cursor, Claude, and Copilot Memory remain private caches; only code-verified facts are promoted to the shared ledger.
- Schema v5 migration preserves existing records, custom documentation paths, mature history layouts, and README prose.

## Added in v0.4.1

- Mature-repository adoption: existing `YYYY-MM/...` change trees are grouped at the month root instead of producing an index in every date or feature directory.
- Existing monthly `YYYY-MM/index.md` files are preserved and reused as the month link; the runtime does not rewrite their human-maintained content.
- Legacy and native trees for the same calendar month share one root-index entry, preferring an existing human-maintained month index.
- Safe index cleanup: an obsolete `README.md` is removed only when the runtime can reproduce it byte-for-byte from current sibling records. Ambiguous or human-edited files are retained.
- Worktree boundaries: module discovery stops at nested Git repositories and worktrees, preventing duplicate module entries and README updates.
- Correct history counts: monthly `index.md` files are treated as indexes rather than change records.

## Added in v0.4.0

- Evidence-first records: new handoffs, specs, and Context Packs use the backward-compatible `evidence-v1` quality profile.
- Real verification capture: `verify` executes the check and records its command, status, exit code, duration, and output hash without persisting command output.
- Git-derived evidence: `evidence` records actual changed paths so agents do not rely on memory.
- Language policy: choose `auto`, `en`, or `zh-CN` while preserving source identifiers and commands.
- Configurable detail: choose `concise`, `standard`, or `detailed`; Context Packs have a size limit.
- Purpose-specific forms: handoffs capture Before/After evidence, specs capture current truth, and Context Packs remain minimal loading routes.
- Legacy-safe adoption: existing records keep their language, format, filenames, and content until explicitly upgraded.

## What it maintains

- `docs/ai/`: concise repository-wide orientation for fresh AI sessions.
- `docs/ai/context-manifest.json`: generated feature-to-context routes for machine discovery.
- `docs/ai/context-packs/`: minimal feature context, load order, boundaries, tests, and tracked-file fingerprints.
- `docs/specs/`: current feature behavior, code maps, contracts, and boundaries.
- `docs/changes/`: chronological implementation and repair handoffs, grouped as `YYYY/MM/<change>.md` with a small monthly index.
- Private branch/worktree state: independent active and paused drafts are stored under Git metadata and are never committed; only completed changes enter formal history.
- Root and module `README.md` files: generated navigation blocks without rewriting human prose.
- `AGENTS.md`, `CLAUDE.md`, Cursor rules, and `.github/copilot-instructions.md`: thin native adapters that route coding agents to the same ledger.
- `.context-ledger/writing-quality.md`: local evidence, language, and record-form rules available to every AI tool.

## Compatibility

The core skill follows the open Agent Skills `SKILL.md` format. It is designed for Codex, Claude Code, Cursor, GitHub Copilot, Grok, and other agents that support Agent Skills or repository instruction files.

Initialized repositories also receive plain instruction files, so tools without native Skill discovery can follow the same workflow. Native discovery and exact installation locations vary by product.

## Install

Clone this repository or download a release, then install the directory `skills/repo-context-ledger` in your AI tool.

### Codex

Ask Codex:

> Use `$skill-installer` to install the `skills/repo-context-ledger` skill from `https://github.com/gviiisen/repo-context-ledger`.

For repository-scoped use, copy or link the skill directory to:

```text
.agents/skills/repo-context-ledger/
```

### Claude Code

Copy or link `skills/repo-context-ledger` to either the personal or project skill directory:

```text
~/.claude/skills/repo-context-ledger/
.claude/skills/repo-context-ledger/
```

### Cursor

Import this GitHub repository from Cursor's Skills/Rules settings, or copy the skill to:

```text
~/.agents/skills/repo-context-ledger/
.agents/skills/repo-context-ledger/
```

### GitHub Copilot

Install the Skill through a compatible Agent Skills client, or let an initialized repository's `.github/copilot-instructions.md` route Copilot to the ledger. The runtime preserves existing Copilot prose outside its managed block.

## Tutorial

### 1. Initialize a repository once

Open the target project with your AI coding tool and ask:

> Use repo-context-ledger to initialize this repository.

The agent first previews the exact operation list with `init --dry-run`, then applies the same plan with `init`. It creates the documentation structure, private workspace state, and durable agent instructions without overwriting existing documentation.

For a manual preview, run:

```text
python path/to/ledger.py --repo path/to/repository init --dry-run
```

The output is a compact plan, not a full diff. It does not create a lock, repository file, or private session-state file.

### 2. Work normally

Make the same request you would make without this skill:

> Fix the withdrawal monitoring interface and verify the behavior.

You do **not** need to run `ctx begin`, name a handoff, or remember lifecycle commands. The agent should autonomously:

1. retrieve the relevant repository and feature context;
2. start a change handoff before implementation;
3. update code and execute claimed checks through the verification recorder;
4. derive changed paths from Git and record Before/After behavior, boundaries, and evidence;
5. update the stable feature spec and Context Pack;
6. refresh affected module README files and the root README summary;
7. close the handoff and validate structure plus Git-diff documentation coverage.

On a feature branch, shared monthly indexes and README summary blocks are intentionally left unchanged until merge.

### Recording language and form

The default quality policy is:

```json
{
  "language": "auto",
  "detail": "standard",
  "max_context_pack_lines": 180
}
```

With `auto`, the agent follows nearby repository documentation, then the user's language when no convention exists. Paths, symbols, commands, protocol fields, and error text stay in their source form. Handoffs, stable specs, and Context Packs deliberately use different Markdown structures because they answer different questions; existing documents are not reformatted during upgrade.

Coverage classification is configured separately in `.context-ledger/config.json`:

```json
{
  "coverage": {
    "implementation_globs": ["**"],
    "test_globs": ["tests/**", "**/*.test.*", "**/*.spec.*"],
    "ci_globs": [".github/**", ".gitlab-ci.yml"],
    "config_globs": ["pyproject.toml", "package.json"],
    "generated_globs": ["dist/**", "build/**"],
    "ignore_globs": []
  }
}
```

The runtime applies ignored, generated, test, CI, and configuration rules before the implementation fallback. Projects can replace the defaults with repository-specific globs. A changed production path only passes Context Pack coverage when that exact path is tracked by a changed Pack; updating an unrelated Pack is not accepted.

### 3. Continue in another agent or switch tasks naturally

When another agent or window will continue the same active task, the current agent records a checkpoint containing completed work, Git-derived changed paths, and the next concrete action. The task remains active; users do not run a checkpoint command themselves.

Tell the agent what you want in ordinary language:

> Pause the withdrawal monitoring fix and switch to the login timeout issue.

For an actual task switch, the agent records a checkpoint, pauses that handoff, loads the login Context Pack, and starts the new work. Later, say:

> Continue the previous withdrawal monitoring task.

The agent restores the handoff, checks whether the repository or tracked files changed, and reloads only the relevant context. Internal `checkpoint`, `pause`, `focus`, `pack`, and `resume` commands are agent-owned bookkeeping; users do not need to run them.

### 4. Collaborate with teammates

Each person or AI should work on its own Git branch or worktree. Active and paused task state is isolated automatically, while handoffs, stable specs, and Context Packs remain reviewable in Git.

Before opening or updating a pull request, the agent should update the base ref and run:

```text
python .context-ledger/ledger.py team-check --base origin/main
```

If another branch changed the same files or feature, coordinate and resolve that overlap before merging. After the pull request is merged, the agent runs this once on the configured default branch:

```text
python .context-ledger/ledger.py sync --derived
```

This rebuilds monthly indexes and managed README summaries from the merged source documents, avoiding routine generated-file conflicts between pull requests.

These are still agent-owned lifecycle commands. The user can simply say, “check this branch before the PR” or “sync the ledger after the merge”; no command memorization is required. Teams can change `team.default_branch` or set `team.derived_updates` to `always` in `.context-ledger/config.json` when the default policy does not fit their workflow.

### 5. Start a new AI session

Tell the new agent which feature or interface you want to change. Its native adapter points to the shared Context Manifest; the agent then loads the matching Context Pack and stable spec instead of scanning a large part of the repository. It never needs access to the previous product's private Memory.

### 6. Review the result

After a completed change, expect to see:

```text
docs/
├── ai/
│   ├── context-manifest.json
│   └── context-packs/
│       └── withdrawal-monitoring.md
├── specs/
└── changes/
    └── 2026/
        └── 08/
            ├── README.md
            └── 20260811123045-alice-a1b2c3d4e5-fix-withdrawal-monitoring.md
```

The exact month is generated from the completion date. Monthly grouping keeps the history readable as the project grows.

## Safety and scope

- Initialization is idempotent.
- Existing documentation and README prose are preserved.
- Existing `AGENTS.md`, `CLAUDE.md`, and GitHub Copilot prose outside managed blocks is preserved.
- Only explicitly marked generated blocks are replaced.
- Every configured path is validated to remain inside the repository before writes occur.
- Handoff files use collision-safe creation and never overwrite existing history.
- Git branches and worktrees keep independent active/paused task state; the old shared active pointer is migrated and removed.
- Feature branches avoid shared derived files by default, and `team-check` reports likely team conflicts before review.
- Active work cannot silently switch to another feature; it must be paused with resumable state first.
- Context Packs detect missing or modified tracked files with SHA-256 fingerprints.
- The Context Manifest is derived from packs, specs, and handoffs and is checked for drift on the default branch.
- Optional Git-diff coverage catches behavior paths omitted from handoff evidence, stable specs, or Context Packs.
- Private vendor Memory is never imported as authoritative repository knowledge.
- Evidence-quality records reject unresolved language, placeholders, vague standalone claims, missing concrete paths, incomplete Before/After behavior, and unverified results.
- Verification output is shown to the active agent but only a hash and metadata are persisted; common secret-bearing command arguments are redacted.
- Managed files use atomic replacement, and mutating commands use a short repository lock to prevent concurrent writers.
- The runtime uses the Python 3.10+ standard library and requires no API key.
- Semantic documentation remains the agent's responsibility; scripts enforce deterministic structure, lifecycle state, and links.

## Development

Run the test suite:

```text
python -m unittest discover -s tests -v
```

Validate the Skill with the OpenAI Skill Creator validator:

```text
python <skill-creator>/scripts/quick_validate.py skills/repo-context-ledger
```

## License

[MIT](LICENSE)

<!-- repo-context-ledger:start -->
## Repository context

- [Stable feature context](docs/specs/README.md)
- [Change history](docs/changes/README.md)
- [Feature Context Packs](docs/ai/context-packs)
- Relevant specs: [Coverage Integrity](docs/specs/coverage-integrity.md), [Native Context Bridge](docs/specs/native-context-bridge.md), [Task session integrity](docs/specs/task-session-integrity.md)
- Latest recorded change: [Implement init dry-run planning](docs/changes/2026/08/20260815153145-gviiisen-c108737ed0-implement-init-dry-run-planning.md)
<!-- repo-context-ledger:end -->
