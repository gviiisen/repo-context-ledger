---
name: repo-context-ledger
description: Record every behavior-changing feature addition, fix, and adjustment as durable, evidence-based repository knowledge, then use that ledger to continue accurately across AI windows, tools, Git collaboration, and pull requests. Use the deterministic runtime to route bounded context, isolate private drafts, publish verified change records, refresh stable feature knowledge, and keep native Codex, Claude, Cursor, Copilot, Grok, and other Agent entry points aligned without asking the user to run bookkeeping commands.
---

# Repo Context Ledger

Turn behavior-changing feature work into durable, code-verified repository knowledge. Git-tracked Packs, specs, and completed Changes form the feature change ledger; cross-window and cross-Agent continuation are capabilities built on that shared source. Private vendor Memory is never read or synchronized.

## First decide what is new — without a Ledger call

Judge new facts/effects from the current request, loaded conversation, known task and inspected code, not similar wording. Do this mentally: no classifier command, extra document, or automatic Git/Markdown rescan.

- Routine question/recheck/operation with sufficient context: answer or execute the authorized request normally, without a new Ledger lifecycle. Do not skip a requested recheck or infer permission to repeat side effects.
- Same known unfinished task: keep its session/epoch and background; add only new changes, findings, decisions and checks. Same-window "continue" does not require resume or a new session.
- Similar work with new behavior/inputs/paths: reuse the method, not a previous pass. Keep a suitable unfinished task; after publication create a new change record and reference relevant history. Independent deliverables stay separate.
- Missing identity/background: query only what is missing. Paused tasks and actual handovers need resume; lifecycle writes still validate ownership/epoch. Resolve stale state rather than guessing.

Proceed when scope/identity are clear, without announcing a classification checklist. Reuse results only while relevant code, inputs, environment and acceptance phase remain valid. Changed conditions and time-sensitive safety checks need fresh verification; never relabel an old pass as new. Investigate uncertain code boundaries.

## Runtime

Resolve this Skill directory. Its runtime is `scripts/ledger.py`. After initialization use the repository entry:

```text
python .context-ledger/ledger.py <command>
```

Use `python3` when needed. `--repo` is optional; discovery walks upward to the nearest `.context-ledger/config.json` and stops at nested Git boundaries.

