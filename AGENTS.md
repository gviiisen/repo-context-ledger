# Agent instructions

<!-- repo-context-ledger:rules:start -->
## Repository context ledger

For every feature, bug fix, refactor, interface change, or other behavior-changing code task:

1. Before editing code, run `status`, then start or reuse only this task's private draft session. Keep the returned session ID and pass `--session <id>` whenever multiple sessions exist.
2. Resolve `quality.language`; when it is `auto`, follow nearby docs or the user's language. Keep paths, symbols, commands, and error text untranslated.
3. Use `context --query "<task>"` and focus the feature Context Pack before broad code exploration. If none exists, create and fill one.
4. Run `checkpoint --session <id> --summary "..." --next "..."` before handing active work to another Agent. Pause only this task's session; never pause, resume, or finish another task's session.
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
