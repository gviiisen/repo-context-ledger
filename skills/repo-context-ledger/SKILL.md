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
- **Single-task small fix**: `status` → `start --feature` → implement → `verify -- <command>` → `finish --spec`. `finish` records evidence automatically when this is the only session. If the worktree is large or another session exists, pass `evidence --path`.
- **Parallel tasks**: pass `--session <id>` on every lifecycle command. Capture evidence with repeated `--path` values for only this task.
- **Medium or large change**: also refresh the related Context Pack, update the stable spec, and write Before/After evidence before `finish`.

`context` returns one primary Context Pack, its linked specs, and why it was chosen. Read that Pack's load order before scanning the rest of the repository.

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
3. If this task will change behavior and has no session, `start --title "<title>" --feature "<feature>"`. Keep the session ID. When more than one task is active, pass `--session <id>`; omission must fail.
4. Route context, then read the primary Pack and its specs:

   ```text
   python .context-ledger/ledger.py context --query "<feature, interface, or module>"
   python .context-ledger/ledger.py focus --feature "<feature>"
   ```

   If no Context Pack exists, create one with `pack --feature`, fill every semantic section, then focus it.
5. Implement the change. Record every claimed check with `verify --session <id> -- <command>`. Failed output is stored as a redacted failure capsule, never as a raw log. Persisted verification evidence replaces repository, Codex, temporary, and user-home roots with stable placeholders, including JSON-escaped Windows paths. If verification is unavailable, use `verify --not-run --reason "<substantive reason>"`.
6. For a small single-session fix, `finish` can collect evidence. If another session exists, or automatic collection finds too many implementation paths, run `evidence --path` for only this task. Read [.context-ledger/writing-quality.md](.context-ledger/writing-quality.md) and remove every `TODO`. Code paths may cite `file.go::Symbol`; the path part is matched against evidence.
7. On medium or large changes, refresh every related Context Pack after tracked production paths change, and update the stable spec when current behavior or contracts changed.
8. Finish with `finish --spec docs/specs/<feature>.md`, or `finish --no-spec --reason "<why>"`. `finish` validates only this session.
9. Run `check --strict --coverage` at integration or pull-request time, not to unblock a parallel session.

## Bridge native Agent entry points

Treat `docs/ai/`, `docs/specs/`, and `docs/changes/` as the vendor-neutral source. `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/repo-context-ledger.mdc`, and `.github/copilot-instructions.md` are thin adapters only.

- Run `python .context-ledger/ledger.py adapters sync` after changing adapter policy or upgrading the runtime.
- Run `python .context-ledger/ledger.py adapters check` before completion.
- Run `python .context-ledger/ledger.py manifest sync` on the default branch when source documents were repaired manually; normal initialization and derived sync regenerate it automatically.
- Prefer code and executed tests over stable specs, stable specs over Context Packs, and all Git-tracked ledger documents over private Agent Memory.

Active lifecycle commands leave formal change history, shared README blocks, and monthly indexes unchanged. `finish` publishes one completed change file; feature branches continue to defer shared derived indexes until merge.

## Collaborate through Git

The runtime supports multiple private task drafts in one worktree. It isolates bookkeeping only: it does not copy source files, create worktrees, claim paths, lock code, or merge code. In a shared worktree, each session records an explicit evidence path set and `finish` ignores unrelated session dirt. Leave source-edit concurrency and conflicts to the host Agent and Git.

Never send messages, delegations, follow-up prompts, or steering instructions to another user-owned task/thread unless the user explicitly requests cross-task coordination. The presence of another session, a foreign stale Pack, a failed global check, or a shared worktree is not permission to contact, pause, redirect, or interrupt it. Report an integration-stage conflict to the user without steering the other task.

Before opening or updating a pull request:

1. Fetch or otherwise update the intended base branch.
2. Run `python .context-ledger/ledger.py team-check --base <base-ref>`.
3. Resolve reported overlaps in code paths or feature handoffs with the other contributor. Rebase or merge the current base as appropriate, then refresh any stale Context Pack.
4. Run `python .context-ledger/ledger.py check --strict`.

After changes are merged, run this once on the configured default branch:

```text
python .context-ledger/ledger.py sync --derived
```

This deterministically rebuilds monthly change indexes and managed root/module README summaries from committed source documents. Do not hand-edit generated indexes.

## Switch or resume context

Interpret natural-language requests such as "pause this and fix login," "continue the previous withdrawal task," or "hand this to another AI" as lifecycle instructions. Do not require command syntax from the user.

Before switching away from active work, record an accurate resume summary and concrete next step:

```text
python .context-ledger/ledger.py checkpoint --summary "<completed work and current state>" --next "<next concrete action>"
python .context-ledger/ledger.py pause --summary "<completed work and current state>" --next "<next concrete action>"
```

Use `checkpoint --session <id>` when another Agent or window will continue the same active task. Use `pause --session <id>` only when suspending that task; never manipulate another task's session.

Focus the target feature's Context Pack, then start its handoff when code behavior will change. Never abandon a different active handoff silently.

Resume the only paused task when it is unambiguous:

```text
python .context-ledger/ledger.py resume
```

Resume a selected task when multiple sessions are paused:

```text
python .context-ledger/ledger.py resume --session <id>
```

After resuming, read the handoff's resume fields, load its Context Pack, inspect dirty paths, and revalidate warnings about changed commits or stale fingerprints before editing code.

## Handle non-behavior work

For read-only analysis, questions, formatting-only edits, or tasks that do not change repository behavior, do not create a handoff. Read existing context as needed and leave the ledger unchanged.

## Recovery

- Run `python .context-ledger/ledger.py status` to inspect the current state.
- Reuse an active draft only when its session ID belongs to the current task.
- Start a separate private draft rather than pausing or overwriting another task.
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