In `runtime.mode: global`, that entry is a small forwarder to the Codex Skill under `CODEX_HOME/skills` (or the user's `.codex/skills`); configuration and records remain repository-local. If the entry is absent, invoke this installed Skill's runtime with explicit `--repo <project>`. Never initialize or copy an old runtime just to execute a command. See [global-runtime.md](references/global-runtime.md) only for runtime installation/migration.

## Plan only when routing is needed

When the decision above leaves task identity or required context unresolved, run:

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
- One bounded logical request gets one session and one completed Change. Archive once, but update the same draft when meaningful facts emerge. Before a context/window switch, and after a changed diagnosis, key decision, or relevant failed approach, preserve the useful explanation while it is fresh. Use private checkpoints for continuation, not a new Change per step; do not combine unrelated requests or independently deliverable work just to reduce record counts.

## Change lifecycle

1. Keep the session ID and epoch from start/resume; use `status` only when this task's identity or state needs resolving. Pass `--session` on lifecycle writes; never guess or absorb another task.
2. Follow an existing accepted plan. Run context/focus only for missing or changed background, not again for every ordinary-work turn. A known code boundary needs no repeated broad routing.
3. Start once when behavior will change and there is no suitable unfinished task: `start --title "<title>" --feature <feature> --workflow <small-fix|ordinary-change> --tool <agent>`. Reuse only a genuinely related task; never reopen a completed record to hide a new change.
4. Implement after verifying the routed boundary in code. Context docs guide where to look; they never justify reading too little code.
5. Choose acceptance goals before verification. Reads, searches, file/configuration generation, preparation, and authorized deployment use ordinary tools, not a verify wrapper per operation. Run acceptance through `verify` once when first needed; do not run it bare and repeat it just for a Ledger entry. Group related checks with an existing reviewed project script/preset, preserving step results and failure exit codes. Keep pre-deployment and post-deployment goals separate. Independent checks may run concurrently only without shared mutable resources; use direct argv, not nested shell strings.
6. Prefer an exact repository preset when configured. If `PRESET_TRUST_REQUIRED` appears, review it and repeat with its exact printed `--trust-digest`; never trust without reviewing. Ordinary operations and useful diagnostic observations belong in the same draft as such, not fabricated managed check results. Never replay a deployment, authorization, migration, or trade to obtain missing logging. See [verification-presets.md](references/verification-presets.md) for grouping and the optional tested script example.
7. A single-session small fix lets `finish` collect evidence. With parallel sessions or a broad dirty tree, run `evidence --path` for this task's paths only.
8. Refresh the related Pack and spec when their facts or dependencies changed. Update only the draft's new differences and correct superseded assumptions; retain useful earlier reasoning rather than rewriting unchanged background. A small-fix form still explains each meaningful change, its file/symbol references, and documentation rationale. Only Updated is generated; share common boundaries and verification rather than repeating them.
9. Remove unresolved template placeholders and finish once the bounded request is actually complete, not at every intermediate reply: `finish --spec <spec>`, or `--no-spec --reason "<why no stable behavior exists>"`. Keep a returned continuation epoch on every resumed write.

Read [production-workflow.md](references/production-workflow.md) for large repositories, verification concurrency, PR baselines, coverage gates, and derived-index timing. Read [writing-quality.md](references/writing-quality.md) before editing an evidence-v1 draft.

Small is a known low-risk boundary, not a line count. Independent behavior changes, permissions, persistence, money, concurrency, public contracts, or uncertain impact need ordinary investigation and records. Expand the same draft when scope grows; preserve its notes and evidence, rather than finishing early or starting over. `finish --dry-run` is optional; do not make it a mandatory extra step or loop through it while still writing. Before finish, reconcile meaningful diff changes against the record; passing structural checks is not proof of complete business explanations.

## Initialize or upgrade

Run `init --dry-run`, review the exact plan, then run the same `init` only when its scope is correct. Preserve prose outside managed markers and all existing completed history. Confirm `adapters check`, `manifest check`, and `doctor`. See [document-model.md](references/document-model.md) for legacy layouts and where facts belong.

## Cross-window continuation

Before switching Agents or windows, run `checkpoint --summary "<state>" --next "<action>"`; use `pause` only when suspending the task. In the new window run `plan --query "continue <keywords>"`, then its explicit resume action. Resume increments the epoch; it does not create a replacement session.

"Continue" inside the same active window is not a handover. If the task and current epoch are already known, continue directly; resume only for an actual handover, paused task, or state recovery.

If several sessions are close matches, choose an explicit session. If only foreign work overlaps, use committed Pack/spec/Change guidance. Private unfinished state does not travel with clone, pull, or another computer.

## Integration and recovery

- Use `doctor` first for bounded read-only diagnosis. It never deletes locks or mutates Packs/sessions.
- At PR/integration time run `policy --base <ref>` for aggregate delta-based checks. Use `audit --history --policy as-recorded --fail-on unresolved` only for controlled historical/release audits, never to unblock an unrelated session.
- After merge, run `sync --derived` once on the configured default branch. Do not hand-edit generated indexes.
- Keep unfinished drafts private. Publish only through `finish`; never persist secrets or machine-specific absolute paths.

## Runtime development

Edit `src/repo_context_ledger/runtime.py.tmpl` and its ordered source fragments, not generated runtimes. Run `python scripts/build_runtime.py` and `python scripts/build_runtime.py --check`; `.context-ledger/ledger.py` and the Skill runtime must remain byte-identical standalone files.
