# Architecture

Repo Context Ledger separates editable source from the single-file runtime installed into repositories.

## Source and generated artifacts

| Path | Role |
| --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl` | Canonical runtime body and ordered build markers. |
| `src/repo_context_ledger/constants.pyfrag` | Stable version, schema, exit, and runtime constants. |
| `src/repo_context_ledger/errors.pyfrag` | Stable user-facing error type and machine error-code carrier. |
| `src/repo_context_ledger/models.pyfrag` | Typed machine-result contracts such as `CommandResult`, raw-byte `GitResult`, and lossless `GitPathChange`. |
| `src/repo_context_ledger/locks.pyfrag` | Repository write-lock acquisition, ownership, and safe cleanup. |
| `src/repo_context_ledger/git.pyfrag` | Core Git process execution, fail-closed errors, repository identity, and actor queries. |
| `src/repo_context_ledger/workflow.pyfrag` | `workflow-plan-v1` classification and rendering. |
| `src/repo_context_ledger/contracts.pyfrag` | Non-built compatibility tombstone that points older contributors to the ordered fragments declared in `scripts/build_runtime.py`. |
| `scripts/build_runtime.py` | Deterministic standard-library builder and drift checker. |
| `.gitattributes` | Pins canonical inputs and generated outputs to LF across Windows and Unix checkouts. |
| `skills/repo-context-ledger/scripts/ledger.py` | Generated standalone artifact shipped with the Skill. |
| `.context-ledger/ledger.py` | Generated dogfood mirror used by this repository. |
| `schemas/*.schema.json` | Git-tracked Draft 2020-12 declarations for stable public JSON protocols; not runtime dependencies. |

The generated files are byte-identical. `init` copies the currently executing standalone runtime into the target repository, so installed projects keep one zero-dependency file and do not import the source package.

## Build contract

The builder reads UTF-8 source, normalizes line endings to LF, injects each ordered fragment through exactly one explicit marker, emits no timestamp or machine path, and writes outputs atomically. When replacing an existing target on Unix-like systems, the temporary file receives the target's permission mode before the atomic replace. New public repository files use `0644`; private session, state, cache, and trust files use `0600`; copied runtime files retain their source mode. Git attributes pin the build inputs and generated outputs to LF so byte comparison remains portable when Windows enables `core.autocrlf`. `--check` compares bytes and never writes. CI runs the check on Windows and Ubuntu with Python 3.10 and 3.12 before tests; release, scheduled, and manual workflows also run on macOS.

Git-facing runtime code captures stdout and stderr as bytes. Path-producing commands use `-z`, split only on NUL, and decode individual paths through the operating-system filesystem codec. Rename-aware evidence retains old and new paths; Coverage compares base Pack ownership of the source with current same-feature Pack ownership of the destination, while ordinary path-list consumers keep their destination-oriented view and copy sources are not treated as changed implementations. After Git confirms a worktree, required path/evidence queries fail closed; only a genuine non-Git directory may use the local fallback.

Repository writes use a short exclusive lock containing only bounded diagnostic metadata and a random ownership nonce. Cleanup checks both the original file identity and nonce. `doctor` may classify the lock but never removes it. Verification presets remain Git-tracked inert data until their normalized digest is trusted for the current local principal; trust state lives below Git metadata and is not part of repository history.

Workflow Planning is a read-only decision layer above the existing lifecycle. `plan` reuses the bounded context route and current-principal Resume Capsule preflight, then emits `workflow-plan-v1`; `context` additively embeds the same decision. The returned argument array is never executed by the planner. Mutation guards remain authoritative in `start` and `resume`, so a caller cannot turn a read-only or continuation decision into a new task merely by bypassing the front door.

Edit source and rebuild with:

```text
python scripts/build_runtime.py
python scripts/build_runtime.py --check
```

Never repair drift by editing a generated output. Change the template/fragment, rebuild both outputs, and review the generated diff.

## Modular source, standalone distribution

v0.7.0 extracted low-coupling constants, errors, and result models first. v1.0 adds repository locks, core Git access, and Workflow Planning as independently reviewed ordered fragments. The builder requires every marker exactly once, preserves deterministic order, and compiles them into the same standalone artifact. Future extraction remains incremental and must have focused tests before moving a boundary.

Configuration, lifecycle, routing, health, and rendering remain in the template for now. This avoids a high-risk flag-day rewrite while giving the most security- and protocol-sensitive subsystems explicit source ownership. Public 1.x protocols are declared under `schemas/`; incompatible required-field, meaning, or exit changes require a new schema name and major version.
