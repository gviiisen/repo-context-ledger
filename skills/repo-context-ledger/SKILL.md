---
name: repo-context-ledger
description: Maintain durable, AI-friendly repository context whenever an agent initializes a repository, implements or fixes behavior, refactors code, changes an interface, pauses or switches tasks, resumes prior work, hands work to another AI session, or completes a coding task. Use this skill to create and update Context Packs, docs/ai, stable feature specifications, active and paused handoffs, change history, and managed README summaries without asking the user to run bookkeeping commands.
---

# Repo Context Ledger

Keep repository knowledge current across AI tools and fresh conversation windows. Treat semantic documentation as part of completing code work, while using the bundled deterministic runtime for paths, indexes, links, README blocks, and validation.

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
3. Preserve existing `AGENTS.md`, `CLAUDE.md`, README content, and documentation. Only managed blocks may be regenerated.
4. Summarize what was added. Do not require the user to learn internal lifecycle commands.

Read [document-model.md](references/document-model.md) when choosing where information belongs or migrating an existing documentation layout.

## Complete behavior-changing work

Apply this workflow autonomously for features, bug fixes, refactors, interface changes, and other changes that alter behavior. Do not ask the user to run ledger commands.

1. Before editing code, inspect `docs/changes/.active-handoff`.
2. If there is no active handoff, run:

   ```text
   python .context-ledger/ledger.py start --title "<concise task title>"
   ```

3. Load the feature Context Pack:

   ```text
   python .context-ledger/ledger.py focus --feature "<feature>"
   ```

   If no Context Pack exists, create one, fill every semantic section, then focus it:

   ```text
   python .context-ledger/ledger.py pack --feature "<feature>" --file <important-file> --spec <related-spec>
   ```

4. When the feature is not yet known, retrieve likely background documents:

   ```text
   python .context-ledger/ledger.py context --query "<feature, interface, or module>"
   ```

5. Read the returned stable specs and relevant project context before broad code exploration.
6. Implement and verify the code change.
7. Update the active handoff with intent, changed behavior, code paths, boundaries, verification, and documentation impact. Remove every `TODO` placeholder.
8. Refresh the Context Pack fingerprints and content when its tracked code paths changed.
9. Update an existing file under the configured stable-spec directory (default `docs/specs/`) when current behavior, boundaries, contracts, or code navigation changed. Create one from `.context-ledger/templates/spec-template.md` when no suitable stable spec exists.
10. Finish and link the change to every affected stable spec:

   ```text
   python .context-ledger/ledger.py finish --spec docs/specs/<feature>.md
   ```

   Repeat `--spec` for multiple specs. When no stable behavior exists to document, make the exception explicit and auditable:

   ```text
   python .context-ledger/ledger.py finish --no-spec --reason "<why no stable spec applies>"
   ```

11. Run `python .context-ledger/ledger.py check --strict` and resolve failures before reporting completion.

## Switch or resume context

Interpret natural-language requests such as "pause this and fix login," "continue the previous withdrawal task," or "hand this to another AI" as lifecycle instructions. Do not require command syntax from the user.

Before switching away from active work, record an accurate resume summary and concrete next step:

```text
python .context-ledger/ledger.py pause --summary "<completed work and current state>" --next "<next concrete action>"
```

Focus the target feature's Context Pack, then start its handoff when code behavior will change. Never abandon a different active handoff silently.

Resume the most recently paused task:

```text
python .context-ledger/ledger.py resume
```

Resume a selected task when multiple handoffs are paused:

```text
python .context-ledger/ledger.py resume --handoff docs/changes/YYYY/MM/<change>.md
```

After resuming, read the handoff's resume fields, load its Context Pack, inspect dirty paths, and revalidate warnings about changed commits or stale fingerprints before editing code.

## Handle non-behavior work

For read-only analysis, questions, formatting-only edits, or tasks that do not change repository behavior, do not create a handoff. Read existing context as needed and leave the ledger unchanged.

## Recovery

- Run `python .context-ledger/ledger.py status` to inspect the current state.
- Reuse an active handoff when it belongs to the current task.
- Pause rather than overwrite a different active handoff.
- Use the paused stack in `.context-ledger/context-state.json`; do not edit it manually.
- Refresh a stale Context Pack with `pack` after inspecting the changed files.
- Run `python .context-ledger/ledger.py sync` after manually repairing documents or configuration.

## Writing rules

- Record current truth in `docs/specs/`; do not turn stable specs into chronological diaries.
- Record why and what changed in `docs/changes/`.
- Keep each change in its own file. Let the runtime build small per-month indexes; never accumulate all change narratives in one document.
- Record cross-cutting repository orientation in `docs/ai/`.
- Keep each `docs/ai/context-packs/<feature>.md` file concise. Link to stable specs and track only the minimum code paths required to resume work.
- Include concrete code paths, entry points, boundaries, failure modes, and verification commands.
- Never rewrite README prose outside managed markers.
- Never invent tests, behavior, or code paths that were not inspected.
