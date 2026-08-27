---
name: repo-context-ledger
description: Maintain durable, evidence-based repository context whenever an agent initializes a repository, implements or fixes behavior, refactors code, changes an interface, checkpoints or switches tasks, resumes or hands work to another AI tool, collaborates across parallel task sessions, Git branches, or worktrees, prepares a pull request, or completes a coding task. Use this skill to bridge Codex, Claude, Cursor, GitHub Copilot, Grok, and other coding agents through native instruction adapters, private session-isolated handoff drafts, atomic completed-change publication, a shared Context Manifest, language-aware Context Packs, stable feature specifications, verified change history, coverage gates, and managed README summaries without asking the user to run bookkeeping commands.
---

# Repo Context Ledger

Keep repository knowledge current across AI tools and fresh conversation windows. Treat semantic documentation as part of completing code work, while using the bundled deterministic runtime for paths, native adapters, the Context Manifest, indexes, links, README blocks, and validation. Never attempt to read or synchronize private vendor Memory; promote only code-verified facts into Git-tracked context.

## Locate the runtime

Resolve the directory containing this `SKILL.md`. The bundled runtime is `scripts/ledger.py` relative to that directory.

After initialization, prefer the repository-local copy:

```text
python .context-ledger/ledger.py <command>
```

Use `python3` instead of `python` when that is the available interpreter.

`--repo` is optional. If omitted, the runtime walks up from the current directory to the nearest `.context-ledger/config.json`, and stops at a nested Git repository boundary.

## Choose the shortest path

Do not run the full lifecycle for every request.

- **Read-only understanding**: `context --query "<task>"`, then `focus --feature "<feature>"`. Do not `start` a session.
- **Repository health audit**: run `doctor` for bounded, read-only diagnostics before deciding whether stale Packs, broken links, adapter drift, or private-state problems need a repair task. Use `doctor --format json` for automation.
- **Automation integration**: use `status --format json`, `check --format json`, `doctor --format json`, and `context --format json`. Preserve each versioned schema and exit class; do not parse the human-readable text as an API.
- **Small worktree-local configuration change**: `status` → `start --kind local-config --feature <feature> --language <en|zh-CN>` → edit one or more tracked configuration paths → `verify --sensitive -- <direct executable and arguments>` → `finish --path <config-path>`. Resolve `auto` to the language of the user and nearby records before starting. Do not run `context`, `focus`, a separate `evidence`, or manually edit the handoff unless the task expands beyond local configuration. Every path must classify as `config`, and the final check must be a passing sensitive verification. The runtime creates a sanitized `Scope: worktree-local` record and applies the stable-spec exception automatically.
- **Single-task small fix with a known code path and boundary**: `status` → `start --feature` → implement → run independent `verify` commands in parallel → `finish --spec`. Prefer a reviewed `verify --preset <name>` when the repository defines the exact check; otherwise pass a direct executable and arguments. Skip `context`, `focus`, and a separate `evidence` command unless the task becomes uncertain or expands. `finish` records evidence automatically when this is the only session. If another session exists, pass scoped `evidence --path` values.
- **Parallel tasks**: pass `--session <id>` on every lifecycle command. Capture evidence with repeated `--path` values for only this task.
- **Continue earlier work in a fresh Agent window**: run `context --query "<keywords>" --tool <agent>`. Resume only one uniquely matched session owned by the current principal, keep the returned continuation epoch, and pass it to later lifecycle writes.
- **Medium or large change**: also refresh the related Context Pack, update the stable spec, and write Before/After evidence before `finish`.

`context` returns `context-bundle-v1` with one current primary Pack, bounded Required reads, cold-history summaries, an optional PR baseline, and an owned `resume-capsule-v2` when one task matches. Capsule v2 organizes only explicit checkpoint/evidence/verification and Git-tracked Pack/spec facts; it does not infer task progress, diffs, translations, or symbols. Pack metadata and tracked-file digests may be reused only from the disposable private cache below Git metadata; Git files, current code, and executed verification remain authoritative. Read only Required reads initially; never recursively read `docs/ai`, `docs/specs`, or `docs/changes`. Do not open a completed Change body unless the Bundle selects it, a required Pack cites it for a named reason, or the user asks for history. Required reads and the Capsule are a starting route, not a maximum code-reading limit. State the unresolved question, then expand whenever callers, implementations, configuration, persistence, permissions, concurrency, retries, tests, or external boundaries can affect the requested behavior. Read [production-workflow.md](references/production-workflow.md) for large repositories and pull-request validation.

