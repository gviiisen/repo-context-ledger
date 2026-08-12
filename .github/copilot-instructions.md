# GitHub Copilot instructions

<!-- repo-context-ledger:rules:start -->
## Repository Context Ledger

Read and follow the repository root `AGENTS.md`. Before broad code exploration, run `python .context-ledger/ledger.py context --query "<task>"` and load the matching Context Pack and stable spec. Treat Copilot Memory as a private cache; Git-tracked ledger documents are the shared cross-Agent source of truth. Never message or steer another user-owned task unless the user explicitly requested cross-task coordination.
<!-- repo-context-ledger:rules:end -->
