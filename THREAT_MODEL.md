# Threat model

## Assets

- repository source and Git-tracked Pack/spec/Change knowledge;
- private active and paused task drafts below Git metadata;
- local verification-preset trust decisions;
- the integrity of evidence, coverage, finish, and generated runtime checks;
- credentials or machine paths that might appear in verification output.

## Trust boundaries

| Boundary | Assumption and control |
| --- | --- |
| Git-tracked repository content | Potentially untrusted after clone, pull, checkout, or PR switch. Presets remain inert until their normalized digest is trusted locally. |
| Local principal state | Private to the clone/account boundary, not committed, and not readable through another principal's Resume Capsule flow. |
| Git executable and repository metadata | Required evidence and changed-scope reads fail closed after worktree confirmation. Git failure is never treated as an empty change set. |
| Repository write lock | Created exclusively with private mode where supported, contains bounded non-secret metadata and an ownership nonce, and is removed only if path identity and nonce still match. |
| Verification subprocess | Runs only after an explicit direct command or trusted preset selection. `shell=False` is used; reviewed scripts are required for shell logic. |
| Persisted evidence | Local roots are redacted and failed output is bounded. `--sensitive` persists neither command arguments nor output. |

## Considered threats

- a pull request changes a verification preset into an arbitrary command;
- a damaged Git index/ref causes a quality gate to pass with no observed paths;
- Git display quoting corrupts evidence paths or associates a rename with the wrong file;
- a crashed writer leaves a stale lock, or another process replaces a lock while the owner exits;
- a symlink or non-regular path is placed at `.context-ledger/.write.lock`;
- verification output leaks a repository, user-home, Codex, or temporary absolute path;
- one local principal attempts to resume or mutate another principal's private task.

## Deliberate non-goals

- sandboxing a trusted project's test/build tools;
- defending against an administrator or process with unrestricted access to the same account;
- detecting malicious behavior hidden inside a reviewed executable or script;
- encrypting private task state at rest;
- synchronizing unfinished private state through Git;
- automatically deleting locks, accepting ownership transfers, or executing presets.

## Recovery principles

Fail closed when the evidence source, trust record, schema, or required Git query is invalid. Keep drafts recoverable after validation failure. Prefer read-only diagnosis and an explicit human/Agent decision over automatic cleanup. Never infer that missing evidence proves no change.