## Initialize a repository

When the user asks to initialize, adopt, or configure repository context documentation:

1. Run `python <skill-dir>/scripts/ledger.py --repo <repository-root> init --dry-run` and inspect the exact planned files, managed blocks, migrations, and detected modules. The preview must remain read-only.
2. If the plan matches the user's requested repository scope, run the same command without `--dry-run`. Do not hand-recreate or selectively replay the plan.
3. Inspect the generated `.context-ledger/config.json`, detected modules, and existing documentation.
4. Run `python .context-ledger/ledger.py adapters check` and `python .context-ledger/ledger.py manifest check` to confirm native entry files and the shared route index are current.
5. Set `quality.language` (`auto`, `en`, or `zh-CN`) and `quality.detail` (`concise`, `standard`, or `detailed`) only when the repository needs a non-default policy.
6. Preserve existing `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, README content, and documentation. Only managed blocks or the dedicated Cursor adapter may be regenerated.
7. Treat nested Git repositories and worktrees as discovery boundaries. When adopting legacy `docs/changes/YYYY-MM/...` trees, preserve and reuse an existing monthly `index.md`; remove an obsolete index only when the runtime can reproduce the whole file byte-for-byte from current sibling records.
8. Summarize what was added. Do not require the user to learn internal lifecycle commands.

Read [document-model.md](references/document-model.md) when choosing where information belongs or migrating an existing documentation layout.

## Complete behavior-changing work

Apply this workflow autonomously when code behavior changes. Follow [Choose the shortest path](#choose-the-shortest-path). Do not ask the user to run ledger commands.

1. Run `python .context-ledger/ledger.py status`. Reuse only this task's private draft. Never adopt, pause, publish, or rewrite another task's draft.
2. Resolve the record language. Keep code identifiers in source form.
3. If this task will change behavior and has no session, `start --title "<title>" --feature "<feature>" --tool <agent>`. Keep the session ID. When more than one task is active, pass `--session <id>`; omission must fail.
4. For medium/large changes, or whenever the code location, caller boundary, contract, or affected Pack is uncertain, route context and read only the Context Bundle's Required reads. A genuinely small fix may skip this step only when its code path and behavior boundary are already established. The compact `local-config` path also skips routing unless it expands into source behavior:

   ```text
   python .context-ledger/ledger.py context --query "<feature, interface, or module>" --tool <agent>
   python .context-ledger/ledger.py focus --feature "<feature>"
   ```

   If no Context Pack exists, create one with `pack --feature`, fill every semantic section, then focus it. Add repeated `--alias "<human phrase>"` values only for reviewed cross-language or colloquial feature names, and keep the code-map `path::Symbol` anchors explicit; never generate aliases or symbols from guessed task state.
5. Implement the change. Before constructing a repeated project check, inspect `.context-ledger/config.json` for an exact reviewed `verification.presets` entry. Prefer `verify --preset <name>` when it matches; presets are explicit argv arrays and are never auto-run. Read [verification-presets.md](references/verification-presets.md) when adding, reviewing, or troubleshooting one. Otherwise use `verify --session <id> [--epoch <n>] -- <direct executable and arguments>`. After code is stable, start independent checks concurrently. While they run, refresh the affected Pack and update the stable spec; do not concurrently hand-edit the private draft because each verification appends to it. Wait for every verification process to record its result before `finish`. Keep checks serial when they share a database, port, generated directory, mutable fixture, or other exclusive resource. Do not wrap a direct executable in nested PowerShell or shell quoting merely to call it through `verify`; after one command-construction failure, correct the invocation instead of trying quote variants. For checks that may expose configuration values, use `verify --sensitive` or a reviewed preset with `sensitive: true`; it displays and persists neither the command arguments nor captured output, while retaining status, exit code, and duration. After a cross-Agent resume, the returned epoch is mandatory for `checkpoint`, `pause`, `evidence`, `verify`, and `finish`. Failed non-sensitive output is stored as a redacted failure capsule, never as a raw log. Persisted verification evidence replaces repository, Codex, temporary, and user-home roots with stable placeholders, including JSON-escaped Windows paths. If verification is unavailable, use `verify --not-run --reason "<substantive reason>"`.
6. For a compact `local-config` task, pass repeated `finish --path` values; the runtime rejects non-config paths, requires the final sensitive check to pass, captures scoped evidence, and completes the sanitized draft, so do not manually remove template TODOs. For an ordinary small single-session fix, let `finish` collect evidence instead of running a duplicate `evidence` command. If another session exists, or automatic collection finds too many implementation paths, run `evidence --path` for only this task. Read the repository-local `.context-ledger/writing-quality.md` and remove every `TODO`. Code paths may cite `file.go::Symbol`; the path part is matched against evidence.
7. On medium or large changes, refresh every related Context Pack after tracked production paths change, and update the stable spec when current behavior or contracts changed. Do this while independent verification runs when the files and checks do not share mutable resources.
8. Finish an ordinary behavior change with `finish --session <id> [--epoch <n>] --spec docs/specs/<feature>.md`, or `finish --no-spec --reason "<why>"`. The compact `local-config` form is `finish --session <id> --path <config-path>` and supplies its own stable-spec exception. `finish` validates only this session.
9. At pull-request time, route once with `context --query "<task>" --baseline <base-ref>` so the Bundle can expose the bounded merge-base delta, then prefer `check --strict --coverage --changed-since <base-ref>` so unrelated historical debt cannot block the current delta while directly related current Packs/specs remain fail-closed. Coverage may use only private sessions whose evidence intersects the changed implementation paths. Reserve the full `check --strict --coverage` audit for scheduled health work or controlled release integration, not to unblock a parallel session.

## Bridge native Agent entry points

Treat `docs/ai/`, `docs/specs/`, and `docs/changes/` as the vendor-neutral source. `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/repo-context-ledger.mdc`, and `.github/copilot-instructions.md` are thin adapters only.

- Run `python .context-ledger/ledger.py adapters sync` after changing adapter policy or upgrading the runtime.
- Run `python .context-ledger/ledger.py adapters check` before completion.
- Run `python .context-ledger/ledger.py manifest sync` on the default branch when source documents were repaired manually; normal initialization and derived sync regenerate it automatically.
- Prefer code and executed tests over stable specs, stable specs over Context Packs, and all Git-tracked ledger documents over private Agent Memory.

Active lifecycle commands leave formal change history, shared README blocks, and monthly indexes unchanged. `finish` publishes one completed change file; feature branches continue to defer shared derived indexes until merge.

## Collaborate through Git

The runtime supports multiple private task drafts in one worktree. It isolates bookkeeping only: it does not copy source files, create worktrees, claim paths, lock code, or merge code. In a shared worktree, each session records an explicit evidence path set and `finish` ignores unrelated session dirt. Leave source-edit concurrency and conflicts to the host Agent and Git.

Private task ownership is principal-based, not tool-based: the same configured human principal may continue between Codex, Cursor, Claude, Copilot, or Grok, while another principal cannot read or mutate the private Capsule by default. The default principal derives from the OS account; teams sharing one OS account should configure a stable private identity with the local Git setting `repo-context-ledger.principal`. This is logical workflow isolation, not an operating-system security sandbox.

Only after the user explicitly authorizes a handoff may an Agent create an expiring `share` grant for another principal. `read-only` reveals a Capsule but cannot resume it; `fork` creates a new recipient-owned child session without changing the source; `transfer` requires a paused source and changes ownership when the recipient resumes. Never infer authorization from shared Git access, a matching feature name, or a foreign-overlap signal.

Never send messages, delegations, follow-up prompts, or steering instructions to another user-owned task/thread unless the user explicitly requests cross-task coordination. The presence of another session, a foreign stale Pack, a failed global check, or a shared worktree is not permission to contact, pause, redirect, or interrupt it. Report an integration-stage conflict to the user without steering the other task.

Before opening or updating a pull request:

1. Fetch or otherwise update the intended base branch.
2. Run `python .context-ledger/ledger.py team-check --base <base-ref>`.
3. Resolve reported overlaps in code paths or feature handoffs with the other contributor. Rebase or merge the current base as appropriate, then refresh any stale Context Pack.
4. Run `python .context-ledger/ledger.py check --strict --coverage --changed-since <base-ref>`. Run the full repository audit separately when the repository's historical debt is expected to be clean.

After changes are merged, run this once on the configured default branch:

```text
python .context-ledger/ledger.py sync --derived
```

This deterministically rebuilds monthly change indexes and managed root/module README summaries from committed source documents. Do not hand-edit generated indexes.

## Switch or resume context

Interpret natural-language requests such as "pause this and fix login," "continue announcement rate limiting in Cursor," or "hand this to another AI" as lifecycle instructions. Do not require command syntax from the user.

Before switching away from active work, record an accurate resume summary and concrete next step:

```text
python .context-ledger/ledger.py checkpoint --summary "<completed work and current state>" --next "<next concrete action>"
python .context-ledger/ledger.py pause --summary "<completed work and current state>" --next "<next concrete action>"
```

Use `checkpoint --session <id> [--epoch <n>]` when another Agent or window will continue the same active task. Use `pause --session <id> [--epoch <n>]` only when suspending that task; never manipulate another task's session.

Focus the target feature's Context Pack, then start its handoff when code behavior will change. Never abandon a different active handoff silently.

In a fresh window, route natural-language keywords before broad exploration:

```text
python .context-ledger/ledger.py context --query "continue <task keywords>" --tool <agent>
```

If exactly one active or paused session owned by the current principal matches, continue that same Ledger session:

```text
python .context-ledger/ledger.py resume --query "continue <task keywords>" --tool <agent>
```

`resume` increments the continuation epoch rather than creating a replacement session. Keep the returned epoch and use it on every later write. If several owned sessions are near matches, select an explicit `--session <id>`; never guess. If only a foreign session overlaps, load only Git-tracked Pack/spec/Change guidance unless the user has explicitly authorized a `read-only`, `fork`, or `transfer` grant.

The `resume-capsule-v2` object is generated on demand from private state and is deliberately bounded. It preserves the earlier checkpoint/evidence fields and adds goal, current state, next action, explicit Pack code anchors, must-preserve contracts, verified facts, unresolved questions, Required reads, and default cold-document guidance. These are routing facts, not inferred implementation truth. It is not a complete execution environment and never excuses insufficient code reading. After resuming, inspect the routed Pack and evidence paths, then follow every behavior-relevant caller, implementation, configuration, storage, permission, concurrency, retry, test, and external boundary until the requested behavior is actually understood.

Private unfinished sessions do not travel with `git clone`, pull, or another computer. On a different clone, use committed Packs, specs, and completed Changes; do not pretend a private Capsule was recovered.

## Handle non-behavior work

For read-only analysis, questions, formatting-only edits, or tasks that do not change repository behavior, do not create a handoff. Read existing context as needed and leave the ledger unchanged.

## Recovery

- Run `python .context-ledger/ledger.py doctor` first when the failure scope is unclear. Doctor groups stale paths by Pack, caps detail output, and suggests actions without changing files, private sessions, Pack status, or lineage.
- Run `python .context-ledger/ledger.py status` to inspect the current state.
- Reuse an active or paused draft only when its session belongs to the current principal and uniquely matches the task. After `resume`, use its continuation epoch for every write.
- Start a separate private draft rather than pausing or overwriting another task.
- Treat foreign overlap as a routing warning only. Do not expose its summary, evidence, verification, draft path, tool, or epoch.
- When another session exists, capture evidence with repeated `--path` values for this task only; never adopt the entire shared dirty set.
- Use `status` and `--session` lifecycle targeting; do not find or edit the Git-metadata state file manually.
- Refresh a stale Context Pack with `pack` after inspecting the changed files.
- Repair drifted native entry files with `adapters sync`; never copy private Agent Memory into the ledger as an unverified fact.
- Run `python .context-ledger/ledger.py sync` after manually repairing documents or configuration. Add `--derived` on the default branch after merges.

## Writing rules

- Apply [writing-quality.md](references/writing-quality.md) to `evidence-v1` records. Preserve legacy records unless explicitly upgrading them.
- Record current truth in `docs/specs/`, chronological evidence in `docs/changes/`, and minimal loading routes in Context Packs.
- Keep unfinished drafts private. Publish each completed change into its own file and let the runtime build monthly indexes.
- Keep the runtime-generated handoff ID, actor, and branch metadata. Unique filenames are intentional and prevent two contributors from creating the same history path.
- Keep Context Packs under the configured line limit and track only the minimum paths required to resume work.
- Never rewrite README prose outside managed markers.
- Never persist secrets or machine-specific absolute paths in records, and never invent tests, behavior, or code paths that were not inspected.

## Develop the runtime

Treat `src/repo_context_ledger/runtime.py.tmpl` and its build-time fragments as the editable runtime source. Never hand-edit `.context-ledger/ledger.py` or `skills/repo-context-ledger/scripts/ledger.py`; run `python scripts/build_runtime.py`, then `python scripts/build_runtime.py --check`. Both generated files must remain byte-identical because initialized repositories copy the standalone artifact and cannot depend on the source package.
