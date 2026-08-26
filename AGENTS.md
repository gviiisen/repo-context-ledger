# Agent instructions

<!-- repo-context-ledger:rules:start -->
## Repository context ledger

Choose the shortest applicable path. Read-only work uses `context` only when routing is needed and never starts a session. A small worktree-local configuration change uses `status` → `start --kind local-config --language <en|zh-CN>` → `verify --sensitive -- <direct executable and arguments>` → `finish --path <changed-config> --summary "<observable result>"`. Do not run context or focus, a separate evidence command, or manually edit the handoff for that compact path. Ordinary behavior changes use the lifecycle below.

For every feature, bug fix, refactor, interface change, or other ordinary behavior-changing code task:

1. Before editing code, run `status`, then start or reuse only this task's private draft session. Keep the returned session ID and pass `--session <id>` whenever multiple sessions exist.
2. Resolve `quality.language`; when it is `auto`, follow nearby docs or the user's language. Keep paths, symbols, commands, and error text untranslated.
3. Before broad documentation exploration, run `context --query "<task>"`. Read only the Context Bundle's Required reads initially. Never recursively read `docs/ai`, `docs/specs`, or `docs/changes`. Do not open completed Change bodies unless the plan selects one, a required Pack cites one for a named reason, or the user asks for historical reasoning. Required reads are a starting route, not a maximum code-reading limit. Expand context only after stating the unresolved question, and always expand whenever callers, implementations, configuration, persistence, permissions, concurrency, retries, tests, or external boundaries can affect the behavior. Focus the selected feature Context Pack before broad code exploration. If no Pack exists, create and fill one.
4. When the user says to continue earlier work, query the keywords first and use only an owned unique Resume Capsule. Continue the same Ledger session with `resume --query "<keywords>" --tool <agent>`; keep the returned continuation epoch and pass `--epoch <n>` to later writes. Never read, resume, pause, checkpoint, finish, or invalidate another principal's private session unless an explicit unexpired grant authorizes that exact access. Read-only grants never permit writes. A foreign overlap without a grant permits only Git-tracked Pack/spec/Change guidance. Run `checkpoint --session <id> --summary "..." --next "..."` before handing active work to another Agent. Pause only this task's session; never pause, resume, or finish another task's session.
5. Run every claimed check through `python .context-ledger/ledger.py verify -- <command>`. Use `verify --not-run --reason "..."` only when verification is genuinely unavailable.
6. Run `evidence`, read `.context-ledger/writing-quality.md`, and fill the private draft from actual changed paths. When another session exists, pass repeated `--path <path>` values for only this task; never capture foreign dirty paths. Refresh affected Context Packs with `pack --file ...`.
7. Update `docs/specs/` when current behavior, contracts, boundaries, or code navigation changes.
8. Finish with `finish --spec <affected-spec>`, or use `--no-spec --reason "..."` only when no stable behavior exists.
9. Let `finish` enforce this session's evidence, specs, and relevant Context Pack fingerprints. Run repository-wide `check --strict --coverage` only at integration or PR time, when foreign sessions are not actively changing the shared worktree.
10. Before opening or updating a pull request, update the base ref and run `team-check --base origin/main`.

Active and paused drafts are stored in Git worktree metadata and must not be committed. Only `finish` may publish a validated draft into `docs/changes/`. On feature branches, do not regenerate shared README or monthly index blocks. After merging on `main`, run `python .context-ledger/ledger.py sync --derived` once.

Never send a message, delegation, follow-up prompt, or steering instruction to another user-owned task or thread unless the user explicitly requested cross-task coordination. A foreign dirty path, stale Pack, failed global check, or shared worktree is not permission. Do not repair another session's docs to unblock this task. The ledger does not copy, lock, merge, or coordinate source-code edits; leave code conflicts to the host Agent and Git without interrupting another task.

Do not ask the user to run bookkeeping commands. Do not create a handoff for read-only analysis or formatting-only work. Preserve prose outside `repo-context-ledger` managed markers.
<!-- repo-context-ledger:rules:end -->
