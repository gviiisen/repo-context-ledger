# Harden Git paths and file writes

Status: completed
Feature: runtime-architecture
Quality profile: evidence-v1
Language: en
Detail: standard
Scope: repository
Handoff ID: 20260827165407-gviiisen-71a5a84051
Session ID: 20260827165407-gviiisen-71a5a84051
Actor: gviiisen
Branch: feat/v0.8.1-repository-reliability
Started: 2026-08-27T16:54:07+08:00
Completed: 2026-08-27T17:14:47+08:00
Paused:
Resumed:
Checkpointed:
Checkpoint actor:
Base commit: 0d7e1f289e726edc4ae2b621361f89c621de5623
Dirty paths: none
Resume summary:
Next step:
Specs: docs/specs/runtime-architecture.md
Spec exception: none

## Intent

Harden repository state collection so unusual valid Git filenames remain exact, unreadable required Git state cannot silently pass a quality gate, and atomic rewrites do not remove an existing executable or read-only mode. Acceptance requires focused path/failure/permission tests, deterministic runtime drift checks, and the legacy runtime suite to pass.

## Changed behavior

Before: Git status/diff paths were parsed from line-delimited display text, so quoting, Unicode, control characters, and rename syntax could be lossy. Required Git command failures were converted to empty output, allowing changed-scope checks to report success against unreadable state. Atomic replacement could replace an existing file with the temporary file's default permission mode.

After: Git path readers consume NUL-delimited bytes and decode each complete path through the filesystem codec, required queries fail with `GIT_COMMAND_FAILED` after worktree confirmation, genuine non-Git fallback remains available, and atomic replacement applies an existing target's mode before replace.

## Code paths

| Path / symbol | Responsibility | Actual change |
| --- | --- | --- |
| `src/repo_context_ledger/runtime.py.tmpl::run_git` | Captures Git process results for repository queries. | Returns raw stdout/stderr bytes and separates optional discovery from required fail-closed reads. |
| `src/repo_context_ledger/runtime.py.tmpl::git_dirty_paths` | Supplies dirty paths to evidence, coverage, finish, and diagnostics. | Parses porcelain v1 NUL records, retains rename destinations, and handles complex filenames losslessly. |
| `src/repo_context_ledger/runtime.py.tmpl::git_changed_paths` | Supplies ref-based changed paths. | Uses NUL output and raises stable Git failures for required operations. |
| `src/repo_context_ledger/runtime.py.tmpl::atomic_write` | Publishes managed repository files. | Preserves an existing target mode before atomic replacement. |
| `scripts/build_runtime.py::write_atomic` | Generates both standalone runtime artifacts. | Preserves an existing output mode before atomic replacement. |
| `tests/test_repository_reliability.py` | Exercises the new repository reliability contract. | Adds Unicode/space evidence, Unicode rename, corrupted-index fail-closed, POSIX control-filename, and POSIX mode tests. |

## Boundaries and risks

- Invariant: Installed runtimes remain byte-identical, zero-dependency standalone Python; non-Git directories retain local fallback behavior; JSON schema names and exit classes do not change.
- Failure / recovery: A required Git failure exits with class 2 and `GIT_COMMAND_FAILED`; repair the repository/index/ref and retry instead of accepting an empty change set. A failed atomic write leaves the previous target in place.
- Not changed: Windows ACL and ownership behavior, automatic lock recovery, preset trust, workflow planning, and runtime module boundaries are reserved for later roadmap phases.

## Verification

Record checks with `ledger.py verify`; do not type claimed results manually.

<!-- repo-context-ledger:checks:start -->
- Command: `python scripts/build_runtime.py --check`
  - Status: passed
  - Preset: `runtime-build-check`
  - Working directory: `.`
  - Exit code: 0
  - Duration: 0.08s
  - Recorded: 2026-08-27T17:14:06+08:00
  - Output evidence: sha256:ad21cba65fcd1e25fe12023ab7408f9c5d797323811eb1dba587b9e8155e8ebf (40 characters captured; content not persisted; last=Standalone runtime outputs are current.)
- Command: `python -B -m unittest discover -s tests -p test_repository_reliability.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 6.03s
  - Recorded: 2026-08-27T17:14:18+08:00
  - Output evidence: sha256:0ea8e341f77bfa4ac94d3247576660aa14255920526413cc323f0e4eab628a75 (1078 characters captured; content not persisted; last=OK (skipped=2))
- Command: `python -B -m unittest discover -s tests -p test_runtime_build.py -v`
  - Status: passed
  - Exit code: 0
  - Duration: 0.70s
  - Recorded: 2026-08-27T17:14:19+08:00
  - Output evidence: sha256:305fcc4e9d0727a5dcf2e88ae3e71c3966eb0f699835d9547695be3b1f3eff54 (1134 characters captured; content not persisted; last=OK (skipped=1))
<!-- repo-context-ledger:checks:end -->

## Documentation updates

Updated: `README.md`, `README.zh-CN.md`, `COMPATIBILITY.md`, `MIGRATIONS.md`, `ARCHITECTURE.md`, `docs/specs/runtime-architecture.md`, and `docs/ai/context-packs/runtime-architecture.md`.

Reason: The release, compatibility, migration, architecture, stable-contract, and first-read routing documents now describe the fail-closed Git boundary and permission-preserving writes.

## Open questions

None.

<!-- repo-context-ledger:evidence:start -->
## Git change evidence

- Base commit: `0d7e1f289e726edc4ae2b621361f89c621de5623`
- Current commit: `0d7e1f289e726edc4ae2b621361f89c621de5623`
- Changed paths:
  - `docs/ai/context-packs/runtime-architecture.md`
  - `docs/specs/runtime-architecture.md`
  - `scripts/build_runtime.py`
  - `src/repo_context_ledger/constants.pyfrag`
  - `src/repo_context_ledger/models.pyfrag`
  - `src/repo_context_ledger/runtime.py.tmpl`
  - `tests/test_repository_reliability.py`
  - `tests/test_runtime_build.py`
<!-- repo-context-ledger:evidence:end -->
