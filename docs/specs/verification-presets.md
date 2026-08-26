# Verification presets

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-27

## Purpose and behavior

Verification presets let a repository define repeatable, reviewed test commands as executable argument arrays. An Agent explicitly selects one with `verify --preset <name>` instead of rebuilding a shell command on every task, reducing PowerShell quoting failures while preserving real subprocess execution and session-scoped evidence.

## Entry points and code map

| Path / symbol | Responsibility |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::normalize_verification_config` | Validates preset names, argv arrays, repository-relative working directories, timeouts, sensitivity, platforms, and forbidden shell-string wrappers. |
| `src/repo_context_ledger/runtime.py.tmpl::resolve_verification_preset` | Selects one explicit preset, checks the current platform and working directory, and returns its execution contract. |
| `src/repo_context_ledger/runtime.py.tmpl::record_verification` | Executes the resolved argv with `shell=False` and records the preset name and repository-relative working directory. |
| `src/repo_context_ledger/runtime.py.tmpl::build_parser`, `run_main` | Enforces mutual exclusion between a preset, direct argv, and not-run evidence, and applies explicit timeout/sensitive overrides. |
| `skills/repo-context-ledger/references/verification-presets.md` | Gives production configuration and Windows/Linux usage examples without loading them for unrelated tasks. |

## Data flow and contracts

- Input: `config.verification.presets` maps a lowercase name to `argv`, `cwd`, `timeout`, `sensitive`, and `platforms`. `verify --preset <name>` is always explicit; no lifecycle command runs all presets.
- Flow: Configuration loading normalizes and validates the full preset before execution. Selection checks the current OS and resolves `cwd` inside the repository. The runtime passes the argv list directly to `subprocess.run` with `shell=False`, using the same unlocked execution and short result-append locks as direct verification.
- Persistence / dependencies: Presets are Git-tracked repository configuration and use no external package. The completed verification record includes the sanitized command, preset name, relative working directory, status, exit code, duration, and evidence summary; sensitive presets retain only sanitized metadata.
- Output: Success and failure use the existing verify exit behavior. Unknown presets list available names; invalid platform, missing cwd, malformed argv, command/preset ambiguity, and forbidden shell-string wrappers fail before execution.

## Boundaries and failure modes

- Invariants: A preset never invokes a shell implicitly, never runs during init/context/finish, never escapes repository `cwd`, and cannot weaken `sensitive: true`. Spaces remain within one argv element. Existing direct verification commands remain compatible.
- Permissions / concurrency: Git review and explicit preset selection are the trust boundary. A preset can run arbitrary executables available to the user, so Agents must not execute unreviewed presets merely because they exist. Independent presets follow the same parallel-verification rules; shared mutable resources remain serial.
- Failure / recovery: Invalid configuration fails closed before session mutation or command execution. A missing executable records an ordinary failed verification; an unsupported platform or missing working directory returns an input error without running the command.
- Non-goals: Presets do not manage secrets or environment variables, infer the correct test suite, replace project scripts, auto-run CI, provide a general task runner, or make shell command strings safe.

## Verification

Run `python -m unittest discover -s tests -p test_ledger.py -k verification_preset` for argv/cwd execution, sensitive persistence, shell-string rejection, platform isolation, missing-name handling, and command ambiguity. Run `python scripts/build_runtime.py --check` and the complete suite for generated-runtime and compatibility coverage.

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Add safe verification presets](../changes/2026/08/20260827065951-gviiisen-6daa4a6c38-add-safe-verification-presets.md)
<!-- repo-context-ledger:changes:end -->
