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

## Initialize a repository

When the user asks to initialize, adopt, or configure repository context documentation:

1. Run `python <skill-dir>/scripts/ledger.py --repo <repository-root> init`.
2. Inspect the generated `.context-ledger/config.json`, detected modules, and existing documentation.
3. Run `python .context-ledger/ledger.py adapters check` and `python .context-ledger/ledger.py manifest check` to confirm native entry files and the shared route index are current.
4. Set `quality.language` (`auto`, `en`, or `zh-CN`) and `quality.detail` (`concise`, `standard`, or `detailed`) only when the repository needs a non-default policy.
5. Preserve existing `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, README content, and documentation. Only managed blocks or the dedicated Cursor adapter may be regenerated.
6. Treat nested Git repositories and worktrees as discovery boundaries. When adopting legacy `docs/changes/YYYY-MM/...` trees, preserve and reuse an existing monthly `index.md`; remove an obsolete index only when the runtime can reproduce the whole file byte-for-byte from current sibling records.
7. Summarize what was added. Do not require the user to learn internal lifecycle commands.

Read [document-model.md](references/document-model.md) when choosing where information belongs or migrating an existing documentation layout.

## Complete behavior-changing work

Apply this workflow autonomously for features, bug fixes, refactors, interface changes, and other changes that alter behavior. Do not ask the user to run ledger commands.

1. Before editing code, run `python .context-ledger/ledger.py status`. Each task owns a private draft session under worktree Git metadata. Never adopt, pause, publish, or rewrite another task's draft.
2. Resolve the record language. Follow configured language; for `auto`, use nearby documentation or the user's language. Keep code identifiers in source form.
3. If there is no active handoff, run:

   ```text
   python .context-ledger/ledger.py start --title "<concise task title>" --language <en|zh-CN>
   ```

   Keep the returned session ID. `start` must not create an unfinished file under `docs/changes/`. When more than one task is active, pass `--session <id>` to lifecycle commands; omission must fail rather than select another task.

4. Query the live route index, then load the feature Context Pack:

   ```text
   python .context-ledger/ledger.py context --query "<feature, interface, or module>"
   python .context-ledger/ledger.py focus --feature "<feature>"
   ```

   If no Context Pack exists, create one, fill every semantic section, then focus it:

   ```text
   python .context-ledger/ledger.py pack --feature "<feature>" --file <important-file> --spec <related-spec>
   ```

5. Read the returned stable specs and relevant project context before broad code exploration.
6. Implement the code change. Run every claimed check through `python .context-ledger/ledger.py verify --session <id> -- <command>`. Verification runs outside the repository write lock and records its result under a short lock afterward. If verification is unavailable, record it with `verify --session <id> --not-run --reason "<substantive reason>"`.
7. Run `python .context-ledger/ledger.py evidence`, then update this session's private draft from the generated changed paths. When any foreign session exists, pass repeated `--path <path>` arguments for only the files this task owns; omission must fail instead of copying the whole worktree diff into this draft. Read [.context-ledger/writing-quality.md](.context-ledger/writing-quality.md) and remove every `TODO` placeholder.
8. Refresh every Context Pack whose tracked production paths changed, then update its navigation content when code ownership or boundaries moved. Coverage is relational: changing an unrelated Pack never covers an implementation path.
9. Update an existing file under the configured stable-spec directory (default `docs/specs/`) when current behavior, boundaries, contracts, or code navigation changed. Create one from `.context-ledger/templates/spec-template.md` when no suitable stable spec exists; resolve its language and detail metadata.
10. Finish and atomically publish the private draft, then link the completed change to every affected stable spec. `finish` validates only this session's recorded evidence, explicit specs, and relevant Context Pack fingerprints; foreign dirty paths and foreign stale Packs are not blockers:

   ```text
   python .context-ledger/ledger.py finish --spec docs/specs/<feature>.md
   ```

   Repeat `--spec` for multiple specs. When no stable behavior exists to document, make the exception explicit and auditable:

   ```text
   python .context-ledger/ledger.py finish --no-spec --reason "<why no stable spec applies>"
   ```

11. Run repository-wide `python .context-ledger/ledger.py check --strict --coverage` at integration or pull-request time when foreign sessions are not actively changing the shared worktree. Do not contact another task or edit its docs merely to make a current task pass the global gate. Adjust validated `coverage` globs in `.context-ledger/config.json` when repository conventions differ from the defaults.

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
- Never persist secrets in records or invent tests, behavior, or code paths that were not inspected.
