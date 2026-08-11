# Repo Context Ledger

[English](README.md) | [简体中文](README.zh-CN.md)

An open Agent Skill that keeps repository context, feature documentation, change handoffs, and README summaries synchronized after AI-assisted code changes.

You make ordinary coding requests. The AI owns the documentation lifecycle.

## Why it exists

AI coding sessions often start without the context accumulated in earlier windows. The next agent must read a large part of the codebase again, and implementation details or important boundaries can be lost between sessions.

Repo Context Ledger gives every AI session a small, durable map of the repository:

- where a feature lives;
- how its code path works;
- which contracts and edge cases must remain stable;
- what changed, why it changed, and how it was verified;
- which project and module README summaries need refreshing.

## What's new in v0.4.1

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
- `docs/ai/context-packs/`: minimal feature context, load order, boundaries, tests, and tracked-file fingerprints.
- `docs/specs/`: current feature behavior, code maps, contracts, and boundaries.
- `docs/changes/`: chronological implementation and repair handoffs, grouped as `YYYY/MM/<change>.md` with a small monthly index.
- Private branch/worktree state: the current handoff and paused tasks are stored under Git metadata and are never committed.
- Root and module `README.md` files: generated navigation blocks without rewriting human prose.
- `AGENTS.md`, `CLAUDE.md`, and Cursor rules: durable instructions that tell coding agents to run the workflow autonomously.
- `.context-ledger/writing-quality.md`: local evidence, language, and record-form rules available to every AI tool.

## Compatibility

The core skill follows the open Agent Skills `SKILL.md` format. It is designed for Codex, Claude Code, Cursor, and other agents that support Agent Skills.

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

## Tutorial

### 1. Initialize a repository once

Open the target project with your AI coding tool and ask:

> Use repo-context-ledger to initialize this repository.

The agent creates the documentation structure, private workspace state, and durable agent instructions without overwriting existing documentation.

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
7. close the handoff and validate the ledger.

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

### 3. Switch tasks naturally

Tell the agent what you want in ordinary language:

> Pause the withdrawal monitoring fix and switch to the login timeout issue.

The agent records the current progress and next step, pauses that handoff, loads the login Context Pack, and starts the new work. Later, say:

> Continue the previous withdrawal monitoring task.

The agent restores the handoff, checks whether the repository or tracked files changed, and reloads only the relevant context. Internal `pause`, `focus`, `pack`, and `resume` commands are agent-owned bookkeeping; users do not need to run them.

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

Tell the new agent which feature or interface you want to change. It can read the compact generated index and relevant spec instead of scanning a large part of the repository for background context.

### 6. Review the result

After a completed change, expect to see:

```text
docs/
├── ai/
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
- Only explicitly marked generated blocks are replaced.
- Every configured path is validated to remain inside the repository before writes occur.
- Handoff files use collision-safe creation and never overwrite existing history.
- Git branches and worktrees keep independent active/paused task state; the old shared active pointer is migrated and removed.
- Feature branches avoid shared derived files by default, and `team-check` reports likely team conflicts before review.
- Active work cannot silently switch to another feature; it must be paused with resumable state first.
- Context Packs detect missing or modified tracked files with SHA-256 fingerprints.
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
