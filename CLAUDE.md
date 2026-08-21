# Claude Code instructions

<!-- repo-context-ledger:rules:start -->
@AGENTS.md

Before broad documentation exploration, run `context --query "<task>"`. Read only the Context Bundle's Required reads initially. Never recursively read `docs/ai`, `docs/specs`, or `docs/changes`. Do not open completed Change bodies unless the plan selects one, a required Pack cites one for a named reason, or the user asks for historical reasoning. Required reads are a starting route, not a maximum code-reading limit. Expand context only after stating the unresolved question, and always expand whenever callers, implementations, configuration, persistence, permissions, concurrency, retries, tests, or external boundaries can affect the behavior. When the user says to continue earlier work, query the keywords first and use only an owned unique Resume Capsule. Continue the same Ledger session with `resume --query "<keywords>" --tool claude`; keep the returned continuation epoch and pass `--epoch <n>` to later writes. Never read, resume, pause, checkpoint, finish, or invalidate another principal's private session unless an explicit unexpired grant authorizes that exact access. Read-only grants never permit writes. A foreign overlap without a grant permits only Git-tracked Pack/spec/Change guidance.

Treat Git-tracked Context Packs, stable specs, and handoffs as the cross-Agent source of truth. Follow the repository context ledger workflow without asking the user to run lifecycle commands. Never message or steer another user-owned task unless the user explicitly requested cross-task coordination.
<!-- repo-context-ledger:rules:end -->
