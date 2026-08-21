# Runtime Architecture

Status: current
Quality profile: evidence-v1
Language: en
Detail: standard
Last reviewed: 2026-08-21

## Purpose and behavior

Runtime Architecture provides one editable source and a deterministic path to the two standalone artifacts used by the Skill and this repository. It removes hand-maintained runtime duplication while preserving the zero-dependency single file copied by `init` into arbitrary repositories.

## Entry points and code map

| Path / symbol | Ownership and role |
| --- | --- |
| `scripts/build_runtime.py::render_runtime` | Normalizes and combines the runtime template with ordered low-coupling fragments. |
| `scripts/build_runtime.py::write_atomic` | Replaces generated outputs atomically without embedding timestamps or machine paths. |
| `src/repo_context_ledger/runtime.py.tmpl` | Owns the executable runtime body and build marker. |
| `src/repo_context_ledger/constants.pyfrag` | Owns stable versions, schemas, exit classes, and constants. |
| `src/repo_context_ledger/errors.pyfrag` | Owns `LedgerError` and stable machine error codes. |
| `src/repo_context_ledger/models.pyfrag` | Owns typed result contracts such as `CommandResult`. |
| `src/repo_context_ledger/contracts.pyfrag` | Keeps a non-built migration pointer for older contributor instructions. |
| `tests/test_runtime_build.py` | Protects drift detection, byte determinism, compilation, and standalone version execution. |

## Data flow and contracts

- Input: UTF-8 template and ordered fragment text plus either the two default repository outputs or explicit test outputs.
- Flow: the builder normalizes CRLF/CR to LF, requires one marker for each ordered fragment, injects constants then errors then models, terminates with one newline, compares or atomically writes each complete byte sequence, and reports repository-relative default paths.
- Persistence / dependencies: the builder uses only Python 3.10+ standard library. Temporary files stay beside their target and are replaced atomically. Generated artifacts import no source package and keep all runtime dependencies embedded.
- Output: `.context-ledger/ledger.py` and `skills/repo-context-ledger/scripts/ledger.py` are byte-identical standalone Python reporting version 0.7.0. `--check` returns 0 when current and 2 on drift or build-source failure without writing.

## Boundaries and failure modes

- Invariants: generated artifacts are never the editable authority; builds contain no timestamp or absolute source path; two fresh builds are byte-identical; `init` continues copying one executable file; v0.6.2 command/JSON/exit contracts remain compatible.
- Permissions / concurrency: atomic replacement prevents a reader from observing a partial generated file. The builder does not lock source files or coordinate concurrent developers; Git/CI detects competing source changes and output drift.
- Failure / recovery: missing/invalid UTF-8 source, a missing/duplicate marker, or stale output returns exit code 2. Recovery is to repair canonical source and rebuild, never to hand-edit one output.
- Non-goals: v0.7.0 does not split every runtime subsystem, publish a Python package, add third-party dependencies, change the installed file shape, or redesign lifecycle/routing behavior.

## Verification

Run `python -m unittest discover -s tests -p test_runtime_build.py`, `python scripts/build_runtime.py --check`, and the complete unit suite. CI repeats the drift check and suite on Windows/Ubuntu with Python 3.10/3.12.

<!-- repo-context-ledger:changes:start -->
## Related changes

- [Build deterministic standalone runtime architecture](../changes/2026/08/20260821233623-gviiisen-a1d83814d8-build-deterministic-standalone-runtime-architect.md)
<!-- repo-context-ledger:changes:end -->
