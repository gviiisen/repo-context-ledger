---
name: repo-context-ledger
description: Maintain durable, evidence-based repository context whenever an agent initializes a repository, changes behavior, checkpoints or resumes work, switches AI tools or windows, collaborates through Git, prepares a pull request, or completes a coding task. Use the deterministic runtime to route bounded context, isolate private drafts, publish verified change records, refresh stable feature knowledge, and keep native Codex, Claude, Cursor, Copilot, Grok, and other Agent entry points aligned without asking the user to run bookkeeping commands.
---

# Repo Context Ledger

Carry code-verified repository knowledge across AI tools and fresh windows. Git-tracked Packs, specs, and completed Changes are the shared source; private vendor Memory is never read or synchronized.

## Runtime

Resolve this Skill directory. Its runtime is `scripts/ledger.py`. After initialization prefer:

```text
python .context-ledger/ledger.py <command>
```

Use `python3` when needed. `--repo` is optional; discovery walks upward to the nearest `.context-ledger/config.json` and stops at nested Git boundaries.

## Start with one plan

For a new request or fresh window, run:

```text
python .context-ledger/ledger.py plan --query "<user request>" --tool <agent>
```

Follow the returned `workflow-plan-v1` mode and `next_action`:

- `readonly`: load bounded context only; never create a session.
- `small-fix`: start one short session, edit the known boundary, verify, finish.
- `ordinary-change`: route the Pack/spec, start one session, implement, verify, refresh stable knowledge, finish.
- `resume`: resume only one uniquely selected accessible session and keep its new epoch.

Automatic classification is guidance, not permission. If `requires_confirmation` is true, clarify the workflow or select a session; never guess. `start --workflow readonly|resume` must fail. `context` returns the same nested Workflow Plan, and `resume --query` uses the same owned-session route.

## Non-negotiable safety

- Never read, pause, resume, checkpoint, finish, invalidate, or expose another principal's private task unless an explicit unexpired grant permits that exact access.
- Never message, delegate to, steer, or interrupt another user-owned Agent task unless the user explicitly requests cross-task coordination.
- The ledger isolates documentation sessions only. It does not lock, copy, merge, or coordinate source-code edits; leave code conflicts to the host Agent and Git.
- Read only Context Bundle `required_reads` initially. Never recursively load `docs/ai`, `docs/specs`, or `docs/changes`. This is a starting route, not a cap: expand through every behavior-relevant caller, implementation, configuration, persistence, permission, concurrency, retry, test, and external boundary.
- Prefer code and executed verification over specs, specs over Packs, and Git-tracked knowledge over private Agent Memory.
- Do not create a handoff for read-only analysis, questions, or formatting-only work.
- Do not ask the user to run ledger bookkeeping commands.

## Change lifecycle

1. Run `status`; keep this task's session ID and use `--session` whenever multiple sessions exist.
2. Follow `plan`. For uncertain or ordinary work, run `context --query` and `focus --feature`; for a known small fix, skip broad routing.
3. Start only when behavior will change: `start --title "<title>" --feature <feature> --workflow <small-fix|ordinary-change> --tool <agent>`.
4. Implement after verifying the routed boundary in code. Context docs guide where to look; they never justify reading too little code.
5. Run independent checks concurrently only when they share no database, port, generated directory, mutable fixture, or other exclusive resource. Use direct argv after `verify --`; do not build nested PowerShell/shell command strings.
6. Prefer an exact repository preset when configured. If `PRESET_TRUST_REQUIRED` appears, review that Git-tracked preset and repeat with its exact printed `--trust-digest`; never trust without reviewing. See [verification-presets.md](references/verification-presets.md).
7. A single-session small fix lets `finish` collect evidence. With parallel sessions or a broad dirty tree, run `evidence --path` for this task's paths only.
8. For ordinary behavior changes, refresh the related Pack and current spec after code stabilizes. Remove every TODO from the private draft.
9. Finish with `finish --spec <spec>`, or `--no-spec --reason "<why no stable behavior exists>"`. Keep a returned continuation epoch on every resumed write.

Read [production-workflow.md](references/production-workflow.md) for large repositories, verification concurrency, PR baselines, coverage gates, and derived-index timing. Read [writing-quality.md](references/writing-quality.md) before editing an evidence-v1 draft.

## Initialize or upgrade

Run `init --dry-run`, review the exact plan, then run the same `init` only when its scope is correct. Preserve prose outside managed markers and all existing completed history. Confirm `adapters check`, `manifest check`, and `doctor`. See [document-model.md](references/document-model.md) for legacy layouts and where facts belong.

## Cross-window continuation

Before switching Agents or windows, run `checkpoint --summary "<state>" --next "<action>"`; use `pause` only when suspending the task. In the new window run `plan --query "continue <keywords>"`, then its explicit resume action. Resume increments the epoch; it does not create a replacement session.

If several sessions are close matches, choose an explicit session. If only foreign work overlaps, use committed Pack/spec/Change guidance. Private unfinished state does not travel with clone, pull, or another computer.

## Integration and recovery

- Use `doctor` first for bounded read-only diagnosis. It never deletes locks or mutates Packs/sessions.
- At PR/integration time run `policy --base <ref>`. It selects the ordinary or derived-only gate from the actual Git delta and includes team overlap, changed-scope Coverage, deterministic derived-output, and diff checks as applicable. Use `audit --history --policy as-recorded --fail-on unresolved` only for controlled historical/release audit; do not use it to unblock an unrelated session.
- After merge, run `sync --derived` once on the configured default branch. Do not hand-edit generated indexes.
- Keep unfinished drafts private. Publish only through `finish`; never persist secrets or machine-specific absolute paths.

## Runtime development

Edit `src/repo_context_ledger/runtime.py.tmpl` and its ordered source fragments, not generated runtimes. Run `python scripts/build_runtime.py` and `python scripts/build_runtime.py --check`; `.context-ledger/ledger.py` and the Skill runtime must remain byte-identical standalone files.
