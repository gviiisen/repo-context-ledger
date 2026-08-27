# Repo Context Ledger — Cross-Agent Context Relay

[English](README.md) | [简体中文](README.zh-CN.md)

[![skills.sh](https://skills.sh/b/gviiisen/repo-context-ledger)](https://skills.sh/gviiisen/repo-context-ledger)

> Switch from Codex to Cursor or Claude, mention the feature, and continue from the right code and boundaries.

Repo Context Ledger is an open repository context management and context switching Agent Skill for AI coding. It bridges verified context across Codex, Claude, Cursor, GitHub Copilot, Grok, and other coding agents while keeping feature documentation, change handoffs, and README summaries synchronized.

Use it for AI coding context management, cross-session continuation, cross-tool context switching, and durable agent handoffs without replaying a long chat.

If you are looking for AI context management, Codex context management, Cursor context switching, Claude context management, or a way to continue work across AI coding sessions, this Skill gives the next agent a focused route to the relevant code, boundaries, and verified change history.

Install it with the standard Agent Skills CLI:

```bash
npx skills@latest add gviiisen/repo-context-ledger --skill repo-context-ledger
```

You make ordinary coding requests. The AI owns the documentation lifecycle.

Before any lifecycle command, the Agent can ask the read-only Workflow Plan whether the request is understanding work, a small fix, an ordinary change, or a continuation. The plan reuses the bounded context router, explains its decision, and asks for clarification instead of guessing when intent is ambiguous.

## Why it exists

AI coding sessions often start without the context accumulated in earlier windows. The next agent must read a large part of the codebase again, and implementation details or important boundaries can be lost between sessions.

Repo Context Ledger gives every AI session a small, durable map of the repository:

- where a feature lives;
- how its code path works;
- which contracts and edge cases must remain stable;
- what changed, why it changed, and how it was verified;
- which project and module README summaries need refreshing.

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

See [COMPATIBILITY.md](COMPATIBILITY.md) for supported Python/platform and CLI schema guarantees, and [MIGRATIONS.md](MIGRATIONS.md) for upgrade rules.

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

## Common usage examples

After installation and one-time repository initialization, talk to your coding Agent normally. You do not need to run Ledger lifecycle commands yourself.

| Situation | What you can say | What the Agent does |
| --- | --- | --- |
| Understand an existing feature | `Explain how withdrawal review works and where its boundaries are.` | Routes to the most relevant Pack and spec, then inspects the necessary code without creating a task session. |
| Implement or fix behavior | `Fix duplicate withdrawal notifications.` | Creates a private task session, loads bounded context, expands through affected code and tests, verifies the result, and publishes one completed Change record. |
| Continue in a fresh window | `Continue announcement API rate limiting.` | Finds your matching active or paused session, generates a Resume Capsule, and continues the same Ledger session rather than starting over. |
| Switch AI tools | Open Cursor after Codex and say `Continue announcement API rate limiting.` | Uses the same vendor-neutral repository context and your principal-owned private session, while revalidating code and stale warnings. |
| Temporarily switch tasks | `Pause this work, fix the login timeout, then let me return later.` | Checkpoints the current task and starts an independent private session, so their handoff drafts do not overwrite each other. |
| Hand work to a teammate | `Transfer this paused task to principal p-…` or request a read-only/fork grant. | Creates an explicit expiring grant. Without one, another principal can use committed Packs, specs, and Changes but cannot read or mutate your private draft. |

The routed files are a starting map, not a limit. The Agent must still read additional callers, implementations, configuration, persistence, permissions, concurrency, retries, tests, and external boundaries whenever they can affect the requested behavior.

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

1. produce a read-only `workflow-plan-v1` decision for the request;
2. retrieve the relevant repository and feature context when the selected workflow needs it;
3. start a private handoff only for a small fix or ordinary behavior change;
4. update code and execute claimed checks through the verification recorder;
5. derive changed paths from Git and record Before/After behavior, boundaries, and evidence;
6. update the stable feature spec and Context Pack;
7. refresh affected module README files and the root README summary;
8. close the handoff and validate structure plus Git-diff documentation coverage.

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

Initial context loading has its own production-safe budget:

```json
{
  "context": {
    "max_required_files": 3,
    "max_linked_specs": 2,
    "max_change_summaries": 3,
    "max_total_characters": 30000,
    "show_close_candidates": 0
  }
}
```

Completed Change bodies are excluded from the initial read boundary. Increasing this budget should follow a measured repository need rather than compensate for oversized Packs.

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

Project maintainers can also define reviewed verification presets in `.context-ledger/config.json`. The Agent selects a name; the runtime executes the stored argument array directly, so it does not need to improvise PowerShell quoting or rebuild a long command from prose:

```json
{
  "verification": {
    "presets": {
      "unit": {
        "argv": ["python", "-m", "unittest", "discover", "-s", "tests", "-v"],
        "cwd": ".",
        "timeout": 300,
        "sensitive": false,
        "platforms": ["windows", "linux", "darwin"]
      },
      "windows-smoke": {
        "argv": ["powershell.exe", "-NoProfile", "-File", "scripts/smoke.ps1"],
        "platforms": ["windows"]
      }
    }
  }
}
```

Run one explicitly with `python .context-ledger/ledger.py verify --preset unit`. The first run, and the first run after a preset changes, stops and prints its exact digest; review the Git-tracked preset and repeat with `--trust-digest sha256:...`. Trust is per local principal and never enters Git. Presets never run during `init`, routing, or `finish`; they cannot carry environment variables or secrets. Shell strings such as PowerShell `-Command`, `cmd.exe`, and `bash -c` are rejected. See [verification-presets.md](skills/repo-context-ledger/references/verification-presets.md) for the complete contract.

### 3. Continue in another agent or switch tasks naturally

When another agent or window will continue the same active task, the current agent records a checkpoint containing completed work, Git-derived changed paths, and the next concrete action. The task remains active; users do not run a checkpoint command themselves.

Tell the agent what you want in ordinary language:

> Pause the withdrawal monitoring fix and switch to the login timeout issue.

For an actual task switch, the agent records a checkpoint, pauses that handoff, loads the login Context Pack, and starts the new work. Later, say:

> Continue announcement rate limiting.

The fresh window routes those keywords to one private task owned by the same principal, generates a bounded Resume Capsule, and continues the same Ledger session with a new epoch. It starts from the Pack, checkpoint, evidence paths, and verification, then reads any additional callers, implementations, configuration, storage, permissions, concurrency, retries, tests, or external boundaries needed for correctness. The Capsule saves aimless rediscovery; it does not authorize shallow code reading. Internal lifecycle commands remain agent-owned bookkeeping.

Another principal cannot see or take over the private Capsule by default. Teammates continue from committed Packs, specs, completed Changes, and normal Git code; an unfinished task is shared only through an explicit expiring read-only, fork, or transfer grant. Private session state does not follow a fresh clone or another computer.

### 4. Collaborate with teammates

Each person should work on a suitable Git branch or worktree. Codex, Cursor, Claude, Copilot, and Grok may share that person's principal, while another person has a different principal. Active and paused task state stays private; completed handoffs, stable specs, Context Packs, and code remain reviewable and mergeable through Git.

Before opening or updating a pull request, the agent should update the base ref and run:

```text
python .context-ledger/ledger.py team-check --base origin/main
python .context-ledger/ledger.py check --strict --coverage --changed-since origin/main
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

Runtime contributors edit `src/repo_context_ledger/runtime.py.tmpl` and build-time fragments, then run:

```text
python scripts/build_runtime.py
python scripts/build_runtime.py --check
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the source/generated boundary.

## What's new in v1.0.1

- Automatic planning treats explicit typo, spelling, and comment-only work as `small-fix`. A one-line request is only supporting evidence when it also names a low-risk README, documentation, comment, copy, text, or example target; code risk remains `ordinary-change` even when the proposed edit is one line.
- Workflow actions preserve an explicitly supplied `--tool`, so a planned `start`, `resume`, or context route keeps its Agent source in continuation records.
- Rename-aware Git evidence and Coverage retain both the old and new path. Coverage requires the old implementation path to be owned by a Pack at the merge base, the new implementation path to be owned by a current Pack of the same feature, and the affected Packs to be refreshed. Moving production code into a test or generated directory cannot hide the removed boundary; copy sources remain informational.
- New Git-tracked documents and configuration use mode `0644` on POSIX, while private sessions, state, cache, and preset trust use `0600`. Existing targets and copied runtime modes remain preserved.

## What's new in v1.0.0

- The editable runtime is now split at tested boundaries for constants, errors, result models, repository locks, core Git access, and Workflow Planning. A deterministic builder still emits one zero-dependency `ledger.py`, so installation and `init` do not gain a package dependency.
- Every public JSON protocol now has a checked-in Draft 2020-12 declaration under `schemas/`: `workflow-plan-v1`, `context-bundle-v1`, `resume-capsule-v2`, `doctor-v1`, `status-v1`, and `check-v1`.
- Protocol tests execute real CLI commands and recursively compare successful, no-match, and error reports with the published schemas. The 1.x compatibility promise freezes required fields, meanings, and exit classes while leaving optional extensions open.
- Extraction remains incremental: lifecycle, routing, health, and rendering stay in the template until a focused test boundary exists, avoiding a flag-day rewrite.

## What's new in v0.9.0

- `plan --query` adds a read-only `workflow-plan-v1` front door with four explicit modes: `readonly`, `small-fix`, `ordinary-change`, and `resume`. It returns reasons, confidence, a confirmation flag, and a structured argument array for the next action without executing it.
- Explicit intent is deterministic. Automatic planning uses bounded English and Chinese request signals plus principal-owned Resume Capsule discovery; an ambiguous request returns `clarify` instead of creating or resuming a session.
- `context --format json` additively embeds the same Workflow Plan, while `start` rejects `readonly` and `resume` workflows so the decision layer cannot accidentally mutate task state.
- A synthetic bilingual evaluation corpus and a golden contract fixture keep the planner behavior and machine schema reviewable without production prompts or repository data.
- The primary `SKILL.md` was reduced from roughly 22,000 characters to under 12,000 and now routes detailed production, verification, and writing guidance through progressive-disclosure references.

## What's new in v0.8.2

- Repository write locks carry a version, PID, start time, command, and random ownership nonce. The owner removes a lock only when both file identity and nonce still match, so it cannot delete a replacement lock created by another writer.
- `doctor` distinguishes a live writer, stale process, unknown owner, malformed legacy metadata, and an unsafe symlink/non-regular lock path. Diagnosis is read-only and never removes a lock automatically.
- Windows process liveness uses a read-only process query instead of signal emulation; Unix uses signal 0. Diagnostics expose only bounded lock metadata and no repository path.
- Git-tracked verification presets require principal-local digest trust before their first execution and after every configuration change. A mismatch fails with `PRESET_TRUST_REQUIRED`; trust decisions stay below Git metadata and do not transfer to another user.
- [SECURITY.md](SECURITY.md) and [THREAT_MODEL.md](THREAT_MODEL.md) document supported reporting, assets, trust boundaries, considered threats, recovery rules, and deliberate non-goals.

## What's new in v0.8.1

- Git path collection now uses NUL-delimited byte output. Spaces, Unicode, quotes, literal backslashes, tabs, newlines, and rename destinations reach evidence and changed-scope checks without shell-style parsing or lossy unquoting.
- Once a directory is confirmed as a Git worktree, required evidence, coverage, finish, and `check --changed-since` operations fail closed when Git cannot read repository state. Genuine non-Git directories keep the documented local fallback.
- Machine-readable Git failures use the stable `GIT_COMMAND_FAILED` error code and bounded, redacted diagnostics instead of silently treating an unreadable index or ref as an empty change set.
- Atomic runtime and managed-file replacement preserves an existing target's permission mode on Unix-like systems while retaining the same crash-safe replace behavior on every platform.
- Focused repository-reliability tests cover complex Git filenames, Unicode renames, fail-closed corrupted-index behavior, and executable-bit preservation without storing production paths or data.

## What's new in v0.8.0

- Resume Capsule v2 keeps the additive `context-bundle-v1` envelope while organizing private continuation guidance into goal, current state, next action, explicit code anchors, must-preserve contracts, verified facts, unresolved questions, Required reads, and cold-document exclusions.
- Context Packs may declare bounded, human-maintained `Aliases` for phrases people actually use in different languages. `pack --alias` preserves those phrases across fingerprint refreshes; the runtime never invents translations or task state.
- The router treats Pack code-map entries such as `file.go::Symbol` as first-class anchors. Exact aliases and symbols guide both Pack selection and an owned active/paused session without reading source bodies or foreign private drafts.
- A fully synthetic continuation corpus evaluates owned-session Top-1 selection, multilingual aliases, path/symbol anchors, ambiguity blocking, foreign-overlap privacy, Capsule budgets, and required guidance without storing production names, paths, logs, or task content.
- Automatic task-progress, diff, and symbol inference remains deliberately deferred. Capsule v2 restructures only explicit checkpoints, evidence, verification, Git position, and Git-tracked Pack/spec facts; Agents must still inspect every behavior-relevant code boundary.

## What's new in v0.7.3

- Repository-owned verification presets replace improvised command strings with reviewed `argv`, working-directory, timeout, sensitivity, and platform metadata.
- `verify --preset <name>` executes the selected argument array directly with `shell=False` and records the preset name plus repository-relative working directory as evidence.
- Unsafe shell-string wrappers are rejected: PowerShell presets must use `-File`; `-Command`, encoded commands, `cmd.exe`, and shell `-c` forms cannot enter the configuration.
- Presets are explicit only. Initialization, context routing, and finish never run them automatically, and presets cannot embed environment variables or secrets. Existing direct `verify -- <program> <args...>` usage remains compatible.

## What's new in v0.7.2

- Small fixes with an already known code path use the short lifecycle: start, implement, run independent checks concurrently, and finish. They skip broad context routing and a separate evidence command unless the task becomes uncertain or another session requires explicit paths.
- Independent `verify` processes execute concurrently and briefly wait for one another only while appending their private results. Checks that share a database, port, generated directory, or mutable fixture remain serial.
- `finish` now prepares evidence and performs validation outside the repository write lock. A short final compare-and-swap step rechecks the session, private draft, specs, Packs, and publication target before atomic publication; derived indexes are regenerated afterward.
- The optional global `--timings` flag prints private per-command stage timings to stderr. Timing data is not persisted and contains no repository paths.
- A reproducible synthetic closeout benchmark compares the old serial choreography with the shorter overlapped workflow. In the recorded three-run fixture, median end-to-end time fell from 3.56 seconds to 2.31 seconds while the median finish lock hold stayed around 20 milliseconds; results vary by machine and checks.

## What's new in v0.7.1

- Small tracked machine/worktree configuration changes now use a compact lifecycle: `start --kind local-config`, `verify --sensitive`, and `finish --path ...`.
- Compact finish accepts only paths classified as configuration, captures task-scoped Git evidence, generates the semantic handoff, marks it `Scope: worktree-local`, and applies the stable-spec exception without manual Markdown editing or a separate `evidence` command.
- Sensitive verification executes the real command but displays and persists neither its arguments nor captured output. The record retains only status, exit code, duration, and timestamp, and compact finish requires the final check to be sensitive and passing.
- Generated Agent rules skip `context`/`focus` for this narrow path, require direct executable arguments instead of nested PowerShell quoting, and keep the full lifecycle for ordinary behavior changes.
- `doctor` warns when unmanaged `.active-handoff` or legacy handoff-template instructions coexist with the private task-session workflow; it never deletes that prose automatically.

## What's new in v0.7.0

- One deterministic build now generates both standalone runtime copies from `src/repo_context_ledger/runtime.py.tmpl` and ordered build-time fragments.
- Version/schema/exit constants, `LedgerError`, and typed command-result contracts now live in ordered `constants.pyfrag`, `errors.pyfrag`, and `models.pyfrag` sources; further extraction can proceed gradually without changing the installed zero-dependency artifact.
- `scripts/build_runtime.py --check` detects drift without writing, while ordinary builds use atomic replacement and normalized LF output. Two fresh builds are tested byte-for-byte and compiled as standalone Python.
- Windows/Ubuntu CI checks generated-runtime drift before running the full suite. Runtime tests moved into a focused architecture test file rather than further enlarging the legacy monolithic test module.
- Initialized repositories still receive one copied `.context-ledger/ledger.py`; users do not install a package and existing CLI/JSON contracts from v0.6.2 remain unchanged.

## What's new in v0.6.2

- `status --format json` and `check --format json` add stable `status-v1` and `check-v1` automation contracts; existing text output and exit behavior remain available.
- `context-bundle-v1` and `doctor-v1` stay unchanged. Golden fixtures protect schema names, required fields, the v8 repository configuration, the pre-v0.6.1 command set, and exit classes `0`, `1`, and `2`.
- A versioned, fully synthetic routing corpus checks exact feature, title, and tracked-path selection without importing production repository data.
- Windows and Ubuntu CI now run on both the minimum supported Python 3.10 and Python 3.12.
- Compatibility and migration documents define additive minor-version rules, schema-breaking major-version rules, private-state boundaries, standalone-runtime upgrades, and rollback expectations.

## What's new in v0.6.1

- `doctor` provides one bounded, read-only repository health report in human-readable text or the versioned `doctor-v1` JSON contract.
- Health checks aggregate runtime/configuration, native adapters, the Context Manifest, private task state, Context Pack freshness and lifecycle, local documentation links, and feature-branch derived-file safety.
- Stale and missing tracked paths are grouped by Pack and capped with `--max-items`, so mature repositories no longer receive hundreds of repetitive lines for one repair decision.
- Duplicate current feature IDs and broken explicit lineage are errors. Shared tracked files are warnings only; the runtime never auto-supersedes a Pack from file overlap.
- Findings distinguish `pass`, `warning`, `repairable`, and `error`, include deterministic suggested actions, and never mutate files, sessions, fingerprints, Pack status, or lineage.

## What's new in v0.6.0

- `context --query` now emits `context-bundle-v1`. It still returns one primary Pack and bounded Required reads, but also carries an optional PR baseline, route warnings, cache/index metrics, and a Pack-scoped Resume Capsule without loading source or Change bodies.
- A disposable private cache below Git metadata reuses parsed Pack metadata and tracked-file digests. Pack edits, tracked-file stat or Git text-mode changes, missing/corrupt cache data, and tool-schema changes invalidate or rebuild safely; the cache never enters Git and never becomes an authority.
- A reverse index shortlists expensive fingerprint checks while a cheap all-Pack metadata ranking remains as a correctness safety net. Exact owned-session features, titles, tracked paths, and PR-delta overlap cannot be excluded by the shortlist.
- `context --baseline <ref>` resolves the merge base, boosts Packs that track the PR delta, and returns only bounded repository-relative relevant paths. An unresolved ref produces an explicit warning instead of a false baseline.
- Resume Capsules rank recorded evidence against the selected Pack. Unrelated legacy paths are omitted by name and reported only as a count; the Agent must still inspect the current diff and every behavior-relevant code boundary.
- The public [performance baseline](benchmarks/README.md) records only anonymous aggregates. In one 59-Pack observation, routing improved from about 10.55 seconds to 1.365 seconds cold and 0.913 seconds warm, while keeping the first Required reads at one file. The reproducible benchmark uses only synthetic Packs, code, and checkpoints.

## What's new in v0.5.10

- A fresh Codex, Cursor, Claude, Copilot, or Grok window can use task keywords to route to one owned active/paused Ledger session. `context-plan-v2` creates a bounded Resume Capsule on demand from private state; it does not persist chat transcripts or a growing capsule Markdown file.
- `resume --query "<keywords>" --tool <agent>` continues the same Ledger session instead of creating a replacement. It increments a continuation epoch, and subsequent lifecycle writes require `--epoch <n>` so a stale window cannot silently overwrite the newer checkpoint.
- Private sessions now have a pseudonymous principal owner independent of the Agent tool. Another principal receives only a foreign-overlap signal by default and cannot read the Capsule or resume, pause, checkpoint, verify, finish, or invalidate the task.
- Explicit expiring grants support `read-only`, `fork`, and paused-session `transfer` workflows. A fork creates a new private child session and leaves the source untouched; a transfer changes ownership only when the recipient accepts it.
- Required reads remain an initial route, never a cap on code investigation. Generated Agent policies require expansion through callers, implementations, configuration, persistence, permissions, concurrency, retries, tests, and external boundaries whenever they can affect the requested behavior.
- Git-tracked Packs, specs, and completed changes remain shared normally. Private unfinished state stays in worktree Git metadata and still does not travel to another clone or machine.

## What's new in v0.5.9

- `context --query` now emits a bounded `context-plan-v1`: exactly one primary Pack, only the linked specs that fit the configured file/character budget, and explicit Required reads.
- `context --format json` provides a stable cross-Agent contract with repository-relative paths, selection confidence, budget usage, and local timing/file-count metrics.
- Recent completed changes remain cold history. The plan may include bounded ID/title/feature/date/summary/evidence metadata from the Context Manifest, but it never loads a Change body into Required reads.
- All generated Agent adapters prohibit recursive reads of `docs/ai`, `docs/specs`, and `docs/changes`; an Agent must read Required reads first, keep completed Change bodies cold, and name an unresolved question before expanding context.
- `check --strict --changed-since <base-ref>` validates the merge-base delta plus directly related current Packs/specs, so unrelated pre-existing debt does not block the current PR while a source change that makes its Pack stale still fails. Coverage considers only private sessions whose evidence intersects the changed implementation paths.
- Full `check --strict [--coverage]` behavior is unchanged and remains available for scheduled repository health audits and controlled release integration.

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

- `context --query` is a Context Pack router: it reads current Pack metadata, excludes superseded/archived Packs, penalizes stale fingerprints, and returns one primary Pack plus linked specs and the selection reason.
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

## License

[MIT](LICENSE)

<!-- repo-context-ledger:start -->
## Repository context

- [Stable feature context](docs/specs/README.md)
- [Change history](docs/changes/README.md)
- [Feature Context Packs](docs/ai/context-packs)
- Relevant specs: [Compact local configuration workflow](docs/specs/compact-local-config-workflow.md), [Context Routing Performance](docs/specs/context-routing-performance.md), [Continuation Quality](docs/specs/continuation-quality.md), [Contract Stability](docs/specs/contract-stability.md), [Coverage Integrity](docs/specs/coverage-integrity.md)
- Latest recorded change: [Harden v1.0.1 workflow and repository boundaries](docs/changes/2026/08/20260827202058-gviiisen-0e61ed5004-harden-v1-0-1-workflow-and-repository-boundaries.md)
<!-- repo-context-ledger:end -->
