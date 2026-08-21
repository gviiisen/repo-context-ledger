# Claude Code instructions

<!-- repo-context-ledger:rules:start -->
@AGENTS.md

Before broad documentation exploration, run `context --query "<task>"`. Read only the Context Plan's Required reads initially. Never recursively read `docs/ai`, `docs/specs`, or `docs/changes`. Do not open completed Change bodies unless the plan selects one, a required Pack cites one for a named reason, or the user asks for historical reasoning. Expand context only after stating the unresolved question.

Treat Git-tracked Context Packs, stable specs, and handoffs as the cross-Agent source of truth. Follow the repository context ledger workflow without asking the user to run lifecycle commands. Never message or steer another user-owned task unless the user explicitly requested cross-task coordination.
<!-- repo-context-ledger:rules:end -->
