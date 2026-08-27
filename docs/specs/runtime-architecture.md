# Runtime Architecture

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-27

## Purpose and behavior

Runtime Architecture provides one editable source and a deterministic path to the two standalone artifacts used by the Skill and this repository. It removes hand-maintained runtime duplication while preserving the zero-dependency single file copied by `init` into arbitrary repositories.

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `scripts/build_runtime.py::render_runtime` | Normalizes and combines the runtime template with ordered low-coupling fragments. |
| `scripts/build_runtime.py::write_atomic` | Replaces generated outputs atomically without embedding timestamps or machine paths, preserving an existing target mode. |
| `.gitattributes` | Keeps runtime-generation inputs and outputs LF-normalized in every checkout. |
| `src/repo_context_ledger/runtime.py.tmpl` | Owns the executable runtime body and build marker. |
| `src/repo_context_ledger/constants.pyfrag` | Owns stable versions, schemas, exit classes, and constants. |
| `src/repo_context_ledger/errors.pyfrag` | Owns `LedgerError` and stable machine error codes. |
| `src/repo_context_ledger/models.pyfrag` | Owns typed result contracts such as `CommandResult`, raw-byte `GitResult`, and old/new `GitPathChange`. |
| `src/repo_context_ledger/locks.pyfrag` | Owns bounded repository lock acquisition, identity/nonce ownership, and safe cleanup. |
| `src/repo_context_ledger/git.pyfrag` | Owns core Git execution, fail-closed command errors, repository detection, revisions, branches, and actor lookup. |
| `src/repo_context_ledger/workflow.pyfrag` | Owns deterministic `workflow-plan-v1` classification and rendering. |
| `src/repo_context_ledger/contracts.pyfrag` | Keeps a non-built migration pointer for older contributor instructions. |
| `schemas/*.schema.json` | Declares stable public JSON protocols without becoming a runtime dependency. |
| `tests/test_runtime_build.py` | Protects drift detection, byte determinism, compilation, and standalone version execution. |
| `tests/test_repository_reliability.py` | Protects lossless Git paths, required-query failure behavior, and permission preservation. |
| `tests/test_lock_and_preset_trust.py` | Protects lock diagnosis/ownership and principal-local verification-preset trust. |
| `SECURITY.md` / `THREAT_MODEL.md` | Define reporting, assets, trust boundaries, threats, recovery, and non-goals. |

## Data flow and contracts

- Input: UTF-8 template and ordered fragment text plus either the two default repository outputs or explicit test outputs.
- Flow: the builder normalizes CRLF/CR to LF, requires one marker for each ordered fragment, injects constants, errors, models, locks, Git, and Workflow Planning in declared order, terminates with one newline, compares or atomically writes each complete byte sequence, and reports repository-relative default paths.
- Persistence / dependencies: the builder uses only Python 3.10+ standard library. Temporary files stay beside their target, inherit an existing target's mode before replacement, and are replaced atomically. New public repository files use `0644`; private session, state, cache, and preset-trust files use `0600`; copied runtime files preserve their source mode. Generated artifacts import no source package and keep all runtime dependencies embedded.
- Repository state: Git path commands return NUL-delimited bytes, split before decoding, and use the operating-system filesystem codec. Destination-oriented callers retain the existing path-list view, while evidence and Coverage consume structured transitions: rename old/new paths both participate, deletion uses the old path, and copy uses only the new path for changed-implementation coverage. A confirmed worktree must answer required evidence, coverage, finish, and changed-scope queries; command failure is not equivalent to an empty change set.
- Write coordination: the short repository lock records version, process, start time, command, and an ownership nonce. Cleanup requires the original file identity and nonce. `doctor` uses platform-safe read-only liveness checks and never removes a lock.
- Preset trust: a normalized verification preset is hashed and must be trusted for the current local principal before first execution and after every change. Trust stays below Git metadata; direct verification commands and public repository schemas remain unchanged.
- Output: `.context-ledger/ledger.py` and `skills/repo-context-ledger/scripts/ledger.py` are byte-identical standalone Python reporting the current release version from `constants.pyfrag`. Contributor-facing schemas remain separate Git files. `--check` returns 0 when current and 2 on drift or build-source failure without writing.

## Boundaries and failure modes

- Invariants: generated artifacts are never the editable authority; builds contain no timestamp or absolute source path; Git checkout keeps the generation chain at LF even with `core.autocrlf=true`; two fresh builds are byte-identical; `init` continues copying one executable file; v1 public command/JSON/exit contracts remain compatible throughout the 1.x line.
- Permissions / concurrency: atomic replacement prevents a reader from observing a partial generated file and preserves an existing target's Unix permission bits. POSIX new-file modes follow the public/private contract above; ownership, ACLs, and Windows inheritance remain operating-system concerns. The builder does not lock source files or coordinate concurrent developers; Git/CI detects competing source changes and output drift.
- Failure / recovery: missing/invalid UTF-8 source, a missing/duplicate marker, stale output, a failed required Git query, or missing preset trust returns exit code 2. Required Git failures carry `GIT_COMMAND_FAILED`; preset trust failures carry `PRESET_TRUST_REQUIRED`. Diagnose locks before manual cleanup, repair repository/source state, and retry rather than inferring an empty change set or hand-editing one generated output.
- Non-goals: v1.0 does not split every runtime subsystem, publish a Python package, add third-party dependencies, change the installed file shape, or redesign lifecycle/routing behavior.

## Verification

Run `python -m unittest discover -s tests -p test_runtime_build.py`, `python -m unittest discover -s tests -p test_repository_reliability.py`, `python -m unittest discover -s tests -p test_lock_and_preset_trust.py`, `python scripts/build_runtime.py --check`, and the complete unit suite. CI repeats the drift check and suite on Windows/Ubuntu with Python 3.10/3.12; POSIX-only cases protect special filenames and permission modes.

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Harden v1.0.1 workflow and repository boundaries](../changes/2026/08/20260827202058-gviiisen-0e61ed5004-harden-v1-0-1-workflow-and-repository-boundaries.md)
- [Modularize runtime source and stabilize protocols](../changes/2026/08/20260827185543-gviiisen-9afe5ba1c7-modularize-runtime-source-and-stabilize-protocol.md)
- [Add lock diagnostics and preset trust](../changes/2026/08/20260827171514-gviiisen-5697daa67f-add-lock-diagnostics-and-preset-trust.md)
- [Harden Git paths and file writes](../changes/2026/08/20260827165407-gviiisen-71a5a84051-harden-git-paths-and-file-writes.md)
- [Accelerate small-task closeout](../changes/2026/08/20260827060627-gviiisen-2e52131353-accelerate-small-task-closeout.md)
- [Pin standalone runtime checkout line endings](../changes/2026/08/20260822003651-gviiisen-9d9c476d8a-pin-standalone-runtime-checkout-line-endings.md)
- [Build deterministic standalone runtime architecture](../changes/2026/08/20260821233623-gviiisen-a1d83814d8-build-deterministic-standalone-runtime-architect.md)
<!-- repo-context-ledger:changes:end -->
