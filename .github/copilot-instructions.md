# GitHub Copilot instructions

<!-- repo-context-ledger:rules:start -->
## Repository Context Ledger

Read and follow the repository root `AGENTS.md`. Before broad documentation exploration, run `context --query "<task>"`. Read only the Context Plan's Required reads initially. Never recursively read `docs/ai`, `docs/specs`, or `docs/changes`. Do not open completed Change bodies unless the plan selects one, a required Pack cites one for a named reason, or the user asks for historical reasoning. Expand context only after stating the unresolved question. Treat Copilot Memory as a private cache; Git-tracked ledger documents are the shared cross-Agent source of truth. Never message or steer another user-owned task unless the user explicitly requested cross-task coordination.
<!-- repo-context-ledger:rules:end -->
